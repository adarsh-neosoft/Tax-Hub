from django.db import models
from api.base_model import BaseModel


class TPStudyReport(BaseModel):
    report_name = models.CharField(
        max_length=255
    )

    report_year = models.CharField(
        max_length=20,
        blank=True,
        null=True
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
        "dropdown_fields": ["id", "report_name"],
        "search_fields": [
            "report_name",
            "report_year"
        ],
        "filter_fields": ["report_year"],
        "list_display_fields": [
            "report_name",
            "report_year",
            "is_active"
        ],
        "form_display_fields": "__all__",
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "TP Study Report",
        "url": "tp-study-report",
        "ordering": 21,
        "api_path": "masters/TPStudyReport",
    }

    class Meta:
        db_table = "tp_study_report"
        app_label = "masters"