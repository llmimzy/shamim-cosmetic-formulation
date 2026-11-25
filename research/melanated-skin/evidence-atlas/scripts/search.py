#!/usr/bin/env python3
"""Simple queryable evidence index; no external dependencies."""
from pathlib import Path
import argparse,csv

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description='Search the melanated-skin evidence atlas')
p.add_argument('--ingredient',default='',help='Case-insensitive ingredient keyword')
p.add_argument('--topic',default='',help='Case-insensitive topic filter')
p.add_argument('--comparison',default='',help='Case-insensitive comparison type')
p.add_argument('--full',action='store_true',help='Include limitations and complete finding')
a=p.parse_args()
with (ROOT/'data/studies.csv').open(newline='',encoding='utf-8') as file:
 rows=list(csv.DictReader(file))
for r in rows:
 if a.ingredient.lower() not in r['ingredients'].lower():continue
 if a.topic.lower() not in r['topic'].lower():continue
 if a.comparison.lower() not in r['comparison'].lower():continue
 print(f"{r['id']} | {r['year']} | {r['title']}\n  {r['comparison']} | {r['source_url']}")
 if a.full: print(f"  Finding: {r['finding']}\n  Limitations: {r['limitations']}")
