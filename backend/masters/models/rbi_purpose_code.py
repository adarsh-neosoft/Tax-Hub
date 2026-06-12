from django.db import models
from api.base_model import BaseModel


class RBIPurposeCode(BaseModel):

    rbi_purpose_code = models.CharField(
        max_length=500,
        unique=True
    )

    model_config = {
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": [
            "rbi_purpose_code",
        ],

        "search_fields": [
            "rbi_purpose_code",
        ],

        "list_display_fields": [
            "rbi_purpose_code",
            "is_active",
        ],

        "form_display_fields": [
            "rbi_purpose_code",
            "is_active",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "RBI Purpose Code",
        "url": "rbi-purpose-code",
        "ordering": 18,
        "api_path": "masters/RBIPurposeCode",
    }

    class Meta:
        db_table = "rbi_purpose_code"
        app_label = "masters"