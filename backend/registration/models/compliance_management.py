import os

from django.conf import settings
from django.db import models
from api.base_model import BaseModel


def compliance_management_upload_to(instance, filename):
    return os.path.join("registration/compliance_management", filename)


class ComplianceManagement(BaseModel):

    pan = models.ForeignKey(
        "masters.LegalEntity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="PAN",
        help_text="Select PAN from Legal Entity Master",
    )

    vertical = models.ForeignKey(
        "masters.Vertical",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Vertical",
        help_text="Auto-filled based on selected PAN",
    )

    legal_entity = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Legal Entity",
        help_text="Auto-filled from Legal Entity Master based on selected PAN",
    )

    law_name = models.ForeignKey(
        "masters.Law",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Law Name",
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

    period = models.ForeignKey(
        "masters.Period",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Period",
    )

    frequency = models.ForeignKey(
        "masters.Compliance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="compliance_management_frequency",
        verbose_name="Frequency",
        help_text="Dropdown from Compliance Name Master",
    )

    user_involved = models.ForeignKey(
        "masters.UserMaster",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="User Involved",
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

    document_link = models.FileField(
        upload_to=compliance_management_upload_to,
        blank=True,
        null=True,
        verbose_name="Document Link",
        help_text="Captures documents uploaded by user in Return/Form Management",
    )

    status_by_workspace_admin = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Status by Workspace Admin",
    )

    status_from_income_tax_website = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Status from Income Tax Website",
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": [
            "id",
            "pan",
            "law_name",
            "compliance_name",
            "frequency",
        ],
        "search_fields": [
            "legal_entity",
            "status_by_user",
        ],
        "filter_fields": [
            "pan",
            "vertical",
            "law_name",
            "compliance_name",
            "compliance_section",
            "period",
            "frequency",
            "user_involved",
        ],
        "list_display_fields": [
            "pan.pan",
            "vertical.particulars",
            "legal_entity",
            "law_name.law_name",
            "compliance_name.compliance_name",
            "compliance_section.section_2025",
            "period.category",
            "frequency.frequency",
            "user_involved.employee_name",
            "statutory_timelines",
            "internal_timelines",
            "actual_completion_date",
            "status_by_user",
            "document_link",
            "status_by_workspace_admin",
            "status_from_income_tax_website",
        ],
        "form_display_fields": [
            "pan",
            "vertical",
            "legal_entity",
            "law_name",
            "compliance_name",
            "compliance_section",
            "period",
            "frequency",
            "user_involved",
            "statutory_timelines",
            "internal_timelines",
            "actual_completion_date",
            "status_by_user",
            "document_link",
            "status_by_workspace_admin",
            "status_from_income_tax_website",
        ],
        "include_related_field_values": [
            "pan.id",
            "pan.pan",
            "vertical.id",
            "vertical.particulars",
            "law_name.id",
            "law_name.law_name",
            "compliance_name.id",
            "compliance_name.compliance_name",
            "compliance_section.id",
            "compliance_section.section_2025",
            "period.id",
            "period.category",
            "frequency.id",
            "frequency.frequency",
            "user_involved.id",
            "user_involved.employee_name",
        ],
    }

    ui_config = {
        "navigation_header": "Registration",
        "title": "Compliance Management",
        "url": "compliance-management",
        "ordering": 7,
        "api_path": "registration/compliancemanagement",
    }

    class Meta:
        db_table = "compliance_management"
        app_label = "registration"
        verbose_name = "Compliance Management"
        verbose_name_plural = "Compliance Management"

    def save(self, *args, **kwargs):
        # Auto-populate vertical and legal_entity from selected PAN (LegalEntity)
        if self.pan_id:
            le = self.pan
            if le:
                if le.vertical_id:
                    self.vertical = le.vertical
                if le.entity_name:
                    self.legal_entity = le.entity_name

        # Auto-populate frequency FK from selected Compliance Name
        if self.compliance_name_id and not self.frequency_id:
            self.frequency = self.compliance_name

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
        return f"Compliance Management #{self.id}"
