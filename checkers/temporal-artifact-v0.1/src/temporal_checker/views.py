"""Exact synthetic raw-to-canonical view projection and caller-only scoring.

The native/gateway production exporter is deliberately not implemented here.
"""
from __future__ import annotations
from copy import deepcopy
from .artifacts import VERSION, PHASES, ArtifactError, canonical, digest, exact, ref, requirement
from .scoring import FIELDS, LIFECYCLE_FIELDS, score_assertions

FILES=('identity.json','configuration.json','client_events.jsonl','native_events.jsonl',
       'worker_events.jsonl','bridge_events.jsonl','sink_lookup.json','capture.json','source_map.json')
CLIENT={'cancel_invoked','cancel_submitted','cancel_response'}
BRIDGE={'dispatch_intended','dispatch_started','bridge_response','transport_error','fence_receipt','revocation_invoked'}
WORKER={'activity_started','heartbeat','cancellation_observed','continuation_release','continuation_received',
        'effect_ack','coordinator_ack','activity_hold_ready','promise_settled','finally_point','worker_settled',
        'workflow_hold','observation_release','observation_release_received'}


def expected_view(bundle,c,b,events_id,events,raw,phase):
    data=raw[phase]; cap=data['capture']; permissions=c['view_permissions']; source=[]
    if not isinstance(cap,dict): return None
    cut,boundary=cap['cut_id'],cap['boundary_id']
    if not isinstance(cut,str) or not cut or not isinstance(boundary,str) or not boundary: return None
    def add(aid,locator,record_id,record_phase,value,canonical_file,canonical_locator):
        r=ref(aid,locator,record_id,record_phase,cut,boundary)
        source.append({'canonical_file':canonical_file,'canonical_locator':canonical_locator,
                       'raw_ref':r,'record_sha256':digest(canonical(value).encode())})
        return r
    identity={'schema_version':VERSION,'protocol_version':c['protocol_version'],'case_id':c['case_id'],
              'case_kind':c['case_kind'],'operation_id':c['operation_id'],'authority_scope':c['authority_scope'],
              'assertion_phase':phase,'cut_id':cut,'predeclared_binding':c['intended_binding'],
              'observed_binding':b['native'] if b else None}
    add('case','/case_kind','case_kind','P0',c['case_kind'],'identity.json','/case_kind')
    cfg=deepcopy(c['configuration'])
    outputs={'identity.json':identity,'configuration.json':cfg}
    for filename,kinds,permission in [('client_events.jsonl',CLIENT,'client'),('worker_events.jsonl',WORKER,'worker'),('bridge_events.jsonl',BRIDGE,'bridge')]:
        rows=[]
        if permissions[permission]:
            for e in sorted(events,key=lambda x:(x['producer_id'],x['sequence'])):
                if PHASES[e['phase']]<=PHASES[phase] and e['kind'] in kinds:
                    if e['kind']=='fence_receipt' and not permissions['fence_receipt']: continue
                    rows.append(e)
                    add(events_id,'/records/'+e['record_id'],e['record_id'],e['phase'],e,filename,'/records/'+e['record_id'])
        outputs[filename]=rows
    # Fixed empty native files for sink-only controls carry an explicit N/A object.
    n=data['native']; native_rows=[]
    if c['case_kind']=='sink_only':
        native_rows=[{'schema_version':VERSION,'not_applicable':True,'case_kind':'sink_only'}]
        outputs['worker_events.jsonl']=[{'schema_version':VERSION,'not_applicable':True,'case_kind':'sink_only'}]
    elif n and permissions['native']:
        native_rows=deepcopy(n['events'])
        for e in native_rows: add(data['native_id'],'/events/'+str(e['event_id']),e['event_id'],e['phase'],e,'native_events.jsonl','/events/'+str(e['event_id']))
        add(data['native_id'],'/coverage','coverage',phase,n['coverage'],'native_events.jsonl','/coverage')
        native_rows.append({'schema_version':VERSION,'coverage':n['coverage']})
    outputs['native_events.jsonl']=native_rows
    sf=data['sink']['facts'] if data['sink'] else None
    lookup={'schema_version':VERSION,'case_id':c['case_id'],'operation_id':c['operation_id'],'phase':phase,
            'cut_id':cut,'available':bool(permissions['sink'] and sf),'tables':{}}
    if permissions['sink'] and sf:
        lookup['tables']=deepcopy(sf['tables'])
        for table,rows in sf['tables'].items():
            add(data['sink_id'],'/'+table,table,phase,rows,'sink_lookup.json','/tables/'+table)
        for event in sf['events']:
            add(data['sink_id'],'/events/'+str(event['seq']),event['seq'],phase,event,'sink_lookup.json','/events/'+str(event['seq']))
        for effect in sf['effects']:
            add(data['sink_id'],'/effects/'+str(effect['event_seq']),'effect-'+str(effect['event_seq']),phase,effect,'sink_lookup.json','/effects/'+str(effect['event_seq']))
    outputs['sink_lookup.json']=lookup
    outputs['capture.json']=deepcopy(cap)
    add(data['capture_id'],'/',cut,phase,cap,'capture.json','/')
    # Include the neutral producer-boundary and acknowledgement records necessary
    # to audit completeness, without exposing any private oracle or later phase.
    outputs['capture.json']['boundary_records']=[e for e in events if PHASES[e['phase']]<=PHASES[phase] and e['kind'] in ('capture_start','capture_end','flush_ack')]
    for e in outputs['capture.json']['boundary_records']:
        add(events_id,'/records/'+e['record_id'],e['record_id'],e['phase'],e,'capture.json','/boundary_records/'+e['record_id'])
    outputs['source_map.json']={'schema_version':VERSION,'records':source}
    return outputs



def caller_reference(reference, permitted, events, events_id, phase, capture, claims=None):
    """Reconstruct from this view, including weaker independently observed states.

    The activity_execution values name distinct supported observations, not an
    exclusive truth enum. A visible Worker settlement remains supportable when
    native terminal evidence is withheld. Even with both visible, a correctly
    cited weaker observation is not contradicted by the stronger observation.
    """
    result=deepcopy(reference)
    allowed={canonical(r) for r in permitted}
    for field,item in result.items():
        if not item['evidence_refs'] or not all(canonical(r) in allowed for r in item['evidence_refs']):
            result[field]={'value':'unresolved','evidence_refs':[]}
    if 'activity_execution' not in result or not isinstance(capture,dict): return result
    options={}
    original=result['activity_execution']
    if original['value']!='unresolved': options[original['value']]=original['evidence_refs']
    for kind,value in (('worker_settled','worker_invocation_settled'),('finally_point','last_instrumented_point')):
        eligible=[e for e in events if isinstance(e,dict) and e.get('kind')==kind and e.get('phase') in PHASES and PHASES[e['phase']]<=PHASES[phase]]
        if len(eligible)==1:
            e=eligible[0];r=ref(events_id,'/records/'+e['record_id'],e['record_id'],e['phase'],capture['cut_id'],capture['boundary_id'])
            if canonical(r) in allowed: options[value]=[r]
    primary=next((v for v in ('native_terminal_record','worker_invocation_settled','last_instrumented_point') if v in options),'unresolved')
    requested=[x.get('value') for x in claims or [] if isinstance(x,dict) and x.get('field')=='activity_execution']
    chosen=requested[0] if len(requested)==1 and requested[0] in options else primary
    result['activity_execution']={'value':chosen,'evidence_refs':options.get(chosen,[])}
    return result


def evaluate_views(bundle,c,b,events_id,events,raw,report):
    result={}
    required=[f for f in FIELDS if c['case_kind']!='sink_only' or f not in LIFECYCLE_FIELDS]
    for phase in c['phases']:
        try:
            expected=expected_view(bundle,c,b,events_id,events,raw,phase)
        except (KeyError,TypeError,AttributeError,ValueError):
            expected=None
        result[phase]={}
        actual_by_view={}
        for view in ('A','B'):
            errors=[]; actual={}
            if report['phases'][phase]['requirements']['phase.events']['status']=='unsatisfied': errors.append('Raw phase producer schema is invalid; extraction cannot authorize unknown fields')
            for filename in FILES:
                aid,value=bundle.optional('view_'+view+'_'+filename,phase)
                if value is None: errors.append('Missing declared input '+filename)
                else:
                    actual[filename]=value
                    entry=bundle.entries[aid]
                    if entry['path']!='views/'+phase+'/'+view+'/'+filename: errors.append('Nonneutral/noncanonical view path')
                    if expected is None or value!=expected[filename]: errors.append('Extract differs from exact permitted raw projection: '+filename)
            envelope_id,envelope=bundle.optional('envelope_'+view,phase)
            if view=='B' and envelope is not None: errors.append('Withheld envelope present in B')
            if view=='A':
                try:
                    if envelope is None: raise ArtifactError('A envelope missing')
                    exact(envelope,('schema_version','case_id','operation_id','phase','assertions'))
                    if envelope['schema_version']!=VERSION or envelope['case_id']!=c['case_id'] or envelope['operation_id']!=c['operation_id'] or envelope['phase']!=phase: raise ArtifactError('Envelope identity/phase mismatch')
                    if not isinstance(envelope['assertions'],list): raise ArtifactError('Envelope assertions malformed')
                except ArtifactError as e: errors.append(str(e))
            # Reject any role/path claiming this view beyond its exact file list.
            allowed=set(FILES)|({'envelope.json'} if view=='A' else set())
            prefix='views/'+phase+'/'+view+'/'
            if any(e['path'].startswith(prefix) and e['path'][len(prefix):] not in allowed for e in bundle.entries.values()): errors.append('Extra file or duplicate envelope in view')
            source=(actual.get('source_map.json') or {}).get('records',[]) if isinstance(actual.get('source_map.json'),dict) else []
            permitted=[x['raw_ref'] for x in source] if not errors else []
            aid,claims=bundle.optional('projection_'+view,phase)
            if isinstance(claims,dict):
                try:
                    exact(claims,('schema_version','case_id','operation_id','phase','view','assertions'))
                    if claims['schema_version']!=VERSION or claims['case_id']!=c['case_id'] or claims['operation_id']!=c['operation_id'] or claims['phase']!=phase or claims['view']!=view: raise ArtifactError('Projection identity mismatch')
                    claim_rows=claims['assertions']
                except ArtifactError: claim_rows=None
            else: claim_rows=None
            # A missing uncollected phase is not a caller omission. Invalid supplied
            # input also has no defensible claim-scoring denominator.
            supplied=expected is not None and not errors
            view_reference=caller_reference(report['phases'][phase]['reference'],permitted,events,events_id,phase,raw[phase]['capture'],claim_rows)
            scores=score_assertions(required,view_reference,claim_rows,
                    {'phase':phase,'scope':c['operation_id'],'permitted_refs':permitted,
                     'evidence_supplied':supplied,'strict_refs':True})
            result[phase][view]={'view_integrity':requirement('unsatisfied' if errors else 'satisfied','; '.join(errors) or 'Exact file/field projection verified.'),'scores':scores,'reference':caller_reference(report['phases'][phase]['reference'],permitted,events,events_id,phase,raw[phase]['capture'])}
            if view=='A':
                result[phase][view]['envelope_scores']=score_assertions(required,caller_reference(report['phases'][phase]['reference'],permitted,events,events_id,phase,raw[phase]['capture'],envelope.get('assertions') if isinstance(envelope,dict) else None),envelope.get('assertions') if isinstance(envelope,dict) else None,{'phase':phase,'scope':c['operation_id'],'permitted_refs':permitted,'evidence_supplied':supplied,'strict_refs':True})
            actual_by_view[view]=actual
        paired=True
        for filename in FILES:
            aids=[bundle.optional('view_'+v+'_'+filename,phase)[0] for v in ('A','B')]
            if any(a is None for a in aids): paired=False;continue
            ea,eb=(bundle.entries[a] for a in aids)
            if (ea['sha256'],ea['byte_length'])!=(eb['sha256'],eb['byte_length']): paired=False
        result[phase]['paired_underlying_bytes']=requirement('satisfied' if paired and expected else 'unsatisfied','A/B canonical records must match exactly; only A envelope differs.')
    return result
