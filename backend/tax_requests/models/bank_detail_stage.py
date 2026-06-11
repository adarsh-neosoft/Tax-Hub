from django.db import models


class BankDetailStage(models.Model):
    tds_opinion = models.OneToOneField(
        "tax_requests.TDSOpinion",
        on_delete=models.CASCADE,
        related_name="bank_detail",
    )
    bank_remarks = models.TextField(null=True, blank=True, verbose_name="Remarks, if any")
    bank_ifsc_code = models.CharField(max_length=20, null=True, blank=True, verbose_name="Bank IFSC Code")
    bank_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Name of Bank")
    branch_name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Branch of the Bank")
    bsr_code = models.CharField(max_length=50, null=True, blank=True, verbose_name="BSR Code")
    proposed_remittance_date = models.DateField(null=True, blank=True, verbose_name="Proposed date of remittance")
    rbi_purpose_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="RBI Purpose Code")
    rbi_sub_code = models.CharField(max_length=50, null=True, blank=True, verbose_name="RBI Sub Code")
    form_146_type = models.CharField(max_length=100, null=True, blank=True, verbose_name="Form 146 - Type")
    external_ca = models.CharField(max_length=255, null=True, blank=True, verbose_name="External CA")
    multiple_15ca_cb = models.BooleanField(default=False, verbose_name="Multiple 15CA/CB")
    generate_single_15ca_cb = models.BooleanField(
        default=False,
        verbose_name="Generate single 15CA/CB against multiple request",
    )
    itdrein = models.CharField(max_length=100, null=True, blank=True, verbose_name="ITDREIN")

    class Meta:
        db_table = "bank_detail_stage"
