from django.db import models
from api.base_model import BaseModel


class PurchaseOrder(BaseModel):

    purchase_order_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Purchase Order Number"
    )

    vendor_code = models.CharField(
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
            "purchase_order_number",
        ],

        "search_fields": [
            "purchase_order_number",
            "vendor_code",
        ],

        "filter_fields": [
            "vendor_code",
            "is_active",
        ],

        "list_display_fields": [
            "purchase_order_number",
            "vendor_code",
            "is_active",
        ],

        "form_display_fields": [
            "purchase_order_number",
            "vendor_code",
            "is_active",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Purchase Order",
        "url": "purchase-order",
        "ordering": 23,
        "api_path": "masters/purchaseorder",
    }

    class Meta:
        db_table = "purchase_order"
        app_label = "masters"

    # def __str__(self):
    #     return self.purchase_order_number