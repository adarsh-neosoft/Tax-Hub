from django.db import models
from api.base_model import BaseModel


class NatureOfService(BaseModel):

    service_description = models.TextField()

    api_config = {
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

    class Meta:
        db_table = "nature_of_service"
        app_label = "masters"