# Experimental Temporal qualification candidate

**Mock-tested development code only. Not integrated into native collection, not production-ready, not a measured study.**

## Guided safeguard review

[Open the visual safeguard review and qualification plan](05_safeguard_review_and_qualification_plan.ipynb). This static Jupyter chapter distinguishes proposed controls, observed cloud metadata, the ten-scenario plan and the still-closed execution gate. No real-process or Temporal run is claimed. [Inspection record](safeguards/RUNTIME_INSPECTION.md).

## What this adds

- Process-supervised single-use child exchange with preserved uncertain outcomes and no retry after timeout/partial send.
- A coordinator-local claim on the endpoint object that prevents a fresh session from reusing that same object.
- A prospective four-domain observation-handoff check: native history, worker instrumentation, bridge and sink. It requires matching attempt/cut identity, producer sequence, explicit freeze acknowledgment, completeness and unchanged artifact hashes before sealing.

`handoff_complete` means these declared inputs passed the handoff checks. It does **not** establish an atomic distributed snapshot, completeness/truth of exporter content, absence of an effect, or a qualified treatment result. All acknowledgments are trusted inputs. No exporter is wired to the gate.

## Safe local tests

From this directory:

```sh
python -m unittest -v
```

The suite uses fake channels/processes/clocks and temporary files. It does not launch a child process or open a socket. Never substitute native contexts into the tests as though that were already authorized qualification.

## Boundaries

Claims are limited to one interpreter and the same weak-referenceable endpoint object. Aliased/duplicated OS descriptors, reconstructed objects, other processes, module reloads and hostile callers are not confined. Endpoint access remains private coordinator responsibility. Existing object claims are not reset for retries. Invalid preflight also consumes the endpoint conservatively.

Deadline-bounded join does not bound blocking process startup, filesystem or kernel calls. An outer watchdog and actual process/pipe qualification are still needed. `reply_observed` is not a case verdict, especially when record_complete or cleanup_complete is false.

Observation state transitions use a local reentrant lock and final cleanup rechecks. Actual producer/cleanup actions must still obey this coordinator; no runtime barrier or distributed synchronization is implemented. Producer sequences are producer-local labels, not cross-system clock comparisons. Hashes detect changed bytes at recheck, not true or complete evidence. Source files must be frozen by actual producers in future integration. A sealed manifest needs subsequent digest verification when read later.

Do not integrate this code into native collection until channel/descriptor ownership, bounded controller cleanup, runtime cutoff acknowledgments, schema authority, exact native terminal mapping and trusted-sink treatment expectations have been qualified. Measured collection requires a distinct decision.

## Provenance and preservation

Built through staged 11 November 2026 AI-assisted engineering/review increments following the [partial qualification decision](../../docs/decisions/2026-11-04-temporal-partial-qualification.md). Original frozen archives and historical study data remain unchanged. No denied EPERM operation was retried. See STATUS.md, REVIEW.md, tests.log and SHA256SUMS. AI assistance produced implementation/tests/review; this is not independent human validation.

