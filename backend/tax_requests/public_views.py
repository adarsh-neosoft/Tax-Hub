"""
Public views for the External CA approval page.

The approval page is accessed via a token link (no authentication).
These views serve dropdown/reference data that the frontend needs
without requiring JWT authentication.
"""

from django.apps import apps
from django.db import models
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class PublicDropdownView(APIView):
    """
    Returns dropdown data for a given model without requiring authentication.
    Used by the External CA approval page to load reference/lookup data.
    """

    permission_classes = [AllowAny]

    def get(self, request, app_label, model_name):
        try:
            model_cls = apps.get_model(app_label=app_label, model_name=model_name)
        except LookupError:
            return Response(
                {"detail": f"Model {app_label}.{model_name} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only allow reading non-sensitive master/reference data
        # Use lowercase model names for case-insensitive matching
        allowed_models = {
            ("masters", "tdsrate"),
            ("masters", "tdssection"),
            ("masters", "type15cb"),
            ("masters", "externalca"),
            ("masters", "currency"),
            ("masters", "bank"),
            ("masters", "rbipurposecode"),
            ("masters", "rbipurposesubcode"),
            ("masters", "supplier"),
            ("masters", "country"),
            ("masters", "natureofservice"),
            ("masters", "legalentity"),
            ("masters", "vendorstatus"),
            ("masters", "particular"),
            ("masters", "purchaseorder"),
        }

        # Normalize to lowercase for case-insensitive comparison
        # Frontend may pass "LDCCertificate", "legalentity", "NatureOfService", etc.
        if (app_label, model_name.lower()) not in allowed_models:
            return Response(
                {"detail": "Access denied."},
                status=status.HTTP_403_FORBIDDEN,
            )

        qs = model_cls.objects.filter(is_deleted=False)

        # Apply filter_fields from query params (e.g. ?rbi_purpose_code=5)
        filter_fields = getattr(model_cls, "api_config", {}).get("filter_fields", [])
        for field in filter_fields:
            value = request.query_params.get(field)
            if value:
                qs = qs.filter(**{field: value})

        # Support search — use search_fields from model config
        search = request.query_params.get("search")
        if search:
            search_fields = getattr(model_cls, "api_config", {}).get("search_fields", [])
            q_objects = models.Q()
            for field_name in search_fields:
                if "." in field_name:
                    fk, related = field_name.split(".")
                    q_objects |= models.Q(**{f"{fk}__{related}__icontains": search})
                else:
                    q_objects |= models.Q(**{f"{field_name}__icontains": search})
            if q_objects:
                qs = qs.filter(q_objects)

        dropdown_fields = getattr(model_cls, "api_config", {}).get("dropdown_fields", []) or ["id"]

        results = []
        for obj in qs:
            entry = {"id": obj.id}
            for field in dropdown_fields:
                if "." in field:
                    parts = field.split(".")
                    related = getattr(obj, parts[0], None)
                    entry[field] = str(getattr(related, parts[1], "")) if related else ""
                else:
                    val = getattr(obj, field, None)
                    entry[field] = str(val) if val is not None else ""
            results.append(entry)

        return Response(results[:50])
