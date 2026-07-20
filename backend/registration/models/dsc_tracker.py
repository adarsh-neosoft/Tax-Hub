from django.db import models
from api.base_model import BaseModel


class DscTracker(BaseModel):
    name = models.ForeignKey(
        "masters.Director",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Name",
    )

    pan = models.CharField(
        max_length=20,
        verbose_name="PAN",
        blank=True,
        null=True,
        help_text="Auto-populated from selected Director's PAN",
    )

    father_name = models.CharField(
        max_length=255,
        verbose_name="Father's Name",
        blank=True,
        null=True,
    )

    from_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="From Date",
        help_text="Auto-populated from selected Director",
    )

    to_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="To Date",
        help_text="Auto-populated from selected Director",
    )

    dsc_registered_on_it = models.BooleanField(
        default=False,
        verbose_name="Whether DSC registered on IT",
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": [
            "id",
            "name",
        ],
        "search_fields": [
            "pan",
            "father_name",
        ],
        "filter_fields": [
            "dsc_registered_on_it",
        ],
        "list_display_fields": [
            "name",
            "pan",
            "father_name",
            "from_date",
            "to_date",
            "dsc_registered_on_it",
        ],
        "form_display_fields": [
            {"field": "name", "display_field": "director_name"},
            "pan",
            "father_name",
            "from_date",
            "to_date",
            "dsc_registered_on_it",
        ],
        "include_related_field_values": [
            "name.id",
            "name.director_name",
        ],
    }

    ui_config = {
        "navigation_header": "Registration",
        "title": "DSC Tracker",
        "url": "dsc-tracker",
        "ordering": 2,
        "api_path": "registration/dsctracker",
    }

    class Meta:
        db_table = "dsc_tracker"
        app_label = "registration"
        verbose_name = "DSC Tracker"
        verbose_name_plural = "DSC Tracker"

    def save(self, *args, **kwargs):
        # Auto-populate PAN from the selected Director
        if self.name_id and not self.pan:
            self.pan = self.name.pan
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name.director_name if self.name else f"DSC Tracker #{self.id}"
