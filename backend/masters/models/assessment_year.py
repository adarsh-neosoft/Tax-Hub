from django.db import models
from api.base_model import BaseModel


class AssessmentYear(BaseModel):

    assessment_year = models.CharField(
        max_length=20,
        unique=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": [
            "id",
            "assessment_year"
        ],

        "search_fields": [
            "assessment_year"
        ],

        "filter_fields": [
            "assessment_year"
        ],

        "list_display_fields": [
            "id",
            "assessment_year",
            "is_active",
            "created_by",
            "created_at",
        ],

        "form_display_fields": [
            "assessment_year",
            "is_active",
        ],

        "include_related_field_values": [
            "created_by",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Assessment Year",
        "url": "assessment-year",
        "ordering": 18,
        "api_path": "masters/assessmentyear",
    }

    class Meta:
        db_table = "assessment_year"
        app_label = "masters"