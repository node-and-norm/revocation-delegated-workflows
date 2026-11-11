"""Unintegrated single-use process-supervised exchange candidate.

Caller retains original gateway endpoint through teardown; never concurrently
uses it. Any use consumes the session, including timeout/failure. No native
process test has qualified this implementation.
"""
import json
import math
import multiprocessing as mp
import os
import threading
import time
import weakref
from pathlib import Path
from bridge import validate

MAX_RESULT_BYTES = 65536

# Same-process coordinator guard, not OS descriptor identity or security isolation.
_CLAIMS = weakref.WeakKeyDictionary()
_CLAIMS_LOCK = threading.Lock()


def claim_channel(channel):
    with _CLAIMS_LOCK:
        if channel in _CLAIMS:
            raise RuntimeError('channel_consumed_no_retry')
        # Weak keys avoid retaining descriptors after their explicit owner drops
        # them. While this exact endpoint object exists its claim is permanent.
        _CLAIMS[channel] = True



def atomic_record(path, value):
    data = json.dumps(value, sort_keys=True).encode('utf-8')
    if len(data) > MAX_RESULT_BYTES:
        raise ValueError('record_too_large')
    temp = path.with_suffix('.pending')
    with temp.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def exchange_worker(channel, request, folder):
    """Single send; intent persisted before send. No retry and no controller ops."""
    folder = Path(folder)
    request = validate(request)
    try:
        atomic_record(folder / 'dispatch_intent.json', {'request_id':request['id']})
        channel.send(request)
        result = channel.recv()  # parent deadline also covers incomplete frames
        atomic_record(folder / 'reply.json', {'request_id':request['id'], 'gateway_result':result})
    except BaseException as error:
        try:
            atomic_record(folder / 'worker_error.json', {'error':repr(error)})
        except BaseException:
            pass  # parent classifies missing completion as uncertain, not absence
        raise
    # Original endpoint remains owned by caller. Process exit closes only this
    # duplicate. Never reuse the original stream after any partial exchange.


class SingleUseExchange:
    def __init__(self, channel, context=None, clock=time.monotonic):
        self.channel = channel
        self.context = context if context is not None else mp.get_context('spawn')
        self.clock = clock
        self._lock = threading.Lock()
        self._used = False

    def run(self, request, folder, timeout=20, cleanup_timeout=5):
        if not self._lock.acquire(blocking=False):
            raise RuntimeError('exchange_already_in_use')
        try:
            if self._used:
                raise RuntimeError('exchange_consumed_no_retry')
            self._used = True
            claim_channel(self.channel)
            return self._run(request, Path(folder), timeout, cleanup_timeout)
        finally:
            self._lock.release()

    def _run(self, request, folder, timeout, cleanup_timeout):
        for duration in (timeout, cleanup_timeout):
            if not isinstance(duration, (int,float)) or not math.isfinite(duration) or duration <= 0:
                raise ValueError('positive_finite_deadline_required')
        request = validate(request.copy())
        folder.mkdir(exist_ok=False)  # exclusive attempt identity; no stale result
        report = {'request_id':request['id'], 'outcome':'not_dispatched',
                  'reply':None, 'cleanup_complete':True, 'errors':[],
                  'channel_reusable':False, 'retry_allowed':False}
        process = None
        launch_attempted = False
        deadline = self.clock() + timeout
        try:
            process = self.context.Process(target=exchange_worker,
                                           args=(self.channel,request,str(folder)))
            if self.clock() >= deadline:
                raise TimeoutError('deadline_before_launch')
            launch_attempted = True
            report['outcome'] = 'uncertain'
            process.start()
            remaining = deadline - self.clock()
            if remaining <= 0:
                raise TimeoutError('exchange_deadline')
            process.join(remaining)
            # Completion at or after cut is late evidence, never a timely reply.
            if self.clock() >= deadline or process.is_alive():
                raise TimeoutError('exchange_deadline')
            if process.exitcode != 0:
                raise RuntimeError('worker_failed')
            path = folder / 'reply.json'
            with path.open('rb') as stream:
                raw = stream.read(MAX_RESULT_BYTES + 1)
            if len(raw) > MAX_RESULT_BYTES:
                raise ValueError('reply_too_large')
            reply = json.loads(raw)
            if set(reply) != {'request_id','gateway_result'} or reply['request_id'] != request['id']:
                raise ValueError('reply_binding')
            if self.clock() >= deadline:
                raise TimeoutError('reply_validation_deadline')
            report['outcome'] = 'reply_observed'
            report['reply'] = reply
        except BaseException as error:
            report['errors'].append({'stage':'exchange','error':repr(error)})
        finally:
            if process is not None and launch_attempted:
                try:
                    # pid may exist even if start raised; never assume no launch.
                    if process.pid is not None:
                        if process.is_alive():
                            report['forced_termination'] = True
                            process.terminate()
                            process.join(cleanup_timeout)
                        report['cleanup_complete'] = not process.is_alive()
                    else:
                        # start without a pid is not proven dispatched or canceled.
                        report['cleanup_complete'] = False
                except BaseException as error:
                    report['cleanup_complete'] = False
                    report['errors'].append({'stage':'cleanup','error':repr(error)})
            report['record_complete'] = True
            try:
                atomic_record(folder / 'supervisor.json', report)
            except BaseException as error:
                report['errors'].append({'stage':'supervisor_record','error':repr(error)})
                report['record_complete'] = False
            else:
                report['record_complete'] = True
        return report
