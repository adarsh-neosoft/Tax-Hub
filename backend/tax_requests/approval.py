from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from tax_requests.models import ApprovalLink, Form146Stage
from tax_requests.services.approval_service import ApprovalService
from tax_requests.services.form146_comparison_service import run_and_save_comparison


class ApprovalView(APIView):
    """
    External CA Approval API

    GET  -> Load request details using approval token
    POST -> Approve / Reject / Return (to be implemented)
    """

    permission_classes = [AllowAny]

    def get(self, request, token):
        try:
            data = ApprovalService.get_request_data(token)

            request_obj = data["request"]

            # Relative URL — the frontend appends this to its API base
            download_url = (
                f"/api/tax_requests/tdsopinion/"
                f"{request_obj.id}/download-form146/"
                f"?approval_token={token}"
            )

            # Upload URL — frontend can use this to upload the Form 146 PDF
            upload_url = (
                f"/api/tax_requests/approval/{token}/upload-form146/"
            )

            # Comparison status URL — frontend can check comparison status
            comparison_url = (
                f"/api/tax_requests/tdsopinion/"
                f"{request_obj.id}/download-form146-comparison/"
            )

            return Response(
                {
                    "success": True,
                    "request_id": request_obj.id,
                    "request_code": request_obj.request_code,
                    "workflow_status": data["workflow_instance"].status,
                    "current_stage": (
                        data["workflow_instance"].current_stage.name
                        if data["workflow_instance"].current_stage
                        else None
                    ),
                    "payload": data["payload"],
                    "download_form146_url": download_url,
                    "upload_form146_url": upload_url,
                    "comparison_status_url": comparison_url,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return Response(
                {
                    "success": False,
                    "message": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    # def post(self, request, token):
    #     """
    #     We will implement this in the next step.
    #     """

    #     return Response(
    #         {
    #             "success": False,
    #             "message": "POST API is not implemented yet.",
    #         },
    #         status=status.HTTP_501_NOT_IMPLEMENTED,
    #     )
    
    def post(self, request, token):
        """
        External CA Approve / Reject / Return
        """

        try:

            action = request.data.get("action")
            remarks = request.data.get("remarks", "")
            return_stage = request.data.get("return_stage")

            if not action:
                return Response(
                    {
                        "success": False,
                        "message": "Action is required.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # -------------------------------
            # Approve
            # -------------------------------

            if action == "approve":

                result = ApprovalService.approve(
                    token=token,
                    remarks=remarks,
                )

            # -------------------------------
            # Reject
            # -------------------------------

            elif action == "reject":

                result = ApprovalService.reject(
                    token=token,
                    remarks=remarks,
                )

            # -------------------------------
            # Return / Revert
            # -------------------------------

            elif action == "return":

                if not return_stage:
                    return Response(
                        {
                            "success": False,
                            "message": "Please select return stage.",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                result = ApprovalService.return_request(
                    token=token,
                    return_stage=return_stage,
                    remarks=remarks,
                )

            else:

                return Response(
                    {
                        "success": False,
                        "message": "Invalid action.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                result,
                status=status.HTTP_200_OK,
            )

        except Exception as exc:

            return Response(
                {
                    "success": False,
                    "message": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ApprovalUploadForm146View(APIView):
    """
    External CA uploads Form 146 PDF on the approval page (no Save button).
    Instantly saves the file and auto-generates the comparison.
    """

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, token):
        try:
            # Validate the approval token
            approval = ApprovalLink.objects.filter(
                token=token,
                is_valid=True,
            ).select_related("tds_opinion").first()

            if not approval:
                return Response(
                    {"detail": "Invalid or expired approval link."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            opinion = approval.tds_opinion

            if opinion.is_deleted:
                return Response(
                    {"detail": "Request not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get the uploaded file
            uploaded_file = request.FILES.get("form_146_attachment")
            if not uploaded_file:
                return Response(
                    {"detail": "No Form 146 PDF file uploaded."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get or create the Form 146 stage
            form_146_stage, _ = Form146Stage.objects.get_or_create(
                tds_opinion=opinion
            )

            # Save the uploaded file to the stage
            form_146_stage.form_146_attachment.save(
                uploaded_file.name,
                uploaded_file,
                save=True,
            )

            # Auto-generate the comparison
            run_and_save_comparison(opinion, form_146_stage)

            # Re-fetch to get updated comparison data
            form_146_stage.refresh_from_db()

            return Response(
                {
                    "success": True,
                    "comparison_status": form_146_stage.comparison_status,
                    "ack_number": form_146_stage.ack_number,
                    "download_form_146_comparison": (
                        form_146_stage.download_form_146_comparison.url
                        if form_146_stage.download_form_146_comparison
                        and form_146_stage.download_form_146_comparison.name
                        else None
                    ),
                    "form_146_attachment": (
                        form_146_stage.form_146_attachment.url
                        if form_146_stage.form_146_attachment
                        and form_146_stage.form_146_attachment.name
                        else None
                    ),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return Response(
                {
                    "success": False,
                    "message": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
