import os

from django.conf import settings
from django.db import models
from api.base_model import BaseModel


def document_vault_upload_to(instance, filename):
    return os.path.join("registration/document_vault", filename)


class DocumentVault(BaseModel):

    legal_entity = models.ForeignKey(
        "masters.LegalEntity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Legal Entity",
        help_text="Dropdown from Legal Entity Master",
    )

    pan = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="PAN",
        help_text="Auto-filled from Legal Entity Master based on selected Legal Entity",
    )

    fy_ay = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="FY / AY",
        help_text="Financial Year / Assessment Year",
    )

    document_name_download = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Name of the Document - as per download",
        help_text="Auto-captured from downloaded file",
    )

    document_download_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Document Download Date",
    )

    document_name_renamed = models.ForeignKey(
        "masters.DocumentMaster",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Name of the Document - renamed",
        help_text="Dropdown from Document Name Master",
    )

    renamed_by = models.ForeignKey(
        "masters.UserMaster",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Renamed By",
        help_text="Dropdown from User Master",
    )

    rename_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Rename Date",
        help_text="Auto-populated when document is renamed",
    )

    document_attachment = models.FileField(
        upload_to=document_vault_upload_to,
        blank=True,
        null=True,
        verbose_name="Document Attachment",
    )

    din = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="DIN",
        help_text="Document Identification Number",
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": [
            "id",
            "legal_entity",
            "document_name_renamed",
            "renamed_by",
        ],
        "search_fields": [
            "pan",
            "fy_ay",
            "din",
        ],
        "filter_fields": [
            "legal_entity",
            "document_name_renamed",
            "renamed_by",
        ],
        "list_display_fields": [
            "legal_entity.entity_name",
            "pan",
            "fy_ay",
            "document_name_download",
            "document_download_date",
            "document_name_renamed.document_name",
            "renamed_by.employee_name",
            "rename_date",
            "din",
        ],
        "form_display_fields": [
            "legal_entity",
            "pan",
            "fy_ay",
            "document_name_download",
            "document_download_date",
            "document_name_renamed",
            "renamed_by",
            "rename_date",
            "document_attachment",
            "din",
        ],
        "include_related_field_values": [
            "legal_entity.entity_name",
            "document_name_renamed.document_name",
            "renamed_by.employee_name",
        ],
    }

    ui_config = {
        "navigation_header": "Registration",
        "title": "Document Vault",
        "url": "document-vault",
        "ordering": 9,
        "api_path": "registration/documentvault",
    }

    class Meta:
        db_table = "document_vault"
        app_label = "registration"
        verbose_name = "Document Vault"
        verbose_name_plural = "Document Vault"

    def save(self, *args, **kwargs):
        # Auto-populate PAN from selected Legal Entity
        if self.legal_entity_id:
            le = self.legal_entity
            if le and le.pan:
                self.pan = le.pan

        # Normalize file paths: strip MEDIA_ROOT prefix so Django generates correct URLs
        for field in self._meta.get_fields():
            if isinstance(field, models.FileField):
                raw_value = self.__dict__.get(field.attname)
                if raw_value and isinstance(raw_value, str) and settings.MEDIA_ROOT in raw_value:
                    self.__dict__[field.attname] = raw_value.replace(settings.MEDIA_ROOT, "").lstrip("/")
        super().save(*args, **kwargs)

    def __str__(self):
        if self.legal_entity_id:
            return f"{self.legal_entity.entity_name} - {self.pan or ''}"
        if self.document_name_download:
            return self.document_name_download
        return f"Document Vault #{self.id}"
