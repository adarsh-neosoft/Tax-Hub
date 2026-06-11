from django.db import models


class Form145Stage(models.Model):
    tds_opinion = models.OneToOneField(
        "tax_requests.TDSOpinion",
        on_delete=models.CASCADE,
        related_name="form_145",
    )
    remarks = models.TextField(null=True, blank=True, verbose_name="Remarks, if any")
    ack_number = models.CharField(max_length=100, null=True, blank=True, verbose_name="Acknowledgement Number")
    posting_date = models.DateField(null=True, blank=True, verbose_name="Posting Date")
    bot_status = models.CharField(max_length=100, null=True, blank=True, verbose_name="Bot Status")
    form_ca_file = models.FileField(
        upload_to="tds_opinion/form145/",
        null=True,
        blank=True,
        verbose_name="Form CA file",
    )

    class Meta:
        db_table = "form_145_stage"
