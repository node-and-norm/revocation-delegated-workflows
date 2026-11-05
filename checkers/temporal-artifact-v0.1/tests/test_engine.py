"""Rehashed semantic regressions. All data are synthetic, never native runs."""
import copy
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from temporal_checker.artifacts import ArtifactError, Bundle, VERSION, loads
from temporal_checker.fixtures import create_fixture, reseal, refresh_views, write_json, write_jsonl
from temporal_checker.engine import check_bundle
from temporal_checker.scoring import aggregate_reports


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
    def fixture(self,cell='M1',mode=None):
        return create_fixture(self.root,cell,mode)
    def edit(self,path,fn):
        p=self.root/path;data=json.loads(p.read_text());fn(data);write_json(p,data)
    def events(self,fn):
        p=self.root/'producer_events.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()];fn(rows);write_jsonl(p,rows)
    def report(self,views=False,refresh=False):
        reseal(self.root)
        if refresh: refresh_views(self.root)
        r=check_bundle(self.root,include_views=views)
        self.assertEqual(r['requirements']['artifact.integrity']['status'],'satisfied',r['requirements'])
        return r
    def rule(self,r,key,phase='P1'):
        return r['phases'][phase]['requirements'][key]['status']
    def value(self,r,key,phase='P1'):
        return r['phases'][phase]['reference'][key]['value']

    def test_six_cells_have_94_opportunities_per_view(self):
        all_reports=[]
        for cell in ('M1','M2','M3','M4','K1','K2'):
            with tempfile.TemporaryDirectory() as d:
                create_fixture(Path(d),cell);r=check_bundle(d)
                self.assertFalse(r['native_qualification'])
                for phase,views in r['views'].items():
                    self.assertEqual(views['paired_underlying_bytes']['status'],'satisfied')
                    self.assertEqual(views['A']['scores']['counts'],views['B']['scores']['counts'])
                    all_reports.append(views['A']['scores'])
                for phase,p in r['phases'].items():
                    self.assertEqual(p['requirements']['outcome.cardinality']['status'],'satisfied')
                    self.assertEqual(p['analysis_eligibility']['sink_accounting']['status'],'satisfied')
        r=aggregate_reports(all_reports,94)
        self.assertEqual(r['planned_opportunities'],94);self.assertEqual(r['evaluated_opportunities'],94)
    def test_c1_zero_execute_both_modes(self):
        for mode in ('TRY_CANCEL','WAIT_CANCELLATION_COMPLETED'):
            with tempfile.TemporaryDirectory() as d:
                create_fixture(Path(d),'C1',mode);r=check_bundle(d)
                self.assertEqual(r['phases']['P1']['observed']['dispatch_attempts'],0)
                self.assertEqual(self.rule(r,'outcome.cardinality'),'satisfied')
                self.assertEqual(self.value(r,'effect_existence'),'absent_with_complete_bounded_evidence')
    def test_c4_historical_effect_before_request(self):
        self.fixture('C4');r=self.report()
        self.assertEqual(self.value(r,'effect_order_vs_request'),'before')
        self.assertEqual(r['cross_phase']['status'],'satisfied')
    def test_c1_extra_dispatch_zero_effect_retained(self):
        self.fixture('C1')
        def add(rows):
            template=copy.deepcopy(rows[0]);template.update(record_id='extra-dispatch',producer_id='extra',sequence=1,kind='dispatch_started',payload={'request_id':'extra'},parents=[]);rows.append(template)
        self.events(add);r=self.report()
        self.assertEqual(self.rule(r,'outcome.cardinality'),'unsatisfied');self.assertTrue(r['attempt_retained'])
        self.assertEqual(r['phases']['P1']['observed']['sink']['effect_rows'],0)
    def test_c4_duplicate_dispatch_one_effect_retained(self):
        self.fixture('C4')
        def add(rows):
            template=copy.deepcopy(next(e for e in rows if e['kind']=='dispatch_started'));template.update(record_id='extra-dispatch',producer_id='extra',sequence=1,payload={'request_id':'extra'},parents=[]);rows.append(template)
        self.events(add);r=self.report()
        self.assertEqual(self.rule(r,'outcome.cardinality'),'unsatisfied');self.assertEqual(r['phases']['P1']['observed']['sink']['effect_rows'],1)
    def test_invocation_without_submission_not_delivery(self):
        self.fixture('C4')
        self.events(lambda rows:[e.update(kind='diagnostic',payload={'namespace':'test','data':{}}) for e in rows if e['kind']=='cancel_submitted'])
        r=self.report();self.assertEqual(self.value(r,'cancellation_request'),'unresolved');self.assertEqual(self.rule(r,'cancellation.submission'),'unobserved')
    def test_wrong_call_identity(self):
        self.fixture();self.events(lambda rows:[e['payload'].update(call_id='wrong') for e in rows if e['kind']=='cancellation_observed'])
        self.assertEqual(self.rule(self.report(),'schedule.causal'),'unobserved')
    def test_c4_ack_wrong_request(self):
        self.fixture('C4');self.events(lambda rows:[e['payload'].update(request_id='wrong') for e in rows if e['kind']=='effect_ack'])
        self.assertEqual(self.rule(self.report(),'schedule.causal'),'unobserved')
    def test_hidden_fence_no_caller_support(self):
        self.fixture('M3');self.edit('case.json',lambda c:c['view_permissions'].update(sink=False));r=self.report(views=True,refresh=True)
        self.assertEqual(self.value(r,'fence_existence'),'present')
        self.assertGreater(r['views']['P1']['B']['scores']['counts']['justified_unresolved'],0)
    def test_receipt_missing_ledger_fence_remains(self):
        self.fixture('M3');self.edit('case.json',lambda c:c['view_permissions'].update(fence_receipt=False));r=self.report(views=True,refresh=True)
        scores=r['views']['P1']['B']['scores'];by={e['field']:e for e in scores['opportunities']}
        self.assertEqual(by['fence']['category'],'justified_unresolved');self.assertEqual(by['fence_existence']['category'],'correct_determinate')
    def test_unsupported_positive_hidden_fence(self):
        self.fixture('M3');self.edit('case.json',lambda c:c['view_permissions'].update(sink=False));self.report(refresh=True)
        self.edit('outputs/P1-B.json',lambda c:[x.update(value='confirmed_for_fixture_scope',evidence_refs=[]) for x in c['assertions'] if x['field']=='fence'])
        r=self.report(views=True);self.assertEqual(r['views']['P1']['B']['scores']['counts']['unsupported_determinate'],1)
    def test_wrong_denial_cause(self):
        self.fixture('M3')
        with sqlite3.connect(self.root/'P1/sink.sqlite') as db: db.execute('UPDATE events SET data=? WHERE kind=?',(json.dumps({'request_id':'execute','result':{'outcome':'denied','reason':'invalid_ticket'}}),'denied'))
        r=self.report();self.assertEqual(self.rule(r,'outcome.sink_expected'),'unsatisfied');self.assertEqual(r['phases']['P1']['analysis_eligibility']['sink_accounting']['status'],'satisfied')
    def test_omitted_effect_row(self):
        self.fixture()
        with sqlite3.connect(self.root/'P1/sink.sqlite') as db: db.execute('DELETE FROM effects')
        r=self.report();self.assertEqual(self.rule(r,'sink.effect_bijection'),'unsatisfied');self.assertEqual(self.value(r,'effect_existence'),'unresolved')
    def test_bad_sink_json_no_crash(self):
        self.fixture('K2')
        with sqlite3.connect(self.root/'P1/sink.sqlite') as db: db.execute("UPDATE events SET data='bad' WHERE kind='denied'")
        r=self.report();self.assertEqual(self.rule(r,'sink.primitives'),'unsatisfied')
    def test_wrong_run_binding(self):
        self.fixture();self.edit('P1/native_history.json',lambda n:n['binding'].update(run_id='wrong'))
        self.assertEqual(self.rule(self.report(),'native.schema'),'unsatisfied')
    def test_wrong_native_start_link(self):
        self.fixture();self.edit('P1/native_history.json',lambda n:n['events'][-1]['attributes'].update(started_event_id='2'))
        self.assertEqual(self.rule(self.report(),'native.linkage'),'unsatisfied')
    def test_fractional_native_id(self):
        self.fixture();self.edit('P1/native_history.json',lambda n:n['events'][-1].update(event_id=4.0))
        self.assertEqual(self.rule(self.report(),'native.schema'),'unsatisfied')
    def test_unexpected_retry_is_outcome_not_setup(self):
        self.fixture();self.edit('observed_binding.json',lambda b:b['native'].update(attempt=2));self.events(lambda rows:[e['binding'].update(attempt=2) for e in rows])
        for phase in ('P1','P2'):
            self.edit(phase+'/native_history.json',lambda n:(n['binding'].update(attempt=2),n['events'][2]['attributes'].update(attempt=2)))
        r=self.report();self.assertEqual(r['requirements']['setup.configuration']['status'],'satisfied');self.assertEqual(self.rule(r,'outcome.native_attempts'),'unsatisfied')
    def test_misconfigured_retry_is_setup(self):
        self.fixture();self.edit('case.json',lambda c:c['configuration'].update(maximum_attempts=2));r=self.report()
        self.assertEqual(r['requirements']['setup.configuration']['status'],'unsatisfied')
    def test_bad_behavior_is_closed_schema(self):
        self.fixture();self.edit('case.json',lambda c:c['configuration'].update(behavior='continue_fenced_typo'));r=self.report()
        self.assertEqual(r['requirements']['schema.case']['status'],'unsatisfied')
    def test_missing_cancel_observation_not_heartbeat(self):
        self.fixture();self.events(lambda rows:[e.update(kind='heartbeat',payload={}) for e in rows if e['kind']=='cancellation_observed']);r=self.report()
        self.assertEqual(self.rule(r,'schedule.causal'),'unobserved')
    def test_finally_not_worker_or_native(self):
        self.fixture();self.events(lambda rows:[e.update(kind='diagnostic',payload={'namespace':'test','data':{}}) for e in rows if e['kind']=='worker_settled'])
        self.edit('P1/native_history.json',lambda n:n['events'].pop());r=self.report()
        self.assertEqual(self.value(r,'activity_execution'),'last_instrumented_point');self.assertFalse(r['phases']['P1']['capture_sufficient'])
    def test_missing_capture_ack_no_absence(self):
        self.fixture('C1');self.edit('P1/capture.json',lambda c:c.update(ack_refs=[]));r=self.report()
        self.assertEqual(self.rule(r,'capture.boundaries'),'unobserved');self.assertEqual(self.value(r,'effect_existence'),'unresolved')
    def test_mixed_sqlite_snapshots(self):
        self.fixture();self.edit('P1/capture.json',lambda c:c['sink_transaction']['table_boundaries'].update(effects='other'));r=self.report()
        self.assertEqual(self.rule(r,'capture.boundaries'),'unobserved')
    def test_queued_work_prevents_absence(self):
        self.fixture('C1');self.edit('P1/capture.json',lambda c:c.update(queued=['execute-2']));r=self.report()
        self.assertEqual(self.rule(r,'capture.stability'),'unobserved');self.assertEqual(self.value(r,'effect_existence'),'unresolved')
    def test_intervention_no_cancellation_credit(self):
        self.fixture('C1');self.edit('P1/capture.json',lambda c:c.update(interventions=['forced_stop']));r=self.report()
        self.assertFalse(r['phases']['P1']['capture_sufficient'])
    def test_missing_history_page_boundary(self):
        self.fixture();self.edit('P1/native_history.json',lambda n:n['coverage'].update(pages=[]));r=self.report()
        self.assertEqual(self.rule(r,'native.coverage'),'unobserved')
    def test_early_workflow_terminal_retained(self):
        self.fixture()
        def mutate(n):
            n['events'].append({'event_id':'5','type':'workflow_failed','phase':'P1','attributes':{'failure':{'synthetic':True}}})
            n['coverage'].update(final_event_id='5',closing_boundary_event_id='5');n['coverage']['pages'][0]['last_event_id']='5'
        self.edit('P1/native_history.json',mutate);r=self.report()
        self.assertEqual(self.rule(r,'native.hold'),'unsatisfied');self.assertEqual(self.value(r,'workflow_execution'),'exact_terminal_status')
    def test_cleanup_failure_preserves_effect(self):
        self.fixture();self.edit('cleanup.json',lambda c:c.update(secondary_errors=['worker shutdown error']));r=self.report()
        self.assertEqual(r['cleanup']['requirement']['status'],'unsatisfied');self.assertEqual(self.value(r,'effect_existence'),'present')
    def test_reverse_wall_clocks_no_change(self):
        self.fixture();before=self.report();self.events(lambda rows:[e.update(wall_clock=-e['wall_clock']) for e in rows]);after=self.report()
        self.assertEqual(before['phases']['P1']['reference'],after['phases']['P1']['reference'])
    def test_permuted_serialization_no_change(self):
        self.fixture();before=self.report();self.events(lambda rows:rows.reverse());after=self.report()
        self.assertEqual(before,after)
    def test_cycle_no_order_claim(self):
        self.fixture();self.events(lambda rows:rows[0]['parents'].append(rows[-1]['record_id']));r=self.report()
        self.assertEqual(r['requirements']['causal.graph']['status'],'unsatisfied');self.assertEqual(self.value(r,'effect_order_vs_request'),'unresolved')
    def test_duplicate_event_identity(self):
        self.fixture();self.events(lambda rows:rows.append(copy.deepcopy(rows[0])));r=self.report()
        self.assertEqual(r['requirements']['schema.events']['status'],'unsatisfied')
    def test_phase_leakage_rejected(self):
        self.fixture();self.edit('views/P1/B/sink_lookup.json',lambda c:c.update(hidden_envelope={'fence':'confirmed'}));r=self.report(views=True)
        self.assertEqual(r['views']['P1']['B']['view_integrity']['status'],'unsatisfied')
    def test_same_json_different_bytes_breaks_pair(self):
        self.fixture();p=self.root/'views/P1/B/configuration.json';p.write_text(json.dumps(json.loads(p.read_text()),separators=(',',':')))
        r=self.report(views=True);self.assertEqual(r['views']['P1']['paired_underlying_bytes']['status'],'unsatisfied')
    def test_always_unresolved_no_conclusive_credit(self):
        self.fixture()
        for phase in ('P1','P2'): self.edit('outputs/'+phase+'-B.json',lambda c:[x.update(value='unresolved',evidence_refs=[]) for x in c['assertions']])
        r=self.report(views=True)
        self.assertEqual(r['views']['P1']['B']['scores']['metrics']['conclusive_coverage'],0)
        self.assertIsNone(r['views']['P1']['B']['scores']['metrics']['determinate_claim_support_rate'])
    def test_omitted_output_is_not_unresolved(self):
        self.fixture();self.edit('outputs/P1-B.json',lambda c:c.update(assertions=[]));r=self.report(views=True)
        self.assertEqual(r['views']['P1']['B']['scores']['counts']['malformed_or_omitted'],10)
    def test_unfavorable_claim_does_not_exclude(self):
        self.fixture();self.edit('outputs/P1-B.json',lambda c:[x.update(value='absent_with_complete_bounded_evidence') for x in c['assertions'] if x['field']=='effect_existence']);r=self.report(views=True)
        self.assertEqual(r['views']['P1']['B']['scores']['counts']['contradicted'],1);self.assertEqual(r['phases']['P1']['analysis_eligibility']['sink_accounting']['status'],'satisfied')
    def test_fake_fence_receipt_no_ledger(self):
        self.fixture()
        def change(rows):
            e=copy.deepcopy(rows[0]);e.update(record_id='fake-fence',producer_id='fake',sequence=1,kind='fence_receipt',payload=dict(request_id='fake',sink_seq=7,root='rootR',withdrawn_epoch=7,new_epoch=8),parents=['sink:7']);rows.append(e)
        self.events(change);r=self.report();self.assertEqual(self.value(r,'fence'),'unresolved')
    def test_declared_native_provenance_relabel_rejected(self):
        self.fixture('K1');self.edit('case.json',lambda c:c.update(study_phase='measurement'));r=self.report()
        self.assertEqual(r['requirements']['schema.case']['status'],'unsatisfied')
    def test_nonobject_registry_entries_no_crash(self):
        for value in (None,'bad',7,[]):
            write_json(self.root/'registry.json',{'schema_version':VERSION,'artifacts':[value]});self.assertTrue(Bundle(self.root).errors)
    def test_nonfinite_number_rejected(self):
        for value in ('1e309','-1e309','NaN','Infinity'):
            with self.assertRaises(ArtifactError): loads(value)
    def test_stale_hash_separate_from_semantics(self):
        self.fixture();p=self.root/'case.json';p.write_text(p.read_text()+' ')
        self.assertEqual(check_bundle(self.root)['requirements']['artifact.integrity']['status'],'unsatisfied')
    def test_unsafe_registry_path(self):
        write_json(self.root/'registry.json',{'schema_version':VERSION,'artifacts':[dict(artifact_id='x',path='../outside.json',role='case',phase='P0',schema_version=VERSION,byte_length=0,sha256='0'*64,producer='fixture')]})
        self.assertTrue(any('path' in x for x in Bundle(self.root).errors))
    def test_unknown_nested_event_field(self):
        self.fixture();self.events(lambda rows:rows[0]['payload'].update(oracle='success'));r=self.report()
        self.assertEqual(r['requirements']['schema.events']['status'],'unsatisfied')
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ArtifactError): loads('{"x":1,"x":2}')

if __name__=='__main__': unittest.main()
