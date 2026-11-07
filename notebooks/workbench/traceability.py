"""Read-only, pinned OOXML table view for the preserved v0.11 workbook.

This deliberately supports the declared workbook, not arbitrary Excel files.
No formulas are evaluated; no workbook, link or macro is executed.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256
from pathlib import PurePosixPath
import posixpath
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile
from .presentation import table

WORKBOOK = 'docs/traceability/Revocation_AI_Use_and_Research_Decision_Traceability_v0.11.xlsx'
DIGEST = 'cd0929a30d3fb5804eead5b69151926bb70afaff24e93f5258965aca057e61d0'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
RNS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PNS = 'http://schemas.openxmlformats.org/package/2006/relationships'

class TraceabilityError(ValueError): pass

def colnum(s):
    n=0
    for c in s: n=n*26+ord(c)-64
    return n

def colname(n):
    s=''
    while n:
        n,r=divmod(n-1,26);s=chr(65+r)+s
    return s

def address(s):
    m=re.fullmatch(r'([A-Z]+)([1-9][0-9]*)',s)
    if not m: raise TraceabilityError('Unsupported cell address')
    return colnum(m[1]),int(m[2])

def relationships(z,owner):
    p=PurePosixPath(owner)
    name=str(p.parent/'_rels'/(p.name+'.rels'))
    result={}
    for r in ET.fromstring(z.read(name)):
        if r.get('TargetMode')=='External':
            continue  # Never follow external relationships.
        raw=r.get('Target')
        target=posixpath.normpath(raw.lstrip('/') if raw.startswith('/') else posixpath.join(str(p.parent),raw))
        if target.startswith('/') or target.startswith('../'): raise TraceabilityError('Unsafe relationship')
        result[r.get('Id')]=target
    return result

@dataclass(frozen=True)
class RecordTable:
    name: str
    sheet: str
    ref: str
    headers: tuple
    rows: tuple
    first_row: int
    first_col: int

    def records(self, query=''):
        q=query.casefold()
        return [(self.first_row+i,dict(zip(self.headers,row))) for i,row in enumerate(self.rows)
                if not q or any(q in str(v).casefold() for v in row)]

    def row(self,key):
        matches=[(i,r) for i,r in self.records() if str(r[self.headers[0]])==key]
        if len(matches)!=1: raise TraceabilityError(f'Expected one exact key: {key}')
        return matches[0]

@dataclass
class WorkbookView:
    digest: str
    tables: dict
    sheets: tuple
    cells: dict


def read_workbook(root):
    path=root/WORKBOOK
    if sha256(path.read_bytes()).hexdigest()!=DIGEST:
        raise TraceabilityError('Workbook digest differs from pinned v0.11; reconcile explicitly before reading.')
    tables={};sheet_names=[];all_cells={}
    with ZipFile(path) as z:
        strings=[''.join(t.itertext()) for t in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        styles=ET.fromstring(z.read('xl/styles.xml'))
        fmts={int(f.get('numFmtId')):f.get('formatCode','') for f in styles.findall('s:numFmts/s:numFmt',NS)}
        date_styles=set()
        for i,xf in enumerate(styles.find('s:cellXfs',NS)):
            n=int(xf.get('numFmtId','0'));fmt=fmts.get(n,'').lower()
            if n in range(14,23) or ('yy' in fmt and ('mm' in fmt or 'dd' in fmt)):
                date_styles.add(i)
        book=ET.fromstring(z.read('xl/workbook.xml'))
        props=book.find('s:workbookPr',NS)
        if props is not None and props.get('date1904') in ('1','true'): raise TraceabilityError('Unexpected date epoch')
        rels=relationships(z,'xl/workbook.xml')
        for sh in book.findall('s:sheets/s:sheet',NS):
            name=sh.get('name');sheet_names.append(name);member=rels[sh.get('{'+RNS+'}id')]
            xml=ET.fromstring(z.read(member));cells={}
            for c in xml.findall('s:sheetData/s:row/s:c',NS):
                if c.find('s:f',NS) is not None: raise TraceabilityError('Formula not supported in pinned record')
                v=c.find('s:v',NS);raw=None if v is None else v.text
                kind=c.get('t');val=raw
                if kind=='s' and raw is not None: val=strings[int(raw)]
                elif kind=='inlineStr': val=''.join(c.find('s:is',NS).itertext())
                elif kind not in ('str','e','d') and raw is not None:
                    if int(c.get('s','0')) in date_styles:
                        # Match Excel's 1900 date system after its fictitious leap day.
                        days=float(raw)
                        if days<61: raise TraceabilityError('Unsupported early Excel date')
                        val=(datetime(1899,12,30)+timedelta(milliseconds=round(days*86400000))).isoformat(sep=' ')
                    elif kind=='b': val=bool(int(raw))
                    else:
                        val=float(raw);val=int(val) if val.is_integer() else val
                cells[c.get('r')]={'value':val,'raw':raw,'type':kind,'style':c.get('s')}
            all_cells[name]=cells
            sr=relationships(z,member)
            for part in xml.findall('s:tableParts/s:tablePart',NS):
                definition=ET.fromstring(z.read(sr[part.get('{'+RNS+'}id')]))
                ref=definition.get('ref');start,end=ref.split(':');c1,r1=address(start);c2,r2=address(end)
                headers=tuple(cells.get(f'{colname(c)}{r1}',{}).get('value') for c in range(c1,c2+1))
                if any(not isinstance(h,str) for h in headers) or len(set(headers))!=len(headers): raise TraceabilityError('Invalid headers')
                rows=tuple(tuple(cells.get(f'{colname(c)}{r}',{}).get('value') for c in range(c1,c2+1)) for r in range(r1+1,r2+1))
                key=definition.get('name');tables[key]=RecordTable(key,name,ref,headers,rows,r1+1,c1)
    return WorkbookView(DIGEST,tables,tuple(sheet_names),all_cells)


def inventory(view):
    return table(['Sheet','Named source table','Source range','Data rows'],
        [[t.sheet,t.name,t.ref,len(t.rows)] for t in view.tables.values()],
        'Six source sheets · seven source tables',
        'Counts are workbook records, not study cases, verified approvals or independent evidence. Blank/template cells outside source tables are not counted.')

def record_view(t,key):
    row,values=t.row(key)
    return table(['Source cell','Field','Exact stored value (dates decoded)'],
        [[f"'{t.sheet}'!{colname(t.first_col+i)}{row}",h,'[blank source cell]' if v is None else v] for i,(h,v) in enumerate(values.items())],
        str(key),f'{WORKBOOK} :: {t.sheet}!{t.ref}. Values are historical statements; their presence does not verify the claim.')

def select_view(t,columns,query=''):
    if not set(columns)<=set(t.headers): raise TraceabilityError('Unknown column')
    rows=t.records(query)
    return table(['Source row',*columns],[[f"'{t.sheet}'!{i}",*('[blank source cell]' if r[c] is None else r[c] for c in columns)] for i,r in rows],
        t.name+(' · literal search: '+query if query else ' · all records'),
        f'{len(rows)} of {len(t.rows)} table records selected. Search is literal across every field; no result is not proof of absence outside this snapshot. No text is truncated.')
