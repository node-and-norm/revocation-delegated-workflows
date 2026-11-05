"""Independent black-box synthetic regression tests; no native/runtime imports."""
import json
import sqlite3
import shutil
import tempfile
import unittest
from pathlib import Path
from temporal_checker.artifacts import Bundle, VERSION, loads
from temporal_checker.engine import check_bundle
from temporal_checker.fixtures import create_fixture, reseal, write_jsonl, seal, refresh_views

class IndependentReview(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
    def tearDown(self): self.tmp.cleanup()
    def make(self,cell='M1'): create_fixture(self.root,cell)
    def edit(self,path,key,value):
        p=self.root/path;obj=json.loads(p.read_text());obj[key]=value;p.write_text(json.dumps(obj))
        reseal(self.root)
    def events(self): return [json.loads(s) for s in (self.root/'producer_events.jsonl').read_text().splitlines()]
    def save_events(self,events):
        write_jsonl(self.root/'producer_events.jsonl',events);reseal(self.root)
    def report(self):
        r=check_bundle(self.root,include_views=False)
        self.assertEqual(r['requirements']['artifact.integrity']['status'],'satisfied')
        return r
    def test_nonobject_registry_fails_closed(self):
        (self.root/'registry.json').write_text(json.dumps({'schema_version':VERSION,'artifacts':[None]}))
        self.assertTrue(Bundle(self.root).errors)
    def test_numeric_overflow_rejected(self):
        with self.assertRaises(ValueError): loads('{"deadline":1e309}')
    def test_mapping_tuple_shape_fails_closed(self):
        self.make();self.edit('case.json','mapping',{'schema_version':VERSION,'kind':'synthetic_test_oracle','tuples':[]})
        r=self.report();self.assertEqual(r['requirements']['schema.case']['status'],'unsatisfied')
    def test_undefined_launch_reference_rejected(self):
        self.make();self.edit('observed_binding.json','launch_ref','native:999999')
        r=self.report();self.assertNotEqual(r['requirements']['schema.binding']['status'],'satisfied')
    def test_undefined_start_reference_rejected(self):
        self.make();self.edit('observed_binding.json','start_ref','does-not-exist')
        r=self.report();self.assertNotEqual(r['requirements']['schema.binding']['status'],'satisfied')
    def test_wrong_gateway_pin_rejected(self):
        self.make();p=self.root/'case.json';c=json.loads(p.read_text());c['pins']['gateway_sha256']='not-a-sha';p.write_text(json.dumps(c));reseal(self.root)
        r=self.report();self.assertNotEqual(r['requirements']['schema.case']['status'],'satisfied')
    def test_a_b_different_bytes_not_equal(self):
        self.make();p=self.root/'views/P1/B/identity.json';p.write_text(json.dumps(json.loads(p.read_text()),separators=(',',':')));reseal(self.root)
        r=check_bundle(self.root)
        self.assertEqual(r['views']['P1']['paired_underlying_bytes']['status'],'unsatisfied')
    def test_cancellation_observation_call_id_must_match(self):
        self.make();ev=self.events()
        for e in ev:
            if e['kind']=='cancellation_observed':e['payload']['call_id']='wrong-call'
        self.save_events(ev);r=self.report()
        self.assertNotEqual(r['phases']['P1']['requirements']['schedule.causal']['status'],'satisfied')
    def test_c4_ack_request_must_match(self):
        self.make('C4');ev=self.events()
        for e in ev:
            if e['kind']=='effect_ack':e['payload']['request_id']='unrelated'
        self.save_events(ev);r=self.report()
        self.assertNotEqual(r['phases']['P1']['requirements']['schedule.causal']['status'],'satisfied')
    def test_c1_extra_dispatch_is_adverse_without_effect(self):
        self.make('C1');ev=self.events();e=dict(ev[0]);e.update(record_id='extra-1',producer_id='extra',sequence=1,kind='dispatch_started',payload={'request_id':'extra'},parents=[]);ev.append(e);self.save_events(ev);r=self.report()
        self.assertEqual(r['phases']['P1']['requirements']['outcome.cardinality']['status'],'unsatisfied')
        self.assertTrue(r['attempt_retained'])
    def test_c4_extra_dispatch_is_adverse_with_one_effect(self):
        self.make('C4');ev=self.events();e=dict(ev[0]);e.update(record_id='extra-1',producer_id='extra',sequence=1,kind='dispatch_started',payload={'request_id':'extra'},parents=[]);ev.append(e);self.save_events(ev);r=self.report()
        self.assertEqual(r['phases']['P1']['requirements']['outcome.cardinality']['status'],'unsatisfied')
        self.assertEqual(r['phases']['P1']['observed']['sink']['effect_rows'],1)
    def test_k1_submission_not_no_request(self):
        self.make('K1');ev=self.events()
        for e in ev:
            if e['kind']=='bridge_response':e['kind']='cancel_submitted';e['payload']={'call_id':'unexpected-cancel'}
        self.save_events(ev);r=self.report()
        self.assertNotEqual(r['phases']['P1']['reference']['cancellation_request']['value'],'not_requested')
        self.assertNotEqual(r['phases']['P1']['reference']['effect_order_vs_request']['value'],'no_request')
    def test_malformed_sink_denial_does_not_crash(self):
        self.make('K2')
        with sqlite3.connect(self.root/'P1/sink.sqlite') as db: db.execute("UPDATE events SET data='{' WHERE kind='denied'")
        reseal(self.root);r=self.report()
        self.assertEqual(r['phases']['P1']['requirements']['sink.primitives']['status'],'unsatisfied')
    def test_p2_unrelated_invalid_reference_does_not_erase_p1(self):
        self.make();before=self.report();ev=self.events()
        for e in ev:
            if e['phase']=='P2' and e['kind']=='capture_end':e['parents'].append('missing-p2-record')
        self.save_events(ev);after=self.report()
        self.assertEqual(after['phases']['P1']['reference'],before['phases']['P1']['reference'])
        self.assertEqual(after['phases']['P1']['capture_sufficient'],before['phases']['P1']['capture_sufficient'])
    def test_p2_unknown_payload_does_not_erase_p1(self):
        self.make();before=self.report();ev=self.events()
        for e in ev:
            if e['phase']=='P2' and e['kind']=='capture_end':e['payload']['unknown_semantic_field']=True
        self.save_events(ev);after=self.report()
        self.assertEqual(after['phases']['P1']['reference'],before['phases']['P1']['reference'])
        self.assertEqual(after['phases']['P1']['capture_sufficient'],before['phases']['P1']['capture_sufficient'])
    def late_sink_fixture(self,request_id):
        self.make();(self.root/'P3').mkdir();shutil.copy2(self.root/'P1/sink.sqlite',self.root/'P3/sink.sqlite')
        if request_id!='execute':
            with sqlite3.connect(self.root/'P3/sink.sqlite') as db:
                for seq,raw in db.execute('SELECT seq,data FROM events WHERE seq IN (6,7)').fetchall():
                    data=json.loads(raw)
                    if seq==6:data['request']['id']=request_id
                    else:data['request_id']=request_id
                    db.execute('UPDATE events SET data=? WHERE seq=?',(json.dumps(data),seq))
        for phase in ('P1','P2'):
            with sqlite3.connect(self.root/phase/'sink.sqlite') as db:
                db.execute('DELETE FROM effects');db.execute('DELETE FROM events WHERE seq>=6')
            p=self.root/phase/'capture.json';c=json.loads(p.read_text());c['sink_transaction']['event_boundary']=5;p.write_text(json.dumps(c))
        ev=self.events();dispatch=next(e['record_id'] for e in ev if e['kind']=='dispatch_started')
        for e in ev:
            if e['kind']=='bridge_response':e['kind']='transport_error';e['payload']={'request_id':'execute','uncertain':False};e['parents']=[dispatch]
        write_jsonl(self.root/'producer_events.jsonl',ev)
        registry=json.loads((self.root/'registry.json').read_text())
        entries=[(e['artifact_id'],e['path'],e['role'],e['phase']) for e in registry['artifacts']]
        entries.append(('sink-p3','P3/sink.sqlite','sink','P3'));seal(self.root,entries)
    def test_p3_same_dispatch_contradicts_certificate(self):
        self.late_sink_fixture('execute');r=self.report()
        for phase in ('P1','P2'):
            self.assertFalse(r['phases'][phase]['capture_sufficient'])
            self.assertEqual(r['phases'][phase]['requirements']['capture.late_contradiction']['status'],'unsatisfied')
            self.assertEqual(r['phases'][phase]['reference']['effect_existence']['value'],'unresolved')
    def test_p3_new_operation_does_not_falsify_earlier_cut(self):
        self.late_sink_fixture('independent-operation');r=self.report()
        for phase in ('P1','P2'):
            self.assertTrue(r['phases'][phase]['capture_sufficient'])
            self.assertEqual(r['phases'][phase]['requirements']['capture.late_contradiction']['status'],'satisfied')
    def test_uncertain_uncommitted_transport_prevents_absence(self):
        self.make('C1');ev=self.events()
        for e in ev:
            if e['kind']=='finally_point':e['kind']='transport_error';e['payload']={'request_id':'unknown-dispatch','uncertain':True}
        self.save_events(ev);r=self.report()
        self.assertFalse(r['phases']['P1']['capture_sufficient'])
        self.assertEqual(r['phases']['P1']['reference']['effect_existence']['value'],'unresolved')
    def test_reserved_graph_id_namespace_rejected(self):
        self.make('C1');ev=self.events();old=next(e['record_id'] for e in ev if e['kind']=='finally_point')
        for e in ev:
            if e['record_id']==old:e['record_id']='sink:5'
            e['parents']=['sink:5' if x==old else x for x in e['parents']]
        self.save_events(ev);r=self.report()
        self.assertNotEqual(r['requirements']['schema.events']['status'],'satisfied')
    def test_visible_worker_proof_survives_hidden_native(self):
        self.make();p=self.root/'case.json';c=json.loads(p.read_text());c['view_permissions']['native']=False;p.write_text(json.dumps(c));reseal(self.root);refresh_views(self.root)
        source=json.loads((self.root/'views/P1/B/source_map.json').read_text())
        worker=[json.loads(x) for x in (self.root/'views/P1/B/worker_events.jsonl').read_text().splitlines()]
        w=next(x for x in worker if x['kind']=='worker_settled')
        ref=next(x['raw_ref'] for x in source['records'] if x['raw_ref']['record_id']==w['record_id'])
        p=self.root/'outputs/P1-B.json';out=json.loads(p.read_text());claim=next(x for x in out['assertions'] if x['field']=='activity_execution');claim['value']='worker_invocation_settled';claim['evidence_refs']=[ref];p.write_text(json.dumps(out));reseal(self.root)
        r=check_bundle(self.root);score=next(x for x in r['views']['P1']['B']['scores']['opportunities'] if x['field']=='activity_execution')
        self.assertEqual(score['category'],'correct_determinate')
    def test_wrong_denial_preserves_complete_zero_effect_fact(self):
        self.make('M3')
        for phase in ('P1','P2'):
            with sqlite3.connect(self.root/phase/'sink.sqlite') as db:
                seq,raw=db.execute("SELECT seq,data FROM events WHERE kind='denied'").fetchone();data=json.loads(raw);data['result']['reason']='invalid_ticket';db.execute('UPDATE events SET data=? WHERE seq=?',(json.dumps(data),seq))
        ev=self.events()
        for e in ev:
            if e['kind']=='bridge_response':e['payload']['result']['reason']='invalid_ticket'
        self.save_events(ev);r=self.report();x=r['phases']['P1']
        self.assertTrue(x['capture_sufficient'])
        self.assertEqual(x['reference']['effect_existence']['value'],'absent_with_complete_bounded_evidence')
        self.assertEqual(x['requirements']['outcome.sink_expected']['status'],'unsatisfied')
    def test_native_payload_duplicate_envelope_rejected(self):
        self.make();p=self.root/'P1/native_history.json';n=json.loads(p.read_text());n['events'][-1]['attributes']['result']['envelope']={'effect_existence':'absent_with_complete_bounded_evidence'};p.write_text(json.dumps(n));reseal(self.root);r=self.report()
        self.assertEqual(r['phases']['P1']['requirements']['native.schema']['status'],'unsatisfied')
    def test_worker_payload_duplicate_envelope_rejected(self):
        self.make();ev=self.events()
        for e in ev:
            if e['kind']=='worker_settled':e['payload']['details']['envelope']={'effect_existence':'present'}
        self.save_events(ev);r=self.report()
        self.assertEqual(r['phases']['P1']['requirements']['phase.events']['status'],'unsatisfied')
    def test_huge_native_boundary_is_bounded(self):
        self.make();p=self.root/'P1/native_history.json';n=json.loads(p.read_text());n['coverage']['final_event_id']='9223372036854775807';n['coverage']['closing_boundary_event_id']='9223372036854775807';n['coverage']['pages'][0]['last_event_id']='9223372036854775807';p.write_text(json.dumps(n));reseal(self.root);r=self.report()
        self.assertEqual(r['phases']['P1']['requirements']['native.coverage']['status'],'unobserved')
    def test_resolution_must_follow_dispatch(self):
        self.late_sink_fixture('independent-operation');ev=self.events()
        for e in ev:
            if e['kind']=='transport_error':e['sequence']=1;e['parents']=[]
            elif e['kind']=='dispatch_intended':e['sequence']=2
            elif e['kind']=='dispatch_started':e['sequence']=3
        self.save_events(ev);r=self.report()
        self.assertFalse(r['phases']['P1']['capture_sufficient'])
        self.assertEqual(r['phases']['P1']['reference']['effect_existence']['value'],'unresolved')
    def test_purely_synthetic_never_qualifies_native(self):
        self.make();r=self.report()
        self.assertFalse(r['native_qualification'])
        self.assertNotEqual(r['qualification_acceptance']['status'],'satisfied')

if __name__=='__main__': unittest.main(verbosity=2)
