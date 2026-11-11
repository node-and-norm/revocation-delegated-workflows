"""Prospective evidence handoff gate, not proof of atomic distributed snapshot.

All acknowledgments are trusted coordinator inputs. No native exporter is wired.
"""
import hashlib
import threading
from functools import wraps
from pathlib import Path

DOMAINS = frozenset({'native_history','worker_instrumentation','bridge','sink'})


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda:stream.read(65536), b''):
            h.update(part)
    return h.hexdigest()


def serialized(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper


class ObservationCut:
    def __init__(self, attempt_id, cut_id):
        if not attempt_id or not cut_id:
            raise ValueError('nonempty_identity_required')
        self._lock = threading.RLock()
        self.attempt_id = attempt_id
        self.cut_id = cut_id
        self._records = {}
        self._cleanup_started = False
        self._sealed = None

    @serialized
    def capture(self, domain, *, attempt_id, cut_id, artifact, producer_sequence,
                acknowledgment, completeness):
        if self._sealed is not None or self._cleanup_started:
            raise RuntimeError('cut_closed')
        if domain not in DOMAINS or domain in self._records:
            raise ValueError('unknown_or_duplicate_domain')
        if attempt_id != self.attempt_id or cut_id != self.cut_id:
            raise ValueError('identity_mismatch')
        if not isinstance(producer_sequence,int) or isinstance(producer_sequence,bool) or producer_sequence < 0:
            raise ValueError('producer_sequence_required')
        if acknowledgment != 'frozen_before_cleanup':
            raise ValueError('freeze_acknowledgment_required')
        if completeness not in ('complete','incomplete','unknown'):
            raise ValueError('explicit_completeness_required')
        path = Path(artifact).resolve(strict=True)
        fingerprint = digest(path)
        if self._cleanup_started or self._sealed is not None:
            raise RuntimeError('cut_closed_during_capture')
        self._records[domain] = {'artifact':str(path),'sha256':fingerprint,
            'producer_sequence':producer_sequence,'acknowledgment':acknowledgment,
            'completeness':completeness}

    @serialized
    def start_cleanup(self):
        self._cleanup_started = True

    @serialized
    def seal(self):
        if self._sealed is not None:
            raise RuntimeError('already_sealed')
        reasons = []
        if self._cleanup_started:
            reasons.append('cleanup_started_before_seal')
        for domain in sorted(DOMAINS):
            record = self._records.get(domain)
            if record is None:
                reasons.append(domain+':missing')
                continue
            if record['completeness'] != 'complete':
                reasons.append(domain+':'+record['completeness'])
            try:
                if digest(record['artifact']) != record['sha256']:
                    reasons.append(domain+':changed_after_capture')
            except OSError:
                reasons.append(domain+':unreadable')
        if self._cleanup_started and 'cleanup_started_before_seal' not in reasons:
            reasons.append('cleanup_started_during_seal')
        self._sealed = {'attempt_id':self.attempt_id,'cut_id':self.cut_id,
            'status':'handoff_complete' if not reasons else 'incomplete',
            'reasons':reasons,'records':{k:v.copy() for k,v in self._records.items()},
            'atomic_snapshot_proven':False,'qualification_verdict':None}
        return {**self._sealed,'records':{k:v.copy() for k,v in self._sealed['records'].items()},
                'reasons':list(reasons)}
