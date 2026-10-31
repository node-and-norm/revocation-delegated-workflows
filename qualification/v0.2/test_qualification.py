"""Finite oracle controls and real IPC negative controls; no models/network."""
import copy
import json
import multiprocessing as mp
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import harness
from gateway import gateway_main
from observer import observer_main
from oracle import assess


def hand_trace():
    # Hand-derived C1 seed: valid grant/admission, root withdrawn, effect afterward.
    requests=[('parentP',{'id':'delegate-1','op':'delegate','claim':'parentP','grant':'parent-0','scope':'summary:task1','child':'childC'}),('childC',{'id':'prepare-1','op':'prepare','claim':'childC','grant':'child-1','scope':'summary:task1'}),('controller',{'id':'revoke-1','op':'revoke','claim':'controller'}),('childC',{'id':'execute-1','op':'execute','claim':'childC','grant':'child-1','scope':'summary:task1','payload':'inert summary','ticket':'ticket-1'}),('childC',{'id':'ack-1','op':'ack','claim':'childC','for_request':'execute-1'})]
    results=[{'outcome':'grant','grant':'child-1','owner':'childC','root':'rootR','epoch':7,'scope':'summary:task1','parent_grant':'parent-0'},{'outcome':'admission','ticket':'ticket-1','grant':'child-1','root':'rootR','epoch':7,'scope':'summary:task1'},{'outcome':'revocation','root':'rootR','withdrawn_epoch':7,'new_epoch':8},{'outcome':'effect','effect_key':'summary:task1','payload':'inert summary','root':'rootR','epoch':7},{'outcome':'ack','for_request':'execute-1'}]
    events=[{'seq':1,'kind':'bootstrap','data':{'root':'rootR','epoch':7,'parent_grant':'parent-0','parent':'parentP','child':'childC','scope':'summary:task1'}}]
    workers={'parentP':[],'childC':[{'kind':'delivery_received','grant':'child-1','peer':'parentP'}]}
    for (actor,req),result in zip(requests,results):
        events.extend([{'seq':len(events)+1,'kind':'receipt','data':{'actor':actor,'request':req}},{'seq':len(events)+2,'kind':result['outcome'],'data':{'request_id':req['id'],'result':result}}])
        if actor!='controller':workers[actor].extend([{'kind':'intent','request':req},{'kind':'response','request_id':req['id'],'response':result}])
        if req['op']=='delegate':workers['parentP'].append({'kind':'delivery_sent','grant':'child-1','peer':'childC'})
    snapshot={'events':events,'authority':[{'root':'rootR','epoch':8,'active':0}],'grants':[{'token':'child-1','owner':'childC','root':'rootR','epoch':7,'scope':'summary:task1','can_delegate':0},{'token':'parent-0','owner':'parentP','root':'rootR','epoch':7,'scope':'summary:task1','can_delegate':1}],'tickets':[{'token':'ticket-1','grant_token':'child-1','owner':'childC','scope':'summary:task1'}],'effects':[{'event_seq':9,'effect_key':'summary:task1','payload':'inert summary','root':'rootR','epoch':7}]}
    return {'case':'C1','arm':'admission_only','snapshot':snapshot,'workers':workers}

class OracleTests(unittest.TestCase):
    def test_hand_derived_positive_violation(self):
        r=assess(hand_trace());self.assertEqual(r['label'],'VIOLATION');self.assertEqual(r['post_fence_effect_sequences'],[9])
    def test_same_trace_strong_arm_still_detected(self):
        t=hand_trace();t['arm']='commit_fenced';self.assertEqual(assess(t)['label'],'VIOLATION')
    def test_each_missing_event_invalid_even_renumbered(self):
        t=hand_trace()
        for i in range(len(t['snapshot']['events'])):
            x=copy.deepcopy(t);x['snapshot']['events'].pop(i)
            for j,e in enumerate(x['snapshot']['events'],1):e['seq']=j
            self.assertEqual(assess(x)['label'],'INVALID')
    def test_duplicate_event(self):
        t=hand_trace();t['snapshot']['events'].append(copy.deepcopy(t['snapshot']['events'][-1]));self.assertEqual(assess(t)['label'],'INVALID')
    def test_reordered_fence(self):
        t=hand_trace();e=t['snapshot']['events'];e[5],e[7]=e[7],e[5]
        for j,row in enumerate(e,1):row['seq']=j
        self.assertEqual(assess(t)['label'],'INVALID')
    def test_boolean_sequence(self):
        t=hand_trace();t['snapshot']['events'][0]['seq']=True;self.assertEqual(assess(t)['label'],'INVALID')
    def test_unknown_attempt(self):
        t=hand_trace();t['snapshot']['events'][7]['data']['request']['id']='execute-999';self.assertEqual(assess(t)['label'],'INVALID')
    def test_prepared_binding(self):
        t=hand_trace();t['snapshot']['events'][3]['data']['request']['scope']='wrong';self.assertEqual(assess(t)['label'],'INVALID')
    def test_duplicate_without_prior_effect(self):
        t=hand_trace();e=t['snapshot']['events'][8];e['kind']='duplicate';e['data']['result']={'outcome':'duplicate'};t['snapshot']['effects']=[];self.assertEqual(assess(t)['label'],'INVALID')
    def test_missing_worker_evidence(self):
        t=hand_trace();t['workers']['childC']=[];self.assertEqual(assess(t)['label'],'INVALID')
    def test_worker_response_conflict(self):
        t=copy.deepcopy(hand_trace());t['workers']['childC'][-1]['response']={'outcome':'different'};self.assertEqual(assess(t)['label'],'INVALID')
    def test_missing_sink_row(self):
        t=hand_trace();t['snapshot']['effects']=[];self.assertEqual(assess(t)['label'],'INVALID')
    def test_grant_epoch_bool(self):
        t=hand_trace();t['snapshot']['grants'][0]['epoch']=True;self.assertEqual(assess(t)['label'],'INVALID')
    def test_malformed_schema(self):
        for t in (None,{},[],{'case':'C1'}):self.assertEqual(assess(t)['label'],'INVALID')
    def test_timeout_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'run'
            with patch('sys.argv',['harness.py','--output',str(output)]),patch('harness.run_case',side_effect=TimeoutError('synthetic timeout')):
                self.assertEqual(harness.main(),1)
            self.assertEqual(json.loads((output/'results.json').read_text())['status'],'INCOMPLETE')

class IPCTests(unittest.TestCase):
    def test_unknown_grant_and_server_bound_caller(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx=mp.get_context('spawn');gc,gs=ctx.Pipe();pc,ps=ctx.Pipe();cc,cs=ctx.Pipe()
            p=ctx.Process(target=gateway_main,args=(Path(tmp)/'test.db','commit_fenced',gs,ps,cs));p.start()
            try:
                harness.recv(gc)
                r=harness.rpc(cc,{'id':'unknown','op':'prepare','claim':'childC','grant':'absent','scope':'summary:task1'})
                self.assertEqual(r,{'outcome':'denied','reason':'unknown_grant'})
                r=harness.rpc(cc,{'id':'forged','op':'delegate','claim':'parentP','grant':'parent-0','scope':'summary:task1','child':'childC'})
                self.assertEqual(r,{'outcome':'denied','reason':'caller_mismatch'})
                harness.rpc(gc,{'op':'stop'});p.join(10);self.assertEqual(p.exitcode,0)
            finally:
                if p.is_alive():p.terminate();p.join(10)
                for c in (gc,gs,pc,ps,cc,cs):c.close()
    def test_actual_observer_missing_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx=mp.get_context('spawn');a,b=ctx.Pipe();p=ctx.Process(target=observer_main,args=(Path(tmp)/'absent.db',b));p.start()
            try:
                self.assertTrue(a.poll(10));r=a.recv();self.assertFalse(r['ok']);self.assertIn('OperationalError',r['error']);p.join(10);self.assertEqual(p.exitcode,0)
            finally:
                if p.is_alive():p.terminate();p.join(10)
                a.close();b.close()


class TreatmentTests(unittest.TestCase):
    def test_preserved_reviewer_counterexamples(self):
        from oracle import qualify
        path=Path(__file__).parent/'review_counterexamples01.json'
        for name,row in json.loads(path.read_text()).items():
            self.assertFalse(qualify(row['trace'])['qualified'],name)
    def test_seeded_violation_not_hidden_by_treatment_check(self):
        from oracle import qualify
        t=hand_trace();self.assertTrue(qualify(t)['qualified'])
        t['arm']='commit_fenced';r=qualify(t)
        self.assertEqual(r['endpoint']['label'],'VIOLATION');self.assertFalse(r['qualified'])

if __name__=='__main__':unittest.main(verbosity=2)
