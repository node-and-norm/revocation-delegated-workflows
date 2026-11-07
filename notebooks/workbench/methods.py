"""Read-only source/freeze inspection; never executes archived study code."""
from dataclasses import dataclass
from hashlib import sha256
import json
import re
from zipfile import ZipFile
from .core import ARCHIVE, EvidenceError
from .presentation import table, View
from html import escape

ARCHIVE_SHA256='adf5e66cb0ad90038cde189330ee46877fabda26f1d829d3ae9b734c44af827c'
FREEZE='frozen_candidate_v02/FREEZE.json'
MANIFEST='measured01/RUN_MANIFEST.json'

@dataclass
class MethodsRecord:
    members: dict
    freeze: dict
    manifest: dict
    receipts: list

    def text(self,name):
        if name not in self.members: raise EvidenceError('Unknown archive member: '+name)
        return self.members[name].decode('utf-8')

    def inventory(self,path='framework',schedule='S4'):
        if path not in ('direct','framework') or schedule not in tuple(f'S{i}' for i in range(6)):
            raise EvidenceError('Choose a declared path and schedule')
        prefix=f'measured01/{path}/{schedule}/'
        return [(n,len(b),sha256(b).hexdigest()) for n,b in self.members.items() if n.startswith(prefix)]


def read_methods(root):
    path=root/ARCHIVE
    if sha256(path.read_bytes()).hexdigest()!=ARCHIVE_SHA256:
        raise EvidenceError('Archive digest differs from preserved study; stop and reconcile')
    with ZipFile(path) as z:
        members={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
    freeze=json.loads(members[FREEZE]);manifest=json.loads(members[MANIFEST]);receipts=[]
    for name,expected in freeze['files'].items():
        member='frozen_candidate_v02/'+name
        actual=sha256(members[member]).hexdigest()
        if actual!=expected:raise EvidenceError('Frozen-file mismatch: '+member)
        receipts.append((member,actual))
    for field,member in [('freeze_file_sha256',FREEZE),('runner_sha256','frozen_candidate_v02/qualify_direct.py'),('checker_sha256','frozen_candidate_v02/independent_checker.py')]:
        if manifest[field]!=sha256(members[member]).hexdigest():raise EvidenceError('Manifest binding mismatch: '+field)
    return MethodsRecord(members,freeze,manifest,receipts)


def freeze_view(record):
    return table(['Frozen member','Verified SHA-256'],record.receipts,'Recorded v02 source freeze · bytes checked now',
        'Source: '+FREEZE+'. Matching bytes do not establish authentic timing, runtime execution or scientific correctness.')


def archive_excerpt(record,name,start=1,count=16):
    lines=record.text(name).splitlines()
    if type(start)!=int or type(count)!=int or start<1 or count<1 or start>len(lines):raise EvidenceError('Invalid excerpt range')
    end=min(len(lines),start+count-1);text='\n'.join(lines[start-1:end]);loc=f'{ARCHIVE} :: {name} · lines {start}–{end}'
    return View(loc+'\n'+text,'<p><strong>'+escape(loc)+'</strong></p><pre>'+escape(text)+'</pre>')
