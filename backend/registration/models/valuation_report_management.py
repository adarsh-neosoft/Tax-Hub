import os

from django.conf import settings
from django.db import models
from api.base_model import BaseModel


def valuation_report_upload_to(instance, filename):
    return os.path.join("registration/valuation_report", filename)


class ValuationReportManagement(BaseModel):

    name_of_firm_counsel = models.CharField(
        max_length=255,
        verbose_name="Name of the Firm/ Counsel",
    )

    entity = models.ForeignKey(
        "masters.LegalEntity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Name of entity",
    )

    purpose = models.ForeignKey(
        "masters.Law",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Purpose",
    )

    date_of_report = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date of Report",
    )

    attachment = models.FileField(
        upload_to=valuation_report_upload_to,
        blank=True,
        null=True,
        verbose_name="Attachment (Download)",
    )

    team_members_involved = models.ManyToManyField(
        "masters.UserMaster",
        blank=True,
        verbose_name="Team Members Involved",
        help_text="Select multiple team members from User Master",
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": [
            "id",
            "name_of_firm_counsel",
        ],
        "search_fields": [
            "name_of_firm_counsel",
        ],
        "filter_fields": [
            "entity",
            "purpose",
        ],
        "list_display_fields": [
            "name_of_firm_counsel",
            "entity.entity_name",
            "purpose.law_name",
            "date_of_report",
            "attachment",
            "team_members_involved",
        ],
        "form_display_fields": [
            "name_of_firm_counsel",
            "entity",
            "purpose",
            "date_of_report",
            "attachment",
            "team_members_involved",
        ],
        "include_related_field_values": [
            "entity.entity_name",
            "purpose.law_name",
        ],
    }

    ui_config = {
        "navigation_header": "Registration",
        "title": "Valuation Report Management",
        "url": "valuation-report-management",
        "ordering": 5,
        "api_path": "registration/valuationreportmanagement",
    }

    class Meta:
        db_table = "valuation_report_management"
        app_label = "registration"
        verbose_name = "Valuation Report Management"
        verbose_name_plural = "Valuation Report Management"

    def save(self, *args, **kwargs):
        # Normalize file paths: strip MEDIA_ROOT prefix so Django generates correct URLs
        for field in self._meta.get_fields():
            if isinstance(field, models.FileField):
                raw_value = self.__dict__.get(field.attname)
                if raw_value and isinstance(raw_value, str) and settings.MEDIA_ROOT in raw_value:
                    self.__dict__[field.attname] = raw_value.replace(settings.MEDIA_ROOT, "").lstrip("/")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_of_firm_counsel or f"Valuation Report #{self.id}"
