import copy,json,unittest
from pathlib import Path
from checker import check
from workflow import execute,ARGS
HERE=Path(__file__).resolve().parent
class InstrumentTests(unittest.TestCase):
 def setUp(self):self.record=json.loads((HERE/'evidence/restart_qualification01/framework_prior0_revoked0/record.json').read_text())
 def test_positive(self):self.assertTrue(check(self.record)['qualified'])
 def test_missing_attempt(self):
  self.record['sink']['events']=[e for e in self.record['sink']['events'] if not(e['kind']=='receipt' and e['data']['request']['id']=='resume-execute')];self.assertFalse(check(self.record)['qualified'])
 def test_wrong_principal(self):
  self.record['binding']['principal']='parentP';self.assertFalse(check(self.record)['qualified'])
 def test_restored_checkpoint(self):
  self.record['workers'][1]['checkpoint_before']={};self.assertFalse(check(self.record)['qualified'])
 def test_no_restart(self):
  self.record['workers'][1]['pid']=self.record['workers'][0]['pid'];self.assertFalse(check(self.record)['qualified'])
 def test_false_completion(self):
  self.record['workers'][1]['result']['messages'][-1]['content']='{"outcome":"sent"}';self.assertFalse(check(self.record)['qualified'])
 def test_wrong_effect(self):
  self.record['sink']['effects'][0]['payload']='other';self.assertFalse(check(self.record)['qualified'])
 def test_missing_terminal(self):
  self.record['sink']['events']=[e for e in self.record['sink']['events'] if e['kind']!='effect'];self.assertFalse(check(self.record)['qualified'])
 def test_post_fence_effect(self):
  # Fabricated counterexample only: insert a committed revocation before the effect.
  r=self.record;r['revoked']=True;r['revocation']={'outcome':'revocation','root':'rootR','withdrawn_epoch':7,'new_epoch':8}
  ev=r['sink']['events'];pos=next(i for i,e in enumerate(ev) if e['kind']=='receipt' and e['data']['request']['id']=='resume-execute')
  ev[pos:pos]=[{'seq':0,'kind':'receipt','data':{'actor':'controller','request':{'id':'revoke','op':'revoke','claim':'controller'}}},{'seq':0,'kind':'revocation','data':{'request_id':'revoke','result':{'outcome':'revocation','root':'rootR','withdrawn_epoch':7,'new_epoch':8}}}]
  for n,e in enumerate(ev,1):e['seq']=n
  r['sink']['effects'][0]['event_seq']=ev[-1]['seq'];r['sink']['authority']=[{'root':'rootR','epoch':8,'active':0}]
  result=check(r);self.assertFalse(result['qualified']);self.assertEqual(result['operation_outcome'],'post_fence_effect')
 def test_duplicate_does_not_substitute_for_effect(self):
  for e in self.record['sink']['events']:
   if e['kind']=='effect':e['data']['result']={'outcome':'duplicate'}
  self.assertFalse(check(self.record)['qualified'])
 def test_wrong_delegation_scope(self):
  self.record['sink']['events'][1]['data']['request']['scope']='other:key';self.assertFalse(check(self.record)['qualified'])
 def test_wrong_admission_grant(self):
  self.record['sink']['events'][4]['data']['result']['grant']='parent-0';self.assertFalse(check(self.record)['qualified'])
 def test_wrong_effect_event_binding(self):
  self.record['sink']['events'][-1]['data']['result']['epoch']=8;self.assertFalse(check(self.record)['qualified'])
 def test_empty_checkpoint_pair(self):
  self.record['workers'][0]['checkpoint_after']={};self.record['workers'][1]['checkpoint_before']={};self.assertFalse(check(self.record)['qualified'])
 def test_empty_interrupt_pair(self):
  self.record['workers'][0]['pending'][0]['id']='';self.record['workers'][1]['restored_interrupts'][0]['id']='';self.assertFalse(check(self.record)['qualified'])
 def test_wrong_worker_binding(self):
  self.record['workers'][1]['binding']['ticket']='other';self.assertFalse(check(self.record)['qualified'])
 def test_wrong_tool_request(self):
  self.record['workers'][1]['trace'][2]['request']['scope']='other';self.assertFalse(check(self.record)['qualified'])
 def test_binding_rejects_before_gateway(self):
  class Never:
   def send(self,x):raise AssertionError('gateway must not be called')
  for field,value in [('to',['other@example.invalid']),('body','changed'),('scope','other'),('subject','changed'),('cc',['other@example.invalid'])]:
   args=copy.deepcopy(ARGS);args[field]=value
   with self.subTest(field=field),self.assertRaises(ValueError):execute(Never(),args,'bad',[])
if __name__=='__main__':unittest.main()
