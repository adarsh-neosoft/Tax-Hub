import os

from django.conf import settings
from django.db import models
from api.base_model import BaseModel


def opinion_management_upload_to(instance, filename):
    return os.path.join("registration/opinion_management", filename)


class OpinionManagement(BaseModel):
    entity = models.ForeignKey(
        "masters.LegalEntity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Name of Entity",
    )

    team_members_involved = models.ManyToManyField(
        "masters.UserMaster",
        blank=True,
        verbose_name="Team Members Involved",
        help_text="Select multiple team members from User Master",
    )

    name_of_counsel_firm = models.CharField(
        max_length=255,
        verbose_name="Name of Counsel/ Firm",
    )

    purpose = models.CharField(
        max_length=500,
        verbose_name="Purpose",
        blank=True,
        null=True,
    )

    date_of_opinion = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date of Opinion",
    )

    attachment = models.FileField(
        upload_to=opinion_management_upload_to,
        blank=True,
        null=True,
        verbose_name="Attachment (Download)",
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": [
            "id",
            "entity",
        ],
        "search_fields": [
            "name_of_counsel_firm",
            "purpose",
        ],
        "filter_fields": [
            "entity",
        ],
        "list_display_fields": [
            "entity",
            "name_of_counsel_firm",
            "purpose",
            "date_of_opinion",
            "attachment",
            "team_members_involved.employee_name",
        ],
        "form_display_fields": [
            "entity",
            "team_members_involved",
            "name_of_counsel_firm",
            "purpose",
            "date_of_opinion",
            "attachment",
        ],
        "include_related_field_values": [
            "entity.id",
            "entity.entity_name",
        ],
    }

    ui_config = {
        "navigation_header": "Registration",
        "title": "Opinion Management",
        "url": "opinion-management",
        "ordering": 4,
        "api_path": "registration/opinionmanagement",
    }

    class Meta:
        db_table = "opinion_management"
        app_label = "registration"
        verbose_name = "Opinion Management"
        verbose_name_plural = "Opinion Management"

    def save(self, *args, **kwargs):
        # Normalize file paths: strip MEDIA_ROOT prefix so Django generates correct URLs
        for field in self._meta.get_fields():
            if isinstance(field, models.FileField):
                raw_value = self.__dict__.get(field.attname)
                if raw_value and isinstance(raw_value, str) and settings.MEDIA_ROOT in raw_value:
                    self.__dict__[field.attname] = raw_value.replace(settings.MEDIA_ROOT, "").lstrip("/")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_of_counsel_firm or f"Opinion #{self.id}"
