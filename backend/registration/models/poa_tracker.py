import os

from django.conf import settings
from django.db import models
from api.base_model import BaseModel


def poa_repository_upload_to(instance, filename):
    return os.path.join("poa_repository", filename)


class PoaTracker(BaseModel):

    entity_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Name of Entity",
    )

    poa_holder_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Name of POA Holder",
    )

    forum = models.ForeignKey(
        "masters.Forum",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Forum",
    )

    pan = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="PAN",
    )

    from_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="From Date",
    )

    to_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="To Date",
    )

    poa_repository = models.FileField(
        upload_to=poa_repository_upload_to,
        blank=True,
        null=True,
        verbose_name="POA Repository",
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": [
            "id",
            "forum",
        ],
        "search_fields": [
            "entity_name",
            "poa_holder_name",
            "pan"
        ],
        "filter_fields": [
            "forum",
        ],
        "list_display_fields": [
            "entity_name",
            "poa_holder_name",
            "forum.forum_name",
            "pan",
            "from_date",
            "to_date",
            "poa_repository",
        ],
        "form_display_fields": [
            "entity_name",
            "poa_holder_name",
            "forum",
            "pan",
            "from_date",
            "to_date",
            "poa_repository",
        ],
        "include_related_field_values": [
            "forum.forum_name",
        ],
    }

    ui_config = {
        "navigation_header": "Registration",
        "title": "POA Tracker",
        "url": "poa-tracker",
        "ordering": 3,
        "api_path": "registration/poatracker",
    }

    class Meta:
        db_table = "poa_tracker"
        app_label = "registration"
        verbose_name = "POA Tracker"
        verbose_name_plural = "POA Tracker"

    def save(self, *args, **kwargs):
        # Normalize file paths: strip MEDIA_ROOT prefix so Django generates correct URLs
        for field in self._meta.get_fields():
            if isinstance(field, models.FileField):
                raw_value = self.__dict__.get(field.attname)
                if raw_value and isinstance(raw_value, str) and settings.MEDIA_ROOT in raw_value:
                    self.__dict__[field.attname] = raw_value.replace(settings.MEDIA_ROOT, "").lstrip("/")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.entity_name or f"POA #{self.id}"
