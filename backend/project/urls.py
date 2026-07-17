"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from registration.views import (
    FormManagementListCreateView,
    FormManagementDetailView,
    ComplianceManagementListCreateView,
    ComplianceManagementDetailView,
    FormManagementByPanView,
)
from tax_requests.public_views import PublicDropdownView
from tax_requests.workflow_views import TDSOpinionRecordWorkflowView
from reports.views import RemittanceCancelledListView, RemittanceListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/workflow/record/<str:app_label>/<str:model_name>/<int:object_id>/",
        TDSOpinionRecordWorkflowView.as_view(),
    ),
    path("api/workflow/", include("workflow.urls")),  # Must be before api/
    path("api/tax_requests/", include("tax_requests.urls")),
    # Public dropdown endpoints for the External CA approval page
    # Only matches models in the PublicDropdownView's allowed list
    # Must be BEFORE the generic api.urls so they take precedence
    re_path(
        r"^api/masters/(?P<model_name>(?i:tdsrate|tdssection|type15cb|externalca|currency|bank|rbipurposecode|rbipurposesubcode|supplier|country|natureofservice|legalentity|vendorstatus|particular|purchaseorder))/dropdown$",
        PublicDropdownView.as_view(),
        kwargs={"app_label": "masters"},
    ),
    # Custom list views for Remittance Report — registered before generic api.urls
    # so they take precedence over the auto-generated list endpoint
    path(
        "api/reports/remittance-cancelled/",
        RemittanceCancelledListView.as_view(),
        kwargs={"app_label": "reports", "model_name": "remittancereport"},
    ),
    path(
        "api/reports/remittancereport/",
        RemittanceListView.as_view(),
        kwargs={"app_label": "reports", "model_name": "remittancereport"},
    ),
    # Custom Form Management endpoints — registered before generic api.urls
    # so they take precedence over the auto-generated endpoints
    path(
        "api/registration/formmanagement/",
        FormManagementListCreateView.as_view(),
        kwargs={"app_label": "registration", "model_name": "formmanagement"},
    ),
    path(
        "api/registration/formmanagement/<str:pk>/",
        FormManagementDetailView.as_view(),
        kwargs={"app_label": "registration", "model_name": "formmanagement"},
    ),
    # Custom Compliance Management endpoints — registered before generic api.urls
    path(
        "api/registration/compliancemanagement/",
        ComplianceManagementListCreateView.as_view(),
        kwargs={"app_label": "registration", "model_name": "compliancemanagement"},
    ),
    path(
        "api/registration/compliancemanagement/<str:pk>/",
        ComplianceManagementDetailView.as_view(),
        kwargs={"app_label": "registration", "model_name": "compliancemanagement"},
    ),
    # Endpoint to fetch FormManagement data by PAN (for Compliance Management auto-population)
    path(
        "api/registration/formmanagement-by-pan/<int:pan_id>/",
        FormManagementByPanView.as_view(),
    ),
    path("api/", include("api.urls")),
    path("api/", include("rest_framework.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
