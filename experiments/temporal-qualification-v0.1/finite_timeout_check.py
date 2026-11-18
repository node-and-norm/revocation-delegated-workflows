"""Unexecuted finite timeout-after-receipt check. Run only after separate user approval.

No sockets, VM operations, controller, retries, or unbounded peer hang.
The finite peer waits six seconds without replying; candidate TERM is intended. Spawn and
filesystem/OS calls can block; configured waits are not a hard wall-clock bound.
"""
import argparse
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import time
import sys
import signal

from bounded_exchange import SingleUseExchange
from bridge import FIXED

REQUEST = dict(FIXED, id='finite-timeout-001')


class Endpoint:
    """Spawn-picklable, weak-referenceable adapter over two one-way pipes."""
    def __init__(self, writer, reader):
        self.writer, self.reader = writer, reader

    def send(self, value):
        self.writer.send(value)

    def recv(self):
        return self.reader.recv()

    def close(self):
        try:
            self.writer.close()
        finally:
            self.reader.close()


def peer(reader, writer, record):
    """One receive only. Receipt count is observed, not global exactly-once proof."""
    result = {'received_count': 0, 'request': None, 'reply_sent': False}
    try:
        if not reader.poll(10):
            raise TimeoutError('peer_request_wait')
        value = reader.recv()
        result.update(received_count=1, request=value)
        if value != REQUEST:
            raise ValueError('peer_request_mismatch')
        result['receipt_monotonic'] = time.monotonic()
        # Preserve receipt before the finite wait. No response is ever sent.
        Path(record).write_text(json.dumps(result, sort_keys=True) + '\n')
        result['wait_started_monotonic'] = time.monotonic()
        time.sleep(6)
        result['wait_ended_monotonic'] = time.monotonic()
        result['end_reason'] = 'finite_wait_then_close_without_reply'
        # Finally closes the sole child reply-writer copy without any send.
    except BaseException as error:
        result['error'] = repr(error)
        raise
    finally:
        reader.close()
        writer.close()
        # Plain record: no crash/power-loss durability claim.
        Path(record).write_text(json.dumps(result, sort_keys=True) + '\n')


class OwnedContext:
    """Uses real spawn Processes and retains only this attempt's child handles."""
    def __init__(self, context):
        self.context, self.children = context, []

    def Process(self, **kwargs):
        child = self.context.Process(**kwargs)
        self.children.append(child)
        return child


def cleanup(child):
    state = {'pid': child.pid, 'signals': [], 'reaped': False, 'closed': False}
    try:
        if child.pid is None:
            state['error'] = 'launch_not_confirmed'
            return state
        child.join(2)
        if child.is_alive():
            child.terminate()  # Only this directly owned child, never a group.
            state['signals'].append('TERM')
            child.join(2)
        if child.is_alive():
            child.kill()
            state['signals'].append('KILL')
            child.join(2)
        state['exitcode'] = child.exitcode
        state['reaped'] = not child.is_alive() and child.exitcode is not None
        if state['reaped']:
            child.close()
            state['closed'] = True
    except BaseException as error:
        state['error'] = repr(error)
    return state


def run(folder):
    folder.mkdir(exist_ok=False)  # Never overwrite or resume an attempt.
    source_hashes = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                     for name in ('finite_timeout_check.py', 'bounded_exchange.py', 'bridge.py')}
    summary = {'scope': 'one finite timeout-after-receipt anonymous-pipe check',
               'python': sys.version, 'executable': sys.executable,
               'source_sha256': source_hashes, 'started_monotonic': time.monotonic(),
               'exchange': None, 'peer_record': None, 'errors': [],
               'cleanup': [], 'record_complete': False, 'pass': False}
    context = mp.get_context('spawn')
    owned = OwnedContext(context)
    endpoints = []
    peer_child = None
    try:
        request_reader, request_writer = context.Pipe(duplex=False)
        endpoints.extend((request_reader, request_writer))
        reply_reader, reply_writer = context.Pipe(duplex=False)
        endpoints.extend((reply_reader, reply_writer))
        endpoint = Endpoint(request_writer, reply_reader)
        peer_child = owned.Process(target=peer,
            args=(request_reader, reply_writer, str(folder / 'peer.json')))
        peer_child.start()
        # Spawn duplicates only the peer's supplied endpoints; originals close.
        request_reader.close()
        reply_writer.close()
        summary['exchange_call_started_monotonic'] = time.monotonic()
        summary['exchange'] = SingleUseExchange(endpoint, context=owned).run(
            REQUEST, folder / 'exchange', timeout=5, cleanup_timeout=2)
        summary['exchange_call_ended_monotonic'] = time.monotonic()
    except BaseException as error:
        summary['errors'].append(repr(error))
    finally:
        # Finish owned-child teardown attempts before retiring parent originals.
        for child in reversed(owned.children[1:]):
            summary['cleanup'].append(cleanup(child))
        # If a child is unresolved, closing our duplicate is NOT its teardown.
        # Close all parent duplicates even after partial launch or pipe failure.
        for connection in endpoints:
            try:
                connection.close()
            except BaseException as error:
                summary['errors'].append('close: ' + repr(error))
        if owned.children:
            summary['cleanup'].append(cleanup(owned.children[0]))
    try:
        with (folder / 'peer.json').open('rb') as stream:
            raw = stream.read(4097)
        if len(raw) > 4096:
            raise ValueError('peer_record_oversize')
        summary['peer_record'] = json.loads(raw)
        peer_record = summary['peer_record']
        peer_ok = (set(peer_record) == {'received_count', 'request', 'reply_sent',
            'receipt_monotonic', 'wait_started_monotonic', 'wait_ended_monotonic', 'end_reason'} and
            peer_record['received_count'] == 1 and peer_record['request'] == REQUEST and
            peer_record['reply_sent'] is False and
            peer_record['end_reason'] == 'finite_wait_then_close_without_reply' and
            peer_record['wait_started_monotonic'] >= peer_record['receipt_monotonic'] and
            peer_record['wait_ended_monotonic'] - peer_record['wait_started_monotonic'] >= 6 and
            peer_record['wait_started_monotonic'] < summary['exchange_call_started_monotonic'] + 5 and
            peer_record['wait_ended_monotonic'] >= summary['exchange_call_ended_monotonic'])
        exchange = summary['exchange'] or {}
        records = {}
        for name in ('dispatch_intent', 'supervisor'):
            with (folder / 'exchange' / (name + '.json')).open('rb') as stream:
                data = stream.read(65537)
            if len(data) > 65536:
                raise ValueError('candidate_record_oversize')
            records[name] = json.loads(data)
        summary['saved_records_match'] = (
            records['dispatch_intent'] == {'request_id': REQUEST['id']} and
            records['supervisor'] == exchange)
        summary['pass'] = bool(peer_ok and not summary['errors'] and
            summary['saved_records_match'] and
            exchange.get('outcome') == 'uncertain' and
            exchange.get('reply') is None and
            exchange.get('errors') == [{'stage': 'exchange', 'error': "TimeoutError('exchange_deadline')"}] and
            not (folder / 'exchange' / 'reply.json').exists() and
            exchange.get('record_complete') is True and
            exchange.get('cleanup_complete') is True and
            exchange.get('forced_termination') is True and
            len(summary['cleanup']) == 2 and
            [c.get('exitcode') for c in summary['cleanup']] == [-signal.SIGTERM, 0] and all(
                c.get('reaped') and c.get('closed') and
                not c.get('signals') and not c.get('error') for c in summary['cleanup']))
    except BaseException as error:
        summary['errors'].append('review: ' + repr(error))
    summary['ended_monotonic'] = time.monotonic()
    summary['record_complete'] = True
    try:
        (folder / 'summary.json').write_text(json.dumps(summary, sort_keys=True, indent=2) + '\n')
    except BaseException as error:
        summary['record_complete'] = False
        summary['pass'] = False
        summary['errors'].append('summary_write: ' + repr(error))
    print(json.dumps(summary, sort_keys=True, indent=2), flush=True)
    return 0 if summary['pass'] else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--approved-single-finite-timeout-check', action='store_true')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if not args.approved_single_finite_timeout_check:
        parser.error('separate user approval required before execution')
    raise SystemExit(run(Path(args.output)))
