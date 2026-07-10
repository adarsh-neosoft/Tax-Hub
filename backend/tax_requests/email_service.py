import smtplib
import traceback

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

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


def get_email_context(tds_opinion, approval_link):
    """
    Builds context for HTML email.
    """

    print("\n========== get_email_context() ==========")

    bank = tds_opinion.bank_detail

    context = {
        "request_id": tds_opinion.request_code,
        "company_code": tds_opinion.company_code,
        "company_name": (
            tds_opinion.company.entity_name
            if tds_opinion.company
            else ""
        ),
        "vendor_code": tds_opinion.vendor_code,
        "vendor_name": tds_opinion.vendor_name,
        "invoice_number": tds_opinion.invoice_number,
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


def send_external_ca_email(tds_opinion):
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