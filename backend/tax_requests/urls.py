from django.urls import path

from tax_requests.views import (
    TDSOpinionWorkflowFormCreateView,
    TDSOpinionWorkflowFormDetailView,
    CheckExistingVendorRequestView,
)

urlpatterns = [
    path(
        "tdsopinion/workflow-form/",
        TDSOpinionWorkflowFormCreateView.as_view(),
        name="tdsopinion-workflow-form-create",
    ),
    path(
        "tdsopinion/<int:pk>/workflow-form/",
        TDSOpinionWorkflowFormDetailView.as_view(),
        name="tdsopinion-workflow-form-detail",
    ),
    path(
        "tdsopinion/check-existing/",
        CheckExistingVendorRequestView.as_view(),
        name="check-existing-vendor",
    ),
]
