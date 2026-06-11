from django.db import models
from api.base_model import BaseModel


class LawRule(BaseModel):
    rule_no = models.CharField(
        max_length=100,
        unique=True
    )

    rule_description = models.TextField(
        blank=True,
        null=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "rule_no"],
        "search_fields": [
            "rule_no",
            "rule_description"
        ],
        "filter_fields": [
            "rule_no"
        ],
        "list_display_fields": [
            "rule_no",
            "rule_description",
            "is_active"
        ],
        "form_display_fields": [
            "rule_no",
            "rule_description",
            "is_active"
        ],
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Law Rule",
        "url": "law-rule",
        "ordering": 11,
        "api_path": "masters/LawRule",
    }

    class Meta:
        db_table = "law_rule"
        app_label = "masters"