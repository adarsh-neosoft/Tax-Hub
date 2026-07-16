from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.decorators import cache_model_api_response
from api.views import GenericAPIView, _build_generic_serializer
from registration.models import FormManagement


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
