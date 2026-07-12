import os

from django.contrib.contenttypes.models import ContentType

from workflow.engine import start_workflow
from workflow.models import Workflow, WorkflowInstance

from masters.models import Particular

from tax_requests.constants import (
    ACCORDION_SECTIONS,
    MASTER_INITIATED_FIELDS,
    STAGE_MODEL_FIELDS,
    STAGE_SECTION_KEYS,
    WORKFLOW_STAGE_NAMES,
)
from tax_requests.models import (
    TDSOpinion,
    TDSOpinionStage,
    InvoicePostingStage,
    BankDetailStage,
    Form146Stage,
    Form145Stage,
    PaymentDetailStage,
    CloseRequestStage,
    ApprovedStage,
)

STAGE_MODEL_MAP = {
    "tds_opinion_stage": TDSOpinionStage,
    "invoice_posting": InvoicePostingStage,
    "bank_detail": BankDetailStage,
    "form_146": Form146Stage,
    "form_145": Form145Stage,
    "payment_detail": PaymentDetailStage,
    "close_request": CloseRequestStage,
    "approved": ApprovedStage,
}

RELATED_NAMES = {
    "tds_opinion_stage": "tds_opinion_stage",
    "invoice_posting": "invoice_posting",
    "bank_detail": "bank_detail",
    "form_146": "form_146",
    "form_145": "form_145",
    "payment_detail": "payment_detail",
    "close_request": "close_request",
    "approved": "approved_stage",
}

from tax_requests.constants import FILE_VALIDITY_MAP, STAGE_FILE_FIELDS
from tax_requests.remittance_service import sync_remittance_report
from tax_requests.workflow_permissions import FK_FIELDS, can_user_act_on_tds_opinion
from tax_requests.email_service import send_external_ca_email
from tax_requests.services.form146_comparison_service import run_and_save_comparison

FILE_FIELDS = STAGE_FILE_FIELDS


def copy_master_files_from_existing(target, source_id, file_fields):
    """Copy specified file fields and their valid_upto from an existing TDSOpinion."""
    from django.core.files import File

    try:
        source = TDSOpinion.objects.get(id=source_id, is_deleted=False)
    except TDSOpinion.DoesNotExist:
        return

    for field_name in file_fields:
        source_file = getattr(source, field_name, None)
        if source_file:
            # Use only the basename to avoid duplicating the upload_to path
            # e.g. "tds_opinion/invoice/dummy.pdf" → "dummy.pdf"
            getattr(target, field_name).save(
                os.path.basename(source_file.name),
                File(source_file),
                save=False
            )
            # Also copy the corresponding valid_upto if it exists
            valid_field = FILE_VALIDITY_MAP.get(field_name)
            if valid_field:
                valid_value = getattr(source, valid_field, None)
                if valid_value is not None:
                    setattr(target, valid_field, valid_value)


def _file_field_url(value):
    if value and getattr(value, "name", None):
        return value.url
    return None


def _get_fk_display_value(record, field_name):
    fk_obj = getattr(record, field_name, None)
    if fk_obj:
        return str(fk_obj)
    return None


def _get_tds_opinion_workflow():
    ct = ContentType.objects.get_for_model(TDSOpinion)
    return Workflow.objects.filter(
        content_type=ct,
        name="TDS Opinion Approval",
        is_active=True,
    ).first()


def _get_latest_workflow_instance(record):
    ct = ContentType.objects.get_for_model(TDSOpinion)
    qs = WorkflowInstance.objects.filter(content_type=ct, object_id=record.pk)
    workflow = _get_tds_opinion_workflow()
    if workflow:
        qs = qs.filter(workflow=workflow)
    return qs.select_related("current_stage", "workflow").order_by("-attempt").first()


def get_current_stage_name(record):
    instance = _get_latest_workflow_instance(record)
    if not instance:
        return "Initiated"
    if instance.status == "approved":
        return "Approved"
    if instance.status in ("rejected", "returned"):
        return "Initiated"
    if instance.current_stage:
        return instance.current_stage.name
    return record.status or "Initiated"


def get_editable_sections(record, user):
    """Return section keys the user may edit right now."""
    instance = _get_latest_workflow_instance(record)
    sections = set()

    if not instance or instance.status in ("rejected", "returned"):
        sections.add("master")
        return sorted(sections)

    if instance.status == "approved":
        return []

    stage_name = instance.current_stage.name if instance.current_stage else "Initiated"
    section_key = STAGE_SECTION_KEYS.get(stage_name)

    # Check if the current stage is a skipped stage — if so, the workflow
    # should not have landed here, but just in case, don't allow editing it
    skipped_stages = get_skipped_stage_names(record)
    if stage_name in skipped_stages:
        return []

    if stage_name == "Initiated":
        if user == record.created_by or user.is_superuser:
            sections.add("master")
    elif section_key and can_user_act_on_tds_opinion(instance, user):
        sections.add(section_key)
    elif user.is_superuser and section_key:
        sections.add(section_key)

    return sorted(sections)


def get_skipped_stage_names(record):
    """
    Return set of workflow stage names that should be skipped/hidden
    based on the form_146_type selected in the bank detail stage.
    """
    try:
        bank = getattr(record, "bank_detail", None)
        if bank and bank.form_146_type:
            form_type = bank.form_146_type.type_15cb.strip().lower()

            if "not required" in form_type:
                # Form-146/145 not required → skip both Form 146 and Form 145
                return {"Form 146 Request", "Form 145 Request"}

            if "part b" in form_type or "part d" in form_type:
                # Form 146 - Part B or Part D → skip Form 146 Request only
                return {"Form 146 Request"}
    except Exception:
        pass

    return set()


def get_visible_accordion_sections(current_stage_name, record=None):
    """Return accordion sections for completed stages and the current stage only.
    Optionally filters out skipped stages based on form_146_type."""
    stage_name = current_stage_name if current_stage_name in WORKFLOW_STAGE_NAMES else "Initiated"
    visible_stages = set(WORKFLOW_STAGE_NAMES[: WORKFLOW_STAGE_NAMES.index(stage_name) + 1])

    # If record is provided, filter out skipped stages
    if record:
        skipped_stages = get_skipped_stage_names(record)
        visible_stages -= skipped_stages

    return [section for section in ACCORDION_SECTIONS if section["stage"] in visible_stages]


# def _serialize_stage(record, section_key):
#     related_name = RELATED_NAMES[section_key]
#     stage_obj = getattr(record, related_name, None)
#     if stage_obj is None:
#         return {}
#     fields = STAGE_MODEL_FIELDS[section_key]
#     data = {}
#     file_fields = set(FILE_FIELDS.get(section_key, []))
#     for field in fields:
#         value = getattr(stage_obj, field, None)
#         if field in file_fields:
#             data[field] = _file_field_url(value)
#         elif field in FK_FIELDS:
#             data[field] = getattr(stage_obj, f"{field}_id", None)
#         else:
#             data[field] = value
#     return data

def _serialize_stage(record, section_key, user=None):
    related_name = RELATED_NAMES[section_key]
    stage_obj = getattr(record, related_name, None)

    data = {}

    # Add computed fields first
    if section_key == "form_146":
        invoice_posting = getattr(record, "invoice_posting", None)

        data["document_number"] = (
            invoice_posting.document_number
            if invoice_posting else None
        )

        data["invoice_posting_date"] = (
            invoice_posting.invoice_posting_date
            if invoice_posting else None
        )

        data["invoice_copy"] = _file_field_url(record.invoice_file)

        data["form_10f_file"] = _file_field_url(
            record.form_10f_file
        )

        data["trc_file"] = _file_field_url(record.trc_file)

        data["no_pe_declaration_file"] = _file_field_url(
            record.no_pe_declaration_file
        )

        # Include comparison data if available (auto-generated on save)
        if stage_obj:
            data["comparison_status"] = stage_obj.comparison_status
            data["ack_number"] = stage_obj.ack_number
            data["download_form_146_comparison"] = _file_field_url(
                stage_obj.download_form_146_comparison
            )

    # No stage record yet
    if stage_obj is None:
        # Auto-fill currency from the master record for TDS Opinion stage
        if section_key == "tds_opinion_stage" and record.currency_id:
            data["currency"] = record.currency_id
            data["currency_display"] = _get_fk_display_value(record, "currency")
        # Auto-fill sap_username for payment_detail with the current user
        if section_key == "payment_detail" and user:
            data["sap_username"] = user.get_full_name() or user.username
        return data

    fields = STAGE_MODEL_FIELDS[section_key]
    file_fields = set(FILE_FIELDS.get(section_key, []))

    for field in fields:
        value = getattr(stage_obj, field, None)

        if field in file_fields:
            data[field] = _file_field_url(value)

        elif field in FK_FIELDS:
            data[field] = getattr(stage_obj, f"{field}_id", None)
            # Include display label for FK fields
            fk_obj = getattr(stage_obj, field, None)
            if fk_obj:
                data[f"{field}_display"] = str(fk_obj)

        else:
            data[field] = value

    # Auto-fill sap_username for payment_detail with the current user if empty
    if section_key == "payment_detail" and user and not data.get("sap_username"):
        data["sap_username"] = user.get_full_name() or user.username

    return data


def _serialize_master(record):
    data = {"id": record.id, "request_code": record.request_code}
    file_fields = set(FILE_FIELDS.get("master", []))
    for field in MASTER_INITIATED_FIELDS:
        value = getattr(record, field, None)
        if field in ("company", "currency", "particular"):
            data[field] = getattr(record, f"{field}_id", None)
            # Include display label for FK fields
            fk_obj = getattr(record, field, None)
            if fk_obj:
                data[f"{field}_display"] = str(fk_obj)
        elif field in file_fields:
            data[field] = _file_field_url(value)
        else:
            data[field] = value
    data["status"] = record.status
    data["open_with"] = record.open_with
    return data


def build_workflow_form_payload(record, user):
    current_stage = get_current_stage_name(record)
    instance = _get_latest_workflow_instance(record)

    # Compute skipped stages once so it's available throughout
    skipped_stages = get_skipped_stage_names(record)

    stages_data = {"master": _serialize_master(record)}
    for section_key in STAGE_MODEL_FIELDS:
        stages_data[section_key] = _serialize_stage(record, section_key, user=user)

    # Filter out skipped stages from the overall stage list
    filtered_stages = [
        s for s in WORKFLOW_STAGE_NAMES
        if s not in skipped_stages
    ]

    return {
        "stages": filtered_stages,
        "accordion_sections": get_visible_accordion_sections(current_stage, record=record),
        "current_stage": current_stage,
        "editable_sections": get_editable_sections(record, user),
        "workflow": {
            "instance_id": instance.id if instance else None,
            "status": instance.status if instance else None,
            "can_act": can_user_act_on_tds_opinion(instance, user) if instance else False,
        },
        "data": stages_data,
    }


def _get_or_create_stage(record, section_key):
    model_cls = STAGE_MODEL_MAP[section_key]
    related_name = RELATED_NAMES[section_key]
    stage_obj = getattr(record, related_name, None)
    if stage_obj is None:
        stage_obj = model_cls.objects.create(tds_opinion=record)
    return stage_obj


def _extract_section_files(files, section_key):
    prefix = f"{section_key}."
    return {
        k.split(".", 1)[1]: v
        for k, v in files.items()
        if k.startswith(prefix)
    }


def _apply_fields(obj, fields, payload, file_payload=None):
    file_payload = file_payload or {}
    for field in fields:
        if field in file_payload:
            setattr(obj, field, file_payload[field])
        elif field in payload:
            value = payload[field]
            if field in FK_FIELDS:
                setattr(obj, f"{field}_id", value if value else None)
            else:
                setattr(obj, field, value)


def save_workflow_form(record, user, payload, files=None):
    files = files or {}
    editable = set(get_editable_sections(record, user))
    if not editable:
        raise PermissionError("You cannot edit any section at the current workflow stage.")

    master_data = payload.get("master", {})
    if "master" in editable and (master_data or _extract_section_files(files, "master")):
        master_files = _extract_section_files(files or {}, "master")

        particular_id = master_data.get("particular")

        required_files = []

        particular = Particular.objects.filter(id=particular_id).first()

        if particular:
            particular_name = (particular.particular_name.strip().lower())

            if "suppy of goods" in particular_name:
                required_files = [
                    "no_pe_declaration_file",
                ]

            elif "supply of services" in particular_name:
                required_files = [
                    "form_10f_file",
                    "no_pe_declaration_file",
                    "trc_file",
                    "contract_agreement_copy",
                ]

            elif (
                "pure reimbursement" in particular_name
                or "any other income" in particular_name
            ):
                required_files = [
                    "proof_of_reimbursement_file",
                ]

        missing = []

        for field in required_files:
            uploaded_now = field in master_files
            existing_file = getattr(record, field, None)

            if not uploaded_now and not existing_file:
                missing.append(field)

        if missing:
            raise ValueError(
                f"Required documents missing: {', '.join(missing)}"
            )
        _apply_fields(
            record,
            MASTER_INITIATED_FIELDS,
            master_data,
            _extract_section_files(files, "master"),
        )
        record.last_updated_by = user
        record.save()
        print("record.id =", record.id)
        print("record.pk =", record.pk)

    for section_key in STAGE_MODEL_FIELDS:
        if section_key not in editable:
            continue
        section_data = payload.get(section_key, {})
        section_files = _extract_section_files(files, section_key)
        if not section_data and not section_files:
            continue
        stage_obj = _get_or_create_stage(record, section_key)
        _apply_fields(
            stage_obj,
            STAGE_MODEL_FIELDS[section_key],
            section_data,
            section_files,
        )
        stage_obj.save()

        if section_key == "tds_opinion_stage":
            bank_stage = _get_or_create_stage(record, "bank_detail")
            bank_stage.form_146_type = stage_obj.form_146_type
            bank_stage.save(update_fields=["form_146_type"])

        # Auto-generate Form 146 comparison when a PDF is uploaded
        if section_key == "form_146" and stage_obj.form_146_attachment:
            print("Form 146 attachment detected — auto-generating comparison...")
            run_and_save_comparison(record, stage_obj)

        print("\n======================================", flush=True)
        print("Current Section:", section_key, flush=True)
        
        if section_key == "bank_detail":
            print("Entered Bank Detail Stage", flush=True)
            print("Selected Form Type:", stage_obj.form_146_type, flush=True)
            print("Selected External CA:", stage_obj.external_ca, flush=True)
        
            if (
                stage_obj.form_146_type
                and stage_obj.external_ca
                and stage_obj.form_146_type.type_15cb == "Form 146 - Part C"
            ):
                print("Condition Matched.", flush=True)
                print("Calling send_external_ca_email()", flush=True)
                send_external_ca_email(record, user=user)
            else:
                print("Condition NOT Matched.", flush=True)
                print("Form Type:",
                      stage_obj.form_146_type.type_15cb if stage_obj.form_146_type else None, flush=True)
                print("External CA:", stage_obj.external_ca, flush=True)
        
        print("======================================\n", flush=True)

    sync_remittance_report(record)
    return build_workflow_form_payload(record, user)


def _section_has_data(section_data, files, section_key):
    if _extract_section_files(files, section_key):
        return True
    return any(
        value is not None and value != "" and value is not False
        for value in (section_data or {}).values()
    )


def create_tds_opinion_with_form(user, payload, files=None):
    files = files or {}
    master_data = payload.get("master", {})
    if not _section_has_data(master_data, files, "master"):
        raise ValueError(
            "No form data was received. Please fill in the request details and try again."
        )
    
    master_files = _extract_section_files(files or {}, "master")

    particular_id = master_data.get("particular")

    required_files = []

    particular = Particular.objects.filter(id=particular_id).first()

    if particular:
        particular_name = (particular.particular_name.strip().lower())

        if "suppy of goods" in particular_name:
            required_files = [
                "no_pe_declaration_file",
            ]

        elif "supply of services" in particular_name:
            required_files = [
                "form_10f_file",
                "no_pe_declaration_file",
                "trc_file",
                "contract_agreement_copy",
            ]

        elif (
            "pure reimbursement" in particular_name
            or "any other income" in particular_name
        ):
            required_files = [
                "proof_of_reimbursement_file",
            ]

    # Account for files that will be copied from an existing request
    copy_fields = (master_data or {}).get("_copy_file_fields", [])
    missing = [
        field
        for field in required_files
        if field not in master_files and field not in copy_fields
    ]

    if missing:
        raise ValueError(
            f"Required documents missing: {', '.join(missing)}"
        )
    record = TDSOpinion(
        created_by=user,
        last_updated_by=user,
        status="Initiated",
        open_with="Initiated",
    )
    _apply_fields(
        record,
        MASTER_INITIATED_FIELDS,
        master_data,
        _extract_section_files(files, "master"),
    )
    record.save()
    print("record.id:", record.id)
    print("record.pk:", record.pk)

    # Copy files from existing request if specified
    master_payload = payload.get("master", {})
    copy_from = master_payload.get("_copy_files_from")
    copy_fields = master_payload.get("_copy_file_fields", [])
    if copy_from and copy_fields:
        copy_master_files_from_existing(record, copy_from, copy_fields)
        record.save()

    workflow = _get_tds_opinion_workflow()
    if workflow:
        instance = start_workflow(record, user, workflow=workflow)

        # Auto-approve the Initiated stage so the user lands directly in TDS Opinion stage
        if instance and instance.current_stage:
            from workflow.models import WorkflowAction

            # Record the approval action for audit trail
            WorkflowAction.objects.create(
                instance=instance,
                stage=instance.current_stage,
                actor=user,
                action="approve",
                comment="[Initiated]",
            )

            # Advance to the next stage (TDS Opinion)
            next_stage = instance.workflow.stages.filter(
                order__gt=instance.current_stage.order
            ).order_by("order").first()

            if next_stage:
                instance.current_stage = next_stage
                instance.save()

                # Update TDSOpinion status to reflect the new stage
                record.status = next_stage.name
                record.open_with = next_stage.name
                record.save(update_fields=["status", "open_with"])

    sync_remittance_report(record)
    return build_workflow_form_payload(record, user)
