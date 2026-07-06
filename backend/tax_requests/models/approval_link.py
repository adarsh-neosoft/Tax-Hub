import uuid

from django.db import models


class ApprovalLink(models.Model):
    tds_opinion = models.ForeignKey(
        "tax_requests.TDSOpinion",
        on_delete=models.CASCADE,
        related_name="approval_links",
    )

    external_ca = models.ForeignKey(
        "masters.ExternalCA",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="External CA",
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name="Approval Token",
    )

    is_valid = models.BooleanField(
        default=True,
        verbose_name="Is Valid",
    )

    is_approved = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Approved",
    )

    remarks = models.TextField(
        null=True,
        blank=True,
        verbose_name="Remarks",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Approved At",
    )

    class Meta:
        db_table = "approval_link"