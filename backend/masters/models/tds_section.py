from django.db import models
from api.base_model import BaseModel


class TDSSection(BaseModel):

    TDS_section = models.CharField(
        max_length=100
    )

    api_config = {
        "search_fields": [
            "TDS_section",
        ],

        "filter_fields": [
            "TDS_section",
        ],

        "list_display_fields": [
            "TDS_section",
            "is_active",
        ],

        "form_display_fields": [
            "TDS_section",
            "is_active",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "TDS Section",
        "url": "tds-section",
        "ordering": 21,
        "api_path": "masters/TDSSection",
    }

    class Meta:
        db_table = "tds_section"
        app_label = "masters"