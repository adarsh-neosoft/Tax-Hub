"""Workflow stage names and editable field mapping for TDS Opinion."""

WORKFLOW_STAGE_NAMES = [
    "Initiated",
    "TDS Opinion",
    "Invoice Posting",
    "Bank Detail",
    "Form 146 Request",
    "Form 145 Request",
    "Payment Details",
    "Close Request",
    "Approved",
]

MASTER_INITIATED_FIELDS = [
    "remarks",
    "company",
    "vendor",
    "pan_number",
    "tin_number",
    "po_npo",
    "po_number",
    "grossing_up",
    "currency",
    "particular",
    "invoice_number",
    "opinion_invoice_amount",
    "invoice_date",
    "invoice_file",
    "form_10f_file",
    "form_10f_valid_upto",
    "trc_file",
    "trc_valid_upto",
    "contract_agreement_copy",
    "agreement_valid_upto",
    "pan_file",
    "pan_valid_upto",
    "no_pe_declaration_file",
    "no_pe_valid_upto",
    "proof_of_reimbursement_file",
    "reimbursement_valid_upto",
]

STAGE_SECTION_KEYS = {
    "Initiated": "master",
    "TDS Opinion": "tds_opinion_stage",
    "Invoice Posting": "invoice_posting",
    "Bank Detail": "bank_detail",
    "Form 146 Request": "form_146",
    "Form 145 Request": "form_145",
    "Payment Details": "payment_detail",
    "Close Request": "close_request",
    "Approved": "approved",
}

ACCORDION_SECTIONS = [
    {"stage": "Close Request", "key": "close_request", "title": "Close Request"},
    {"stage": "Payment Details", "key": "payment_detail", "title": "Payment Details"},
    {"stage": "Form 145 Request", "key": "form_145", "title": "145 Form Request"},
    {"stage": "Form 146 Request", "key": "form_146", "title": "146 Form Request"},
    {"stage": "Bank Detail", "key": "bank_detail", "title": "Bank Details"},
    {"stage": "Invoice Posting", "key": "invoice_posting", "title": "Invoice Posting"},
    {"stage": "TDS Opinion", "key": "tds_opinion_stage", "title": "TDS Opinion"},
    {"stage": "Initiated", "key": "master", "title": "Opinion request"},
]

STAGE_MODEL_FIELDS = {
    "tds_opinion_stage": [
        "country",
        "currency",
        "vendor_status",
        "has_trc",
        "has_no_pe",
        "has_e_form_10f",
        "it_or_dtaa",
        "grossing_up_applicable",
        "nature_of_service",
        "invoice_value_fc",
        "taxable_in_india",
        "assesseable_value_fc",
        "exchange_rate_date",
        "exchange_rate",
        "invoice_value_inr",
        "assesseable_value_inr",
        "tds_section",
        "tax_rate",
        "ldc_certificate",
        "form_146_type",
        "tds_amount_fc",
        "tds_amount_inr",
        "net_payable_fc",
        "net_payable_inr",
        "income_amount",
        "external_document",
        "opinion_remarks",
    ],
    "invoice_posting": [
        "posting_remarks",
        "document_number",
        "invoice_posting_date",
        "description",
    ],
    "bank_detail": [
        "bank_remarks",
        "bank_ifsc_code",
        "bank_name",
        "branch_name",
        "bsr_code",
        "proposed_remittance_date",
        "rbi_purpose_code",
        "rbi_sub_code",
        "form_146_type",
        "external_ca",
        "multiple_15ca_cb",
        "generate_single_15ca_cb",
        "itdrein",
    ],
    "form_146": [
        "remarks",
        "download_form_146",
        "form_146_attachment",
        "download_form_146_comparison",
        "comparison_status",
        "ack_number",
        "ack_date",
        "udin",
        # "sap_document_number",
        # "invoice_posting_date",
    ],
    "form_145": [
        "remarks",
        "ack_number",
        "posting_date",
        "bot_status",
        "form_145_file",
    ],
    "payment_detail": [
        "remarks",
        "sap_document_number",
        "posting_date",
        "payment_bank_documents",
        "sap_username",
    ],
    "close_request": ["closing_remarks"],
    "approved": ["approval_remarks"],
}

# Mapping of workflow stages to their approver group names
# Each stage can only be seen/acted upon by users belonging to the mapped group.
STAGE_APPROVER_GROUPS = {
    "Initiated": "AP (Account Payable)",
    "TDS Opinion": "DT (Direct Tax)",
    "Invoice Posting": "AP (Account Payable)",
    "Bank Detail": "Treasury",
    "Form 146 Request": "External CA",
    "Form 145 Request": "DT (Direct Tax)",
    "Payment Details": "Treasury",
    "Close Request": "DT (Direct Tax)",
}

# Mapping of master file fields to their corresponding valid_upto fields
FILE_VALIDITY_MAP = {
    "form_10f_file": "form_10f_valid_upto",
    "trc_file": "trc_valid_upto",
    "contract_agreement_copy": "agreement_valid_upto",
    "pan_file": "pan_valid_upto",
    "no_pe_declaration_file": "no_pe_valid_upto",
    "proof_of_reimbursement_file": "reimbursement_valid_upto",
}

STAGE_FILE_FIELDS = {
    "master": [
        "invoice_file",
        "form_10f_file",
        "trc_file",
        "contract_agreement_copy",
        "pan_file",
        "no_pe_declaration_file",
        "proof_of_reimbursement_file",
    ],
    "tds_opinion_stage": ["external_document"],
    "form_146": ["download_form_146", "form_146_attachment", "download_form_146_comparison"],
    "form_145": ["form_145_file"],
    "payment_detail": ["payment_bank_documents"],
}


# ==========================================
# Form146 Excel Template Cell Mapping
# Using pandas 0-indexed row numbers (column C = index 2)
# Excel row X = pandas row X-1
# ==========================================

FORM146_CELL_MAPPING = {

    # Remitter
    "company_name": 2,      # Excel row 3
    "company_pan": 3,       # Excel row 4
    "company_tan": 4,       # Excel row 5

    # Beneficiary
    "vendor_name": 5,       # Excel row 6
    "vendor_address": 6,    # Excel row 7
    "vendor_country": 7,    # Excel row 8

    # Currency
    "currency": 8,          # Excel row 9

    # Amount (Amount Payable)
    "invoice_fc": 10,       # Excel row 11 - In foreign currency
    "invoice_inr": 11,      # Excel row 12 - In INR

    # Bank
    "ifsc": 12,             # Excel row 13
    "bank_name": 13,        # Excel row 14
    "branch": 14,           # Excel row 15
    "bsr": 15,              # Excel row 16
    "remittance_date": 16,  # Excel row 17

    # Nature
    "nature_of_service": 17, # Excel row 18
    "rbi_purpose_code": 18,  # Excel row 19

    "grossing_up": 19,       # Excel row 20

    "taxable_india": 21,     # Excel row 22

    "tds_section": 23,       # Excel row 24

    "income_amount": 24,     # Excel row 25 - (b) amount of income chargeable to tax
    "tax_liability": 25,     # Excel row 26 - (c) the tax liability

    # TDS Amount
    "tds_fc": 42,            # Excel row 43 - In foreign currency
    "tds_inr": 43,           # Excel row 44 - In INR

    "tds_rate": 44,          # Excel row 45 - Rate of TDS

    "it_or_dtaa": 45,         # Excel row 46 - As per income tax act (%) or as per DTAA (%)

    "net_payable": 46,       # Excel row 47 - Actual amount of remittance after TDS

    # DTAA section
    "has_trc": 28,            # Excel row 29 - whether TRC is obtained
    "dtaa_taxable_income": 32, # Excel row 33 - (iii) taxable income as per DTAA
    "dtaa_tax_liability": 33,  # Excel row 34 - (iv) tax liability as per DTAA

    # Other fields
    "tds_deduction_date": 47, # Excel row 48 - Date of deduction of tax at source
    "ttbr_rate": 48,          # Excel row 49 - SBI TTBR rate on date of filing Form 15CB
}
