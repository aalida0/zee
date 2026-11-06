# Codex AGENTS — final Zee workflow code completion

**Branch:** `feature/zee-d14-conditional-cascade-scan`.

## CURRENT TASK — FINAL SCIENTIFIC FREEZE; NO SCANS

Read **`module14/FINAL_PHYSICS_FREEZE_TASK.md`** first. The
public-tool physics-adapter work is COMPLETE at commit `5865e8d`
within its scoped evidence. The pipeline is technically ready,
including the source-locked streaming exporter, but full-loop
SPheno 4.0.5 results are **NOT operative** (unphysical 5.5 eV
neutrino masses, 300+ GeV h125 and 10^6 GeV total widths on saved
cards).

Current **bounded** tasks:
- Forensically inspect saved full-loop SPheno source/SLHA output,
  identify exact anomalous width channel(s), mass/mixing and
  radiative-neutrino order/scheme mismatch.
- At most one demonstrated model-correct fix, at most two native
  reruns of **existing** cards, or stop and retain full-loop
  `UNAVAILABLE`. No parameter tuning.
- Freeze exact verified hard cuts vs partial/conditional
  diagnostics; ensure no config can promote an unvalidated
  SPheno, B→Xsγ, LFV, Higgs or vacuum result to a hard veto.
- Verify old 225-point export and all focused tests remain
  intact; publish `FINAL_PHYSICS_FREEZE.md`.

**No new parameter points, exploratory scans, 20k/100k tests,
Condor submissions, MG5, global vacuum solver construction,
two-loop matching, or new author outreach.** The user will
authorize one separate final big scan after the freeze, not now.
All answers, logs, docs and commit messages should be English.

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
