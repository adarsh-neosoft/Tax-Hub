from django.db import models
from api.base_model import BaseModel


class EntityName(BaseModel):

    entity_name = models.CharField(
        max_length=255
    )

    entity_code = models.CharField(
        max_length=100,
        unique=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "entity_name"
        ],

        "search_fields": [
            "entity_name",
            "entity_code"
        ],

        "filter_fields": [
            "entity_name"
        ],

        "list_display_fields": [
            "id",
            "entity_name",
            "entity_code",
            "is_active",
            "created_by",
        ],

        "form_display_fields": [
            "entity_name",
            "entity_code",
            "is_active",
        ],

        "include_related_field_values": [
            "created_by",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Entity Name",
        "url": "entity-name",
        "ordering": 20,
        "api_path": "masters/entityname",
    }

    # def __str__(self):
    #     return self.entity_name

    class Meta:
        db_table = "entity_name"
        app_label = "masters"