"""Finite local instrument qualification. Standard library only; no remote actions."""
import argparse
import hashlib
import json
import multiprocessing as mp
import platform
import sqlite3
import sys
import traceback
from pathlib import Path
from oracle import assess

VERSION = '0.1.0'
TIMEOUT = 10

def connect(path):
    c = sqlite3.connect(path, timeout=TIMEOUT, isolation_level=None)
    c.execute('PRAGMA synchronous=FULL')
    return c

def event(c, kind, data):
    return c.execute('INSERT INTO events(kind,data) VALUES (?,?)', (kind, json.dumps(data, sort_keys=True))).lastrowid

def transaction(c, fn):
    c.execute('BEGIN IMMEDIATE')
    try:
        value = fn()
        c.execute('COMMIT')
        return value
    except BaseException:
        c.execute('ROLLBACK')
        raise

def worker(path, arm, pipe):
    try:
        c = connect(path)
        while True:
            command, arg = pipe.recv()
            if command == 'stop':
                c.close(); pipe.send({'ok': True}); return
            if command == 'prepare':
                def prepare():
                    epoch, active = c.execute("SELECT epoch,active FROM authority WHERE root='rootR'").fetchone()
                    allowed = epoch == 7 and active == 1
                    event(c, 'admission', {'root': 'rootR', 'epoch': 7, 'allowed': allowed})
                    event(c, 'prepared', {'effect_key': 'summary:task1', 'payload': 'inert summary'})
                    return {'root': 'rootR', 'epoch': 7, 'allowed': allowed}
                result = transaction(c, prepare)
            elif command == 'attempt':
                attempt, ticket = arg
                transaction(c, lambda: event(c, 'attempt', {'attempt': attempt}))
                def commit_effect():
                    # Full mediation: check and insertion share the SAME write transaction.
                    if arm == 'commit_fenced':
                        current = c.execute('SELECT epoch,active FROM authority WHERE root=?', (ticket['root'],)).fetchone()
                        allowed = current == (ticket['epoch'], 1)
                    else:
                        allowed = ticket['allowed']  # Deliberately stale admission, seeded flaw.
                    if not allowed:
                        event(c, 'denied', {'attempt': attempt}); return 'denied'
                    if c.execute('SELECT 1 FROM effects WHERE effect_key=?', ('summary:task1',)).fetchone():
                        event(c, 'duplicate', {'attempt': attempt}); return 'duplicate'
                    seq = event(c, 'effect', {'attempt': attempt})
                    c.execute('INSERT INTO effects VALUES (?,?,?,?,?)', (seq, 'summary:task1', 'inert summary', ticket['root'], ticket['epoch']))
                    return 'effect'
                result = transaction(c, commit_effect)
            elif command == 'ack':
                attempt, outcome = arg
                result = transaction(c, lambda: event(c, 'ack', {'attempt': attempt, 'outcome': outcome}))
            else:
                raise ValueError(command)
            pipe.send({'ok': True, 'result': result})
    except BaseException:
        pipe.send({'ok': False, 'error': traceback.format_exc()})

def observer(path, pipe):
    """Read-only independent process. Reads actual committed sink rows, not worker claims."""
    try:
        c = sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True, isolation_level=None)
        while True:
            command = pipe.recv()
            if command == 'stop':
                c.close(); pipe.send({'ok': True}); return
            c.execute('BEGIN')
            events = [{'seq': s, 'kind': k, 'data': json.loads(d)} for s, k, d in c.execute('SELECT seq,kind,data FROM events ORDER BY seq')]
            effects = [dict(zip(('event_seq', 'effect_key', 'payload', 'root', 'epoch'), row)) for row in c.execute('SELECT * FROM effects ORDER BY event_seq')]
            row = c.execute('SELECT root,epoch,active FROM authority').fetchone()
            c.execute('COMMIT')
            pipe.send({'ok': True, 'result': {'events': events, 'effects': effects, 'authority': dict(zip(('root', 'epoch', 'active'), row))}})
    except BaseException:
        pipe.send({'ok': False, 'error': traceback.format_exc()})

def launch(ctx, target, *args):
    parent, child = ctx.Pipe()
    p = ctx.Process(target=target, args=(*args, child))
    p.start(); child.close()
    return p, parent

def request(pair, command):
    p, pipe = pair
    pipe.send(command)
    if not pipe.poll(TIMEOUT):
        raise TimeoutError(f'IPC barrier timed out; pid {p.pid}; command {command}')
    response = pipe.recv()
    if not response['ok']:
        raise RuntimeError(response['error'])
    return response.get('result')

def stop(pair, is_observer=False):
    request(pair, 'stop' if is_observer else ('stop', None))
    pair[0].join(TIMEOUT)
    if pair[0].is_alive() or pair[0].exitcode != 0:
        raise RuntimeError('Process did not terminate cleanly')
    pair[1].close()

def run_case(ctx, folder, arm, case):
    path = (folder / f'{arm}_{case}.sqlite3').resolve()
    c = connect(path)
    c.executescript('''CREATE TABLE authority(root TEXT PRIMARY KEY, epoch INTEGER, active INTEGER);
    INSERT INTO authority VALUES ('rootR',7,1);
    CREATE TABLE events(seq INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT,data TEXT);
    CREATE TABLE effects(event_seq INTEGER UNIQUE,effect_key TEXT PRIMARY KEY,payload TEXT,root TEXT,epoch INTEGER);''')
    obs = launch(ctx, observer, path)
    workers = []
    snapshots = []
    def snap(stage):
        snapshots.append({'stage': stage, **request(obs, 'snapshot')})
    try:
        w = launch(ctx, worker, path, arm); workers.append(w)
        ticket = request(w, ('prepare', None)); snap('prepared')
        if case == 'C2':
            stop(w); workers.remove(w)
            w = launch(ctx, worker, path, arm); workers.append(w)
        def revoke():
            def action():
                c.execute("UPDATE authority SET epoch=8,active=0 WHERE root='rootR'")
                event(c, 'revocation', {'root': 'rootR', 'withdrawn_epoch': 7, 'new_epoch': 8})
            transaction(c, action); snap('revocation_committed')
        if case in ('C1', 'C2', 'C3'):
            revoke()
        for attempt in range(1, 4 if case == 'C3' else 2):
            outcome = request(w, ('attempt', (attempt, ticket))); snap(f'outcome_{attempt}_committed')
            if case == 'C4':
                revoke()
            request(w, ('ack', (attempt, outcome))); snap(f'ack_{attempt}')
        final = {'case': case, 'arm': arm, **request(obs, 'snapshot')}
        result = assess(final)
        expected = 'VIOLATION' if arm == 'admission_only' and case in ('C1','C2','C3') else 'NO_VIOLATION'
        expected_effects = 0 if arm == 'commit_fenced' and case in ('C1','C2','C3') else 1
        qualified = result['label'] == expected and result['effects'] == expected_effects
        return {'trace': final, 'snapshots': snapshots, 'oracle': result, 'expected_label': expected, 'expected_effects': expected_effects, 'qualification_pass': qualified}
    finally:
        c.close()
        cleanup_errors = []
        for pair in workers + [obs]:
            try:
                stop(pair, pair is obs)
            except BaseException:
                cleanup_errors.append(traceback.format_exc())
                if pair[0].is_alive(): pair[0].terminate(); pair[0].join(TIMEOUT)
                pair[1].close()
        if cleanup_errors:
            raise RuntimeError('Process cleanup failed: ' + '\n'.join(cleanup_errors))

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True)
    args = parser.parse_args(); folder = Path(args.output)
    folder.mkdir(parents=True, exist_ok=False)  # Never overwrite an earlier attempt.
    metadata = {'version': VERSION, 'python': sys.version, 'sqlite': sqlite3.sqlite_version, 'platform': platform.platform(), 'multiprocessing_start_method': 'spawn', 'timeout_seconds': TIMEOUT, 'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}}
    (folder / 'runtime.json').write_text(json.dumps(metadata, indent=2) + '\n')
    # Preserve exact source used for every attempt, including unsuccessful attempts.
    source_dir = folder / 'source'; source_dir.mkdir()
    for p in Path(__file__).parent.glob('*.py'): (source_dir / p.name).write_bytes(p.read_bytes())
    results = []
    try:
        for arm in ('admission_only', 'commit_fenced'):
            for case in ('C0','C1','C2','C3','C4'):
                r = run_case(mp.get_context('spawn'), folder, arm, case)
                (folder / f'{arm}_{case}.json').write_text(json.dumps(r, indent=2) + '\n')
                results.append({'arm': arm, 'case': case, **r['oracle'], 'qualification_pass': r['qualification_pass']})
        summary = {'status': 'QUALIFIED' if all(r['qualification_pass'] for r in results) else 'FAILED', 'cases': results}
    except BaseException:
        summary = {'status': 'INCOMPLETE', 'cases': results, 'error': traceback.format_exc()}
    (folder / 'results.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return 0 if summary['status'] == 'QUALIFIED' else 1

if __name__ == '__main__':
    raise SystemExit(main())
