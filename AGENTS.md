# Codex AGENTS — final Zee workflow code completion

**Branch:** `feature/zee-d14-conditional-cascade-scan`.

## CURRENT USER-APPROVED TASK — FINAL PHYSICS-ADAPTER INTEGRATION

Read **`module14/FINAL_PHYSICS_ADAPTER_TASK.md`** first. It supersedes
the earlier `WORKFLOW_COMPLETION_TASK.md`, whose engineering code gate
is COMPLETE at commit `bff3e52`. The user approved **bounded
physics-adapter work with public code** before the one final scan.

Priorities in order:
1. Fix the actual SARAH 4.15.4 / SPheno 4.0.5 Zee full-loop-decay
   build issue with `ZRUNoMatrix/ZRUNoMatrixc` (model-correct fix,
   not dummy declarations); validate on original saved D12 cards.
2. Investigate the corrected 2026 general-2HDM two-loop LFV source
   as an independently verified **subset** only; gauge and
   charged-singlet completeness decide whether any rate is usable.
3. Audit SARAH→Vevacious++ or certified polynomial backends for the
   **full Zee scalar potential**, testing only saved D10 PASS/UNKNOWN
   points; missed numerical minima remain UNKNOWN.
4. Enhance HiggsTools only with real validated h125/charged-loop
   sources and complete same-point hashes, not a generic 2HDM guess.
5. Eliminate final exporter's all-rows-in-RAM scaling without
   changing physics, using frozen original data and synthetic rows.

**Absolutely no new parameter-space points, small/big scans, Condor
submissions, or MG5 production.** Existing previously saved benchmark
cards may be evaluated by pinned external packages as *validation
comparisons only*. Use limited attempts, source hashes and strict
failure/UNKNOWN propagation. If public software cannot supply full
Zee coverage, document the actual blocker and move on; do not invent
physics or spend unbounded effort.

No final scan will run without the user's separate explicit approval.
All new work is on this branch, with original Modules0–13 and
historical production/results held read-only. Use English exclusively.

## PREVIOUS TASK — WORKFLOW CODE COMPLETED (ARCHIVED)


Read **`module14/WORKFLOW_COMPLETION_TASK.md`** first and execute it.
This supersedes **all previous paper/scan/production task plans**.
The existing 20k/225 collected scan, 16-point real 13 TeV map, and
three 14 TeV checks are completed historical evidence, NOT work to rerun.

**Prohibition:** do not launch or prepare an actual new proposal scan,
including "small pilot", "another 20k", "100k", or "final big scan" itself.
Do not generate any new physics points as a workflow test.
Tests are unit tests, mock fixtures and replay of existing immutable
records only. Do not submit HTCondor, execute MG5, redo physics
calculations or ask authors for information.

**Only after all workflow code is finished, tested and frozen** will the
user authorize one final big scan in a separate step. Do not silently
choose the count/seed/arms for them.

## Public-code reuse BEFORE new physics work

Read `module14/PUBLIC_CODE_REUSE_AUDIT.md` when auditing external
capabilities. Source-qualified priority: corrected 2026
general-2HDM two-loop radiative-LFV Python code, SARAH/FlavorKit/SPheno,
Vevacious++ and HomotopyContinuation.jl, existing HiggsTools.
**None is proven automatically complete in Zee Type-II.** Adapt only
independently verified diagram/operator subsets and preserve
`UNKNOWN` for uncovered contributions. Do not rebuild completed
matching/RG or claim new theory uncertainties from legacy-code
differences. Do not download, execute, or vendor unpinned third-party
binaries as part of a broad scan. First build a bounded compatibility
audit and use frozen points/fixtures, not new proposals.

## Physics integrity

- The published Misiak 2026 Eq.(4) flavor result is an **approximate,
  conditional LO-NP diagnostic**, not a validated Zee B→Xsγ 95% CL
  exclusion. Do not transfer the 2HDM-II one-Higgs 670 GeV bound to
  individual mixed states.
- Vacuum sufficient certificate misses remain UNKNOWN, partial LFV
  remains PARTIAL/DIAGNOSTIC_ONLY; incomplete HiggsTools channels
  remain NOT_EVALUATED/DIAGNOSTIC_ONLY. No claim of globally allowed
  Zee points.
- Source-validated production is an **optional per-point input/sidecar**;
  absence means null, not 0. Decay BRs use full original on-shell
  tree two-body inventory. Energy/PDF/scale/process mismatches fail closed.
- Preserve Modules0–13, historical scans/probes/receipts,
  original results and the independent flavor branch. New workflow
  code may change Module14 and its conditional/Condor components
  only with explicit backward-compatibility tests.
- Use English exclusively for Codex session titles, progress, logs,
  documentation and Git commit messages unless otherwise requested.

## Required completion outcome

Deliver `module14/{WORKFLOW_GAP_AUDIT.md,FINAL_WORKFLOW_RUNBOOK.md,
FINAL_WORKFLOW_READINESS.md,final_config_template.json}`, the
necessary **implemented and tested** orchestration components,
and source-locked deterministic replay/robustness tests.
Do not mark `CODE_READY` if the end-to-end fixture replay, failure
handling, reproducible export and preflight aren't working.
Scientific limitations must be separately and explicitly recorded.

Commit and push only code/documentation that passes tests.
**Do not run the user's final large scan.**

## Historical documents

The old `module14/PAPER_CONDITIONAL_ANALYSIS_TASK.md`,
`NEXT_PRODUCTION_MAP_TASK.md`, `NEXT_PRODUCTION_VACUUM_TASK.md` and
`CONDITIONAL_SCAN_TASK.md` are retained for provenance only and are
NOT active instructions.
