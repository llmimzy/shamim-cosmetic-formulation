#!/usr/bin/env python3
"""Rebuild generated data from the raw file, the change log and the hand-maintained tables.

    raw CSV --import_raw.base_ingredients()--> base records
    base records + change_log.csv            --> data/curated/ingredients.csv
    all curated tables                       --> data/build/database.json
                                             --> data/build/ingredients_cleaned.csv (flat export)

Never edit data/curated/ingredients.csv by hand: add a row to change_log.csv.
"""
from __future__ import annotations

import json
import sys

from common import BUILD, CATEGORY_LABELS, CURATED, ROOT, read_csv, write_csv
from import_raw import INGREDIENT_FIELDS, base_ingredients

STUDY_FIELDS = ["id", "aliases", "source_type", "title", "raw_title", "authors", "year", "journal", "doi", "pmid",
                "url", "population", "phototypes", "sample_size", "funding_or_conflicts", "limitations",
                "verification_status", "verified_on", "notes"]
LINK_FIELDS = ["id", "ingredient_id", "study_id", "purpose", "test_material", "concentration_studied", "endpoints",
               "finding_summary", "phototype_relevance", "statistically_significant", "status", "notes"]
CONTEXT_FIELDS = ["category", "study_id", "raw_scope", "note"]
RANGE_FIELDS = ["id", "ingredient_id", "product_type", "min_percent", "max_percent", "basis", "status", "source_id", "note"]
REG_FIELDS = ["id", "ingredient_id", "jurisdiction", "status", "max_concentration", "product_types", "conditions",
              "legal_reference", "source_id", "status_basis", "last_verified"]
CHANGE_FIELDS = ["id", "date", "record_id", "field", "old_value", "new_value", "reason", "source_ids"]

ATLAS = ROOT / "research" / "melanated-skin" / "evidence-atlas" / "data"


class ChangeLogError(Exception):
    pass


def apply_change_log(records: list[dict], changes: list[dict]) -> list[dict]:
    """Apply logged edits in order. Each edit must state the value it replaces.

    A row with field '__record__', old_value 'present' and new_value 'removed' drops the whole
    record from the curated table. The raw row is kept unchanged in data/raw.
    """
    by_id = {r["id"]: r for r in records}
    removed = set()
    for c in changes:
        rec = by_id.get(c["record_id"])
        if rec is None or c["record_id"] in removed:
            raise ChangeLogError(f"{c['id']}: unknown or removed record {c['record_id']}")
        if c["field"] == "__record__":
            if (c["old_value"], c["new_value"]) != ("present", "removed") or not c["reason"].strip():
                raise ChangeLogError(f"{c['id']}: record removal must be present -> removed with a reason")
            removed.add(c["record_id"])
            continue
        if c["field"] not in INGREDIENT_FIELDS or c["field"] == "id":
            raise ChangeLogError(f"{c['id']}: field '{c['field']}' cannot be changed")
        if rec[c["field"]] != c["old_value"]:
            raise ChangeLogError(f"{c['id']}: {c['record_id']}.{c['field']} is '{rec[c['field']]}', "
                                 f"log expects '{c['old_value']}'")
        if not c["reason"].strip():
            raise ChangeLogError(f"{c['id']}: reason is required")
        rec[c["field"]] = c["new_value"]
    return [r for r in records if r["id"] not in removed]


def curated_ingredients() -> list[dict]:
    return apply_change_log(base_ingredients(), read_csv(CURATED / "change_log.csv"))


def build() -> dict:
    ingredients = curated_ingredients()
    write_csv(CURATED / "ingredients.csv", ingredients, INGREDIENT_FIELDS)

    studies = read_csv(CURATED / "studies.csv")
    links = read_csv(CURATED / "evidence_links.csv")
    context = read_csv(CURATED / "category_context.csv")
    ranges = read_csv(CURATED / "use_ranges.csv")
    regulatory = read_csv(CURATED / "regulatory.csv")
    atlas = read_csv(ATLAS / "studies.csv") if (ATLAS / "studies.csv").exists() else []

    db = {
        "meta": {
            "title": "Shamim Quresh | Cosmetic Formulation Intelligence: ingredient database",
            "status": "Formulation-screening reference. Not a safety assessment, regulatory clearance or efficacy guarantee.",
            "categories": CATEGORY_LABELS,
            "counts": {"ingredients": len(ingredients), "sources": len(studies), "evidence_links": len(links),
                       "regulatory_entries": len(regulatory), "atlas_studies": len(atlas)},
        },
        "ingredients": ingredients, "use_ranges": ranges, "sources": studies, "evidence_links": links,
        "category_context": context, "regulatory": regulatory, "atlas_studies": atlas,
    }
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / "database.json").write_text(json.dumps(db, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # Flat, cleaned export: one row per ingredient, general range plus evidence counts.
    general = {r["ingredient_id"]: r for r in ranges if r["product_type"] == "general"}
    n_links = {}
    for link in links:
        n_links[link["ingredient_id"]] = n_links.get(link["ingredient_id"], 0) + 1
    flat_fields = INGREDIENT_FIELDS + ["category_label", "typical_use_min", "typical_use_max", "typical_use_status",
                                       "evidence_link_count"]
    flat = []
    for ing in ingredients:
        g = general.get(ing["id"], {})
        flat.append({**ing, "category_label": CATEGORY_LABELS[ing["primary_category"]],
                     "typical_use_min": g.get("min_percent", ""), "typical_use_max": g.get("max_percent", ""),
                     "typical_use_status": g.get("status", ""), "evidence_link_count": n_links.get(ing["id"], 0)})
    write_csv(BUILD / "ingredients_cleaned.csv", flat, flat_fields)
    return db["meta"]["counts"]


if __name__ == "__main__":
    try:
        counts = build()
    except ChangeLogError as e:
        print(f"BUILD FAILED: {e}")
        sys.exit(1)
    print("Built:", ", ".join(f"{k}={v}" for k, v in counts.items()))
