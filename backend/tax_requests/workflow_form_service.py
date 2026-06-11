from django.contrib.contenttypes.models import ContentType

from workflow.engine import start_workflow
from workflow.models import Workflow, WorkflowInstance

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

from tax_requests.constants import STAGE_FILE_FIELDS
from tax_requests.remittance_service import sync_remittance_report
from tax_requests.workflow_permissions import FK_FIELDS, can_user_act_on_tds_opinion

FILE_FIELDS = STAGE_FILE_FIELDS


def _file_field_url(value):
    if value and getattr(value, "name", None):
        return value.url
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

    if stage_name == "Initiated":
        if user == record.created_by or user.is_superuser:
            sections.add("master")
    elif section_key and can_user_act_on_tds_opinion(instance, user):
        sections.add(section_key)
    elif user.is_superuser and section_key:
        sections.add(section_key)

    return sorted(sections)


def get_visible_accordion_sections(current_stage_name):
    """Return accordion sections for completed stages and the current stage only."""
    stage_name = current_stage_name if current_stage_name in WORKFLOW_STAGE_NAMES else "Initiated"
    visible_stages = set(WORKFLOW_STAGE_NAMES[: WORKFLOW_STAGE_NAMES.index(stage_name) + 1])
    return [section for section in ACCORDION_SECTIONS if section["stage"] in visible_stages]


def _serialize_stage(record, section_key):
    related_name = RELATED_NAMES[section_key]
    stage_obj = getattr(record, related_name, None)
    if stage_obj is None:
        return {}
    fields = STAGE_MODEL_FIELDS[section_key]
    data = {}
    file_fields = set(FILE_FIELDS.get(section_key, []))
    for field in fields:
        value = getattr(stage_obj, field, None)
        if field in file_fields:
            data[field] = _file_field_url(value)
        else:
            data[field] = value
    return data


def _serialize_master(record):
    data = {"id": record.id, "request_code": record.request_code}
    file_fields = set(FILE_FIELDS.get("master", []))
    for field in MASTER_INITIATED_FIELDS:
        value = getattr(record, field, None)
        if field in ("company", "currency", "particular"):
            data[field] = getattr(record, f"{field}_id", None)
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

    stages_data = {"master": _serialize_master(record)}
    for section_key in STAGE_MODEL_FIELDS:
        stages_data[section_key] = _serialize_stage(record, section_key)

    return {
        "stages": WORKFLOW_STAGE_NAMES,
        "accordion_sections": get_visible_accordion_sections(current_stage),
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
        _apply_fields(
            record,
            MASTER_INITIATED_FIELDS,
            master_data,
            _extract_section_files(files, "master"),
        )
        record.last_updated_by = user
        record.save()

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
    workflow = _get_tds_opinion_workflow()
    if workflow:
        start_workflow(record, user, workflow=workflow)
    sync_remittance_report(record)
    return build_workflow_form_payload(record, user)
