from django.db import models
from api.base_model import BaseModel


class TaskTracker(BaseModel):

    fy = models.ForeignKey(
        "masters.Period",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="FY",
        help_text="From Period Master",
    )

    legal_entity = models.ForeignKey(
        "masters.LegalEntity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Legal Entity",
        help_text="From Legal Entity Master",
    )

    task_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Task Name",
        help_text="Based on Email to tag",
    )

    assign_to = models.ForeignKey(
        "masters.UserMaster",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Assign To",
        help_text="From User Master",
    )

    priority = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Priority",
        help_text="Low / Medium / High",
    )

    status = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Status",
        help_text="Open / WIP / Close",
    )

    statutory_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Statutory Date",
    )

    internal_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Internal Date",
    )

    reminder_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Reminder Date",
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": [
            "id",
            "fy",
            "legal_entity",
            "assign_to",
        ],
        "search_fields": [
            "task_name",
            "status",
            "priority",
        ],
        "filter_fields": [
            "fy",
            "legal_entity",
            "assign_to",
            "status",
            "priority",
        ],
        "list_display_fields": [
            "fy.category",
            "legal_entity.sap_code",
            "legal_entity.entity_name",
            "assign_to.employee_name",
            "status",
        ],
        "form_display_fields": [
            "fy",
            "legal_entity",
            "task_name",
            "assign_to",
            "priority",
            "status",
            "statutory_date",
            "internal_date",
            "reminder_date",
        ],
        "include_related_field_values": [
            "fy.category",
            "legal_entity.sap_code",
            "legal_entity.entity_name",
            "assign_to.employee_name",
        ],
    }

    ui_config = {
        "navigation_header": "Registration",
        "title": "Task Tracker",
        "url": "task-tracker",
        "ordering": 9,
        "api_path": "registration/tasktracker",
    }

    class Meta:
        db_table = "task_tracker"
        app_label = "registration"
        verbose_name = "Task Tracker"
        verbose_name_plural = "Task Tracker"

    def __str__(self):
        if self.legal_entity_id:
            le = self.legal_entity
            return f"{le.entity_name or le.sap_code or '#' + str(le.id)} - {self.task_name or 'No Task'}"
        return f"Task #{self.id}"
