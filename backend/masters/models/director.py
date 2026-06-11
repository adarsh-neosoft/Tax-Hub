from django.db import models
from api.base_model import BaseModel

class Director(BaseModel):
    director_name = models.CharField(max_length=255)

    pan = models.CharField(
        max_length=20
    )

    address = models.TextField()

    legal_entity = models.ForeignKey(
        "masters.LegalEntity",
        on_delete=models.CASCADE
    )

    date_from = models.DateField(
        null=True,
        blank=True
    )

    date_to = models.DateField(
        null=True,
        blank=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "director_name"],
        "search_fields": ["director_name", "pan"],
        "filter_fields": ["legal_entity"],
        "list_display_fields": [
            "director_name",
            "pan",
            "legal_entity",
            "is_active",
        ],
        "form_display_fields": "__all__",
        "include_related_field_values": ["legal_entity"],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Director",
        "url": "director",
        "ordering": 16,
        "api_path": "masters/director",
    }

    class Meta:
        db_table = "director"
        app_label = "masters"