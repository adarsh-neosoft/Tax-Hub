from django.db import models


class CloseRequestStage(models.Model):
    tds_opinion = models.OneToOneField(
        "tax_requests.TDSOpinion",
        on_delete=models.CASCADE,
        related_name="close_request",
    )
    closing_remarks = models.TextField(null=True, blank=True, verbose_name="Remarks, if any")

    class Meta:
        db_table = "close_request_stage"
