"""Trusted fixture gateway; all sink writes and authorization live here."""
import json
import sqlite3
from multiprocessing.connection import wait

SCOPE='summary:task1'
PAYLOAD='inert summary'

def gateway_main(path, arm, control, parent, child):
    c=sqlite3.connect(path, isolation_level=None, timeout=10)
    c.execute('PRAGMA synchronous=FULL')
    c.executescript('''CREATE TABLE authority(root TEXT PRIMARY KEY,epoch INTEGER,active INTEGER);
    INSERT INTO authority VALUES ('rootR',7,1);
    CREATE TABLE grants(token TEXT PRIMARY KEY,owner TEXT,root TEXT,epoch INTEGER,scope TEXT,can_delegate INTEGER);
    INSERT INTO grants VALUES ('parent-0','parentP','rootR',7,'summary:task1',1);
    CREATE TABLE tickets(token TEXT PRIMARY KEY,grant_token TEXT,owner TEXT,scope TEXT);
    CREATE TABLE events(seq INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT,data TEXT);
    CREATE TABLE effects(event_seq INTEGER UNIQUE,effect_key TEXT PRIMARY KEY,payload TEXT,root TEXT,epoch INTEGER);
    ''')
    def event(kind,data):
        return c.execute('INSERT INTO events(kind,data) VALUES (?,?)',(kind,json.dumps(data,sort_keys=True))).lastrowid
    event('bootstrap',{'root':'rootR','epoch':7,'parent_grant':'parent-0','parent':'parentP','child':'childC','scope':SCOPE})
    control.send({'ok':True})
    channels={parent:'parentP',child:'childC',control:'controller'}
    try:
        while True:
            for channel in wait(list(channels)):
                req=channel.recv(); actor=channels[channel]
                if actor=='controller' and req['op']=='stop':
                    c.close(); channel.send({'ok':True}); return
                c.execute('BEGIN IMMEDIATE')
                try:
                    event('receipt',{'actor':actor,'request':req})
                    result={}; kind='denied'
                    reason=None
                    if req.get('claim') != actor: reason='caller_mismatch'
                    op=req['op']
                    if reason is None and op=='revoke' and actor=='controller':
                        c.execute("UPDATE authority SET epoch=8,active=0 WHERE root='rootR'")
                        kind='revocation';result={'outcome':kind,'root':'rootR','withdrawn_epoch':7,'new_epoch':8}
                    elif reason is None and op=='ack' and actor=='childC':
                        kind='ack';result={'outcome':kind,'for_request':req['for_request']}
                    elif reason is None and op in ('delegate','prepare','execute'):
                        g=c.execute('SELECT owner,root,epoch,scope,can_delegate FROM grants WHERE token=?',(req['grant'],)).fetchone()
                        if g is None: reason='unknown_grant'
                        elif g[0]!=actor: reason='foreign_grant'
                        elif req['scope']!=g[3] or req.get('payload',PAYLOAD)!=PAYLOAD: reason='scope_expansion'
                        if reason is None:
                            state=c.execute('SELECT epoch,active FROM authority WHERE root=?',(g[1],)).fetchone()
                            fresh=state==(g[2],1)
                            if op=='delegate':
                                if not g[4] or req['child']!='childC': reason='delegation_forbidden'
                                elif not fresh: reason='revoked'
                                else:
                                    c.execute('INSERT INTO grants VALUES (?,?,?,?,?,?)',('child-1',req['child'],g[1],g[2],g[3],0))
                                    kind='grant';result={'outcome':kind,'grant':'child-1','owner':'childC','root':g[1],'epoch':g[2],'scope':g[3],'parent_grant':req['grant']}
                            elif op=='prepare':
                                if not fresh: reason='revoked'
                                else:
                                    c.execute('INSERT INTO tickets VALUES (?,?,?,?)',('ticket-1',req['grant'],actor,req['scope']))
                                    kind='admission';result={'outcome':kind,'ticket':'ticket-1','grant':req['grant'],'root':g[1],'epoch':g[2],'scope':req['scope']}
                            else:
                                ticket=c.execute('SELECT grant_token,owner,scope FROM tickets WHERE token=?',(req['ticket'],)).fetchone()
                                if ticket!=(req['grant'],actor,req['scope']): reason='invalid_ticket'
                                elif arm=='commit_fenced' and not fresh: reason='revoked'
                                elif c.execute('SELECT 1 FROM effects WHERE effect_key=?',(req['scope'],)).fetchone():
                                    kind='duplicate';result={'outcome':kind}
                                else:
                                    kind='effect';result={'outcome':kind,'effect_key':req['scope'],'payload':req['payload'],'root':g[1],'epoch':g[2]}
                    elif reason is None:
                        reason='operation_forbidden'
                    if reason:
                        kind='denied';result={'outcome':kind,'reason':reason}
                    seq=event(kind,{'request_id':req['id'],'result':result})
                    if kind=='effect':
                        c.execute('INSERT INTO effects VALUES (?,?,?,?,?)',(seq,result['effect_key'],result['payload'],result['root'],result['epoch']))
                    c.execute('COMMIT')
                    channel.send(result)
                except BaseException:
                    c.execute('ROLLBACK');raise
    except BaseException as error:
        control.send({'ok':False,'error':repr(error)})
        c.close()
