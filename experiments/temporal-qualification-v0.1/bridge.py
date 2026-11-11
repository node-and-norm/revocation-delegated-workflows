"""Single-use trusted fixture bridge. Never accepts controller operations."""
import json, socket, time
MAX_FRAME=4096
FIXED={'op':'execute','claim':'childC','grant':'child-1','scope':'summary:task1','ticket':'ticket-1','payload':'inert summary'}

def validate(req):
    if not isinstance(req,dict) or set(req)!=set(FIXED)|{'id'}: raise ValueError('schema')
    if any(req[k]!=v for k,v in FIXED.items()): raise ValueError('binding')
    if not isinstance(req['id'],str) or not 1<=len(req['id'])<=128: raise ValueError('id')
    return req

def receive_frame(conn, timeout=15, clock=time.monotonic):
    """One bounded newline frame; EOF is an error, never a retry."""
    deadline = clock() + timeout
    buf = b''
    while b'\n' not in buf:
        remaining = deadline - clock()
        if remaining <= 0:
            raise TimeoutError('frame_deadline')
        conn.settimeout(remaining)
        part = conn.recv(min(1024, MAX_FRAME + 1 - len(buf)))
        if clock() >= deadline:
            raise TimeoutError('frame_deadline')
        if not part:
            raise ValueError('truncated_frame')
        buf += part
        if len(buf) > MAX_FRAME:
            raise ValueError('oversize_frame')
    line, extra = buf.split(b'\n', 1)
    if extra:
        raise ValueError('extra_frame')
    return json.loads(line)

def serve(path, child, log_path, teardown):
    journal_errors=[]
    def record(kind, suppress=False, **data):
        try:
            with open(log_path,'a') as f:
                f.write(json.dumps({'kind':kind,'monotonic_ns':time.monotonic_ns(),**data},sort_keys=True)+'\n'); f.flush()
        except BaseException as error:
            journal_errors.append(error)
            if not suppress: raise
    server=None
    conn=None
    primary=None
    cleanup_errors=[]
    dispatch_attempted=False;dispatched=False
    try:
        server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        server.bind(path);server.listen(1);server.settimeout(40)
        record('ready')
        conn,_=server.accept()
        conn.settimeout(15)
        req=validate(receive_frame(conn));record('dispatch',request=req)
        dispatch_attempted=True
        child.send(req);dispatched=True
        if not child.poll(20):raise TimeoutError('gateway_response')
        result=child.recv();record('gateway_response',request_id=req['id'],result=result)
        conn.sendall((json.dumps({'request_id':req['id'],'gateway_result':result})+'\n').encode())
        record('transport_response_sent')
    except BaseException as e:
        primary=e
        record('failure',suppress=True,error=repr(e),dispatch_attempted=dispatch_attempted,dispatched=dispatched,outcome='uncertain' if dispatch_attempted else 'not_dispatched')
        raise
    finally:
        # Cleanup is attempted independently and cannot replace a primary error.
        def cleanup(label, action):
            try:
                action()
            except BaseException as error:
                cleanup_errors.append(error)
                record('cleanup_failure',suppress=True,stage=label,error=repr(error))
        if conn is not None:
            cleanup('connection_close', conn.close)
        if server is not None:
            cleanup('server_close', server.close)
        record('transport_closed_waiting_for_teardown',suppress=True)
        def await_teardown():
            if not teardown.wait(100):
                raise TimeoutError('teardown')
        cleanup('teardown_wait', await_teardown)
        cleanup('child_close', child.close)
        record('closed',suppress=True,cleanup_ok=not cleanup_errors and not journal_errors)
        if primary is None and (cleanup_errors or journal_errors):
            raise (cleanup_errors or journal_errors)[0]
