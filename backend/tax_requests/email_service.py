import smtplib
import traceback

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.contrib.contenttypes.models import ContentType
from workflow.models import WorkflowAction, WorkflowInstance

from tax_requests.models import ApprovalLink


def invalidate_old_links(tds_opinion, external_ca):
    """
    Only one approval link should remain active.
    """

    print("\n========== invalidate_old_links() ==========")
    print("Request:", tds_opinion.request_code)
    print("External CA:", external_ca)

    ApprovalLink.objects.filter(
        tds_opinion=tds_opinion,
        external_ca=external_ca,
        is_valid=True,
    ).update(is_valid=False)

    print("Previous approval links invalidated.")


def create_approval_link(tds_opinion, external_ca):
    """
    Creates a fresh approval token.
    """

    print("\n========== create_approval_link() ==========")

    invalidate_old_links(
        tds_opinion,
        external_ca,
    )

    approval = ApprovalLink.objects.create(
        tds_opinion=tds_opinion,
        external_ca=external_ca,
    )

    print("Approval Link Created Successfully")
    print("Approval ID:", approval.id)
    print("Approval Token:", approval.token)

    return approval


def build_approval_url(token):
    """
    Builds frontend approval url.
    """

    frontend = settings.FRONTEND_URL.rstrip("/")

    url = f"{frontend}/approval/{token}"

    print("\n========== build_approval_url() ==========")
    print("Approval URL:", url)

    return url


def get_email_context(tds_opinion, approval_link, user=None):
    """
    Builds context for HTML email.
    """

    print("\n========== get_email_context() ==========")

    bank = tds_opinion.bank_detail

    # Fetch workflow instance and latest action for audit trail
    ct = ContentType.objects.get_for_model(tds_opinion.__class__)
    workflow_instance = WorkflowInstance.objects.filter(
        content_type=ct,
        object_id=tds_opinion.id,
    ).select_related("current_stage").order_by("-attempt").first()

    latest_action = None
    if workflow_instance:
        latest_action = WorkflowAction.objects.filter(
            instance=workflow_instance,
        ).select_related("actor", "stage").order_by("-acted_at").first()

    # Determine Previous Stage — from the latest action's stage
    previous_stage = ""
    if latest_action and latest_action.stage:
        previous_stage = latest_action.stage.name

    # Determine New Stage — current workflow stage
    new_stage = ""
    if workflow_instance and workflow_instance.current_stage:
        new_stage = workflow_instance.current_stage.name
    elif workflow_instance and workflow_instance.status == "approved":
        new_stage = "Approved"

    # Determine Action description
    action = "Submitted"
    if latest_action:
        action_map = {
            "approve": "Approved",
            "reject": "Rejected",
            "return": "Returned",
            "cancel": "Cancelled",
        }
        action = action_map.get(latest_action.action, latest_action.action.capitalize())

    # Determine Performed By
    performed_by = ""
    if latest_action and latest_action.actor:
        performed_by = latest_action.actor.get_full_name() or latest_action.actor.username
    elif user:
        performed_by = user.get_full_name() or user.username

    # Determine Remarks — from latest action comment or bank detail remarks
    remarks = ""
    if latest_action and latest_action.comment:
        remarks = latest_action.comment
    elif bank and bank.bank_remarks:
        remarks = bank.bank_remarks

    # Build vendor display
    vendor_parts = []
    if tds_opinion.vendor_name:
        vendor_parts.append(tds_opinion.vendor_name)
    if tds_opinion.vendor_code:
        vendor_parts.append(f"({tds_opinion.vendor_code})")
    vendor_display = " ".join(vendor_parts) if vendor_parts else ""

    context = {
        "request_id": tds_opinion.request_code,
        "request_code": tds_opinion.request_code,
        "vendor": vendor_display,
        "previous_stage": previous_stage,
        "new_stage": new_stage,
        "action": action,
        "performed_by": performed_by,
        "remarks": remarks,
        "company_code": tds_opinion.company_code,
        "company_name": (
            tds_opinion.company.entity_name
            if tds_opinion.company
            else ""
        ),
        "vendor_code": tds_opinion.vendor_code,
        "vendor_name": tds_opinion.vendor_name,
        "invoice_number": tds_opinion.invoice_number,
        "invoice_amount": (
            str(tds_opinion.opinion_invoice_amount)
            if tds_opinion.opinion_invoice_amount
            else ""
        ),
        "form_type": (
            bank.form_146_type.type_15cb
            if bank.form_146_type
            else ""
        ),
        "reverted": "No",
        "approval_link": build_approval_url(
            approval_link.token
        ),
    }

    print("Email Context:")
    for key, value in context.items():
        print(f"{key}: {value}")

    return context


def send_external_ca_email(tds_opinion, user=None):
    """
    Sends approval email to External CA.
    """

    print("\n====================================================", flush=True)
    print("Entered send_external_ca_email()", flush=True)
    print("====================================================", flush=True)

    print("Request Code:", tds_opinion.request_code, flush=True)

    bank = tds_opinion.bank_detail

    print("External CA:", bank.external_ca, flush=True)
    print("Form Type:", bank.form_146_type, flush=True)

    if not bank.external_ca:
        print("No External CA selected. Email will not be sent.", flush=True)
        return

    approval = create_approval_link(
        tds_opinion,
        bank.external_ca,
    )

    context = get_email_context(
        tds_opinion,
        approval,
        user=user,
    )

    print("\nRendering HTML template...")

    try:
        html = render_to_string(
            "emails/external_ca_approval.html",
            context,
        )
        print("HTML template rendered successfully.")

    except Exception:
        print("========== TEMPLATE ERROR ==========")
        traceback.print_exc()
        raise

    print("HTML template rendered successfully.")

    # Save preview for debugging
    try:
        import os
        preview_dir = os.path.join(settings.BASE_DIR, "logs", "email_previews")
        os.makedirs(preview_dir, exist_ok=True)
        preview_path = os.path.join(preview_dir, f"external_ca_preview_{tds_opinion.id}.html")
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Email preview saved to: {preview_path}", flush=True)
    except Exception as e:
        print(f"Could not save email preview: {e}", flush=True)

    print("\nCreating Email Object...")

    email = EmailMultiAlternatives(
        subject="15CA - Pending for Approval",
        body="Please open this email using an HTML compatible email client.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[bank.external_ca.email_id],
    )

    email.attach_alternative(
        html,
        "text/html",
    )

    print("Recipient:", bank.external_ca.email_id)
    print("Subject: 15CA - Pending for Approval")

    print("\nAttempting to send email...")

    try:
        email.send(fail_silently=False)
        print("\nEmail sent successfully.")
        print("====================================================\n")

    except smtplib.SMTPAuthenticationError:
        print("\nEmail sending FAILED - SMTP Authentication Error")
        traceback.print_exc()
        print("====================================================\n")
        raise Exception("Authentication unsuccessful")

    except Exception as e:
        print("\nEmail sending FAILED")
        print("Error:", str(e))
        traceback.print_exc()
        print("====================================================\n")
        raise