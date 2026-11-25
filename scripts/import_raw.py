#!/usr/bin/env python3
"""Turn the supplied raw CSV into the canonical tables.

Two jobs:

* ``base_ingredients()`` is a pure, repeatable transformation of the raw file.
  ``build.py`` calls it every time and then applies ``change_log.csv`` on top, so
  every difference between the raw file and the curated ingredient table is
  explained by a logged change.
* ``--seed`` writes the hand-maintained tables (studies, evidence links,
  category context, regulatory entries, use ranges, change log) the first time
  only. It refuses to overwrite them.

Import rules are documented in docs/DATA_MODEL.md.
"""
from __future__ import annotations

import argparse
import sys

from common import (CATEGORIES, CURATED, PHASES, RAW_CSV, SOLUBILITY, read_csv, write_csv)

INGREDIENT_FIELDS = [
    "id", "raw_row_ref", "inci_name", "inci_name_variants", "common_names", "primary_category",
    "secondary_functions", "origin", "botanical_name", "plant_part",
    "cas_number", "cas_status", "cas_sources", "cas_note", "ec_number", "ec_status",
    "chemical_family", "primary_function", "role_summary",
    "active_matter_percent", "active_matter_status", "hlb", "hlb_status",
    "addition_phase", "addition_phase_raw", "solubility", "formulation_ph", "formulation_ph_status",
    "melanated_evidence_tier", "safety_note_raw", "record_status", "notes",
]


def parse_range(text: str) -> tuple[str, str]:
    lo, hi = text.split("-")
    return lo.strip(), hi.strip()


def raw_rows() -> list[dict]:
    rows = read_csv(RAW_CSV)
    if len(rows) != 140:
        raise SystemExit(f"Expected 140 raw rows, found {len(rows)}")
    return rows


def base_ingredients() -> list[dict]:
    out = []
    for i, r in enumerate(raw_rows(), start=1):
        cas = r["CAS_Number"].strip()
        hlb = r["HLB"].strip()
        out.append({
            "id": f"ING-{i:03d}",
            "raw_row_ref": f"{r['Functional_Category']}#{r['Selection_Order']}",
            "inci_name": r["INCI_Name"].strip(),
            "inci_name_variants": "",
            "common_names": "",
            "primary_category": CATEGORIES[r["Functional_Category"]][0],
            "secondary_functions": "",
            "origin": "unknown",
            "botanical_name": "",
            "plant_part": "",
            "cas_number": cas,
            "cas_status": "imported_unverified" if cas else "not_researched",
            "cas_sources": "",
            "cas_note": "",
            "ec_number": "",
            "ec_status": "not_researched",
            "chemical_family": "",
            "primary_function": r["Primary_Function"].strip(),
            "role_summary": r["Effect_or_Formulation_Role"].strip(),
            "active_matter_percent": r["Active_Matter_Percent"].strip(),
            "active_matter_status": "not_researched",
            "hlb": hlb,
            "hlb_status": "imported_unverified" if hlb else "not_researched",
            "addition_phase": PHASES[r["Phase_to_Add"].strip()],
            "addition_phase_raw": r["Phase_to_Add"].strip(),
            "solubility": SOLUBILITY[r["Solubility_or_Processing"].strip()],
            "formulation_ph": r["Recommended_pH"].strip(),
            "formulation_ph_status": "not_researched",
            "melanated_evidence_tier": "not_yet_assessed",
            "safety_note_raw": r["Regulatory_or_Safety_Note"].strip(),
            "record_status": "imported",
            "notes": "",
        })
    return out


# ---------------------------------------------------------------- seeding --
# Classification of the 28 raw references, decided by reading each raw row's
# Evidence_Scope text (see docs/PHASE_1_AUDIT.md section 3.4).
CONTEXT_TITLES = {  # category-level references: detached from individual ingredients (decision D3)
    "Oral and topical peptides for skin aging: systematic review and meta-analysis of RCTs",
    "Topical treatment for postinflammatory hyperpigmentation: systematic review",
    "Ceramide-dominant moisturizer randomized trial",
    "Enhancement of stratum corneum lipid structure improves barrier function: RCT",
    "The effects of common OTC moisturizers on skin barrier function: controlled trial",
    "In vitro and in vivo evaluation of an emollient-rich moisturizer",
    "Vegetable butters and oils as dermal ingredients: review of clinical studies",
    "Vegetable butters and oils as dermal ingredients: clinical studies review",
}
SOURCE_TYPE_BY_TITLE = {
    "European Commission CosIng ingredient database": "identity_database",
    "ECHA EU cosmetic preservative listings": "regulatory_listing",
    "FDA OTC sunscreen monograph M020": "regulatory_listing",
    "Oral and topical peptides for skin aging: systematic review and meta-analysis of RCTs": "systematic_review_or_meta_analysis",
    "Topical treatment for postinflammatory hyperpigmentation: systematic review": "systematic_review_or_meta_analysis",
    "Topical treatments for melasma and their mechanism of action: systematic review": "systematic_review_or_meta_analysis",
    "Vegetable butters and oils as dermal ingredients: review of clinical studies": "review_narrative",
    "Vegetable butters and oils as dermal ingredients: clinical studies review": "review_narrative",
}
REMOVED = {
    "FDA OTC sunscreen monograph M020": "Removed 2026-11-25 by owner decision: US monograph status is out of scope for sunscreen filters; it was never evidence of efficacy.",
    "ECHA EU cosmetic preservative listings": "Replaced 2026-11-25 by owner decision with Annex V of Regulation (EC) No 1223/2009 (SRC-0001).",
}
# The 19 ingredient-specific evidence rows: what was actually tested, read from Evidence_Scope.
TEST_MATERIAL_BY_INCI = {
    "Niacinamide": ("ingredient_vs_vehicle", ""),
    "Azelaic Acid": ("isolated_ingredient", "20%"),
    "Tranexamic Acid": ("ingredient_vs_vehicle", "5%"),
    "Ascorbic Acid": ("isolated_ingredient", "5%"),
    "Salicylic Acid": ("isolated_ingredient", "peel strength (not 0.5-2%)"),
    "Glycolic Acid": ("isolated_ingredient", "peel strength (not leave-on)"),
    "Lactic Acid": ("ingredient_class_only", ""),
    "Alpha-Arbutin": ("multi_ingredient_formulation", "5% with 2% kojic acid"),
    "Retinol": ("ingredient_vs_vehicle", ""),
    "Isobutylamido Thiazolyl Resorcinol": ("ingredient_vs_vehicle", ""),
    "Ceramide NP": ("multi_ingredient_formulation", ""),
    "Palmitoyl Pentapeptide-4": ("ingredient_vs_vehicle", "3 ppm"),
    "Centella Asiatica Extract": ("ingredient_vs_vehicle", ""),
    "Hydrogenated Lecithin": ("multi_ingredient_formulation", ""),
    "Glycerin": ("ingredient_vs_vehicle", ""),
    "Urea": ("multi_ingredient_formulation", "4% urea + 4% sodium chloride"),
    "Panthenol": ("ingredient_vs_vehicle", ""),
    "Butyrospermum Parkii (Shea) Butter": ("ingredient_class_only", ""),
    "Helianthus Annuus (Sunflower) Seed Oil": ("isolated_ingredient", "neat oil"),
    "Cocos Nucifera (Coconut) Oil": ("ingredient_class_only", ""),
}


def seed() -> None:
    targets = ["studies.csv", "evidence_links.csv", "category_context.csv", "regulatory.csv",
               "use_ranges.csv", "change_log.csv"]
    existing = [t for t in targets if (CURATED / t).exists()]
    if existing:
        raise SystemExit(f"Refusing to overwrite hand-maintained tables: {existing}")

    raw = raw_rows()
    ingredients = base_ingredients()
    id_by_inci = {r["inci_name"]: r["id"] for r in ingredients}

    # Studies: one row per distinct URL (the butters/oils review appears under two titles).
    studies, sid_by_url = [], {}
    for r in raw:
        url, title = r["Reference_URL"].strip(), r["Reference_Title"].strip()
        if url in sid_by_url:
            continue
        stype = SOURCE_TYPE_BY_TITLE.get(title, "")
        prefix = "SRC" if stype in {"identity_database", "regulatory_listing"} else "STU"
        sid = f"{prefix}-{len(studies) + 2:04d}"  # SRC-0001 reserved for Annex V
        sid_by_url[url] = sid
        pmid = url.rstrip("/").rsplit("/", 1)[-1] if "pubmed" in url else ""
        studies.append({
            "id": sid, "aliases": "", "source_type": stype, "title": "", "raw_title": title,
            "authors": "", "year": "", "journal": "", "doi": "", "pmid": pmid, "url": url,
            "population": "", "phototypes": "not_reported", "sample_size": "",
            "funding_or_conflicts": "", "limitations": "",
            "verification_status": "removed" if title in REMOVED else "unverified",
            "verified_on": "", "notes": REMOVED.get(title, ""),
        })
    studies.insert(0, {
        "id": "SRC-0001", "aliases": "", "source_type": "regulation",
        "title": "Regulation (EC) No 1223/2009 on cosmetic products, Annex V (list of preservatives allowed in cosmetic products), consolidated text",
        "raw_title": "", "authors": "European Parliament and Council", "year": "2009", "journal": "Official Journal of the European Union",
        "doi": "", "pmid": "", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02009R1223-20250901",
        "population": "", "phototypes": "not_applicable", "sample_size": "", "funding_or_conflicts": "", "limitations": "",
        "verification_status": "unverified", "verified_on": "",
        "notes": "Replaces the raw ECHA citation. Consolidated-version URL to be confirmed during regulatory verification.",
    })

    links, context, seen_ctx = [], [], set()
    for r in raw:
        inci, title = r["INCI_Name"].strip(), r["Reference_Title"].strip()
        sid = sid_by_url[r["Reference_URL"].strip()]
        cat = CATEGORIES[r["Functional_Category"]][0]
        specific = r["Direct_Human_Study_Specific_To_Ingredient"].startswith("Some")
        if specific and inci in TEST_MATERIAL_BY_INCI:
            material, conc = TEST_MATERIAL_BY_INCI[inci]
            links.append({
                "id": f"EVL-{len(links) + 1:04d}", "ingredient_id": id_by_inci[inci], "study_id": sid,
                "purpose": "efficacy", "test_material": material, "concentration_studied": conc,
                "endpoints": "", "finding_summary": "", "phototype_relevance": "not_reported",
                "statistically_significant": "not_reported", "status": "imported_unverified",
                "notes": "Raw scope: " + r["Evidence_Scope"].strip(),
            })
        elif title in REMOVED:
            continue
        else:
            key = (cat, sid)
            if key not in seen_ctx:
                seen_ctx.add(key)
                context.append({"category": cat, "study_id": sid,
                                "raw_scope": r["Evidence_Scope"].strip(),
                                "note": "Category-level context only. Not evidence for any individual ingredient unless an evidence link says so."})

    ranges = []
    for r, ing in zip(raw, ingredients):
        lo, hi = parse_range(r["Typical_Use_Percent_Range"])
        ranges.append({"id": f"RNG-{len(ranges) + 1:04d}", "ingredient_id": ing["id"], "product_type": "general",
                       "min_percent": lo, "max_percent": hi, "basis": "unknown",
                       "status": "imported_unverified", "source_id": "",
                       "note": "Raw: indicative screening range, not a regulatory limit or validated supplier recommendation."})

    reg = [
        {"id": "REG-0001", "ingredient_id": id_by_inci["Alpha-Arbutin"], "jurisdiction": "EU",
         "status": "permitted_with_restrictions", "max_concentration": "2% face cream; 0.5% body lotion",
         "product_types": "face cream; body lotion", "conditions": "Hydroquinone impurity to be monitored (raw note)",
         "legal_reference": "Commission Regulation (EU) 2024/996", "source_id": "", "status_basis": "imported_unverified", "last_verified": ""},
        {"id": "REG-0002", "ingredient_id": id_by_inci["Retinol"], "jurisdiction": "EU",
         "status": "permitted_with_restrictions", "max_concentration": "0.05% retinol equivalent body lotion; 0.3% RE other products",
         "product_types": "body lotion; hand/face and other leave-on/rinse-off", "conditions": "Raw note mentions pregnancy-related precautions",
         "legal_reference": "Commission Regulation (EU) 2024/996", "source_id": "", "status_basis": "imported_unverified", "last_verified": ""},
    ]

    from build import CHANGE_FIELDS, CONTEXT_FIELDS, LINK_FIELDS, RANGE_FIELDS, REG_FIELDS, STUDY_FIELDS
    write_csv(CURATED / "studies.csv", studies, STUDY_FIELDS)
    write_csv(CURATED / "evidence_links.csv", links, LINK_FIELDS)
    write_csv(CURATED / "category_context.csv", context, CONTEXT_FIELDS)
    write_csv(CURATED / "use_ranges.csv", ranges, RANGE_FIELDS)
    write_csv(CURATED / "regulatory.csv", reg, REG_FIELDS)
    write_csv(CURATED / "change_log.csv", [], CHANGE_FIELDS)
    print(f"Seeded {len(studies)} sources, {len(links)} evidence links, {len(context)} category-context rows, "
          f"{len(ranges)} ranges, {len(reg)} regulatory entries.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seed", action="store_true", help="write hand-maintained tables (first run only)")
    args = p.parse_args()
    if args.seed:
        seed()
    else:
        print(f"{len(base_ingredients())} base ingredient records OK")
    sys.exit(0)
