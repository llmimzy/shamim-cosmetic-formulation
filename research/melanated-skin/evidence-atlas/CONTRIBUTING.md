# Contributing and scientific correction policy

Thanks for helping improve scientific accuracy. Contributions should make the catalogue **more falsifiable**, not more promotional.

## Propose a new paper

Open an issue or pull request with: stable PMID/DOI; exact title; population and sample sizes; measured phototypes/melanin index; intervention and vehicle; endpoint; comparator; effect size/CI; whether there was a formal treatment-by-phototype interaction test; conflicts and limitations; and working primary-source link.

1. Add one row to `data/studies.csv` using a unique `MS###` ID.
2. Add one corresponding `studies/MS###.md` evidence card.
3. Add its ingredient(s) to `data/ingredient_index.csv`, referencing the study ID.
4. Run `python scripts/build_site_data.py` and `python scripts/validate_data.py`.
5. Run `python -m unittest discover -s tests -v`.
6. Update `docs/evidence-matrix.md` if the inference category changes.

Do not publish copyrighted PDFs, lengthy verbatim abstracts, fabricated p-values or unverified subgroup numbers. Be precise about race/ethnicity and phototype. State uncertainty openly. This repository is not a platform for skin-lightening product sales claims.
