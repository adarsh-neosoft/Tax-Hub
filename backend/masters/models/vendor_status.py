from django.db import models
from api.base_model import BaseModel


class VendorStatus(BaseModel):

    status_name = models.CharField(
        max_length=100,
        unique=True,
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "status_name",
        ],

        "search_fields": [
            "status_name",
        ],

        "filter_fields": [
            "status_name",
            "is_active",
        ],

        "list_display_fields": [
            "status_name",
            "is_active",
        ],

        "form_display_fields": [
            "status_name",
            "is_active",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Vendor Status",
        "url": "vendor-status",
        "ordering": 31,
        "api_path": "masters/vendorstatus",
    }

    def __str__(self):
        return self.status_name

    class Meta:
        db_table = "vendor_status"
        app_label = "masters"