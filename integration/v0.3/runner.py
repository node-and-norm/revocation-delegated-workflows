"""Trusted controller, isolated worker process, immutable historical gateway."""
import argparse, hashlib, json, multiprocessing as mp, os, sqlite3, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent.parent/'qualification'/'v0.2'))
from gateway import gateway_main
from workflow import worker, execute, BINDING, ARGS
CTX=mp.get_context('spawn')

def call(pipe,req):
    pipe.send(req)
    if not pipe.poll(30): raise TimeoutError(req)
    return pipe.recv()

def spawn_worker(db,phase,pending,child):
    out,inside=CTX.Pipe()
    proc=CTX.Process(target=worker,args=(str(db),phase,pending,child,inside))
    proc.start()
    if not out.poll(60):
        proc.terminate();proc.join();raise TimeoutError('worker')
    result=out.recv();proc.join(15)
    if proc.is_alive():proc.terminate();proc.join()
    result['exitcode']=proc.exitcode
    (Path(db).parent/f'worker_{phase}.json').write_text(json.dumps(result,indent=2))
    assert result['ok'],result
    assert proc.exitcode==0,result
    return result

def snapshot(path):
    with sqlite3.connect(f'file:{path}?mode=ro',uri=True) as c:
        c.row_factory=sqlite3.Row
        data={table:[dict(x) for x in c.execute('SELECT * FROM '+table)] for table in ('authority','grants','tickets','events','effects')}
    for e in data['events']:e['data']=json.loads(e['data'])
    return data

def run_case(root,path,prior,revoked):
    name=f'{path}_prior{int(prior)}_revoked{int(revoked)}'; folder=root/name;folder.mkdir()
    control,cg=CTX.Pipe();parent,pg=CTX.Pipe();child,ch=CTX.Pipe()
    proc=CTX.Process(target=gateway_main,args=(str(folder/'sink.sqlite'),'commit_fenced',cg,pg,ch));proc.start()
    assert control.poll(20) and control.recv()=={'ok':True}
    record={'name':name,'path':path,'prior':prior,'revoked':revoked,'gateway_pid':proc.pid,'binding':BINDING,'workers':[],'trace':[],'protocol_sha256':hashlib.sha256((HERE/'PROTOCOL.md').read_bytes()).hexdigest()}
    try:
        record['grant']=call(parent,{'id':'delegate','op':'delegate','claim':'parentP','grant':'parent-0','scope':'summary:task1','child':'childC'})
        record['admission']=call(child,{'id':'prepare','op':'prepare','claim':'childC','grant':'child-1','scope':'summary:task1'})
        assert record['grant']['outcome']=='grant' and record['admission']['outcome']=='admission'
        pending=[]
        if path=='framework':
            first=spawn_worker(folder/'checkpoint.sqlite','pause',None,child);record['workers'].append(first);pending=first['pending']
            assert pending and not snapshot(folder/'sink.sqlite')['effects']
        if prior:record['prior_result']=json.loads(execute(child,ARGS,'prior-execute',record['trace']))
        if revoked:record['revocation']=call(control,{'id':'revoke','op':'revoke','claim':'controller'})
        if path=='framework':
            resumed=spawn_worker(folder/'checkpoint.sqlite','resume',pending,child);record['workers'].append(resumed)
        else:record['final']=json.loads(execute(child,ARGS,'resume-execute',record['trace']))
        record['gateway_alive_after_resume']=proc.is_alive()
    finally:
        if proc.is_alive():record['stop']=call(control,{'op':'stop'})
        proc.join(15)
        record['gateway_exitcode']=proc.exitcode
        record['sink']=snapshot(folder/'sink.sqlite')
        (folder/'record.json').write_text(json.dumps(record,indent=2))
    return record

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--qualification',action='store_true');args=parser.parse_args()
    root=Path(args.output);root.mkdir(parents=True,exist_ok=False)
    if args.qualification:cases=[('framework',False,False)]
    else:cases=[(p,h,r) for p in ('direct','framework') for h in (False,True) for r in (False,True)]
    for p,h,r in cases:
        record=run_case(root,p,h,r);print(record['name'], 'recorded',flush=True)
