from django.db import models
from api.base_model import BaseModel

from masters.models.legal_entity import LegalEntity
from masters.models.supplier import Supplier


class LDCCertificate(BaseModel):

    certificate_number = models.CharField(
        max_length=100
    )

    under_section_obtained = models.CharField(
        max_length=100
    )

    issued_officer = models.CharField(
        max_length=255
    )

    officer_designation = models.CharField(
        max_length=255
    )

    certificate_date = models.DateField()

    company = models.ForeignKey(
        LegalEntity,
        on_delete=models.PROTECT,
        related_name="ldc_certificates"
    )

    vendor = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="ldc_certificates"
    )

    certificate_valid_from = models.DateField()

    certificate_valid_to = models.DateField()

    certificate_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2
    )

    api_config = {
        "dropdown_fields": [
            "id",
            "certificate_number",
        ],

        "search_fields": [
            "certificate_number",
            "issued_officer",
            "under_section_obtained",
        ],

        "filter_fields": [
            "company",
            "vendor",
            "certificate_date",
        ],

        "list_display_fields": [
            "certificate_number",
            "under_section_obtained",
            "issued_officer",
            "officer_designation",
            "certificate_date",
            "company",
            "vendor",
            "certificate_valid_from",
            "certificate_valid_to",
            "certificate_amount",
            "is_active",
        ],

        "form_display_fields": [
            "certificate_number",
            "under_section_obtained",
            "issued_officer",
            "officer_designation",
            "certificate_date",
            "company",
            "vendor",
            "certificate_valid_from",
            "certificate_valid_to",
            "certificate_amount",
            "is_active",
        ],

        "include_related_field_values": [
            "company",
            "vendor",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "LDC Certificate",
        "url": "ldc-certificate",
        "ordering": 11,
        "api_path": "masters/LDCCertificate",
    }

    class Meta:
        db_table = "ldc_certificate"
        app_label = "masters"