from django.db import models
from api.base_model import BaseModel


class RBIPurposeSubCode(BaseModel):

    rbi_purpose_code = models.ForeignKey(
        "masters.RBIPurposeCode",
        on_delete=models.PROTECT,
        related_name="purpose_sub_codes"
    )

    sub_code = models.CharField(
        max_length=50
    )

    description = models.TextField()

    model_config = {
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "sub_code",
        ],

        "search_fields": [
            "sub_code",
            "description",
            "rbi_purpose_code",
        ],

        "filter_fields": [
            "rbi_purpose_code",
        ],

        "list_display_fields": [
            "rbi_purpose_code",
            "sub_code",
            "description",
            "is_active",
        ],

        "form_display_fields": [
            "rbi_purpose_code",
            "sub_code",
            "description",
            "is_active",
        ],

        "include_related_field_values": [
            "rbi_purpose_code",
        ],
    }

    ui_config = {
        "navigation_header": "Master Data",
        "title": "RBI Purpose Sub Code",
        "url": "rbi-purpose-sub-code",
        "ordering": 19,
        "api_path": "masters/RBIPurposeSubCode",
    }

    class Meta:
        db_table = "rbi_purpose_sub_code"
        app_label = "masters"