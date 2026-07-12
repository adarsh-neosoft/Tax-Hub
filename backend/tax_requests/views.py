from datetime import datetime
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tax_requests.constants import FILE_VALIDITY_MAP, STAGE_APPROVER_GROUPS, WORKFLOW_STAGE_NAMES
from tax_requests.models import TDSOpinion, ApprovalLink, Form146Stage
from masters.models import Currency, ExchangeRate
from django.http import FileResponse

from tax_requests.services.form146_excel_generator import (Form146ExcelGenerator,)
from tax_requests.services.form146_comparison_service import generate_comparison_excel
from rest_framework.permissions import IsAuthenticated
from tax_requests.workflow_form_service import (
    build_workflow_form_payload,
    create_tds_opinion_with_form,
    save_workflow_form,
)

from api.views import GenericListAPIView
from django.db.models import Q


def _parse_request_payload(request):
    import json

    content_type = request.content_type or ""
    if "multipart" in content_type or request.FILES:
        raw = request.data.get("payload") if hasattr(request, "data") else None
        if raw is None and hasattr(request, "POST"):
            raw = request.POST.get("payload")
        if raw is None:
            raw = "{}"
        if isinstance(raw, str):
            payload = json.loads(raw) if raw else {}
        elif isinstance(raw, dict):
            payload = raw
        else:
            payload = {}
        return payload, request.FILES

    data = request.data
    if isinstance(data, dict) and "payload" in data and "master" not in data:
        inner = data["payload"]
        if isinstance(inner, str):
            return json.loads(inner) if inner else {}, {}
        if isinstance(inner, dict):
            return inner, {}
    return data, {}


class TDSOpinionWorkflowFormCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        try:
            payload, files = _parse_request_payload(request)
            result = create_tds_opinion_with_form(request.user, payload, files)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class TDSOpinionWorkflowFormDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, pk):
        record = get_object_or_404(TDSOpinion, pk=pk, is_deleted=False)
        return Response(build_workflow_form_payload(record, request.user))

    def patch(self, request, pk):
        record = get_object_or_404(TDSOpinion, pk=pk, is_deleted=False)
        try:
            payload, files = _parse_request_payload(request)
            result = save_workflow_form(record, request.user, payload, files)
            return Response(result)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        

class CheckExistingVendorRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        company = request.GET.get("company")
        vendor = request.GET.get("vendor")
        invoice_date_str = request.GET.get("invoice_date")

        existing = (
            TDSOpinion.objects
            .filter(
                company=company,
                vendor=vendor,
                is_deleted=False
            )
            .order_by("-id")
            .first()
        )

        if not existing:
            return Response({
                "exists": False
            })

        response_data = {
            "exists": True,
            "request_id": existing.id,
            "pan_number": existing.pan_number,
            "tin_number": existing.tin_number,
        }

        # If invoice_date is provided, return valid file URLs
        if invoice_date_str:
            try:
                invoice_date = datetime.strptime(invoice_date_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                invoice_date = None

            if invoice_date:
                valid_files = {}

                # invoice_file has no valid_upto - always include if present
                if existing.invoice_file:
                    valid_files["invoice_file"] = existing.invoice_file.url

                # Check files with validity periods
                for file_field, valid_field in FILE_VALIDITY_MAP.items():
                    file_value = getattr(existing, file_field, None)
                    valid_upto = getattr(existing, valid_field, None)
                    if file_value and valid_upto and valid_upto >= invoice_date:
                        valid_files[file_field] = file_value.url

                response_data["valid_files"] = valid_files
                response_data["valid_file_fields"] = list(valid_files.keys())

                # Return corresponding valid_upto dates for each valid file
                valid_file_upto_dates = {}
                for file_field in valid_files:
                    if file_field in FILE_VALIDITY_MAP:
                        valid_field = FILE_VALIDITY_MAP[file_field]
                        valid_upto = getattr(existing, valid_field, None)
                        if valid_upto:
                            valid_file_upto_dates[file_field] = valid_upto.isoformat()
                response_data["valid_file_upto_dates"] = valid_file_upto_dates

        return Response(response_data)
    

class FetchExchangeRateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date = request.GET.get("date")
        currency_id = request.GET.get("currency_id")

        if not date or not currency_id:
            return Response(
                {"detail": "Both 'date' and 'currency_id' parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            currency = Currency.objects.get(id=currency_id)
        except Currency.DoesNotExist:
            return Response(
                {"detail": "Currency not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        exchange_rate = ExchangeRate.objects.filter(
            date=date,
            currency=currency.currency,
            is_deleted=False,
        ).first()

        if not exchange_rate:
            return Response({
                "found": False,
                "message": f"No exchange rate found for {currency.currency} on {date}",
            })

        return Response({
            "found": True,
            "exchange_rate": str(exchange_rate.exchange_rate),
            "date": date,
            "currency": currency.currency,
        })


class DownloadForm146View(APIView):

    permission_classes = [IsAuthenticated]

    def check_permissions(self, request):
        """
        Allow unauthenticated access if there is a valid (unexpired) approval link
        for this TDSOpinion — the External CA's token has already been validated
        when they opened the approval page.
        """
        if not request.user.is_authenticated:
            pk = self.kwargs.get("pk")
            # Any valid (unexpired) approval link for this TDSOpinion is sufficient
            has_valid_link = ApprovalLink.objects.filter(
                tds_opinion_id=pk,
                is_valid=True,
            ).exists()
            if has_valid_link:
                return  # Skip IsAuthenticated check
        return super().check_permissions(request)

    def get(self, request, pk):

        opinion = get_object_or_404(
            TDSOpinion,
            pk=pk,
            is_deleted=False,
        )

        generator = Form146ExcelGenerator(opinion)

        file_path = generator.generate()

        return FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=file_path.name,
        )


class TDSOpinionListView(GenericListAPIView):
    """
    List view for TDS Opinion requests that filters requests based on the user's
    group membership and the current workflow stage's approver group.

    - Superusers see all requests.
    - Non-superusers only see requests whose current `status` (which tracks the
      active workflow stage) is mapped to one of the user's Django auth Groups.
    - Approved/completed requests are visible to all authenticated users.
    - Rejected / Returned requests (which go back to Initiated) are visible to
      the group mapped to "Initiated" (AP).
    - Records with no workflow instance (status is null) are also included.
    """

    def initial(self, request, *args, **kwargs):
        kwargs.setdefault("app_label", "tax_requests")
        kwargs.setdefault("model_name", "tdsopinion")
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset().exclude(status="Cancelled")
        user = self.request.user

        if not user or user.is_anonymous:
            return qs.none()

        if user.is_superuser:
            return qs

        # Determine which stages the user's groups are approvers for
        user_group_names = set(user.groups.values_list("name", flat=True))

        visible_stages = set()
        for stage_name, group_name in STAGE_APPROVER_GROUPS.items():
            if group_name in user_group_names:
                visible_stages.add(stage_name)

        if not visible_stages:
            return qs.none()

        # Rejected / Returned requests go back to Initiated — the creator
        # (AP group) needs to see them to fix & resubmit
        visible_stages.add("Rejected")
        visible_stages.add("Returned")

        # Filter: status is in visible_stages, OR status is NULL/empty
        # (null status may happen before a workflow instance is created)
        return qs.filter(
            Q(status__in=visible_stages)
            | Q(status__isnull=True)
        )


class DownloadForm146ComparisonView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def check_permissions(self, request):
        """
        Allow unauthenticated access if there is a valid (unexpired) approval link
        for this TDSOpinion (same logic as DownloadForm146View).
        """
        if not request.user.is_authenticated:
            pk = self.kwargs.get("pk")
            has_valid_link = ApprovalLink.objects.filter(
                tds_opinion_id=pk,
                is_valid=True,
            ).exists()
            if has_valid_link:
                return
        return super().check_permissions(request)

    def post(self, request, pk):

        opinion = get_object_or_404(
            TDSOpinion,
            pk=pk,
            is_deleted=False,
        )

        # Get or create the Form 146 stage (OneToOne relationship)
        form_146_stage, _ = Form146Stage.objects.get_or_create(
            tds_opinion=opinion
        )

        # If a file was uploaded in the request, save it first
        # Try both direct field name and prefixed (workflow form pattern)
        uploaded_file = request.FILES.get("form_146_attachment")
        if not uploaded_file:
            uploaded_file = request.FILES.get("form_146.form_146_attachment")
        
        file_was_uploaded_now = False
        if uploaded_file:
            form_146_stage.form_146_attachment.save(
                uploaded_file.name,
                uploaded_file,
                save=True,
            )
            form_146_stage.refresh_from_db()
            file_was_uploaded_now = True

        # If no file was uploaded now and no existing attachment, just return current status
        if not file_was_uploaded_now and not form_146_stage.form_146_attachment:
            return Response(
                {
                    "success": True,
                    "comparison_status": None,
                    "ack_number": None,
                    "download_form_146_comparison": None,
                    "form_146_attachment": None,
                },
                status=status.HTTP_200_OK,
            )

        # Generate comparison (from newly uploaded file or from existing attachment)
        # Only regenerate if file was just uploaded or if comparison hasn't been generated yet
        if file_was_uploaded_now or not form_146_stage.comparison_status:
            try:
                result = generate_comparison_excel(opinion, form_146_stage)
            except ValueError as exc:
                return Response(
                    {
                        "success": False,
                        "comparison_status": "Error",
                        "detail": str(exc),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as exc:
                return Response(
                    {
                        "success": False,
                        "comparison_status": "Error",
                        "detail": f"Comparison failed: {str(exc)}",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Save the comparison file to the stage
            file_path = result["comparison_file_path"]
            with open(file_path, "rb") as f:
                file_content = f.read()

            form_146_stage.download_form_146_comparison.save(
                result["filename"],
                ContentFile(file_content),
                save=False,
            )
            form_146_stage.comparison_status = result["status"]
            if result["ack_number"]:
                form_146_stage.ack_number = result["ack_number"]
            form_146_stage.save()

        # Return JSON with status and download URLs
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

    def get(self, request, pk):
        """Return the previously generated comparison file, if available."""

        opinion = get_object_or_404(
            TDSOpinion,
            pk=pk,
            is_deleted=False,
        )
        form_146_stage = getattr(opinion, "form_146", None)

        if (
            form_146_stage
            and form_146_stage.download_form_146_comparison
            and form_146_stage.download_form_146_comparison.name
        ):
            return FileResponse(
                form_146_stage.download_form_146_comparison,
                as_attachment=True,
            )

        return Response(
            {
                "detail": "No comparison file available. Please upload the Form 146 PDF and click 'Download Form 146 Comparison'."
            },
            status=status.HTTP_404_NOT_FOUND,
        )
