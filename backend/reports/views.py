from reports.models import RemittanceReport
from api.views import GenericListAPIView


class RemittanceCancelledListView(GenericListAPIView):
    """
    Custom API endpoint for cancelled/returned remittance reports.
    Only returns records with status="Returned".
    Matches the old project pattern of a dedicated view for cancelled requests.
    """

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(revert=True)
