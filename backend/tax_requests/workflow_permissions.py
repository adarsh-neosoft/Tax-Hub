from workflow.engine import can_user_act as _base_can_user_act

from tax_requests.models import TDSOpinion

FK_FIELDS = frozenset({"company", "currency", "particular"})


def can_user_act_on_tds_opinion(instance, user):
    """Allow stage approvers, superusers, and the request creator at Initiated."""
    if not instance or instance.status != "pending" or not instance.current_stage:
        return False

    if _base_can_user_act(instance, user) or user.is_superuser:
        return True

    if instance.current_stage.name != "Initiated":
        return False

    try:
        record = TDSOpinion.objects.get(pk=instance.object_id, is_deleted=False)
    except TDSOpinion.DoesNotExist:
        return False

    return record.created_by_id == user.id
