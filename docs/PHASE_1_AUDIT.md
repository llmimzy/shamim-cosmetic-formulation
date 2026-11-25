# Phase 1 — Audit, architecture and implementation plan

**Status:** draft for approval · **Date:** 2026-11-25 · **Scope:** this repository only (not the portfolio website)

AI assistance: this audit was prepared with Claude (Anthropic) and is for review by Shamim Quresh. Any statement here about a paper's existence or content was checked only as described in §4. Everything else remains unverified.

---

## 1. What exists today

| Item | Finding |
|---|---|
| Repository | `llmimzy/shamim-cosmetic-formulation` (renamed). Contains one commit with a two-line README and nothing else, so no existing code or schemas have to be preserved. |
| Existing README text | It describes the repo as worksheets for HLB, pH and stability logs, an INCI glossary and East African regulatory steps, and says it is "not a substitute for lab testing or regulatory sign-off". I'll keep that disclaimer and widen the README. |
| Profile repo `llmimzy/Shamim-Quresh` | Calls this "a formulation toolkit" and says AI assistance is disclosed in each repo. I'll follow both conventions. Its career facts are the only source for the README's experience section. |
| `AGENTS.md` / `CLAUDE.md` / config | None. |
| Source data | `data/raw/` holds the CSV and XLSX, unmodified, with SHA-256 hashes. |

## 2. The dataset at a glance

- **Size:** 140 ingredients, 25 columns, 14 categories × 10. The CSV and the XLSX main sheet are identical. The XLSX also carries an "Evidence Method" sheet dated 2026-11-22.
- **Integrity:** there are no duplicate INCI names and no duplicate CAS numbers. All 90 CAS numbers present have a valid check digit. 50 CAS numbers are blank, and the Evidence Method sheet says that is deliberate.
- **Already done well:** every concentration range is labelled "indicative screening range, NOT a regulatory limit". Each evidence row says whether the study was multi-ingredient. Peel studies are flagged as not supporting low-dose daily use, and the 90% rule is recorded as removed. I'll keep these caveats.

## 3. Data-quality findings

### 3.1 Most "ingredient" fields are really category statements
In 12 of 25 columns, every ingredient in a category has the same value. That includes:

- `Relevance_to_Melanated_Skin`: 14 distinct sentences for 140 ingredients.
- `Skin_Applications`, `Hair_Applications` and `Body_Applications`.
- `Active_Matter_Note`, `Typical_Range_Status` and most of `Regulatory_or_Safety_Note` (114 rows share one generic sentence).

**Consequence:** today the melanated-skin assessment is per category, not per ingredient. Shea butter and cocoa butter get identical relevance text, and so do all 10 sunscreen filters. I will import these as `imported_unverified` category notes, not as ingredient findings.

### 3.2 Empty or near-empty fields
| Field | Populated |
|---|---|
| `Active_Matter_Percent` | 0 / 140 |
| `Recommended_pH` | 0 / 140 |
| `HLB` | 4 / 140 (PEG-100 Stearate 18.8, Polysorbate 80 15.0, Polysorbate 20 16.7, Glyceryl Stearate 3.8) |
| `CAS_Number` | 90 / 140 |

`Phase_to_Add` has 30 free-text variants (e.g. "Water", "Cool-down water", "Water/cool-down; pH adjust"). These will be normalised to a fixed list, with the original text kept.

### 3.3 Fields required by the brief that are absent
None of these exist in the source and all start as `not_researched`:

- **Identity:** common name, EC number, chemical family, secondary functions, origin class, botanical name and plant part, standardisation requirements.
- **Formulation:** clinically tested concentration, supplier-grade concentration, processing temperature, oxidation sensitivity, photostability, known incompatibilities, preservative interactions.
- **Efficacy:** mechanism of action, Fitzpatrick IV–VI suitability, per-concern relevance, PIH/irritation risk.
- **Every study field:** authors, year, journal, DOI, design, sample size, phototypes, concentration, duration, comparator, endpoints, results, significance, limitations.
- **Every per-jurisdiction regulatory field.** No row covers Kenya, the UK or China, and only six rows name a specific EU or US limit.

### 3.4 Reference problems (most important)
There are 28 reference titles (27 URLs) for 140 ingredients. 121 rows are marked "not established from category reference", meaning a single shared paper stands in for many different ingredients:

| Shared reference | Rows using it | Problem |
|---|---|---|
| EU CosIng database | 29 | An identity/regulatory listing, not evidence of efficacy. Move it to the identity/regulatory sources table. |
| Vegetable butters and oils clinical-studies review (PMID 35548366) | 19 | The same paper appears under **two different title spellings**. It does not cover most of the butters it is attached to. |
| FDA OTC sunscreen monograph M020 | 10 | Cited for all 10 filters, which reads as US authorisation. Of these filters, zinc oxide, titanium dioxide and avobenzone are the long-standing US monograph filters. Bemotrizinol's US status is described in the dataset as a 2026 order and **needs checking**. The other six should be recorded as **not permitted in US OTC sunscreens unless verified otherwise**. |
| "ECHA EU cosmetic preservative listings" | 10 | EU cosmetic preservatives are listed in **Annex V of Regulation (EC) No 1223/2009** (searchable in CosIng), not in an ECHA register, so the URL needs checking. Ethylhexylglycerin and caprylyl glycol are not Annex V preservatives. They are multifunctional boosters (see 3.5). |
| Lamellar barrier-formulation RCT (PMID 34921679) | 10 | A multi-lipid finished product used as the reference for 10 different moisturiser actives, from cholesterol to ectoin. |
| OTC moisturisers barrier study (PMID 32947459) | 10 | A small within-patient comparison of commercial moisturisers on non-lesional atopic skin, which the authors describe as underpowered. It is **not** about any of the 10 named emollients. |
| PIH topical-treatment systematic review (PMID 34525885) | 9 | A real 2022 review (Tan et al., *J Dermatol Treat*). Whether it covers rooibos, moringa leaf, hibiscus, mulberry and the others it is attached to has to be checked one by one. |
| Ceramide-dominant moisturiser RCT (PMID 33984185) | 9 | A finished multi-ceramide cream, so it can't tell the 9 ceramide species apart. |
| Oral and topical peptides meta-analysis (PMID 41924746) | 9 | This 2026 *Frontiers in Medicine* meta-analysis pooled 19 RCTs. Most participants were in **oral** peptide trials and only two trials were topical, so it cannot support nine specific topical INCI peptides. |
| Emollient-rich moisturiser study (PMID 40176773) | 8 | A multi-ingredient product used as the reference for 8 different humectants. |

Specific rows:
- **Isobutylamido Thiazolyl Resorcinol (Thiamidol):** the trial is described correctly: a 24-week, double-blind, vehicle-controlled study in phototypes III–V (*J Dermatol* 2021). The author affiliations still need recording to check for manufacturer involvement. The CAS number is blank even though this is a single defined molecule, so it can be found.
- **Ceramide NP:** the trial exists (adults with moderate atopic dermatitis, n = 60, finished emollient vs placebo). The abstract describes "more favourable numerical trends", so it must be checked whether the between-group differences were significant before the trial supports any claim.
- **Alpha-arbutin:** the cited study tested 5% alpha-arbutin combined with kojic acid. That is above the EU face-cream limit stated in the row's own note (2%), and it is a combination.
- **Tranexamic acid:** the population was Asian patients; the phototype range has to be confirmed. **Palmitoyl Pentapeptide-4:** the population was Caucasian, as the dataset already notes.
- **Titles:** most are paraphrased rather than exact. No row has authors, year, journal or DOI.

### 3.5 Classification and nomenclature issues
- **Ethylhexylglycerin and caprylyl glycol** sit under Preservatives but are boosters/multifunctionals. Proposed: keep them in the category so it stays at 10 records as the brief requires, but tag them "preservative booster, not a stand-alone preservative" and block any automated check from counting them as a preservative system.
- **Cetyl alcohol** (under Emollients) is chiefly a consistency factor and co-emulsifier. **Glyceryl stearate (HLB 3.8)** is a co-emulsifier. **Hydrogenated lecithin** has an emulsifier role but its evidence row is copied from the moisturiser group. All three get secondary functions.
- **Possible ceramide synonyms:** "Ceramide NG"/"Ceramide NDS" and "Ceramide AG"/"Ceramide ADS" may be old and new INCI names for the same dihydrosphingosine ceramides. Check against CosIng before treating them as four distinct materials.
- **INCI form:** names mix EU and US styles (e.g. US "Butyrospermum Parkii (Shea) Butter"). Store the CosIng name as primary and the US form as a variant.
- **Category labels:** these differ from the brief ("Thickeners" vs "Thickeners and rheology modifiers"; "Moisturizers" vs "Moisturisers"). They will be normalised to the brief's 14 labels, with the original text kept.
- **Moringa** appears twice, as leaf extract and seed oil. Both records stay because they are different materials, and both will link to one botanical record.
- **Grade-dependent CAS numbers:** bisabolol 515-69-5 may refer to a different stereoisomer from natural (−)-α-bisabolol. Carbomer, sodium polyacrylate and the PEG/polysorbate CAS numbers are generic polymer identifiers. A valid checksum proves none of these identities.

### 3.6 Concentration ranges that cross a regulatory limit for some product types
Each of these ranges is acceptable for one product type but not for another, so ranges will become product-type specific:

| Ingredient | Recorded range | Issue to resolve |
|---|---|---|
| Retinol | 0.05–0.3% | The row's own note gives an EU limit of 0.05% retinol equivalent in body lotion, so above 0.05% is face-only. |
| Alpha-arbutin | 0.2–2% | The row's own note gives an EU limit of 0.5% in body lotion. |
| Salicylic acid | 0.5–2% | EU limits differ by product type, including lower body-lotion limits. To verify. |
| Azelaic acid | 5–20% | 15–20% strengths are typically medicines in many markets. Cosmetic status needs a per-market check. |
| Sunscreen filters | various | Each filter's maximum differs by jurisdiction, and several filters are not permitted at all in the US. |

### 3.7 African botanical coverage
- **Present:** shea, marula, baobab, moringa (leaf and seed oil), rooibos, *Allanblackia*, *Pentadesma*, argan, hibiscus.
- **Not African:** several butters (*Garcinia indica*, *Shorea*, murumuru, cupuaçu). That is fine for the database, but the African-botanicals section will be scoped to species with documented African origin or sourcing.

## 4. How far the references have been checked so far
- **Spot-checked by search:** PMIDs 42868105, 41924746, 32947459, 34676600 and 34525885, plus the titles behind them. Each found paper is real and broadly matches its title. The limitations above come from their published abstracts or summaries.
- **Not yet checked:** the remaining 22 references. Direct PubMed access is blocked in this workspace, so Phase 3 will check every reference through search and record DOI, PMID, authors and population with a `verified_on` date.

## 5. Proposed architecture

```text
shamim-cosmetic-formulation/
├── README.md  LICENSE  CONTRIBUTING.md  CITATION.cff  CHANGELOG.md
├── data/
│   ├── raw/                  # supplied files, never edited (+ hashes)
│   ├── curated/              # canonical tables (CSV, Excel-editable)
│   │   ├── ingredients.csv
│   │   ├── studies.csv           # papers and official sources
│   │   ├── evidence_links.csv    # study × ingredient × purpose
│   │   ├── regulatory.csv        # ingredient × jurisdiction
│   │   ├── botanicals.csv
│   │   ├── compatibility_rules.csv
│   │   └── change_log.csv        # every edit vs raw, with reason
│   ├── schemas/database.schema.json
│   └── build/                # generated: database.json, flat cleaned CSV
├── research/  melanated-skin/ (evidence-atlas/ already added)  african-botanicals/  active-ingredients/
│              ceramides-and-peptides/  evidence-reviews/
├── formulation/  ingredient-selection/  compatibility/  stability/  formulation-frameworks/
├── regulatory/  kenya/  eu/  uk/  us/  china/
├── explorer/index.html       # static, no server, GitHub Pages
├── scripts/  import_raw.py  build.py  validate.py  score.py
├── tests/
└── docs/
```

- **Canonical format: CSV tables.** You can edit them in Excel or Google Sheets without code. Multi-value cells use `|`. `build.py` validates them against the schema and generates `database.json` for the explorer, plus the flat "cleaned CSV" deliverable.
- **IDs:** `ING-001`…`ING-140` in raw order, plus `STU-/SRC-`, `EVL-`, `REG-`, `BOT-`, `CMP-` and `CHG-` prefixes. IDs are never reused.
- **Stack:** Python 3 standard library plus `jsonschema` and `pytest`, both already available. The explorer is plain HTML/CSS/JS with no build step.
- **Draft schema:** `data/schemas/database.schema.json`, already written and checked as valid JSON Schema. Its key design rules:
  - every uncertain value carries its own status;
  - "what was tested" (isolated ingredient, ingredient vs vehicle, multi-ingredient formulation, or class only) is a required field on every evidence link;
  - a regulatory listing can never be typed as a clinical study;
  - melanated-skin evidence is graded in five tiers, matching section 7 of the brief.

## 6. Evaluation framework (Phase 4 preview)
- Six dimensions with the brief's starting weights (30/20/15/15/10/10), stored in `config/scoring.json`.
- Each dimension is scored only from recorded evidence. A missing dimension shows as **insufficient data** and is excluded from the weighted total, not counted as zero.
- Every score carries a confidence label (High / Moderate / Low / Insufficient) based on how much of the weight actually has data.
- The output is labelled "formulation-screening priority", never an efficacy or safety prediction.

## 7. Decisions for you

| # | Decision | My recommendation |
|---|---|---|
| D1 | Canonical data format | **CSV tables** (Excel-editable), with JSON generated from them. |
| D2 | Licence for a public repo | **CC BY 4.0** for data and docs, **MIT** for code. Alternatively, all rights reserved if you want to restrict reuse. |
| D3 | Handling the shared category references | **Detach them** from the 121 ingredients. They move to a "context sources" list, and those ingredients show "no ingredient-specific evidence verified yet". The database will look thinner, but it will be accurate. |
| D4 | Phase 3 research order (140 ingredients is a large job) | **Tier 1:** the 10 actives, the 10 sunscreen filters, and the African botanicals (~9). **Tier 2:** ceramides, peptides and the other botanical extracts. **Tier 3:** functional excipients, which need regulatory and technical sources more than clinical trials. |
| D5 | Experience section in the README | Use **only** the facts already in your public profile README. Tell me of anything else to add. |
| D6 | Branch and visibility | Work stays on branch `phase-1-audit`, which hasn't been pushed. The repo is public, so I'll push only when you say so. |

## 8. Phased plan
1. **Phase 2 — Data integration.**
   - Import the raw file into the curated tables; normalise category, phase and solubility values.
   - Assign IDs, split out studies, evidence links and regulatory entries, and log every transformation in `change_log.csv`.
   - Build `validate.py` with the checks in brief §13 and the tests.
2. **Phase 3 — Evidence research.** Verify all 27 references, then research Tier 1, Tier 2 and Tier 3 in turn. For each: exact citation, DOI/PMID, population and phototypes, concentration, endpoints, results, significance and limitations. Unresolved items go to the backlog.
3. **Phase 4 — Formulation intelligence.** Compatibility rules, labelled *evidence-backed* vs *theoretical*, starting with the seven examples in the brief. Also: stability and manufacturing notes, the melanated-skin framework, the African-botanicals monographs, and the scoring script.
4. **Phase 5 — Explorer and documentation.** Static explorer (search, filters, evidence and phototype filters, compatibility view, citations, CSV export), README, CONTRIBUTING, CITATION, maintenance guide.
5. **Phase 6 — Testing and delivery.** Validation report, link checks, export round-trip tests, accessibility check of the explorer, final summary and prioritised verification backlog.

## 9. Addendum: Melanated Skin × Ingredient Response evidence atlas (added 2026-11-25)

**What it is.** A self-contained research module with:
- 13 studies (1988–2025), each with a PMID-linked evidence card;
- a 20-entry ingredient index, a methodology, an evidence matrix, formulation hypotheses and a research-gaps note;
- a stdlib-only validator, 3 tests and a static browser page.

**Where it is.** `research/melanated-skin/evidence-atlas/`, copied unchanged except for two files:
- its GitHub Actions workflow now lives at the repo root (`.github/workflows/validate.yml`) and runs in the atlas folder, because GitHub only runs workflows from the root;
- its `.gitignore` moved to the root.

Its validator and tests pass: 13 studies, 20 index entries, 3/3 tests OK.

**Why it matters for the main database.** The atlas is built on the right question for section 7 of the brief: it separates a *different response across phototypes* from *efficacy shown in a darker-skin cohort*. In Phase 2 I'll import its 13 studies into `studies.csv` (keeping the `MS###` IDs as aliases) and link them to the ingredients they actually tested:

| Atlas study | Links to database ingredient | Type of link |
|---|---|---|
| MS005 | Glycolic Acid | Cross-population photoresponse (small study) |
| MS006 | Lactic Acid, Retinol | Irritation/stinging provocation; safety, not efficacy |
| MS009 | Zinc Oxide, Titanium Dioxide | Comparator formula only (iron oxides were the variable) |
| MS011 | Ascorbic Acid | **Null result:** 7% ascorbic acid did not prevent visible-light pigmentation in phototypes III–IV. The Ascorbic Acid record must reflect this. |
| MS012 | Azelaic Acid | 20% in a single-active vehicle, phototypes IV–V; not significant versus control |
| MS013 | Isobutylamido Thiazolyl Resorcinol | PIH vs vehicle in phototypes V–VI. A different paper from the melasma trial already in the dataset. Manufacturer-affiliated authors are flagged. |

What the atlas covers that the database doesn't:
- Iron oxides, sodium lauryl sulfate and the prescription retinoids/hydroquinone are context only. None is one of the 140.
- **Iron oxides** are central to visible-light protection, which brief §7 prioritises, but are absent from the database. That's a candidate addition (backlog item 9).
- **Arbutin (MS012) is not alpha-arbutin.** It will *not* be linked to the Alpha-Arbutin record as efficacy evidence.

**Issues found in the atlas (to fix in Phase 3, not silently):**
- MS007 gives its author as "Racial differences cohort study authors", a placeholder, not real names. It needs the actual author list.
- DOI is blank for MS003, MS004, MS005, MS007, MS009 and MS012.
- Several sample sizes are "Not confirmed". That is honest, but they should be filled from the full text where available.
- `validate_data.py` hard-codes "exactly 13 studies" and the test hard-codes "8 cross-population". Both will fail as soon as a study is added, so in Phase 2 they become counts checked against the data.
- There will be two browser pages (the atlas page and the planned main explorer). In Phase 5 the main explorer will read the atlas studies too. The atlas page stays as a focused view.

**Licence.** The atlas is already released as CC BY 4.0 (content) + MIT (code), which matches recommendation D2. Approving D2 makes the whole repository consistent.

## 10. Initial verification backlog (top items)
1. Check the US status of the 10 sunscreen filters against the current FDA monograph and orders, especially bemotrizinol.
2. Replace the "ECHA preservative" source with Annex V of Regulation (EC) No 1223/2009 and record the per-preservative limits.
3. Verify all 27 PMIDs: existence, exact title, DOI, population.
4. Settle whether the ceramide INCI names NG/NDS and AG/ADS are synonyms.
5. Find the CAS for Isobutylamido Thiazolyl Resorcinol and the CAS/EC numbers for marula, baobab and the other botanicals (they may be grade-dependent).
6. Make retinol, alpha-arbutin and salicylic acid ranges product-type specific.
7. Check azelaic acid and tranexamic acid cosmetic vs medicinal status per market.
8. Find Kenya's requirements (KEBS standards, PPB boundary) for actives and sunscreens. No source in the dataset covers Kenya.
9. Decide whether to add iron oxides (CI 77491/77492/77499) as a visible-light-relevant ingredient. The atlas evidence (MS009, MS010) supports researching it.
10. Fill the missing authors/DOIs in the atlas (MS007 author list; DOIs for six studies).
