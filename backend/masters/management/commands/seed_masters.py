"""
Django Management Command — Seed Masters Data
==============================================
File location:  backend/masters/management/commands/seed_masters.py

Run:
    python manage.py seed_masters --excel /path/to/AMNS-Tax-Hub_17022026.xlsx
    python manage.py seed_masters --excel /path/to/file.xlsx --dry-run
    python manage.py seed_masters --excel /path/to/file.xlsx --clear
"""

import os
import datetime
import pyxlsb
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from masters.models import (
    Vertical, Law, Role, Period, AmountUnit, Forum, Issue,
    DocumentMaster, FormMaster, LawRule, LegalEntity, LawSection,
    Consultant, Compliance, Director, MaterialHSN,
    UserMaster, ExchangeRate, IntragroupAgreement,
    TPBenchmarking, TPStudyReport, ITActMapping,
)


# ── Utilities ────────────────────────────────────────────────────────────────

def _s(val):
    """Return clean string or '' for NaN/None."""
    if val is None:
        return ""
    try:
        if pd.isna(val):
            return ""
    except Exception:
        pass
    return str(val).strip()


def _get_sheet_names(path):
    with pyxlsb.open_workbook(path) as wb:
        return wb.sheets


def _find_sheet(all_sheets, number):
    """Find sheet by leading number prefix (robust to spacing/naming)."""
    prefix = str(number)
    for name in all_sheets:
        stripped = name.lstrip()
        if stripped.startswith(prefix) and len(stripped) > len(prefix):
            if not stripped[len(prefix)].isdigit():
                return name
    return None


def _read(path, sheet, header_row):
    """
    Read sheet, stopping at the first blank row OR 'Facility required' footer —
    whichever comes first. Applies universally to every sheet.
    """
    df = pd.read_excel(path, engine="pyxlsb", sheet_name=sheet, header=None)
    df.columns = [_s(c) for c in df.iloc[header_row]]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    cutoff = len(df)

    # Guard 1: first fully-blank row
    all_blank = df.isnull().all(axis=1)
    if all_blank.any():
        cutoff = min(cutoff, int(all_blank.idxmax()))

    # Guard 2: any cell starting with 'facility' (case-insensitive)
    for idx, row in df.iterrows():
        if idx >= cutoff:
            break
        if any(_s(cell).lower().startswith("facility") for cell in row):
            cutoff = min(cutoff, int(idx))
            break

    return df.iloc[:cutoff].dropna(how="all")


def _read_by_number(path, all_sheets, number, header_row, label):
    sheet = _find_sheet(all_sheets, number)
    if sheet is None:
        raise CommandError(
            f"\n  ❌  Could not find sheet #{number} ({label}) in the workbook.\n"
            f"     Available sheets:\n" + "\n".join(f"       {n!r}" for n in all_sheets)
        )
    return sheet, _read(path, sheet, header_row)


# ── Command ──────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Seed all masters data from the AMNS Tax Hub Excel workbook."

    def add_arguments(self, parser):
        parser.add_argument("--excel", required=True, help="Full path to the Excel file.")
        parser.add_argument("--clear", action="store_true", help="Delete existing records before seeding.")
        parser.add_argument("--dry-run", action="store_true", help="Show what would be inserted without writing to DB.")

    def handle(self, *args, **options):
        xl, dry, clear = options["excel"], options["dry_run"], options["clear"]

        if not os.path.exists(xl):
            raise CommandError(f"\n  ❌  Excel file not found:\n     {xl}")

        self.all_sheets = _get_sheet_names(xl)
        self.stdout.write(f"  📋  Sheets found: {self.all_sheets}\n")

        from django.contrib.auth import get_user_model
        self.u = get_user_model().objects.filter(is_superuser=True).first()
        if not self.u:
            raise CommandError("\n  ❌  No users in DB. Run: python manage.py createsuperuser")

        self.stdout.write(self.style.MIGRATE_HEADING(f"\n📂  {xl}"))
        self.stdout.write(f"  👤  System user: {self.u}\n")
        if dry:
            self.stdout.write(self.style.WARNING("⚠️   DRY RUN — nothing will be saved.\n"))

        seeders = [
            (self._verticals,            4,  1,  "Vertical Master"),
            (self._laws,                 5,  1,  "Law Name Master"),
            (self._roles,                2,  1,  "Role Master"),
            (self._periods,              9,  2,  "Period Master"),
            (self._amount_units,         11, 2,  "Amounts Master"),
            (self._forums,               20, 1,  "Forum Master"),
            (self._issues,               19, 1,  "Issue Master"),
            (self._document_masters,     12, 1,  "Document Name Master"),
            (self._form_masters,         13, 1,  "Form No. Master"),
            (self._law_rules,            14, 1,  "Law Rule Master"),
            (self._legal_entities,       1,  1,  "Legal Entity Master"),
            (self._law_sections,         6,  1,  "Law Section Master"),
            (self._consultants,          7,  3,  "Consultant Master"),
            (self._compliance,           8,  2,  "Compliance Name Master"),
            (self._directors,            21, 1,  "Director Master"),
            (self._material_hsn,         22, 1,  "Material code vs HSN"),
            (self._user_masters,         3,  1,  "User Master"),
            (self._exchange_rates,       10, 1,  "Exchange Rate Master"),
            (self._intragroup_agreements,15, 1,  "Intragroup Agreement"),
            (self._tp_benchmarking,      16, 1,  "TP Benchmarking"),
            (self._tp_study_report,      17, 1,  "TP Study Report"),
            (self._it_act_mapping,       18, 1,  "IT Act 2025 vs 1961"),
        ]

        with transaction.atomic():
            if clear and not dry:
                self._clear()

            for fn, sheet_no, hdr, label in seeders:
                sheet = _find_sheet(self.all_sheets, sheet_no)
                if sheet is None:
                    self.stdout.write(self.style.WARNING(f"  ⚠  Sheet #{sheet_no} ({label}) not found — skipped"))
                    continue
                df = _read(xl, sheet, hdr)
                fn(df, dry)

            if dry:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS("\n✅  Done!\n"))

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _base(self):
        return {"created_by": self.u, "last_updated_by": self.u}

    def _ok(self, label, c, s):
        self.stdout.write(f"  ✔  {label:<26} created={c}  skipped={s}")

    def _upsert(self, model, lookup, defaults, label, dry):
        if dry:
            self.stdout.write(f"  [DRY] {label}")
            return 0, 0
        _, created = model.objects.get_or_create(**lookup, defaults={**defaults, **self._base()})
        return (1, 0) if created else (0, 1)

    def _clear(self):
        for m in [
            Director, MaterialHSN, Compliance, LawSection, LegalEntity,
            LawRule, FormMaster, DocumentMaster, Issue, Forum,
            AmountUnit, Period, Role, Law, Vertical, Consultant,
            UserMaster, ExchangeRate, IntragroupAgreement,
            TPBenchmarking, TPStudyReport, ITActMapping,
        ]:
            n, _ = m.objects.all().delete()
            self.stdout.write(f"  🗑  {m.__name__}: deleted {n}")

    # ── Seeders ──────────────────────────────────────────────────────────────

    def _verticals(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if name := _s(row.get("Particulars")):
                dc, ds = self._upsert(Vertical, {"particulars": name}, {}, f"Vertical → {name}", dry)
                c += dc; s += ds
        if not dry: self._ok("Vertical", c, s)

    def _laws(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if name := _s(row.get("Law Name")):
                dc, ds = self._upsert(Law, {"law_name": name}, {}, f"Law → {name}", dry)
                c += dc; s += ds
        if not dry: self._ok("Law", c, s)

    def _roles(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if role_type := _s(row.get("Type of Role")):
                dc, ds = self._upsert(Role, {"role_type": role_type}, {
                    "rights_involved": _s(row.get("Rights involved")),
                    "level":           _s(row.get("Levels")),
                }, f"Role → {role_type}", dry)
                c += dc; s += ds
        if not dry: self._ok("Role", c, s)

    def _periods(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if category := _s(row.get("Category")):
                dc, ds = self._upsert(Period, {"category": category}, {
                    "description": _s(row.get("Description")),
                }, f"Period → {category}", dry)
                c += dc; s += ds
        if not dry: self._ok("Period", c, s)

    def _amount_units(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if unit := _s(row.get("Amount in")):
                dc, ds = self._upsert(AmountUnit, {"amount_in": unit}, {}, f"AmountUnit → {unit}", dry)
                c += dc; s += ds
        if not dry: self._ok("AmountUnit", c, s)

    def _forums(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if name := _s(row.get("Name of Forum")):
                dc, ds = self._upsert(Forum, {"forum_name": name}, {}, f"Forum → {name}", dry)
                c += dc; s += ds
        if not dry: self._ok("Forum", c, s)

    def _issues(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if name := _s(row.get("Issue Name")):
                dc, ds = self._upsert(Issue, {"issue_name": name}, {}, f"Issue → {name}", dry)
                c += dc; s += ds
        if not dry: self._ok("Issue", c, s)

    def _document_masters(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if name := _s(row.get("Name Of Document")):
                dc, ds = self._upsert(DocumentMaster, {"document_name": name}, {}, f"DocumentMaster → {name}", dry)
                c += dc; s += ds
        if not dry: self._ok("DocumentMaster", c, s)

    def _form_masters(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if form_no := _s(row.get("Form No.")):
                dc, ds = self._upsert(FormMaster, {"form_no": form_no}, {
                    "form_description": _s(row.get("Form Description")),
                }, f"FormMaster → {form_no}", dry)
                c += dc; s += ds
        if not dry: self._ok("FormMaster", c, s)

    def _law_rules(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if rule_no := _s(row.get("Rule No.")):
                dc, ds = self._upsert(LawRule, {"rule_no": rule_no}, {
                    "rule_description": _s(row.get("Rule Description")),
                }, f"LawRule → {rule_no}", dry)
                c += dc; s += ds
        if not dry: self._ok("LawRule", c, s)

    def _legal_entities(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            sap_code    = _s(row.get("SAP Code*"))
            entity_name = _s(row.get("Name of the entity*"))
            if not sap_code or not entity_name:
                continue
            # Skip footer rows (real SAP codes are numeric and >= 4 digits)
            if sap_code.isdigit() and len(sap_code) < 4:
                continue
            vertical_nm = _s(row.get("Vertical"))
            vertical    = Vertical.objects.filter(particulars=vertical_nm).first() if vertical_nm else None
            dc, ds = self._upsert(LegalEntity, {"sap_code": sap_code}, {
                "entity_name":  entity_name,
                "pan":          _s(row.get("PAN*")),
                "tan":          _s(row.get("TAN*")),
                "pan_password": "",
                "vertical":     vertical,
            }, f"LegalEntity → {sap_code} | {entity_name}", dry)
            c += dc; s += ds
        if not dry: self._ok("LegalEntity", c, s)

    def _law_sections(self, df, dry):
        c = s = 0
        law = Law.objects.filter(law_name="Income Tax Act,1961").first()
        for _, row in df.iterrows():
            s2025 = _s(row.get("Section No of IT Act 2025"))
            s1961 = _s(row.get("Section No of IT Act 1961"))
            if not s2025 and not s1961:
                continue
            dc, ds = self._upsert(LawSection, {"section_2025": s2025, "section_1961": s1961}, {
                "law":          law,
                "chapter_2025": _s(row.get("Chapter of IT Act 2025")),
                "chapter_1961": _s(row.get("Chapter of IT Act 1961")),
                "description":  _s(row.get("Section Description")),
            }, f"LawSection → 2025={s2025} | 1961={s1961}", dry)
            c += dc; s += ds
        if not dry: self._ok("LawSection", c, s)

    def _consultants(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if firm := _s(row.get("Name of the Consultant/ Firm")):
                dc, ds = self._upsert(Consultant, {"consultant_name": firm}, {
                    "registration_no": _s(row.get("Firm registration number, if any")),
                    "partner_name":    _s(row.get("Full Name of the Partner")),
                    "membership_no":   _s(row.get("Membership number")),
                    "address":         _s(row.get("Address")),
                    "email":           _s(row.get("Email ID")) or None,
                    "mobile":          _s(row.get("Mobile Number")),
                    "service_type":    _s(row.get("Nature of services Provided")),
                    "vendor_code":     _s(row.get("Vendor Code")),
                }, f"Consultant → {firm}", dry)
                c += dc; s += ds
        if not dry: self._ok("Consultant", c, s)

    def _compliance(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if name := _s(row.get("Name of compliance")):
                law_nm      = _s(row.get("Law"))
                vertical_nm = _s(row.get("Vertical"))
                dc, ds = self._upsert(Compliance, {"compliance_name": name}, {
                    "frequency": _s(row.get("Frequency")),
                    "law":       Law.objects.filter(law_name=law_nm).first() if law_nm else None,
                    "vertical":  Vertical.objects.filter(particulars=vertical_nm).first() if vertical_nm else None,
                }, f"Compliance → {name}", dry)
                c += dc; s += ds
        if not dry: self._ok("Compliance", c, s)

    def _directors(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if not (name := _s(row.get("Name of Director"))):
                continue
            entity_nm = _s(row.get("Entity in which director position is held"))
            entity    = LegalEntity.objects.filter(entity_name=entity_nm).first() if entity_nm else None
            if not entity:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠  Director '{name}': entity '{entity_nm}' not found — skipped"))
                continue
            dc, ds = self._upsert(Director, {"director_name": name, "pan": _s(row.get("PAN"))}, {
                "address":      _s(row.get("Address")),
                "legal_entity": entity,
                "date_from":    _s(row.get("Date from")) or None,
                "date_to":      _s(row.get("Date to")) or None,
            }, f"Director → {name}", dry)
            c += dc; s += ds
        if not dry: self._ok("Director", c, s)

    def _material_hsn(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if mat := _s(row.get("Material Code")):
                dc, ds = self._upsert(MaterialHSN, {"material_code": mat}, {
                    "hsn_code": _s(row.get("HSN Code")),
                }, f"MaterialHSN → {mat}", dry)
                c += dc; s += ds
        if not dry: self._ok("MaterialHSN", c, s)

    def _user_masters(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            sap_id = _s(row.get("SAP ID"))
            email  = _s(row.get("Email ID"))
            if not sap_id or not email:
                continue
            role_nm     = _s(row.get("Role"))
            law_nm      = _s(row.get("Law"))
            vertical_nm = _s(row.get("Vertical"))
            dc, ds = self._upsert(UserMaster, {"sap_id": sap_id}, {
                "department":    _s(row.get("Department")),
                "employee_name": _s(row.get("Employee Name")),
                "email":         email,
                "mobile":        _s(row.get("Mobile Number")) or None,
                "role":          Role.objects.filter(role_type=role_nm).first()           if role_nm     else None,
                "law":           Law.objects.filter(law_name=law_nm).first()              if law_nm      else None,
                "vertical":      Vertical.objects.filter(particulars=vertical_nm).first() if vertical_nm else None,
            }, f"UserMaster → {sap_id} | {email}", dry)
            c += dc; s += ds
        if not dry: self._ok("UserMaster", c, s)

    def _exchange_rates(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            currency = _s(row.get("Currency"))
            date_val = row.get("Date")
            rate_val = row.get("Exchange Rate")
            if not currency or date_val is None or rate_val is None:
                continue
            try:
                if not isinstance(date_val, (datetime.datetime, datetime.date)):
                    date_val = pd.to_datetime(_s(date_val)).date()
                elif isinstance(date_val, datetime.datetime):
                    date_val = date_val.date()
            except Exception:
                self.stdout.write(self.style.WARNING(
                    f"  ⚠  ExchangeRate: unparseable date '{date_val}' for {currency} — skipped"))
                continue
            try:
                rate_val = float(rate_val)
            except (ValueError, TypeError):
                self.stdout.write(self.style.WARNING(
                    f"  ⚠  ExchangeRate: unparseable rate '{rate_val}' for {currency} — skipped"))
                continue
            dc, ds = self._upsert(ExchangeRate, {"date": date_val, "currency": currency}, {
                "exchange_rate": rate_val,
            }, f"ExchangeRate → {date_val} | {currency} | {rate_val}", dry)
            c += dc; s += ds
        if not dry: self._ok("ExchangeRate", c, s)

    def _intragroup_agreements(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if name := _s(row.get("Agreement Name")):
                dc, ds = self._upsert(IntragroupAgreement, {"agreement_name": name}, {
                    "agreement_type": _s(row.get("Agreement Type")) or None,
                    "description":    _s(row.get("Description")) or None,
                }, f"IntragroupAgreement → {name}", dry)
                c += dc; s += ds
        if not dry: self._ok("IntragroupAgreement", c, s)

    def _tp_benchmarking(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if name := _s(row.get("Benchmarking Name")):
                dc, ds = self._upsert(TPBenchmarking, {"benchmarking_name": name}, {
                    "description": _s(row.get("Description")) or None,
                }, f"TPBenchmarking → {name}", dry)
                c += dc; s += ds
        if not dry: self._ok("TPBenchmarking", c, s)

    def _tp_study_report(self, df, dry):
        c = s = 0
        for _, row in df.iterrows():
            if name := _s(row.get("Report Name")):
                dc, ds = self._upsert(TPStudyReport, {"report_name": name}, {
                    "report_year": _s(row.get("Report Year")) or None,
                    "description": _s(row.get("Description")) or None,
                }, f"TPStudyReport → {name}", dry)
                c += dc; s += ds
        if not dry: self._ok("TPStudyReport", c, s)

    def _it_act_mapping(self, df, dry):
        c = s = 0
        self.stdout.write(f"  ℹ  ITActMapping columns: {df.columns.tolist()}")
        for _, row in df.iterrows():
            s2025 = _s(row.get("Section No."))
            s1961 = _s(row.get("Parallel Section(s) of Income-tax Act, 1961"))
            if not s2025 and not s1961:
                continue
            chapter = _s(row.get("Chapter No., Chapter heading and Section heading"))
            dc, ds = self._upsert(ITActMapping, {"section_2025": s2025, "section_1961": s1961}, {
                "chapter_2025": chapter or None,
            }, f"ITActMapping → 2025={s2025} | 1961={s1961}", dry)
            c += dc; s += ds
        if not dry: self._ok("ITActMapping", c, s)