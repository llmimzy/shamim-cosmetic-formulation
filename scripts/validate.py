#!/usr/bin/env python3
"""Validate the curated database and write docs/VALIDATION_REPORT.md.

ERRORS break the data model and fail the build.
WARNINGS are open uncertainty. They are reported, never "fixed" by assumption.

A valid CAS checksum, DOI pattern or URL shape proves format only, not identity
or scientific relevance.
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from datetime import date

from build import curated_ingredients
from common import (CAS_RE, CATEGORY_KEYS, CURATED, DOI_RE, EVIDENCE_TIERS, JURISDICTIONS, PHASE_VALUES,
                    PHOTOTYPES, PMID_RE, PURPOSES, ROOT, SOURCE_TYPES, STUDY_VERIFICATION, TEST_MATERIAL,
                    VALUE_STATUS, VERIFIED_CAS, cas_checksum_ok, read_csv)

URL_RE = re.compile(r"^https?://[^\s/$.?#].[^\s]*$")
PCT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")


def validate() -> tuple[list[str], list[str], dict]:
    errors: list[str] = []
    warnings: list[str] = []
    ing = curated_ingredients()
    studies = read_csv(CURATED / "studies.csv")
    links = read_csv(CURATED / "evidence_links.csv")
    ranges = read_csv(CURATED / "use_ranges.csv")
    reg = read_csv(CURATED / "regulatory.csv")
    context = read_csv(CURATED / "category_context.csv")
    ing_ids = {r["id"] for r in ing}
    study_ids = {s["id"] for s in studies}

    # Identity -----------------------------------------------------------------
    for name, n in Counter(r["inci_name"].lower() for r in ing).items():
        if n > 1:
            errors.append(f"Duplicate INCI name: {name}")
    by_cas = defaultdict(list)
    for r in ing:
        for field in ("id", "inci_name", "primary_category", "record_status"):
            if not r[field]:
                errors.append(f"{r['id']}: missing required field {field}")
        if r["primary_category"] not in CATEGORY_KEYS:
            errors.append(f"{r['id']}: unmapped category {r['primary_category']}")
        for f in ("cas_status", "ec_status", "hlb_status", "active_matter_status", "formulation_ph_status"):
            if r[f] not in VALUE_STATUS:
                errors.append(f"{r['id']}: {f} has unsupported value '{r[f]}'")
        if r["melanated_evidence_tier"] not in EVIDENCE_TIERS:
            errors.append(f"{r['id']}: unsupported melanated_evidence_tier")
        for p in r["addition_phase"].split("|"):
            if p not in PHASE_VALUES:
                errors.append(f"{r['id']}: unsupported addition_phase '{p}'")
        cas = r["cas_number"]
        if cas:
            if not CAS_RE.match(cas) or not cas_checksum_ok(cas):
                errors.append(f"{r['id']} {r['inci_name']}: CAS {cas} fails format/checksum")
            by_cas[cas].append(f"{r['id']} {r['inci_name']}")
        if r["cas_status"] in VERIFIED_CAS and len([s for s in r["cas_sources"].split("|") if s]) < 2:
            errors.append(f"{r['id']}: CAS marked {r['cas_status']} with fewer than two sources")
        if r["cas_status"] in VERIFIED_CAS and not r["cas_number"]:
            errors.append(f"{r['id']}: CAS marked {r['cas_status']} but cas_number is blank")
        for alt in filter(None, (r["cas_alternatives"] + "|" + r["cas_related"]).split("|")):
            if not cas_checksum_ok(alt):
                errors.append(f"{r['id']}: alternative/related CAS {alt} fails checksum")
        for url in filter(None, r["cas_sources"].split("|")):
            if not URL_RE.match(url):
                errors.append(f"{r['id']}: malformed source URL {url}")
        if r["cas_status"] in {"imported_unverified", "conflicting_sources", "not_found", "unresolved",
                               "conflicting_identity", "generic_identifier"}:
            warnings.append(f"CAS {r['cas_status']}: {r['id']} {r['inci_name']}")
        if not r["active_matter_percent"]:
            pass  # counted below; reported once, not 140 times
    for cas, who in by_cas.items():
        if len(who) > 1:
            warnings.append(f"Shared CAS {cas} (species- or class-level identifier?): {'; '.join(who)}")

    # Sources and evidence -------------------------------------------------------
    for s in studies:
        if s["source_type"] not in SOURCE_TYPES:
            errors.append(f"{s['id']}: unsupported source_type '{s['source_type']}'")
        if s["verification_status"] not in STUDY_VERIFICATION:
            errors.append(f"{s['id']}: unsupported verification_status")
        if s["phototypes"] not in PHOTOTYPES:
            errors.append(f"{s['id']}: unsupported phototypes value")
        if s["doi"] and not DOI_RE.match(s["doi"]):
            errors.append(f"{s['id']}: malformed DOI {s['doi']}")
        if s["pmid"] and not PMID_RE.match(s["pmid"]):
            errors.append(f"{s['id']}: malformed PMID {s['pmid']}")
        if s["url"] and not URL_RE.match(s["url"]):
            errors.append(f"{s['id']}: malformed URL")
        if s["pmid"] and s["url"] and "pubmed" in s["url"] and s["pmid"] not in s["url"]:
            errors.append(f"{s['id']}: PMID does not match PubMed URL")
        if s["verification_status"] == "unverified":
            warnings.append(f"Source unverified: {s['id']} {s['raw_title'] or s['title']}")
        if s["source_type"] in {"regulatory_listing", "regulation", "identity_database"}:
            for l in links:
                if l["study_id"] == s["id"] and l["purpose"] == "efficacy":
                    errors.append(f"{l['id']}: regulatory/identity source used as efficacy evidence")
    for l in links:
        if l["ingredient_id"] not in ing_ids:
            errors.append(f"{l['id']}: broken ingredient reference {l['ingredient_id']}")
        if l["study_id"] not in study_ids:
            errors.append(f"{l['id']}: broken source reference {l['study_id']}")
        if l["purpose"] not in PURPOSES:
            errors.append(f"{l['id']}: unsupported purpose")
        if l["test_material"] not in TEST_MATERIAL:
            errors.append(f"{l['id']}: unsupported test_material")
    for c in context:
        if c["study_id"] not in study_ids:
            errors.append(f"category_context: broken source reference {c['study_id']}")
        if c["category"] not in CATEGORY_KEYS:
            errors.append(f"category_context: unknown category {c['category']}")

    # Concentrations vs recorded limits -----------------------------------------
    for r in ranges:
        if r["ingredient_id"] not in ing_ids:
            errors.append(f"{r['id']}: broken ingredient reference")
        try:
            lo, hi = float(r["min_percent"]), float(r["max_percent"])
            if lo > hi:
                errors.append(f"{r['id']}: min_percent > max_percent")
        except ValueError:
            errors.append(f"{r['id']}: non-numeric range")
    for g in reg:
        if g["ingredient_id"] not in ing_ids:
            errors.append(f"{g['id']}: broken ingredient reference")
        if g["jurisdiction"] not in JURISDICTIONS:
            errors.append(f"{g['id']}: unknown jurisdiction")
        limits = [float(x) for x in PCT_RE.findall(g["max_concentration"])]
        if not limits:
            continue
        for r in ranges:
            if r["ingredient_id"] == g["ingredient_id"] and r["max_percent"] and float(r["max_percent"]) > min(limits):
                warnings.append(f"Range {r['id']} ({r['product_type']}, max {r['max_percent']}%) exceeds the lowest "
                                f"recorded {g['jurisdiction']} limit ({min(limits)}%) for some product type: "
                                f"{g['product_types']}")

    stats = {
        "ingredients": len(ing),
        "cas_status": Counter(r["cas_status"] for r in ing),
        "active_matter_missing": sum(1 for r in ing if not r["active_matter_percent"]),
        "ph_missing": sum(1 for r in ing if not r["formulation_ph"]),
        "sources": Counter(s["verification_status"] for s in studies),
        "evidence_links": len(links),
        "regulatory_entries": len(reg),
    }
    warnings.append(f"Active-matter % missing for {stats['active_matter_missing']}/{len(ing)} ingredients "
                    "(needs supplier CoA/TDS)")
    return errors, warnings, stats


def write_report(errors, warnings, stats) -> None:
    lines = [f"# Validation report", "", f"Generated {date.today().isoformat()} by `scripts/validate.py`.", "",
             "Errors break the data model. Warnings are open uncertainty to resolve by research, never by assumption.",
             "A valid CAS checksum or DOI pattern proves format only, not identity.", "",
             "## Summary", "", f"- Ingredients: {stats['ingredients']}",
             f"- CAS status: " + ", ".join(f"{k} {v}" for k, v in sorted(stats["cas_status"].items())),
             f"- Sources by verification status: " + ", ".join(f"{k} {v}" for k, v in sorted(stats["sources"].items())),
             f"- Evidence links: {stats['evidence_links']} · Regulatory entries: {stats['regulatory_entries']}",
             f"- Errors: **{len(errors)}** · Warnings: **{len(warnings)}**", "", "## Errors", ""]
    lines += [f"- {e}" for e in errors] or ["None."]
    lines += ["", "## Warnings", ""] + [f"- {w}" for w in warnings]
    (ROOT / "docs" / "VALIDATION_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    errs, warns, st = validate()
    write_report(errs, warns, st)
    print(f"{len(errs)} errors, {len(warns)} warnings -> docs/VALIDATION_REPORT.md")
    sys.exit(1 if errs else 0)
