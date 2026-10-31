# Current v0.2 runnable qualification

Read PROTOCOL.md first. This compact tree preserves reviewed code bytes and import layout. SCENARIOS.json declares 18 case-arm fixtures; qualification_summary.json is the historical final summary. review_counterexamples01.json supports the 19 current tests. legacy_v01/ contains the separate 18-test regression suite.

From this directory, with installed Python and no added packages:

```sh
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v
PYTHONDONTWRITEBYTECODE=1 python test_qualification.py
(cd legacy_v01 && PYTHONDONTWRITEBYTECODE=1 python -m unittest -v)
PYTHONDONTWRITEBYTECODE=1 python harness.py --output ../../../revocation-fresh-run
```

Choose a fresh nonexisting output directory for every run. All evidence is written outside the repository by this example. See the root README for interpretation and limits; QUALIFIED includes successful detection of deliberately seeded admission-only violations, not a universal safety finding.
