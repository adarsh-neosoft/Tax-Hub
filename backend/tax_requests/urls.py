from django.urls import path

from tax_requests.views import (
    TDSOpinionWorkflowFormCreateView,
    TDSOpinionWorkflowFormDetailView,
    CheckExistingVendorRequestView,
    FetchExchangeRateView,
    DownloadForm146View,
    DownloadForm146ComparisonView,
)

from tax_requests.approval import ApprovalView, ApprovalUploadForm146View

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
    path(
        "tdsopinion/fetch-exchange-rate/",
        FetchExchangeRateView.as_view(),
        name="tdsopinion-fetch-exchange-rate",
    ),
    path(
        "tdsopinion/<int:pk>/download-form146/",
        DownloadForm146View.as_view(),
        name="download-form146",
    ),
    path(
        "tdsopinion/<int:pk>/download-form146-comparison/",
        DownloadForm146ComparisonView.as_view(),
        name="download-form146-comparison",
    ),
    path(
        "approval/<uuid:token>/",
        ApprovalView.as_view(),
        name="external-ca-approval",
    ),
    path(
        "approval/<uuid:token>/upload-form146/",
        ApprovalUploadForm146View.as_view(),
        name="approval-upload-form146",
    ),
]


