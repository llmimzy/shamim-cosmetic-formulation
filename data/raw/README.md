# Raw source data (read-only)

These files are the dataset exactly as supplied. They are never edited. Every curated value in `data/curated/` traces back to a row here or to a logged change.

| File | Rows × columns | SHA-256 |
|---|---|---|
| `INCI_Melanated_Skin_140_Curated.csv` | 140 × 25 | `e8b47a6a8c91646158d8097affd8ce1a336500d622036162fad9c23803d2f390` |
| `INCI_Melanated_Skin_140_Curated.xlsx` | Sheet "INCI Database" 140 × 25; sheet "Evidence Method" 13 × 2 | `94bc542f62e45ccc215c4e01728ba6d538afe83c2ddee038467747f786eb1064` |

- The CSV and the XLSX "INCI Database" sheet are identical, cell for cell (checked 2026-11-25).
- The XLSX adds an "Evidence Method" sheet, dated 2026-11-22, which records the dataset's own caveats. Among them, the 90% efficacy threshold is marked as removed.
- Received: 2026-11-25.
- Status: a starting dataset, **not independently verified**. See `docs/PHASE_1_AUDIT.md`.
