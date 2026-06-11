from django.db import models


class InvoicePostingStage(models.Model):
    tds_opinion = models.OneToOneField(
        "tax_requests.TDSOpinion",
        on_delete=models.CASCADE,
        related_name="invoice_posting",
    )
    posting_remarks = models.TextField(null=True, blank=True, verbose_name="Remarks, if any")
    document_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Document Number")
    invoice_posting_date = models.DateField(null=True, blank=True, verbose_name="Invoice Posting Date")
    description = models.TextField(null=True, blank=True, verbose_name="Description")

    class Meta:
        db_table = "invoice_posting_stage"
