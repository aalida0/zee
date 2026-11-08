# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## Mandatory source-first literature gate (new: 7 Nov 2026)

Before claiming any Zee-specific loop calculation, scalar/vacuum constraint,
flavor uncertainty, or numerical implementation is absent from the literature,
**read** `research/full_constraints/LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md`
and the actual paper full text, then check relevant **references AND citing works**.
Document DOI/arXiv, exact equation, physical particle content, Yukawa
restrictions, source/code version, and a tested limiting case. A previous
false absence claim overlooked Florentino–Romão–Silva 2021 App. D.3 Eq(D.20)
for mixed charged-scalar h→Zγ, Hue 2018 unequal-mass PV formulas,
Bilenky–Santamaria 1994 singlet EFT, and old Zee LFV box/Z-penguin formulas.
Do **not** call an unimplemented published expression nonexistent; do not call
a restricted formula complete general Zee physics. Citation-search indexing is
not exhaustive; report limitations. Always preserve original frozen modules.

## CURRENT TASK — Practical physical-constraint closure on saved Zee cards (8 Nov 2026)

**Authorized science task:** `research/full_constraints/PHYSICAL_CONSTRAINT_CLOSURE_EXECUTION_TASK_2026-11-08.md`. Execute source-checked repairs and bounded independent validation of missing LFV amplitudes/materiality, B→Xsγ one-state control/theory uncertainty, applicable Higgs predictions and an integrated conservative benchmark-acceptance table. This supersedes the **completed** Candidate A vacuum task, which ended `NO_GO_CURRENT_DIRECTION`; retain the valid D10 exact sufficient tree certificates rather than rerunning the 93-point vacuum materiality exercise. The prior fixed-card flavor–cascade novelty pilot also returned NO-GO and must not be repeated.

**User authorization and permissions:** Codex may write **only** `research/full_constraints/physical_closure_2026/` and the new report `research/full_constraints/PHYSICAL_CONSTRAINT_CLOSURE_REPORT_2026-11-08.md`. It may run bounded Python/math code and download verified public papers, official public-code releases and datasets into ignored `work/physical_closure_2026/` using a workspace-write Codex sandbox and outbound **network allowlist**. It must NOT use full-access or `--yolo`, alter system packages, inspect secret credentials or write outside the repository, modify frozen SARAH or Modules 0–14, submit Condor/MG5 jobs, create a broad new scan or run detector simulation. **Do not ask for direct Git metadata write access**: a separate user-launched narrow Git wrapper commits/pushes only allowlisted research outputs.

**Status policy:** A partial but validated result is not a full physical exclusion. Missing LFV gauge/mixed-F, non-calibrated B NP theory uncertainty or incomplete Higgs signal tables stay `UNKNOWN`. A validated single hard failure can reject a point, but `GLOBAL_PASS` requires every applicable mandatory constraint independently covered. `global_acceptance=null` for any unresolved card. Never convert all unproven vacua into exclusions; saved D10 positive certificates apply to their exact pinned tree potentials.

**Completion:** source-hashed fixed-card joined data, bounded real attempts to close the three blockers, independent controls, actual executable acceptance gate, tested results and report, with a truthful `GLOBAL_BENCHMARKS_VERIFIED` / `NO_VALIDATED_BENCHMARKS_YET` / `ALL_SAVED_CARDS_VALIDATED_FAIL` status. The safe launcher is `research/full_constraints/physical_closure_2026/run_codex_closure.sh`; it handles scoped Git commits/pushes and stops on failures, rather than consuming rounds for Git/network issues.

## Mandatory physics safeguards

- "Complete" means all materially relevant contributions at the
  **explicitly declared perturbative order** with justified numerical
  and theoretical uncertainties, correct interference and physical
  confidence interpretation. Not literally all perturbative orders.
- Two mixed Zee charged states are NOT separately subject to the
  single Type-II 670 GeV bound. Use coherent Wilson coefficients.
- The corrected general 2HDM two-loop LFV backend is NOT complete Zee;
  the neutral fermion/photon subset is already in Module4 and must
  not be double-counted.
- SARAH/SPheno **full-loop observables are unavailable** (unphysical
  ~10^6 GeV WW loop widths and eV neutrino input-scheme mismatches).
  Compiling the backend did not validate its physics.
- HiggsTools requires source-bound rates for every applicable
  channel and collision energy; missing predictions are NOT zeros.
- A validated single failing observable can yield PHYSICAL_FAIL.
  `global_acceptance=PASS` requires all mandatory observables
  independently covered. Any uncomputed mandatory observable -> UNKNOWN.
- Original Modules0–13, D14 scanners/reports, 20k/225 collections,
  16-point MG5 map, all frozen source/receipts and separate B research
  branch are **read-only**. Work in `research/full_constraints/` and
  isolated optional adapters, retaining complete provenance and tests.
- No new parameter-space proposals (even a pilot), no exploratory
  scans, no Condor submission, no production campaign, no unauthorized
  merge into the frozen final-scan branch. Existing saved cards and
  analytic model-limit controls may be evaluated for validation only.
- Timebox/source-gate every area. A blocked full-physics result must
  remain UNKNOWN, not become a soft/conditional claim mislabeled 95% CL.
- Use English for all Codex sessions, notes, code review and commits.

## Current deliverable

Execute the complete `PHYSICAL_CONSTRAINT_CLOSURE_EXECUTION_TASK_2026-11-08.md` on existing validated cards; record physical uncertainty and missing amplitudes honestly; deliver a tested joined-card gate and final scientific blocker report. Do not re-run past completed novelty or global vacuum investigations.
