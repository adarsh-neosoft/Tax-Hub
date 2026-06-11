from django.db import models
from api.base_model import BaseModel


class CurrencyRate(BaseModel):

    currency = models.ForeignKey(
        "masters.Currency",
        on_delete=models.PROTECT
    )

    value_date = models.DateField()

    ttbuy = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    api_config = {
        "search_fields": [
            "currency__currency_name",
        ],

        "filter_fields": [
            "currency",
            "value_date",
        ],

        "list_display_fields": [
            "currency",
            "value_date",
            "ttbuy",
            "is_active",
        ],

        "form_display_fields": [
            "currency",
            "value_date",
            "ttbuy",
            "is_active",
        ],

        "include_related_field_values": [
            "currency"
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Currency Rate",
        "url": "currency-rate",
        "ordering": 4,
        "api_path": "masters/CurrencyRate",
    }

    class Meta:
        db_table = "currency_rate"
        app_label = "masters"