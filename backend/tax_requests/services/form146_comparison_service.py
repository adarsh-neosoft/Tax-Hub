"""
Service to compare the generated Form 146 Excel data against
data extracted from the uploaded Form 146 PDF, producing a
comparison Excel with Matched/Unmatched status.
"""
import re
import difflib
from io import BytesIO
from pathlib import Path
from datetime import datetime

from django.conf import settings
from django.core.files.base import ContentFile
import openpyxl

from tax_requests.services.form146_excel_generator import Form146ExcelGenerator, FORM146_DATA_ROWS
from tax_requests.services.form146_pdf_parser import (
    Form146PDFParser,
    EXACT_MATCH_FIELDS,
    SIMILARITY_THRESHOLD,
)


def _calculate_similarity(str1, str2):
    """Calculate string similarity ratio (0-100)."""
    ratio = difflib.SequenceMatcher(None, str1, str2).ratio()
    return ratio * 100


def _check_similarity_threshold(str1, str2):
    """Return True if strings are similar enough per threshold."""
    return _calculate_similarity(str1, str2) > SIMILARITY_THRESHOLD


def _normalize(value):
    """Normalize value for comparison: lowercase, remove non-alphanumeric."""
    return re.sub(r"[^a-zA-Z0-9]", "", str(value).lower())


def _format_value_display(value):
    """
    Standalone version of Form146ExcelGenerator._format_value.
    Formats a value for display in the comparison Excel.
    """
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


def _build_comparison_rows(values_dict):
    """
    Build comparison rows from FORM146_DATA_ROWS.

    Each row contains:
        - particulars: The label from the data row
        - details: The formatted data value (empty for header/unmapped rows)
        - extracted_value: Will be filled later from PDF
        - matched_status: Will be filled later

    Returns:
        list of dicts
    """
    rows = []

    for s_no, particulars, data_key in FORM146_DATA_ROWS:
        if data_key is None:
            # Header row or unmapped row (e.g. duplicate SBI TTBR rate)
            # — no data to compare.
            rows.append({
                "s_no": s_no,
                "particulars": particulars,
                "details": "",
                "extracted_value": "",
                "matched_status": "",
            })
        else:
            details = values_dict.get(data_key, "")
            if details is None:
                details = ""
            formatted_details = _format_value_display(details)
            rows.append({
                "s_no": s_no,
                "particulars": particulars,
                "details": formatted_details,
                "extracted_value": "",
                "matched_status": "",
            })

    return rows


def run_and_save_comparison(opinion, form_146_stage):
    """
    Generate the Form 146 comparison Excel and save the results
    directly onto the form_146_stage instance.

    This is called automatically when a Form 146 PDF is uploaded
    and saved, so the comparison is ready immediately.

    Args:
        opinion: TDSOpinion instance
        form_146_stage: Form146Stage instance (must have form_146_attachment)
    """
    if not form_146_stage.form_146_attachment:
        return

    try:
        result = generate_comparison_excel(opinion, form_146_stage)
    except Exception as exc:
        # If comparison fails, log it but don't break the save
        print(f"Form 146 comparison auto-generation failed: {exc}")
        return

    # Save the comparison file to the stage
    file_path = result["comparison_file_path"]
    with open(file_path, "rb") as f:
        file_content = f.read()

    form_146_stage.download_form_146_comparison.save(
        result["filename"],
        ContentFile(file_content),
        save=False,
    )
    form_146_stage.comparison_status = result["status"]
    if result["ack_number"]:
        form_146_stage.ack_number = result["ack_number"]
    form_146_stage.save(update_fields=[
        "download_form_146_comparison",
        "comparison_status",
        "ack_number",
    ])

    print(f"Form 146 comparison auto-generated: {result['status']}")


def generate_comparison_excel(opinion, form_146_stage):
    """
    Main entry point: Generate a comparison Excel by comparing the
    generated Form 146 Excel data against the uploaded PDF.

    Args:
        opinion: TDSOpinion instance
        form_146_stage: Form146Stage instance (must have form_146_attachment)

    Returns:
        dict: {
            "comparison_file_path": Path to the saved comparison Excel,
            "status": "Pass" or "Fail",
            "ack_number": str or "",
        }
    """
    # Step 1: Generate the Form 146 Excel to get filled data
    generator = Form146ExcelGenerator(opinion)
    generator.generate()

    # Step 2: Get the values dict that was used to fill the Excel
    company = opinion.company
    opinion_stage = getattr(opinion, "tds_opinion_stage", None)
    invoice = getattr(opinion, "invoice_posting", None)
    bank = getattr(opinion, "bank_detail", None)

    from masters.models import Supplier

    supplier = Supplier.objects.filter(
        vendor_code=opinion.vendor_code
    ).first()

    values_dict = generator._build_values(company, supplier, opinion_stage, invoice, bank)

    # Step 3: Parse the uploaded PDF
    pdf_file = form_146_stage.form_146_attachment
    if not pdf_file:
        raise ValueError(
            "No Form 146 PDF attachment found. "
            "Please upload the Form 146 PDF first."
        )

    parser = Form146PDFParser(pdf_file)
    pdf_data, ack_number = parser.get_extracted_data()

    # Step 4: Build comparison rows from FORM146_DATA_ROWS
    comparison_rows = _build_comparison_rows(values_dict)

    # Step 5: Fill in extracted values and match status
    for row in comparison_rows:
        particulars = row["particulars"]
        details = row["details"]

        # Skip rows with no form data — nothing to compare
        if not details:
            continue

        # Extract the PDF value for this field
        pdf_value = pdf_data.get(particulars, "") or ""
        if pdf_value:
            row["extracted_value"] = pdf_value.lstrip()

        # Compare — every row gets Matched or Unmatched
        normalized_details = _normalize(details)
        normalized_pdf = _normalize(pdf_value) if pdf_value else ""

        if particulars in EXACT_MATCH_FIELDS:
            matched = normalized_details == normalized_pdf
        elif not normalized_pdf:
            # PDF has no value for this field → definitely Unmatched
            matched = False
        else:
            matched = _check_similarity_threshold(normalized_details, normalized_pdf)

        row["matched_status"] = "Matched" if matched else "Unmatched"

    # Step 6: Determine overall status
    all_statuses = [r["matched_status"] for r in comparison_rows if r["matched_status"]]
    has_unmatched = "Unmatched" in all_statuses
    overall_status = "Pass" if not has_unmatched else "Fail"

    # Step 7: Create the comparison Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Comparison"

    # Headers
    headers = ["S.No.", "Particulars", "Details", "Extracted_Value", "Matched_status"]
    header_font = openpyxl.styles.Font(bold=True)
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = header_font

    # Data rows — preserve original S.No. from FORM146_DATA_ROWS (blank for sub-rows)
    for row_idx, row_data in enumerate(comparison_rows, 2):
        if row_data["s_no"] is not None:
            ws.cell(row=row_idx, column=1, value=row_data["s_no"])
        ws.cell(row=row_idx, column=2, value=row_data["particulars"])
        ws.cell(row=row_idx, column=3, value=row_data["details"])
        ws.cell(row=row_idx, column=4, value=row_data["extracted_value"])
        status_cell = ws.cell(row=row_idx, column=5, value=row_data["matched_status"])

        # Color the status cell
        if row_data["matched_status"] == "Matched":
            status_cell.font = openpyxl.styles.Font(color="008000")  # Green
        elif row_data["matched_status"] == "Unmatched":
            status_cell.font = openpyxl.styles.Font(color="FF0000")  # Red

    # Auto-adjust column widths
    for col_idx in range(1, 6):
        ws.column_dimensions[chr(64 + col_idx)].width = 20
    ws.column_dimensions[chr(66)].width = 50  # Particulars column wider
    ws.column_dimensions[chr(67)].width = 30  # Details column
    ws.column_dimensions[chr(68)].width = 30  # Extracted_Value column

    # Step 8: Save the comparison file
    output_dir = Path(settings.MEDIA_ROOT) / "generated_form146_comparison"
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = (
        f"FORM146_COMPARISON_{opinion.request_code}_"
        f"{datetime.now().strftime('%d%m%y%H%M%S%f')[:-4]}.xlsx"
    )
    output_path = output_dir / filename

    wb.save(str(output_path))
    wb.close()

    return {
        "comparison_file_path": output_path,
        "status": overall_status,
        "ack_number": ack_number,
        "filename": filename,
    }
