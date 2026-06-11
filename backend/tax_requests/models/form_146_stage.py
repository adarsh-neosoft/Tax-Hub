from django.db import models


class Form146Stage(models.Model):
    tds_opinion = models.OneToOneField(
        "tax_requests.TDSOpinion",
        on_delete=models.CASCADE,
        related_name="form_146",
    )
    remarks = models.TextField(null=True, blank=True, verbose_name="Remarks, if any")
    form_146_attachment = models.FileField(
        upload_to="tds_opinion/form146/",
        null=True,
        blank=True,
        verbose_name="Form 146",
    )
    comparison_status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Form 146 Comparison Status",
    )
    ack_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Acknowledgement Number")
    ack_date = models.DateField(null=True, blank=True, verbose_name="Acknowledgement Date")
    udin = models.CharField(max_length=100, null=True, blank=True, verbose_name="UDIN")
    sap_document_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="SAP Document Number")
    invoice_posting_date = models.DateField(null=True, blank=True, verbose_name="Invoice Posting Date")

    class Meta:
        db_table = "form_146_stage"
