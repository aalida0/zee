# Codex AGENTS — Conditional Zee charged-Higgs cascade scan

**Branch:** `feature/zee-d14-conditional-cascade-scan`.

## Current task (after 111b544 model-matched production result)

**Read and execute `module14/NEXT_PRODUCTION_MAP_TASK.md` first.**

The real 13 TeV production pilot for three conditional benchmark points
and the bounded sub-TeV vacuum searches are COMPLETE at commit
`111b544`. Do NOT repeat these tasks. The current bounded goal is
the **actual 13 TeV production map for the remaining 13 of 16 vacuum-PASS
and nominal-flavor-compatible scalar points**, plus an independent
**14 TeV production check for three existing benchmarks**. Preserve
original 13 TeV receipts; no mass/energy rescaling is an acceptable
substitute for actual generator runs.

Make a clearly documented data/plot bundle, not a new big scan or
an experimental sensitivity claim. Missing scale/PDF uncertainties,
physical B→Xsγ classification, partial LFV and HiggsTools coverage must
remain explicit. Do not change Modules 0–13 or original Module14
worker, underlying data, or acceptance logic.

The B→Xsγ authors were already emailed; no reply is available and
no further author outreach is needed. All Codex output, task titles,
documentation and commits should be in **English**.

## Prior task archive (completed)

The original `module14/NEXT_PRODUCTION_VACUUM_TASK.md` and
`module14/CONDITIONAL_SCAN_TASK.md` are retained for provenance,
not active instructions.

## Historical conditional-scan task (completed)



Read `module14/CONDITIONAL_SCAN_TASK.md` fully and execute its phases
in order. This supersedes the historic D14A development task from the
base branch, which was completed in the original D14 pilot. Read existing
`module14/D14A_INTEGRATED_SCAN_AUDIT.md` and `AF_RUNBOOK.md` before
touching production workflows.

The user has already contacted the 2026 B→Xsγ authors and received
**no reply**; do not instruct the user to send the same request again,
repeat the same uncertainty literature search, or restart a flavor
backend calculation.

## Mandatory scientific safeguards

- Reuse the validated ordinary LO two-state matching and the **published
  2026 linear Eq.(4)** strictly as a **conditional diagnostic**.
- A nominal Gaussian or method-stability test is not a full
  new-physics theory uncertainty or official 95% CL exclusion.
  Report unresolved B→Xsγ physical classification as `UNKNOWN`.
- `D10` sufficient vacuum certificate failures, partial LFV, incomplete
  HiggsTools channels, and missing production must retain their actual
  `UNKNOWN/NOT_EVALUATED` statuses. Do not declare globally allowed
  points.
- Keep the `H2→H1 Z` cascade open and remember its off-diagonal
  coupling vanishes at gamma=0 and ±pi/2. Rank candidates with
  validated complete decay BR and documented production, not
  just a partial width.
- Keep Modules 0–13, original Module14 pipeline/evidence,
  source hashes, legacy bsgamma studies, and the separate research
  branch untouched. Add a clearly separated optional sidecar.
- First verify whether existing UChicago AF 20k and 225-point
  follow-up results are actually accessible/complete. Ubuntu has no
  automatic access to AF `/data`; do not claim the runs were collected
  without reading remote outputs/receipts.
- Do not run large scans, run HTCondor or commit binaries/logs on behalf
  of the user. Prepare runbook commands and a small local pilot.
- Use English exclusively for Codex text, titles, progress,
  documentation and commit messages unless explicitly requested otherwise.

## Work and reporting

Keep new code in `module14/conditional_scan/`, tests in
`tests/test_module14_conditional_*.py`, and a scan-readiness report
in `module14/CONDITIONAL_SCAN_READINESS.md`. Run targeted tests and
`git diff --check`, then commit/push only validated changes to this branch.

A valid outcome can be a conditional scan **ready to run**, not a final
fully constrained physics result. Stop and document blockers instead of
fabricating acceptance, uncertainty or remote scan data.
