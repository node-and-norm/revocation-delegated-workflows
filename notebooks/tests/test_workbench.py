"""Offline regressions. No historical input is modified."""
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "notebooks"))
from workbench.core import (ARCHIVE, RECORDS, SUMMARY, EvidenceError, EvidenceStore,
                            Scope, _json, _safe_path, barrier_rows, challenge_claims,
                            derive_case, read_member, reconcile, run_workbench)
from workbench.presentation import case_matrix, excerpt, table, barrier_view, workflow_map


class WorkbenchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review_run = run_workbench(ROOT)
        cls.store = cls.review_run.evidence

    def test_all_twelve_cases_reconcile(self):
        self.assertEqual(12, len(self.store.rows))
        self.assertEqual(12, len({(r['path'], r['schedule']) for r in self.store.rows}))

    def test_aggregate_accounting(self):
        b = self.review_run.brief()
        self.assertEqual((12, 6, 6, 8, 0, 4), tuple(b[k] for k in (
            'selected_cases', 'effects', 'revoked_denials', 'cases_with_fence',
            'post_fence_effects_in_fenced_cases', 'no_fence_cases')))

    def test_three_claims_have_expected_counterexamples(self):
        for c, schedule in zip(self.review_run.challenges, ('S4', 'S5', 'S2')):
            self.assertEqual([f'direct/{schedule}', f'framework/{schedule}'], c['witnesses'])

    def test_absent_counterexample_is_unresolved(self):
        rows = self.store.select(Scope(schedules=('S0',)))
        self.assertTrue(all(c['status'].startswith('unresolved') for c in challenge_claims(rows)))

    def test_single_case_scope_changes_brief(self):
        r = run_workbench(ROOT, Scope(paths=('framework',), schedules=('S2',)))
        self.assertEqual(1, r.brief()['selected_cases'])
        self.assertEqual(1, r.brief()['effects'])

    def test_default_scope_resets_selection(self):
        self.store.select(Scope(paths=('direct',), schedules=('S0',)))
        self.assertEqual(12, len(self.store.select(Scope())))

    def test_empty_and_invalid_scope_rejected(self):
        for kw in ({'paths': ()}, {'schedules': ()}, {'paths': ('temporal',)},
                   {'schedules': ('S99',)}, {'schedules': ('S1', 'S1')}, {'paths': ['direct']}):
            with self.subTest(kw=kw), self.assertRaises(EvidenceError):
                Scope(**kw)

    def test_invalid_case_rejected(self):
        with self.assertRaises(EvidenceError):
            self.store.case('direct', 'S7')

    def test_no_fence_is_not_zero_post_fence_evidence(self):
        for row in self.store.rows:
            if row['schedule'] in ('S0', 'S5'):
                self.assertIsNone(row['post_fence_effect_count'])
                self.assertEqual(0, row['historical_post_fence_field'])

    def test_no_fenced_cases_has_no_post_fence_aggregate(self):
        r = run_workbench(ROOT, Scope(schedules=('S0', 'S5')))
        self.assertIsNone(r.brief()['post_fence_effects_in_fenced_cases'])

    def test_s0_stays_idle_without_request(self):
        for row in self.store.select(Scope(schedules=('S0',))):
            self.assertEqual('IDLE', row['caller_state'])
            self.assertFalse(row['request_accepted'])

    def test_s2_effect_precedes_fence_and_persists(self):
        for path in ('direct', 'framework'):
            row = derive_case(self.store.case(path, 'S2'))
            self.assertEqual([7], row['effect_sequences'])
            self.assertEqual(9, row['fence_seq'])
            barriers = barrier_rows(self.store.case(path, 'S2'))
            self.assertEqual(1, barriers[-1]['effects'])
            self.assertEqual('INSTALLED_CONFIRMED', barriers[-1]['caller'])

    def test_source_hashes_all_resolve(self):
        self.assertEqual(10, len(self.store.sources))
        for key, source in self.store.sources.items():
            self.assertEqual(source['sha256'], sha256(self.store.source_bytes[key]).hexdigest())

    def test_temporal_status_transformation_disclosed(self):
        s = self.store.sources['temporal_status']
        self.assertIn('transformation', s)
        self.assertIn('original_sha256', s)

    def test_source_keys_unknown_rejected(self):
        with self.assertRaises(EvidenceError):
            self.store.source_text('invented')

    def test_claim_filter_is_literal_case_insensitive_and_resettable(self):
        self.assertEqual(10, len(self.store.source_claims('')))
        self.assertEqual(self.store.source_claims('TEMPORAL'), self.store.source_claims('temporal'))
        self.assertEqual([], self.store.source_claims('no-such-claim-999'))
        self.assertEqual(10, len(self.store.source_claims('')))

    def test_bad_claim_query_rejected(self):
        with self.assertRaises(EvidenceError):
            self.store.source_claims(None)

    def test_case_inspection_cannot_mutate_internal_evidence(self):
        c = self.store.case('direct', 'S2')
        c['sink']['effects'][0]['root'] = 'tampered'
        self.assertEqual('rootR', self.store.case('direct', 'S2')['sink']['effects'][0]['root'])

    def test_selection_and_claim_copies_are_deep(self):
        rows = self.store.select(Scope())
        rows[0]['effect_sequences'].append(999)
        self.assertEqual([7], self.store.rows[0]['effect_sequences'])
        claims = self.store.source_claims('')
        claims[0]['source_refs'][0]['source_key'] = 'bad'
        self.assertNotEqual('bad', self.store.registry['records'][0]['source_refs'][0]['source_key'])

    def test_summary_disagreement_stops(self):
        s = deepcopy(self.store.summary)
        s['rows'][0]['effect_count'] = 0
        with self.assertRaises(EvidenceError):
            reconcile(s, self.store.raw)

    def test_duplicate_or_missing_case_stops(self):
        for rows in (self.store.summary['rows'][:-1], self.store.summary['rows'] + self.store.summary['rows'][:1]):
            s = deepcopy(self.store.summary); s['rows'] = rows
            with self.assertRaises(EvidenceError):
                reconcile(s, self.store.raw)

    def test_effect_identity_mutation_stops(self):
        c = self.store.case('direct', 'S2')
        c['sink']['effects'][0]['root'] = 'wrong'
        with self.assertRaises(EvidenceError):
            derive_case(c)

    def test_effect_without_event_stops(self):
        c = self.store.case('direct', 'S2')
        c['sink']['effects'][0]['event_seq'] = 999
        with self.assertRaises(EvidenceError):
            derive_case(c)

    def test_barrier_caller_mutation_stops(self):
        c = self.store.case('direct', 'S2')
        c['barriers'][0]['caller_state'] = 'INSTALLED_CONFIRMED'
        with self.assertRaises(EvidenceError):
            derive_case(c)

    def test_barrier_effect_mutation_stops(self):
        c = self.store.case('direct', 'S2')
        c['barriers'][-1]['effects'] = []
        with self.assertRaises(EvidenceError):
            derive_case(c)

    def test_barrier_history_mutation_stops(self):
        c = self.store.case('direct', 'S2')
        c['barriers'][0]['committed_events'][0]['kind'] = 'changed'
        with self.assertRaises(EvidenceError):
            derive_case(c)

    def test_caller_trace_discontinuity_stops(self):
        c = self.store.case('direct', 'S2')
        c['caller_trace'][1]['before'] = 'IDLE'
        with self.assertRaises(EvidenceError):
            derive_case(c)

    def test_duplicate_json_key_stops(self):
        with self.assertRaises(EvidenceError):
            _json(b'{"a":1,"a":2}', 'test')

    def test_path_escape_stops(self):
        for path in ('../outside', '/tmp/outside', 'a/../../outside'):
            with self.assertRaises(EvidenceError):
                _safe_path(ROOT, path)

    def test_missing_archive_member_stops(self):
        with self.assertRaises(EvidenceError):
            read_member(self.store.files[ARCHIVE], 'not-present')

    def test_ambiguous_archive_member_stops(self):
        import warnings
        b = BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with ZipFile(b, 'w') as z:
                z.writestr('same', 'a'); z.writestr('same', 'b')
        with self.assertRaises(EvidenceError):
            read_member(b.getvalue(), 'same')

    def test_changed_and_missing_inputs_stop(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            manifest = ROOT / 'notebooks/workbench/input_manifest.json'
            target = temp / 'notebooks/workbench/input_manifest.json'
            target.parent.mkdir(parents=True); target.write_bytes(manifest.read_bytes())
            for item in json.loads(manifest.read_text())['inputs']:
                out = temp / item['path']; out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes((ROOT / item['path']).read_bytes())
            self.assertEqual(12, len(EvidenceStore.load(temp).rows))
            damaged = temp / SUMMARY
            saved = damaged.read_bytes()
            damaged.write_bytes(saved + b' ')
            with self.assertRaisesRegex(EvidenceError, 'hash mismatch'):
                EvidenceStore.load(temp)
            damaged.unlink()
            with self.assertRaisesRegex(EvidenceError, 'Missing or malformed'):
                EvidenceStore.load(temp)

    def test_source_excerpt_is_exact(self):
        s = self.store.source_text('withdrawal_review').splitlines()
        view = excerpt(self.store, 'withdrawal_review', 3, 5)
        self.assertIn('\n'.join(s[2:7]), view.text)

    def test_bad_excerpt_range_rejected(self):
        for start, count in ((0, 1), (1, 0), (999999, 1)):
            with self.assertRaises(ValueError):
                excerpt(self.store, 'withdrawal_review', start, count)

    def test_html_escapes_untrusted_text(self):
        view = table(['<script>'], [['<script>alert(1)</script>']])
        self.assertNotIn('<script>', view.html)
        self.assertIn('&lt;script&gt;', view.html)

    def test_empty_table_is_explicit(self):
        self.assertIn('No records match', table(['x'], []).text)

    def test_svg_has_titles_no_remote_assets(self):
        views = [workflow_map(), barrier_view(self.store.case('direct', 'S2')),
                 barrier_view(self.store.case('direct', 'S4'))]
        import xml.etree.ElementTree as ET
        ids = []
        for view in views:
            svg = ET.fromstring(view.svg)
            ids.extend(e.attrib['id'] for e in svg.iter() if 'id' in e.attrib)
            self.assertNotIn('<script', view.svg)
            self.assertNotIn('<image', view.svg)
        self.assertEqual(len(ids), len(set(ids)))

    def test_audit_tracks_actual_stages(self):
        self.assertEqual(['scope', 'verify', 'reconcile', 'retrieve', 'challenge', 'brief'],
                         [a['stage'] for a in self.review_run.audit])

    def test_overlay_does_not_rewrite_original_registry(self):
        self.assertEqual('2026-11-04', self.store.registry['as_of_utc_date'])
        self.assertEqual('2026-11-06', self.store.overlays['as_of_utc_date'])
        self.assertIn('outstanding', self.store.source_claims('unchecked_success')[0]['uncertainty_and_limits'])


if __name__ == '__main__':
    unittest.main()
