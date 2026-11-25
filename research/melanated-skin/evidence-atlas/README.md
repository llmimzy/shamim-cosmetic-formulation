# Melanated Skin × Ingredient Response

**A curated evidence atlas for cosmetic formulation and skin-of-colour research.**  
*Research compilation by Shamim Quresh · last reviewed 25 November 2026*

> **Core question:** When does a skincare ingredient or finished formulation produce a measurably different outcome across populations with different pigmentation, and when has efficacy merely been demonstrated in a darker-skin cohort?

This repository brings together **13 peer-reviewed papers** (1988–2025) and treats their distinctions as a feature, not a footnote. It spans photoprotection, tyrosinase inhibitors, retinoids, exfoliants, surfactant irritation, post-inflammatory hyperpigmentation (PIH), and barrier measurements. It is intended to support *critical scientific analysis and formulation research*, not marketing shortcuts.

## Start here

| Path | Purpose |
|---|---|
| [`data/studies.csv`](data/studies.csv) | Primary, filterable study catalogue: design, population, outcomes, limitations, source links |
| [`data/ingredient_index.csv`](data/ingredient_index.csv) | Ingredient-to-publication cross-reference (not an INCI or dosing recommendation) |
| [`studies/`](studies/) | Thirteen evidence cards: result, what it does **not** prove, formulation question |
| [`docs/methodology.md`](docs/methodology.md) | Inclusion rules, study categorisation, limits of phototype and ethnicity proxies |
| [`docs/evidence-matrix.md`](docs/evidence-matrix.md) | Findings grouped by problem and strength of inference |
| [`docs/formulation-implications.md`](docs/formulation-implications.md) | Hypothesis-led formulation and testing priorities |
| [`docs/research-gaps.md`](docs/research-gaps.md) | Priorities for future IV–VI research and African participant recruitment |
| [`docs/index.html`](docs/index.html) | Static, searchable research browser suitable for GitHub Pages |
| [`scripts/search.py`](scripts/search.py) | Command-line ingredient and evidence lookup |
| [`scripts/validate_data.py`](scripts/validate_data.py) | Catalogue integrity checks |

## What this evidence *does* and *does not* establish

There are **8 studies comparing population groups** and **5 studying treatments within moderate/deeper phototypes**. Of the eight population comparisons, *some use ethnic or racial categories without measuring skin melanin*. Those studies cannot isolate pigmentation as the causal factor. The five darker-phototype studies demonstrate outcomes for particular formulations, exposures and populations; **they do not prove different efficacy versus lighter skin**.

A measurable outcome depends on multiple variables: **vehicle, dose, frequency, light source, skin condition, barrier function, study endpoint and individual variability**. Fitzpatrick type measures a tendency to burn/tan, not melanin concentration. The repository uses the phrase *skin of colour* only where the cited study or context warrants it, and explicitly states which groups were studied.

### Five research themes

1. **Pigment pathways.** Tyrosinase inhibitors and retinoids do not produce identical biochemical or clinical results in every study population.
2. **Visible light.** SPF addresses specified UV endpoints; protection against visible-light-associated darkening must be investigated separately.
3. **Irritation vs pigmentation.** A surfactant, acid or retinoid can change irritation, barrier metrics and pigmentation through different pathways.
4. **Tolerability is not a racial hierarchy.** Observed responses depend on context, and reports can differ across studies.
5. **Formulation is part of the intervention.** A clinical result for a specific product cannot be attributed automatically to an isolated ingredient.

## Illustrative findings

| Topic | Example | What it supports | What it does not prove |
|---|---|---|---|
| Irritation | [SLS patch testing](studies/MS002.md) | Barrier and vascular measurements can vary between studied groups | That all dark skin is more irritation-prone |
| Retinoids | [Adapalene pooled studies](studies/MS003.md) | Efficacy and dryness outcomes should be assessed independently | That all retinoids behave identically |
| Visible light | [Iron oxide formulas](studies/MS009.md) | Some tinted formulations outperform tested non-tinted UV sunscreen on visible-light pigmentation | That all tinted products have equivalent spectral protection |
| Active comparison | [Arbutin vs other agents](studies/MS012.md) | Vehicle-controlled comparisons can change observed rankings | That one active is universally superior |
| PIH | [Thiamidol research](studies/MS013.md) | Selected formulations improved PIH measures in studied darker-skin groups | A comparative response versus lighter skin |

## Inspect the catalogue

```bash
python scripts/validate_data.py
python scripts/search.py --ingredient 'iron oxides'
python scripts/search.py --topic 'Retinoid tolerability'
python scripts/build_site_data.py
python -m unittest discover -s tests -v
```

The website is deliberately dependency-free. After uploading the repository to GitHub, go to **Settings → Pages → Deploy from a branch → main /docs**. The [`docs/data/studies.json`](docs/data/studies.json) file is committed so the website works without a build server. When updating the CSV, rerun `python scripts/build_site_data.py` and commit the regenerated JSON.

## How to cite this repository

> Quresh, Shamim. (2026). *Melanated Skin × Ingredient Response: A Curated Evidence Atlas.* Research catalogue, version 1.0. Individual scientific findings should be cited to their original publications, not solely to this compilation.

## Research ethics and limitations

- No clinical dosing, safety, regulatory, or SPF claims can be inferred from this catalogue.
- Hydroquinone, tretinoin, adapalene and tazarotene can be regulated medicines; local authorisation and medical oversight requirements differ.
- Ingredient-index terms are for literature retrieval; verify regulatory INCI, CAS, supplier grades, use limits and safety separately before formulation.
- Product-specific and sponsor-associated evidence is flagged; see each study's `flags` field.
- These entries are **curated secondary summaries**, not systematic-review findings. Full-text checks and independent appraisal should precede consequential product decisions.
- This repository contains **no copied full-paper PDFs** or copyrighted article text.

Original synthesis and data structure are released under [CC BY 4.0](LICENSE-CONTENT). The scripts and browser are licensed under [MIT](LICENSE-CODE). Contributions and corrections are welcome via [`CONTRIBUTING.md`](CONTRIBUTING.md).
