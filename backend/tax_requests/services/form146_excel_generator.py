from pathlib import Path
from datetime import datetime

from django.conf import settings
import openpyxl

from masters.models import Supplier


# Complete row structure for the Form 15CA/CB Excel.
# Each entry: (S.No. value, Particulars text, data_key or None)
# If data_key is None, the Details cell is left empty (header-only row).
FORM146_DATA_ROWS = [
    # --- Remitter ---
    (1, "Name of Remitter", "company_name"),
    (2, "PAN of remitter", "company_pan"),
    (3, "TAN of remitter", "company_tan"),
    # --- Beneficiary ---
    (4, "Name of Beneficiary", "vendor_name"),
    (5, "Address of Beneficiary", "vendor_address"),
    (6, "Country to which remittance is made", "vendor_country"),
    # --- Currency ---
    (7, "Currency", "currency"),
    # --- Amount Payable ---
    (8, "Amount Payable", None),
    (None, "In foreign currency", "invoice_fc"),
    (None, "In INR", "invoice_inr"),
    # --- Bank ---
    (8, "IFSC Code", "ifsc"),
    (9, "Name of Bank (Remitter' Bank)", "bank_name"),
    (10, "Branch of Bank", "branch"),
    (11, "BSR Code of the Bank Branch (7 digit)", "bsr"),
    (12, "Proposed date of remittance", "remittance_date"),
    # --- Nature ---
    (13, "Nature of remittance as per agreement", "nature_of_service"),
    ("13a", "Please furnish the relevant purpose code as per RBI", "rbi_purpose_code"),
    (14, "In case remittance is net of taxes, whether tax payable has been grossed up?", "grossing_up"),
    # --- Taxability under the Act ---
    (15, "Taxability under the provisions of the Act (Without consdering DTAA)", None),
    (None, "(i) is remittance chargeable to tax in India", "taxable_india"),
    (None, "(ii) if not reasons thereof", None),
    (None, "(iii) if yes, (a) the relevant section of the Act under which the remittance is covered", "tds_section"),
    (None, "(b) the amount of income chargeable to tax", "income_amount"),
    (None, "(c) the tax liability", "tax_liability"),
    (None, "(d) basis of determining taxable income and tax liability", None),
    # --- DTAA ---
    (16, "If income is chargeable to tax in India and any relief is claimed under DTAA-", None),
    (None, "(i) whether tax residency certificate is obtained from the recipient of remittance", "has_trc"),
    (None, "(ii) please specify relevant DTAA", None),
    (None, "please specify relevant article of DTAA", None),
    (None, "Nature of payment as per DTAA", None),
    (None, "(iii) taxable income as per DTAA", "dtaa_taxable_income"),
    (None, "(iv) tax liability as per DTAA", "dtaa_tax_liability"),
    # --- Royalties / Business income / Capital gains ---
    (17, "A. If the remittance is for royalties, fee for technical services, interest, dividend, etc,(not connected with permanent establishment) please\nindicate:-", None),
    (None, "B. In case the remittance is on account of business income, please indicate:-", None),
    (None, "C. In case the remittance is on account of capital gains, please indicate:-", None),
    (None, "(a) amount of long term capital gains", None),
    (None, "(b) amount of short-term capital gains", None),
    (None, "(c) basis of arriving at taxable income", None),
    (None, "D. In case of other remittance not covered by sub- items A, B and C", None),
    # --- TDS ---
    (18, "Amount of TDS", None),
    (None, "In foreign currency", "tds_rate"),
    (None, "In INR", "tds_inr"),
    (19, "Rate of TDS", None),
    (None, "As per income tax act (%) or as per DTAA (%)", "it_or_dtaa"),
    (20, "Actual amount of remittance after TDS (in Foreign Currency)", "net_payable"),
    # --- Other ---
    (21, "Date of deduction of tax at source, if (DD/MM/YYYY)", "tds_deduction_date"),
    (None, "SBI TTBR rate on the date of filing Form 15CB", None),
    (None, "SBI TTBR rate on the date of filing Form 15CB", None),
]


class Form146ExcelGenerator:

    TEMPLATE_NAME = "FormCB_Template.xlsx"

    def __init__(self, opinion):
        self.opinion = opinion

    def generate(self):
        company = self.opinion.company

        opinion_stage = getattr(self.opinion, "tds_opinion_stage", None)
        invoice = getattr(self.opinion, "invoice_posting", None)
        bank = getattr(self.opinion, "bank_detail", None)

        supplier = Supplier.objects.filter(
            vendor_code=self.opinion.vendor_code
        ).first()

        values = self._build_values(company, supplier, opinion_stage, invoice, bank)

        # Build a lookup: data_key → formatted value
        formatted_values = {}
        for key, value in values.items():
            formatted_values[key] = self._format_value(value)

        # Create a clean workbook from scratch
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"

        # Row 1: Title
        ws.cell(row=1, column=2, value="Details for Form 15CB")

        # Row 2: Headers
        headers = ["S. No.", "Particulars", "Details"]
        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=2, column=col_idx, value=header)

        # Rows 3-50: Data
        for row_idx, (s_no, particulars, data_key) in enumerate(FORM146_DATA_ROWS, 3):
            # Column A — S.No. (None for sub-fields)
            if s_no is not None:
                ws.cell(row=row_idx, column=1, value=s_no)
            # Column B — Particulars
            ws.cell(row=row_idx, column=2, value=particulars)
            # Column C — Details
            if data_key and data_key in formatted_values:
                ws.cell(row=row_idx, column=3, value=formatted_values[data_key])

        # Column widths
        ws.column_dimensions["A"].width = 10
        ws.column_dimensions["B"].width = 60
        ws.column_dimensions["C"].width = 35

        # Save
        output_dir = Path(settings.MEDIA_ROOT) / "generated_form146"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = (
            output_dir
            / f"FORM146_{self.opinion.request_code}_{datetime.now().strftime('%d%m%y%H%M%S%f')[:-4]}.xlsx"
        )

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
            # "tds_inr": (
            #     opinion_stage.tds_amount_inr
            #     if opinion_stage
            #     else None
            # ),
            "tds_inr": (
                opinion_stage.tds_amount_fc
                if opinion_stage
                else None
            ),
            "tds_rate": (
                f"{opinion_stage.tax_rate}%"
                if opinion_stage and opinion_stage.tax_rate
                else ""
            ),
            "it_or_dtaa": (
                self._format_it_or_dtaa(opinion_stage)
                if opinion_stage
                else ""
            ),
            # "net_payable": (
            #     opinion_stage.net_payable_fc
            #     if opinion_stage
            #     else None
            # ),
            "net_payable": (
                opinion_stage.tds_amount_inr
                if opinion_stage
                else None
            ),
            # ---------------- DTAA section ----------------
            "has_trc": (
                opinion_stage.has_trc
                if opinion_stage
                else False
            ),
            "dtaa_taxable_income": (
                opinion_stage.assesseable_value_fc
                if opinion_stage and opinion_stage.assesseable_value_fc
                else None
            ),
            "dtaa_tax_liability": (
                opinion_stage.tds_amount_inr
                if opinion_stage and opinion_stage.tds_amount_inr
                else None
            ),
            # ---------------- Other fields ----------------
            "tds_deduction_date": (
                opinion_stage.exchange_rate_date
                if opinion_stage
                else None
            ),
            "ttbr_rate": (
                opinion_stage.exchange_rate
                if opinion_stage and opinion_stage.exchange_rate
                else None
            ),
        }

    @staticmethod
    def _format_it_or_dtaa(opinion_stage):
        """
        Format the IT/DTAA indicator with the tax rate.
        E.g., "DTAA - 10.0" or "IT - 10.0"
        """
        it_or_dtaa = opinion_stage.it_or_dtaa or ""
        tax_rate = opinion_stage.tax_rate

        if not it_or_dtaa and tax_rate is None:
            return ""

        if tax_rate is not None:
            rate_str = f"{float(tax_rate):.1f}".rstrip("0").rstrip(".")
            if it_or_dtaa:
                return f"{it_or_dtaa} - {rate_str}"
            return rate_str

        return it_or_dtaa

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
