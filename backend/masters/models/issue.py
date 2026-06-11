from django.db import models
from api.base_model import BaseModel


class Issue(BaseModel):

    issue_type = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    issue_title = models.CharField(
        max_length=500,
        blank=True,
        null=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "issue_title"
        ],

        "search_fields": [
            "issue_type",
            "issue_title"
        ],

        "filter_fields": [
            "issue_type"
        ],

        "list_display_fields": [
            "issue_type",
            "issue_title",
            "is_active",
            "created_by",
            "created_at",
        ],

        "form_display_fields": [
            "issue_type",
            "issue_title",
            "is_active",
        ],

        "include_related_field_values": [
            "created_by",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Issue",
        "url": "issue",
        "ordering": 8,
        "api_path": "masters/issue",
    }

    class Meta:
        db_table = "issue"
        app_label = "masters"