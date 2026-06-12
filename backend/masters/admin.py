from django.contrib import admin
from masters.models import *

models_to_register = [
    Vertical,
    Role,
    Law,
    Period,
    AmountUnit,
    Forum,
    Issue,
    ExchangeRate,
    DocumentMaster,
    FormMaster,
    LawRule,

    LegalEntity,
    LawSection,
    Consultant,
    UserMaster,
    Compliance,
    Director,

    IntragroupAgreement,
    TPBenchmarking,
    TPStudyReport,
    ITActMapping,
    MaterialHSN,
    AssessmentYear,
    FinancialYear,
    EntityName,
    Currency,
    Particular,
    Bank,
    Country,
    CurrencyRate,
    ExternalCA,
    TDSRate,
    TDSSection,
    NatureOfService,
    Supplier,
    LDACCertificate,
]

for model in models_to_register:
    admin.site.register(model)