import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class EvidenceAtlasTests(unittest.TestCase):
    def test_validator(self):
        completed=subprocess.run([sys.executable,str(ROOT/'scripts/validate_data.py')],capture_output=True,text=True)
        self.assertEqual(completed.returncode,0,completed.stdout+completed.stderr)
    def test_site_json_fresh(self):
        with (ROOT/'data/studies.csv').open(newline='',encoding='utf-8') as f:
            csv_rows=list(csv.DictReader(f))
        json_rows=json.loads((ROOT/'docs/data/studies.json').read_text(encoding='utf-8'))
        self.assertEqual(csv_rows,json_rows,'Run python scripts/build_site_data.py')
    def test_population_categories(self):
        with (ROOT/'data/studies.csv').open(newline='',encoding='utf-8') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(sum(r['comparison']=='Across population groups' for r in rows),8)
        self.assertEqual(len(rows),13)

if __name__=='__main__':unittest.main()
