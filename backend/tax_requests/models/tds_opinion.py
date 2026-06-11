from django.db import models
from api.base_model import BaseModel
import re


class TDSOpinion(BaseModel):

    request_code = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    remarks = models.TextField(
        verbose_name="Remarks, if any",
        null=True,
        blank=True
    )

    company = models.ForeignKey(
        "masters.LegalEntity",
        on_delete=models.PROTECT,
        related_name="tds_company",
        null=True,
        blank=True
    )

    vendor = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    vendor_name = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    vendor_code = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    company_code = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    pan_number = models.CharField(
        max_length=20,
        verbose_name="PAN Number",
        null=True,
        blank=True
    )

    tin_number = models.CharField(
        max_length=50,
        verbose_name="TIN Number",
        null=True,
        blank=True
    )

    po_npo = models.BooleanField(
        default=False,
        verbose_name="PO / NPO"
    )

    grossing_up = models.BooleanField(
        default=False,
        verbose_name="Grossing up"
    )

    currency = models.ForeignKey(
        "masters.Currency",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    particular = models.ForeignKey(
        "masters.Particular",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    invoice_number = models.CharField(
        max_length=100,
        verbose_name="Invoice Number",
        null=True,
        blank=True
    )

    opinion_invoice_amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="Opinion/Invoice Amount",
        null=True,
        blank=True
    )

    invoice_date = models.DateField(
        verbose_name="Invoice Date",
        null=True,
        blank=True
    )

    invoice_file = models.FileField(
        upload_to="tds_opinion/invoice/",
        verbose_name="Invoice File",
        null=True,
        blank=True
    )

    form_10f_file = models.FileField(
        upload_to="tds_opinion/form10f/",
        verbose_name="Electronically filed form 10F",
        null=True,
        blank=True
    )

    form_10f_valid_upto = models.DateField(
        verbose_name="Valid Upto",
        null=True,
        blank=True
    )

    trc_file = models.FileField(
        upload_to="tds_opinion/trc/",
        verbose_name="Tax Residency Certificate (TRC)",
        null=True,
        blank=True
    )

    trc_valid_upto = models.DateField(
        verbose_name="Valid Upto",
        null=True,
        blank=True
    )

    contract_agreement_copy = models.FileField(
        upload_to="tds_opinion/agreement/",
        verbose_name="Contract/ Agreement Copy",
        null=True,
        blank=True
    )

    agreement_valid_upto = models.DateField(
        verbose_name="Valid Upto",
        null=True,
        blank=True
    )

    pan_file = models.FileField(
        upload_to="tds_opinion/pan/",
        verbose_name="PAN",
        null=True,
        blank=True
    )

    pan_valid_upto = models.DateField(
        verbose_name="Valid Upto",
        null=True,
        blank=True
    )

    no_pe_declaration_file = models.FileField(
        upload_to="tds_opinion/no_pe/",
        verbose_name="No Permanent (NO PE) Establishment Declaration/ Tax Residency Declaration",
        null=True,
        blank=True
    )

    no_pe_valid_upto = models.DateField(
        verbose_name="Valid Upto",
        null=True,
        blank=True
    )

    proof_of_reimbursement_file = models.FileField(
        upload_to="tds_opinion/reimbursement/",
        verbose_name="Proof of reimbursement claims",
        null=True,
        blank=True
    )

    reimbursement_valid_upto = models.DateField(
        verbose_name="Valid Upto",
        null=True,
        blank=True
    )
    
    status = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    open_with = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    revert = models.BooleanField(
        default=False
    )

    def save(self, *args, **kwargs): 
        if not self.request_code:
            last = TDSOpinion.objects.order_by("-id").first()
            if last:
                next_id = last.id + 1
            else:
                next_id = 1
            self.request_code = f"TDS-{next_id:05d}"

        if self.company:
            self.company_code = self.company.sap_code

        if self.vendor:
            match = re.match(r"^(.*?)\s*\((.*?)\)$", self.vendor)
            if match:
                self.vendor_name = match.group(1).strip()
                self.vendor_code = match.group(2).strip()

        super().save(*args, **kwargs)

    model_config = {
        "encrypted_fields": [],
        "exclude_from_audit_log": [],
    }

    api_config = {

        "dropdown_fields": [
            "id",
            "request_code"
        ],

        "search_fields": [
            "request_code",
            "vendor_name",
            "vendor_code",
            "invoice_number"
        ],

        "filter_fields": [
            "status",
            "company",
            "currency"
        ],

        "list_display_fields": [
            "request_code",
            # "vendor",
            "vendor_name",
            "vendor_code",
            "company_code",
            "invoice_date",
            "invoice_number",
            # "opinion_invoice_amount",
            "status",
            "open_with",
            "revert",
        ],

        "form_display_fields": [
            "remarks",
            "company",
            "vendor",
            "pan_number",
            "tin_number",
            "po_npo",
            "grossing_up",
            "currency",
            "particular",
            "invoice_number",
            "opinion_invoice_amount",
            "invoice_date",
            "invoice_file",
            "form_10f_file",
            "form_10f_valid_upto",
            "trc_file",
            "trc_valid_upto",
            "contract_agreement_copy",
            "agreement_valid_upto",
            "pan_file",
            "pan_valid_upto",
            "no_pe_declaration_file",
            "no_pe_valid_upto",
            "proof_of_reimbursement_file",
            "reimbursement_valid_upto",
            "status",
            "is_active",
        ],

        "include_related_field_values": [
            "company",
            "currency",
            "particular",
        ],
    }

    ui_config = {
        "navigation_header": "Tax Requests",
        "title": "TDS Opinion",
        "url": "tds-opinion",
        "ordering": 1,
        "api_path": "tax_requests/tdsopinion",
    }

    class Meta:
        db_table = "tds_opinion"
        app_label = "tax_requests"