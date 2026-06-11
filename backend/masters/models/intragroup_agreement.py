from django.db import models
from api.base_model import BaseModel


class IntragroupAgreement(BaseModel):
    agreement_name = models.CharField(
        max_length=255
    )

    agreement_type = models.CharField(
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
        "dropdown_fields": ["id", "agreement_name"],
        "search_fields": ["agreement_name"],
        "filter_fields": ["agreement_type"],
        "list_display_fields": [
            "agreement_name",
            "agreement_type",
            "is_active"
        ],
        "form_display_fields": "__all__",
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Intragroup Agreement",
        "url": "intragroup-agreement",
        "ordering": 19,
        "api_path": "masters/IntragroupAgreement",
    }

    class Meta:
        db_table = "intragroup_agreement"
        app_label = "masters"