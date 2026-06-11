from django.db import models
from api.base_model import BaseModel


class FinancialYear(BaseModel):

    financial_year = models.CharField(
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
            "financial_year"
        ],

        "search_fields": [
            "financial_year"
        ],

        "filter_fields": [
            "financial_year"
        ],

        "list_display_fields": [
            "id",
            "financial_year",
            "is_active",
            "created_by",
            "created_at",
        ],

        "form_display_fields": [
            "financial_year",
            "is_active",
        ],

        "include_related_field_values": [
            "created_by",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Financial Year",
        "url": "financial-year",
        "ordering": 19,
        "api_path": "masters/financialyear",
    }

    class Meta:
        db_table = "financial_year"
        app_label = "masters"