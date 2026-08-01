from django.db import models
from api.base_model import BaseModel

class Counsel(BaseModel):
    counsel_name = models.CharField(
        max_length=255,
        unique=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "counsel_name"
        ],

        "search_fields": [
            "counsel_name",
        ],

        "filter_fields": [
            "counsel_name",
            "is_active",
        ],

        "list_display_fields": [
            "counsel_name",
            "is_active",
        ],

        "form_display_fields": [
            "counsel_name",
            "is_active",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Counsel",
        "url": "counsel",
        "ordering": 22,
        "api_path": "masters/counsel",
    }