"""Shared paths, vocabularies and CSV helpers. Standard library only."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "data" / "raw" / "INCI_Melanated_Skin_140_Curated.csv"
CURATED = ROOT / "data" / "curated"
BUILD = ROOT / "data" / "build"
CONFIG = ROOT / "config"

# Raw category label -> canonical key and display label (brief section 4).
CATEGORIES = {
    "Active ingredients": ("active_ingredients", "Active ingredients"),
    "Ceramides": ("ceramides", "Ceramides"),
    "Peptides": ("peptides", "Peptides"),
    "Botanical extracts": ("botanical_extracts", "Botanical extracts"),
    "Emulsifiers": ("emulsifiers", "Emulsifiers"),
    "Preservatives": ("preservatives", "Preservatives"),
    "Thickeners": ("thickeners_and_rheology_modifiers", "Thickeners and rheology modifiers"),
    "Surfactants": ("surfactants", "Surfactants"),
    "Humectants": ("humectants", "Humectants"),
    "Emollients": ("emollients", "Emollients"),
    "Moisturizers and barrier support": ("moisturisers_and_barrier_support", "Moisturisers and barrier-supporting ingredients"),
    "Sunscreen filters": ("sunscreen_filters", "Sunscreen filters"),
    "Natural butters": ("natural_butters", "Natural butters"),
    "Natural oils": ("natural_oils", "Natural oils"),
}
CATEGORY_KEYS = [v[0] for v in CATEGORIES.values()]
CATEGORY_LABELS = {v[0]: v[1] for v in CATEGORIES.values()}

# Raw free-text addition phase -> one or more controlled values (pipe-separated).
PHASES = {
    "Water": "water",
    "Oil": "oil",
    "Heated oil": "heated_oil",
    "Cool-down": "cool_down",
    "Cool-down water": "cool_down",
    "Lipid premix": "lipid_premix",
    "Water; neutralize": "water|neutralise",
    "Water/cool-down; pH adjust": "water|cool_down|ph_adjust",
    "Water/oil per formula": "water|oil",
    "Heated lipid premix": "heated_oil|lipid_premix",
    "Water/solvent": "water|solvent",
    "Oil/silicone": "oil",
    "Cool-down oil": "cool_down",
    "Dispersed oil or water": "dispersion",
    "Dispersed water": "dispersion",
    "Dispersed or dissolved per system": "formula_dependent",
    "Water or cool-down": "water|cool_down",
    "Cool-down water; low pH": "cool_down|ph_adjust",
    "Solvent phase; pH-dependent": "solvent|ph_adjust",
    "Cool-down oil; protect light/air": "cool_down",
    "Supplier-defined cool-down": "cool_down|supplier_defined",
    "Cool-down/solvent dependent": "cool_down|solvent",
    "Water or heated phase": "water|heated_oil",
    "Supplier-defined": "supplier_defined",
    "Disperse in water": "dispersion",
    "Water hydration": "water",
    "Heated surfactant phase": "heated_surfactant",
    "Cool-down/hydrate water": "cool_down|water",
    "Cool-down lipid": "cool_down",
    "Water/cool-down": "water|cool_down",
}
PHASE_VALUES = {"water", "oil", "heated_oil", "lipid_premix", "cool_down", "neutralise", "ph_adjust", "solvent",
                "dispersion", "formula_dependent", "supplier_defined", "heated_surfactant"}

SOLUBILITY = {
    "Water soluble or water dispersible; verify supplier grade": "water",
    "Oil/lipid soluble or dispersible; verify supplier grade": "oil",
    "Processing depends on grade and matrix": "grade_dependent",
}

VALUE_STATUS = {"not_researched", "imported_unverified", "source_verified", "grade_dependent",
                "conflicting_sources", "not_applicable", "owner_decision", "not_found",
                # owner-confirmed CAS audit vocabulary (data/curated/research/cas_verified_2026-11-25.csv)
                "verified_exact", "verified_representative", "verified_botanical", "generic_identifier",
                "unresolved", "conflicting_identity"}
VERIFIED_CAS = {"source_verified", "verified_exact", "verified_representative", "verified_botanical"}
EVIDENCE_TIERS = {"direct_fitzpatrick_iv_vi", "mixed_population", "lighter_phototypes_only",
                  "laboratory_or_mechanistic", "preliminary_or_unsubstantiated", "not_yet_assessed"}
SOURCE_TYPES = {"rct", "controlled_clinical", "systematic_review_or_meta_analysis", "human_instrumental",
                "observational_human", "ex_vivo", "in_vitro", "physicochemical", "supplier_technical",
                "regulatory_listing", "regulation", "review_narrative", "identity_database"}
STUDY_VERIFICATION = {"unverified", "identity_verified", "content_extracted", "removed"}
TEST_MATERIAL = {"isolated_ingredient", "ingredient_vs_vehicle", "multi_ingredient_formulation",
                 "ingredient_class_only", "comparator_only"}
PURPOSES = {"efficacy", "safety", "stability", "regulatory", "identity", "context"}
JURISDICTIONS = {"KE", "EU", "UK", "US", "CN"}
PHOTOTYPES = {"fitzpatrick_iv_vi", "mixed_including_iv_vi", "fitzpatrick_iii_iv", "fitzpatrick_i_iii",
              "not_reported", "not_applicable"}

CAS_RE = re.compile(r"^(\d{2,7})-(\d{2})-(\d)$")
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
PMID_RE = re.compile(r"^\d{1,9}$")


def cas_checksum_ok(cas: str) -> bool:
    """True if the CAS check digit is valid. Syntax only: says nothing about identity."""
    m = CAS_RE.match(cas)
    if not m:
        return False
    digits = (m.group(1) + m.group(2))[::-1]
    return sum((i + 1) * int(d) for i, d in enumerate(digits)) % 10 == int(m.group(3))


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
