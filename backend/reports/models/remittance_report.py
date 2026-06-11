from django.db import models
from api.base_model import BaseModel


class RemittanceReport(BaseModel):

    tds_opinion = models.OneToOneField(
        "tax_requests.TDSOpinion",
        on_delete=models.CASCADE,
        related_name="remittance_report",
        null=True,
        blank=True,
    )

    request_id = models.CharField(
        max_length=100
    )

    vendor_code = models.CharField(
        max_length=100
    )

    vendor_name = models.CharField(
        max_length=255
    )

    gross_amount_fc = models.DecimalField(
        max_digits=18,
        decimal_places=2
    )

    tds_amount_fc = models.DecimalField(
        max_digits=18,
        decimal_places=2
    )

    gross_amount_inr = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="Gross Amt-INR"
    )

    tds_amount_inr = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="TDS Amt-INR"
    )

    net_amount_inr = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="Net Amount-INR"
    )

    sap_document_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="SAP Document Number"
    )

    invoice_number = models.CharField(
        max_length=100,
        verbose_name="Invoice Number"
    )

    form_145_ack_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Form 145 Ackn. Number"
    )

    form_146_ack_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Form 146 Ackn. Number"
    )

    payment_document_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Payment Document Number"
    )

    payment_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Payment Date"
    )

    form_145_attachment = models.FileField(
        upload_to="remittance/form145/",
        blank=True,
        null=True,
        verbose_name="Form 145 Attachment"
    )

    form_146_attachment = models.FileField(
        upload_to="remittance/form146/",
        blank=True,
        null=True,
        verbose_name="Form 146 Attachment"
    )

    trc_attachment = models.FileField(
        upload_to="remittance/trc/",
        blank=True,
        null=True,
        verbose_name="TRC Attachment"
    )

    no_pe_attachment = models.FileField(
        upload_to="remittance/no_pe/",
        blank=True,
        null=True,
        verbose_name="NO PE Attachment"
    )

    form_10f_attachment = models.FileField(
        upload_to="remittance/10f/",
        blank=True,
        null=True,
        verbose_name="Form 10F"
    )

    invoice_attachment = models.FileField(
        upload_to="remittance/invoice/",
        blank=True,
        null=True,
        verbose_name="Invoice"
    )

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "request_id"
        ],

        "search_fields": [
            "request_id",
            "vendor_name",
            "invoice_number"
        ],

        "filter_fields": [
            "vendor_name"
        ],

        "list_display_fields": [
            "request_id",
            "vendor_name",
            "vendor_code",
            "gross_amount_inr",
            "tds_amount_inr",
            "net_amount_inr",
            "sap_document_number",
            "invoice_number",
            "form_145_ack_number",
            "form_146_ack_number",
            "payment_document_number",
            "payment_date",
            "form_145_attachment",
            "form_146_attachment",
            "trc_attachment",
            "no_pe_attachment",
            "form_10f_attachment",
            "invoice_attachment",
        ],

        "form_display_fields": [
            "__all__"
        ],

        "include_related_field_values": [],
    }

    ui_config = {
        "navigation_header": "Report",
        "title": "Remittance Report",
        "url": "remittance-report",
        "ordering": 1,
        "api_path": "reports/remittancereport",
    }

    class Meta:
        db_table = "remittance_report"
        app_label = "reports"