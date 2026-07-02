from pathlib import Path
from datetime import datetime

from django.conf import settings
import openpyxl

from masters.models import Supplier
from tax_requests.constants import FORM146_CELL_MAPPING


class Form146ExcelGenerator:

    TEMPLATE_NAME = "FormCB_Template.xlsx"

    def __init__(self, opinion):
        self.opinion = opinion

    def generate(self):
        template_path = (
            Path(settings.BASE_DIR)
            / "templates"
            / "form146"
            / self.TEMPLATE_NAME
        )

        # Load the workbook preserving all formatting, merged cells, formulas, etc.
        wb = openpyxl.load_workbook(template_path)
        ws = wb.active

        company = self.opinion.company

        opinion_stage = getattr(self.opinion, "tds_opinion_stage", None)
        invoice = getattr(self.opinion, "invoice_posting", None)
        bank = getattr(self.opinion, "bank_detail", None)

        supplier = Supplier.objects.filter(
            vendor_code=self.opinion.vendor_code
        ).first()

        values = self._build_values(company, supplier, opinion_stage, invoice, bank)

        # Fill the mapped cells
        for key, value in values.items():
            row_index = FORM146_CELL_MAPPING.get(key)
            if row_index is not None:
                # Convert 0-indexed pandas row to Excel cell reference (column C)
                # pandas row 0 = Excel row 1, so cell = f"C{row_index + 1}"
                cell_ref = f"C{row_index + 1}"
                ws[cell_ref] = self._format_value(value)

        output_dir = Path(settings.MEDIA_ROOT) / "generated_form146"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = (
            output_dir
            / f"FORM146_{self.opinion.request_code}_{datetime.now().strftime('%d%m%y%H%M%S%f')[:-4]}.xlsx"
        )

        # Save — preserves all template formatting
        wb.save(str(output_file))
        wb.close()

        return output_file

    def _build_values(self, company, supplier, opinion_stage, invoice, bank):
        return {
            # ---------------- Company ----------------
            "company_name": company.entity_name if company else "",
            "company_pan": company.pan if company else "",
            "company_tan": company.tan if company else "",
            # ---------------- Vendor ----------------
            "vendor_name": supplier.vendor_name if supplier else "",
            "vendor_address": supplier.address if supplier else "",
            "vendor_country": (
                supplier.country.country_name
                if supplier and supplier.country
                else ""
            ),
            # ---------------- Currency ----------------
            "currency": (
                opinion_stage.currency.currency
                if opinion_stage and opinion_stage.currency
                else (
                    self.opinion.currency.currency
                    if self.opinion.currency
                    else ""
                )
            ),
            # ---------------- Amount ----------------
            "invoice_fc": (
                opinion_stage.invoice_value_fc
                if opinion_stage
                else None
            ),
            "invoice_inr": (
                opinion_stage.invoice_value_inr
                if opinion_stage
                else None
            ),
            # ---------------- Bank ----------------
            "ifsc": (
                bank.bank_ifsc_code.ifsc_code
                if bank and bank.bank_ifsc_code
                else ""
            ),
            "bank_name": (
                bank.bank_name
                if bank
                else ""
            ),
            "branch": (
                bank.branch_name
                if bank
                else ""
            ),
            "bsr": (
                bank.bsr_code
                if bank
                else ""
            ),
            "remittance_date": (
                bank.proposed_remittance_date
                if bank
                else None
            ),
            # ---------------- Nature ----------------
            "nature_of_service": (
                opinion_stage.nature_of_service.service_description
                if opinion_stage and opinion_stage.nature_of_service
                else ""
            ),
            "rbi_purpose_code": (
                bank.rbi_purpose_code.rbi_purpose_code
                if bank and bank.rbi_purpose_code
                else ""
            ),
            "grossing_up": self.opinion.grossing_up,
            "taxable_india": (
                opinion_stage.taxable_in_india
                if opinion_stage
                else False
            ),
            "tds_section": (
                opinion_stage.tds_section
                if opinion_stage
                else ""
            ),
            "income_amount": (
                opinion_stage.income_amount
                if opinion_stage
                else None
            ),
            "tax_liability": (
                opinion_stage.tds_amount_inr
                if opinion_stage
                else None
            ),
            "tds_fc": (
                opinion_stage.tds_amount_fc
                if opinion_stage
                else None
            ),
            "tds_inr": (
                opinion_stage.tds_amount_inr
                if opinion_stage
                else None
            ),
            "tds_rate": (
                f"{opinion_stage.tax_rate}%"
                if opinion_stage and opinion_stage.tax_rate
                else ""
            ),
            "it_or_dtaa": (
                opinion_stage.it_or_dtaa
                if opinion_stage and opinion_stage.it_or_dtaa
                else ""
            ),
            "net_payable": (
                opinion_stage.net_payable_fc
                if opinion_stage
                else None
            ),
        }

    def _format_value(self, value):
        from decimal import Decimal
        from datetime import date, datetime

        if value is None:
            return ""

        if isinstance(value, bool):
            return "Yes" if value else "No"

        if isinstance(value, (int, float, Decimal)):
            if isinstance(value, Decimal):
                value = float(value)
            formatted = f"{value:,.2f}" if isinstance(value, float) else str(value)
            return formatted

        if isinstance(value, datetime):
            return value.strftime("%d-%b-%Y")

        if isinstance(value, date):
            return value.strftime("%d-%b-%Y")

        return str(value)
