from django.db import models
from api.base_model import BaseModel


class TDSRate(BaseModel):

    tds_rate = models.DecimalField(
        max_digits=10,
        decimal_places=3
    )

    api_config = {
        "search_fields": [
            "tds_rate",
        ],

        "filter_fields": [
            "tds_rate",
        ],

        "list_display_fields": [
            "tds_rate",
            "is_active",
        ],

        "form_display_fields": [
            "tds_rate",
            "is_active",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "TDS Rate",
        "url": "tds-rate",
        "ordering": 20,
        "api_path": "masters/TDSRate",
    }

    class Meta:
        db_table = "tds_rate"
        app_label = "masters"