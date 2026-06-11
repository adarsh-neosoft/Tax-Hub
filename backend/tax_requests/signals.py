from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver

from workflow.models import WorkflowInstance

from tax_requests.models import TDSOpinion
from tax_requests.remittance_service import sync_remittance_report


@receiver(post_save, sender=WorkflowInstance)
def sync_tds_opinion_workflow_status(sender, instance, **kwargs):
    if instance.content_type_id != ContentType.objects.get_for_model(TDSOpinion).id:
        return

    try:
        record = TDSOpinion.objects.get(pk=instance.object_id)
    except TDSOpinion.DoesNotExist:
        return

    if instance.status == "approved":
        record.status = "Approved"
        record.open_with = "Approved"
    elif instance.status == "rejected":
        record.status = "Rejected"
        record.open_with = "Rejected"
    elif instance.status == "returned":
        record.status = "Returned"
        record.open_with = "Initiated"
        record.revert = True
    elif instance.current_stage:
        record.status = instance.current_stage.name
        record.open_with = instance.current_stage.name
        record.revert = False
    else:
        return

    record.save(update_fields=["status", "open_with", "revert", "last_updated_at"])
    sync_remittance_report(record)


@receiver(post_save, sender=TDSOpinion)
def sync_remittance_on_tds_save(sender, instance, **kwargs):
    if instance.is_deleted:
        return
    sync_remittance_report(instance)
