from django.db import models
from api.base_model import BaseModel


class Law(BaseModel):
    law_name = models.CharField(
        max_length=255,
        unique=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "law_name"],
        "search_fields": ["law_name"],
        "filter_fields": ["law_name"],
        "list_display_fields": [
            "law_name",
            "is_active"
        ],
        "form_display_fields": [
            "law_name",
            "is_active"
        ],
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Law",
        "url": "law",
        "ordering": 3,
        "api_path": "masters/law",
    }

    class Meta:
        db_table = "law"
        app_label = "masters"