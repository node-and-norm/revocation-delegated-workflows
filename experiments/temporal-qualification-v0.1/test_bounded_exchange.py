import json,tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock,patch
from bounded_exchange import SingleUseExchange,exchange_worker,atomic_record
from bridge import FIXED

class ExchangeTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.folder=Path(self.tmp.name)/'attempt';self.req={'id':'case-1',**FIXED}
  self.now=0;self.context=MagicMock();self.process=self.context.Process.return_value
  self.process.pid=1;self.process.exitcode=0;self.process.is_alive.return_value=False
  self.channel=MagicMock();self.channel.recv.return_value={'outcome':'denied','reason':'revoked'}
  self.session=SingleUseExchange(self.channel,self.context,lambda:self.now)
  self.process.join.side_effect=lambda _:exchange_worker(self.channel,self.req,self.folder)
 def run_exchange(self):return self.session.run(self.req,self.folder,timeout=10,cleanup_timeout=2)
 def test_timely_reply_and_no_retry(self):
  r=self.run_exchange();self.assertEqual(r['outcome'],'reply_observed');self.channel.send.assert_called_once();self.assertFalse(r['retry_allowed'])
  with self.assertRaisesRegex(RuntimeError,'no_retry'):self.session.run(self.req,Path(self.tmp.name)/'again')
  self.context.Process.assert_called_once()
 def test_constructor_failure_not_dispatched(self):
  self.context.Process.side_effect=RuntimeError('construct');r=self.run_exchange();self.assertEqual(r['outcome'],'not_dispatched');self.channel.send.assert_not_called()
 def test_start_failure_uncertain(self):
  self.process.start.side_effect=RuntimeError('start');self.process.pid=None
  r=self.run_exchange();self.assertEqual(r['outcome'],'uncertain');self.assertFalse(r['cleanup_complete'])
 def test_partial_send_failure_uncertain_no_retry(self):
  self.channel.send.side_effect=BrokenPipeError('partial');r=self.run_exchange();self.assertEqual(r['outcome'],'uncertain');self.channel.send.assert_called_once();self.channel.recv.assert_not_called()
 def test_readable_but_incomplete_reply_timeout(self):
  def blocked(_):self.now=10
  self.process.join.side_effect=blocked;self.process.is_alive.side_effect=[True,False]
  r=self.run_exchange();self.assertEqual(r['outcome'],'uncertain');self.process.terminate.assert_called_once();self.assertTrue(r['cleanup_complete'])
 def test_termination_does_not_settle(self):
  self.process.join.side_effect=lambda _:setattr(self,'now',10);self.process.is_alive.return_value=True
  r=self.run_exchange();self.assertFalse(r['cleanup_complete']);self.assertEqual(r['outcome'],'uncertain')
 def test_late_reply_preserved_not_counted_timely(self):
  def late(_):exchange_worker(self.channel,self.req,self.folder);self.now=10
  self.process.join.side_effect=late
  r=self.run_exchange();self.assertEqual(r['outcome'],'uncertain');self.assertIsNone(r['reply']);self.assertTrue((self.folder/'reply.json').exists());self.channel.send.assert_called_once()
 def test_missing_reply_not_no_effect(self):
  self.process.join.side_effect=None;r=self.run_exchange();self.assertEqual(r['outcome'],'uncertain')
 def test_wrong_binding_not_accepted(self):
  self.process.join.side_effect=lambda _:atomic_record(self.folder/'reply.json',{'request_id':'other','gateway_result':{}})
  self.assertEqual(self.run_exchange()['outcome'],'uncertain')
 def test_primary_and_cleanup_errors_preserved(self):
  self.process.start.side_effect=RuntimeError('primary');self.process.is_alive.return_value=True;self.process.terminate.side_effect=OSError('cleanup')
  r=self.run_exchange();self.assertEqual([e['stage'] for e in r['errors']],['exchange','cleanup']);self.assertFalse(r['cleanup_complete'])
 def test_disk_failure_prevents_send(self):
  self.folder.mkdir()
  with patch('bounded_exchange.atomic_record',side_effect=OSError('disk')):
   with self.assertRaises(OSError):exchange_worker(self.channel,self.req,self.folder)
  self.channel.send.assert_not_called()
 def test_intent_present_before_dispatch(self):
  self.folder.mkdir()
  def send(_):self.assertEqual(json.loads((self.folder/'dispatch_intent.json').read_text())['request_id'],'case-1')
  self.channel.send.side_effect=send;exchange_worker(self.channel,self.req,self.folder);self.channel.send.assert_called_once()
 def test_output_write_failure_retains_send_uncertainty(self):
  original=atomic_record
  def fail_reply(path,value):
   if path.name=='reply.json':raise OSError('disk after send')
   return original(path,value)
  with patch('bounded_exchange.atomic_record',side_effect=fail_reply):r=self.run_exchange()
  self.assertEqual(r['outcome'],'uncertain');self.channel.send.assert_called_once()
 def test_all_record_failure_keeps_primary_in_return(self):
  with patch('bounded_exchange.atomic_record',side_effect=OSError('disk')):r=self.run_exchange()
  self.assertEqual(r['outcome'],'uncertain');self.assertFalse(r['record_complete']);self.assertTrue(r['errors']);self.channel.send.assert_not_called()
 def test_budget_expires_before_launch(self):
  def construct(**kwargs):self.now=10;return self.process
  self.context.Process.side_effect=construct
  r=self.run_exchange();self.assertEqual(r['outcome'],'not_dispatched');self.process.start.assert_not_called()
 def test_oversize_reply_rejected(self):
  self.process.join.side_effect=lambda _:(self.folder/'reply.json').write_bytes(b'x'*65537)
  self.assertEqual(self.run_exchange()['outcome'],'uncertain')
 def test_cleanup_join_bound(self):
  calls=[]
  def blocked(duration):calls.append(duration);self.now=10
  self.process.join.side_effect=blocked;self.process.is_alive.side_effect=[True,False]
  self.run_exchange();self.assertEqual(calls,[10,2])
 def test_nonzero_exit_with_reply_remains_uncertain(self):
  self.process.exitcode=1
  r=self.run_exchange();self.assertEqual(r['outcome'],'uncertain');self.assertTrue((self.folder/'reply.json').exists())
 def test_validation_crosses_cutoff(self):
  original=json.loads
  def delayed(raw):self.now=10;return original(raw)
  with patch('bounded_exchange.json.loads',side_effect=delayed):r=self.run_exchange()
  self.assertEqual(r['outcome'],'uncertain')
 def test_supervisor_record_failure_is_not_qualification(self):
  original=atomic_record
  def fail_supervisor(path,value):
   if path.name=='supervisor.json':raise OSError('supervisor disk')
   return original(path,value)
  with patch('bounded_exchange.atomic_record',side_effect=fail_supervisor):r=self.run_exchange()
  self.assertEqual(r['outcome'],'reply_observed');self.assertFalse(r['record_complete'])
 def test_invalid_timeout_no_process(self):
  for val in [0,-1,float('inf'),float('nan')]:
   with self.subTest(value=val),self.assertRaises(ValueError):SingleUseExchange(MagicMock(),self.context).run(self.req,self.folder,timeout=val)
  self.context.Process.assert_not_called()
 def test_concurrent_use_rejected_without_launch(self):
  self.session._lock.acquire()
  try:
   with self.assertRaisesRegex(RuntimeError,'already_in_use'):self.run_exchange()
  finally:self.session._lock.release()
  self.context.Process.assert_not_called()
if __name__=='__main__':unittest.main()
