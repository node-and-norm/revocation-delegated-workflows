"""Strict, bounded local artifact loading. Hashes bind bytes, not authenticity."""
from __future__ import annotations
import hashlib
import json
import math
import re
from pathlib import Path

VERSION = 'synthetic-artifact-0.1'
PHASES = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
MAX_BYTES = 16 * 1024 * 1024

class ArtifactError(ValueError):
    pass

def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ArtifactError('duplicate JSON key: ' + key)
        result[key] = value
    return result

def _float(text):
    number=float(text)
    if not math.isfinite(number):
        raise ArtifactError("nonfinite JSON number")
    return number

def loads(data):
    try:
        return json.loads(data, object_pairs_hook=_pairs, parse_float=_float,
                          parse_constant=lambda x: (_ for _ in ()).throw(ArtifactError('nonfinite number: '+x)))
    except (ValueError, UnicodeError, RecursionError) as e:
        raise ArtifactError(str(e)) from e

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def exact(obj, required, optional=()):
    if not isinstance(obj, dict):
        raise ArtifactError('expected object')
    missing, extra = set(required)-obj.keys(), obj.keys()-set(required)-set(optional)
    if missing or extra:
        raise ArtifactError(f'closed schema: missing={sorted(missing)}, extra={sorted(extra)}')

def integer(value, minimum=0):
    return type(value) is int and value >= minimum

def native_id(value):
    # Never coerce floats, bool, signs, exponent strings, or leading zeroes.
    if type(value) is int and 0 < value <= 2**63-1:
        return value
    if isinstance(value, str) and len(value)<=19 and re.fullmatch('[1-9][0-9]*', value) and int(value) <= 2**63-1:
        return int(value)
    raise ArtifactError('native identifier must be a lossless positive int64')

def safe_path(root, relative):
    if not isinstance(relative, str) or not re.fullmatch(r'[A-Za-z0-9_./-]+', relative):
        raise ArtifactError('unsafe or alternate-encoded path')
    p = Path(relative)
    if p.is_absolute() or any(x in ('', '.', '..') for x in relative.split('/')):
        raise ArtifactError('path traversal or noncanonical path')
    target = root / p
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            raise ArtifactError('symlink input is forbidden')
    if not target.resolve().is_relative_to(root.resolve()):
        raise ArtifactError('path escape')
    return target

def requirement(status, reason, refs=()):
    return {'status': status, 'reason': reason, 'evidence_refs': list(refs)}

def ref(artifact_id, locator, record_id, phase, cut_id, boundary_id):
    return dict(artifact_id=artifact_id, locator=locator, record_id=str(record_id),
                phase=phase, cut_id=cut_id, boundary_id=boundary_id)

class Bundle:
    """Load each independently valid input; one bad input does not erase others."""
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.entries, self.values, self.errors = {}, {}, []
        self.registry = None
        try:
            registry_path = safe_path(self.root, 'registry.json')
            if registry_path.stat().st_size > MAX_BYTES:
                raise ArtifactError('oversize registry')
            self.registry = loads(registry_path.read_bytes())
            exact(self.registry, ('schema_version', 'artifacts'))
            if self.registry['schema_version'] != VERSION:
                raise ArtifactError('unsupported registry schema')
            entries = self.registry['artifacts']
            if not isinstance(entries, list) or len(entries) > 256:
                raise ArtifactError('invalid artifact count')
        except (ArtifactError, OSError) as e:
            self.errors.append('registry: '+str(e)); return
        ids, paths = set(), set()
        for entry in entries:
            try:
                exact(entry, ('artifact_id', 'path', 'role', 'phase', 'schema_version', 'byte_length', 'sha256', 'producer'))
                aid, path = entry['artifact_id'], entry['path']
                if not isinstance(aid, str) or not re.fullmatch('[a-z0-9_.-]+', aid):
                    raise ArtifactError('nonneutral artifact identity')
                if aid in ids or path in paths or path == 'registry.json':
                    raise ArtifactError('duplicate identity/path or self-hashing registry')
                ids.add(aid); paths.add(path)
                if entry['phase'] not in PHASES or entry['schema_version'] != VERSION:
                    raise ArtifactError('unsupported phase/schema')
                if not integer(entry['byte_length']) or entry['byte_length'] > MAX_BYTES:
                    raise ArtifactError('invalid byte length')
                if not isinstance(entry['sha256'], str) or not re.fullmatch('[a-f0-9]{64}', entry['sha256']):
                    raise ArtifactError('invalid digest')
                target = safe_path(self.root, path)
                if target.stat().st_size > MAX_BYTES:
                    raise ArtifactError('oversize artifact')
                data = target.read_bytes()
                if len(data) > MAX_BYTES or len(data) != entry['byte_length'] or digest(data) != entry['sha256']:
                    raise ArtifactError('byte length or SHA256 mismatch')
                if path.endswith('.jsonl'):
                    if data and not data.endswith(b'\n'):
                        raise ArtifactError('truncated JSONL: missing line terminator')
                    value = [loads(x) for x in data.splitlines()]
                elif path.endswith('.json'):
                    value = loads(data)
                elif path.endswith('.sqlite'):
                    value = target
                else:
                    raise ArtifactError('unsupported artifact encoding')
                self.entries[aid], self.values[aid] = entry, value
            except (ArtifactError, OSError, TypeError, KeyError) as e:
                self.errors.append(str(entry.get('path', '?') if isinstance(entry, dict) else '<non-object>')+': '+str(e))
        if len(ids) != len(entries) or len(paths) != len(entries):
            self.errors.append('duplicate registry identity')
        # All files within a bundle are evidence or explicitly registered outputs.
        for p in self.root.rglob('*'):
            if p.is_symlink():
                self.errors.append('symlink in bundle: '+str(p.relative_to(self.root)))
            elif p.is_file() and str(p.relative_to(self.root)) not in paths | {'registry.json'}:
                self.errors.append('undeclared file: '+str(p.relative_to(self.root)))

    def get(self, role, phase=None):
        found = [aid for aid, e in self.entries.items() if e['role'] == role and (phase is None or e['phase'] == phase)]
        if len(found) != 1:
            raise ArtifactError(f'{role}/{phase}: expected exactly one artifact, found {len(found)}')
        return found[0], self.values[found[0]]

    def optional(self, role, phase=None):
        try:
            return self.get(role, phase)
        except ArtifactError:
            return None, None
