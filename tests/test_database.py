"""Tests for the curated database. Run: python -m pytest -q"""
import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build  # noqa: E402
import validate  # noqa: E402
from common import CURATED, cas_checksum_ok, read_csv  # noqa: E402
from import_raw import INGREDIENT_FIELDS, base_ingredients  # noqa: E402


def test_raw_file_untouched():
    rows = read_csv(ROOT / "data/raw/INCI_Melanated_Skin_140_Curated.csv")
    assert len(rows) == 140
    assert len({r["Functional_Category"] for r in rows}) == 14


def test_curated_ingredients_equal_raw_plus_change_log():
    """Every difference from the raw import must be explained by a logged change."""
    on_disk = read_csv(CURATED / "ingredients.csv")
    rebuilt = build.curated_ingredients()
    assert [{k: r[k] for k in INGREDIENT_FIELDS} for r in on_disk] == rebuilt


def test_ten_per_category():
    counts = {}
    for r in base_ingredients():
        counts[r["primary_category"]] = counts.get(r["primary_category"], 0) + 1
    assert set(counts.values()) == {10} and len(counts) == 14


def test_change_log_rejects_unlogged_old_value():
    recs = base_ingredients()
    bad = [{"id": "CHG-99999", "record_id": "ING-001", "field": "cas_number", "old_value": "WRONG",
            "new_value": "x", "reason": "test"}]
    with pytest.raises(build.ChangeLogError):
        build.apply_change_log(recs, bad)


def test_change_log_requires_reason():
    recs = base_ingredients()
    bad = [{"id": "CHG-99999", "record_id": "ING-001", "field": "notes", "old_value": "",
            "new_value": "x", "reason": " "}]
    with pytest.raises(build.ChangeLogError):
        build.apply_change_log(recs, bad)


@pytest.mark.parametrize("cas,ok", [("98-92-0", True), ("50-81-7", True), ("98-92-1", False),
                                     ("1428450-95-6", True), ("not-a-cas", False)])
def test_cas_checksum(cas, ok):
    assert cas_checksum_ok(cas) is ok


def test_validator_has_no_errors():
    errors, _warnings, _stats = validate.validate()
    assert errors == [], "\n".join(errors)


def test_uncertainty_is_reported_not_hidden():
    _errors, warnings, stats = validate.validate()
    assert stats["active_matter_missing"] > 0
    assert any("Active-matter" in w for w in warnings)


def test_removed_sources_not_used_as_evidence():
    studies = {s["id"]: s for s in read_csv(CURATED / "studies.csv")}
    for link in read_csv(CURATED / "evidence_links.csv"):
        assert studies[link["study_id"]]["verification_status"] != "removed"
    for ctx in read_csv(CURATED / "category_context.csv"):
        assert studies[ctx["study_id"]]["verification_status"] != "removed"


def test_build_json_round_trip():
    build.build()
    db = json.loads((ROOT / "data/build/database.json").read_text(encoding="utf-8"))
    removed = sum(c["field"] == "__record__" for c in read_csv(ROOT / "data/curated/change_log.csv"))
    assert len(db["ingredients"]) == 140 - removed
    with (ROOT / "data/build/ingredients_cleaned.csv").open(newline="", encoding="utf-8") as fh:
        flat = list(csv.DictReader(fh))
    assert [r["id"] for r in flat] == [r["id"] for r in db["ingredients"]]
    assert all(r["cas_number"] == d["cas_number"] for r, d in zip(flat, db["ingredients"]))
