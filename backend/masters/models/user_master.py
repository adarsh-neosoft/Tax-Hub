from django.db import models
from api.base_model import BaseModel


class UserMaster(BaseModel):
    department = models.CharField(max_length=100)

    employee_name = models.CharField(
        max_length=255
    )

    sap_id = models.CharField(
        max_length=50,
        unique=True
    )

    email = models.EmailField()

    mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    role = models.ForeignKey(
        "masters.Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    law = models.ForeignKey(
        "masters.Law",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    vertical = models.ForeignKey(
        "masters.Vertical",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "employee_name"],
        "search_fields": [
            "employee_name",
            "email",
            "sap_id"
        ],
        "filter_fields": [
            "department",
            "role",
            "vertical"
        ],
        "list_display_fields": [
            "employee_name",
            "sap_id",
            "email",
            "role",
            "is_active"
        ],
        "form_display_fields": "__all__",
        "include_related_field_values": [
            "role",
            "law",
            "vertical"
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "User Master",
        "url": "user-master",
        "ordering": 18,
        "api_path": "masters/UserMaster",
    }

    class Meta:
        db_table = "user_master"
        app_label = "masters"