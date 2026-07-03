from datetime import datetime
from io import BytesIO

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tax_requests.constants import FILE_VALIDITY_MAP
from tax_requests.models import TDSOpinion, Form146Stage
from django.http import FileResponse

from tax_requests.services.form146_excel_generator import (Form146ExcelGenerator,)
from tax_requests.services.form146_comparison_service import generate_comparison_excel
from rest_framework.permissions import IsAuthenticated
from tax_requests.workflow_form_service import (
    build_workflow_form_payload,
    create_tds_opinion_with_form,
    save_workflow_form,
)


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
    

class DownloadForm146View(APIView):

    permission_classes = [IsAuthenticated]

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


class DownloadForm146ComparisonView(APIView):

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

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

        if not form_146_stage.form_146_attachment:
            return Response(
                {
                    "detail": "No Form 146 PDF uploaded yet. Please upload the PDF form in the 'Form 146' field and save, then try again."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = generate_comparison_excel(opinion, form_146_stage)
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            return Response(
                {"detail": f"Comparison failed: {str(exc)}"},
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

        return FileResponse(
            BytesIO(file_content),
            as_attachment=True,
            filename=result["filename"],
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
