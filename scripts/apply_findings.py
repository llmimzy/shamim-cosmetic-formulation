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
from common import CAS_RE, CURATED, VALUE_STATUS, VERIFIED_CAS, cas_checksum_ok, read_csv, write_csv

FIELD_MAP = {"cas_number": "cas_number", "ec_number": "ec_number", "cas_status": "cas_status",
             "sources": "cas_sources", "note": "cas_note"}
# Owner-confirmed audit format (adds identifiers and scope; supersedes earlier findings).
AUDIT_MAP = {"cas_number": "cas_number", "ec_number": "ec_number", "cas_status": "cas_status",
             "cas_scope": "cas_scope", "alternative_cas_numbers": "cas_alternatives",
             "related_or_candidate_cas_numbers": "cas_related", "unii": "unii", "pubchem_cid": "pubchem_cid",
             "supplier_sds_required": "supplier_sds_required", "chemical_identity": "chemical_identity",
             "verification_notes": "cas_note"}


def main(path: Path) -> int:
    date = path.stem.rsplit("_", 1)[-1]
    findings = [f for f in read_csv(path) if f.get("inci_name")]
    audit = "cas_scope" in findings[0]
    fmap = AUDIT_MAP if audit else FIELD_MAP
    reason = (f"Owner-confirmed CAS audit {date}: see {path.name}" if audit
              else f"Identifier research {date}: see {path.name}")
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
        for field in ("cas_number", "alternative_cas_numbers", "related_or_candidate_cas_numbers"):
            for cas in filter(None, f.get(field, "").split("|")):
                if not (CAS_RE.match(cas.strip()) and cas_checksum_ok(cas.strip())):
                    raise SystemExit(f"CAS fails checksum: {f['inci_name']} {cas}")
        srcs = [x for x in (f["sources"] + "|" + f.get("audit_sources", "")).split("|") if x]
        if f["cas_status"] in VERIFIED_CAS and len(srcs) < 2:
            raise SystemExit(f"{f['cas_status']} needs two sources: {f['inci_name']}")
        updates = {fmap[k]: f[k].strip() for k in fmap}
        if audit:
            updates["cas_sources"] = "|".join(dict.fromkeys(srcs))
            if f.get("original_note", "").strip():
                updates["cas_note"] = (f["verification_notes"].strip() + " Earlier note: " + f["original_note"].strip()).strip()
        if f["ec_number"].strip():
            updates["ec_status"] = "source_verified" if f["cas_status"] in VERIFIED_CAS else "imported_unverified"
        elif audit and ing["ec_number"]:
            updates["ec_status"] = "unresolved"
        for field, new in updates.items():
            old = ing[field]
            if old == new:
                continue
            log.append({"id": f"CHG-{next_id:05d}", "date": f"{date[:4]}-{date[4:6]}-{date[6:]}" if "-" not in date else date,
                        "record_id": ing["id"], "field": field, "old_value": old, "new_value": new,
                        "reason": reason,
                        "source_ids": updates.get("cas_sources", f["sources"])})
            ing[field] = new
            next_id += 1
            added += 1
    write_csv(CURATED / "change_log.csv", log, CHANGE_FIELDS)
    print(f"Appended {added} change-log entries from {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1])))
