# Supported synthetic schema and allowlist

Schema version: `synthetic-artifact-0.1`. Protocol proposal: `0.3`. This document explains the implementation, not a production exporter contract.

The authoritative closed field definitions are in `artifacts.py`, `schema.py`, `engine.py` and `views.py`. Unsupported fields/versions require a new reviewed schema. The accepted source pins are TypeScript SDK 1.25.0 and historical gateway SHA256 `98445edd61af21bc5c740053f8a93f6c179e4c5efa7b28dd7363e779b8f059a9`. These identify compatibility assumptions, not a qualified runtime.

## Artifact registry

`registry.json` lists each input/output artifact's neutral ID, exact relative path, role, phase, schema version, byte length, SHA256 and producer. It does not hash itself. All regular files under the case directory must be declared. Duplicate IDs/paths, noncanonical paths, traversal, symlinks, extra files, altered bytes, unsupported encodings and malformed JSON fail integrity. Files are limited to 16 MiB and 256 registry entries. Native identifiers are positive lossless int64 values, never floats, booleans, exponential strings or leading-zero strings.

The root fixture registry is a synthetic package seal. Independent runtime phase seals remain unimplemented and are not inferred from this registry.

## Case and bindings

`case.json` includes cell/schedule only in the privileged case record, never in the caller identity extract. Generated case and attempt IDs are random neutral IDs. Preregistration contains intended Workflow/Activity IDs; returned run, schedule/start references and attempt live in `observed_binding.json`. Sink-only cases contain no native identities.

`producer_events.jsonl` uses closed event kinds and payloads. `record_id` may not use reserved `sink:` or `native:` graph namespaces. Every event binds case, operation, phase, producer position and observed native identity where applicable. Direct causal parents and same-producer order establish edges. Wall clocks are diagnostic and ignored for ordering. Unsupported later-phase records cannot erase a valid earlier-phase result.

Normalized native history uses a closed synthetic enum and attributes. Pagination and final-boundary records are checked in addition to contiguous IDs. Native and settlement result payloads accept only an empty object, `{"synthetic": true/false}`, or string `type`/`message` fields. Bridge responses are restricted to effect, duplicate, or denied-with-reason. This deliberately does not parse native Temporal encoded payloads.

Saved SQLite uses the historical gateway's actual authority, grants, tickets, events and effects tables. The reader opens `mode=ro&immutable=1`, `query_only`, and an explicit read transaction. It rejects views/triggers/noncanonical schema and limits rows. The source database must already be a consistent immutable snapshot. The checker does not perform a live database backup.

## Captures

Each phase capture names its operation, cut/boundary, linked interval, exact producer watermarks and flush acknowledgments, SQLite transaction/table boundary, native final-event boundary and queued/in-flight/uncertain work. Native terminal and Worker settlement must independently precede primary capture. Every dispatch is reconciled against a committed result or an explicit known-no-commit transport record. Response content alone cannot replace a committed ledger result.

P1 excludes release and cleanup. P2 has a matched observation release/receipt and separately scoped terminal history. K controls have P1 only. P3 is diagnostic, excluded from caller files, and can expose a contradiction in a prior no-pending certificate. These are trusted saved declarations, not proof of actual producer honesty.

## Caller files

Each view has exactly these files: `identity.json`, `configuration.json`, `client_events.jsonl`, `native_events.jsonl`, `worker_events.jsonl`, `bridge_events.jsonl`, `sink_lookup.json`, `capture.json`, `source_map.json`. A additionally has `envelope.json`; B must not. The source map records exact canonical locators, raw artifact/record references, phases/cuts/boundaries and content hashes. All underlying A/B file hashes and byte lengths must match.

`views.expected_view` is the concrete synthetic field transformation. It copies only selected validated event kinds and phase-permitted records. Sink lookup is checked against the raw saved tables. Optional authorized absence of a source is represented explicitly rather than substituting hidden evidence. Phase-inapplicable native files contain a declared not-applicable object. Cell labels, expected outcomes, private verdicts and mapping oracles are not copied.

Assertions contain exactly field, value, observer, operation scope, assertion phase and evidence references. A reference contains exactly artifact ID, structural locator, record ID, phase, cut ID and boundary ID. Each cited reference must belong to the supplied view; extra hidden references also fail support. Reference derivation is per view. Receipt-backed fence confirmation and ledger-backed fence existence remain separate.
