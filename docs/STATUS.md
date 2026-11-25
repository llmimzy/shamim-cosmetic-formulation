# Status

_Last updated 2026-11-25. Branch `phase-1-audit`, not pushed._

## Owner decisions (2026-11-25)
| # | Decision |
|---|---|
| 1 | US FDA sunscreen monograph status is out of scope. The M020 citation is kept in the record as removed (SRC-0026), never used as evidence. |
| 2 | The ECHA preservative citation is replaced by Annex V of Regulation (EC) No 1223/2009 (SRC-0001). The Annex V limits are still to be entered. |
| 3 | Every reference is to be verified. |
| 4 | Ceramide NG / NDS and AG / ADS are **distinct** materials, not synonyms. |
| 5 | All CAS numbers are to be found and double-checked (two independent sources) before being reported. |
| 6 | Retinol, alpha-arbutin and salicylic acid ranges are to be split by product type. |
| 7 | Azelaic acid / tranexamic acid medicinal-status research: **not required**. |
| 8 | Kenya/KEBS regulatory research: **not required**. |
| 9 | Iron oxides: **not added**. |
| 10 | Evidence-atlas authors and DOIs are to be filled and double-checked before upload. |
| D1–D5 | Proceeding on the Phase 1 recommendations: CSV canonical tables; CC BY 4.0 + MIT; category references detached; Tier 1 research first; README experience from the public profile only. |

## Done
- **Phase 2 pipeline.** Raw file → `import_raw.py` → change log → `build.py` → `data/curated/ingredients.csv`, `data/build/database.json` and `data/build/ingredients_cleaned.csv`. A test proves the curated table equals raw + change log.
- **Missing CAS research (50 of 50).** Results are in `data/curated/research/cas_findings_2026-11-25.csv` and applied through 196 change-log entries:
  - 31 verified with two sources;
  - 6 grade-dependent (ceramide classes, polymers, olivate);
  - 5 conflicting (recorded with each candidate);
  - 7 not found;
  - 1 single-source (Ceramide EOS).
- **Validator and tests.** `scripts/validate.py` writes `docs/VALIDATION_REPORT.md` (0 errors, 133 open-uncertainty warnings). `tests/test_database.py` has 17 tests, all passing.
- **Evidence atlas** added under `research/melanated-skin/evidence-atlas/`.

## Next, in order
1. Double-check the **90 CAS numbers already in the raw file**; they are still `imported_unverified`.
2. Verify all **27 dataset references and 13 atlas references**: exact title, authors, year, journal, DOI, PMID, population. Fill MS007 authors and the six missing atlas DOIs.
3. Annex V preservative limits; product-type ranges for retinol, alpha-arbutin and salicylic acid.
4. Owner review: the INCI name "Allanblackia Floribunda Seed Butter" is not confirmed in CosIng (CosIng lists *A. stuhlmannii* and *A. parviflora*).
5. Phase 4–6: compatibility rules, melanated-skin framework, African botanicals, explorer, README.
