#!/usr/bin/env python3
"""Turn a dated research-findings table into change-log entries.

Findings live in data/curated/research/*.csv. Each run appends only the edits
not yet logged, so it is safe to re-run. Then run build.py.

    python scripts/apply_findings.py data/curated/research/cas_findings_2026-11-25.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

from build import CHANGE_FIELDS, curated_ingredients
from common import CAS_RE, CURATED, VALUE_STATUS, cas_checksum_ok, read_csv, write_csv

FIELD_MAP = {"cas_number": "cas_number", "ec_number": "ec_number", "cas_status": "cas_status",
             "sources": "cas_sources", "note": "cas_note"}


def main(path: Path) -> int:
    date = path.stem.rsplit("_", 1)[-1]
    findings = read_csv(path)
    current = {r["inci_name"]: r for r in curated_ingredients()}
    log = read_csv(CURATED / "change_log.csv")
    next_id = len(log) + 1
    added = 0
    for f in findings:
        ing = current.get(f["inci_name"])
        if ing is None:
            raise SystemExit(f"Unknown INCI in findings: {f['inci_name']}")
        if f["cas_status"] not in VALUE_STATUS:
            raise SystemExit(f"Bad status {f['cas_status']} for {f['inci_name']}")
        cas = f["cas_number"].strip()
        if cas and not (CAS_RE.match(cas) and cas_checksum_ok(cas)):
            raise SystemExit(f"CAS fails checksum: {f['inci_name']} {cas}")
        if f["cas_status"] == "source_verified" and len([s for s in f["sources"].split("|") if s]) < 2:
            raise SystemExit(f"source_verified needs two sources: {f['inci_name']}")
        updates = {FIELD_MAP[k]: f[k].strip() for k in FIELD_MAP}
        if f["ec_number"].strip():
            updates["ec_status"] = "source_verified" if f["cas_status"] == "source_verified" else "imported_unverified"
        for field, new in updates.items():
            old = ing[field]
            if old == new:
                continue
            log.append({"id": f"CHG-{next_id:05d}", "date": f"{date[:4]}-{date[4:6]}-{date[6:]}" if "-" not in date else date,
                        "record_id": ing["id"], "field": field, "old_value": old, "new_value": new,
                        "reason": f"Identifier research {date}: see {path.name}",
                        "source_ids": f["sources"]})
            ing[field] = new
            next_id += 1
            added += 1
    write_csv(CURATED / "change_log.csv", log, CHANGE_FIELDS)
    print(f"Appended {added} change-log entries from {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
