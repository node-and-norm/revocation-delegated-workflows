"""Bounded orchestrator; workers do not own or access the sink database."""
import argparse
import hashlib
import json
import multiprocessing as mp
import platform
import shutil
import sqlite3
import sys
import traceback
from pathlib import Path
from worker import run_worker
from gateway import gateway_main
from observer import observer_main
from oracle import assess, qualify

TIMEOUT=10
VERSION='0.2.0'

def recv(pipe):
    if not pipe.poll(TIMEOUT):raise TimeoutError('IPC barrier expired')
    result=pipe.recv()
    if isinstance(result,dict) and result.get('ok') is False:raise RuntimeError(str(result))
    return result

def rpc(pipe,req):pipe.send(req);return recv(pipe)

def run_case(folder,arm,case):
    ctx=mp.get_context('spawn');path=(folder/f'{arm}_{case}.sqlite3').resolve()
    gc,gs=ctx.Pipe();pc,ps=ctx.Pipe();cc,cs=ctx.Pipe();pg,pw=ctx.Pipe();cg,cw=ctx.Pipe();dp,dc=ctx.Pipe();oc,os=ctx.Pipe()
    processes=[];snapshots=[];workers={}
    def launch(target,args):
        p=ctx.Process(target=target,args=args);p.start();processes.append(p);return p
    def snapshot(stage):snapshots.append({'stage':stage,**rpc(oc,'snapshot')['snapshot']})
    def worker_request(pipe,request):return rpc(pipe,{'op':'request','request':request})['response']
    def revoke():
        rpc(gc,{'id':'revoke-1','op':'revoke','claim':'controller'});snapshot('revocation_committed')
    try:
        launch(gateway_main,(path,arm,gs,pg,cg));recv(gc)
        launch(run_worker,('parentP',ps,pw,dp));launch(run_worker,('childC',cs,cw,dc))
        launch(observer_main,(path,os));snapshot('bootstrap')
        if case=='C8':revoke()
        delegated=worker_request(pc,{'id':'delegate-1','op':'delegate','claim':'parentP','grant':'parent-0','scope':'other:key' if case=='C7' else 'summary:task1','child':'childC'})
        snapshot('delegation_outcome_committed')
        if case not in ('C7','C8'):
            if delegated['outcome']!='grant':raise RuntimeError('required child grant missing')
            rpc(pc,{'op':'deliver'});rpc(cc,{'op':'receive'})
            prepared=worker_request(cc,{'id':'prepare-1','op':'prepare','claim':'childC','grant':'$child','scope':'summary:task1'})
            if prepared['outcome']!='admission':raise RuntimeError('required preparation missing')
            snapshot('admission_committed')
            if case in ('C1','C3'):revoke()
            for i in range(1,4 if case=='C3' else 2):
                worker_request(cc,{'id':f'execute-{i}','op':'execute','claim':'parentP' if case=='C5' else 'childC','grant':'parent-0' if case=='C6' else '$child','scope':'other:key' if case=='C4' else 'summary:task1','payload':'inert summary','ticket':'ticket-1'})
                snapshot(f'execution_outcome_{i}_committed')
                if case=='C2':revoke()
                worker_request(cc,{'id':f'ack-{i}','op':'ack','claim':'childC','for_request':f'execute-{i}'})
                snapshot(f'explicit_ack_{i}')
        final=rpc(oc,'snapshot')['snapshot']
        workers['parentP']=rpc(pc,{'op':'stop'})['ledger'];workers['childC']=rpc(cc,{'op':'stop'})['ledger']
        rpc(gc,{'op':'stop'});rpc(oc,'stop')
        for p in processes:
            p.join(TIMEOUT)
            if p.is_alive() or p.exitcode!=0:raise RuntimeError('child process not cleanly terminated')
        trace={'case':case,'arm':arm,'snapshot':final,'workers':workers};result=assess(trace);qualification=qualify(trace)
        expected_effects=1 if case in ('C0','C2') or (arm=='admission_only' and case in ('C1','C3')) else 0
        expected_label='VIOLATION' if arm=='admission_only' and case in ('C1','C3') else 'NO_VIOLATION'
        reasons={'C4':'scope_expansion','C5':'caller_mismatch','C6':'foreign_grant','C7':'scope_expansion','C8':'revoked'}
        negatives=[e['data']['result'].get('reason') for e in final['events'] if e['kind']=='denied']
        negative_ok=case not in reasons or negatives==[reasons[case]]
        return {'trace':trace,'snapshots':snapshots,'oracle':result,'expected_effects':expected_effects,'expected_label':expected_label,'qualification':qualification,'qualification_pass':qualification['qualified']}
    finally:
        for p in processes:
            if p.is_alive():p.terminate()
        for p in processes:p.join(TIMEOUT)
        for connection in (gc,gs,pc,ps,cc,cs,pg,pw,cg,cw,dp,dc,oc,os):connection.close()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();folder=Path(args.output);folder.mkdir(parents=True,exist_ok=False)
    sources=sorted(Path(__file__).parent.glob('*.py'));(folder/'source').mkdir()
    for source in sources:shutil.copyfile(source,folder/'source'/source.name)
    metadata={'version':VERSION,'python':sys.version,'sqlite':sqlite3.sqlite_version,'platform':platform.platform(),'start_method':'spawn','timeout_seconds':TIMEOUT,'source_sha256':{s.name:hashlib.sha256(s.read_bytes()).hexdigest() for s in sources}}
    (folder/'runtime.json').write_text(json.dumps(metadata,indent=2)+'\n');results=[]
    try:
        for arm in ('admission_only','commit_fenced'):
            for i in range(9):
                case=f'C{i}';r=run_case(folder,arm,case);(folder/f'{arm}_{case}.json').write_text(json.dumps(r,indent=2)+'\n');results.append({'arm':arm,'case':case,**r['oracle'],'qualification_pass':r['qualification_pass']})
        summary={'status':'QUALIFIED' if all(r['qualification_pass'] for r in results) else 'FAILED','cases':results}
    except BaseException:summary={'status':'INCOMPLETE','cases':results,'error':traceback.format_exc()}
    (folder/'results.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2));return 0 if summary['status']=='QUALIFIED' else 1

if __name__=='__main__':raise SystemExit(main())
