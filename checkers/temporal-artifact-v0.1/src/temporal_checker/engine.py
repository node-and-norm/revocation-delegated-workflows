"""Phase-aware saved-evidence reasoning; no runtime or transport imports."""
from __future__ import annotations
from collections import defaultdict
from .artifacts import ArtifactError, Bundle, PHASES, VERSION, canonical, exact, integer, native_id, ref, requirement
from .schema import validate_case, validate_binding, validate_events, validate_native, BUDGETS
from .sink import inspect_sink


def check_bundle(root, *, include_views=True):
    bundle=Bundle(root)
    report={'checker_version':'0.1.0','evidence_class':'synthetic_only','native_qualification':False,
            'requirements':{},'phases':{},'limitations':[
              'Only synthetic-artifact-0.1 is supported; the saved native exporter is not adapted or qualified.',
              'Saved certificates are checked under trusted-fixture assumptions, not authenticated attestations.',
              'Native outcome mappings and calibrated numerical deadlines remain open.'],
            'qualification_acceptance':requirement('unobserved','Native acceptance is unavailable for synthetic evidence.'),
            'execution_readiness':requirement('unobserved','No runtime execution is supported by this artifact-only checker.'),
            'freeze_requirements':{'production_exporter':requirement('unobserved','Only the explicit synthetic adapter exists.'),'phase_manifest_sealing':requirement('unobserved','The synthetic bundle registry seals the complete saved fixture; independently persisted runtime phase registries remain unimplemented.'),'native_mappings':requirement('unobserved','No observed native tuples have been qualified.'),'deadline_calibration':requirement('unobserved','No numerical runtime deadline is calibrated.')}}
    R=report['requirements']
    R['artifact.integrity']=requirement('unsatisfied' if bundle.errors else 'satisfied','; '.join(bundle.errors) or 'All registered bytes and paths verified.')
    try:
        case_id,c=bundle.get('case'); validate_case(c)
        R['schema.case']=requirement('satisfied','Explicit synthetic case schema verified.')
    except (ArtifactError,TypeError,KeyError) as e:
        R['schema.case']=requirement('unsatisfied',str(e)); return report
    report['case']={k:c[k] for k in ('case_id','operation_id','attempt_id','cell','case_kind','study_phase','phases')}
    report['attempt_retained']=True
    try:
        binding_id,b=bundle.get('binding'); validate_binding(b,c)
        R['schema.binding']=requirement('satisfied','Observed binding agrees with predeclared identities.')
    except (ArtifactError,TypeError,KeyError) as e:
        R['schema.binding']=requirement('unsatisfied',str(e)); b=None
    try:
        events_id,events=bundle.get('events')
        if b is None: raise ArtifactError('No validated binding for event linkage')
        validate_events(events,c,b)
        R['schema.events']=requirement('satisfied','Closed event schemas, identities and positions verified.')
    except (ArtifactError,TypeError,KeyError) as e:
        R['schema.events']=requirement('unsatisfied',str(e)); events=events if isinstance(locals().get('events'),list) else []; events_id=locals().get('events_id','unavailable')
    report['events_observed']=len(events)
    # Parse each phase independently. Invalid P2 cannot rewrite P1 facts.
    raw={}
    for phase in c['phases']:
        aid,sink_path=bundle.optional('sink',phase)
        sink=inspect_sink(sink_path,c['authority_scope']) if sink_path else None
        cap_id,cap=bundle.optional('capture',phase)
        nat_id,nat=bundle.optional('native',phase)
        native_error=None
        if c['case_kind']=='native_activity':
            try:
                if nat is None or b is None: raise ArtifactError('Missing native history or binding')
                validate_native(nat,c,b,phase)
            except (ArtifactError,TypeError,KeyError) as e:
                native_error=str(e); nat=None
        elif nat is not None:
            native_error='Native history is forbidden for sink-only controls'; nat=None
        raw[phase]=dict(sink_id=aid,sink=sink,capture_id=cap_id,capture=cap,native_id=nat_id,native=nat,native_error=native_error)
    p3_id,p3_path=bundle.optional('sink','P3')
    if p3_path:
        raw['P3']=dict(sink_id=p3_id,sink=inspect_sink(p3_path,c['authority_scope']),capture_id=None,capture=None,native_id=None,native=None,native_error=None)
    graph_errors=[]
    native=c['case_kind']=='native_activity'
    config_ok=(not native or (c['configuration']['maximum_attempts']==1 and type(c['configuration']['maximum_attempts']) is int and c['configuration']['activity_scope']=='cancellable_root' and c['configuration']['hold_scope']=='non_cancellable_observation_only'))
    R['setup.configuration']=requirement('satisfied' if config_ok else 'unsatisfied','Explicit policy and observation scope match.' if config_ok else 'Misconfigured retry or cancellation scope.')
    R['setup.registration']=requirement('satisfied' if c['registered_before_dispatch'] else 'unsatisfied','Synthetic registration declaration; historical registration authenticity is not inferred.')
    R['freeze.deadlines']=requirement('unobserved' if any(x is None for x in c['configuration']['deadlines'].values()) else 'satisfied','Required finite budgets are unset; calibration is not invented.' if any(x is None for x in c['configuration']['deadlines'].values()) else 'Synthetic test budgets present, not empirically calibrated.')
    for phase in c['phases']:
        phase_events=[e for e in events if isinstance(e,dict) and e.get('phase') in PHASES and PHASES[e['phase']]<=PHASES[phase]]
        phase_schema_error=None
        try:
            if any(not isinstance(e,dict) or e.get('phase') not in PHASES for e in events): raise ArtifactError('Unscoped malformed producer record')
            if b is None: raise ArtifactError('Binding unavailable')
            validate_events(phase_events,c,b)
        except (ArtifactError,TypeError,KeyError) as e:
            phase_schema_error=str(e);phase_events=[]
        phase_raw={p:d for p,d in raw.items() if PHASES[p]<=PHASES[phase]}
        graph,errors=build_graph(phase_events,phase_raw)
        if phase_schema_error: errors.append(phase_schema_error)
        graph_errors.extend(phase+': '+x for x in errors)
        result=analyze_phase(bundle,c,b,events_id,phase_events,raw,phase,graph,not errors)
        result['graph_valid']=not errors
        result['requirements']['phase.events']=requirement('unsatisfied' if phase_schema_error else 'satisfied',phase_schema_error or 'This phase producer schema is valid independently of later phases.')
        result['requirements']['phase.graph']=requirement('unsatisfied' if errors else 'satisfied','; '.join(errors) or 'Phase causal graph verified.')
        report['phases'][phase]=result
    R['causal.graph']=requirement('unsatisfied' if graph_errors else 'satisfied','; '.join(graph_errors) or 'Each phase causal graph is valid.')
    report['cleanup']=check_cleanup(bundle,c)
    check_late_evidence(c,[e for e in events if isinstance(e,dict) and e.get('kind') in ('dispatch_started','bridge_response') and isinstance(e.get('payload'),dict) and e.get('phase') in PHASES],raw,report)
    report['cross_phase']=compare_phases(c,raw,report)
    if include_views:
        from .views import evaluate_views
        report['views']=evaluate_views(bundle,c,b,events_id,events,raw,report)
    # No favorable outcome or caller score is an inclusion condition.
    for p,result in report['phases'].items():
        reqs=result['requirements']; observed=result['observed']
        result['analysis_eligibility']={
          'sink_accounting':requirement('satisfied' if observed.get('sink_usable') else 'unobserved','Depends on accounting evidence, not favorable sink outcome.'),
          'native_description':requirement('not_applicable' if not native else ('satisfied' if raw[p]['native'] else 'unobserved'),'Observed tuples remain describable when unexpected; no native field invented for K controls.'),
          'joint_causal':requirement('satisfied' if result['capture_sufficient'] and result['graph_valid'] and reqs['schedule.causal']['status']=='satisfied' else 'unobserved','Requires interpretable causal evidence; all attempted cases remain registered.')}
    return report


def build_graph(events,raw):
    graph={e['record_id']:set(e['parents']) for e in events}; phases={e['record_id']:e['phase'] for e in events}
    errors=[]; prior_sink={}; prior_native={}
    for phase in ('P1','P2'):
        if phase not in raw: continue
        item=raw[phase]
        sink=item['sink']
        if sink and sink['requirements']['sink.primitives']['status']=='satisfied':
            last=None
            for e in sorted(sink['facts']['events'],key=lambda x:x['seq']):
                key='sink:'+str(e['seq'])
                if key in prior_sink and prior_sink[key]!=e:
                    errors.append('Changed historical sink event '+key)
                prior_sink[key]=e
                graph.setdefault(key,set())
                if last: graph[key].add(last)
                phases.setdefault(key,phase); last=key
                if e['kind']=='receipt' and isinstance(e['data'],dict):
                    request=e['data'].get('request',{})
                    for record in events:
                        if record['kind'] in ('dispatch_started','revocation_invoked') and record['payload']['request_id']==request.get('id'):
                            graph[key].add(record['record_id'])
        if item['native']:
            last=None
            for e in item['native']['events']:
                key='native:'+str(native_id(e['event_id']))
                if key in prior_native and prior_native[key]!=e: errors.append('Changed native prefix '+key)
                prior_native[key]=e
                graph.setdefault(key,set())
                if last: graph[key].add(last)
                phases.setdefault(key,e['phase']); last=key
    producers=defaultdict(list)
    for e in events: producers[e['producer_id']].append(e)
    for records in producers.values():
        for earlier,later in zip(sorted(records,key=lambda e:e['sequence']),sorted(records,key=lambda e:e['sequence'])[1:]):
            graph[later['record_id']].add(earlier['record_id'])
    for child,parents in graph.items():
        for parent in parents:
            if parent not in graph: errors.append('Unresolved causal reference '+parent)
            elif PHASES[phases[parent]]>PHASES[phases[child]]: errors.append('Future-phase causal reference '+parent+' -> '+child)
    visiting,visited=set(),set()
    def visit(node):
        if node in visiting: raise ArtifactError('Cyclic causal graph')
        if node in visited or node not in graph: return
        visiting.add(node)
        for parent in graph[node]: visit(parent)
        visiting.remove(node); visited.add(node)
    try:
        for node in graph: visit(node)
    except (ArtifactError,RecursionError) as e: errors.append(str(e))
    return graph,errors


def precedes(graph,a,b):
    todo=list(graph.get(b,())); seen=set()
    while todo:
        node=todo.pop()
        if node==a: return True
        if node not in seen:
            seen.add(node); todo.extend(graph.get(node,()))
    return False


def analyze_phase(bundle,c,b,events_id,events,raw,phase,graph,graph_ok):
    data=raw[phase]; req={}; facts={}; reference={}
    ev=[e for e in events if PHASES[e['phase']]<=PHASES[phase]]
    by=defaultdict(list)
    for e in ev: by[e['kind']].append(e)
    cap=data['capture']; cut=cap.get('cut_id','unavailable') if isinstance(cap,dict) and isinstance(cap.get('cut_id'),str) and cap.get('cut_id') else 'unavailable'
    boundary=cap.get('boundary_id','unavailable') if isinstance(cap,dict) and isinstance(cap.get('boundary_id'),str) and cap.get('boundary_id') else 'unavailable'
    def er(e): return ref(events_id,'/records/'+e['record_id'],e['record_id'],e['phase'],cut,boundary)
    def sr(seq): return ref(data['sink_id'],'/events/'+str(seq),seq,phase,cut,boundary)
    def nr(e): return ref(data['native_id'],'/events/'+str(e['event_id']),e['event_id'],e['phase'],cut,boundary)
    cr=ref(data['capture_id'] or 'unavailable','/',cut,phase,cut,boundary)
    def fact(field,value,refs=()): reference[field]={'value':value,'evidence_refs':list({canonical(r):r for r in refs}.values())}
    native=c['case_kind']=='native_activity'
    sink=data['sink']; sf=sink['facts'] if sink else None
    facts['sink_usable']=bool(sink and all(sink['requirements']['sink.'+k]['status']=='satisfied' for k in ('readable','schema','primitives','event_accounting','effect_bijection')))
    if sink:
        for key,value in sink['requirements'].items():
            req[key]={**value,'evidence_refs':[ref(data['sink_id'],'/',data['sink_id'],phase,cut,boundary)]}
        facts['sink']={k:v for k,v in sf.items() if k not in ('tables',)}
    else: req['sink.available']=requirement('unobserved','No valid phase-specific saved sink.')
    # Native chain and exact tuple components stay distinct.
    n=data['native']; complete_native=False
    tuple_={'cancellation_observation':None,'workflow_promise':None,'worker_settlement':None,'activity_terminal':None,'workflow_status':None}
    if native:
        complete_native,nreq,nfacts=inspect_native(n,b,data['native_error'])
        req.update(nreq); facts.update(nfacts)
        for kind,key in [('cancellation_observed','cancellation_observation'),('promise_settled','workflow_promise'),('worker_settled','worker_settlement')]:
            records=by[kind]
            tuple_[key]=records[-1]['payload'] if len(records)==1 else None
        terminal=[e for e in (n or {}).get('events',[]) if e['type'] in ('activity_completed','activity_failed','activity_canceled','activity_timed_out')]
        wterminal=[e for e in (n or {}).get('events',[]) if e['type'] in ('workflow_completed','workflow_failed','workflow_canceled','workflow_timed_out')]
        tuple_['activity_terminal']=terminal[0] if len(terminal)==1 else None
        tuple_['workflow_status']=wterminal[0] if len(wterminal)==1 else ('running' if complete_native else None)
        req['native.mapping']=requirement('unobserved','Exact observed Temporal mapping remains open.')
        if c['mapping']:
            expected=c['mapping']['tuples'].get(phase)
            simplified={k:(v['type'] if isinstance(v,dict) and 'type' in v else v) for k,v in tuple_.items()}
            req['native.mapping']=requirement('satisfied' if expected==simplified else 'unsatisfied','Comparison to explicitly synthetic mapping only; no native qualification.')
        req['native.hold']=requirement('satisfied' if phase=='P1' and len(by['workflow_hold'])==1 and not wterminal else ('satisfied' if phase=='P2' and len(wterminal)==1 else 'unsatisfied' if wterminal and phase=='P1' else 'unobserved'),'Primary Workflow remains held; postrelease terminal is separate.' if not (wterminal and phase=='P1') else 'Unexpected early Workflow terminal is retained as an adverse outcome.')
        if by['promise_settled']:
            e=by['promise_settled'][-1]; fact('activity_call','settled_with_recorded_'+('result' if e['payload']['disposition']=='result' else 'failure'),[er(e)])
        else: fact('activity_call','unresolved')
        if len(terminal)==1 and req.get('native.linkage',{}).get('status')=='satisfied': fact('activity_execution','native_terminal_record',[nr(terminal[0])])
        elif len(by['worker_settled'])==1: fact('activity_execution','worker_invocation_settled',[er(by['worker_settled'][0])])
        elif len(by['finally_point'])==1: fact('activity_execution','last_instrumented_point',[er(by['finally_point'][0])])
        else: fact('activity_execution','unresolved')
        if len(wterminal)==1: fact('workflow_execution','exact_terminal_status',[nr(wterminal[0])])
        elif complete_native: fact('workflow_execution','running',[ref(data['native_id'],'/coverage','coverage',phase,cut,boundary)])
        else: fact('workflow_execution','unresolved')
    else:
        req['native.applicability']=requirement('not_applicable','Sink-only control has no native lifecycle.')
    facts['native_tuple']=tuple_ if native else None
    capture_ok,capreq=inspect_capture(cap,c,b,phase,ev,sink,n,complete_native,graph,graph_ok)
    req.update(capreq)
    # Schedule commands and observed system behavior have different gates.
    schedule,causal,outcomes=inspect_schedule(c,phase,by,sf,graph,graph_ok,capture_ok)
    req.update(schedule); req['schedule.causal']=causal; req.update(outcomes)
    facts['dispatch_attempts']=len(by['dispatch_started'])
    facts['transport_uncertain']=any(e['payload']['uncertain'] for e in by['transport_error'])
    responses=by['cancel_response']
    if len(responses)==1:
        response=responses[0]
        linked=[e for e in by['cancel_submitted'] if e['payload']['call_id']==response['payload']['call_id'] and precedes(graph,e['record_id'],response['record_id'])]
        fact('cancellation_request',response['payload']['outcome'],[er(response)]+[er(e) for e in linked]) if linked else fact('cancellation_request','unresolved')
    elif not native and not any(by[k] for k in ('cancel_invoked','cancel_submitted','cancel_response')): fact('cancellation_request','not_requested',[ref('case','/case_kind','case_kind','P0',cut,boundary)])
    elif capture_ok and not by['cancel_invoked'] and not by['cancel_submitted']: fact('cancellation_request','not_requested',[cr])
    else: fact('cancellation_request','unresolved')
    valid_sink=bool(facts['sink_usable'] and sink['requirements']['sink.scope']['status']=='satisfied')
    effects=sf['effects'] if sf else []; revocations=sf['revocations'] if sf else []
    if valid_sink and effects: fact('effect_existence','present',[sr(e['event_seq']) for e in effects])
    elif valid_sink and capture_ok: fact('effect_existence','absent_with_complete_bounded_evidence',[cr,ref(data['sink_id'],'/effects','effects',phase,cut,boundary)])
    else: fact('effect_existence','unresolved')
    if valid_sink and revocations: fact('fence_existence','present',[sr(e['seq']) for e in revocations])
    elif valid_sink and capture_ok: fact('fence_existence','absent_with_complete_bounded_evidence',[cr,ref(data['sink_id'],'/events','events',phase,cut,boundary)])
    else: fact('fence_existence','unresolved')
    matching=[]
    for e in by['fence_receipt']:
        p=e['payload']
        for revoke in revocations:
            if not isinstance(revoke.get('data'),dict) or not isinstance(revoke['data'].get('result'),dict): continue
            if p['sink_seq']==revoke['seq'] and p['request_id']==revoke['data']['request_id'] and all(p[k]==revoke['data']['result'].get(k) for k in ('root','withdrawn_epoch','new_epoch')) and precedes(graph,'sink:'+str(revoke['seq']),e['record_id']): matching.append((e,revoke))
    if valid_sink and len(matching)==1: fact('fence','confirmed_for_fixture_scope',[er(matching[0][0]),sr(matching[0][1]['seq'])])
    else: fact('fence','unresolved')
    for field,anchor_kind in [('effect_order_vs_request','cancel_invoked'),('effect_order_vs_observed_cancellation','cancellation_observed')]:
        if reference['effect_existence']['value']=='absent_with_complete_bounded_evidence': fact(field,'not_applicable_no_effect',reference['effect_existence']['evidence_refs'])
        elif not valid_sink or not effects: fact(field,'unresolved')
        elif not native and not any(by[k] for k in ('cancel_invoked','cancel_submitted','cancel_response','cancellation_observed')): fact(field,'no_request' if field.endswith('request') else 'no_observation',[ref('case','/case_kind','case_kind','P0',cut,boundary)])
        elif len(by[anchor_kind])==1 and graph_ok:
            anchor=by[anchor_kind][0]; orders=[]
            for e in effects:
                source='sink:'+str(e['event_seq'])
                orders.append('before' if precedes(graph,source,anchor['record_id']) else 'after' if precedes(graph,anchor['record_id'],source) else 'unresolved')
            value=orders[0] if len(set(orders))==1 else 'unresolved'
            fact(field,value,[er(anchor)]+[sr(e['event_seq']) for e in effects]+causal_refs(graph,[anchor['record_id']]+['sink:'+str(e['event_seq']) for e in effects],ev,er,sr))
        elif capture_ok and not by[anchor_kind] and not by['cancel_submitted']: fact(field,'no_request' if field.endswith('request') else 'no_observation',[cr])
        else: fact(field,'unresolved')
    if reference['effect_existence']['value']=='absent_with_complete_bounded_evidence': fact('effect_order_vs_fence','not_applicable_no_effect',reference['effect_existence']['evidence_refs'])
    elif valid_sink and effects and len(revocations)==1:
        orders=['before' if e['event_seq']<revocations[0]['seq'] else 'after' for e in effects]
        fact('effect_order_vs_fence',orders[0] if len(set(orders))==1 else 'unresolved',[sr(e['event_seq']) for e in effects]+[sr(revocations[0]['seq'])])
    elif reference['fence_existence']['value']=='absent_with_complete_bounded_evidence' and effects:
        fact('effect_order_vs_fence','no_fence_in_complete_window',reference['fence_existence']['evidence_refs']+[sr(e['event_seq']) for e in effects])
    else: fact('effect_order_vs_fence','unresolved')
    return {'requirements':req,'observed':facts,'reference':reference,'capture_sufficient':capture_ok}


def causal_refs(graph,ends,events,er,sr):
    # Include every explicit producer node on any ancestor path: conservative support.
    seen=set(); todo=list(ends); byid={e['record_id']:e for e in events}
    while todo:
        node=todo.pop()
        if node in seen: continue
        seen.add(node); todo.extend(graph.get(node,()))
    return [er(byid[x]) for x in sorted(seen) if x in byid]


def inspect_native(n,b,error):
    req={}; facts={}
    if n is None:
        req['native.schema']=requirement('unobserved' if error and 'Missing' in error else 'unsatisfied',error or 'Native history missing.')
        return False,req,facts
    req['native.schema']=requirement('satisfied','Synthetic normalized native schema verified, not provider-qualified.')
    events=n['events']; cov=n['coverage']; pages=cov['pages']; coverage=False
    try:
        if type(cov['complete_prefix']) is not bool or not cov['complete_prefix']: raise ArtifactError('No complete-prefix declaration')
        if not isinstance(pages,list) or not pages: raise ArtifactError('No pagination chain')
        expected_token=None; last=0
        for i,page in enumerate(pages):
            exact(page,('input_token','output_token','first_event_id','last_event_id'))
            if page['input_token']!=expected_token or (i<len(pages)-1 and not page['output_token']): raise ArtifactError('Broken pagination token chain')
            first,end=native_id(page['first_event_id']),native_id(page['last_event_id'])
            if first!=last+1 or end<first: raise ArtifactError('Incomplete page boundary')
            expected_token=page['output_token']; last=end
        if expected_token is not None or last!=native_id(cov['final_event_id']) or native_id(cov['closing_boundary_event_id'])!=last:
            raise ArtifactError('Missing closing boundary or final token')
        if len(events)!=last or any(native_id(e['event_id'])!=i for i,e in enumerate(events,1)): raise ArtifactError('History does not match declared full prefix')
        coverage=True; req['native.coverage']=requirement('satisfied','Token chain, prefix and closing boundary agree under synthetic schema.')
    except (ArtifactError,TypeError,KeyError) as e: req['native.coverage']=requirement('unobserved',str(e))
    schedule=[e for e in events if e['type']=='activity_scheduled']; starts=[e for e in events if e['type']=='activity_started']
    terminals=[e for e in events if e['type'] in ('activity_completed','activity_failed','activity_canceled','activity_timed_out')]
    try:
        if len(schedule)!=1 or len(starts)!=1 or len(terminals)!=1: raise ArtifactError('Expected one schedule/start/terminal chain')
        s,a,t=schedule[0],starts[0],terminals[0]; binding=b['native']
        if s['attributes']['activity_id']!=binding['activity_id'] or native_id(s['event_id'])!=native_id(binding['scheduled_event_id']) or native_id(a['event_id'])!=native_id(binding['started_event_id']): raise ArtifactError('Native schedule/start binding differs')
        if native_id(a['attributes']['scheduled_event_id'])!=native_id(s['event_id']) or native_id(t['attributes']['scheduled_event_id'])!=native_id(s['event_id']) or native_id(t['attributes']['started_event_id'])!=native_id(a['event_id']): raise ArtifactError('Wrong native scheduled/start reference')
        if not native_id(s['event_id'])<native_id(a['event_id'])<native_id(t['event_id']): raise ArtifactError('Invalid native chain order')
        if a['attributes']['attempt']!=binding['attempt']: raise ArtifactError('Attempt binding differs')
        req['native.linkage']=requirement('satisfied','Schedule/start/terminal references match this run and attempt.')
    except (ArtifactError,TypeError,KeyError) as e: req['native.linkage']=requirement('unsatisfied' if terminals or starts else 'unobserved',str(e))
    req['outcome.native_attempts']=requirement('satisfied' if len(starts)==1 and starts[0]['attributes']['attempt']==1 else 'unsatisfied','Observed retry deviations are retained, independently of configured retry policy.')
    facts['native_attempts']=[e['attributes']['attempt'] for e in starts]
    return coverage,req,facts


def inspect_capture(cap,c,b,phase,ev,sink,n,complete_native,graph,graph_ok):
    req={}
    try:
        if cap is None: raise ArtifactError('Capture certificate missing')
        exact(cap,('schema_version','case_id','operation_id','phase','cut_id','boundary_id','interval',
                   'producer_watermarks','ack_refs','sink_transaction','native_final_event_id',
                   'complete_producer_accounting','logs_flushed','no_detached_work','queued','in_flight','uncertain',
                   'interventions','completeness_limits'))
        if any(not isinstance(cap[k],str) or not cap[k] for k in ('cut_id','boundary_id')): raise ArtifactError('Invalid capture identities')
        if cap['schema_version']!=VERSION or cap['case_id']!=c['case_id'] or cap['operation_id']!=c['operation_id'] or cap['phase']!=phase:
            raise ArtifactError('Capture identity, scope or phase mismatch')
        for k in ('complete_producer_accounting','logs_flushed','no_detached_work'):
            if type(cap[k]) is not bool: raise ArtifactError('Capture declarations must be boolean')
        for k in ('queued','in_flight','uncertain','interventions','completeness_limits'):
            if not isinstance(cap[k],list): raise ArtifactError('Capture work accounting must be explicit lists')
        exact(cap['interval'],('start_ref','end_ref'))
        byid={e['record_id']:e for e in ev}
        start,end=byid.get(cap['interval']['start_ref']),byid.get(cap['interval']['end_ref'])
        if not start or not end or start['kind']!='capture_start' or end['kind']!='capture_end' or start['payload']['cut_id']!=cap['cut_id'] or end['payload']['cut_id']!=cap['cut_id'] or not precedes(graph,start['record_id'],end['record_id']):
            raise ArtifactError('Capture interval lacks linked start/end records')
        if not isinstance(cap['producer_watermarks'],dict) or not isinstance(cap['ack_refs'],list): raise ArtifactError('Invalid producer boundaries')
        relevant={e['producer_id'] for e in ev if e['kind'] not in ('capture_start','capture_end','diagnostic')}
        if set(cap['producer_watermarks'])!=relevant: raise ArtifactError('Missing or extra producer watermark')
        for producer,position in cap['producer_watermarks'].items():
            if not integer(position,1): raise ArtifactError('Invalid producer watermark')
            records=[e for e in ev if e['producer_id']==producer]
            if max(e['sequence'] for e in records)!=position: raise ArtifactError('Producer records exceed or fail boundary')
            if len(records)!=position or any(e['sequence']!=i for i,e in enumerate(sorted(records,key=lambda e:e['sequence']),1)): raise ArtifactError('Producer prefix has gaps')
            acks=[byid.get(a) for a in cap['ack_refs']]
            matching=[a for a in acks if a and a['kind']=='flush_ack' and a['producer_id']==producer and a['payload']['cut_id']==cap['cut_id'] and a['payload']['through_sequence']==position]
            if len(matching)!=1: raise ArtifactError('Missing exact producer flush acknowledgment')
            if not precedes(graph,start['record_id'],matching[0]['record_id']) or not precedes(graph,matching[0]['record_id'],end['record_id']): raise ArtifactError('Flush acknowledgment lies outside capture interval')
        exact(cap['sink_transaction'],('transaction_id','single_read_transaction','table_boundaries','event_boundary'))
        tr=cap['sink_transaction']
        if type(tr['single_read_transaction']) is not bool or not tr['single_read_transaction'] or not tr['transaction_id']:
            raise ArtifactError('No explicit consistent read transaction')
        if not isinstance(tr['table_boundaries'],dict) or set(tr['table_boundaries'])!={'authority','grants','tickets','events','effects'} or set(tr['table_boundaries'].values())!={tr['transaction_id']}:
            raise ArtifactError('Mixed SQLite table snapshots')
        if not sink or not sink['facts']['events'] or tr['event_boundary']!=max(x['seq'] for x in sink['facts']['events']): raise ArtifactError('Sink boundary does not match saved ledger')
        if c['case_kind']=='native_activity':
            if not n or not complete_native or cap['native_final_event_id']!=n['coverage']['final_event_id']: raise ArtifactError('Native history boundary unavailable or mismatched')
            if not any(e['kind']=='worker_settled' and precedes(graph,e['record_id'],start['record_id']) for e in ev) or not any(e['type'] in ('activity_completed','activity_failed','activity_canceled','activity_timed_out') for e in n['events']): raise ArtifactError('Worker settlement and Activity terminal required independently')
            terminals=[e for e in n['events'] if e['type'] in ('activity_completed','activity_failed','activity_canceled','activity_timed_out')]
            if not all(precedes(graph,'native:'+str(native_id(e['event_id'])),start['record_id']) for e in terminals): raise ArtifactError('Native terminal not observed before capture start')
            if phase=='P1':
                if any(e['kind'] in ('observation_release','shutdown_request') for e in ev): raise ArtifactError('Primary capture occurs after release or cleanup')
                if not any(e['kind']=='workflow_hold' for e in ev) or any(e['type'].startswith('workflow_') and e['type']!='workflow_started' for e in n['events']): raise ArtifactError('Workflow not held at primary capture')
            else:
                releases=[e for e in ev if e['kind']=='observation_release']; received=[e for e in ev if e['kind']=='observation_release_received']
                if len(releases)!=1 or len(received)!=1 or releases[0]['payload']!=received[0]['payload'] or not precedes(graph,releases[0]['record_id'],received[0]['record_id']): raise ArtifactError('Missing case-bound release receipt')
        elif cap['native_final_event_id'] is not None: raise ArtifactError('Invented sink-only native boundary')
        started=[e for e in ev if e['kind']=='dispatch_started']
        committed={e['data']['request_id'] for e in sink['facts']['events'] if e['kind'] in ('effect','denied','duplicate') and isinstance(e.get('data'),dict) and isinstance(e['data'].get('request_id'),str)}
        response_rows=[e for e in ev if e['kind']=='bridge_response']
        responses={e['payload']['request_id'] for e in response_rows}
        started_ids=[e['payload']['request_id'] for e in started]
        if len(started_ids)!=len(set(started_ids)) or len(responses)!=len(response_rows): raise ArtifactError('Ambiguous repeated dispatch/response identity')
        for response in response_rows:
            rid=response['payload']['request_id'];observed=response['payload']['result']
            terminals=[e for e in sink['facts']['events'] if e['kind'] in ('effect','denied','duplicate') and isinstance(e.get('data'),dict) and e['data'].get('request_id')==rid]
            if rid not in started_ids or len(terminals)!=1 or any(terminals[0]['data'].get('result',{}).get(k)!=v for k,v in observed.items()): raise ArtifactError('Bridge response conflicts with saved committed terminal or dispatch')
        known_no_commit=set()
        for dispatch in started:
            rid=dispatch['payload']['request_id']
            resolutions=[e for e in ev if e['kind']=='transport_error' and e['payload']['uncertain'] is False and e['payload']['request_id']==rid and precedes(graph,dispatch['record_id'],e['record_id']) and precedes(graph,e['record_id'],start['record_id'])]
            if len(resolutions)==1: known_no_commit.add(rid)
            terminals=[e for e in sink['facts']['events'] if e['kind'] in ('effect','denied','duplicate') and isinstance(e.get('data'),dict) and e['data'].get('request_id')==rid]
            for terminal in terminals:
                node='sink:'+str(terminal['seq'])
                if not precedes(graph,dispatch['record_id'],node) or not precedes(graph,node,start['record_id']): raise ArtifactError('Committed dispatch resolution is not causally before capture')
        if any(rid not in committed|known_no_commit for rid in started_ids): raise ArtifactError('Dispatch lacks committed resolution or explicit known-no-commit record')
        if any(rid not in started_ids for rid in sink['facts']['execute_request_ids']): raise ArtifactError('Execute receipt has no accounted bridge dispatch')
        if any(e['kind']=='transport_error' and e['payload']['uncertain'] and e['payload']['request_id'] not in committed for e in ev): raise ArtifactError('Unresolved uncertain commit contradicts capture accounting')
        if not graph_ok: raise ArtifactError('Capture causal references are not valid')
        req['capture.boundaries']=requirement('satisfied','Phase, transaction, source positions and flush records agree.')
    except (ArtifactError,KeyError,TypeError,ValueError) as e:
        req['capture.boundaries']=requirement('unobserved',str(e))
    stable=bool(isinstance(cap,dict) and all(cap.get(k) is True for k in ('complete_producer_accounting','logs_flushed','no_detached_work')) and all(cap.get(k)==[] for k in ('queued','in_flight','uncertain','interventions','completeness_limits')))
    req['capture.stability']=requirement('satisfied' if stable else 'unobserved','Passive stable-operation certificate; not producer attestation.' if stable else 'Pending work, intervention or incomplete stability declaration prevents absence/cessation credit.')
    return stable and req['capture.boundaries']['status']=='satisfied',req


def inspect_schedule(c,phase,by,sf,graph,graph_ok,capture_ok):
    cell=c['cell']; native=c['case_kind']=='native_activity'; req={}; outcome={}
    required=['cancel_invoked'] if native else []
    if cell in ('M1','M2','M3','M4'): required+=['continuation_release']
    if cell in ('M3','M4','K2'): required+=['revocation_invoked']
    if phase=='P2': required+=['observation_release']
    issued=all(len(by[k])==1 for k in required)
    forbidden=['continuation_release'] if cell in ('C1','C4') else []
    if cell not in ('M3','M4','K2'): forbidden+=['revocation_invoked']
    if not native: forbidden+=['cancel_invoked','cancel_submitted','cancel_response']
    commands_ok=issued and not any(by[k] for k in forbidden)
    req['schedule.commands']=requirement('satisfied' if commands_ok else 'unsatisfied','Required controller commands issued exactly once and forbidden commands absent.' if commands_ok else 'Missing, duplicate or forbidden schedule command; actual outcomes retained.')
    causal='satisfied'; why='Required observation and linked-command sequence is present.'
    if native and (len(by['activity_started'])!=1 or len(by['cancellation_observed'])!=1): causal='unobserved'; why='Activity start or actual cancellation observation missing; heartbeats are insufficient.'
    def chain(nodes): return graph_ok and all(precedes(graph,a,b) for a,b in zip(nodes,nodes[1:]))
    if native and causal=='satisfied':
        if any(len(by[k])!=1 for k in ('cancel_invoked','cancel_submitted')):
            causal='unobserved';why='Cancellation invocation/submission observation missing.'
        else:
            started,invoked,submitted,observed=[by[k][0] for k in ('activity_started','cancel_invoked','cancel_submitted','cancellation_observed')]
            if not chain([started['record_id'],invoked['record_id'],submitted['record_id'],observed['record_id']]) or len({invoked['payload']['call_id'],submitted['payload']['call_id'],observed['payload']['call_id']})!=1:
                causal='unobserved';why='Start, invocation, submission and cancellation observation are not one linked call.'
    if cell in ('M1','M2','M3','M4') and causal=='satisfied':
        if len(by['continuation_release'])!=1 or len(by['continuation_received'])!=1 or not by['dispatch_started']:
            causal='unobserved'; why='Continuation release, receiver observation or dispatch missing.'
        else:
            nodes=[by['cancellation_observed'][0]['record_id'],by['continuation_release'][0]['record_id'],by['continuation_received'][0]['record_id'],by['dispatch_started'][0]['record_id']]
            if not chain(nodes) or by['continuation_release'][0]['payload']!=by['continuation_received'][0]['payload']:
                causal='unobserved'; why='Post-observation continuation causal chain not established.'
            if cell in ('M3','M4'):
                rev=sf['revocations'] if sf else []
                receipts=by['fence_receipt']
                if len(rev)!=1 or len(receipts)!=1 or not chain(['sink:'+str(rev[0]['seq']),receipts[0]['record_id'],by['continuation_release'][0]['record_id']]):
                    causal='unobserved'; why='Fence commit and linked receipt do not precede release.'
    if cell=='C4' and causal=='satisfied':
        effects=sf['effects'] if sf else []
        if len(effects)!=1 or any(len(by[k])!=1 for k in ('bridge_response','effect_ack','coordinator_ack','activity_hold_ready','cancel_invoked')):
            causal='unobserved'; why='Missing historical effect acknowledgment chain.'
        else:
            nodes=['sink:'+str(effects[0]['event_seq'])]+[by[k][0]['record_id'] for k in ('bridge_response','effect_ack','coordinator_ack','cancel_invoked')]
            effect_event=next((e for e in sf['events'] if e['seq']==effects[0]['event_seq']),None)
            expected_id=effect_event['data']['request_id'] if effect_event and isinstance(effect_event.get('data'),dict) else None
            linked=expected_id is not None and all(by[k][0]['payload']['request_id']==expected_id for k in ('bridge_response','effect_ack','coordinator_ack')) and by['effect_ack'][0]['payload']['sink_seq']==effects[0]['event_seq']
            if not linked or not chain(nodes) or not precedes(graph,by['activity_hold_ready'][0]['record_id'],by['cancel_invoked'][0]['record_id']):
                causal='unobserved'; why='Effect commit and active hold are not causally before invocation.'
    if cell=='K2':
        rev=sf['revocations'] if sf else []
        if len(rev)!=1 or len(by['fence_receipt'])!=1 or not by['dispatch_started'] or not chain(['sink:'+str(rev[0]['seq']),by['fence_receipt'][0]['record_id'],by['dispatch_started'][0]['record_id']]):
            causal='unobserved'; why='Sink-only fence/receipt/dispatch chain missing.'
    if native:
        submissions=by['cancel_submitted']; responses=by['cancel_response']
        req['cancellation.submission']=requirement('satisfied' if len(submissions)==1 else 'unobserved','Actual client submission record is separate from invocation-start; no submission inferred from intention.')
    if sf:
        want=0 if cell=='C1' else 1
        counts=(len(by['dispatch_started']),sf['execute_receipts'],sf['effect_rows'])
        want_effect=1 if cell in ('M1','M2','K1','C4') else 0
        count_ok=counts==(want,want,want_effect)
        # Extra observed work is adverse even when the remaining capture is incomplete.
        status='satisfied' if count_ok and capture_ok else 'unsatisfied' if counts[0]>want or counts[1]>want or counts[2]>want_effect else 'unobserved' if not capture_ok else 'unsatisfied'
        outcome['outcome.cardinality']=requirement(status,f'Observed dispatch/execute/effect counts {counts}; expected {(want,want,want_effect)}. Adverse outcomes remain included.')
        rev=sf['revocations']; den=sf['denials']
        fenced=cell in ('M3','M4','K2')
        fence_ok=len(rev)==(1 if fenced else 0)
        if fenced:
            execute_ids={x for x in sf['execute_request_ids'] if isinstance(x,str)}; execute_den=[d for d in den if isinstance(d.get('data'),dict) and d['data'].get('request_id') in execute_ids]
            denial_ok=len(execute_den)==1 and execute_den[0]['data']['result']=={'outcome':'denied','reason':'revoked'}
        else: denial_ok=not den
        outcome['outcome.sink_expected']=requirement('satisfied' if fence_ok and denial_ok and count_ok and capture_ok else ('unobserved' if not capture_ok and fence_ok and denial_ok else 'unsatisfied'),'Exact fence, cardinality and revoked-denial expectations checked; other denial causes get no protection credit.')
    else:
        outcome['outcome.cardinality']=requirement('unobserved','Sink evidence unavailable.')
    return req,requirement(causal,why),outcome


def check_cleanup(bundle,c):
    aid,cleanup=bundle.optional('cleanup','P3')
    try:
        if cleanup is None: raise ArtifactError('Cleanup record missing')
        exact(cleanup,('schema_version','case_id','operation_id','initial_error_ref','secondary_errors','shutdown_requested','shutdown_acknowledged','budget_expired','forced_actions','child_exits','outstanding','capture_errors'))
        if cleanup['schema_version']!=VERSION or cleanup['case_id']!=c['case_id'] or cleanup['operation_id']!=c['operation_id']: raise ArtifactError('Cleanup identity mismatch')
        for key in ('shutdown_requested','shutdown_acknowledged','budget_expired'):
            if type(cleanup[key]) is not bool: raise ArtifactError('Invalid cleanup boolean')
        for key in ('secondary_errors','forced_actions','child_exits','outstanding','capture_errors'):
            if not isinstance(cleanup[key],list): raise ArtifactError('Invalid cleanup record list')
        for e in cleanup['child_exits']:
            exact(e,('child_id','exit_code'))
            if not isinstance(e['child_id'],str) or type(e['exit_code']) is not int: raise ArtifactError('Invalid child exit')
        ok=cleanup['shutdown_requested'] and cleanup['shutdown_acknowledged'] and not cleanup['budget_expired'] and not cleanup['forced_actions'] and not cleanup['outstanding'] and not cleanup['secondary_errors'] and bool(cleanup['child_exits']) and all(x['exit_code']==0 for x in cleanup['child_exits'])
        return {'requirement':requirement('satisfied' if ok else 'unsatisfied','Finite normal synthetic shutdown recorded.' if ok else 'Shutdown error, missing acknowledgment, forced action or uncertain work blocks acceptance.'),'record':cleanup}
    except (ArtifactError,KeyError,TypeError) as e: return {'requirement':requirement('unobserved',str(e))}


def check_late_evidence(c,events,raw,report):
    for phase,result in report['phases'].items():
        ids={e['payload']['request_id'] for e in events if e['kind']=='dispatch_started' and PHASES[e['phase']]<=PHASES[phase]}
        late=[e for e in events if PHASES[e['phase']]>PHASES[phase] and e['kind']=='bridge_response' and e['payload']['request_id'] in ids]
        cap=raw[phase]['capture']
        # A later receipt alone is not a late commit. Explicit source events after the
        # certified sink boundary, linked to a previously resolved request, contradict it.
        later_events=[]
        for later_phase,data in raw.items():
            if PHASES[later_phase]<=PHASES[phase] or not data['sink'] or not cap: continue
            boundary=cap.get('sink_transaction',{}).get('event_boundary',0)
            later_events += [e for e in data['sink']['facts']['events'] if e['seq']>boundary and e['kind']=='effect' and isinstance(e.get('data'),dict) and e['data'].get('request_id') in ids]
        contradiction=bool(later_events and result['capture_sufficient'])
        result['requirements']['capture.late_contradiction']=requirement('unsatisfied' if contradiction else 'satisfied','Late commit from previously accounted dispatch contradicts its saved no-pending certificate.' if contradiction else 'No linked later commit contradicting this interval is present in supplied artifacts; this is not a universal guarantee.')
        if contradiction:
            result['capture_sufficient']=False
            for field,item in result['reference'].items():
                if item['value'] in ('absent_with_complete_bounded_evidence','no_fence_in_complete_window','no_request','no_observation','not_applicable_no_effect'):
                    item['value']='unresolved'; item['evidence_refs']=[]


def compare_phases(c,raw,report):
    if c['case_kind']=='sink_only': return requirement('not_applicable','Sink-only controls have no P2.')
    first=raw['P1']['sink']; second=raw['P2']['sink']
    if not first or not second: return requirement('unobserved','Missing one phase; no evidence is borrowed from later records.')
    if c['cell']=='C4':
        equal=first['facts']['effects']==second['facts']['effects'] and len(first['facts']['effects'])==1
        return requirement('satisfied' if equal else 'unsatisfied','Same effect identity, payload, root, epoch and linkage at both cuts; uninterrupted preservation is not inferred from two snapshots.' if equal else 'Historical effect differs or is absent at one observation.')
    return requirement('satisfied','Phase-specific facts kept separately; postrelease evidence does not repair P1.')
