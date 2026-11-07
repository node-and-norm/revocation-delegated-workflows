"""Structure and evidence-view contract; not an experiment or renderer test."""
import json
from pathlib import Path
import re
import unittest
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "notebooks"))
from workbench.presentation import table

class StudyReportTests(unittest.TestCase):
    def setUp(self):
        self.nb = json.loads((ROOT / 'RESEARCH_STUDY.ipynb').read_text())
        self.text = '\n'.join(''.join(c['source']) for c in self.nb['cells'])

    def test_reading_sequence(self):
        for section in ('1 · What', '2 · How', '3 · Open', '4 · The', '5 · Challenge',
                        '6 · Where', '7 · The', '8 · When', '9 · Who', '10 · What',
                        '11 · How', '12 · Provenance'):
            self.assertIn(section, self.text)

    def test_limits_remain_explicit(self):
        for phrase in ('not a live LangGraph', 'not a reliability estimate',
                       'not independent human validation', 'not a signed remote certificate',
                       'Unobserved / uncalibrated', 'not an extra result'):
            self.assertIn(phrase, self.text)

    def test_relative_links_resolve(self):
        for link in re.findall(r'\]\(([^)]+)\)', self.text):
            if not link.startswith(('https:', '#')):
                self.assertTrue((ROOT / link.split('#')[0]).exists(), link)

    def test_saved_outputs_and_units(self):
        code = [c for c in self.nb['cells'] if c['cell_type'] == 'code']
        self.assertEqual(len(code), 7)
        self.assertEqual([c['execution_count'] for c in code], list(range(1,8)))
        self.assertTrue(all(c['outputs'] for c in code))
        self.assertFalse(any(o['output_type']=='error' for c in code for o in c['outputs']))
        text=json.dumps([c['outputs'] for c in code])
        self.assertIn('N/A', text)
        self.assertIn('S4', text)
        self.assertIn('S5', text)

    def test_paired_table_colors_and_text_fallback(self):
        view=table(['A'],[['B']])
        self.assertIn('color:#191820;background:#ffffff',view.html)
        self.assertIn('B',view.text)

if __name__ == '__main__': unittest.main()
