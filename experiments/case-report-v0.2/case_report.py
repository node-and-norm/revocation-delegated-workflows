"""Unexecuted deterministic saved-artifact POC; spec 6eaf9b7, no runtime actions.

The trusted extractor and report consumer are separate API boundaries. A receipt
is a local custodian assertion, NOT a signature, independent witness or proof.
Import has no I/O. There is deliberately no automatic command-line entry point.
"""
from copy import deepcopy
from hashlib import sha256
from html import escape
import json
import math
import re
from zipfile import ZipFile

SPEC_REVISION = "6eaf9b7e9ddb67f0e2fc25849ca031373805db57"
SOURCE_REVISION = "1866a73e61049c6e60354c0e4a565c8482736d33"
ARCHIVE_HASH = "adf5e66cb0ad90038cde189330ee46877fabda26f1d829d3ae9b734c44af827c"
MEMBERS = {
    "S4": ("measured01/framework/S4/record.json", "265d275eaadf11b9537299fce72ea164df9d7fafa756a53b62e8cd48ef07ffce", (1, 3, 5, 6, 7, 8, 9)),
    "S5": ("measured01/framework/S5/record.json", "304414e8e12dfaa39d650d3d8f87a9d6ce5f76946969a65db99c7288095cb665", (1, 3, 5, 6, 7)),
}
CATEGORIES = ("requester", "authority", "events", "effects")
VERSION = "case-report-packet/0.2"
RECEIPT_VERSION = "case-report-receipt/0.2"
EXTRACTOR = "case-report-extractor/0.2-unexecuted-candidate"
BOUNDARY = "saved terminal snapshot of selected local framework case"
PACKET_KEYS = {"packet_id", "schema_version", "source_case", "source_path", "source_archive_sha256", "source_member_sha256", "input_revision", "packet_boundary", "fixture_kind", "transformations", "expected_categories", *CATEGORIES}
RECEIPT_KEYS = {"receipt_schema_version", "packet_id", "packet_schema_version", "packet_sha256", "digest_algorithm", "trusted_source_manifest_revision", "source_checks", "extractor_version", "transformation_scope", "verification_result"}


class InvalidInput(ValueError):
    """Explicit intake rejection, not evidence of an absent event."""


def require(ok, reason):
    if not ok:
        raise InvalidInput(reason)


def strict_json(raw):
    require(type(raw) is bytes, "input must be original bytes")
    require(not raw.startswith(b"\xef\xbb\xbf"), "UTF-8 BOM forbidden")
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    def constant(value):
        raise InvalidInput("non-finite JSON number: " + value)
    try:
        value = json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=pairs, parse_constant=constant)
        def finite(node):
            if type(node) is float:
                require(math.isfinite(node), "non-finite decoded number")
            elif type(node) is dict:
                for child in node.values():
                    finite(child)
            elif type(node) is list:
                for child in node:
                    finite(child)
        finite(value)
        return value
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InvalidInput(str(exc)) from exc


def encode(value):
    """Producer serialization only; consumer always hashes original received bytes."""
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")


def digest(raw):
    return sha256(raw).hexdigest()


def exact_keys(value, keys, where):
    require(type(value) is dict and set(value) == set(keys), "unexpected/missing fields: " + where)


def text(value, where):
    require(type(value) is str and bool(value), "nonempty string required: " + where)


def hexadecimal(value):
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def integer(value):
    return type(value) is int and value >= 0


def source_identity(packet):
    """Use pinned independent constants, never packet-provided expected hashes."""
    case = packet["source_case"]
    require(case in MEMBERS, "source case outside pinned manifest")
    member, member_hash, _ = MEMBERS[case]
    require(packet["source_path"] == member, "source member mismatch")
    require(packet["source_archive_sha256"] == ARCHIVE_HASH, "archive identity mismatch")
    require(packet["source_member_sha256"] == member_hash, "member identity mismatch")
    require(packet["input_revision"] == SOURCE_REVISION, "source revision mismatch")
    return member, member_hash


def validate_packet(packet):
    exact_keys(packet, PACKET_KEYS, "packet")
    require(packet["schema_version"] == VERSION, "unknown packet schema")
    for name in ("packet_id", "source_case", "source_path", "input_revision", "packet_boundary"):
        text(packet[name], name)
    for name in ("source_archive_sha256", "source_member_sha256"):
        require(hexadecimal(packet[name]), "invalid SHA-256: " + name)
    require(packet["fixture_kind"] in ("derived_original", "constructed"), "unknown fixture kind")
    require(type(packet["transformations"]) is list and all(type(x) is str and x for x in packet["transformations"]), "invalid transformations")
    require(packet["fixture_kind"] != "constructed" or bool(packet["transformations"]), "constructed packet needs transformations")
    require(packet["expected_categories"] == list(CATEGORIES), "expected category declaration differs from schema")
    ids = set()
    original_pointers = set()
    for category in CATEGORIES:
        section = packet[category]
        exact_keys(section, {"availability", "items", "coverage"}, category)
        require(section["availability"] in ("present", "unavailable"), "invalid availability")
        require(type(section["items"]) is list, "items must be array")
        coverage = section["coverage"]
        exact_keys(coverage, {"status", "boundary", "basis"}, "coverage")
        require(coverage["status"] in ("declared_complete", "declared_partial", "unknown"), "invalid coverage")
        for key in ("boundary", "basis"):
            require(coverage[key] is None or (type(coverage[key]) is str and bool(coverage[key])), "invalid coverage " + key)
        if coverage["status"] == "declared_complete":
            require(coverage["boundary"] is not None and coverage["basis"] is not None, "complete needs boundary/basis")
        if section["availability"] == "unavailable":
            require(not section["items"] and coverage["status"] == "unknown", "unavailable is not observed empty")
        for item in section["items"]:
            exact_keys(item, {"item_id", "source_member", "pointer", "value", "origin", "boundary"}, "item")
            for key in ("item_id", "source_member", "pointer", "boundary"):
                text(item[key], key)
            require(item["item_id"] not in ids, "duplicate item ID")
            ids.add(item["item_id"])
            require(item["source_member"] == packet["source_path"], "item source member mismatch")
            require(item["origin"] in ("original", "constructed"), "unknown item origin")
            require(item["origin"] == "original" or packet["fixture_kind"] == "constructed", "unlabeled constructed item")
            if item["origin"] == "original":
                require(item["pointer"] not in original_pointers, "duplicate original source pointer")
                original_pointers.add(item["pointer"])
            patterns = {"requester": r"/caller_state", "authority": r"/sink/authority/[0-9]+", "events": r"/sink/events/[0-9]+", "effects": r"/sink/effects/[0-9]+"}
            require(re.fullmatch(patterns[category], item["pointer"]) is not None, "pointer outside allowlist")
            require(type(item["value"]) is (str if category == "requester" else dict), "invalid item value type")
    source_identity(packet)


def validate_receipt(receipt, raw, packet):
    exact_keys(receipt, RECEIPT_KEYS, "receipt")
    require(receipt["receipt_schema_version"] == RECEIPT_VERSION, "unknown receipt schema")
    require(receipt["packet_schema_version"] == packet["schema_version"], "packet schema binding mismatch")
    require(receipt["packet_id"] == packet["packet_id"], "packet ID binding mismatch")
    require(receipt["digest_algorithm"] == "sha256" and hexadecimal(receipt["packet_sha256"]), "invalid receipt digest")
    require(receipt["packet_sha256"] == digest(raw), "packet byte digest mismatch")
    require(receipt["trusted_source_manifest_revision"] == SOURCE_REVISION, "receipt source revision mismatch")
    text(receipt["extractor_version"], "extractor version")
    require(receipt["transformation_scope"] == packet["transformations"], "transformation scope mismatch")
    require(receipt["verification_result"] in ("match", "mismatch", "unavailable"), "unknown verification result")
    checks = receipt["source_checks"]
    require(type(checks) is list and len(checks) == 2, "archive and member checks required")
    member, member_hash = source_identity(packet)
    expected = {"archive": ("withdrawal_interface_study_v01_20261103.zip", ARCHIVE_HASH), "member": (member, member_hash)}
    seen = set()
    for check in checks:
        exact_keys(check, {"kind", "identity", "expected_sha256", "observed_sha256", "result"}, "source check")
        kind = check["kind"]
        require(kind in expected and kind not in seen, "duplicate/unknown source check")
        seen.add(kind)
        identity, pin = expected[kind]
        require(check["identity"] == identity and check["expected_sha256"] == pin, "source check not independently pinned")
        observed = check["observed_sha256"]
        require(observed is None or hexadecimal(observed), "invalid observed hash")
        correct_result = "unavailable" if observed is None else ("match" if observed == pin else "mismatch")
        require(check["result"] == correct_result, "inconsistent source check")
    require(receipt["verification_result"] == "match" and all(c["result"] == "match" for c in checks), "source verification not matched")


def category(items, boundary=BOUNDARY, basis="all entries of declared original field selected"):
    return {"availability": "present", "items": items, "coverage": {"status": "declared_complete", "boundary": boundary, "basis": basis}}


def unavailable():
    return {"availability": "unavailable", "items": [], "coverage": {"status": "unknown", "boundary": None, "basis": None}}


def extract(archive_path, case, packet_id):
    """Trusted local extraction only. Reads originals; returns bytes; writes nothing.

    The case chooses a pinned member/allowlist, NOT classification results.
    Archive/member digest failure raises before producing a successful receipt.
    """
    require(case in MEMBERS, "unsupported original source")
    with open(archive_path, "rb") as stream:
        archive_bytes = stream.read()
    require(digest(archive_bytes) == ARCHIVE_HASH, "original archive digest mismatch")
    from io import BytesIO
    member, member_hash, sequences = MEMBERS[case]
    with ZipFile(BytesIO(archive_bytes)) as archive:
        require(archive.namelist().count(member) == 1, "ambiguous source member")
        raw = archive.read(member)
    require(digest(raw) == member_hash, "original member digest mismatch")
    original = strict_json(raw)
    def item(pointer, value):
        return {"item_id": packet_id + ":" + pointer, "source_member": member, "pointer": pointer, "value": deepcopy(value), "origin": "original", "boundary": BOUNDARY}
    events = [item("/sink/events/" + str(i), event) for i, event in enumerate(original["sink"]["events"]) if event["seq"] in sequences]
    require(tuple(e["value"]["seq"] for e in events) == sequences, "pinned event allowlist not found")
    packet = {
        "packet_id": packet_id, "schema_version": VERSION, "source_case": case, "source_path": member,
        "source_archive_sha256": ARCHIVE_HASH, "source_member_sha256": member_hash, "input_revision": SOURCE_REVISION,
        "packet_boundary": BOUNDARY, "fixture_kind": "derived_original", "transformations": ["select caller_state, authority entries, explicit event sequence allowlist and effect entries; exclude all other fields"], "expected_categories": list(CATEGORIES),
        "requester": category([item("/caller_state", original["caller_state"])]),
        "authority": category([item("/sink/authority/" + str(i), value) for i, value in enumerate(original["sink"]["authority"])]),
        "events": category(events, basis="all entries of explicitly selected event sequence allowlist; not entire event stream"),
        "effects": category([item("/sink/effects/" + str(i), value) for i, value in enumerate(original["sink"]["effects"])]),
    }
    validate_packet(packet)
    return seal_local(packet)


def seal_local(packet):
    """TRUSTED CUSTODIAN ONLY. Not public validation or authentication.

    Caller must have verified original bytes and declared all transformations.
    This function does NOT itself inspect the archive; never use to bless an
    untrusted imported packet. The receipt is an assertion, not a signature.
    """
    validate_packet(packet)
    raw = encode(packet)
    member, member_hash = source_identity(packet)
    checks = [{"kind": kind, "identity": identity, "expected_sha256": h, "observed_sha256": h, "result": "match"} for kind, identity, h in (("archive", "withdrawal_interface_study_v01_20261103.zip", ARCHIVE_HASH), ("member", member, member_hash))]
    receipt = {"receipt_schema_version": RECEIPT_VERSION, "packet_id": packet["packet_id"], "packet_schema_version": VERSION, "packet_sha256": digest(raw), "digest_algorithm": "sha256", "trusted_source_manifest_revision": SOURCE_REVISION, "source_checks": checks, "extractor_version": EXTRACTOR, "transformation_scope": deepcopy(packet["transformations"]), "verification_result": "match"}
    return raw, encode(receipt)


def item_ref(packet, item):
    return {"namespace": [packet["packet_id"], packet["source_case"], packet["source_archive_sha256"], packet["source_member_sha256"]], "item_id": item["item_id"], "source_member": item["source_member"], "pointer": item["pointer"], "origin": item["origin"], "boundary": item["boundary"]}


def report(raw, receipt_raw=None):
    """Read supplied bytes only; never access archive, network, labels-as-answers."""
    result = {"status": "unbound", "scope": None, "panels": {k: [] for k in ("requester", "authority", "action", "evidence")}, "issues": [], "timeline": [], "supplied_packet": None, "limits": ["Local custodian receipt is not independent authentication.", "Supplied inventory is not global system coverage.", "Synthetic saved observations, not live-model judgment or Temporal qualification."]}
    try:
        packet = strict_json(raw)
        # Keep even malformed/unbound positive assertions inspectable, unclassified.
        result["supplied_packet"] = packet
        validate_packet(packet)
        result["scope"] = {k: packet[k] for k in ("packet_id", "source_case", "source_path", "packet_boundary", "fixture_kind")}
        require(receipt_raw is not None, "source verification receipt unavailable")
        validate_receipt(strict_json(receipt_raw), raw, packet)
    except (InvalidInput, TypeError, KeyError) as exc:
        result["issues"].append(str(exc))
        for panel in result["panels"]:
            result["panels"][panel].append({"classification": "unknown", "text": "Unknown from supplied packet: source binding unresolved.", "sources": [], "rule": "intake-gate"})
        return result
    result["status"] = "source_bound_under_local_custody"
    def say(panel, classification, message, items, rule):
        result["panels"][panel].append({"classification": classification, "text": message, "sources": [item_ref(packet, i) for i in items], "rule": rule})
    def rows(name):
        return packet[name]["items"]
    for name in CATEGORIES:
        section = packet[name]
        say("evidence", "recorded_metadata", name + ": " + section["availability"] + "; coverage " + section["coverage"]["status"], rows(name), "category-metadata-not-global-completeness")
    caller = rows("requester")
    if caller:
        values = {i["value"] for i in caller}
        say("requester", "conflicted" if len(values) > 1 else "recorded", "Saved caller state: " + ", ".join(sorted(values)), caller, "caller-observation-only")
    else:
        say("requester", "unknown", "Request caller observation at the declared boundary.", [], "missing-caller")
    authority = rows("authority")
    good_authority = []
    for item in authority:
        v = item["value"]
        if set(v) == {"root", "epoch", "active"} and type(v["root"]) is str and integer(v["epoch"]) and type(v["active"]) is int and v["active"] in (0, 1):
            good_authority.append(item)
        else:
            say("authority", "unbound", "Malformed authority assertion; inspect supplied value.", [item], "authority-shape")
    groups = {}
    for item in good_authority:
        v = item["value"]
        groups.setdefault((v["root"], v["epoch"], item["boundary"]), []).append(item)
    if not authority:
        say("authority", "unknown", "Request authority snapshot and transition records.", [], "missing-authority")
    events = rows("events")
    valid_events = []
    seen = set()
    stream_bad = False
    for item in events:
        v = item["value"]
        if set(v) != {"seq", "kind", "data"} or not integer(v["seq"]) or type(v["kind"]) is not str or type(v["data"]) is not dict or v["seq"] in seen:
            say("action", "unbound", "Malformed or duplicate event sequence; no joined action conclusion.", [item], "event-shape")
            stream_bad = True
            continue
        seen.add(v["seq"])
        valid_events.append(item)
        result["timeline"].append({"sequence": v["seq"], "kind": v["kind"], "source": item_ref(packet, item), "value": v["data"]})
    result["timeline"].sort(key=lambda x: x["sequence"])
    if stream_bad:
        valid_events = []  # Do not use a selectively retained part of a bad stream.
    def kind(name):
        return [i for i in valid_events if i["value"]["kind"] == name]
    # Snapshot observations remain visible; association is a separate claim.
    context_roots = []
    for item in kind("bootstrap") + kind("grant"):
        data = item["value"]["data"]
        value = data.get("result") if item["value"]["kind"] == "grant" else data
        if type(value) is dict and type(value.get("root")) is str:
            context_roots.append((value["root"], item))
    for (root, epoch, boundary), group in groups.items():
        active = {i["value"]["active"] for i in group}
        message = "Snapshot root " + root + ", epoch " + str(epoch) + ", active assertions " + str(sorted(active)) + "; boundary " + boundary
        if len(active) > 1:
            say("authority", "conflicted", message + ". Request original authority/event records at this boundary and provenance clarification to resolve the conflict.", group, "same-boundary-authority-comparison")
        elif context_roots and root not in {r for r, _ in context_roots}:
            say("authority", "unbound", message + ". Direct snapshot assertion retained, but unrelated to supplied bootstrap/grant context; not selected-action authority. Request matching authority/context records.", group + [i for _, i in context_roots], "snapshot-context-root-mismatch")
        elif not context_roots:
            say("authority", "recorded", message + ". Direct snapshot only; selected-action association unknown because bootstrap/grant context is unavailable. Request matching context; no linkage inferred.", group, "snapshot-without-action-context")
        else:
            say("authority", "recorded", message + ". Root occurs in supplied bootstrap/grant context; this snapshot does not itself establish an action outcome.", group + [i for r, i in context_roots if r == root], "snapshot-context-root-reference")
    for item in kind("revocation"):
        v = item["value"]["data"].get("result", {})
        if type(v) is dict and v.get("outcome") == "revocation" and type(v.get("root")) is str and integer(v.get("withdrawn_epoch")) and integer(v.get("new_epoch")):
            say("authority", "recorded", "Withdrawal event sequence " + str(item["value"]["seq"]) + ": " + v["root"] + " epoch " + str(v["withdrawn_epoch"]) + " → " + str(v["new_epoch"]), [item], "recorded-transition-not-snapshot-substitution")
        else:
            say("authority", "unbound", "Malformed revocation record.", [item], "revocation-shape")
    # Join only explicit execute receipt -> unique prior admission+grant+bootstrap.
    attempts = []
    execute_receipts = [i for i in kind("receipt") if type(i["value"]["data"].get("request")) is dict and i["value"]["data"]["request"].get("op") == "execute"]
    for receipt in kind("receipt"):
        req = receipt["value"]["data"].get("request")
        if type(req) is not dict or req.get("op") != "execute":
            continue
        same_id = [i for i in execute_receipts if i["value"]["data"]["request"].get("id") == req.get("id")]
        if len(same_id) != 1:
            say("action", "unbound", "Repeated execute request ID; outcome attribution ambiguous. Request uniquely identified receipt/result association.", same_id, "duplicate-execute-id")
            continue
        admissions = [i for i in kind("admission") if type(i["value"]["data"].get("result")) is dict and i["value"]["seq"] < receipt["value"]["seq"] and all(i["value"]["data"]["result"].get(k) == req.get(k) and req.get(k) is not None for k in ("grant", "ticket", "scope"))]
        if len(admissions) != 1:
            say("action", "unbound", "Execute receipt lacks unique matching prior admission.", [receipt], "attempt-admission-join")
            continue
        adm = admissions[0]
        identity = adm["value"]["data"]["result"]
        grants = [i for i in kind("grant") if type(i["value"]["data"].get("result")) is dict and i["value"]["seq"] < adm["value"]["seq"] and all(i["value"]["data"]["result"].get(k) == identity.get(k) and identity.get(k) is not None for k in ("grant", "scope", "root", "epoch"))]
        bootstraps = [i for i in kind("bootstrap") if i["value"]["seq"] < adm["value"]["seq"] and all(i["value"]["data"].get(k) == identity.get(k) and identity.get(k) is not None for k in ("root", "epoch", "scope"))]
        if len(grants) != 1 or len(bootstraps) != 1 or type(req.get("id")) is not str:
            say("action", "unbound", "Execute receipt lacks unique grant/bootstrap context.", [receipt, adm], "attempt-context-join")
            continue
        grant = grants[0]["value"]["data"]["result"]
        bootstrap = bootstraps[0]["value"]["data"]
        actor = receipt["value"]["data"].get("actor")
        if not (type(actor) is str and actor == req.get("claim") == grant.get("owner") == bootstrap.get("child") and grant.get("parent_grant") == bootstrap.get("parent_grant") and type(grant.get("parent_grant")) is str and integer(identity.get("epoch")) and type(identity.get("root")) is str and grant.get("outcome") == "grant" and identity.get("outcome") == "admission"):
            say("action", "unbound", "Actor, grant or bootstrap identity inconsistent.", [receipt, adm, grants[0], bootstraps[0]], "attempt-actor-context-mismatch")
            continue
        context = [receipt, adm, grants[0], bootstraps[0]]
        attempts.append((receipt, identity, context))
        say("action", "derived", "Attempt " + req["id"] + " received at local sequence " + str(receipt["value"]["seq"]) + "; root/epoch derived through admission/grant/bootstrap, not directly in receipt.", context, "explicit-same-packet-attempt-join")
        for outcome in kind("denied") + kind("effect"):
            data = outcome["value"]["data"]
            if data.get("request_id") != req["id"] or outcome["value"]["seq"] <= receipt["value"]["seq"]:
                continue
            value = data.get("result")
            if type(value) is not dict:
                continue
            if outcome["value"]["kind"] == "denied" and value.get("outcome") == "denied":
                say("action", "derived", "Attempt denied at sequence " + str(outcome["value"]["seq"]) + "; reason " + str(value.get("reason")) + ". This is not cumulative effect absence.", context + [outcome], "denial-request-id-join")
            elif outcome["value"]["kind"] == "effect" and value.get("outcome") == "effect" and all(value.get(k) == identity.get(k) for k in ("root", "epoch")) and value.get("effect_key") == identity.get("scope") and "payload" in req and value.get("payload") == req["payload"]:
                say("action", "derived", "Matching effect event at sequence " + str(outcome["value"]["seq"]) + ". Inventory completeness assessed separately.", context + [outcome], "effect-event-identity-join")
            else:
                say("action", "unbound", "Outcome identity inconsistent with joined attempt.", context + [outcome], "outcome-identity-mismatch")
    matched = []
    matched_identities = set()
    for effect in rows("effects"):
        v = effect["value"]
        candidates = []
        for receipt, identity, context in attempts:
            for event in kind("effect"):
                data = event["value"]["data"]
                res = data.get("result", {})
                req = receipt["value"]["data"]["request"]
                if type(res) is dict and res.get("outcome") == "effect" and "payload" in req and res.get("payload") == req["payload"] and data.get("request_id") == req["id"] and integer(v.get("event_seq")) and v["event_seq"] == event["value"]["seq"] and event["value"]["seq"] > receipt["value"]["seq"] and all(v.get(k) == res.get(k) and v.get(k) is not None for k in ("root", "epoch", "effect_key", "payload")) and v.get("root") == identity.get("root") and v.get("epoch") == identity.get("epoch") and v.get("effect_key") == identity.get("scope"):
                    candidates.append(context + [event, effect])
        if len(candidates) == 1:
            effect_identity = encode([packet["packet_id"], packet["source_case"], packet["source_archive_sha256"], packet["source_member_sha256"], effect["source_member"], v["event_seq"], v["root"], v["epoch"], v["effect_key"]])
            if effect_identity in matched_identities:
                say("action", "duplicate_evidence", "Duplicate evidence for an already counted effect identity; retained copy is not an additional effect.", candidates[0], "effect-identity-deduplication")
            else:
                matched_identities.add(effect_identity)
                matched.append(effect)
                say("action", "derived", "One matching local effect entry; source pointer " + effect["pointer"] + "; counted once by distinct effect identity.", candidates[0], "effect-entry-event-attempt-join")
        else:
            say("action", "unbound", "Positive effect assertion retained, but no unique matching event/attempt context.", [effect], "effect-unbound-not-absent")
    effects = packet["effects"]
    if effects["availability"] == "unavailable":
        say("action", "unknown", "Effect inventory unavailable; cumulative effects unknown. Request inventory for the declared boundary.", [], "missing-effect-inventory")
    elif effects["coverage"]["status"] != "declared_complete":
        say("action", "derived" if matched else "unknown", "At least " + str(len(matched)) + " distinct matched recorded effect identities; total count and coverage unknown." if matched else "Total count and coverage unknown; inspect any supplied positive assertions.", matched, "positive-evidence-with-incomplete-coverage")
    else:
        say("action", "recorded", str(len(rows("effects"))) + " entries in supplied local-effect inventory; " + str(len(matched)) + " distinct matched effect identities. Entry count includes any duplicate evidence, not additional effects. No claim of global absence or completeness.", rows("effects"), "declared-inventory-count-only")
    if not attempts:
        say("action", "unknown", "No bound attempt identified. Request matching receipt, admission, grant and result records.", [], "missing-bound-attempt")
    return result


def render_html(result):
    """Escaped, self-contained readable output; no scripts or external assets."""
    def dump(value):
        return escape(json.dumps(value, ensure_ascii=False, indent=2))
    parts = ['<!doctype html><meta charset="utf-8"><title>Bounded case report</title>', '<style>body{font:18px/1.6 system-ui;max-width:960px;margin:3em auto;padding:1em;color:#202124;background:#fff}section{border-top:1px solid #ccc;margin-top:2em}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}table{border-collapse:collapse;width:100%}td,th{padding:.6em;text-align:left;border:1px solid #ccc}</style>', '<h1>Four questions about one saved packet</h1><p>Unexecuted candidate renderer. A rendered report is not a new experiment.</p>', '<p>Binding: ' + escape(result['status']) + '</p><pre>' + dump(result['scope']) + '</pre>']
    for name, assertions in result['panels'].items():
        parts.append('<section><h2>' + escape(name.title()) + '</h2>')
        for assertion in assertions:
            parts.append('<p><strong>' + escape(assertion['classification']) + '</strong>: ' + escape(assertion['text']) + '</p><pre>' + dump({'rule': assertion['rule'], 'sources': assertion['sources']}) + '</pre>')
        parts.append('</section>')
    parts.append('<h2>Local event timeline (same information as table)</h2><pre>' + escape(' → '.join(str(i['sequence']) + ': ' + i['kind'] for i in result['timeline'])) + '</pre><table><tr><th>Sequence</th><th>Kind</th><th>Original locator</th></tr>')
    for event in result['timeline']:
        parts.append('<tr><td>' + str(event['sequence']) + '</td><td>' + escape(event['kind']) + '</td><td>' + escape(event['source']['source_member'] + '#' + event['source']['pointer']) + '</td></tr>')
    parts.append('</table><h2>Issues and limits</h2><pre>' + dump(result['issues'] + result['limits']) + '</pre><h2>Supplied packet (including unbound assertions)</h2><pre>' + dump(result['supplied_packet']) + '</pre>')
    return '\n'.join(parts)
