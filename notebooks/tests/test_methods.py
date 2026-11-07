"""Source-byte and notebook-view tests; no historical code is executed."""
from pathlib import Path
import ast
import json
import re
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'notebooks'))
from workbench.methods import *

class MethodsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.record=read_methods(ROOT)

    def test_freeze_and_manifest_bindings(self):
        self.assertEqual(len(self.record.receipts),12)
        for name,digest in self.record.receipts:self.assertEqual(sha256(self.record.members[name]).hexdigest(),digest)
        self.assertEqual(self.record.manifest['freeze_file_sha256'],sha256(self.record.members[FREEZE]).hexdigest())
        self.assertIn('Written after collection',self.record.manifest['record_basis'])

    def test_case_inventory(self):
        for path in ('direct','framework'):
            for s in range(6):
                rows=self.record.inventory(path,f'S{s}');names=[x[0] for x in rows]
                self.assertTrue(any(n.endswith('/record.json') for n in names))
                self.assertTrue(any(n.endswith('/sink.sqlite') for n in names))
                if path=='framework':self.assertTrue(any(n.endswith('/checkpoint.sqlite') for n in names))
                for n,b,h in rows:self.assertEqual(len(self.record.members[n]),b)
        with self.assertRaises(EvidenceError):self.record.inventory('other','S4')
        with self.assertRaises(EvidenceError):self.record.inventory('direct','S9')

    def test_saved_verdict_units(self):
        checks=json.loads(self.record.text('measured01/checker.json'))
        self.assertEqual(len(checks),12)
        self.assertTrue(all(set(c['verdicts'])=={'caller_knowledge','sink_effect','framework_path','completeness'} for c in checks))
        self.assertEqual(len(set(c['record'] for c in checks)),12)

    def test_excerpt_exact_and_boundaries(self):
        text=self.record.text('CORRECTIONS.md')
        self.assertIn('\n'.join(text.splitlines()[:5]),archive_excerpt(self.record,'CORRECTIONS.md',1,5).text)
        self.assertIn('No measured study collection has occurred',text)
        with self.assertRaises(EvidenceError):archive_excerpt(self.record,'CORRECTIONS.md',0,4)
        with self.assertRaises(EvidenceError):self.record.text('missing')

    def test_digest_change_stops(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/ARCHIVE;p.parent.mkdir(parents=True)
            p.write_bytes((ROOT/ARCHIVE).read_bytes()+b'changed')
            with self.assertRaises(EvidenceError):read_methods(Path(d))

    def test_no_archived_code_execution(self):
        source=(ROOT/'notebooks/workbench/methods.py').read_text()
        node=ast.parse(source)
        for call in (x for x in ast.walk(node) if isinstance(x,ast.Call)):
            if isinstance(call.func,ast.Name):self.assertNotIn(call.func.id,('exec','eval','compile','__import__'))
            if isinstance(call.func,ast.Attribute):self.assertNotIn(call.func.attr,('extract','extractall','Popen','system','connect'))

    def test_notebook_links_outputs_and_limits(self):
        n=json.loads((ROOT/'notebooks/03_methods_and_reproduction.ipynb').read_text());alltext='\n'.join(''.join(c['source']) for c in n['cells'])
        for link in re.findall(r'\]\(([^)]+)\)',alltext):
            if not link.startswith(('https:','#')):self.assertTrue((ROOT/'notebooks'/link.split('#')[0]).exists(),link)
        code=[c for c in n['cells'] if c['cell_type']=='code']
        self.assertEqual(len(code),5)
        self.assertEqual([c['execution_count'] for c in code],list(range(1,6)))
        self.assertTrue(all(c['outputs'] for c in code))
        for phrase in ('not a new checker run','not independently rechecking','not a random population sample','not executable cells','not rerun'):
            self.assertIn(phrase,alltext)

if __name__=='__main__':unittest.main()
