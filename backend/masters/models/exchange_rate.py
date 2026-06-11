from django.db import models
from api.base_model import BaseModel


class ExchangeRate(BaseModel):
    date = models.DateField()
    currency = models.CharField(max_length=20)
    exchange_rate = models.DecimalField(
        max_digits=18,
        decimal_places=4
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "currency"],
        "search_fields": ["currency"],
        "filter_fields": ["currency", "date"],
        "list_display_fields": ["date", "currency", "exchange_rate", "is_active"],
        "form_display_fields": ["date", "currency", "exchange_rate", "is_active"],
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Exchange Rate",
        "url": "exchange-rate",
        "ordering": 6,
        "api_path": "masters/ExchangeRate",
    }

    class Meta:
        db_table = "exchange_rate"
        app_label = "masters"