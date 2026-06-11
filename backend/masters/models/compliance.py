from django.db import models
from api.base_model import BaseModel

class Compliance(BaseModel):
    compliance_name = models.CharField(max_length=255)

    frequency = models.CharField(
        max_length=100
    )

    period = models.ForeignKey(
        "masters.Period",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    law = models.ForeignKey(
        "masters.Law",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    vertical = models.ForeignKey(
        "masters.Vertical",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "compliance_name"],
        "search_fields": ["compliance_name"],
        "filter_fields": ["law", "vertical"],
        "list_display_fields": [
            "compliance_name",
            "frequency",
            "law",
            "is_active",
        ],
        "form_display_fields": "__all__",
        "include_related_field_values": [
            "law",
            "period",
            "vertical",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Compliance",
        "url": "compliance",
        "ordering": 15,
        "api_path": "masters/compliance",
    }

    class Meta:
        db_table = "compliance"
        app_label = "masters"