from django.db import models
from api.base_model import BaseModel


class TPBenchmarking(BaseModel):
    benchmarking_name = models.CharField(
        max_length=255
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
        "dropdown_fields": ["id", "benchmarking_name"],
        "search_fields": ["benchmarking_name"],
        "filter_fields": ["benchmarking_name"],
        "list_display_fields": [
            "benchmarking_name",
            "is_active"
        ],
        "form_display_fields": "__all__",
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "TP Benchmarking",
        "url": "tp-benchmarking",
        "ordering": 20,
        "api_path": "masters/TPBenchmarking",
    }

    class Meta:
        db_table = "tp_benchmarking"
        app_label = "masters"