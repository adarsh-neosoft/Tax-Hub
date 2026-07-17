from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.decorators import cache_model_api_response
from api.views import GenericAPIView, _build_generic_serializer
from registration.models import FormManagement, ComplianceManagement


def _get_form_management_serializer():
    """Build a custom serializer for FormManagement that resolves
    form_no.form_no and form_description from the FK relationship
    on top of the generic serializer's behavior (file handling,
    encryption, audit logging, and other FK resolutions)."""

    base_serializer = _build_generic_serializer(FormManagement)

    class FormManagementSerializer(base_serializer):
        """Extends the generic serializer to also resolve form_no.form_no
        and form_no.form_description — since include_related_field_values
        can only handle one entry per FK field."""

        def to_representation(self, instance):
            data = super().to_representation(instance)

            # Resolve form_no.form_no and form_no.form_description from FK
            if instance.form_no_id:
                try:
                    fm = instance.form_no
                    if fm:
                        data["form_no"] = fm.form_no
                        data["form_no.form_no"] = fm.form_no
                        data["form_no.form_description"] = fm.form_description
                        # Populate form_description for real-time display
                        if not data.get("form_description"):
                            data["form_description"] = fm.form_description
                except Exception:
                    pass

            return data

    return FormManagementSerializer


class FormManagementListCreateView(GenericAPIView, ListCreateAPIView):
    """Custom list/create view for FormManagement with form_no FK resolution.

    Inherits from both api.views.GenericAPIView (custom filtering, OPTIONS
    metadata) and DRF's ListCreateAPIView (provides filter_queryset,
    paginate_queryset, get_serializer, etc. that the mixins require).
    """

    model = FormManagement
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return _get_form_management_serializer()

    @cache_model_api_response
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class FormManagementDetailView(GenericAPIView, RetrieveUpdateDestroyAPIView):
    """Custom retrieve/update/destroy view for FormManagement.

    Inherits from both api.views.GenericAPIView (custom OPTIONS metadata)
    and DRF's RetrieveUpdateDestroyAPIView (provides get_serializer,
    filter_queryset, etc. that the mixins require).
    """

    model = FormManagement
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return _get_form_management_serializer()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.model.objects.filter(pk=kwargs["pk"]).update(
            is_deleted=True, is_active=False
        )
        return Response({"message": "Successfully deleted"})


class ComplianceManagementListCreateView(GenericAPIView, ListCreateAPIView):
    """Custom list/create view for ComplianceManagement with resolved related fields."""

    model = ComplianceManagement
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return _build_generic_serializer(self.model)

    @cache_model_api_response
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ComplianceManagementDetailView(GenericAPIView, RetrieveUpdateDestroyAPIView):
    """Custom retrieve/update/destroy view for ComplianceManagement."""

    model = ComplianceManagement
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return _build_generic_serializer(self.model)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.model.objects.filter(pk=kwargs["pk"]).update(
            is_deleted=True, is_active=False
        )
        return Response({"message": "Successfully deleted"})


class FormManagementByPanView(APIView):
    """
    Returns the latest FormManagement records and aggregated data for a given PAN.
    Used by the Compliance Management form to auto-populate fields.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pan_id):
        # Fetch the latest FormManagement record for this PAN
        latest_record = FormManagement.objects.filter(
            pan_id=pan_id,
            is_deleted=False,
        ).order_by("-created_at").first()

        # Fetch all FormManagement records for document links
        form_records = FormManagement.objects.filter(
            pan_id=pan_id,
            is_deleted=False,
        ).order_by("-created_at").values(
            "id",
            "form_no__form_no",
            "form_description",
            "acknowledgement_upload",
            "form_upload",
            "statutory_timelines",
            "internal_timelines",
            "actual_completion_date",
            "status_by_user",
        )[:10]

        data = {
            "latest": {
                "statutory_timelines": getattr(latest_record, "statutory_timelines", None) if latest_record else None,
                "internal_timelines": getattr(latest_record, "internal_timelines", None) if latest_record else None,
                "actual_completion_date": getattr(latest_record, "actual_completion_date", None) if latest_record else None,
                "status_by_user": getattr(latest_record, "status_by_user", None) if latest_record else None,
            },
            "documents": list(form_records),
        }

        return Response(data)
