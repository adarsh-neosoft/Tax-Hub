from django.db import models
from api.base_model import BaseModel


class ExternalCA(BaseModel):

    firm_name = models.CharField(
        max_length=255
    )

    firm_registration_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    full_name_of_the_partner = models.CharField(
        max_length=255
    )

    membership_number = models.CharField(
        max_length=100
    )

    address = models.TextField()

    email_id = models.EmailField()

    mobile_number = models.CharField(
        max_length=20
    )

    is_active = models.BooleanField(
        default=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "firm_name",
        ],
        "search_fields": [
            "firm_name",
            "full_name_of_the_partner",
            "membership_number",
            "email_id",
        ],

        "list_display_fields": [
            "firm_name",
            "firm_registration_number",
            "full_name_of_the_partner",
            "membership_number",
            "address",
            "email_id",
            "mobile_number",
            "is_active",
        ],

        "form_display_fields": [
            "firm_name",
            "firm_registration_number",
            "full_name_of_the_partner",
            "membership_number",
            "address",
            "email_id",
            "mobile_number",
            "is_active",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "External CA",
        "url": "external-ca",
        "ordering": 5,
        "api_path": "masters/ExternalCA",
    }

    class Meta:
        db_table = "external_ca"
        app_label = "masters"