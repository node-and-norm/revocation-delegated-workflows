"""Read-only evidence checker; no imports of runner/workflow/gateway."""
import argparse,json
from pathlib import Path
ARGS={'to':['synthetic@example.invalid'],'subject':'Synthetic summary','body':'inert summary','cc':[]}
BINDING={'principal':'childC','grant':'child-1','parent_grant':'parent-0','parent_principal':'parentP','root':'rootR','epoch':7,'scope':'summary:task1','ticket':'ticket-1','action':'send_email','args':ARGS}

def check(r):
    errors=[]
    def need(condition,label):
        if not condition:errors.append(label)
    try:
        need(r['binding']==BINDING,'binding')
        need(r['gateway_alive_after_resume'] and r['gateway_exitcode']==0,'gateway lifetime')
        sink=r['sink'];ev=sink['events'];effects=sink['effects']
        need([e['seq'] for e in ev]==list(range(1,len(ev)+1)),'event sequence')
        # Full independent expected event transcript, including authority setup.
        effect_result={'outcome':'effect','effect_key':'summary:task1','payload':'inert summary','root':'rootR','epoch':7}
        grant_result={'outcome':'grant','grant':'child-1','owner':'childC','root':'rootR','epoch':7,'scope':'summary:task1','parent_grant':'parent-0'}
        admission_result={'outcome':'admission','ticket':'ticket-1','grant':'child-1','root':'rootR','epoch':7,'scope':'summary:task1'}
        revoke_result={'outcome':'revocation','root':'rootR','withdrawn_epoch':7,'new_epoch':8}
        expected_events=[{'kind':'bootstrap','data':{'root':'rootR','epoch':7,'parent_grant':'parent-0','parent':'parentP','child':'childC','scope':'summary:task1'}}]
        def pair(actor,request,result):
            expected_events.extend([{'kind':'receipt','data':{'actor':actor,'request':request}},{'kind':result['outcome'],'data':{'request_id':request['id'],'result':result}}])
        pair('parentP',{'id':'delegate','op':'delegate','claim':'parentP','grant':'parent-0','scope':'summary:task1','child':'childC'},grant_result)
        pair('childC',{'id':'prepare','op':'prepare','claim':'childC','grant':'child-1','scope':'summary:task1'},admission_result)
        execute_request={'op':'execute','claim':'childC','grant':'child-1','scope':'summary:task1','ticket':'ticket-1','payload':'inert summary'}
        if r['prior']:pair('childC',dict(execute_request,id='prior-execute'),effect_result)
        if r['revoked']:pair('controller',{'id':'revoke','op':'revoke','claim':'controller'},revoke_result)
        expected_result={'outcome':'denied','reason':'revoked'} if r['revoked'] else ({'outcome':'duplicate'} if r['prior'] else effect_result)
        pair('childC',dict(execute_request,id='resume-execute'),expected_result)
        need([{k:e[k] for k in ('kind','data')} for e in ev]==expected_events,'full event transcript')
        need(r['grant']==grant_result and r['admission']==admission_result,'controller setup agreement')
        if r['revoked']:need(r['revocation']==revoke_result,'controller revoke agreement')
        if r['prior']:need(r['prior_result']==effect_result,'controller prior agreement')
        receipts=[e for e in ev if e['kind']=='receipt']
        need(len(receipts)==3+int(r['prior'])+int(r['revoked']),'request count')
        need(sink['authority']==[{'root':'rootR','epoch':8 if r['revoked'] else 7,'active':0 if r['revoked'] else 1}],'authority state')
        need(sorted(sink['grants'],key=lambda x:x['token'])==[{'token':'child-1','owner':'childC','root':'rootR','epoch':7,'scope':'summary:task1','can_delegate':0},{'token':'parent-0','owner':'parentP','root':'rootR','epoch':7,'scope':'summary:task1','can_delegate':1}],'grant lineage')
        need(sink['tickets']==[{'token':'ticket-1','grant_token':'child-1','owner':'childC','scope':'summary:task1'}],'ticket binding')
        for x in receipts:
            q=x['data']['request'];op=q['op']
            need(x['data']['actor']=={'delegate':'parentP','prepare':'childC','execute':'childC','revoke':'controller'}[op],'receipt principal')
            need(q['claim']==x['data']['actor'],'claim')
            if op=='execute':need({k:q[k] for k in ('grant','scope','ticket','payload')}=={'grant':'child-1','scope':'summary:task1','ticket':'ticket-1','payload':'inert summary'},'execute binding')
        attempts=[e for e in receipts if e['data']['request']['id']=='resume-execute']
        terminals=[e for e in ev if e['kind']!='receipt' and e['data'].get('request_id')=='resume-execute']
        need(len(attempts)==1 and len(terminals)==1,'observed resumed attempt')
        if len(attempts)!=1 or len(terminals)!=1:raise ValueError('missing attempt evidence')
        need(terminals[0]['seq']==attempts[0]['seq']+1,'attempt terminal ordering')
        result=terminals[0]['data']['result'];kind=result['outcome']
        disposition='revoked' if kind=='denied' and result.get('reason')=='revoked' else ('other_denial' if kind=='denied' else kind)
        expected='revoked' if r['revoked'] else ('duplicate' if r['prior'] else 'effect')
        need(disposition==expected,'attempt expected disposition')
        fences=[e['seq'] for e in ev if e['kind']=='revocation']
        need(len(fences)==int(r['revoked']),'fence count')
        if fences:need(fences[0]<attempts[0]['seq'],'resume after fence')
        need(len(effects)==int(r['prior'] or not r['revoked']),'effect count')
        effectevents=[e for e in ev if e['kind']=='effect']
        need(len(effectevents)==len(effects),'effect event count')
        for eff in effects:
            need({k:eff[k] for k in ('effect_key','payload','root','epoch')}=={'effect_key':'summary:task1','payload':'inert summary','root':'rootR','epoch':7},'effect binding')
            matches=[e for e in effectevents if e['seq']==eff['event_seq']]
            need(len(matches)==1,'effect observation link')
            if matches:
                need(matches[0]['data']['request_id']==('prior-execute' if r['prior'] else 'resume-execute'),'effect attribution')
                need(matches[0]['data']['result']==dict(outcome='effect',**{k:v for k,v in eff.items() if k!='event_seq'}),'effect row-event agreement')
        operation='no_effect' if not effects else ('post_fence_effect' if fences and any(e['event_seq']>fences[0] for e in effects) else ('pre_fence_effect' if fences else 'authorized_effect'))
        need(operation!='post_fence_effect','post-fence effect')
        if r['path']=='framework':
            need(len(r['workers'])==2,'worker count')
            a,b=r['workers']
            need(a['binding']==b['binding']==BINDING,'worker bindings')
            need(a['pid']!=b['pid'],'fresh process')
            need(a['phase']=='pause' and b['phase']=='resume','worker phases')
            need(a['exitcode']==b['exitcode']==0 and a['ok'] and b['ok'],'worker completion')
            for cfg in (a['checkpoint_after'],b['checkpoint_before']):
                need(bool(cfg['configurable']['checkpoint_id']) and cfg['configurable']['thread_id']=='pilot','checkpoint provenance')
            need(a['checkpoint_after']==b['checkpoint_before'],'checkpoint identity')
            need(a['pending']==b['restored_interrupts'] and len(a['pending'])==1,'interrupt identity')
            need(bool(a['pending'][0]['id']),'interrupt provenance')
            action=a['pending'][0]['value']['action_requests']
            need(len(action)==1 and action[0]['name']=='send_email' and action[0]['args']==ARGS,'interrupt action')
            need(not b['pending'],'resume termination')
            need([t['kind'] for t in a['trace']]==['manage_email_entry'],'no sink before pause')
            need([t['kind'] for t in b['trace']]==['manage_email_entry','tool_entry','tool_response'],'native tool trace')
            need(b['trace'][1]['binding']==BINDING and b['trace'][1]['args']==ARGS,'adapter binding')
            need(b['trace'][2]['result']==result,'tool result agreement')
            need(b['trace'][2]['request']==attempts[0]['data']['request'],'tool request agreement')
            need(json.loads(b['result']['messages'][-1]['content'])==result,'structured final propagation')
            need(a['models'][0][0]['output']['tool_calls'][0]['name']=='manage_email','supervisor route')
            need(a['models'][1][0]['output']['tool_calls'][0]['name']=='send_email','subagent route')
        else:need(r['final']==result,'direct result agreement')
        return {'name':r['name'],'qualified':not errors,'operation_outcome':operation,'attempt_disposition':disposition,'errors':errors}
    except (KeyError,ValueError,IndexError,TypeError) as e:
        return {'name':r.get('name'),'qualified':False,'operation_outcome':'unresolved','attempt_disposition':'unresolved','errors':errors+[str(e)]}

def check_dir(root):
    records=[json.loads(p.read_text()) for p in sorted(root.glob('*/record.json'))]
    results=[check(r) for r in records]
    matrix={(r['path'],r['prior'],r['revoked']) for r in records}
    complete=matrix=={(p,h,r) for p in ('direct','framework') for h in (False,True) for r in (False,True)} and len(records)==8
    return {'qualified':complete and all(x['qualified'] for x in results),'complete_matrix':complete,'results':results}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);args=p.parse_args();summary=check_dir(args.directory);print(json.dumps(summary,indent=2));raise SystemExit(0 if summary['qualified'] else 1)
