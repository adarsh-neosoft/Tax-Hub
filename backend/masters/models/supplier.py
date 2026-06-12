from django.db import models
from api.base_model import BaseModel

from masters.models.country import Country


class Supplier(BaseModel):

    vendor_code = models.CharField(
        max_length=200,
        unique=True
    )

    vendor_name = models.CharField(
        max_length=200
    )

    address = models.TextField()

    addr_no = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    house_no = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    street2 = models.CharField(
        max_length=40,
        blank=True,
        null=True
    )

    street3 = models.CharField(
        max_length=40,
        blank=True,
        null=True
    )

    street4 = models.CharField(
        max_length=40,
        blank=True,
        null=True
    )

    street5 = models.CharField(
        max_length=40,
        blank=True,
        null=True
    )

    city = models.CharField(
        max_length=40
    )

    state = models.CharField(
        max_length=40
    )

    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    pin_code = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    tin = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    pan_if_any = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    exemption_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    certificate_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    contact_person_email = models.EmailField(
        blank=True,
        null=True
    )

    api_config = {
        "dropdown_fields": [
            "vendor_code",
            "vendor_name"
        ],

        "search_fields": [
            "vendor_code",
            "vendor_name",
            "pan_if_any",
            "tin",
            "city",
            "state"
        ],

        "filter_fields": [
            "country",
            "city",
            "state"
        ],

        "list_display_fields": [
            "vendor_code",
            "vendor_name",
            "address",
            "city",
            "state",
            "country",
            "pin_code",
            "pan_if_any",
            "tin",
            "exemption_percentage",
            "certificate_number",
            "contact_person_email",
            "is_active"
        ],

        "form_display_fields": [
            "vendor_code",
            "vendor_name",
            "address",
            "street1",
            "street2",
            "street3",
            "street4",
            "street5",
            "city",
            "state",
            "country",
            "pin_code",
            "pan_if_any",
            "tin",
            "exemption_percentage",
            "certificate_number",
            "contact_person_email",
            "is_active"
        ],

        "include_related_field_values": [
            "country"
        ]
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Supplier",
        "url": "supplier",
        "ordering": 22,
        "api_path": "masters/Supplier",
    }

    class Meta:
        db_table = "supplier"
        app_label = "masters"