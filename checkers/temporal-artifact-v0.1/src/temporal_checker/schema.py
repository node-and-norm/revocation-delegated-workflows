"""Explicit synthetic canonical schemas. NOT an adapter for a native exporter."""
from __future__ import annotations
from .artifacts import ArtifactError, VERSION, PHASES, exact, integer, native_id

CELLS = {'M1','M2','M3','M4','K1','K2','C1','C4'}
MODES = {'TRY_CANCEL','WAIT_CANCELLATION_COMPLETED'}
BUDGETS = ('activity_start','cancellation_observation','execute_response','settlement',
           'p1_capture','workflow_release','p2_capture','cleanup','workflow_hold','overall')
PAYLOADS = {
 'revocation_invoked': ('request_id',), 'activity_started': (), 'heartbeat': (), 'cancel_invoked': ('call_id',),
 'cancel_submitted': ('call_id',), 'cancel_response': ('call_id','outcome','details'),
 'cancellation_observed': ('call_id',), 'continuation_release': ('release_id',),
 'continuation_received': ('release_id',), 'dispatch_intended': ('request_id',),
 'dispatch_started': ('request_id',), 'bridge_response': ('request_id','result'),
 'transport_error': ('request_id','uncertain'), 'effect_ack': ('request_id','sink_seq'),
 'coordinator_ack': ('request_id',), 'activity_hold_ready': (),
 'promise_settled': ('disposition','details'), 'finally_point': (),
 'worker_settled': ('disposition','details'), 'workflow_hold': (),
 'fence_receipt': ('request_id','sink_seq','root','withdrawn_epoch','new_epoch'),
 'observation_release': ('release_id',), 'observation_release_received': ('release_id',),
 'capture_start': ('cut_id',), 'capture_end': ('cut_id',),
 'flush_ack': ('cut_id','through_sequence'), 'shutdown_request': (), 'shutdown_response': (),
 'diagnostic': ('namespace','data'),
}



def synthetic_result(value):
    """Closed synthetic payload only; production result/failure adapter is open."""
    if not isinstance(value,dict): raise ArtifactError('result/details must be object')
    if not value: return
    if set(value)=={'synthetic'} and type(value['synthetic']) is bool: return
    if set(value)=={'type','message'} and all(isinstance(x,str) for x in value.values()): return
    raise ArtifactError('unsupported nested result/failure fields')


def validate_case(c):
    exact(c, ('schema_version','protocol_version','case_id','operation_id','case_kind','cell',
              'study_phase','origin','pins','intended_binding','configuration','authority_scope',
              'phases','view_permissions','mapping','registered_before_dispatch','attempt_id'))
    if c['schema_version'] != VERSION or c['protocol_version'] != '0.3':
        raise ArtifactError('unsupported case/protocol version')
    if c['origin'] != 'synthetic' or c['study_phase'] != 'synthetic':
        raise ArtifactError('only explicitly synthetic artifacts are supported by this adapter')
    for k in ('case_id','operation_id','attempt_id'):
        if not isinstance(c[k], str) or not c[k]: raise ArtifactError('empty/nonstring identity')
    if c['cell'] not in CELLS or c['case_kind'] not in ('native_activity','sink_only'):
        raise ArtifactError('unknown case kind/cell')
    native = c['case_kind'] == 'native_activity'
    if native != (c['cell'] not in ('K1','K2')):
        raise ArtifactError('case kind does not match cell')
    if c['phases'] != (['P1','P2'] if native else ['P1']):
        raise ArtifactError('invalid planned phases')
    exact(c['pins'], ('sdk','gateway_sha256','native_adapter','exporter_status'))
    if c['pins']['sdk']!='1.25.0' or c['pins']['gateway_sha256']!='98445edd61af21bc5c740053f8a93f6c179e4c5efa7b28dd7363e779b8f059a9':
        raise ArtifactError('unsupported SDK or historical gateway source pin')
    if c['pins']['native_adapter'] != 'synthetic-normalized-v1' or c['pins']['exporter_status'] != 'unqualified':
        raise ArtifactError('unsupported adapter or claimed exporter qualification')
    exact(c['intended_binding'], ('workflow_id','activity_id') if native else ())
    exact(c['configuration'], ('mode','behavior','maximum_attempts','activity_scope','hold_scope','deadlines'))
    cfg = c['configuration']
    behavior = {'M1':'continue','M2':'continue','M3':'continue_fenced','M4':'continue_fenced',
                'K1':'sink_live','K2':'sink_fenced','C1':'cooperative','C4':'historical'}[c['cell']]
    if cfg['behavior'] != behavior: raise ArtifactError('unknown or wrong behavior label')
    if native and cfg['mode'] not in MODES: raise ArtifactError('unknown native mode')
    fixed_mode = {'M1':'TRY_CANCEL','M2':'WAIT_CANCELLATION_COMPLETED','M3':'TRY_CANCEL','M4':'WAIT_CANCELLATION_COMPLETED'}.get(c['cell'])
    if fixed_mode and cfg['mode'] != fixed_mode: raise ArtifactError('cell mode mismatch')
    if not native and any(cfg[k] is not None for k in ('mode','maximum_attempts','activity_scope','hold_scope')):
        raise ArtifactError('fabricated sink-only native configuration')
    exact(cfg['deadlines'], BUDGETS)
    for value in cfg['deadlines'].values():
        if value is not None and (type(value) not in (int,float) or value <= 0):
            raise ArtifactError('budget must be positive finite seconds or explicitly unset')
    exact(c['authority_scope'], ('root','epoch','scope','actor','grant','ticket','payload'))
    exact(c['view_permissions'], ('sink','fence_receipt','client','worker','native','bridge'))
    if any(type(v) is not bool for v in c['view_permissions'].values()): raise ArtifactError('permission must be boolean')
    if type(c['registered_before_dispatch']) is not bool: raise ArtifactError('registration flag must be boolean')
    if c['mapping'] is not None:
        exact(c['mapping'], ('schema_version','kind','tuples'))
        if c['mapping']['schema_version'] != VERSION or c['mapping']['kind'] != 'synthetic_test_oracle':
            raise ArtifactError('only synthetic mapping oracles supported; no observed native qualification')
        if not isinstance(c['mapping']['tuples'],dict) or set(c['mapping']['tuples'])-set(c['phases']):
            raise ArtifactError('mapping tuples must be a phase-keyed object')
        for value in c['mapping']['tuples'].values():
            exact(value, ('cancellation_observation','workflow_promise','worker_settlement','activity_terminal','workflow_status'))
    return c


def validate_binding(b, c):
    exact(b, ('schema_version','case_id','operation_id','native','launch_ref','start_ref'))
    if b['schema_version'] != VERSION or b['case_id'] != c['case_id'] or b['operation_id'] != c['operation_id']:
        raise ArtifactError('binding case mismatch')
    if c['case_kind'] == 'sink_only':
        if b['native'] != {} or b['launch_ref'] is not None or b['start_ref'] is not None:
            raise ArtifactError('fabricated sink-only observed binding')
        return b
    n = b['native']
    exact(n, ('workflow_id','run_id','activity_id','scheduled_event_id','started_event_id','attempt','mode'))
    for key in ('workflow_id','activity_id'):
        if n[key] != c['intended_binding'][key]: raise ArtifactError('observed binding differs from preregistration')
    if not isinstance(n['run_id'], str) or not n['run_id']: raise ArtifactError('missing run ID')
    native_id(n['scheduled_event_id']); native_id(n['started_event_id'])
    if b['launch_ref']!='native:1' or b['start_ref']!='native:'+str(native_id(n['started_event_id'])):
        raise ArtifactError('launch/start references do not match declared native linkage')
    if not integer(n['attempt'],1) or n['mode'] != c['configuration']['mode']:
        raise ArtifactError('attempt/mode binding invalid')
    return b


def validate_events(events, c, b):
    if not isinstance(events,list): raise ArtifactError('events must be list')
    ids, positions = set(), set()
    for e in events:
        exact(e, ('record_id','producer_id','sequence','case_id','operation_id','phase','kind','payload','parents','binding'), ('wall_clock',))
        if not isinstance(e['record_id'],str) or not e['record_id'] or e['record_id'] in ids:
            raise ArtifactError('duplicate or invalid logical record ID')
        if e['record_id'].startswith(('sink:','native:')): raise ArtifactError('producer ID uses reserved graph namespace')
        ids.add(e['record_id'])
        if not isinstance(e['producer_id'],str) or not integer(e['sequence'],1): raise ArtifactError('invalid producer position')
        pos = (e['producer_id'],e['sequence'])
        if pos in positions: raise ArtifactError('duplicate producer position')
        positions.add(pos)
        if e['case_id'] != c['case_id'] or e['operation_id'] != c['operation_id'] or e['binding'] != b['native']:
            raise ArtifactError('event operation/run/attempt binding mismatch')
        if e['phase'] not in PHASES or e['kind'] not in PAYLOADS:
            raise ArtifactError('unknown event kind or phase')
        if c['case_kind']=='sink_only' and e['kind'] in {'activity_started','cancellation_observed','promise_settled','worker_settled','workflow_hold','finally_point','heartbeat','observation_release','observation_release_received'}:
            raise ArtifactError('fabricated native event in sink-only control')
        exact(e['payload'], PAYLOADS[e['kind']])
        if not isinstance(e['parents'], list) or any(not isinstance(x,str) for x in e['parents']) or len(set(e['parents']))!=len(e['parents']):
            raise ArtifactError('invalid causal references')
        p=e['payload']
        if e['kind'] in ('cancel_response','promise_settled','worker_settled'): synthetic_result(p['details'])
        if e['kind']=='bridge_response':
            result=p['result']
            if not isinstance(result,dict) or result.get('outcome') not in ('effect','denied','duplicate'): raise ArtifactError('unsupported bridge result')
            if result['outcome']=='denied':
                exact(result,('outcome','reason'))
                if not isinstance(result['reason'],str): raise ArtifactError('invalid denial reason')
            else: exact(result,('outcome',))
        for key in ('request_id','call_id','release_id','cut_id'):
            if key in p and (not isinstance(p[key],str) or not p[key]): raise ArtifactError('invalid event identity')
        if e['kind'] == 'cancel_response' and (p['outcome'] not in ('response_received','error') or not isinstance(p['details'],dict)):
            raise ArtifactError('invalid client outcome')
        if e['kind'] in ('promise_settled','worker_settled') and (p['disposition'] not in ('result','failure') or not isinstance(p['details'],dict)):
            raise ArtifactError('invalid settlement')
        if e['kind']=='transport_error' and type(p['uncertain']) is not bool: raise ArtifactError('invalid uncertain flag')
        if e['kind']=='fence_receipt' and (not integer(p['sink_seq'],1) or not integer(p['withdrawn_epoch']) or not integer(p['new_epoch'])):
            raise ArtifactError('invalid fence receipt')
    return events


def validate_native(n, c, b, phase):
    exact(n, ('schema_version','adapter','case_id','operation_id','phase','binding','events','coverage'))
    if n['schema_version']!=VERSION or n['adapter']!='synthetic-normalized-v1': raise ArtifactError('unsupported native schema')
    if n['case_id']!=c['case_id'] or n['operation_id']!=c['operation_id'] or n['phase']!=phase or n['binding']!=b['native']:
        raise ArtifactError('native history binding mismatch')
    exact(n['coverage'], ('complete_prefix','pages','final_event_id','closing_boundary_event_id','namespace','run_id','schema_pin'))
    cov=n['coverage']
    if cov['run_id']!=b['native']['run_id'] or cov['schema_pin']!='synthetic-normalized-v1' or not isinstance(cov['namespace'],str):
        raise ArtifactError('native coverage binding mismatch')
    types={
      'workflow_started': (), 'activity_scheduled': ('activity_id',),
      'activity_started': ('scheduled_event_id','attempt'),
      'activity_completed': ('scheduled_event_id','started_event_id','result'),
      'activity_failed': ('scheduled_event_id','started_event_id','failure'),
      'activity_canceled': ('scheduled_event_id','started_event_id','details'),
      'activity_timed_out': ('scheduled_event_id','started_event_id','details'),
      'workflow_completed': ('result',), 'workflow_failed': ('failure',),
      'workflow_canceled': ('details',), 'workflow_timed_out': ('details',),
    }
    previous=0
    for e in n['events']:
        exact(e, ('event_id','type','phase','attributes'))
        ident=native_id(e['event_id'])
        if ident <= previous: raise ArtifactError('duplicate or unordered native event IDs')
        previous=ident
        if e['type'] not in types or e['phase'] not in PHASES or PHASES[e['phase']]>PHASES[phase]:
            raise ArtifactError('unknown or future native event')
        exact(e['attributes'], types[e['type']])
        for key in ('result','failure','details'):
            if key in e['attributes']: synthetic_result(e['attributes'][key])
        for key in ('scheduled_event_id','started_event_id'):
            if key in e['attributes']: native_id(e['attributes'][key])
        if e['type']=='activity_started' and not integer(e['attributes']['attempt'],1): raise ArtifactError('invalid native attempt')
    return n
