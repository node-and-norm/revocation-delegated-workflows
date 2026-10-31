"""Read-only observer process, no gateway/enforcement imports."""
import json
import sqlite3

def observer_main(path,control):
    try:
        c=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True,isolation_level=None)
        while True:
            cmd=control.recv()
            if cmd=='stop': c.close();control.send({'ok':True});return
            c.execute('BEGIN')
            result={}
            result['events']=[{'seq':s,'kind':k,'data':json.loads(d)} for s,k,d in c.execute('SELECT seq,kind,data FROM events ORDER BY seq')]
            for table,fields in [('authority',('root','epoch','active')),('grants',('token','owner','root','epoch','scope','can_delegate')),('tickets',('token','grant_token','owner','scope')),('effects',('event_seq','effect_key','payload','root','epoch'))]:
                result[table]=[dict(zip(fields,row)) for row in c.execute('SELECT * FROM '+table+' ORDER BY 1')]
            c.execute('COMMIT');control.send({'ok':True,'snapshot':result})
    except BaseException as error:
        control.send({'ok':False,'error':repr(error)})
