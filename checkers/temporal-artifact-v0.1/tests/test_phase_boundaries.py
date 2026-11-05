"""Review regressions for phase isolation, late commits, and bounded parsing."""
import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from temporal_checker.artifacts import Bundle, VERSION
from temporal_checker.fixtures import create_fixture, reseal, write_json, write_jsonl
from temporal_checker.engine import check_bundle

class PhaseBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
    def fixture(self,cell='M1'): create_fixture(self.root,cell)
    def mutate_json(self,path,func):
        p=self.root/path;data=json.loads(p.read_text());func(data);write_json(p,data)
    def report(self):
        reseal(self.root);r=check_bundle(self.root,include_views=False)
        self.assertEqual(r['requirements']['artifact.integrity']['status'],'satisfied');return r
    def test_huge_history_boundary_bounded(self):
        self.fixture()
        def mutate(n):
            n['coverage']['final_event_id']='9223372036854775807';n['coverage']['closing_boundary_event_id']='9223372036854775807';n['coverage']['pages'][0]['last_event_id']='9223372036854775807'
        self.mutate_json('P1/native_history.json',mutate)
        self.assertEqual(self.report()['phases']['P1']['requirements']['native.coverage']['status'],'unobserved')
    def test_huge_producer_boundary_bounded(self):
        self.fixture();self.mutate_json('P1/capture.json',lambda c:c['producer_watermarks'].update(worker=9223372036854775807))
        self.assertEqual(self.report()['phases']['P1']['requirements']['capture.boundaries']['status'],'unobserved')
    def test_bad_p2_does_not_rewrite_p1(self):
        self.fixture();p=self.root/'producer_events.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()]
        next(e for e in rows if e['phase']=='P2')['payload']['unknown']='bad';write_jsonl(p,rows)
        r=self.report();self.assertEqual(r['phases']['P1']['requirements']['schedule.causal']['status'],'satisfied');self.assertEqual(r['phases']['P2']['requirements']['phase.events']['status'],'unsatisfied')
    def test_unknown_launch_ref_rejected(self):
        self.fixture();self.mutate_json('observed_binding.json',lambda b:b.update(launch_ref='native:999'))
        self.assertEqual(self.report()['requirements']['schema.binding']['status'],'unsatisfied')
    def test_bad_mapping_nested_type_rejected(self):
        self.fixture();self.mutate_json('case.json',lambda c:c.update(mapping={'schema_version':VERSION,'kind':'synthetic_test_oracle','tuples':[]}))
        self.assertEqual(self.report()['requirements']['schema.case']['status'],'unsatisfied')
    def test_sink_kind_cannot_override_cancel_submission(self):
        self.fixture('K1');p=self.root/'producer_events.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()]
        e=next(x for x in rows if x['kind']=='bridge_response');e.update(kind='cancel_submitted',payload={'call_id':'unexpected'})
        write_jsonl(p,rows);r=self.report()
        self.assertEqual(r['phases']['P1']['reference']['cancellation_request']['value'],'unresolved');self.assertEqual(r['phases']['P1']['reference']['effect_order_vs_request']['value'],'unresolved')
    def test_native_terminal_requires_capture_causal_link(self):
        self.fixture();p=self.root/'producer_events.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()]
        for e in rows:
            if e['kind']=='capture_start':e['parents']=[x for x in e['parents'] if x!='native:4']
        write_jsonl(p,rows)
        self.assertEqual(self.report()['phases']['P1']['requirements']['capture.boundaries']['status'],'unobserved')
    def test_cleanup_late_commit_same_dispatch_investigated(self):
        self.fixture('M3')
        # Captured M3 denied its request. A later synthetic commit of that same
        # request contradicts the claim it was resolved with no work outstanding.
        p=self.root/'P3/sink.sqlite';p.parent.mkdir();p.write_bytes((self.root/'P1/sink.sqlite').read_bytes())
        with sqlite3.connect(p) as db:
            db.execute('INSERT INTO events(kind,data) VALUES(?,?)',('receipt',json.dumps({'actor':'childC','request':dict(id='execute',op='execute',claim='childC',grant='child-1',scope='summary:task1',ticket='ticket-1',payload='inert summary')})))
            seq=db.execute('INSERT INTO events(kind,data) VALUES(?,?)',('effect',json.dumps({'request_id':'execute','result':dict(outcome='effect',effect_key='summary:task1',payload='inert summary',root='rootR',epoch=7)}))).lastrowid
            db.execute('INSERT INTO effects VALUES(?,?,?,?,?)',(seq,'summary:task1','inert summary','rootR',7))
        registry=json.loads((self.root/'registry.json').read_text());registry['artifacts'].append(dict(artifact_id='sink-p3',path='P3/sink.sqlite',role='sink',phase='P3',schema_version=VERSION,byte_length=0,sha256='0'*64,producer='synthetic_fixture'));write_json(self.root/'registry.json',registry)
        r=self.report();self.assertEqual(r['phases']['P1']['requirements']['capture.late_contradiction']['status'],'unsatisfied');self.assertEqual(r['phases']['P1']['reference']['effect_existence']['value'],'unresolved')
    def test_missing_phase_keeps_planned_opportunities(self):
        self.fixture();registry=json.loads((self.root/'registry.json').read_text())
        remove=[e for e in registry['artifacts'] if e['phase']=='P2']
        for e in remove:(self.root/e['path']).unlink()
        registry['artifacts']=[e for e in registry['artifacts'] if e not in remove];write_json(self.root/'registry.json',registry)
        r=check_bundle(self.root)
        self.assertEqual(r['views']['P2']['B']['scores']['planned_opportunities'],10)
        self.assertEqual(r['views']['P2']['B']['scores']['evaluated_opportunities'],0)
        self.assertEqual(r['views']['P2']['B']['scores']['counts']['malformed_or_omitted'],0)

if __name__=='__main__':unittest.main()

class AdditionalReviewTests(unittest.TestCase):
    setUp=PhaseBoundaryTests.setUp
    fixture=PhaseBoundaryTests.fixture
    mutate_json=PhaseBoundaryTests.mutate_json
    report=PhaseBoundaryTests.report
    def test_reserved_producer_namespace_rejected(self):
        self.fixture('C1');p=self.root/'producer_events.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()]
        target=next(e for e in rows if e['kind']=='finally_point');old=target['record_id'];target['record_id']='sink:5'
        for e in rows:e['parents']=['sink:5' if x==old else x for x in e['parents']]
        write_jsonl(p,rows);r=self.report();self.assertEqual(r['requirements']['schema.events']['status'],'unsatisfied')
    def test_committed_effect_survives_lost_bridge_response(self):
        self.fixture();p=self.root/'producer_events.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()]
        target=next(e for e in rows if e['kind']=='bridge_response');target.update(kind='transport_error',payload={'request_id':'execute','uncertain':True})
        write_jsonl(p,rows);r=self.report();self.assertEqual(r['phases']['P1']['reference']['effect_existence']['value'],'present');self.assertTrue(r['phases']['P1']['observed']['transport_uncertain'])
    def test_absent_revocation_command_is_schedule_defect(self):
        self.fixture('M3');p=self.root/'producer_events.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()]
        target=next(e for e in rows if e['kind']=='revocation_invoked');target.update(kind='diagnostic',payload={'namespace':'test','data':{}})
        write_jsonl(p,rows);r=self.report();self.assertEqual(r['phases']['P1']['requirements']['schedule.commands']['status'],'unsatisfied')
    def test_invented_success_cannot_override_wrong_outcome(self):
        self.fixture('M3');p=self.root/'producer_events.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()]
        target=next(e for e in rows if e['kind']=='bridge_response');target.update(kind='diagnostic',payload={'namespace':'runner','data':{'ok':True,'exit_code':0}})
        write_jsonl(p,rows)
        with sqlite3.connect(self.root/'P1/sink.sqlite') as db:db.execute('UPDATE events SET data=? WHERE kind=?',(json.dumps({'request_id':'execute','result':{'outcome':'denied','reason':'invalid_ticket'}}),'denied'))
        r=self.report();self.assertEqual(r['phases']['P1']['requirements']['outcome.sink_expected']['status'],'unsatisfied');self.assertFalse(r['native_qualification'])

class FinalBoundaryTests(unittest.TestCase):
    setUp=PhaseBoundaryTests.setUp
    fixture=PhaseBoundaryTests.fixture
    mutate_json=PhaseBoundaryTests.mutate_json
    report=PhaseBoundaryTests.report
    def test_missing_native_keeps_worker_support(self):
        from temporal_checker.fixtures import refresh_views
        self.fixture();self.mutate_json('case.json',lambda c:c['view_permissions'].update(native=False));reseal(self.root);refresh_views(self.root);r=check_bundle(self.root)
        self.assertEqual(r['views']['P1']['B']['reference']['activity_execution']['value'],'worker_invocation_settled')
        row=next(x for x in r['views']['P1']['B']['scores']['opportunities'] if x['field']=='activity_execution');self.assertEqual(row['category'],'correct_determinate')
    def test_wrong_denial_preserves_bounded_absence(self):
        self.fixture('M3')
        with sqlite3.connect(self.root/'P1/sink.sqlite') as db:db.execute('UPDATE events SET data=? WHERE kind=?',(json.dumps({'request_id':'execute','result':{'outcome':'denied','reason':'invalid_ticket'}}),'denied'))
        # Keep observed bridge result consistent with the adverse committed denial.
        p=self.root/'producer_events.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()]
        for e in rows:
            if e['kind']=='bridge_response':e['payload']['result']['reason']='invalid_ticket'
        write_jsonl(p,rows);r=self.report();self.assertEqual(r['phases']['P1']['reference']['effect_existence']['value'],'absent_with_complete_bounded_evidence');self.assertEqual(r['phases']['P1']['requirements']['outcome.sink_expected']['status'],'unsatisfied')
    def test_nested_envelope_payload_rejected(self):
        self.fixture();p=self.root/'producer_events.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()]
        e=next(x for x in rows if x['kind']=='worker_settled');e['payload']['details']['envelope']={'fence':'confirmed'};write_jsonl(p,rows)
        r=self.report();self.assertEqual(r['requirements']['schema.events']['status'],'unsatisfied')
    def test_numeric_capture_identity_fails_without_crash(self):
        self.fixture();self.mutate_json('P1/capture.json',lambda c:c.update(cut_id=123));reseal(self.root);r=check_bundle(self.root)
        self.assertEqual(r['phases']['P1']['requirements']['capture.boundaries']['status'],'unobserved');self.assertEqual(r['views']['P1']['B']['scores']['evaluated_opportunities'],0)
    def test_bad_table_boundaries_type_fails(self):
        self.fixture();self.mutate_json('P1/capture.json',lambda c:c['sink_transaction'].update(table_boundaries=['authority','grants','tickets','events','effects']))
        self.assertEqual(self.report()['phases']['P1']['requirements']['capture.boundaries']['status'],'unobserved')
