from django.db import models
from api.base_model import BaseModel


class Vertical(BaseModel):
    particulars = models.CharField(
        max_length=255,
        unique=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "particulars"],
        "search_fields": ["particulars"],
        "filter_fields": ["particulars"],
        "list_display_fields": [
            "particulars",
            "is_active",
            "created_at",
            "created_by",
        ],
        "form_display_fields": [
            "particulars",
            "is_active"
        ],
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Vertical",
        "url": "vertical",
        "ordering": 1,
        "api_path": "masters/vertical",
    }

    class Meta:
        db_table = "vertical"
        app_label = "masters"

