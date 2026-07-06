from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from tax_requests.services.approval_service import ApprovalService


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

            return Response(
                {
                    "success": True,
                    "request_id": data["request"].id,
                    "request_code": data["request"].request_code,
                    "workflow_status": data["workflow_instance"].status,
                    "current_stage": (
                        data["workflow_instance"].current_stage.name
                        if data["workflow_instance"].current_stage
                        else None
                    ),
                    "payload": data["payload"],
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