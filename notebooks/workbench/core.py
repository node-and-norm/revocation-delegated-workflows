"""Deterministic evidence workflow. Standard library only; no runtime execution.

The reader verifies pinned bytes, keeps original records separate from derived
facts, and stops on missing, ambiguous or inconsistent input. This is not an
authentication mechanism, independent instrument reimplementation or sandbox.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
from typing import Any
from zipfile import BadZipFile, ZipFile

BASE_COMMIT = "6a2d6b19e18df28e2a8e69ee45830a5f9b94f26c"
RECORDS = "docs/research-records/v0.1"
SUMMARY = "docs/review/WITHDRAWAL_INTERFACE_SUMMARY_v0.1.json"
ARCHIVE = "archives/withdrawal_interface_study_v01_20261103.zip"
CHECKER = "checkers/temporal-artifact-v0.1"
QUESTION = ("What can the saved request-to-fence cases establish separately "
            "about request acceptance, fence installation, caller confirmation "
            "and protected effects within the recorded observation window?")
PATHS = ("direct", "framework")
SCHEDULES = tuple(f"S{i}" for i in range(6))


class EvidenceError(ValueError):
    """An input cannot safely support this bounded review."""


@dataclass(frozen=True)
class Scope:
    paths: tuple[str, ...] = PATHS
    schedules: tuple[str, ...] = SCHEDULES

    def __post_init__(self):
        for name, values, allowed in (("paths", self.paths, PATHS),
                                      ("schedules", self.schedules, SCHEDULES)):
            if not isinstance(values, tuple) or not values or len(set(values)) != len(values):
                raise EvidenceError(f"{name} must be a nonempty tuple without duplicates")
            if any(v not in allowed for v in values):
                raise EvidenceError(f"Unknown {name}: {values!r}; allowed: {allowed}")


def _safe_path(root: Path, name: str) -> Path:
    p = PurePosixPath(name)
    if p.is_absolute() or not p.parts or any(x in (".", "..") for x in p.parts):
        raise EvidenceError(f"Unsafe repository path: {name}")
    target = (root / name).resolve()
    if not target.is_relative_to(root.resolve()):
        raise EvidenceError(f"Path leaves repository: {name}")
    return target


def _json(data: bytes, label: str) -> Any:
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise EvidenceError(f"Duplicate JSON key in {label}: {k}")
            out[k] = v
        return out
    try:
        return json.loads(data, object_pairs_hook=pairs)
    except (ValueError, UnicodeError) as e:
        raise EvidenceError(f"Invalid JSON in {label}: {e}") from e


def _unique(items, key, label):
    values = [x[key] for x in items]
    if not values or len(values) != len(set(values)):
        raise EvidenceError(f"Empty or duplicate {label}")


@dataclass
class EvidenceStore:
    root: Path
    files: dict[str, bytes]
    sources: dict[str, dict]
    source_bytes: dict[str, bytes]
    registry: dict
    glossary: dict
    summary: dict
    raw: dict[tuple[str, str], dict]
    rows: list[dict]
    receipts: list[dict]
    overlays: dict

    @classmethod
    def load(cls, root: Path):
        root = Path(root).resolve()
        lock_path = root / "notebooks/workbench/input_manifest.json"
        try:
            lock = _json(lock_path.read_bytes(), "input manifest")
            _unique(lock["inputs"], "path", "pinned input paths")
            files, receipts = {}, []
            for item in lock["inputs"]:
                name = item["path"]
                data = _safe_path(root, name).read_bytes()
                digest = sha256(data).hexdigest()
                if digest != item["sha256"]:
                    raise EvidenceError(f"Input hash mismatch: {name}")
                files[name] = data
                receipts.append(dict(path=name, sha256=digest, bytes=len(data),
                                     check="matched pinned bytes"))
            manifest = _json(files[f"{RECORDS}/source_manifest.json"], "source manifest")
            registry = _json(files[f"{RECORDS}/evidence_registry.json"], "evidence registry")
            glossary = _json(files[f"{RECORDS}/glossary.json"], "glossary")
            _unique(manifest["sources"], "source_key", "source keys")
            _unique(registry["records"], "record_key", "claim keys")
            _unique(glossary["terms"], "term_key", "term keys")
            sources, source_bytes = {}, {}
            for source in manifest["sources"]:
                key = source["source_key"]
                data = files[source["repository_path"]]
                member = source.get("archive_member")
                if member:
                    data = read_member(data, member)
                if sha256(data).hexdigest() != source["sha256"]:
                    raise EvidenceError(f"Source snapshot hash mismatch: {key}")
                sources[key], source_bytes[key] = source, data
            for item in registry["records"] + glossary["terms"]:
                if not item["source_refs"]:
                    raise EvidenceError("Record has no source references")
                for ref in item["source_refs"]:
                    if ref["source_key"] not in sources or not ref["locator"].strip():
                        raise EvidenceError(f"Unresolvable source reference: {ref}")
            summary = _json(files[SUMMARY], "historical summary")
            raw = {}
            for path in PATHS:
                for schedule in SCHEDULES:
                    member = f"measured01/{path}/{schedule}/record.json"
                    raw[(path, schedule)] = _json(read_member(files[ARCHIVE], member), member)
            rows = reconcile(summary, raw)
            overlays = _json(files["notebooks/workbench/status_overlay.json"], "dated overlay")
            return cls(root, files, sources, source_bytes, registry, glossary,
                       summary, raw, rows, receipts, overlays)
        except EvidenceError:
            raise
        except (OSError, KeyError, TypeError, BadZipFile) as e:
            raise EvidenceError(f"Missing or malformed required evidence: {e}") from e

    def source_text(self, key: str) -> str:
        if key not in self.source_bytes:
            raise EvidenceError(f"Unknown source key: {key}")
        return self.source_bytes[key].decode("utf-8")

    def select(self, scope: Scope) -> list[dict]:
        return [deepcopy(r) for r in self.rows
                if r["path"] in scope.paths and r["schedule"] in scope.schedules]

    def source_claims(self, text: str = "") -> list[dict]:
        """Case-insensitive literal filter; empty query resets to all records."""
        if not isinstance(text, str):
            raise EvidenceError("Claim query must be a string")
        return [deepcopy(r) for r in self.registry["records"]
                if text.casefold() in json.dumps(r, ensure_ascii=False).casefold()]

    def case(self, path: str, schedule: str) -> dict:
        Scope(paths=(path,), schedules=(schedule,))
        return deepcopy(self.raw[(path, schedule)])


def read_member(archive: bytes, member: str) -> bytes:
    """Read an exact member in memory. Never extract files or run archive code."""
    with ZipFile(BytesIO(archive)) as z:
        if z.namelist().count(member) != 1:
            raise EvidenceError(f"Missing or ambiguous archive member: {member}")
        info = z.getinfo(member)
        if info.file_size > 8_000_000:
            raise EvidenceError(f"Oversized evidence member: {member}")
        return z.read(member)


def derive_case(record: dict) -> dict:
    """Recompute selected summary facts from saved JSON, not from a new run."""
    path, schedule = record["path"], record["schedule"]
    Scope(paths=(path,), schedules=(schedule,))
    if record["kind"] != "measured":
        raise EvidenceError("Expected a saved historical measured record")
    events, effects = record["sink"]["events"], record["sink"]["effects"]
    sequences = [e["seq"] for e in events]
    if any(type(x) is not int for x in sequences) or sequences != sorted(set(sequences)):
        raise EvidenceError("Sink event sequence is ambiguous")
    fences = [e["seq"] for e in events if e["kind"] == "revocation"]
    if len(fences) > 1:
        raise EvidenceError("More than one fence is outside this notebook's scope")
    fence = fences[0] if fences else None
    effect_sequences = [e["event_seq"] for e in effects]
    event_index = {e["seq"]: e for e in events}
    if any(s not in event_index or event_index[s]["kind"] != "effect" for s in effect_sequences):
        raise EvidenceError("Effect row lacks a matching committed effect event")
    if len(effect_sequences) != len(set(effect_sequences)):
        raise EvidenceError("Duplicate effect sequence")
    for effect in effects:
        result = event_index[effect["event_seq"]]["data"]["result"]
        if any(effect[k] != result[k] for k in ("effect_key", "payload", "root", "epoch")):
            raise EvidenceError("Effect row identity or payload differs from committed event")
    trace = record["caller_trace"]
    state = "IDLE"
    for transition in trace:
        if transition["before"] != state:
            raise EvidenceError("Discontinuous caller trace")
        state = transition["after"]
    if state != record["caller_state"]:
        raise EvidenceError("Caller trace and terminal state disagree")
    validate_barriers(record)
    result = record["execute_response"]
    return dict(path=path, schedule=schedule, caller_state=state,
                request_accepted=any(t["input"]["kind"] == "accepted_volatile" for t in trace),
                fence_seq=fence, effect_count=len(effects), effect_sequences=effect_sequences,
                outcome=result["outcome"], reason=result.get("reason"),
                post_fence_effect_count=sum(s > fence for s in effect_sequences) if fence is not None else None,
                source_member=f"measured01/{path}/{schedule}/record.json")


def validate_barriers(record: dict):
    """Validate the saved fields used by the diagram, not the entire instrument."""
    barriers = record["barriers"]
    if not barriers or barriers[-1]["name"] != "terminal_observation":
        raise EvidenceError("Missing terminal barrier")
    _unique(barriers, "name", "barrier names")
    events, effects = record["sink"]["events"], record["sink"]["effects"]
    names = {"accepted", "fence_installed", "completion_observed", "execute_terminal", "terminal_observation"}
    last_count, prior_state = 0, "IDLE"
    states = ["IDLE"] + [t["after"] for t in record["caller_trace"]]
    for b in barriers:
        if b["name"] not in names:
            raise EvidenceError("Unknown saved barrier")
        committed = b["committed_events"]
        if len(committed) < last_count or committed != events[:len(committed)]:
            raise EvidenceError("Barrier events do not preserve the final event prefix")
        last_count = len(committed)
        seqs = {e["seq"] for e in committed}
        if b["effects"] != [e for e in effects if e["event_seq"] in seqs]:
            raise EvidenceError("Barrier effects disagree with committed event prefix")
        caller = b["caller_state"]
        if caller not in states or states.index(caller) < states.index(prior_state):
            raise EvidenceError("Barrier caller state is absent from or regresses the caller trace")
        prior_state = caller
        expected_state = {"accepted": "PENDING", "fence_installed": "PENDING",
                          "completion_observed": "INSTALLED_CONFIRMED",
                          "terminal_observation": record["caller_state"]}.get(b["name"])
        if expected_state is not None and caller != expected_state:
            raise EvidenceError("Barrier name and caller state disagree")
    if barriers[-1]["committed_events"] != events or barriers[-1]["effects"] != effects:
        raise EvidenceError("Terminal barrier disagrees with final saved sink")


def reconcile(summary: dict, records: dict) -> list[dict]:
    expected = {(p, s) for p in PATHS for s in SCHEDULES}
    pairs = [(r["path"], r["schedule"]) for r in summary["rows"]]
    if set(pairs) != expected or len(pairs) != len(expected) or set(records) != expected:
        raise EvidenceError("Expected exactly direct/framework × S0–S5, once each")
    if summary["fixed_cases"] != len(expected):
        raise EvidenceError("Historical summary case count disagrees")
    result = []
    for saved in summary["rows"]:
        row = derive_case(records[(saved["path"], saved["schedule"])])
        for key in ("path", "schedule", "caller_state", "fence_seq", "effect_count", "effect_sequences"):
            if saved[key] != row[key]:
                raise EvidenceError(f"Summary/raw mismatch: {row['path']}/{row['schedule']} {key}")
        if saved["attempt_result"] != records[(row["path"], row["schedule"])]["execute_response"]:
            raise EvidenceError("Summary/raw attempt result mismatch")
        # Historical convention stores zero even when no fence exists. Preserve
        # that value but display N/A for the conditional post-fence question.
        if saved["post_fence_effect_count"] != (row["post_fence_effect_count"] or 0):
            raise EvidenceError("Summary/raw post-fence count mismatch")
        row["historical_post_fence_field"] = saved["post_fence_effect_count"]
        result.append(row)
    return result


def barrier_rows(record: dict) -> list[dict]:
    """Saved capture order, not timestamps or a complete distributed event log."""
    result = []
    for i, b in enumerate(record["barriers"]):
        fences = [e["seq"] for e in b["committed_events"] if e["kind"] == "revocation"]
        result.append(dict(capture=i + 1, barrier=b["name"], caller=b["caller_state"],
                           fence=fences[0] if fences else None,
                           effects=len(b["effects"])))
    return result


def challenge_claims(rows: list[dict]) -> list[dict]:
    """Fixed counterexample queries; not general natural-language fact checking."""
    checks = [
        ("C1", "Unconfirmed at observation end means no fence was installed.",
         lambda r: r["caller_state"] == "UNCONFIRMED_AT_OBSERVATION_END" and r["fence_seq"] is not None),
        ("C2", "Unconfirmed at observation end means a fence was installed.",
         lambda r: r["caller_state"] == "UNCONFIRMED_AT_OBSERVATION_END" and r["fence_seq"] is None),
        ("C3", "Caller confirmation means no effect occurred in the window.",
         lambda r: r["caller_state"] == "INSTALLED_CONFIRMED" and r["effect_count"] > 0),
    ]
    return [dict(claim_id=key, proposition=text,
                 status="counterexample in selected records" if any(pred(r) for r in rows)
                 else "unresolved in selected records; not established",
                 witnesses=[f"{r['path']}/{r['schedule']}" for r in rows if pred(r)])
            for key, text, pred in checks]


@dataclass
class ReviewRun:
    scope: Scope
    evidence: EvidenceStore
    rows: list[dict]
    challenges: list[dict]
    audit: list[dict] = field(default_factory=list)

    def brief(self) -> dict:
        fenced = [r for r in self.rows if r["fence_seq"] is not None]
        return {
            "question": QUESTION,
            "selected_cases": len(self.rows),
            "effects": sum(r["effect_count"] for r in self.rows),
            "revoked_denials": sum(r["outcome"] == "denied" and r["reason"] == "revoked" for r in self.rows),
            "cases_with_fence": len(fenced),
            "post_fence_effects_in_fenced_cases": sum(r["post_fence_effect_count"] for r in fenced) if fenced else None,
            "no_fence_cases": len(self.rows) - len(fenced),
            "challenge_results": self.challenges,
            "basis": "Recomputed selected facts from preserved JSON; summary agreement checked. Historical execution and full checker audit not rerun.",
            "limits": self.evidence.summary["limits"],
            "temporal": "Synthetic artifact-only prototype exists; native qualification remains blocked, no measured Temporal result.",
        }


def run_workbench(root: Path, scope: Scope = Scope()) -> ReviewRun:
    """Six real, bounded stages. No agent, model, LangGraph or research service."""
    if not isinstance(scope, Scope):
        raise EvidenceError("Expected a validated Scope")
    audit = [dict(stage="scope", outcome="bounded", detail=f"{len(scope.paths)} paths × {len(scope.schedules)} schedules")]
    store = EvidenceStore.load(root)
    audit.append(dict(stage="verify", outcome="matched", detail=f"{len(store.receipts)} input files; {len(store.sources)} source snapshots"))
    audit.append(dict(stage="reconcile", outcome="matched", detail=f"{len(store.rows)} raw JSON cases agree with selected summary fields"))
    rows = store.select(scope)
    audit.append(dict(stage="retrieve", outcome="selected", detail=f"{len(rows)} saved cases; no new observations"))
    challenges = challenge_claims(rows)
    audit.append(dict(stage="challenge", outcome="evaluated", detail="3 fixed counterexample queries"))
    audit.append(dict(stage="brief", outcome="assembled", detail="Derived facts, source links, uncertainty and dated status overlay"))
    return ReviewRun(scope, store, rows, challenges, audit)
