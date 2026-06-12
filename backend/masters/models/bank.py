from django.db import models
from api.base_model import BaseModel


class Bank(BaseModel):

    legal_entity = models.ForeignKey(
        "masters.LegalEntity",
        on_delete=models.PROTECT,
        related_name="banks"
    )

    bank_name = models.CharField(
        max_length=255
    )

    branch_name = models.CharField(
        max_length=255
    )

    address = models.TextField()
    
    ifsc_code = models.CharField(
        max_length=20
    )

    bsr_code = models.CharField(
        max_length=20
    )

    itdrein = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "bank_name",
            "ifsc_code",
        ],

        "search_fields": [
            "bank_name",
            "branch_name",
            "ifsc_code",
            "bsr_code",
            "itdrein",
        ],

        "filter_fields": [
            "legal_entity",
            "bank_name",
            "ifsc_code",
            "is_active",
        ],

        "list_display_fields": [
            "legal_entity",
            "bank_name",
            "branch_name",
            "address",
            "ifsc_code",
            "bsr_code",
            "itdrein",
            "is_active",
        ],

        "form_display_fields": [
            "legal_entity",
            "bank_name",
            "branch_name",
            "address",
            "ifsc_code",
            "bsr_code",
            "itdrein",
            "is_active",
        ],

        "include_related_field_values": [
            "legal_entity",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Bank",
        "url": "bank",
        "ordering": 20,
        "api_path": "masters/bank",
    }

    class Meta:
        db_table = "bank"
        app_label = "masters"

    # def __str__(self):
    #     return f"{self.bank_name} - {self.branch_name}"