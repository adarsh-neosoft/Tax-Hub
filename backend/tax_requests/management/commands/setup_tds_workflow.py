"""
Create the TDS Opinion approval workflow with all required stages.
Run: python manage.py setup_tds_workflow
"""
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from tax_request.constants import WORKFLOW_STAGE_NAMES
from tax_request.models import TDSOpinion
from workflow.models import Workflow, WorkflowStage


class Command(BaseCommand):
    help = "Set up TDS Opinion multi-stage approval workflow"

    def handle(self, *args, **options):
        ct = ContentType.objects.get_for_model(TDSOpinion)
        workflow, created = Workflow.objects.get_or_create(
            name="TDS Opinion Approval",
            content_type=ct,
            defaults={
                "description": "Multi-stage TDS Opinion request approval flow",
                "is_active": True,
                "trigger_type": "manual",
                "allow_resubmission": True,
            },
        )

        if not created and workflow.stages.exists():
            self.stdout.write(self.style.WARNING("Workflow already exists with stages — skipping."))
            return

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created workflow: {workflow.name}"))

        for order, stage_name in enumerate(WORKFLOW_STAGE_NAMES, start=1):
            stage, stage_created = WorkflowStage.objects.get_or_create(
                workflow=workflow,
                order=order,
                defaults={
                    "name": stage_name,
                    "stage_type": "sequential",
                    "allow_return": order > 1,
                    "return_to": "previous_stage" if order > 1 else "initiator",
                },
            )
            if stage_created:
                self.stdout.write(f"  Stage {order}: {stage_name}")

        self.stdout.write(
            self.style.SUCCESS(
                "\nDone. Assign approvers to each stage in Admin → Workflows → TDS Opinion Approval."
            )
        )
