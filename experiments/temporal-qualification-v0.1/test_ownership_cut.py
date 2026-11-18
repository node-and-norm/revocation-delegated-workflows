import tempfile,unittest
from pathlib import Path
from unittest.mock import MagicMock,patch
from bounded_exchange import SingleUseExchange,claim_channel
from observation_cut import ObservationCut,DOMAINS

class OwnershipTests(unittest.TestCase):
 def test_fresh_session_cannot_reuse_same_endpoint(self):
  c=MagicMock();ctx=MagicMock();s=SingleUseExchange(c,ctx)
  with tempfile.TemporaryDirectory() as d:
   # Even invalid preflight consumes this exact endpoint; conservative no-retry.
   with self.assertRaises(ValueError):s.run({},Path(d)/'first',timeout=0)
   with self.assertRaisesRegex(RuntimeError,'channel_consumed'):SingleUseExchange(c,ctx).run({},Path(d)/'second')
  ctx.Process.assert_not_called()
 def test_distinct_endpoint_allowed(self):
  a,b=MagicMock(),MagicMock();claim_channel(a);claim_channel(b)
  with self.assertRaises(RuntimeError):claim_channel(a)

class CutTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.path=Path(self.temp.name)/'snapshot';self.path.write_text('synthetic fixture')
  self.cut=ObservationCut('attempt-1','cut-1')
 def add(self,domain,**overrides):
  args={'attempt_id':'attempt-1','cut_id':'cut-1','artifact':self.path,
        'producer_sequence':1,'acknowledgment':'frozen_before_cleanup','completeness':'complete'}
  args.update(overrides);self.cut.capture(domain,**args)
 def test_complete_handoff_not_atomic_or_qualified(self):
  for d in DOMAINS:self.add(d)
  r=self.cut.seal();self.assertEqual(r['status'],'handoff_complete');self.assertFalse(r['atomic_snapshot_proven']);self.assertIsNone(r['qualification_verdict'])
 def test_missing_not_absence(self):
  self.add('sink');r=self.cut.seal();self.assertEqual(r['status'],'incomplete');self.assertIn('native_history:missing',r['reasons'])
 def test_explicit_unknown_and_incomplete(self):
  self.add('sink',completeness='unknown');self.add('bridge',completeness='incomplete');r=self.cut.seal();self.assertIn('sink:unknown',r['reasons']);self.assertIn('bridge:incomplete',r['reasons'])
 def test_mismatched_ack_id_rejected(self):
  with self.assertRaises(ValueError):self.add('sink',cut_id='other')
  with self.assertRaises(ValueError):self.add('sink',attempt_id='other')
 def test_cleanup_before_cut_invalid(self):
  for d in DOMAINS:self.add(d)
  self.cut.start_cleanup();self.assertIn('cleanup_started_before_seal',self.cut.seal()['reasons'])
 def test_no_captures_after_cleanup(self):
  self.cut.start_cleanup()
  with self.assertRaises(RuntimeError):self.add('sink')
 def test_mutated_record_invalid(self):
  for d in DOMAINS:self.add(d)
  self.path.write_text('mutated');self.assertIn('sink:changed_after_capture',self.cut.seal()['reasons'])
 def test_duplicate_capture_rejected(self):
  self.add('sink')
  with self.assertRaises(ValueError):self.add('sink')
 def test_unreadable_record_invalid(self):
  self.add('sink');self.path.unlink();self.assertIn('sink:unreadable',self.cut.seal()['reasons'])
 def test_cleanup_during_hash_blocks_complete_handoff(self):
  for d in DOMAINS:self.add(d)
  from observation_cut import digest
  def interleave(path):self.cut.start_cleanup();return digest(path)
  with patch('observation_cut.digest',side_effect=interleave):r=self.cut.seal()
  self.assertEqual(r['status'],'incomplete');self.assertIn('cleanup_started_during_seal',r['reasons'])
 def test_cleanup_during_capture_blocks_acceptance(self):
  from observation_cut import digest
  def interleave(path):self.cut.start_cleanup();return digest(path)
  with patch('observation_cut.digest',side_effect=interleave):
   with self.assertRaises(RuntimeError):self.add('sink')
  self.assertIn('sink:missing',self.cut.seal()['reasons'])
 def test_closed_after_seal(self):
  self.cut.seal()
  with self.assertRaises(RuntimeError):self.add('sink')
  with self.assertRaises(RuntimeError):self.cut.seal()
 def test_ack_and_sequence_required(self):
  with self.assertRaises(ValueError):self.add('sink',acknowledgment='received')
  with self.assertRaises(ValueError):self.add('sink',producer_sequence=True)
if __name__=='__main__':unittest.main()
