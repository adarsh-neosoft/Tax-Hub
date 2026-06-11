from django.db import models
from api.base_model import BaseModel

class MaterialHSN(BaseModel):
    material_code = models.CharField(
        max_length=100
    )

    hsn_code = models.CharField(
        max_length=100
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id", "material_code"],
        "search_fields": ["material_code", "hsn_code"],
        "filter_fields": ["material_code"],
        "list_display_fields": [
            "material_code",
            "hsn_code",
            "is_active",
        ],
        "form_display_fields": "__all__",
        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "Material HSN",
        "url": "material-hsn",
        "ordering": 17,
        "api_path": "masters/MaterialHSN",
    }

    class Meta:
        db_table = "material_hsn"
        app_label = "masters"