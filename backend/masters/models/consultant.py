from django.db import models
from api.base_model import BaseModel

class Consultant(BaseModel):
    consultant_name = models.CharField(max_length=255)
    registration_no = models.CharField(max_length=100, blank=True, null=True)
    partner_name = models.CharField(max_length=255, blank=True, null=True)
    membership_no = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    service_type = models.CharField(max_length=255, blank=True, null=True)
    vendor_code = models.CharField(max_length=50, blank=True, null=True)

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "consultant_name"],
        "search_fields": ["consultant_name"],
        "filter_fields": ["consultant_name"],
        "list_display_fields": ["consultant_name", "email", "is_active"],
        "form_display_fields": "__all__",
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Consultant",
        "url": "consultant",
        "ordering": 13,
        "api_path": "masters/consultant",
    }

    class Meta:
        db_table = "consultant"
        app_label = "masters"