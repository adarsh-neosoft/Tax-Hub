from django.db import models
from api.base_model import BaseModel


class Period(BaseModel):
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "category"],
        "search_fields": ["category"],
        "filter_fields": ["category"],
        "list_display_fields": ["category", "description", "is_active"],
        "form_display_fields": ["category", "description", "is_active"],
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Period",
        "url": "period",
        "ordering": 4,
        "api_path": "masters/period",
    }

    class Meta:
        db_table = "period"
        app_label = "masters"