from django.db import models
from api.base_model import BaseModel


class Role(BaseModel):
    role_type = models.CharField(max_length=100)
    rights_involved = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=20, blank=True, null=True)

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "role_type"],
        "search_fields": ["role_type"],
        "filter_fields": ["role_type"],
        "list_display_fields": ["role_type", "level", "is_active"],
        "form_display_fields": ["role_type", "rights_involved", "level", "is_active"],
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Role",
        "url": "role",
        "ordering": 2,
        "api_path": "masters/role",
    }

    class Meta:
        db_table = "role"
        app_label = "masters"