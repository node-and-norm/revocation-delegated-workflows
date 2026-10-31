"""Independent offline oracle: no imports from harness or enforcement code."""

def assess(trace):
    errors = []
    def invalid_schema():
        return {'label': 'INVALID', 'errors': ['invalid_trace_schema'], 'post_fence_effect_sequences': [], 'attempts': 0, 'effects': 0}
    if not isinstance(trace, dict):
        return invalid_schema()
    events = trace.get('events', [])
    effects = trace.get('effects', [])
    case = trace.get('case')
    count = 3 if case == 'C3' else 1
    if not isinstance(events, list) or not isinstance(effects, list):
        return invalid_schema()
    fields = {'admission': {'root', 'epoch', 'allowed'}, 'prepared': {'effect_key', 'payload'}, 'revocation': {'root', 'withdrawn_epoch', 'new_epoch'}, 'attempt': {'attempt'}, 'effect': {'attempt'}, 'denied': {'attempt'}, 'duplicate': {'attempt'}, 'ack': {'attempt', 'outcome'}}
    for e in events:
        if not isinstance(e, dict) or set(e) != {'seq', 'kind', 'data'} or type(e['seq']) is not int or not isinstance(e['kind'], str) or e['kind'] not in fields or not isinstance(e['data'], dict) or set(e['data']) != fields[e['kind']]:
            return invalid_schema()
        d = e['data']
        for k in ('epoch', 'withdrawn_epoch', 'new_epoch', 'attempt'):
            if k in d and type(d[k]) is not int: return invalid_schema()
        if 'allowed' in d and type(d['allowed']) is not bool: return invalid_schema()
        if 'attempt' in d and d['attempt'] not in range(1, count + 1):
            errors.append('unknown_attempt_id')
    for row in effects:
        if not isinstance(row, dict) or set(row) != {'event_seq', 'effect_key', 'payload', 'root', 'epoch'} or type(row['event_seq']) is not int or type(row['epoch']) is not int:
            return invalid_schema()
    authority = trace.get('authority')
    if not isinstance(authority, dict) or set(authority) != {'root', 'epoch', 'active'} or type(authority['epoch']) is not int or type(authority['active']) is not int:
        return invalid_schema()
    if case not in ('C0', 'C1', 'C2', 'C3', 'C4'):
        errors.append('unknown_case')
    if [e['seq'] for e in events] != list(range(1, len(events) + 1)):
        errors.append('noncontiguous_event_order')
    by = lambda kind: [e for e in events if e['kind'] == kind]
    if len(by('admission')) != 1 or len(by('prepared')) != 1:
        errors.append('missing_or_duplicate_preparation')
    fences = by('revocation')
    if len(fences) != (0 if case == 'C0' else 1):
        errors.append('missing_or_duplicate_fence')
    if len([e for e in events if e['kind'] in ('effect', 'denied', 'duplicate')]) != count:
        errors.append('outcome_count_mismatch')
    if len(by('attempt')) != count or len(by('ack')) != count:
        errors.append('missing_or_duplicate_attempt_or_ack')
    known = {'admission', 'prepared', 'revocation', 'attempt', 'effect', 'denied', 'duplicate', 'ack'}
    if any(e['kind'] not in known for e in events):
        errors.append('unknown_event')
    if len(by('admission')) == len(by('prepared')) == 1:
        a, p = by('admission')[0], by('prepared')[0]
        if a['seq'] >= p['seq'] or a['data'] != {'root': 'rootR', 'epoch': 7, 'allowed': True}:
            errors.append('invalid_admission_preparation')
        if p['data'] != {'effect_key': 'summary:task1', 'payload': 'inert summary'}:
            errors.append('prepared_binding_mismatch')
        if any(e['seq'] <= p['seq'] for e in by('attempt')):
            errors.append('attempt_before_prepared')
    for i in range(1, count + 1):
        attempts = [e for e in by('attempt') if e['data'].get('attempt') == i]
        outcomes = [e for e in events if e['kind'] in ('effect', 'denied', 'duplicate') and e['data'].get('attempt') == i]
        acks = [e for e in by('ack') if e['data'].get('attempt') == i]
        if not (len(attempts) == len(outcomes) == len(acks) == 1):
            errors.append('missing_or_duplicate_attempt_outcome')
        elif not attempts[0]['seq'] < outcomes[0]['seq'] < acks[0]['seq'] or acks[0]['data'].get('outcome') != outcomes[0]['kind']:
            errors.append('invalid_attempt_outcome_ack_order')
    for e in by('duplicate'):
        if not any(prior['kind'] == 'effect' and prior['seq'] < e['seq'] for prior in events):
            errors.append('duplicate_without_prior_effect')
    for i in range(2, count + 1):
        previous = [e for e in by('ack') if e['data']['attempt'] == i - 1]
        current = [e for e in by('attempt') if e['data']['attempt'] == i]
        if previous and current and previous[0]['seq'] >= current[0]['seq']:
            errors.append('retry_continuation_order_mismatch')
    committed = by('effect')
    expected_effects = [{'event_seq': e['seq'], 'effect_key': 'summary:task1', 'payload': 'inert summary', 'root': 'rootR', 'epoch': 7} for e in committed]
    if effects != expected_effects or len(effects) > 1:
        errors.append('effect_event_mismatch_or_duplicate')
    expected_authority = {'root': 'rootR', 'epoch': 7 if case == 'C0' else 8, 'active': 1 if case == 'C0' else 0}
    if trace.get('authority') != expected_authority:
        errors.append('authority_state_mismatch')
    if fences:
        f = fences[0]
        if f['data'] != {'root': 'rootR', 'withdrawn_epoch': 7, 'new_epoch': 8}:
            errors.append('invalid_fence')
        if by('prepared') and f['seq'] <= by('prepared')[0]['seq']:
            errors.append('fence_before_preparation')
        if case in ('C1', 'C2', 'C3') and any(e['seq'] <= f['seq'] for e in by('attempt')):
            errors.append('schedule_fence_order_mismatch')
        if case == 'C4' and (not committed or any(e['seq'] >= f['seq'] for e in committed) or any(e['seq'] <= f['seq'] for e in by('ack'))):
            errors.append('late_ack_schedule_mismatch')
    violations = [e['seq'] for e in committed if fences and e['seq'] > fences[0]['seq']]
    return {'label': 'INVALID' if errors else ('VIOLATION' if violations else 'NO_VIOLATION'), 'errors': sorted(set(errors)), 'post_fence_effect_sequences': violations, 'attempts': len(by('attempt')), 'effects': len(effects)}
