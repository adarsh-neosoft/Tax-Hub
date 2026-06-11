from django.db import models
from api.base_model import BaseModel


class IndemnityTracker(BaseModel):

    entity_name = models.ForeignKey(
        "masters.EntityName",
        on_delete=models.PROTECT,
        null=True,
        blank=True

    )

    financial_year = models.ForeignKey(
        "masters.FinancialYear",
        on_delete=models.PROTECT
    )

    assessment_year = models.ForeignKey(
        "masters.AssessmentYear",
        on_delete=models.PROTECT
    )


    date_of_notice_order = models.DateField()

    date_of_filing_appeal_writ = models.DateField(
        null=True,
        blank=True
    )

    date_of_communication_sent_to_essar = models.DateField(
        null=True,
        blank=True
    )

    issue_involved = models.ForeignKey(
        "masters.Issue",
        on_delete=models.PROTECT,
        null=True,
        blank=True

    )

    disputed_tax_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        # default=0
    )

    interest = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        # default=0
    )

    penalty = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        # default=0
    )

    total_demand_as_per_order = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        # default=0
    )

    estimated_interest = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        # default=0
    )

    estimated_penalty = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        # default=0
    )

    total_liability = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        # default=0
    )

    possible_amount_of_claim = models.BooleanField(
        default=False,
        verbose_name="Possible amount of claim > INR 40 crores?"
    )

    covered_under_specific_indemnity = models.BooleanField(
        default=False,
        verbose_name="Whether covered under specific indemnity?"
    )

    appearing_in_disclosure_letter = models.BooleanField(
        default=False,
        verbose_name="Whether appearing in disclosure letter?"
    )

    comments = models.TextField(
        blank=True,
        null=True
    )

    attachment = models.FileField(
        upload_to="indemnity/",
        null=True,
        blank=True
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {
        "dropdown_fields": ["id"],
        "search_fields": ["financial_year"],
        "filter_fields": ["financial_year"],
        "list_display_fields": [
            "entity_name.entity_name",
            "created_at",
            "created_by",
            "financial_year",
            "assessment_year",
            "date_of_notice_order",
            "date_of_filing_appeal_writ",
            "date_of_communication_sent_to_essar",
            "issue_involved.issue_name",
            "disputed_tax_amount",
            "interest",
            "penalty",
            "total_demand_as_per_order",
            "estimated_interest",
            "estimated_penalty",
            "total_liability",
            "possible_amount_of_claim",
            "covered_under_specific_indemnity",
            "appearing_in_disclosure_letter",
            "is_active",
        ],

        "form_display_fields": [
            "entity_name",
            "financial_year",
            "assessment_year",
            "date_of_notice_order",
            "date_of_filing_appeal_writ",
            "date_of_communication_sent_to_essar",
            "issue_involved",
            "disputed_tax_amount",
            "interest",
            "penalty",
            "total_demand_as_per_order",
            "estimated_interest",
            "estimated_penalty",
            "total_liability",
            "possible_amount_of_claim",
            "covered_under_specific_indemnity",
            "appearing_in_disclosure_letter",
            "comments",
            "attachment",
            "is_active",
        ],
        "include_related_field_values": [
            "entity_name.entity_name",
            "issue_involved.issue_name",
            "created_by.username",
        ],
    }

    ui_config = {
        "navigation_header": "Indemnity",
        "title": "Indemnity Tracker",
        "url": "indemnity-tracker",
        "ordering": 1,
        "api_path": "indemnity/indemnitytracker",
    }

    class Meta:
        db_table = "indemnity_tracker"
        app_label = "indemnity"