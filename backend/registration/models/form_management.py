import os

from django.conf import settings
from django.db import models
from api.base_model import BaseModel


def form_management_upload_to(instance, filename):
    return os.path.join("registration/form_management", filename)


class FormManagement(BaseModel):

    financial_year = models.ForeignKey(
        "masters.FinancialYear",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Financial Year",
    )

    assessment_year = models.ForeignKey(
        "masters.AssessmentYear",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Assessment Year",
    )

    pan = models.ForeignKey(
        "masters.LegalEntity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="PAN",
        help_text="Select PAN from Legal Entity Master",
    )

    compliance_name = models.ForeignKey(
        "masters.Compliance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Compliance Name",
    )

    compliance_section = models.ForeignKey(
        "masters.LawSection",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Compliance Section",
    )

    form_no = models.ForeignKey(
        "masters.FormMaster",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Form No.",
    )

    form_description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Form No. Description",
        help_text="Auto-populated from Form Master based on selected Form No.",
    )

    filing_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Filing Type",
    )

    acknowledgement_upload = models.FileField(
        upload_to=form_management_upload_to,
        blank=True,
        null=True,
        verbose_name="Acknowledgement Upload",
    )

    form_upload = models.FileField(
        upload_to=form_management_upload_to,
        blank=True,
        null=True,
        verbose_name="Form Upload",
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
            "compliance_name",
            "form_no",
        ],
        "search_fields": [
            "filing_type",
            "status_by_user",
        ],
        "filter_fields": [
            "financial_year",
            "assessment_year",
            "pan",
            "compliance_name",
            "compliance_section",
            "form_no",
        ],
        "list_display_fields": [
            "financial_year.financial_year",
            "assessment_year.assessment_year",
            "pan.pan",
            "compliance_name.compliance_name",
            "compliance_section.section_2025",
            "form_no.form_no",
            "form_description",
            "filing_type",
            "statutory_timelines",
            "internal_timelines",
            "actual_completion_date",
            "status_by_user",
        ],
        "form_display_fields": [
            "financial_year",
            "assessment_year",
            "pan",
            "compliance_name",
            "compliance_section",
            "form_no",
            "form_description",
            "filing_type",
            "acknowledgement_upload",
            "form_upload",
            "statutory_timelines",
            "internal_timelines",
            "actual_completion_date",
            "status_by_user",
        ],
        "include_related_field_values": [
            "financial_year.financial_year",
            "assessment_year.assessment_year",
            "pan.pan",
            "compliance_name.compliance_name",
            "compliance_section.section_2025",
        ],
    }

    ui_config = {
        "navigation_header": "Registration",
        "title": "Form Management",
        "url": "form-management",
        "ordering": 6,
        "api_path": "registration/formmanagement",
    }

    class Meta:
        db_table = "form_management"
        app_label = "registration"
        verbose_name = "Form Management"
        verbose_name_plural = "Form Management"

    def save(self, *args, **kwargs):
        # Auto-populate form_description from selected FormMaster
        if self.form_no_id:
            fm = self.form_no
            if fm and fm.form_description:
                self.form_description = fm.form_description

        # Normalize file paths: strip MEDIA_ROOT prefix so Django generates correct URLs
        for field in self._meta.get_fields():
            if isinstance(field, models.FileField):
                raw_value = self.__dict__.get(field.attname)
                if raw_value and isinstance(raw_value, str) and settings.MEDIA_ROOT in raw_value:
                    self.__dict__[field.attname] = raw_value.replace(settings.MEDIA_ROOT, "").lstrip("/")
        super().save(*args, **kwargs)

    def __str__(self):
        if self.pan_id and self.financial_year_id:
            return f"{self.pan.pan} - {self.financial_year.financial_year}"
        if self.pan_id:
            return self.pan.pan
        return f"Form Management #{self.id}"
