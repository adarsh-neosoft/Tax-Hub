from django.db import models
from api.base_model import BaseModel


class DocumentMaster(BaseModel):
    document_name = models.CharField(
        max_length=255,
        unique=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "document_name"],
        "search_fields": ["document_name"],
        "filter_fields": ["document_name"],
        "list_display_fields": [
            "document_name",
            "is_active"
        ],
        "form_display_fields": [
            "document_name",
            "is_active"
        ],
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Document Master",
        "url": "document-master",
        "ordering": 9,
        "api_path": "masters/DocumentMaster",
    }

    class Meta:
        db_table = "document_master"
        app_label = "masters"