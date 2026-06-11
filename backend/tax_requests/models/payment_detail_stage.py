from django.db import models


class PaymentDetailStage(models.Model):
    tds_opinion = models.OneToOneField(
        "tax_requests.TDSOpinion",
        on_delete=models.CASCADE,
        related_name="payment_detail",
    )
    remarks = models.TextField(null=True, blank=True, verbose_name="Remarks, if any")
    sap_document_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="SAP Document Number")
    posting_date = models.DateField(null=True, blank=True, verbose_name="Posting Date")
    payment_bank_documents = models.FileField(
        upload_to="tds_opinion/payment/",
        null=True,
        blank=True,
        verbose_name="Payment Bank Documents",
    )
    sap_username = models.CharField(max_length=100, null=True, blank=True, verbose_name="SAP Username")

    class Meta:
        db_table = "payment_detail_stage"
