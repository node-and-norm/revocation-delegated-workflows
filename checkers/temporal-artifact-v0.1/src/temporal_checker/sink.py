"""Read-only accounting of the pinned gateway's saved SQLite format.

This validates a saved ledger, not its completeness or producer authenticity.
Even a usable ledger cannot by itself support absence during a capture window.
No gateway modules are imported or executed.
"""
from contextlib import closing
from pathlib import Path
import json
import sqlite3

RULES = ('readable', 'schema', 'primitives', 'event_accounting',
         'effect_bijection', 'scope', 'authorization', 'revocation')
FIXED = dict(root='rootR', epoch=7, scope='summary:task1', actor='childC',
             grant='child-1', ticket='ticket-1', payload='inert summary')
SCHEMA = {
    'authority': [('root', 'TEXT', 1), ('epoch', 'INTEGER', 0), ('active', 'INTEGER', 0)],
    'grants': [('token', 'TEXT', 1), ('owner', 'TEXT', 0), ('root', 'TEXT', 0),
               ('epoch', 'INTEGER', 0), ('scope', 'TEXT', 0), ('can_delegate', 'INTEGER', 0)],
    'tickets': [('token', 'TEXT', 1), ('grant_token', 'TEXT', 0), ('owner', 'TEXT', 0), ('scope', 'TEXT', 0)],
    'events': [('seq', 'INTEGER', 1), ('kind', 'TEXT', 0), ('data', 'TEXT', 0)],
    'effects': [('event_seq', 'INTEGER', 0), ('effect_key', 'TEXT', 1), ('payload', 'TEXT', 0), ('root', 'TEXT', 0), ('epoch', 'INTEGER', 0)],
}
# All SQL identifiers are hard-coded, never obtained from artifacts.
QUERIES = {name: 'SELECT * FROM ' + name for name in SCHEMA}
PRAGMAS = {name: 'PRAGMA table_xinfo(' + name + ')' for name in SCHEMA}
INDEXES = {name: 'PRAGMA index_list(' + name + ')' for name in SCHEMA}


def _json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def constant(value):
        raise ValueError('nonfinite JSON')
    result = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    def check(value):
        if type(value) is dict:
            for nested in value.values():
                check(nested)
        elif type(value) not in (str, int):
            raise ValueError('Unsupported gateway JSON primitive')
    check(result)
    return result


def inspect_sink(path: Path, authority_scope: dict) -> dict:
    """Return independent requirements and positive facts; never mutate ``path``."""
    requirements = {f'sink.{rule}': dict(status='unobserved', reason='Not checked.', evidence_refs=[])
                    for rule in RULES}
    facts = dict(execute_receipts=0, effect_rows=0, effect_events=0, denials=[],
                 revocations=[], execute_request_ids=[], effects=[], events=[], tables={})
    answer = dict(requirements=requirements, facts=facts, usable=False)

    def mark(rule, ok, reason, refs=None):
        requirements['sink.' + rule] = dict(status='satisfied' if ok else 'unsatisfied',
                                           reason=reason, evidence_refs=refs or ['sink.sqlite'])
    try:
        if not isinstance(path, Path) or not path.is_file() or path.is_symlink():
            raise ValueError('Sink must be an existing regular, non-symlink file.')
        if authority_scope != FIXED or type(authority_scope.get('epoch')) is not int:
            raise ValueError('Unsupported authority scope; the adapter is pinned to the fixture.')
        uri = path.resolve().as_uri() + '?mode=ro&immutable=1'
        with closing(sqlite3.connect(uri, uri=True)) as conn:
            conn.execute('PRAGMA query_only=ON')
            conn.execute('PRAGMA trusted_schema=OFF')
            conn.execute('BEGIN')
            catalog = conn.execute('SELECT type,name,tbl_name,sql FROM sqlite_master').fetchall()
            mark('readable', True, 'Opened the saved database read-only and immutable.')
            schema_errors = []
            if {r[1] for r in catalog if r[0] == 'table'} != set(SCHEMA) | {'sqlite_sequence'}:
                schema_errors.append('Unexpected or missing tables.')
            if any(r[0] not in ('table', 'index') or (r[0] == 'index' and r[3] is not None) for r in catalog):
                schema_errors.append('Views, triggers, or noncanonical indexes present.')
            for name, expected in SCHEMA.items():
                actual = conn.execute(PRAGMAS[name]).fetchall()
                if [(r[1], r[2], r[5]) for r in actual] != expected or any(r[3] != 0 or r[4] is not None or r[6] != 0 for r in actual):
                    schema_errors.append('Invalid schema for ' + name + '.')
            # Compare actual constraint columns, not merely the number of indexes.
            expected_indexes = {'authority': {('root',)}, 'grants': {('token',)},
                                'tickets': {('token',)}, 'events': set(),
                                'effects': {('event_seq',), ('effect_key',)}}
            for name in SCHEMA:
                indexes = conn.execute(INDEXES[name]).fetchall()
                actual_indexes = set()
                for index in indexes:
                    columns = conn.execute('SELECT name FROM pragma_index_info(?) ORDER BY seqno', (index[1],)).fetchall()
                    actual_indexes.add(tuple(col[0] for col in columns))
                    if index[2] != 1 or index[4] != 0:
                        schema_errors.append('Invalid index constraint.')
                if actual_indexes != expected_indexes[name] or len(indexes) != len(actual_indexes):
                    schema_errors.append('Invalid unique constraints for ' + name + '.')
            for row in catalog:
                if row[0] == 'table' and row[1] in SCHEMA:
                    sql = row[3].lower() if isinstance(row[3], str) else ''
                    if row[1] == 'events' and 'autoincrement' not in sql:
                        schema_errors.append('Events AUTOINCREMENT is missing.')
                    if any(word in sql for word in ('virtual', 'check', 'references', 'collate', 'without', 'strict')):
                        schema_errors.append('Noncanonical table semantics.')
            mark('schema', not schema_errors, ' '.join(schema_errors) or 'Pinned table structure and passive schema verified.')
            # Never query a view or a table with an incompatible shape.
            if schema_errors:
                return answer
            tables = {}
            total = 0
            for name in SCHEMA:
                rows = conn.execute(QUERIES[name]).fetchmany(100001)
                total += len(rows)
                if total > 100000:
                    raise ValueError('Saved sink exceeds 100000-row adapter limit.')
                tables[name] = [dict(zip([col[0] for col in SCHEMA[name]], row)) for row in rows]
    except (OSError, sqlite3.Error, ValueError, TypeError, UnicodeError) as exc:
        mark('readable', False, 'Saved sink cannot be safely read: ' + str(exc))
        return answer

    facts['tables'] = tables
    facts['effects'] = tables['effects']
    facts['effect_rows'] = len(tables['effects'])
    errors = []
    for name, rows in tables.items():
        for row in rows:
            if any(type(row[key]) is not (int if kind == 'INTEGER' else str) for key, kind, _ in SCHEMA[name]):
                errors.append('Invalid primitive in ' + name + '.')
    for row in tables['events']:
        data = None
        try:
            data = _json(row['data'])
            if not isinstance(data, dict):
                raise ValueError('Event data is not an object.')
        except (ValueError, TypeError, RecursionError):
            errors.append('Malformed event JSON.')
        ev = dict(seq=row['seq'], kind=row['kind'], data=data)
        facts['events'].append(ev)
        if ev['kind'] == 'effect':
            facts['effect_events'] += 1
        elif ev['kind'] == 'denied':
            facts['denials'].append(ev)
        elif ev['kind'] == 'revocation':
            facts['revocations'].append(ev)
        if ev['kind'] == 'receipt' and isinstance(data, dict) and isinstance(data.get('request'), dict) and data['request'].get('op') == 'execute':
            facts['execute_receipts'] += 1
            facts['execute_request_ids'].append(data['request'].get('id'))
    mark('primitives', not errors, ' '.join(errors) or 'SQL and JSON primitive types verified.')
    if errors:
        return answer
    events = sorted(facts['events'], key=lambda ev: ev['seq'])
    accounting, scope_errors, auth_errors, revoke_errors = [], [], [], []
    bootstrap = dict(root='rootR', epoch=7, parent_grant='parent-0', parent='parentP', child='childC', scope='summary:task1')
    if not events or events[0] != dict(seq=1, kind='bootstrap', data=bootstrap):
        accounting.append('Missing or invalid initial bootstrap.')
    if [e['seq'] for e in events] != list(range(1, len(events) + 1)):
        accounting.append('Event sequence has gaps or invalid positions.')
    pairs = []
    for i in range(1, len(events), 2):
        receipt = events[i]
        terminal = events[i + 1] if i + 1 < len(events) else None
        data = receipt['data']
        req = data.get('request')
        valid_receipt = (receipt['kind'] == 'receipt' and set(data) == {'actor', 'request'}
                         and type(data.get('actor')) is str and isinstance(req, dict)
                         and type(req.get('id')) is str and bool(req['id']) and type(req.get('op')) is str)
        if not valid_receipt or terminal is None:
            accounting.append('Receipt/terminal pairing is missing or malformed.')
            continue
        td = terminal['data']
        if (set(td) != {'request_id', 'result'} or td.get('request_id') != req['id']
                or not isinstance(td.get('result'), dict) or td['result'].get('outcome') != terminal['kind']
                or terminal['kind'] not in {'grant', 'admission', 'effect', 'duplicate', 'denied', 'revocation', 'ack'}):
            accounting.append('Terminal does not match its adjacent receipt.')
            continue
        pairs.append((receipt, terminal))
    ids = [r['data']['request']['id'] for r, _ in pairs]
    if len(ids) != len(set(ids)):
        accounting.append('Duplicate request identity.')
    granted = admitted = revoked = effected = False
    expected_grants = [dict(token='parent-0', owner='parentP', root='rootR', epoch=7, scope='summary:task1', can_delegate=1)]
    expected_tickets = []
    for receipt, terminal in pairs:
        req, actor = receipt['data']['request'], receipt['data']['actor']
        kind, result, op = terminal['kind'], terminal['data']['result'], req['op']
        if req.get('claim') != actor:
            auth_errors.append('Request claim differs from gateway actor.')
        if op == 'delegate':
            expected = dict(outcome='grant', grant='child-1', owner='childC', root='rootR', epoch=7, scope='summary:task1', parent_grant='parent-0')
            valid = actor == 'parentP' and req.get('grant') == 'parent-0' and req.get('scope') == FIXED['scope'] and req.get('child') == 'childC'
            if kind == 'grant' and valid and result == expected and not revoked and not granted:
                granted = True
                expected_grants.append(dict(token='child-1', owner='childC', root='rootR', epoch=7, scope='summary:task1', can_delegate=0))
            else:
                auth_errors.append('Invalid grant setup or outcome.')
        elif op == 'prepare':
            expected = dict(outcome='admission', ticket='ticket-1', grant='child-1', root='rootR', epoch=7, scope='summary:task1')
            if (kind == 'admission' and result == expected and granted and not admitted and not revoked
                    and actor == 'childC' and req.get('grant') == 'child-1' and req.get('scope') == FIXED['scope']):
                admitted = True
                expected_tickets.append(dict(token='ticket-1', grant_token='child-1', owner='childC', scope='summary:task1'))
            else:
                auth_errors.append('Invalid admission setup or outcome.')
        elif op == 'execute':
            if not (granted and admitted and actor == 'childC' and all(req.get(k) == FIXED[k] for k in ('grant', 'ticket', 'scope', 'payload'))):
                auth_errors.append('Execute lacks matching prior grant/admission or exact request scope.')
            if kind == 'effect':
                expected = dict(outcome='effect', effect_key=FIXED['scope'], payload=FIXED['payload'], root='rootR', epoch=7)
                if result != expected or effected:
                    scope_errors.append('Effect payload/scope/root/epoch or uniqueness differs.')
                effected = True
            elif kind == 'duplicate':
                if result != {'outcome': 'duplicate'} or not effected:
                    accounting.append('Duplicate outcome has no preceding effect.')
            elif kind == 'denied':
                if result != {'outcome': 'denied', 'reason': 'revoked'} or not revoked:
                    auth_errors.append('Execute denial is not supported by a prior revocation of valid authorization.')
            else:
                accounting.append('Execute has a non-execute terminal.')
        elif op == 'revoke':
            expected = dict(outcome='revocation', root='rootR', withdrawn_epoch=7, new_epoch=8)
            if kind != 'revocation' or result != expected or actor != 'controller' or revoked or not admitted:
                revoke_errors.append('Invalid revocation transition or missing prior admission.')
            else:
                revoked = True
        elif op == 'ack':
            if actor != 'childC' or result != dict(outcome='ack', for_request=req.get('for_request')) or type(req.get('for_request')) is not str:
                accounting.append('Invalid acknowledgment.')
        else:
            accounting.append('Unknown operation.')
    # Enforce closed request shapes, including no hidden semantic extensions.
    shapes = {'delegate': {'grant', 'scope', 'child'}, 'prepare': {'grant', 'scope'},
              'execute': {'grant', 'scope', 'ticket', 'payload'}, 'revoke': set(), 'ack': {'for_request'}}
    for receipt, _ in pairs:
        req = receipt['data']['request']
        if req['op'] in shapes and set(req) != shapes[req['op']] | {'id', 'op', 'claim'}:
            accounting.append('Unknown or missing request fields.')
    if sorted(tables['grants'], key=lambda r: r['token']) != sorted(expected_grants, key=lambda r: r['token']) or tables['tickets'] != expected_tickets:
        auth_errors.append('Grant/ticket tables disagree with setup events.')
    expected_authority = [dict(root='rootR', epoch=8 if revoked else 7, active=0 if revoked else 1)]
    if tables['authority'] != expected_authority:
        revoke_errors.append('Authority state disagrees with committed revocation history.')
    effect_events = [e for e in events if e['kind'] == 'effect']
    expected_rows = []
    for ev in effect_events:
        result = ev['data'].get('result', {})
        if not isinstance(result, dict):
            result = {}
        expected_rows.append(dict(event_seq=ev['seq'], **{k: result.get(k) for k in ('effect_key', 'payload', 'root', 'epoch')}))
    bijective = sorted(tables['effects'], key=lambda r: r['event_seq']) == sorted(expected_rows, key=lambda r: r['event_seq'])
    for row in tables['effects']:
        if any(row[k] != FIXED[k] for k in ('payload', 'root', 'epoch')) or row['effect_key'] != FIXED['scope']:
            scope_errors.append('Stored effect differs from pinned authority scope.')
    mark('event_accounting', not accounting, ' '.join(accounting) or 'Every receipt has one adjacent terminal and every terminal has one receipt.')
    mark('effect_bijection', bijective, 'Effects rows and effect events match bijectively.' if bijective else 'Orphan, omitted, duplicate, or inconsistent effect row/event.')
    mark('scope', not scope_errors, ' '.join(scope_errors) or 'Effect scope and payload match the pinned fixture.')
    mark('authorization', not auth_errors, ' '.join(auth_errors) or 'Authorization setup, request identities, and tables agree.')
    mark('revocation', not revoke_errors, ' '.join(revoke_errors) or 'Revocation transition and final authority state agree.')
    answer['usable'] = all(v['status'] == 'satisfied' for v in requirements.values())
    return answer
