from django.db import models
from api.base_model import BaseModel


class NatureOfService(BaseModel):

    service_description = models.TextField()

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "service_description",
        ],

        "search_fields": [
            "service_description",
        ],

        "filter_fields": [
            "service_description",
        ],

        "list_display_fields": [
            "service_description",
            "is_active",
        ],

        "form_display_fields": [
            "service_description",
            "is_active",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Nature Of Service",
        "url": "nature-of-service",
        "ordering": 13,
        "api_path": "masters/NatureOfService",
    }

    def __str__(self):
        return self.service_description

    class Meta:
        db_table = "nature_of_service"
        app_label = "masters"