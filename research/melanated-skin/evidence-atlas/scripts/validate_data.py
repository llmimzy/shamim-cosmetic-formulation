#!/usr/bin/env python3
"""Validate reference integrity and schema; stdlib only."""
from pathlib import Path
import csv
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / 'data' / 'studies.csv'
INDEX = ROOT / 'data' / 'ingredient_index.csv'
REQUIRED = ('id','year','title','pmid','ingredients','category','comparison','finding','limitations','source_url','status','topic')
ALLOWED_COMPARISONS = {
 'Across population groups',
 'Formulations within darker phototypes',
 'Active treatments within III–IV phototypes',
 'Actives within darker phototypes',
 'Treatment vs vehicle within darker phototypes',
}

def validate():
    errors=[]
    with TABLE.open(newline='', encoding='utf-8') as fh:
        reader=csv.DictReader(fh)
        if not set(REQUIRED).issubset(reader.fieldnames or []):
            errors.append('Missing required CSV columns')
        studies=list(reader)
    ids=set();pmids=set()
    for row in studies:
        rid=row['id'];pmid=row['pmid']
        if not re.fullmatch(r'MS\d{3}', rid):errors.append(f'Invalid ID {rid}')
        if rid in ids:errors.append(f'Duplicate ID {rid}')
        if pmid in pmids:errors.append(f'Duplicate PMID {pmid}')
        if not re.fullmatch(r'\d{7,9}', pmid):errors.append(f'Invalid PMID in {rid}')
        if row['source_url'] != f'https://pubmed.ncbi.nlm.nih.gov/{pmid}/':errors.append(f'Mismatched PubMed link {rid}')
        if row['comparison'] not in ALLOWED_COMPARISONS:errors.append(f'Invalid comparison: {rid}')
        if not (ROOT/'studies'/f'{rid}.md').is_file():errors.append(f'Missing study evidence card: {rid}')
        for field in REQUIRED:
            if not row.get(field):errors.append(f'Missing {field} for {rid}')
        ids.add(rid);pmids.add(pmid)
    with INDEX.open(newline='',encoding='utf-8') as fh:
        ingredients=list(csv.DictReader(fh))
    for ing in ingredients:
        for ref in ing['study_ids'].split('|'):
            if ref not in ids:errors.append(f"Unknown study {ref} for ingredient {ing['ingredient']}")
    if len(studies) < 1:errors.append("No studies found")
    if errors:
        print('Data validation FAILED:',*errors,sep='\n - ')
        return 1
    print(f'Validated {len(studies)} studies, {len(ingredients)} ingredient-index entries, {len(ids)} cards.')
    return 0

if __name__ == '__main__':sys.exit(validate())
