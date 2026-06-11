from django.db import models
from api.base_model import BaseModel


class AmountUnit(BaseModel):
    amount_in = models.CharField(max_length=100)

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "amount_in"],
        "search_fields": ["amount_in"],
        "filter_fields": ["amount_in"],
        "list_display_fields": ["amount_in", "is_active"],
        "form_display_fields": ["amount_in", "is_active"],
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Amount Unit",
        "url": "amount-unit",
        "ordering": 5,
        "api_path": "masters/AmountUnit",
    }

    class Meta:
        db_table = "amount_unit"
        app_label = "masters"