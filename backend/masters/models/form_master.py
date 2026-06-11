from django.db import models
from api.base_model import BaseModel


class FormMaster(BaseModel):
    form_no = models.CharField(
        max_length=100,
        unique=True
    )

    form_description = models.TextField(
        blank=True,
        null=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "form_no"],
        "search_fields": [
            "form_no",
            "form_description"
        ],
        "filter_fields": [
            "form_no"
        ],
        "list_display_fields": [
            "form_no",
            "form_description",
            "is_active"
        ],
        "form_display_fields": [
            "form_no",
            "form_description",
            "is_active"
        ],
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Form Master",
        "url": "form-master",
        "ordering": 10,
        "api_path": "masters/FormMaster",
    }

    class Meta:
        db_table = "form_master"
        app_label = "masters"