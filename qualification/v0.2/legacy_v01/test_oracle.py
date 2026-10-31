"""Hand-derived semantic controls; none call enforcement to derive expected labels."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import harness
from oracle import assess


def fixture(case='C1', outcome='effect'):
    kinds = ['admission', 'prepared', 'revocation', 'attempt', outcome, 'ack']
    if case == 'C4': kinds = ['admission', 'prepared', 'attempt', 'effect', 'revocation', 'ack']
    if case == 'C0': kinds = ['admission', 'prepared', 'attempt', 'effect', 'ack']
    data = {'admission': {'root':'rootR','epoch':7,'allowed':True}, 'prepared': {'effect_key':'summary:task1','payload':'inert summary'}, 'revocation': {'root':'rootR','withdrawn_epoch':7,'new_epoch':8}, 'attempt': {'attempt':1}, 'effect': {'attempt':1}, 'denied': {'attempt':1}, 'ack': {'attempt':1,'outcome':outcome}}
    events = [{'seq':i,'kind':k,'data':copy.deepcopy(data[k])} for i,k in enumerate(kinds,1)]
    effects = [{'event_seq':e['seq'],'effect_key':'summary:task1','payload':'inert summary','root':'rootR','epoch':7} for e in events if e['kind']=='effect']
    return {'case':case, 'events':events, 'effects':effects, 'authority': {'root':'rootR','epoch':7 if case=='C0' else 8,'active':1 if case=='C0' else 0}}

class OracleTests(unittest.TestCase):
    def test_positive_seeded_violation(self):
        result = assess(fixture())
        self.assertEqual(result['label'], 'VIOLATION')
        self.assertEqual(result['post_fence_effect_sequences'], [5])
    def test_denial_has_no_effect(self):
        self.assertEqual(assess(fixture(outcome='denied'))['label'], 'NO_VIOLATION')
    def test_positive_liveness(self):
        result = assess(fixture('C0'))
        self.assertEqual((result['label'],result['effects']), ('NO_VIOLATION',1))
    def test_late_ack_is_not_effect(self):
        self.assertEqual(assess(fixture('C4'))['label'], 'NO_VIOLATION')
    def test_missing_event_semantic_even_renumbered(self):
        t = fixture(outcome='denied'); t['events'].pop()
        self.assertEqual(assess(t)['label'], 'INVALID')
    def test_duplicate_event(self):
        t = fixture(); t['events'].append(copy.deepcopy(t['events'][-1])); t['events'][-1]['seq']=7
        self.assertEqual(assess(t)['label'], 'INVALID')
    def test_reordered_fence(self):
        t=fixture(); t['events'][1],t['events'][2]=t['events'][2],t['events'][1]
        for i,e in enumerate(t['events'],1):e['seq']=i
        self.assertEqual(assess(t)['label'], 'INVALID')
    def test_removed_sink_event(self):
        t=fixture(); t['events'].pop(4)
        self.assertEqual(assess(t)['label'], 'INVALID')
    def test_unlogged_sink_row(self):
        t=fixture(outcome='denied'); t['effects']=fixture()['effects']
        self.assertEqual(assess(t)['label'], 'INVALID')
    def test_wrong_payload(self):
        t=fixture(); t['effects'][0]['payload']='other'
        self.assertEqual(assess(t)['label'], 'INVALID')
    def test_missing_fence(self):
        t=fixture(); t['events'].pop(2)
        self.assertEqual(assess(t)['label'], 'INVALID')
    def test_duplicate_without_effect(self):
        t=fixture(outcome='denied'); t['events'][4]['kind']='duplicate'; t['events'][5]['data']['outcome']='duplicate'
        self.assertEqual(assess(t)['label'], 'INVALID')
    def test_unknown_attempt_outcome(self):
        t=fixture(outcome='denied'); t['events'].append({'seq':7,'kind':'denied','data':{'attempt':999}})
        self.assertEqual(assess(t)['label'], 'INVALID')
    def test_prepared_binding(self):
        t=fixture(); t['events'][1]['data']['payload']='wrong'; t['events'][1]['data']['effect_key']='wrong'
        self.assertEqual(assess(t)['label'], 'INVALID')
    def test_boolean_sequence(self):
        t=fixture(); t['events'][0]['seq']=True
        self.assertEqual(assess(t)['label'], 'INVALID')
    def test_malformed_schema(self):
        for t in (None, {}, {'events': None}, {'events':[{}]}):
            self.assertEqual(assess(t)['label'], 'INVALID')
    def test_timeout_never_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'failed_run'
            with patch('sys.argv',['harness.py','--output',str(target)]), patch('harness.run_case',side_effect=TimeoutError('synthetic observer timeout')):
                self.assertEqual(harness.main(),1)
            self.assertEqual(json.loads((target/'results.json').read_text())['status'],'INCOMPLETE')
    def test_observer_error_never_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'failed_run'
            with patch('sys.argv',['harness.py','--output',str(target)]), patch('harness.run_case',side_effect=RuntimeError('synthetic corrupt observer')):
                self.assertEqual(harness.main(),1)
            self.assertEqual(json.loads((target/'results.json').read_text())['status'],'INCOMPLETE')

if __name__=='__main__': unittest.main(verbosity=2)
