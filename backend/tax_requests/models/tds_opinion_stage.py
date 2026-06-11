from django.db import models


class TDSOpinionStage(models.Model):
    tds_opinion = models.OneToOneField(
        "tax_requests.TDSOpinion",
        on_delete=models.CASCADE,
        related_name="tds_opinion_stage",
    )
    country = models.CharField(max_length=100, null=True, blank=True)
    vendor_status = models.CharField(max_length=100, null=True, blank=True, verbose_name="Status of Vendor")
    has_trc = models.BooleanField(default=False, verbose_name="Tax Residency Certificate (TRC)")
    has_no_pe = models.BooleanField(default=False, verbose_name="No PE Declaration")
    has_e_form_10f = models.BooleanField(default=False, verbose_name="E form 10F")
    it_or_dtaa = models.CharField(max_length=20, null=True, blank=True, verbose_name="As per IT or DTAA")
    grossing_up_applicable = models.BooleanField(default=False, verbose_name="Grossing up or not")
    nature_of_service = models.CharField(max_length=255, null=True, blank=True)
    invoice_value_fc = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    taxable_in_india = models.BooleanField(default=True, verbose_name="Whether Taxable in INDIA")
    assesseable_value_fc = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    exchange_rate_date = models.DateField(null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    invoice_value_inr = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    assesseable_value_inr = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tds_section = models.CharField(max_length=50, null=True, blank=True, verbose_name="TDS Section")
    tax_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="TDS Rate (%)")
    ldc_certificate = models.CharField(max_length=255, null=True, blank=True)
    form_146_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Form 146 - Type")
    tds_amount_fc = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tds_amount_inr = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    net_payable_fc = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    net_payable_inr = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    income_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True, verbose_name="Amount of income")
    external_document = models.FileField(upload_to="tds_opinion/external/", null=True, blank=True)
    opinion_remarks = models.TextField(null=True, blank=True, verbose_name="Remarks, if any")

    class Meta:
        db_table = "tds_opinion_stage"
