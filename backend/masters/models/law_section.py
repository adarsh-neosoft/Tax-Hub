from django.db import models
from api.base_model import BaseModel

class LawSection(BaseModel):

    law = models.ForeignKey(
        "masters.Law",
        on_delete=models.CASCADE
    )

    section_2025 = models.CharField(max_length=100)
    section_1961 = models.CharField(max_length=100)

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

    description = models.TextField(
        blank=True,
        null=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "section_2025"],
        "search_fields": ["section_2025", "section_1961"],
        "filter_fields": ["law"],
        "list_display_fields": [
            "law",
            "section_2025",
            "section_1961",
            "is_active",
        ],
        "form_display_fields": "__all__",
        "include_related_field_values": ["law"],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Law Section",
        "url": "law-section",
        "ordering": 14,
        "api_path": "masters/LawSection",
    }

    class Meta:
        db_table = "law_section"
        app_label = "masters"