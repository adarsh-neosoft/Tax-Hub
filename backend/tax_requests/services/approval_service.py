from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from workflow.models import WorkflowInstance
from workflow.engine import process_external_action
from tax_requests.models import ApprovalLink, TDSOpinion
from tax_requests.workflow_form_service import build_workflow_form_payload


class ApprovalService:

    @staticmethod
    def get_approval_link(token):
        """
        Returns the active ApprovalLink for the given token.
        """

        approval = ApprovalLink.objects.filter(
            token=token,
            is_valid=True,
        ).select_related(
            "tds_opinion",
            "external_ca",
        ).first()

        if not approval:
            raise Exception("Invalid or expired approval link.")

        return approval

    @staticmethod
    def get_workflow_instance(tds_opinion):
        """
        Returns WorkflowInstance for the request.
        """

        content_type = ContentType.objects.get_for_model(TDSOpinion)

        instance = WorkflowInstance.objects.filter(
            content_type=content_type,
            object_id=tds_opinion.id,
        ).select_related(
            "workflow",
            "current_stage",
        ).first()

        if not instance:
            raise Exception("Workflow instance not found.")

        return instance

    @staticmethod
    def get_request_data(token):
        """
        Used by GET Approval API.
        """

        approval = ApprovalService.get_approval_link(token)

        request = approval.tds_opinion

        workflow_instance = ApprovalService.get_workflow_instance(
            request
        )

        payload = build_workflow_form_payload(
            request,
            workflow_instance.initiated_by,
        )

        return {
            "approval": approval,
            "request": request,
            "workflow_instance": workflow_instance,
            "payload": payload,
        }
    
    @staticmethod
    @transaction.atomic
    def approve(token, remarks=""):
        """
        Approve request from External CA.
        """

        # Validate approval link
        approval = ApprovalService.get_approval_link(token)

        request = approval.tds_opinion

        workflow_instance = ApprovalService.get_workflow_instance(
            request
        )

        success, message = process_external_action(
            instance=workflow_instance,
            approval_link=approval,
            action="approve",
            comment=remarks,
        )

        if not success:
            raise Exception(message)

        # ------------------------------------------------------------------
        # Optional:
        # Keep TDSOpinion synchronized with WorkflowInstance
        # ------------------------------------------------------------------

        if workflow_instance.current_stage:
            request.status = workflow_instance.current_stage.name
            request.open_with = workflow_instance.current_stage.name
        else:
            request.status = workflow_instance.status
            request.open_with = ""

        request.save(
            update_fields=[
                "status",
                "open_with",
            ]
        )

        # ------------------------------------------------------------------
        # Mark approval link
        # ------------------------------------------------------------------

        approval.is_approved = True
        approval.is_valid = False
        approval.save(update_fields=["is_approved", "is_valid"])

        return {
            "success": True,
            "message": message,
            "action": "approved",
            "request_id": request.id,
            "request_code": request.request_code,
            "current_stage": (
                workflow_instance.current_stage.name
                if workflow_instance.current_stage
                else None
            ),
            "workflow_status": workflow_instance.status,
        }
    
    @staticmethod
    @transaction.atomic
    def reject(token, remarks=""):
        """
        Reject request from External CA.
        """

        # Validate approval link
        approval = ApprovalService.get_approval_link(token)

        request = approval.tds_opinion

        workflow_instance = ApprovalService.get_workflow_instance(
            request
        )

        success, message = process_external_action(
            instance=workflow_instance,
            approval_link=approval,
            action="reject",
            comment=remarks,
        )

        if not success:
            raise Exception(message)

        # Sync TDS Opinion status with workflow
        request.status = workflow_instance.status
        request.open_with = ""
        request.revert = False

        request.save(
            update_fields=[
                "status",
                "open_with",
                "revert",
            ]
        )

        # Mark approval link as rejected
        approval.is_approved = False
        approval.is_valid = False
        approval.save(update_fields=["is_approved", "is_valid"])

        return {
            "success": True,
            "message": message,
            "action": "rejected",
            "request_id": request.id,
            "request_code": request.request_code,
            "workflow_status": workflow_instance.status,
            "current_stage": (
                workflow_instance.current_stage.name
                if workflow_instance.current_stage
                else None
            ),
        }
    
    @staticmethod
    @transaction.atomic
    def return_request(
        token,
        return_stage,
        remarks="",
    ):
        """
        Return request from External CA.
        """

        approval = ApprovalService.get_approval_link(token)

        request = approval.tds_opinion

        workflow_instance = ApprovalService.get_workflow_instance(
            request
        )

        success, message = process_external_action(
            instance=workflow_instance,
            approval_link=approval,
            action="return",
            comment=remarks,
            return_stage=return_stage,
        )

        if not success:
            raise Exception(message)

        request.status = "Returned"
        request.open_with = return_stage
        request.revert = True

        request.save(
            update_fields=[
                "status",
                "open_with",
                "revert",
            ]
        )

        approval.is_approved = False
        approval.is_valid = False
        approval.save(update_fields=["is_approved", "is_valid"])

        return {
            "success": True,
            "message": message,
            "action": "returned",
            "request_id": request.id,
            "request_code": request.request_code,
            "current_stage": workflow_instance.current_stage.name,
            "workflow_status": workflow_instance.status,
        }