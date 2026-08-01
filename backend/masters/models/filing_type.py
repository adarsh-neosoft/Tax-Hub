from django.db import models
from api.base_model import BaseModel


class FilingType(BaseModel):

    name_of_form = models.CharField(
        max_length=255,
        unique=True
    )

    description = models.TextField(
        blank=True,
        null=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "name_of_form"
        ],

        "search_fields": [
            "name_of_form",
            "description",
        ],

        "filter_fields": [
            "name_of_form",
            "is_active",
        ],

        "list_display_fields": [
            "name_of_form",
            "description",
            "is_active",
        ],

        "form_display_fields": [
            "name_of_form",
            "description",
            "is_active",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Filing Type",
        "url": "filing-type",
        "ordering": 23,
        "api_path": "masters/FilingType",
    }

    class Meta:
        db_table = "filing_type"
        app_label = "masters"
