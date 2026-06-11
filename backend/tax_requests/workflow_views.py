from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from workflow.engine import can_user_act
from workflow.models import WorkflowInstance
from workflow.serializers import WorkflowInstanceSerializer

from tax_requests.workflow_permissions import can_user_act_on_tds_opinion


class TDSOpinionRecordWorkflowView(APIView):
    """Workflow status for a record, including can_act for approve/reject buttons."""

    permission_classes = [IsAuthenticated]

    def get(self, request, app_label, model_name, object_id):
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name)
        except ContentType.DoesNotExist:
            return Response({"detail": "Model not found"}, status=404)

        instances = (
            WorkflowInstance.objects.filter(content_type=ct, object_id=object_id)
            .select_related("workflow", "current_stage", "initiated_by")
            .prefetch_related("actions__actor", "actions__acted_on_behalf_of")
            .order_by("-attempt")[:5]
        )

        data = []
        for instance in instances:
            item = WorkflowInstanceSerializer(instance).data
            if model_name == "tdsopinion":
                item["can_act"] = can_user_act_on_tds_opinion(instance, request.user)
            else:
                item["can_act"] = can_user_act(instance, request.user)
            data.append(item)

        return Response(data)
