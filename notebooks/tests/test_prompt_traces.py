"""Exact preserved spans, not model quality or completeness tests."""
from pathlib import Path
import json
import re
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'notebooks'))
from workbench.prompt_traces import *

class PromptTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.archive=read_traces(ROOT)

    def test_coverage_and_phase_bindings(self):
        self.assertEqual(len(self.archive.snapshots),8)
        self.assertEqual(len(self.archive.calls()),16)
        for (case,phase),s in self.archive.snapshots.items():
            self.assertEqual(s.values['phase'],phase)
            self.assertIn(case,s.member)
        self.assertTrue(all(r['input'] and r['output'] for r in self.archive.calls()))

    def test_every_input_output_role_exact(self):
        for row in self.archive.calls():
            s=self.archive.snapshot(row['case'],row['phase'])
            call=s.values['models'][row['group']][row['invocation']]
            for field in ('role','input','output'):
                raw,lo,hi=s.fragment(row['pointer']+'/'+field)
                self.assertEqual(raw.encode(),s.raw[lo:hi])
                self.assertEqual(json.loads(raw),call[field])

    def test_empty_content_is_preserved(self):
        s=self.archive.snapshot(CASES[0],'pause')
        raw,_,_=s.fragment('/models/0/0/output')
        j=json.loads(raw);self.assertEqual(j['content'],'');self.assertEqual(len(j['tool_calls']),1)
        self.assertIn('"content": ""',raw)

    def test_unicode_escaping_and_pointer(self):
        text=' { "a/b": ["é", "escaped \\\" quote", {"~x": null}], "n": 1 } \n'
        spans=source_spans(text)
        self.assertEqual(json.loads(text[slice(*spans['/a~1b/0'])]),'é')
        self.assertEqual(text[slice(*spans['/a~1b/2/~0x'])],'null')
        self.assertEqual(json.loads(text[slice(*spans[''])]),json.loads(text))

    def test_duplicate_or_malformed_rejected(self):
        for text in ('{"x":1,"x":2}','[1,','{"a" 1}','{} trailing'):
            with self.assertRaises(EvidenceError):source_spans(text)

    def test_missing_not_reconstructed(self):
        with self.assertRaises(EvidenceError):self.archive.snapshot('direct_prior0_revoked0','pause')
        with self.assertRaises(EvidenceError):self.archive.snapshot(CASES[0],'pause').fragment('/missing')

    def test_changed_archive_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/ARCHIVE;p.parent.mkdir(parents=True);p.write_bytes((ROOT/ARCHIVE).read_bytes()+b'change')
            with self.assertRaises(EvidenceError):read_traces(Path(d))

    def test_preserved_stage_source(self):
        for stage in STAGES:self.assertTrue(stage_members(ROOT,stage))
        member='integration/v0.3/workflow.py';raw=stage_members(ROOT,'v0.3')[member]
        v=source_file_view(ROOT,'v0.3',member,1,49)
        self.assertIn(''.join(raw.decode().splitlines(keepends=True)[:49]),v.text)
        self.assertIn('StateScriptModel',v.text)
        with self.assertRaises(EvidenceError):source_file_view(ROOT,'v0.3','missing')

    def test_notebook_links_and_boundaries(self):
        n=json.loads((ROOT/'notebooks/04_exact_scripted_inputs_outputs.ipynb').read_text());text='\n'.join(''.join(c['source']) for c in n['cells'])
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if not link.startswith(('https:','#')):self.assertTrue((ROOT/'notebooks'/link.split('#')[0]).exists(),link)
        code=[c for c in n['cells'] if c['cell_type']=='code'];self.assertEqual(len(code),8)
        self.assertEqual([c['execution_count'] for c in code],list(range(1,9)))
        self.assertTrue(all(c['outputs'] for c in code))
        for phrase in ('not live LLM generations','not a claim that every action from day one','not proof of success','not reconstructed'):
            self.assertIn(phrase,text)

if __name__=='__main__':unittest.main()
