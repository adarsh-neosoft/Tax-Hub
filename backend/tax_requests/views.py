from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tax_requests.models import TDSOpinion
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
