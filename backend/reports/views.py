from reports.models import RemittanceReport
from api.views import GenericListAPIView


class RemittanceListView(GenericListAPIView):
    """
    Main Remittance Report list view.
    Excludes cancelled requests (they appear in the Cancelled tab instead).
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.exclude(status="Cancelled")


class RemittanceCancelledListView(GenericListAPIView):
    """
    Custom API endpoint for cancelled remittance reports.
    Only returns records with status="Cancelled".
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(status="Cancelled")
