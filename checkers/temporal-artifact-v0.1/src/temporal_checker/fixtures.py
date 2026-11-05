"""Synthetic saved-artifact constructors only. These never run the gateway."""
from __future__ import annotations
import json
import sqlite3
import uuid
from pathlib import Path
from copy import deepcopy
from collections import defaultdict
from .artifacts import VERSION, digest, canonical, Bundle
from .schema import BUDGETS
from .sink import FIXED
from .engine import check_bundle, inspect_sink
from .views import expected_view, caller_reference

DDL='''CREATE TABLE authority(root TEXT PRIMARY KEY,epoch INTEGER,active INTEGER);
CREATE TABLE grants(token TEXT PRIMARY KEY,owner TEXT,root TEXT,epoch INTEGER,scope TEXT,can_delegate INTEGER);
CREATE TABLE tickets(token TEXT PRIMARY KEY,grant_token TEXT,owner TEXT,scope TEXT);
CREATE TABLE events(seq INTEGER PRIMARY KEY AUTOINCREMENT,kind TEXT,data TEXT);
CREATE TABLE effects(event_seq INTEGER UNIQUE,effect_key TEXT PRIMARY KEY,payload TEXT,root TEXT,epoch INTEGER);'''


def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+'\n')


def write_jsonl(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(canonical(x)+'\n' for x in rows))


def make_sink(path,cell):
    path.parent.mkdir(parents=True,exist_ok=True)
    conn=sqlite3.connect(path); conn.executescript(DDL)
    fenced=cell in ('M3','M4','K2')
    conn.execute('INSERT INTO authority VALUES(?,?,?)',('rootR',8 if fenced else 7,0 if fenced else 1))
    conn.executemany('INSERT INTO grants VALUES(?,?,?,?,?,?)',[('parent-0','parentP','rootR',7,'summary:task1',1),('child-1','childC','rootR',7,'summary:task1',0)])
    conn.execute('INSERT INTO tickets VALUES(?,?,?,?)',('ticket-1','child-1','childC','summary:task1'))
    def event(kind,data): return conn.execute('INSERT INTO events(kind,data) VALUES(?,?)',(kind,canonical(data))).lastrowid
    def pair(actor,request,kind,result):
        event('receipt',{'actor':actor,'request':request})
        return event(kind,{'request_id':request['id'],'result':{'outcome':kind,**result}})
    event('bootstrap',dict(root='rootR',epoch=7,parent_grant='parent-0',parent='parentP',child='childC',scope='summary:task1'))
    pair('parentP',dict(id='delegate',op='delegate',claim='parentP',grant='parent-0',scope='summary:task1',child='childC'),'grant',dict(grant='child-1',owner='childC',root='rootR',epoch=7,scope='summary:task1',parent_grant='parent-0'))
    pair('childC',dict(id='prepare',op='prepare',claim='childC',grant='child-1',scope='summary:task1'),'admission',dict(ticket='ticket-1',grant='child-1',root='rootR',epoch=7,scope='summary:task1'))
    if fenced: pair('controller',dict(id='revoke',op='revoke',claim='controller'),'revocation',dict(root='rootR',withdrawn_epoch=7,new_epoch=8))
    if cell!='C1':
        execute=dict(id='execute',op='execute',claim='childC',grant='child-1',scope='summary:task1',ticket='ticket-1',payload='inert summary')
        if fenced: pair('childC',execute,'denied',dict(reason='revoked'))
        else:
            seq=pair('childC',execute,'effect',dict(effect_key='summary:task1',payload='inert summary',root='rootR',epoch=7))
            conn.execute('INSERT INTO effects VALUES(?,?,?,?,?)',(seq,'summary:task1','inert summary','rootR',7))
    conn.commit(); conn.close()


def seal(root,entries):
    manifest=[]
    for aid,path,role,phase in entries:
        data=(root/path).read_bytes()
        manifest.append(dict(artifact_id=aid,path=path,role=role,phase=phase,schema_version=VERSION,
                             byte_length=len(data),sha256=digest(data),producer='synthetic_fixture'))
    write_json(root/'registry.json',{'schema_version':VERSION,'artifacts':manifest})


def reseal(root):
    registry=json.loads((root/'registry.json').read_text())
    for e in registry['artifacts']:
        data=(root/e['path']).read_bytes();e['byte_length']=len(data);e['sha256']=digest(data)
    write_json(root/'registry.json',registry)


def create_fixture(root,cell='M1',mode=None,views=True):
    root=Path(root); root.mkdir(parents=True,exist_ok=True)
    if any(root.iterdir()): raise ValueError('Fixture destination must be fresh')
    native=cell not in ('K1','K2'); phases=['P1','P2'] if native else ['P1']
    mode=mode or ('WAIT_CANCELLATION_COMPLETED' if cell in ('M2','M4') else 'TRY_CANCEL')
    binding=dict(workflow_id='workflow-1',run_id='run-1',activity_id='activity-1',scheduled_event_id='2',started_event_id='3',attempt=1,mode=mode) if native else {}
    case=dict(schema_version=VERSION,protocol_version='0.3',case_id='case-'+uuid.uuid4().hex,operation_id='operation-1',case_kind='native_activity' if native else 'sink_only',cell=cell,study_phase='synthetic',origin='synthetic',attempt_id='attempt-'+uuid.uuid4().hex,pins=dict(sdk='1.25.0',gateway_sha256='98445edd61af21bc5c740053f8a93f6c179e4c5efa7b28dd7363e779b8f059a9',native_adapter='synthetic-normalized-v1',exporter_status='unqualified'),intended_binding={k:binding[k] for k in ('workflow_id','activity_id')} if native else {},configuration=dict(mode=mode if native else None,behavior={'M1':'continue','M2':'continue','M3':'continue_fenced','M4':'continue_fenced','K1':'sink_live','K2':'sink_fenced','C1':'cooperative','C4':'historical'}[cell],maximum_attempts=1 if native else None,activity_scope='cancellable_root' if native else None,hold_scope='non_cancellable_observation_only' if native else None,deadlines={k:None for k in BUDGETS}),authority_scope=FIXED,phases=phases,view_permissions=dict(sink=True,fence_receipt=True,client=True,worker=True,native=True,bridge=True),mapping=None,registered_before_dispatch=True)
    observed=dict(schema_version=VERSION,case_id=case['case_id'],operation_id=case['operation_id'],native=binding,launch_ref='native:1' if native else None,start_ref='native:3' if native else None)
    entries=[('case','case.json','case','P0'),('binding','observed_binding.json','binding','P0'),('events','producer_events.jsonl','events','P0')]
    write_json(root/'case.json',case);write_json(root/'observed_binding.json',observed)
    events=[];seq=defaultdict(int)
    def event(kind,producer='worker',payload=None,parents=(),phase='P1'):
        seq[producer]+=1;rid=producer+'-'+str(seq[producer])
        events.append(dict(record_id=rid,producer_id=producer,sequence=seq[producer],case_id=case['case_id'],operation_id=case['operation_id'],phase=phase,kind=kind,payload=payload or {},parents=list(parents),binding=binding,wall_clock=1000-len(events)))
        return rid
    def dispatch(parent=()):
        intended=event('dispatch_intended','bridge',{'request_id':'execute'},parent)
        started=event('dispatch_started','bridge',{'request_id':'execute'},[intended])
        return started
    started=event('activity_started',parents=['native:3']) if native else None
    if cell=='C4':
        dispatch([started]);response=event('bridge_response','bridge',{'request_id':'execute','result':{'outcome':'effect'}},['sink:7'])
        ack=event('effect_ack',payload={'request_id':'execute','sink_seq':7},parents=[response]);coordinator=event('coordinator_ack','controller',{'request_id':'execute'},[ack]);hold=event('activity_hold_ready',parents=[ack]);prior=[coordinator,hold]
    else: prior=[started] if native else []
    if native:
        invocation=event('cancel_invoked','client',{'call_id':'cancel-1'},prior)
        submitted=event('cancel_submitted','client',{'call_id':'cancel-1'},[invocation])
        event('cancel_response','client',{'call_id':'cancel-1','outcome':'response_received','details':{}},[submitted])
        observed_cancel=event('cancellation_observed',payload={'call_id':'cancel-1'},parents=[submitted])
        prior=[observed_cancel]
    if cell in ('M3','M4','K2'):
        event('revocation_invoked','controller',{'request_id':'revoke'},prior)
        fence=event('fence_receipt','controller',dict(request_id='revoke',sink_seq=7,root='rootR',withdrawn_epoch=7,new_epoch=8),['sink:7'])
        prior=[fence]
    if cell in ('M1','M2','M3','M4'):
        release=event('continuation_release','controller',{'release_id':'continue-1'},prior)
        received=event('continuation_received',payload={'release_id':'continue-1'},parents=[release]);prior=[received]
    if cell not in ('C1','C4'):
        dispatch(prior)
        response=event('bridge_response','bridge',{'request_id':'execute','result':{'outcome':'denied','reason':'revoked'} if cell in ('M3','M4','K2') else {'outcome':'effect'}},['sink:'+str(9 if cell in ('M3','M4','K2') else 7)])
        prior=[response]
    if native:
        final=event('finally_point',parents=prior)
        settled=event('worker_settled',payload={'disposition':'result','details':{'synthetic':True}},parents=[final])
        promise=event('promise_settled','workflow',{'disposition':'result','details':{'synthetic':True}},[settled])
        event('workflow_hold','workflow',parents=[promise])
    for phase in phases:
        if phase=='P2':
            p1_end=[e['record_id'] for e in events if e['kind']=='capture_end'][-1]
            release=event('observation_release','controller',{'release_id':'observation-1'},[p1_end],phase)
            event('observation_release_received','workflow',{'release_id':'observation-1'},[release],phase)
        make_sink(root/(phase+'/sink.sqlite'),cell)
        entries.append(('sink-'+phase.lower(),phase+'/sink.sqlite','sink',phase))
        native_history=None
        if native:
            native_events=[dict(event_id='1',type='workflow_started',phase='P1',attributes={}),dict(event_id='2',type='activity_scheduled',phase='P1',attributes={'activity_id':'activity-1'}),dict(event_id='3',type='activity_started',phase='P1',attributes={'scheduled_event_id':'2','attempt':1}),dict(event_id='4',type='activity_completed',phase='P1',attributes={'scheduled_event_id':'2','started_event_id':'3','result':{'synthetic':True}})]
            if phase=='P2': native_events.append(dict(event_id='5',type='workflow_completed',phase='P2',attributes={'result':{'synthetic':True}}))
            last=native_events[-1]['event_id']
            native_history=dict(schema_version=VERSION,adapter='synthetic-normalized-v1',case_id=case['case_id'],operation_id=case['operation_id'],phase=phase,binding=binding,events=native_events,coverage=dict(complete_prefix=True,pages=[dict(input_token=None,output_token=None,first_event_id='1',last_event_id=last)],final_event_id=last,closing_boundary_event_id=last,namespace='synthetic',run_id='run-1',schema_pin='synthetic-normalized-v1'))
            write_json(root/(phase+'/native_history.json'),native_history);entries.append(('native-'+phase.lower(),phase+'/native_history.json','native',phase))
        cut='cut-'+phase;start=event('capture_start','capture',{'cut_id':cut},[events[-1]['record_id']]+(['native:'+native_history['coverage']['final_event_id']] if native else []),phase)
        acks=[]
        for producer in list(seq):
            if producer=='capture': continue
            acks.append(event('flush_ack',producer,{'cut_id':cut,'through_sequence':seq[producer]+1},[start],phase))
        end=event('capture_end','capture',{'cut_id':cut},acks,phase)
        boundary=9 if cell in ('M3','M4','K2') else 5 if cell=='C1' else 7
        capture=dict(schema_version=VERSION,case_id=case['case_id'],operation_id=case['operation_id'],phase=phase,cut_id=cut,boundary_id='boundary-'+phase,interval={'start_ref':start,'end_ref':end},producer_watermarks={p:n for p,n in seq.items() if p!='capture'},ack_refs=acks,sink_transaction=dict(transaction_id='txn-'+phase,single_read_transaction=True,table_boundaries={t:'txn-'+phase for t in ('authority','grants','tickets','events','effects')},event_boundary=boundary),native_final_event_id=native_history['coverage']['final_event_id'] if native else None,complete_producer_accounting=True,logs_flushed=True,no_detached_work=True,queued=[],in_flight=[],uncertain=[],interventions=[],completeness_limits=[])
        write_json(root/(phase+'/capture.json'),capture);entries.append(('capture-'+phase.lower(),phase+'/capture.json','capture',phase))
    write_jsonl(root/'producer_events.jsonl',events)
    cleanup=dict(schema_version=VERSION,case_id=case['case_id'],operation_id=case['operation_id'],initial_error_ref=None,secondary_errors=[],shutdown_requested=True,shutdown_acknowledged=True,budget_expired=False,forced_actions=[],child_exits=[{'child_id':'synthetic-child','exit_code':0}],outstanding=[],capture_errors=[])
    write_json(root/'cleanup.json',cleanup);entries.append(('cleanup','cleanup.json','cleanup','P3'))
    seal(root,entries)
    if views: refresh_views(root)
    return root


def refresh_views(root):
    """Fixture tool: regenerate canonical views and honest claims after semantic edits."""
    root=Path(root);bundle=Bundle(root);_,c=bundle.get('case');_,b=bundle.get('binding');events_id,events=bundle.get('events')
    raw={}
    for phase in c['phases']:
        sid,path=bundle.optional('sink',phase);cid,cap=bundle.optional('capture',phase);nid,nat=bundle.optional('native',phase)
        raw[phase]=dict(sink_id=sid,sink=inspect_sink(path,c['authority_scope']) if path else None,capture_id=cid,capture=cap,native_id=nid,native=nat)
    report=check_bundle(root,include_views=False)
    entries=[(e['artifact_id'],e['path'],e['role'],e['phase']) for e in bundle.registry['artifacts'] if not (e['role'].startswith('view_') or e['role'].startswith('envelope_') or e['role'].startswith('projection_'))]
    for phase in c['phases']:
        expected=expected_view(bundle,c,b,events_id,events,raw,phase)
        if expected is None: continue
        for view in ('A','B'):
            for filename,value in expected.items():
                path='views/'+phase+'/'+view+'/'+filename
                (write_jsonl if filename.endswith('.jsonl') else write_json)(root/path,value)
                entries.append(('v-'+phase.lower()+'-'+view.lower()+'-'+filename.replace('.','-'),path,'view_'+view+'_'+filename,phase))
            claims=[]
            permitted={canonical(x['raw_ref']) for x in expected['source_map.json']['records']}
            visible_reference=caller_reference(report['phases'][phase]['reference'],[x['raw_ref'] for x in expected['source_map.json']['records']],events,events_id,phase,raw[phase]['capture'])
            for field,item in visible_reference.items():
                sufficient=item['evidence_refs'] and all(canonical(r) in permitted for r in item['evidence_refs'])
                value=item['value'] if sufficient else 'unresolved'
                claims.append(dict(field=field,value=value,observer='synthetic_projection',scope=c['operation_id'],assertion_phase=phase,evidence_refs=item['evidence_refs'] if sufficient else []))
            if view=='A':
                path='views/'+phase+'/A/envelope.json';write_json(root/path,dict(schema_version=VERSION,case_id=c['case_id'],operation_id=c['operation_id'],phase=phase,assertions=claims));entries.append(('envelope-'+phase.lower(),path,'envelope_A',phase))
            path='outputs/'+phase+'-'+view+'.json';write_json(root/path,dict(schema_version=VERSION,case_id=c['case_id'],operation_id=c['operation_id'],phase=phase,view=view,assertions=claims));entries.append(('output-'+phase.lower()+'-'+view.lower(),path,'projection_'+view,phase))
    seal(root,entries)
