"""Worker protocol only: deliberately no SQLite, filesystem, or gate implementation."""
def run_worker(actor, control, gateway, delivery):
    ledger = []
    grant = None
    try:
        while True:
            cmd = control.recv()
            if cmd['op'] == 'stop':
                control.send({'ok': True, 'ledger': ledger}); return
            if cmd['op'] == 'deliver':
                delivery.send(grant)
                ledger.append({'kind': 'delivery_sent', 'grant': grant, 'peer': 'childC'})
                control.send({'ok': True}); continue
            if cmd['op'] == 'receive':
                if not delivery.poll(10): raise TimeoutError('parent-child delivery timeout')
                grant = delivery.recv()
                ledger.append({'kind': 'delivery_received', 'grant': grant, 'peer': 'parentP'})
                control.send({'ok': True}); continue
            request = dict(cmd['request'])
            if request.get('grant') == '$child': request['grant'] = grant
            ledger.append({'kind': 'intent', 'request': request})
            gateway.send(request)
            if not gateway.poll(10): raise TimeoutError('gateway response timeout')
            response = gateway.recv()
            ledger.append({'kind': 'response', 'request_id': request['id'], 'response': response})
            if request['op'] == 'delegate' and response['outcome'] == 'grant': grant = response['grant']
            control.send({'ok': True, 'response': response})
    except BaseException as error:
        control.send({'ok': False, 'error': repr(error), 'ledger': ledger})
