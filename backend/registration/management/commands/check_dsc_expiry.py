import logging
from datetime import date, timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from registration.models import DscTracker

logger = logging.getLogger(__name__)

# Hardcoded recipient email as requested
RECIPIENT_EMAIL = "adarsh.dwivedi@neosofttech.com"
DAYS_BEFORE_EXPIRY = 30


class Command(BaseCommand):
    help = "Check for DSCs expiring within 30 days and send email reminders."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without sending emails, just log what would be done",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        today = timezone.now().date()
        thirty_days_from_now = today + timedelta(days=DAYS_BEFORE_EXPIRY)
        is_monday = today.weekday() == 0  # Monday = 0

        self.stdout.write(f"Running DSC expiry check on {today}")
        self.stdout.write(f"Looking for DSCs expiring on or before {thirty_days_from_now}")
        self.stdout.write(f"Today is{' ' if is_monday else ' NOT '}Monday")
        self.stdout.write("")

        # Find DSCs that are expiring within 30 days (to_date <= 30 days from now)
        # and are not deleted. Expired DSCs are excluded since they no longer
        # appear in the popup, so users can't respond to them.
        all_dscs = DscTracker.objects.filter(
            to_date__lte=thirty_days_from_now,
            to_date__gte=today,
            is_deleted=False,
        ).select_related("name")

        self.stdout.write(f"Found {len(all_dscs)} DSC(s) needing attention:")
        for dsc in all_dscs:
            self.stdout.write(f"  - {dsc} (expires: {dsc.to_date})")
        self.stdout.write("")

        for dsc in all_dscs:
            self._process_dsc(dsc, today, is_monday, dry_run)

        self.stdout.write(self.style.SUCCESS("DSC expiry check complete."))

    def _process_dsc(self, dsc, today, is_monday, dry_run):
        """Process a single DSC record: send reminders as needed."""
        days_remaining = (dsc.to_date - today).days if dsc.to_date else 0

        # Case 1: User said Yes to new DSC → no reminders at all
        if dsc.new_dsc_prepared is True:
            self.stdout.write(f"  [SKIP] {dsc}: New DSC already prepared. Skipping.")
            return

        # Case 2: Initial 30-day reminder not yet sent
        if not dsc.initial_reminder_sent:
            self._send_reminder(dsc, days_remaining, is_initial=True, dry_run=dry_run)
            if not dry_run:
                dsc.initial_reminder_sent = True
                dsc.last_reminder_sent = today
                dsc.save(update_fields=["initial_reminder_sent", "last_reminder_sent"])
            return

        # Case 3: Weekly Monday reminders — ONLY if user explicitly selected "No"
        if is_monday and dsc.new_dsc_prepared is False:
            # Check if we already sent a reminder this week (today)
            if dsc.last_reminder_sent == today:
                self.stdout.write(f"  [SKIP] {dsc}: Already sent reminder today ({today}).")
                return

            self._send_reminder(dsc, days_remaining, is_initial=False, dry_run=dry_run)
            if not dry_run:
                dsc.last_reminder_sent = today
                dsc.save(update_fields=["last_reminder_sent"])

    def _send_reminder(self, dsc, days_remaining, is_initial, dry_run=False):
        """Send the email reminder."""
        # Build context
        director_name = dsc.name.director_name if dsc.name else "N/A"
        context = {
            "director_name": director_name,
            "pan": dsc.pan or "N/A",
            "father_name": dsc.father_name or "N/A",
            "from_date": str(dsc.from_date) if dsc.from_date else "N/A",
            "to_date": str(dsc.to_date) if dsc.to_date else "N/A",
            "days_remaining": max(days_remaining, 0),
            "is_initial": is_initial,
        }

        try:
            html = render_to_string("emails/dsc_expiry_reminder.html", context)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  [ERROR] Template rendering failed: {e}"))
            return

        subject = (
            "DSC Expiry Reminder - Action Required"
            if is_initial
            else "Weekly Reminder: DSC Expiring Soon - Action Required"
        )

        self.stdout.write(f"  {'[DRY-RUN]' if dry_run else '[SEND]'} {dsc}:")
        self.stdout.write(f"    To: {RECIPIENT_EMAIL}")
        self.stdout.write(f"    Subject: {subject}")
        self.stdout.write(f"    Days remaining: {days_remaining}")
        self.stdout.write(f"    new_dsc_prepared: {dsc.new_dsc_prepared}")
        self.stdout.write(f"    initial_reminder_sent: {dsc.initial_reminder_sent}")
        self.stdout.write(f"    Type: {'Initial' if is_initial else 'Weekly Reminder'}")

        if dry_run:
            return

        # Print full email content to terminal with clear separators
        self.stdout.write(self.style.WARNING(f""))
        self.stdout.write(self.style.WARNING(f"  ╔══════════════════════════════════════════════════╗"))
        self.stdout.write(self.style.WARNING(f"  ║              EMAIL CONTENT BELOW                ║"))
        self.stdout.write(self.style.WARNING(f"  ╚══════════════════════════════════════════════════╝"))
        self.stdout.write(f"")
        self.stdout.write(f"  From: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"  To: {RECIPIENT_EMAIL}")
        self.stdout.write(f"  Subject: {subject}")
        self.stdout.write(f"")
        self.stdout.write(f"  ---------- HTML CONTENT START ----------")
        self.stdout.write(html)
        self.stdout.write(f"  ---------- HTML CONTENT END ----------")
        self.stdout.write(f"")

        try:
            email = EmailMultiAlternatives(
                subject=subject,
                body="Please open this email using an HTML compatible email client.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[RECIPIENT_EMAIL],
            )
            email.attach_alternative(html, "text/html")
            email.send(fail_silently=False)
            self.stdout.write(self.style.SUCCESS(f"  ✓ Email processed successfully (see content above)."))
            self.stdout.write(self.style.WARNING(f"  ══════════════════════════════════════════════════"))
            self.stdout.write(f"")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Email sending FAILED: {e}"))
