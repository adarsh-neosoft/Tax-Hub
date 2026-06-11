from decimal import Decimal

from reports.models import RemittanceReport


def _dec(value):
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value))


def sync_remittance_report(tds_opinion):
    """Create or update remittance report row for a TDS Opinion request."""
    tds_stage = getattr(tds_opinion, "tds_opinion_stage", None)
    invoice_stage = getattr(tds_opinion, "invoice_posting", None)
    payment_stage = getattr(tds_opinion, "payment_detail", None)
    form145 = getattr(tds_opinion, "form_145", None)
    form146 = getattr(tds_opinion, "form_146", None)

    gross_fc = _dec(getattr(tds_stage, "invoice_value_fc", None) if tds_stage else None)
    tds_fc = _dec(getattr(tds_stage, "tds_amount_fc", None) if tds_stage else None)
    gross_inr = _dec(getattr(tds_stage, "invoice_value_inr", None) if tds_stage else None)
    tds_inr = _dec(getattr(tds_stage, "tds_amount_inr", None) if tds_stage else None)
    net_inr = _dec(getattr(tds_stage, "net_payable_inr", None) if tds_stage else None)

    defaults = {
        "request_id": tds_opinion.request_code or f"TDS-{tds_opinion.pk}",
        "vendor_code": tds_opinion.vendor_code or "",
        "vendor_name": tds_opinion.vendor_name or tds_opinion.vendor or "",
        "gross_amount_fc": gross_fc,
        "tds_amount_fc": tds_fc,
        "gross_amount_inr": gross_inr,
        "tds_amount_inr": tds_inr,
        "net_amount_inr": net_inr or (gross_inr - tds_inr),
        "sap_document_number": (
            getattr(payment_stage, "sap_document_number", None)
            or getattr(invoice_stage, "document_number", None)
            or getattr(form146, "sap_document_number", None)
            or ""
        ),
        "invoice_number": tds_opinion.invoice_number or "",
        "form_145_ack_number": getattr(form145, "ack_number", None) or "",
        "form_146_ack_number": getattr(form146, "ack_number", None) or "",
        "payment_document_number": getattr(payment_stage, "sap_document_number", None) or "",
        "payment_date": getattr(payment_stage, "posting_date", None),
        "last_updated_by": tds_opinion.last_updated_by,
    }

    if tds_opinion.invoice_file:
        defaults["invoice_attachment"] = tds_opinion.invoice_file
    if tds_opinion.form_10f_file:
        defaults["form_10f_attachment"] = tds_opinion.form_10f_file
    if tds_opinion.trc_file:
        defaults["trc_attachment"] = tds_opinion.trc_file
    if tds_opinion.no_pe_declaration_file:
        defaults["no_pe_attachment"] = tds_opinion.no_pe_declaration_file
    if form145 and form145.form_ca_file:
        defaults["form_145_attachment"] = form145.form_ca_file
    if form146 and form146.form_146_attachment:
        defaults["form_146_attachment"] = form146.form_146_attachment

    report = RemittanceReport.objects.filter(tds_opinion=tds_opinion).first()
    if report:
        for key, value in defaults.items():
            if key.endswith("_attachment") and not value:
                continue
            setattr(report, key, value)
        report.save()
        return report

    return RemittanceReport.objects.create(
        tds_opinion=tds_opinion,
        created_by=tds_opinion.created_by,
        **defaults,
    )
