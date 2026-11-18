# Saved-case report component: source draft, not executed

This is implementation preparation for specification v0.2 at commit
`6eaf9b7e9ddb67f0e2fc25849ca031373805db57`. It is not an experimental result,
qualified instrument, tested release or merge recommendation.

## Reader route

1. Read the specification notebook for the four questions.
2. `case_report.py`: `extract` reads only the pinned saved archive and creates an
   allowlisted packet plus detached local receipt; `report` consumes only those
   byte strings; `render_html` prepares four panels, source pointers and timeline.
3. `test_case_report.py` contains prospective checks, not results.
4. `REQUIREMENT_MAP.md` gives implementation boundaries and remaining work.
5. `ASSIGNMENT.txt` and `IMPLEMENTER_RETURN.txt` preserve the actual assignment and
   returned account. The original assignment contains local workspace paths; a
   later repository copy should label any redaction rather than silently change it.

No candidate code, tests, notebook cells, VM actions, model calls or new study
were executed in this preparation. Shell commands were used to inspect existing
source files and author these files. Original archives were read only.
Exact deployed model/version metadata was not supplied to this implementer;
none is asserted here. This is AI-assisted source preparation, not human validation.

## Proposed API (not invoked)

`extract(archive_path, "S4" or "S5", packet_id)` returns packet and receipt bytes.
The case selects a pinned source and allowlist, not the report's conclusion.
`report(packet_bytes, receipt_bytes)` returns separate requester, authority,
action and evidence assertions plus every input locator and rule.
`render_html(report_dict)` returns escaped self-contained HTML, with no scripts.
None writes an output file. There is no command-line auto-run or import-time I/O.

The producer's serializer is merely a production convention. Intake hashes the
actual supplied bytes; a whitespace change invalidates the old receipt.
The trusted source constants are pinned independently of supplied inputs.
A matching receipt is not a digital signature; a replacement pair could pass.
`seal_local` is expressly a trusted custodian helper, not an imported-packet
verification service. It asserts that its caller has already checked originals.

## Future checks requiring separate approval

Proposed command from this directory, after review (NOT RUN):

```sh
CASE_REPORT_ARCHIVE=/path/to/preserved/withdrawal_interface_study_v01_20261103.zip \
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_case_report
```

This would read the immutable ZIP, create derived artifacts in RAM and produce
console output. It does not run historical workflows. No dependency installation,
network, VM, socket or live model is required. Neither command nor checks have
been run. Preserve exact command/output and input/runtime identities if approved.

## Important remaining limitations

- Only two pinned source members and their declared local scope are supported.
  No arbitrary event schema, distributed history or external provenance system.
- The report does not reread originals; the receipt's extraction claim relies on
  local custody. An independent reviewer should compare generated packet values
  against originals before accepting outputs from a future run.
- Unknown schema fields/versions fail closed; the concrete JSON shape is an
  implementation proposal requiring source review against the prose contract.
- Full finite adversarial coverage is not claimed. A8a wrong-original-bytes
  extraction test still needs an approved fixture strategy: changing the archive
  trips the archive digest before the member digest. Do not falsely label a
  report-input mutation as an original extraction-boundary test.
- Conflict handling explicitly covers same-root/epoch/boundary authority snapshots.
  General contradictions across event kinds, duplicate sequence streams and
  malformed records need review; malformed/duplicate streams disable all joins.
- Historical evidence preserves scripted framework output, not live model judgment.
- Browser rendering, code import, syntax, runtime, tests and report outputs remain
  unverified. No generated report is represented as available yet.

R2 adds local effect-identity deduplication and a proposed regression. Duplicate
copies remain inspectable but cannot increase the distinct matched-effect lower
bound. This is not general semantic duplicate detection. No check was executed.
