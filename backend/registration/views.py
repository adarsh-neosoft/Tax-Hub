from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.decorators import cache_model_api_response
from api.views import GenericAPIView, _build_generic_serializer
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from registration.models import FormManagement, ComplianceManagement, OpinionManagement, ValuationReportManagement, DscTracker


def _make_m2m_resolving_serializer(model_class):
    """Factory for custom serializers that resolve team_members_involved M2M field."""
    base_serializer = _build_generic_serializer(model_class)

    class M2MResolvingSerializer(base_serializer):
        def to_representation(self, instance):
            data = super().to_representation(instance)

            # Resolve team_members_involved M2M to employee names
            names = list(
                instance.team_members_involved.values_list("employee_name", flat=True)
            )
            if names:
                data["team_members_involved.employee_name"] = ", ".join(names)

            return data

    return M2MResolvingSerializer


def _get_opinion_management_serializer():
    return _make_m2m_resolving_serializer(OpinionManagement)


def _get_valuation_report_management_serializer():
    return _make_m2m_resolving_serializer(ValuationReportManagement)


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
                        # Save the raw FK id BEFORE overwriting data["form_no"]
                        data["form_no.id"] = instance.form_no_id
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


class OpinionManagementListCreateView(GenericAPIView, ListCreateAPIView):
    """Custom list/create view for OpinionManagement with M2M team_members_involved resolution."""

    model = OpinionManagement
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return _get_opinion_management_serializer()

    @cache_model_api_response
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class OpinionManagementDetailView(GenericAPIView, RetrieveUpdateDestroyAPIView):
    """Custom retrieve/update/destroy view for OpinionManagement."""

    model = OpinionManagement
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return _get_opinion_management_serializer()

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


class ValuationReportManagementListCreateView(GenericAPIView, ListCreateAPIView):
    """Custom list/create view for ValuationReportManagement with M2M team_members_involved resolution."""

    model = ValuationReportManagement
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return _get_valuation_report_management_serializer()

    @cache_model_api_response
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ValuationReportManagementDetailView(GenericAPIView, RetrieveUpdateDestroyAPIView):
    """Custom retrieve/update/destroy view for ValuationReportManagement."""

    model = ValuationReportManagement
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return _get_valuation_report_management_serializer()

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


class DscExpiringSoonView(APIView):
    """
    Returns DSCs that are expiring within 30 days (future) and need user attention (popup).
    Already-expired DSCs are excluded. Includes:
      - DSCs where user has NOT responded yet (new_dsc_prepared is NULL)
      - DSCs where user selected "No" (new_dsc_prepared is False) — keeps showing until Yes or expiry
    Excludes:
      - DSCs where user selected "Yes" (new_dsc_prepared is True)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        thirty_days = today + timedelta(days=30)

        expiring_dscs = DscTracker.objects.filter(
            to_date__lte=thirty_days,
            to_date__gte=today,
            is_deleted=False,
        ).exclude(new_dsc_prepared=True)

        results = []
        for dsc in expiring_dscs:
            results.append({
                "id": dsc.id,
                "director_name": dsc.name.director_name if dsc.name else "N/A",
                "pan": dsc.pan,
                "father_name": dsc.father_name,
                "from_date": str(dsc.from_date) if dsc.from_date else None,
                "to_date": str(dsc.to_date) if dsc.to_date else None,
            })

        return Response(results)


class DscUpdateNewDscPreparedView(APIView):
    """
    Update the new_dsc_prepared field for a DSC record.
    Accepts: {"new_dsc_prepared": true/false}
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            dsc = DscTracker.objects.get(pk=pk, is_deleted=False)
        except DscTracker.DoesNotExist:
            return Response(
                {"detail": "DSC record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        value = request.data.get("new_dsc_prepared")
        if value is None:
            return Response(
                {"detail": "new_dsc_prepared is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        dsc.new_dsc_prepared = bool(value)
        dsc.new_dsc_prepared_at = timezone.now()
        dsc.save(update_fields=["new_dsc_prepared", "new_dsc_prepared_at", "last_updated_at"])

        return Response({
            "id": dsc.id,
            "new_dsc_prepared": dsc.new_dsc_prepared,
            "new_dsc_prepared_at": dsc.new_dsc_prepared_at,
        })


class DscBatchUpdateNewDscPreparedView(APIView):
    """
    Batch update new_dsc_prepared for multiple DSC records at once.
    Accepts: {"updates": [{"id": 1, "new_dsc_prepared": true}, ...]}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        updates = request.data.get("updates", [])
        if not isinstance(updates, list) or len(updates) == 0:
            return Response(
                {"detail": "Provide a non-empty list of updates."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        errors = []

        for item in updates:
            pk = item.get("id")
            value = item.get("new_dsc_prepared")

            if pk is None or value is None:
                errors.append({"id": pk, "detail": "Both id and new_dsc_prepared are required."})
                continue

            try:
                dsc = DscTracker.objects.get(pk=pk, is_deleted=False)
                dsc.new_dsc_prepared = bool(value)
                dsc.new_dsc_prepared_at = timezone.now()
                dsc.save(update_fields=["new_dsc_prepared", "new_dsc_prepared_at", "last_updated_at"])
                results.append({
                    "id": dsc.id,
                    "new_dsc_prepared": dsc.new_dsc_prepared,
                    "new_dsc_prepared_at": dsc.new_dsc_prepared_at,
                })
            except DscTracker.DoesNotExist:
                errors.append({"id": pk, "detail": "DSC record not found."})

        return Response({
            "success": results,
            "errors": errors,
        })


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
