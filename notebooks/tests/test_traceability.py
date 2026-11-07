"""Tests of a pinned historical workbook view, not validation of its claims."""
from pathlib import Path
import json
import re
import shutil
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'notebooks'))
from workbench.traceability import *

class TraceabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.book=read_workbook(ROOT)

    def test_all_sheets_and_table_counts(self):
        self.assertEqual(self.book.sheets,('ReadMe','DecisionTrace','Artifacts','DisclosureRules','OpenQuestions','AI Disclosure Guidance'))
        self.assertEqual([len(t.rows) for t in self.book.tables.values()],[33,50,26,12,12,5,5])

    def test_template_excluded(self):
        t=self.book.tables['RVDecisionTraceTable']
        self.assertEqual([r['Trace ID'] for _,r in t.records()],[f'RV-TR-{i:03}' for i in range(1,51)])
        self.assertIn('not an event',self.book.cells['DecisionTrace']['A57']['value'])
        self.assertEqual(t.row('RV-TR-050')[0],55)

    def test_keys_and_blanks(self):
        for t in self.book.tables.values():
            keys=[r[0] for r in t.rows]
            self.assertEqual(len(keys),len(set(keys)))
        self.assertIsNone(self.book.tables['RVArtifactRegisterTable'].row('RV-A-026')[1]['First delivered UTC'])
        self.assertIn('[blank source cell]',record_view(self.book.tables['RVArtifactRegisterTable'],'RV-A-026').text)

    def test_full_record_and_source_cells(self):
        t=self.book.tables['RVDecisionTraceTable'];view=record_view(t,'RV-TR-050')
        self.assertIn("'DecisionTrace'!O55",view.text)
        for value in t.row('RV-TR-050')[1].values():
            if value is not None:self.assertIn(str(value),view.text)

    def test_literal_filter_and_missing_keys(self):
        t=self.book.tables['RVDecisionTraceTable']
        self.assertEqual(t.records('tEmPoRaL'),t.records('Temporal'))
        self.assertEqual(t.records('xyz-no-such-source'),[])
        with self.assertRaises(TraceabilityError):t.row('RV-TR-999')
        with self.assertRaises(TraceabilityError):select_view(t,['imaginary field'])

    def test_dates_preserve_raw(self):
        c=self.book.cells['DecisionTrace']['B6']
        self.assertEqual(c['value'],'2026-10-31 17:47:19')
        self.assertTrue(float(c['raw'])>40000)
        self.assertEqual(self.book.cells['DecisionTrace']['B48']['type'],'d')

    def test_changed_digest_stops(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/WORKBOOK;p.parent.mkdir(parents=True)
            p.write_bytes((ROOT/WORKBOOK).read_bytes()+b'changed')
            with self.assertRaises(TraceabilityError):read_workbook(Path(tmp))

    def test_notebook_links_and_outputs(self):
        n=json.loads((ROOT/'notebooks/02_traceability_and_disclosure.ipynb').read_text())
        for c in n['cells']:
            for link in re.findall(r'\]\(([^)]+)\)',''.join(c['source'])):
                if not link.startswith(('https:','#')):self.assertTrue((ROOT/'notebooks'/link.split('#')[0]).exists(),link)
        code=[c for c in n['cells'] if c['cell_type']=='code']
        self.assertEqual(len(code),10)
        self.assertEqual([c['execution_count'] for c in code],list(range(1,11)))
        self.assertFalse(any(o['output_type']=='error' for c in code for o in c['outputs']))

if __name__=='__main__':unittest.main()
