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
- **Missing CAS (50 of 50).** My findings (`cas_findings_2026-11-25.csv`) were superseded by the owner-confirmed list (`cas_verified_2026-11-25.csv`, 292 change-log entries).
- **References (24 of 24 dataset studies).** `reference_verification_2026-11-25.csv`, applied by `scripts/apply_references.py` (refuses PMID mismatches and single-source verifications; idempotent). All 24 are `identity_verified` at abstract level; Ceramide NP trial authors not confirmed. The 19 evidence links now carry concentration, endpoint, finding, significance and caveats.
  - The remaining dataset sources are regulations/identity databases (SRC-*), not studies. Two (FDA M020, ECHA) are `removed` per owner decisions 1–2.
- **Atlas references (13).** MS007 authors filled (Chang YF et al.). DOIs added for MS004, MS005, MS007, MS009. MS003 (*Cutis* 2002) and MS012 (*JCAD* 2022) have no DOI assigned; the cards say so. The atlas validator and tests no longer hard-code 13 studies.
- **EU limits.** `eu_limits_2026-11-25.csv` → 19 rows in `regulatory.csv`, one per ingredient × product type:
  - Annex V: phenoxyethanol, benzyl alcohol, benzoic acid/sodium benzoate, sorbic acid/potassium sorbate, dehydroacetic acid, chlorphenesin (single source; flagged), salicylic acid (preservative use).
  - Annex III: salicylic acid (2019/1966), alpha-arbutin and retinol (2024/996).
  - Ethylhexylglycerin and caprylyl glycol are not Annex V preservatives and have no row.
- **Product-type ranges** for retinol, alpha-arbutin and salicylic acid replace the old general rows (kept as `superseded`). The maximum is the EU limit; the minimum is blank because no sourced minimum exists. The validator now errors if a range exceeds the limit for the same product type.
- **Allanblackia removed** (owner decision). ING-129 is dropped from the curated data by a logged `__record__` removal (CHG entry); the raw row is untouched. Research note kept in `data/curated/research/allanblackia_species_2026-11-25.md`.
- **Checks.** 0 validation errors, 100 warnings (open uncertainty); 14 database tests and 3 atlas tests pass.

## Waiting on the owner
- Nothing outstanding. Published to github.com/llmimzy/shamim-cosmetic-formulation (main).

## Next, in order
1. The 90 CAS numbers from the raw file stay `imported_unverified`; the owner chose not to re-check them (2026-11-25).
2. Full-text extraction for the key studies (effect sizes, phototype subgroups), moving them from `identity_verified` to `content_extracted`.
3. Phase 4–6: compatibility rules, melanated-skin framework, African botanicals, explorer, README.
