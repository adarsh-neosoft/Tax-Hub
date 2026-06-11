from django.db import models
from api.base_model import BaseModel


class LegalEntity(BaseModel):
    sap_code = models.CharField(
        max_length=50,
        unique=True
    )

    entity_name = models.CharField(
        max_length=255
    )

    pan = models.CharField(
        max_length=20
    )

    vertical = models.ForeignKey(
        "masters.Vertical",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    pan_password = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    tan = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    income_tax_tan_password = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    traces_user_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    traces_password = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    corporate_identification_no = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    pan_card = models.FileField(
        upload_to="legal_entity/pan_card/",
        blank=True,
        null=True
    )

    tan_card = models.FileField(
        upload_to="legal_entity/tan_card/",
        blank=True,
        null=True
    )

    certificate_of_incorporation = models.FileField(
        upload_to="legal_entity/certificate_of_incorporation/",
        blank=True,
        null=True
    )

    revised_certificate_of_incorporation = models.FileField(
        upload_to="legal_entity/revised_certificate_of_incorporation/",
        blank=True,
        null=True
    )

    date_of_commencement_of_business = models.DateField(
        blank=True,
        null=True
    )

    shareholder1_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    equity_shareholding_1_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    shareholder2_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    equity_shareholding_2_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True
    )

    abbreviation = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    bpm_code = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    model_config = {
        "encrypted_fields": [
            "pan_password",
            "income_tax_tan_password",
            "traces_password",
        ],
        "exclude_from_audit_log": [],
    }
    
    api_config = {
        "dropdown_fields": ["id", "sap_code", "entity_name"],
        "search_fields": [
            "entity_name",
            "sap_code",
            "pan",
            "tan",
        ],
        "filter_fields": [
            "vertical",
            "entity_name",
        ],
        "list_display_fields": [
            "sap_code",
            "entity_name",
            "pan",
            "vertical",
            "abbreviation",
            "is_active",
        ],
        "form_display_fields": [
            "sap_code",
            "entity_name",
            "pan",
            "vertical",
            "pan_password",
            "tan",
            "income_tax_tan_password",
            "traces_user_id",
            "traces_password",
            "corporate_identification_no",
            "pan_card",
            "tan_card",
            "certificate_of_incorporation",
            "revised_certificate_of_incorporation",
            "date_of_commencement_of_business",
            "shareholder1_name",
            "equity_shareholding_1_percent",
            "shareholder2_name",
            "equity_shareholding_2_percent",
            "abbreviation",
            "bpm_code",
            "is_active",
        ],
        "include_related_field_values": [
            "vertical"
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Legal Entity",
        "url": "legal-entity",
        "ordering": 12,
        "api_path": "masters/LegalEntity",
    }

    class Meta:
        db_table = "legal_entity"
        app_label = "masters"
