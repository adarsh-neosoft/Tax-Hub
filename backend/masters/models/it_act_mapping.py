from django.db import models
from api.base_model import BaseModel


class ITActMapping(BaseModel):
    section_2025 = models.CharField(
        max_length=100
    )

    section_1961 = models.CharField(
        max_length=100
    )

    chapter_2025 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    chapter_1961 = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "section_2025"],
        "search_fields": [
            "section_2025",
            "section_1961"
        ],
        "filter_fields": [],
        "list_display_fields": [
            "section_2025",
            "section_1961",
            "is_active"
        ],
        "form_display_fields": "__all__",
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "IT Act Mapping",
        "url": "it-act-mapping",
        "ordering": 22,
        "api_path": "masters/ITActMapping",
    }

    class Meta:
        db_table = "it_act_mapping"
        app_label = "masters"