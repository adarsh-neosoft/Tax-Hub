from django.db import models
from api.base_model import BaseModel


class Currency(BaseModel):

    currency = models.CharField(
        max_length=20,
        unique=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "currency"
        ],

        "search_fields": [
            "currency"
        ],

        "filter_fields": [
            "currency"
        ],

        "list_display_fields": [
            "id",
            "currency",
            "is_active",
            "created_by",
            "created_at",
        ],

        "form_display_fields": [
            "currency",
            "is_active",
        ],

        "include_related_field_values": [
            "created_by",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Currency",
        "url": "currency",
        "ordering": 21,
        "api_path": "masters/currency",
    }

    class Meta:
        db_table = "currency"
        app_label = "masters"