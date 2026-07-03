"""
Service to parse Form 146 (15CB) PDF documents and extract field values
using regex patterns. Adapted from the legacy project's PDF_FNC class.
"""
import re
from io import BytesIO

from pypdf import PdfReader


# Regex patterns to extract fields from the 15CB PDF text
# Each key is a field identifier, value is the regex to capture the field value
REGEX_PATTERNS = {
    "Name_of_Remitter": r"(?<=M/s\.\s)([A-Z\s]+)(?=\s+with PAN)",
    "PAN_of_remitter": r"with\s+PAN\s+([A-Z0-9]+)\s*\(Remitters\)",
    "Name_of_Beneficiary": r"beneficiary\s+of\s+the\s+remittance\s+(.*?)(?=\n|$)",
    "Country_of_remittance": r"Country to which remittance is made\s*([\s\S]*?)\s*Currency\s*(.*)",
    "Curreny": r"Currency\s+(\S+)",
    "nature_of_remittance": (
        r"Nature of remittance as per agreement\/document\s*([\s\S]*?)"
        r"(?=8\. Please furnish)"
    ),
    "In_foreign_currency": r"Amount payable\s+In foreign currency\s+([\d,.]+)",
    "Branch_of_Bank": r"Branch of the bank\s+(.*)",
    "remittance_chargable": r"Whether tax residency certificate is obtained from the\s+(.*)",
    "chargeable_tax": r"The amount of income chargeable to tax ₹\s*([\d.]+)",
    "tax_libality": r"The tax Liability ₹\s*([\d.]+)",
    "actual_amount_of_remittance": (
        r"Actual amount of remittance after TDS \(In foreign currency\)\s+([\d,.]+)"
    ),
    "date_of_deduction": r"Date of deduction of tax at source, if any\s*-\s*(.*?)\s*Accountant",
    "bsr_number": r"BSR code of the bank branch \(7 digit\)\s+([0-9]{7})",
    "in_inr": r"(?<=In Indian \(₹\)\s₹\s)([\d,]+)",
    "name_of_bank": r"(?<=Name of Bank\s)(.*)",
    "tax_payable": (
        r"(?<=In case the remittance is net of taxes, whether tax payable has\s)"
        r"(.*?)(?=\n)"
    ),
    "actual_amt_remittance": (
        r"Actual amount of remittance after TDS \(In foreign currency\)\s*:?\s*([\d,.]+)"
    ),
    "ifsc": r"IFSC Code\s+([^\n]+?)\s+Name of Bank",
}

# Patterns that need special handling (multi-line, etc.)
SPECIAL_PATTERNS = {
    "address_of_benificary": (
        r"(?<=beneficiary of the remittance\s)(.*?)(?=\sB\.|$)"
    ),
    "remittance_covered": (
        r"If yes, \(a\) the relevant section of the Act under which the(.*?)"
        r"\(b\) The amount"
    ),
}

# Mapping from PDF extractor keys to the "Particulars" labels in the Excel template
PDF_TO_EXCEL_MAPPING = {
    "Name_of_Remitter": "Name of Remitter",
    "PAN_of_remitter": "PAN of remitter",
    "Name_of_Beneficiary": "Name of Beneficiary",
    "Country_of_remittance": "Country to which remittance is made",
    "Curreny": "Currency",
    "nature_of_remittance": "Nature of remittance as per agreement",
    "In_foreign_currency": "In foreign currency",
    "Branch_of_Bank": "Branch of Bank",
    "remittance_chargable": "(i) is remittance chargeable to tax in India",
    "chargeable_tax": "(b) the amount of income chargeable to tax",
    "tax_libality": "(c) the tax liability",
    "actual_amount_of_remittance": (
        "Actual amount of remittance after TDS (in Foreign Currency)"
    ),
    "date_of_deduction": "Date of deduction of tax at source, if (DD/MM/YYYY)",
    "bsr_number": "BSR Code of the Bank Branch (7 digit)",
    "in_inr": "In INR",
    "name_of_bank": "Name of Bank (Remitter' Bank)",
    "tax_payable": (
        "In case remittance is net of taxes, whether tax payable has been grossed up?"
    ),
    "address_of_benificary": "Address of Beneficiary",
    "ifsc": "IFSC Code",
}

# Fields that require exact character-for-character matching
EXACT_MATCH_FIELDS = [
    "PAN of remitter",
    "BSR Code of the Bank Branch (7 digit)",
    "IFSC Code",
]

# Confidence threshold for fuzzy matching (0-100)
SIMILARITY_THRESHOLD = 80

ACK_NUMBER_PATTERN = r"Acknowledgement Number\s*[-:]?\s*([^\n]*?)\s*(?=I,\s+have\s+examined)"


class Form146PDFParser:
    """Parse a Form 146 (15CB) PDF and extract field values."""

    def __init__(self, pdf_file_or_path):
        """
        Args:
            pdf_file_or_path: A file path (str/Path), a file-like object, or a
                               Django UploadedFile / InMemoryUploadedFile.
        """
        self.pdf_source = pdf_file_or_path
        self.pdf_text = self._extract_text()

    def _extract_text(self):
        """Extract all text from the PDF using pypdf."""
        text = ""
        reader = PdfReader(self.pdf_source)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text

    def get_extracted_data(self):
        """
        Extract field values from the PDF text using regex patterns.

        Returns:
            tuple: (field_dict, ack_number)
                - field_dict: dict mapping Excel label names to extracted values
                - ack_number: extracted acknowledgement number (str)
        """
        value_dict = {}
        for key in REGEX_PATTERNS:
            value_dict[key] = ""

        if len(self.pdf_text) < 250:
            raise ValueError(
                f"Not able to extract sufficient text from PDF "
                f"(only {len(self.pdf_text)} chars). "
                f"Check the PDF file."
            )

        # Apply standard regex patterns
        for key, pattern in REGEX_PATTERNS.items():
            match = re.search(pattern, self.pdf_text)
            if match:
                captured = match.group(1).strip()
                value_dict[key] = captured.replace(",", "") if "," in captured else captured

        # Special pattern: address of beneficiary
        address_match = re.search(
            SPECIAL_PATTERNS["address_of_benificary"],
            self.pdf_text,
            re.DOTALL,
        )
        if address_match:
            address = address_match.group(0).strip()
            beneficiary_name = value_dict.get("Name_of_Beneficiary", "")
            value_dict["address_of_benificary"] = address.replace(
                beneficiary_name, ""
            ).strip()

        # Special pattern: remittance covered section
        covered_match = re.search(
            SPECIAL_PATTERNS["remittance_covered"],
            self.pdf_text,
            re.DOTALL,
        )
        if covered_match:
            relevant_section = covered_match.group(1)
            uppercase_numbers_pattern = r"\b[A-Z0-9./]+\b"
            uppercase_numbers = re.findall(
                uppercase_numbers_pattern, relevant_section
            )
            value_dict["remittance_covered"] = " ".join(uppercase_numbers)

        # Map raw keys to Excel label names
        updated_dict = {}
        for raw_key, excel_label in PDF_TO_EXCEL_MAPPING.items():
            raw_value = value_dict.get(raw_key, "")
            if raw_value and "-" in raw_value:
                raw_value = raw_value.replace("-", "")
            updated_dict[excel_label] = raw_value

        # Extract acknowledgement number
        ack_match = re.search(ACK_NUMBER_PATTERN, self.pdf_text)
        ack_number = ""
        if ack_match:
            ack_number = re.sub(r"[^a-zA-Z0-9\s]", "", ack_match.group(1).strip())

        return updated_dict, ack_number

    def get_field_dict(self):
        """Convenience: return only the field dict without ack number."""
        return self.get_extracted_data()[0]
