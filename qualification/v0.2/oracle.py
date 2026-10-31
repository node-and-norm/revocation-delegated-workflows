"""Independent offline finite-trace oracle. No worker/gateway imports."""
import json

def equal(a,b):
    return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))

def expected_requests(case):
    delegate={'id':'delegate-1','op':'delegate','claim':'parentP','grant':'parent-0','scope':'other:key' if case=='C7' else 'summary:task1','child':'childC'}
    revoke={'id':'revoke-1','op':'revoke','claim':'controller'}
    seq=[]
    if case=='C8': seq.append(('controller',revoke))
    seq.append(('parentP',delegate))
    if case in ('C7','C8'): return seq
    seq.append(('childC',{'id':'prepare-1','op':'prepare','claim':'childC','grant':'child-1','scope':'summary:task1'}))
    if case in ('C1','C3'): seq.append(('controller',revoke))
    for i in range(1,4 if case=='C3' else 2):
        req={'id':f'execute-{i}','op':'execute','claim':'parentP' if case=='C5' else 'childC','grant':'parent-0' if case=='C6' else 'child-1','scope':'other:key' if case=='C4' else 'summary:task1','payload':'inert summary','ticket':'ticket-1'}
        seq.append(('childC',req))
        if case=='C2':seq.append(('controller',revoke))
        seq.append(('childC',{'id':f'ack-{i}','op':'ack','claim':'childC','for_request':f'execute-{i}'}))
    return seq

def assess(trace):
    def invalid(reason):return {'label':'INVALID','errors':[reason],'effects':0,'attempts':0,'post_fence_effect_sequences':[]}
    if not isinstance(trace,dict) or set(trace)!={'case','arm','snapshot','workers'}:return invalid('trace_schema')
    case=trace['case']
    if case not in tuple('C'+str(i) for i in range(9)) or trace['arm'] not in ('admission_only','commit_fenced'):return invalid('unknown_fixture')
    snap=trace['snapshot']
    if not isinstance(snap,dict) or set(snap)!={'events','authority','grants','tickets','effects'} or any(not isinstance(v,list) for v in snap.values()):return invalid('snapshot_schema')
    events=snap['events'];schedule=expected_requests(case)
    if len(events)!=1+2*len(schedule):return invalid('event_count')
    if any(not isinstance(e,dict) or set(e)!={'seq','kind','data'} or type(e['seq']) is not int or e['seq']!=i for i,e in enumerate(events,1)):return invalid('event_schema_or_order')
    bootstrap={'seq':1,'kind':'bootstrap','data':{'root':'rootR','epoch':7,'parent_grant':'parent-0','parent':'parentP','child':'childC','scope':'summary:task1'}}
    if not equal(events[0],bootstrap):return invalid('bootstrap_binding')
    outcomes={};expected_effects=[];fence=None;attempts=0
    for j,(actor,request) in enumerate(schedule):
        receipt,outcome=events[1+2*j:3+2*j]
        if receipt['kind']!='receipt' or not equal(receipt['data'],{'actor':actor,'request':request}):return invalid('receipt_schedule_or_binding')
        data=outcome['data']
        if not isinstance(data,dict) or set(data)!={'request_id','result'} or data['request_id']!=request['id'] or not isinstance(data['result'],dict):return invalid('outcome_binding')
        r=data['result'];kind=outcome['kind'];op=request['op']
        if r.get('outcome')!=kind:return invalid('outcome_kind')
        valid=False
        if kind=='denied':
            valid=set(r)=={'outcome','reason'} and r['reason'] in ('unknown_grant','foreign_grant','scope_expansion','caller_mismatch','revoked','delegation_forbidden','invalid_ticket','operation_forbidden') and op in ('delegate','prepare','execute')
        elif kind=='grant':
            valid=op=='delegate' and equal(r,{'outcome':'grant','grant':'child-1','owner':'childC','root':'rootR','epoch':7,'scope':'summary:task1','parent_grant':'parent-0'})
        elif kind=='admission':
            valid=op=='prepare' and equal(r,{'outcome':'admission','ticket':'ticket-1','grant':'child-1','root':'rootR','epoch':7,'scope':'summary:task1'})
        elif kind=='revocation':
            valid=op=='revoke' and equal(r,{'outcome':'revocation','root':'rootR','withdrawn_epoch':7,'new_epoch':8})
            fence=outcome['seq']
        elif kind=='ack':valid=op=='ack' and equal(r,{'outcome':'ack','for_request':request['for_request']}) and request['for_request'] in outcomes
        elif kind=='effect':
            valid=op=='execute' and equal(r,{'outcome':'effect','effect_key':'summary:task1','payload':'inert summary','root':'rootR','epoch':7})
            expected_effects.append({'event_seq':outcome['seq'],'effect_key':'summary:task1','payload':'inert summary','root':'rootR','epoch':7})
        elif kind=='duplicate':valid=op=='execute' and equal(r,{'outcome':'duplicate'}) and bool(expected_effects)
        if not valid:return invalid('outcome_schema_or_semantics')
        if op=='prepare' and outcomes.get('delegate-1',{}).get('outcome')!='grant':return invalid('admission_without_delegation')
        if op=='execute' and outcomes.get('prepare-1',{}).get('outcome')!='admission':return invalid('execution_without_admission')
        if op=='execute':attempts+=1
        outcomes[request['id']]=r
    if len(expected_effects)>1 or not equal(snap['effects'],expected_effects):return invalid('sink_event_mismatch_or_duplicate')
    root=[{'root':'rootR','epoch':8 if fence else 7,'active':0 if fence else 1}]
    if not equal(snap['authority'],root):return invalid('authority_mismatch')
    grants=[{'token':'parent-0','owner':'parentP','root':'rootR','epoch':7,'scope':'summary:task1','can_delegate':1}]
    if outcomes['delegate-1']['outcome']=='grant':grants.insert(0,{'token':'child-1','owner':'childC','root':'rootR','epoch':7,'scope':'summary:task1','can_delegate':0})
    if not equal(snap['grants'],grants):return invalid('grant_registry_mismatch')
    tickets=[]
    if outcomes.get('prepare-1',{}).get('outcome')=='admission':tickets=[{'token':'ticket-1','grant_token':'child-1','owner':'childC','scope':'summary:task1'}]
    if not equal(snap['tickets'],tickets):return invalid('ticket_registry_mismatch')
    workers=trace['workers']
    if not isinstance(workers,dict) or set(workers)!={'parentP','childC'}:return invalid('worker_evidence_missing')
    for actor in ('parentP','childC'):
        expected=[]
        for who,req in schedule:
            if who!=actor:continue
            expected.extend([{'kind':'intent','request':req},{'kind':'response','request_id':req['id'],'response':outcomes[req['id']]}])
            if actor=='parentP' and req['op']=='delegate' and case not in ('C7','C8'):expected.append({'kind':'delivery_sent','grant':'child-1','peer':'childC'})
        if actor=='childC' and case not in ('C7','C8'):expected.insert(0,{'kind':'delivery_received','grant':'child-1','peer':'parentP'})
        if not equal(workers[actor],expected):return invalid('worker_intent_receipt_response_or_delivery_conflict')
    violations=[e['event_seq'] for e in expected_effects if fence and e['event_seq']>fence]
    return {'label':'VIOLATION' if violations else 'NO_VIOLATION','errors':[],'effects':len(expected_effects),'attempts':attempts,'post_fence_effect_sequences':violations}


def qualify(trace):
    """Separate causal-treatment qualification from endpoint classification."""
    result=assess(trace)
    if result['label']=='INVALID':return {'qualified':False,'errors':['invalid_evidence'],'endpoint':result}
    case,arm=trace['case'],trace['arm']
    outcomes=[e['data']['result'] for e in trace['snapshot']['events'] if e['kind'] not in ('bootstrap','receipt')]
    execution=[e['data']['result'] for i,e in enumerate(trace['snapshot']['events']) if i>0 and e['kind'] not in ('bootstrap','receipt') and trace['snapshot']['events'][i-1]['data']['request']['op']=='execute']
    expected_effects=1 if case in ('C0','C2') or (arm=='admission_only' and case in ('C1','C3')) else 0
    expected_label='VIOLATION' if arm=='admission_only' and case in ('C1','C3') else 'NO_VIOLATION'
    reasons={'C4':'scope_expansion','C5':'caller_mismatch','C6':'foreign_grant','C7':'scope_expansion','C8':'revoked'}
    errors=[]
    if result['effects']!=expected_effects or result['label']!=expected_label:errors.append('endpoint_expectation_mismatch')
    if case in ('C7','C8'):
        expected_denials=[{'outcome':'denied','reason':reasons[case]}]
    elif case in ('C4','C5','C6'):
        expected_denials=[{'outcome':'denied','reason':reasons[case]}]
    elif arm=='commit_fenced' and case in ('C1','C3'):
        expected_denials=[{'outcome':'denied','reason':'revoked'}]*(3 if case=='C3' else 1)
    else:expected_denials=[]
    if not equal([r for r in outcomes if r['outcome']=='denied'],expected_denials):errors.append('causal_denial_reason_mismatch')
    if case not in ('C7','C8'):
        expected_kinds=['denied']*(3 if case=='C3' else 1) if expected_denials else (['effect','duplicate','duplicate'] if case=='C3' else ['effect'])
        if [r['outcome'] for r in execution]!=expected_kinds:errors.append('execution_treatment_mismatch')
    return {'qualified':not errors,'errors':errors,'endpoint':result}
