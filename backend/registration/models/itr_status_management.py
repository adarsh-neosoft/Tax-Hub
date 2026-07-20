import os

from django.conf import settings
from django.db import models
from api.base_model import BaseModel


def itr_status_management_upload_to(instance, filename):
    return os.path.join("registration/itr_status_management", filename)


class ItrStatusManagement(BaseModel):

    financial_year = models.ForeignKey(
        "masters.FinancialYear",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Financial Year",
        help_text="Dropdown from Financial Year Master",
    )

    assessment_year = models.ForeignKey(
        "masters.AssessmentYear",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Assessment Year",
        help_text="Dropdown from Assessment Year Master",
    )

    pan = models.ForeignKey(
        "masters.LegalEntity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="PAN",
        help_text="Dropdown from Legal Entity Master",
    )

    legal_entity = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Legal Entity",
        help_text="Auto-filled from Legal Entity Master based on selected PAN",
    )

    compliance_section = models.ForeignKey(
        "masters.LawSection",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Compliance Section",
        help_text="Dropdown from Law Section Master",
    )

    filing_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Filing Type",
        help_text="Dropdown: Original, Revised, Updated, Modified",
    )

    itr_form = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="ITR Form",
        help_text="Dropdown: ITR 5, ITR 6, ITR 7",
    )

    acknowledgement_upload = models.FileField(
        upload_to=itr_status_management_upload_to,
        blank=True,
        null=True,
        verbose_name="Acknowledgement Upload",
    )

    itr_form_upload = models.FileField(
        upload_to=itr_status_management_upload_to,
        blank=True,
        null=True,
        verbose_name="ITR Form Upload",
    )

    statutory_timelines = models.DateField(
        null=True,
        blank=True,
        verbose_name="Statutory Timelines",
    )

    internal_timelines = models.DateField(
        null=True,
        blank=True,
        verbose_name="Internal Timelines",
    )

    actual_completion_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Actual Completion Date",
    )

    status_by_user = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Status by User",
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": [
            "id",
            "financial_year",
            "assessment_year",
            "pan",
            "compliance_section",
        ],
        "search_fields": [
            "filing_type",
            "status_by_user",
            "itr_form",
        ],
        "filter_fields": [
            "financial_year",
            "assessment_year",
            "pan",
            "compliance_section",
            "itr_form",
        ],
        "list_display_fields": [
            "financial_year.financial_year",
            "assessment_year.assessment_year",
            "pan.pan",
            "legal_entity",
            "compliance_section.section_2025",
            "filing_type",
            "itr_form",
            "statutory_timelines",
            "internal_timelines",
            "actual_completion_date",
            "status_by_user",
        ],
        "form_display_fields": [
            "financial_year",
            "assessment_year",
            "pan",
            "legal_entity",
            "compliance_section",
            "filing_type",
            "itr_form",
            "acknowledgement_upload",
            "itr_form_upload",
            "statutory_timelines",
            "internal_timelines",
            "actual_completion_date",
            "status_by_user",
        ],
        "include_related_field_values": [
            "financial_year.id",
            "financial_year.financial_year",
            "assessment_year.id",
            "assessment_year.assessment_year",
            "pan.id",
            "pan.pan",
            "compliance_section.id",
            "compliance_section.section_2025",
        ],
    }

    ui_config = {
        "navigation_header": "Registration",
        "title": "ITR Status Management",
        "url": "itr-status-management",
        "ordering": 8,
        "api_path": "registration/itrstatusmanagement",
    }

    class Meta:
        db_table = "itr_status_management"
        app_label = "registration"
        verbose_name = "ITR Status Management"
        verbose_name_plural = "ITR Status Management"

    def save(self, *args, **kwargs):
        # Auto-populate legal_entity from selected PAN (LegalEntity)
        if self.pan_id:
            le = self.pan
            if le and le.entity_name:
                self.legal_entity = le.entity_name

        # Normalize file paths: strip MEDIA_ROOT prefix so Django generates correct URLs
        for field in self._meta.get_fields():
            if isinstance(field, models.FileField):
                raw_value = self.__dict__.get(field.attname)
                if raw_value and isinstance(raw_value, str) and settings.MEDIA_ROOT in raw_value:
                    self.__dict__[field.attname] = raw_value.replace(settings.MEDIA_ROOT, "").lstrip("/")
        super().save(*args, **kwargs)

    def __str__(self):
        if self.pan_id:
            return f"{self.pan.pan} - {self.legal_entity or ''}"
        return f"ITR Status Management #{self.id}"
