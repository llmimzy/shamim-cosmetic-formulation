"""Apply a dated reference-verification CSV to data/curated/studies.csv.

Each row in data/curated/research/reference_verification_*.csv records what was
confirmed for one study from at least two independent web sources. This script:
  * refuses rows whose PMID disagrees with the PMID already held for the study;
  * refuses 'identity_verified' rows with fewer than two evidence sources;
  * writes bibliographic and population fields, never inventing a value
    ('Not confirmed' becomes blank, with a note);
  * appends the abstract-level key result to the study notes once (idempotent).

Usage: python scripts/apply_references.py data/curated/research/reference_verification_2026-11-25.csv
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import CURATED, PHOTOTYPES, SOURCE_TYPES, STUDY_VERIFICATION, read_csv, write_csv  # noqa: E402
from build import STUDY_FIELDS  # noqa: E402

COPY = {"title": "title", "authors": "authors", "year": "year", "journal": "journal", "doi": "doi",
        "source_type": "source_type", "population": "population", "phototypes": "phototypes",
        "sample_size": "sample_size", "funding_or_conflicts": "funding_or_conflicts",
        "limitations": "limitations", "verification_status": "verification_status"}
UNKNOWN = {"not confirmed", "not extracted", ""}


def main(path):
    findings = read_csv(Path(path))
    verified_on = Path(path).stem.rsplit("_", 1)[-1]
    studies = read_csv(CURATED / "studies.csv")
    by_id = {s["id"]: s for s in studies}
    errors, changed = [], 0
    for f in findings:
        sid = f["study_id"]
        s = by_id.get(sid)
        if s is None:
            errors.append(f"{sid}: not in studies.csv"); continue
        if f["pmid"] and s["pmid"] and f["pmid"] != s["pmid"]:
            errors.append(f"{sid}: PMID {f['pmid']} != held {s['pmid']}"); continue
        srcs = [u for u in f["evidence_sources"].split("|") if u.strip()]
        if f["verification_status"] in {"identity_verified", "content_extracted"} and len(srcs) < 2:
            errors.append(f"{sid}: verified with fewer than two sources"); continue
        if f["source_type"] not in SOURCE_TYPES or f["phototypes"] not in PHOTOTYPES \
                or f["verification_status"] not in STUDY_VERIFICATION:
            errors.append(f"{sid}: vocabulary error"); continue
        before = dict(s)
        for src, dst in COPY.items():
            v = f[src].strip()
            s[dst] = "" if v.lower() in UNKNOWN else v
        s["sample_size"] = "" if not s["sample_size"] or not any(c.isdigit() for c in s["sample_size"]) else s["sample_size"]
        s["url"] = srcs[0] if srcs else s["url"]
        s["verified_on"] = verified_on
        notes = [n for n in s["notes"].split(" || ") if n and not n.startswith("source_type provisional")]
        key = f"Key result (abstract-level, {verified_on}): {f['key_result']}"
        if f["key_result"] and key not in notes:
            notes.append(key)
        if f["authors"].strip().lower() in UNKNOWN and "Author list not confirmed" not in " ".join(notes):
            notes.append("Author list not confirmed from accessible sources.")
        notes = [n for n in notes if not n.startswith("Verification sources:")]
        notes.append("Verification sources: " + " ; ".join(srcs))
        s["notes"] = " || ".join(notes)
        changed += s != before
    if errors:
        print("Refused:", *errors, sep="\n - ")
        return 1
    write_csv(CURATED / "studies.csv", studies, STUDY_FIELDS)
    print(f"Applied {len(findings)} verification rows; {changed} studies changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
