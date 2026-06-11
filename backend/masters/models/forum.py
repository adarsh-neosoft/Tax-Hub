from django.db import models
from api.base_model import BaseModel


class Forum(BaseModel):
    forum_name = models.CharField(max_length=255)

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "forum_name"],
        "search_fields": ["forum_name"],
        "filter_fields": ["forum_name"],
        "list_display_fields": ["forum_name", "is_active"],
        "form_display_fields": ["forum_name", "is_active"],
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Forum",
        "url": "forum",
        "ordering": 7,
        "api_path": "masters/forum",
    }

    class Meta:
        db_table = "forum"
        app_label = "masters"