from django.db import models
from api.base_model import BaseModel


class Type15CB(BaseModel):

    type_15cb = models.CharField(
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
            "type_15cb",
        ],

        "search_fields": [
            "type_15cb",
        ],

        "filter_fields": [
            "is_active",
        ],

        "list_display_fields": [
            "type_15cb",
            "is_active",
        ],

        "form_display_fields": [
            "type_15cb",
            "is_active",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Type 15CB",
        "url": "type-15cb",
        "ordering": 30,
        "api_path": "masters/Type15CB",
    }

    class Meta:
        db_table = "type_15cb"
        app_label = "masters"