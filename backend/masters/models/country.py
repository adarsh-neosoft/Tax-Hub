from django.db import models
from api.base_model import BaseModel


class Country(BaseModel):

    country_name = models.CharField(
        max_length=255,
        unique=True
    )

    code = models.CharField(
        max_length=10,
        unique=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "country_name"
        ],

        "search_fields": [
            "country_name",
            "code",
        ],

        "filter_fields": [
            "country_name",
            "code",
            "is_active",
        ],

        "list_display_fields": [
            "country_name",
            "code",
            "is_active",
        ],

        "form_display_fields": [
            "country_name",
            "code",
            "is_active",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Country",
        "url": "country",
        "ordering": 21,
        "api_path": "masters/country",
    }

    class Meta:
        db_table = "country"
        app_label = "masters"