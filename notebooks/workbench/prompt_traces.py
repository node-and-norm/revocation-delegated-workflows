"""Exact JSON-source spans from pinned scripted v0.3 worker snapshots.

No model calls or archived code execution. JSON fragments are source substrings,
not json.dumps reconstructions, and carry UTF-8 byte offsets into the member.
"""
from dataclasses import dataclass
from hashlib import sha256
from html import escape
import json
from zipfile import ZipFile
from .presentation import View, table
from .core import EvidenceError

ARCHIVE='archives/revocation_integration_pilot_v03_20261103.zip'
ARCHIVE_SHA256='b088613324c731e900e71317be725a8f2a8002d22a29bc40dcc4670ffb68f3c9'
PREFIX='integration/v0.3/evidence/measured01/'
CASES=tuple(f'framework_prior{p}_revoked{r}' for p in (0,1) for r in (0,1))
PHASES=('pause','resume')


def source_spans(text):
    """Map JSON pointers to exact character spans; reject duplicate object keys."""
    decoder=json.JSONDecoder();spans={}
    def ws(i):
        while i<len(text) and text[i] in ' \t\r\n':i+=1
        return i
    def walk(i,path):
        i=ws(i);start=i
        if text[i]=='{':
            i=ws(i+1);seen=set()
            if text[i]!='}':
                while True:
                    key,end=decoder.raw_decode(text,i)
                    if not isinstance(key,str) or key in seen:raise EvidenceError('Duplicate or invalid JSON key')
                    seen.add(key);i=ws(end)
                    if text[i]!=':':raise EvidenceError('Expected colon')
                    ptr=path+'/'+key.replace('~','~0').replace('/','~1')
                    i=ws(walk(i+1,ptr))
                    if text[i]=='}':break
                    if text[i]!=',':raise EvidenceError('Expected comma')
                    i=ws(i+1)
            i+=1
        elif text[i]=='[':
            i=ws(i+1);index=0
            if text[i]!=']':
                while True:
                    i=ws(walk(i,path+'/'+str(index)));index+=1
                    if text[i]==']':break
                    if text[i]!=',':raise EvidenceError('Expected comma')
                    i=ws(i+1)
            i+=1
        else:
            _,i=decoder.raw_decode(text,i)
        spans[path]=(start,i);return i
    try:
        end=walk(0,'')
        if ws(end)!=len(text):raise EvidenceError('Trailing JSON content')
    except (IndexError,json.JSONDecodeError) as exc:raise EvidenceError('Malformed source JSON') from exc
    return spans

@dataclass
class Snapshot:
    member:str
    raw:bytes
    text:str
    values:dict
    spans:dict

    def fragment(self,pointer):
        if pointer not in self.spans:raise EvidenceError('Field absent from preserved snapshot: '+pointer)
        a,b=self.spans[pointer];lo=len(self.text[:a].encode('utf-8'));hi=len(self.text[:b].encode('utf-8'))
        value=self.raw[lo:hi].decode('utf-8')
        if value!=self.text[a:b]:raise EvidenceError('Source span mismatch')
        return value,lo,hi

    def view(self,pointer,title):
        raw,lo,hi=self.fragment(pointer)
        loc=f'{ARCHIVE} :: {self.member} :: {pointer or "/ (document)"}'
        receipt=f'Member SHA-256 {sha256(self.raw).hexdigest()} | UTF-8 bytes [{lo}, {hi}) | fragment SHA-256 {sha256(raw.encode()).hexdigest()}'
        return View(title+'\n'+loc+'\n'+receipt+'\n'+raw,
                    '<h3>'+escape(title)+'</h3><p>'+escape(loc)+'</p><p><small>'+escape(receipt)+'</small></p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">'+escape(raw)+'</pre>')

@dataclass
class TraceArchive:
    snapshots:dict
    members:tuple

    def snapshot(self,case,phase):
        if (case,phase) not in self.snapshots:raise EvidenceError('Choose an available case/phase; no transcript is reconstructed')
        return self.snapshots[case,phase]

    def calls(self):
        rows=[]
        for (case,phase),s in self.snapshots.items():
            for g,group in enumerate(s.values.get('models',[])):
                for i,call in enumerate(group):
                    ptr=f'/models/{g}/{i}'
                    rows.append({'case':case,'phase':phase,'group':g,'invocation':i,'role':call.get('role','[missing]'),
                                 'input':ptr+'/input' in s.spans,'output':ptr+'/output' in s.spans,
                                 'pointer':ptr,'member':s.member})
        return rows


def read_traces(root):
    path=root/ARCHIVE
    if sha256(path.read_bytes()).hexdigest()!=ARCHIVE_SHA256:raise EvidenceError('Pilot archive digest changed; reconcile before reading')
    snapshots={}
    with ZipFile(path) as z:
        names=tuple(z.namelist())
        for case in CASES:
            for phase in PHASES:
                member=PREFIX+case+f'/worker_{phase}.json'
                if member not in names:continue
                raw=z.read(member);text=raw.decode('utf-8');spans=source_spans(text);values=json.loads(text)
                if values.get('phase')!=phase:raise EvidenceError('Phase binding mismatch')
                snapshots[case,phase]=Snapshot(member,raw,text,values,spans)
    return TraceArchive(snapshots,names)


def trace_index(archive):
    return table(['Case','Phase','Role','Source pointer','Input recorded','Output recorded'],
                 [[r['case'],r['phase'],r['role'],r['pointer'],r['input'],r['output']] for r in archive.calls()],
                 'Preserved scripted-model invocation index',
                 'Array group/order is preserved. It is not a global timestamp ordering across agents. These are serialized synthetic test messages, not live-provider generations or a complete research conversation archive.')

# Preserved stage archives, not an assertion that every command/conversation exists.
STAGES={
    'v0.1':('archives/qualification_revocation_v01.zip','ce289cb5b8a4402fd08c6db25b00fc41866f9f8e0637730c1757e706f1c09d66'),
    'v0.2':('archives/qualification_revocation_v02.zip','7355be609c634bdf48de8b3582ea4018f2e48ed0a47d421afbb073d24190d386'),
    'v0.3':(ARCHIVE,ARCHIVE_SHA256),
    'request-to-fence':('archives/withdrawal_interface_study_v01_20261103.zip','adf5e66cb0ad90038cde189330ee46877fabda26f1d829d3ae9b734c44af827c'),
}

def stage_members(root,stage):
    if stage not in STAGES:raise EvidenceError('Unknown preserved stage')
    archive,digest=STAGES[stage];path=root/archive
    if sha256(path.read_bytes()).hexdigest()!=digest:raise EvidenceError('Historical stage archive changed')
    with ZipFile(path) as z:
        return {n:z.read(n) for n in z.namelist() if not n.endswith('/')}


def stage_index(root):
    rows=[]
    for stage,(archive,digest) in STAGES.items():
        members=stage_members(root,stage)
        source=sum(n.endswith(('.py','.ts','.js','.cjs','.sh')) for n in members)
        logs=sum(n.endswith(('.log','.stdout','.stderr')) for n in members)
        rows.append([stage,archive,digest,len(members),source,logs])
    return table(['Stage','Archive','SHA-256','File members','Code files','Log/stdout/stderr files'],rows,
        'Verified preserved stage inventory',
        'Counts include copied snapshots and tests; they are not unique programs, executions, samples or completeness scores. Archive bytes identify versions, not authentic capture dates.')


def source_file_view(root,stage,member,start=1,count=45):
    members=stage_members(root,stage)
    if member not in members:raise EvidenceError('Member not preserved in selected archive')
    raw=members[member];text=raw.decode('utf-8');lines=text.splitlines(keepends=True)
    if type(start)!=int or type(count)!=int or start<1 or count<1 or start>len(lines):raise EvidenceError('Invalid source line range')
    end=min(len(lines),start+count-1);lo=len(''.join(lines[:start-1]).encode());hi=len(''.join(lines[:end]).encode())
    excerpt=raw[lo:hi].decode();loc=f'{STAGES[stage][0]} :: {member} :: lines {start}–{end}; UTF-8 bytes [{lo}, {hi})'
    note=f'Member SHA-256 {sha256(raw).hexdigest()}. Exact source text, not executed by this reader.'
    return View(loc+'\n'+note+'\n'+excerpt,'<p>'+escape(loc)+'</p><p><small>'+escape(note)+'</small></p><pre style="white-space:pre-wrap;overflow-wrap:anywhere">'+escape(excerpt)+'</pre>')
