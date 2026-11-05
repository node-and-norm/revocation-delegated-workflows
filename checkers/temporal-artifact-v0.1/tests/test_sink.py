"""Synthetic-only fixtures: no gateway, Temporal, or sockets are executed."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from temporal_checker.sink import FIXED, inspect_sink

DDL = '''
CREATE TABLE authority(root TEXT PRIMARY KEY,epoch INTEGER,active INTEGER);
CREATE TABLE grants(token TEXT PRIMARY KEY,owner TEXT,root TEXT,epoch INTEGER,scope TEXT,can_delegate INTEGER);
CREATE TABLE tickets(token TEXT PRIMARY KEY,grant_token TEXT,owner TEXT,scope TEXT);
CREATE TABLE events(seq INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT,data TEXT);
CREATE TABLE effects(event_seq INTEGER UNIQUE,effect_key TEXT PRIMARY KEY,payload TEXT,root TEXT,epoch INTEGER);
'''


def fixture(path, fenced=False):
    c = sqlite3.connect(path)
    c.executescript(DDL)
    c.execute('INSERT INTO authority VALUES (?,?,?)', ('rootR', 8 if fenced else 7, 0 if fenced else 1))
    c.executemany('INSERT INTO grants VALUES (?,?,?,?,?,?)', [
        ('parent-0', 'parentP', 'rootR', 7, 'summary:task1', 1),
        ('child-1', 'childC', 'rootR', 7, 'summary:task1', 0)])
    c.execute('INSERT INTO tickets VALUES (?,?,?,?)', ('ticket-1', 'child-1', 'childC', 'summary:task1'))
    def event(kind, data):
        return c.execute('INSERT INTO events(kind,data) VALUES (?,?)', (kind, json.dumps(data))).lastrowid
    def pair(actor, req, kind, result):
        event('receipt', dict(actor=actor, request=req))
        return event(kind, dict(request_id=req['id'], result=dict(outcome=kind, **result)))
    event('bootstrap', dict(root='rootR', epoch=7, parent_grant='parent-0', parent='parentP', child='childC', scope='summary:task1'))
    pair('parentP', dict(id='delegate', op='delegate', claim='parentP', grant='parent-0', scope='summary:task1', child='childC'), 'grant', dict(grant='child-1', owner='childC', root='rootR', epoch=7, scope='summary:task1', parent_grant='parent-0'))
    pair('childC', dict(id='prepare', op='prepare', claim='childC', grant='child-1', scope='summary:task1'), 'admission', dict(ticket='ticket-1', grant='child-1', root='rootR', epoch=7, scope='summary:task1'))
    if fenced:
        pair('controller', dict(id='revoke', op='revoke', claim='controller'), 'revocation', dict(root='rootR', withdrawn_epoch=7, new_epoch=8))
    req = dict(id='execute', op='execute', claim='childC', grant='child-1', ticket='ticket-1', scope='summary:task1', payload='inert summary')
    if fenced:
        pair('childC', req, 'denied', dict(reason='revoked'))
    else:
        seq = pair('childC', req, 'effect', dict(effect_key='summary:task1', payload='inert summary', root='rootR', epoch=7))
        c.execute('INSERT INTO effects VALUES (?,?,?,?,?)', (seq, 'summary:task1', 'inert summary', 'rootR', 7))
    c.commit()
    c.close()


class SinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'sink.sqlite'

    def inspect(self):
        return inspect_sink(self.path, FIXED)

    def mutate(self, sql, args=()):
        with sqlite3.connect(self.path) as c:
            c.execute(sql, args)

    def test_live(self):
        fixture(self.path)
        before = self.path.read_bytes()
        report = self.inspect()
        self.assertTrue(report['usable'], report)
        self.assertEqual(report['facts']['execute_receipts'], 1)
        self.assertEqual(report['facts']['effect_rows'], 1)
        self.assertEqual(self.path.read_bytes(), before)

    def test_fenced(self):
        fixture(self.path, True)
        report = self.inspect()
        self.assertTrue(report['usable'], report)
        self.assertEqual(report['facts']['execute_receipts'], 1)
        self.assertEqual(len(report['facts']['revocations']), 1)
        self.assertEqual(report['facts']['effect_rows'], 0)

    def test_empty_not_usable(self):
        with sqlite3.connect(self.path) as c:
            c.executescript(DDL)
        self.assertFalse(self.inspect()['usable'])

    def test_effect_positive_survives_orphan(self):
        fixture(self.path)
        self.mutate('DELETE FROM events WHERE seq=7')
        report = self.inspect()
        self.assertFalse(report['usable'])
        self.assertEqual(report['facts']['effect_rows'], 1)
        self.assertEqual(report['requirements']['sink.effect_bijection']['status'], 'unsatisfied')

    def test_omitted_effect(self):
        fixture(self.path)
        self.mutate('DELETE FROM effects')
        report = self.inspect()
        self.assertEqual(report['facts']['effect_events'], 1)
        self.assertFalse(report['usable'])

    def test_missing_receipt(self):
        fixture(self.path)
        self.mutate('DELETE FROM events WHERE seq=6')
        report = self.inspect()
        self.assertFalse(report['usable'])
        self.assertEqual(report['facts']['effect_events'], 1)

    def test_bad_payload(self):
        fixture(self.path)
        self.mutate("UPDATE effects SET payload='bad'")
        report = self.inspect()
        self.assertFalse(report['usable'])
        self.assertEqual(report['facts']['effect_rows'], 1)

    def test_wrong_denial(self):
        fixture(self.path, True)
        self.mutate('UPDATE events SET data=? WHERE kind=?', (json.dumps(dict(request_id='execute', result=dict(outcome='denied', reason='invalid_ticket'))), 'denied'))
        self.assertEqual(self.inspect()['requirements']['sink.authorization']['status'], 'unsatisfied')

    def test_authority_disagrees(self):
        fixture(self.path, True)
        self.mutate('UPDATE authority SET epoch=7,active=1')
        self.assertEqual(self.inspect()['requirements']['sink.revocation']['status'], 'unsatisfied')

    def test_request_id_mismatch(self):
        fixture(self.path)
        self.mutate('UPDATE events SET data=? WHERE seq=7', (json.dumps(dict(request_id='other', result=dict(outcome='effect'))),))
        self.assertFalse(self.inspect()['usable'])

    def test_trigger_rejected_without_execution(self):
        fixture(self.path)
        self.mutate('CREATE TRIGGER bad AFTER INSERT ON authority BEGIN DELETE FROM effects; END')
        self.assertEqual(self.inspect()['requirements']['sink.schema']['status'], 'unsatisfied')

    def test_malformed_json_keeps_effect_rows(self):
        fixture(self.path)
        self.mutate("UPDATE events SET data='{bad' WHERE seq=6")
        report = self.inspect()
        self.assertFalse(report['usable'])
        self.assertEqual(report['facts']['effect_rows'], 1)

    def test_duplicate_json_key(self):
        fixture(self.path)
        self.mutate('UPDATE events SET data=? WHERE seq=6', ('{"request":{},"request":{}}',))
        self.assertFalse(self.inspect()['usable'])

    def test_non_database(self):
        self.path.write_text('not sqlite')
        self.assertFalse(self.inspect()['usable'])

    def test_missing_file_not_created(self):
        self.assertFalse(self.inspect()['usable'])
        self.assertFalse(self.path.exists())

    def test_symlink_not_opened(self):
        target = self.path.with_name('target.sqlite')
        fixture(target)
        self.path.symlink_to(target)
        self.assertFalse(self.inspect()['usable'])

    def test_raw_tables_preserved(self):
        fixture(self.path)
        report = self.inspect()
        self.assertIsInstance(report['facts']['tables']['events'][0]['data'], str)
        self.assertIsInstance(report['facts']['events'][0]['data'], dict)

    def test_bool_epoch_rejected(self):
        fixture(self.path)
        self.mutate('UPDATE events SET data=? WHERE seq=1', (json.dumps(dict(root='rootR', epoch=True, parent_grant='parent-0', parent='parentP', child='childC', scope='summary:task1')),))
        self.assertEqual(self.inspect()['requirements']['sink.primitives']['status'], 'unsatisfied')

    def test_wrong_unique_constraint(self):
        with sqlite3.connect(self.path) as c:
            c.executescript(DDL.replace('event_seq INTEGER UNIQUE', 'event_seq INTEGER').replace('payload TEXT', 'payload TEXT UNIQUE'))
        self.assertEqual(self.inspect()['requirements']['sink.schema']['status'], 'unsatisfied')

    def test_row_limit(self):
        with sqlite3.connect(self.path) as c:
            c.executescript(DDL)
            c.executemany('INSERT INTO events(kind,data) VALUES (?,?)', [('bootstrap', '{}')] * 100001)
        self.assertFalse(self.inspect()['usable'])

    def test_duplicate_outcome_and_receipt_count(self):
        fixture(self.path)
        with sqlite3.connect(self.path) as c:
            data = json.loads(c.execute('SELECT data FROM events WHERE seq=6').fetchone()[0])
            data['request']['id'] = 'execute-again'
            c.execute('INSERT INTO events(kind,data) VALUES (?,?)', ('receipt', json.dumps(data)))
            c.execute('INSERT INTO events(kind,data) VALUES (?,?)', ('duplicate', json.dumps(dict(request_id='execute-again', result=dict(outcome='duplicate')))))
        report = self.inspect()
        self.assertTrue(report['usable'], report)
        self.assertEqual(report['facts']['execute_receipts'], 2)
        self.assertEqual(report['facts']['effect_rows'], 1)

    def test_malformed_terminal_object_fails_closed(self):
        fixture(self.path)
        self.mutate('UPDATE events SET data=? WHERE seq=7', ('{"request_id":"execute","result":7}',))
        report = self.inspect()
        self.assertFalse(report['usable'])
        self.assertEqual(report['facts']['effect_rows'], 1)

    def test_bad_scope(self):
        fixture(self.path)
        self.assertFalse(inspect_sink(self.path, dict(FIXED, epoch=8))['usable'])


if __name__ == '__main__':
    unittest.main()
