from django.db import models


class ApprovedStage(models.Model):
    tds_opinion = models.OneToOneField(
        "tax_requests.TDSOpinion",
        on_delete=models.CASCADE,
        related_name="approved_stage",
    )
    approval_remarks = models.TextField(
        null=True,
        blank=True,
        verbose_name="Approval Remarks",
    )

    class Meta:
        db_table = "approved_stage"

    def __str__(self):
        return f"Approved — {self.tds_opinion_id}"
