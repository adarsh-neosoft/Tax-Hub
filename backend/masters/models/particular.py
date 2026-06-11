from django.db import models
from api.base_model import BaseModel


class Particular(BaseModel):

    particular_name = models.CharField(
        max_length=255,
        unique=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "particular_name"
        ],

        "search_fields": [
            "particular_name"
        ],

        "filter_fields": [
            "particular_name"
        ],

        "list_display_fields": [
            "id",
            "particular_name",
            "is_active",
            "created_by",
            "created_at",
        ],

        "form_display_fields": [
            "particular_name",
            "is_active",
        ],

        "include_related_field_values": [
            "created_by",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Particular",
        "url": "particular",
        "ordering": 22,
        "api_path": "masters/particular",
    }

    class Meta:
        db_table = "particular"
        app_label = "masters"