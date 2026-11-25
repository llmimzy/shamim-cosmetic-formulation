#!/usr/bin/env python3
"""Export CSV to the GitHub Pages website's same-directory JSON asset."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'data/studies.csv').open(newline='',encoding='utf-8') as f:
 rows=list(csv.DictReader(f))
output=ROOT/'docs/data/studies.json';output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Wrote {len(rows)} research entries to {output.relative_to(ROOT)}')
