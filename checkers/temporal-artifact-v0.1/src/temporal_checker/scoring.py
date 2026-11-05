"""Artifact-only caller scoring. No native qualification or execution is performed.

References are already boundary-validated canonical identifiers from the checker.
The scoring layer never resolves identifiers or reads privileged evidence itself.
"""
import json

FIELDS = (
    "cancellation_request", "activity_call", "activity_execution",
    "workflow_execution", "fence", "effect_existence", "fence_existence",
    "effect_order_vs_fence", "effect_order_vs_request",
    "effect_order_vs_observed_cancellation",
)
LIFECYCLE_FIELDS = frozenset(("activity_call", "activity_execution", "workflow_execution"))
VALUES = {
    "cancellation_request": frozenset(("not_requested", "response_received", "error", "unresolved")),
    "activity_call": frozenset(("pending", "settled_with_recorded_result", "settled_with_recorded_failure", "unresolved")),
    "activity_execution": frozenset(("last_instrumented_point", "worker_invocation_settled", "native_terminal_record", "unresolved")),
    "workflow_execution": frozenset(("running", "exact_terminal_status", "unresolved")),
    "fence": frozenset(("confirmed_for_fixture_scope", "unresolved")),
    "effect_existence": frozenset(("present", "absent_with_complete_bounded_evidence", "unresolved")),
    "fence_existence": frozenset(("present", "absent_with_complete_bounded_evidence", "unresolved")),
    "effect_order_vs_fence": frozenset(("before", "after", "not_applicable_no_effect", "no_fence_in_complete_window", "unresolved")),
    "effect_order_vs_request": frozenset(("before", "after", "not_applicable_no_effect", "no_request", "unresolved")),
    "effect_order_vs_observed_cancellation": frozenset(("before", "after", "not_applicable_no_effect", "no_observation", "unresolved")),
}
CATEGORIES = (
    "correct_determinate", "justified_unresolved", "avoidable_unresolved",
    "unsupported_determinate", "contradicted", "malformed_or_omitted",
)
CLAIM_KEYS = frozenset(("field", "value", "observer", "scope", "assertion_phase", "evidence_refs"))


def planned_opportunities(cells=("M1", "M2", "M3", "M4", "K1", "K2")):
    """Fixed registered denominator per view, not independent observations."""
    cells = list(cells)
    if len(cells) != len(set(cells)) or any(c not in ("M1", "M2", "M3", "M4", "K1", "K2") for c in cells):
        raise ValueError("Cells must be unique measured-cell identifiers")
    return sum(7 if c.startswith("K") else 20 for c in cells)


REF_KEYS = frozenset(("artifact_id", "locator", "record_id", "phase", "cut_id", "boundary_id"))


def _key(ref):
    return json.dumps(ref, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _refset(refs):
    return {_key(ref) for ref in refs}


def _refs(value, strict=False):
    if not isinstance(value, list):
        return False
    for ref in value:
        if isinstance(ref, str) and ref and not strict:
            continue
        if not isinstance(ref, dict) or set(ref) != REF_KEYS or any(not isinstance(v, str) or not v.strip() for v in ref.values()) or ref["phase"] not in ("P0", "P1", "P2"):
            return False
    return len(value) == len(_refset(value))


def _ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def _metrics(report):
    counts = report["counts"]
    return {
        "determinate_claim_support_rate": _ratio(counts["correct_determinate"], report["determinate_claims"]),
        "conclusive_coverage": _ratio(counts["correct_determinate"], report["reference_decidable_opportunities"]),
        "required_output_completion": _ratio(report["valid_output_opportunities"], report["evaluated_opportunities"]),
        "planned_completion": _ratio(report["evaluated_opportunities"], report["planned_opportunities"]),
    }


def score_assertions(required_fields: list[str], reference: dict[str, dict], claims: list | None, context: dict) -> dict:
    """Score against *permitted* reference facts; hidden agreement is not support.

    Missing input is availability missingness, not caller omission. Bad scorer
    configuration raises ValueError; malformed caller output is a scored category.
    Reference evidence must be a nonempty sufficient set for determinate facts.
    Every cited reference must be permitted, including unnecessary extra citations.
    """
    if not isinstance(required_fields, list) or any(not isinstance(f, str) or f not in FIELDS for f in required_fields) or len(set(required_fields)) != len(required_fields):
        raise ValueError("required_fields must contain unique contract fields")
    if not isinstance(context, dict) or not {"phase", "scope", "permitted_refs", "evidence_supplied"} <= set(context) or (isinstance(context, dict) and set(context) - {"phase", "scope", "permitted_refs", "evidence_supplied", "strict_refs"}):
        raise ValueError("context has missing or unknown keys")
    strict = context.get("strict_refs", False)
    if type(strict) is not bool:
        raise ValueError("strict_refs must be boolean")
    if any(not isinstance(context[k], str) or not context[k].strip() for k in ("phase", "scope")) or not _refs(context["permitted_refs"], strict) or type(context["evidence_supplied"]) is not bool:
        raise ValueError("invalid context values")
    if context["phase"] not in ("P1", "P2"):
        raise ValueError("Only P1 and P2 are caller assertion phases")
    report = {
        "phase": context["phase"], "scope": context["scope"],
        "planned_opportunities": len(required_fields),
        "evidence_supplied_opportunities": 0, "evaluated_opportunities": 0,
        "reference_decidable_opportunities": 0, "determinate_claims": 0,
        "valid_output_opportunities": 0,
        "counts": dict.fromkeys(CATEGORIES, 0), "opportunities": [], "diagnostics": [],
    }
    if not context["evidence_supplied"]:
        report["opportunities"] = [{"field": f, "status": "evidence_unavailable", "category": None, "reasons": ["declared input was not supplied"]} for f in required_fields]
        report["metrics"] = _metrics(report)
        return report
    if not isinstance(reference, dict):
        raise ValueError("reference must be a mapping")
    permitted = _refset(context["permitted_refs"])
    if context["phase"] == "P1" and any(isinstance(ref, dict) and ref["phase"] == "P2" for ref in context["permitted_refs"]):
        raise ValueError("P1 may not permit P2 evidence")
    decidable = {}
    for field in required_fields:
        ref = reference.get(field)
        if not isinstance(ref, dict) or not {"value", "evidence_refs"} <= set(ref) or set(ref) - {"value", "evidence_refs", "allowed_values"}:
            raise ValueError("invalid reference for " + field)
        if not isinstance(ref["value"], str) or ref["value"] not in VALUES[field] or not _refs(ref["evidence_refs"], strict):
            raise ValueError("invalid reference value or evidence for " + field)
        if "allowed_values" in ref and (not isinstance(ref["allowed_values"], list) or not ref["allowed_values"] or any(not isinstance(v, str) or v not in VALUES[field] for v in ref["allowed_values"]) or ref["value"] not in ref["allowed_values"]):
            raise ValueError("invalid allowed_values for " + field)
        decidable[field] = ref["value"] != "unresolved" and bool(ref["evidence_refs"]) and _refset(ref["evidence_refs"]) <= permitted
    report["reference_decidable_opportunities"] = sum(decidable.values())
    indexed = {}
    if claims is not None and not isinstance(claims, list):
        report["diagnostics"].append({"reason": "claims must be a list or null"})
    for index, claim in enumerate(claims if isinstance(claims, list) else []):
        if not isinstance(claim, dict) or not isinstance(claim.get("field"), str):
            report["diagnostics"].append({"index": index, "reason": "claim lacks a string field"})
            continue
        field = claim["field"]
        if field not in required_fields:
            report["diagnostics"].append({"index": index, "field": field, "reason": "unknown or inapplicable field"})
            continue
        indexed.setdefault(field, []).append(claim)
    for field in required_fields:
        entries = indexed.get(field, [])
        reasons = []
        category = "malformed_or_omitted"
        if not entries:
            reasons.append("required assertion omitted")
        elif len(entries) != 1:
            reasons.append("duplicate field claims")
        else:
            claim = entries[0]
            if set(claim) != CLAIM_KEYS:
                reasons.append("missing or unknown assertion keys")
            elif not isinstance(claim["value"], str) or claim["value"] not in VALUES[field] or ("allowed_values" in reference[field] and claim["value"] not in reference[field]["allowed_values"]):
                reasons.append("invalid contract value")
            elif not isinstance(claim["observer"], str) or not claim["observer"].strip():
                reasons.append("observer must be nonempty")
            elif claim["scope"] != context["scope"] or claim["assertion_phase"] != context["phase"]:
                reasons.append("assertion scope or phase mismatch")
            elif not _refs(claim["evidence_refs"], strict):
                reasons.append("invalid evidence reference list")
            else:
                report["valid_output_opportunities"] += 1
                cited = _refset(claim["evidence_refs"])
                if claim["value"] == "unresolved":
                    # Unresolved needs no evidence, but cannot smuggle hidden refs.
                    if not cited <= permitted:
                        category = "malformed_or_omitted"
                        report["valid_output_opportunities"] -= 1
                        reasons.append("unresolved assertion cites unavailable evidence")
                    else:
                        category = "avoidable_unresolved" if decidable[field] else "justified_unresolved"
                else:
                    report["determinate_claims"] += 1
                    if decidable[field] and claim["value"] != reference[field]["value"]:
                        category = "contradicted"
                        reasons.append("permitted reference establishes an incompatible value")
                    elif not decidable[field] or not cited <= permitted or not _refset(reference[field]["evidence_refs"]) <= cited:
                        category = "unsupported_determinate"
                        reasons.append("insufficient cited permitted evidence")
                    else:
                        category = "correct_determinate"
        report["counts"][category] += 1
        report["opportunities"].append({"field": field, "status": "evaluated", "category": category, "reference_decidable": decidable[field], "reasons": reasons, "evidence_refs": entries[0].get("evidence_refs", []) if len(entries) == 1 and _refs(entries[0].get("evidence_refs", []), strict) else []})
    report["evidence_supplied_opportunities"] = len(required_fields)
    report["evaluated_opportunities"] = len(required_fields)
    report["metrics"] = _metrics(report)
    return report


def aggregate_reports(reports: list, planned_opportunities: int) -> dict:
    """Aggregate a single view without shrinking its registered denominator.

    Pair matching, attempt identity and exclusion of nonmeasured fixtures are the
    parent ledger's responsibility. Do not pass both views as independent cases.
    """
    if type(planned_opportunities) is not int or planned_opportunities < 0:
        raise ValueError("planned denominator must be a nonnegative integer")
    report = {"planned_opportunities": planned_opportunities, "counts": dict.fromkeys(CATEGORIES, 0)}
    for key in ("evidence_supplied_opportunities", "evaluated_opportunities", "reference_decidable_opportunities", "determinate_claims", "valid_output_opportunities"):
        report[key] = sum(r[key] for r in reports)
    registered = sum(r["planned_opportunities"] for r in reports)
    if registered > planned_opportunities:
        raise ValueError("reports exceed planned denominator; duplicate or mixed views?")
    for category in CATEGORIES:
        report["counts"][category] = sum(r["counts"][category] for r in reports)
    report["unrepresented_planned_opportunities"] = planned_opportunities - registered
    report["evidence_unavailable_opportunities"] = planned_opportunities - report["evidence_supplied_opportunities"]
    report["metrics"] = _metrics(report)
    return report
