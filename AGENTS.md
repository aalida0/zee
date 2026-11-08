# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## CURRENT PRIORITY — integrated leading-LFV closure (8 Nov 2026)

**User-authorized large task:** `research/full_constraints/lfv_integrated_2026/EXECUTION_TASK.md`. One coordinated execution across validated `Zgamma`, independent `hZ`, material leading doublet/Zee-F gauge groups, leading `mu->3e`, `mu-e` conversion and integrated paper-usable constraints for **four existing D7/F13 NO/IO low-texture witnesses** only. **Do the calculations**, not a re-audit. The goal is a defensible *declared leading perturbative accuracy* for a non-detector-level charged-Higgs-cascade phenomenology paper, **not** formal all-two-loop completeness. Follow the task's subtask stop criteria: unresolved gauge-invariant groups remain UNKNOWN, and complete the other feasible operator sectors instead of spinning on new R-xi tensors.

**Already finished:** `research/full_constraints/lfv_transfer_2026/zgamma/CONTINUATION_RESULT.json` and `CONTINUATION_TESTS.json` are committed at `82b77db9be51eecd5374cede2f7edee301626393`. Neutral-fermion Zgamma complex source controls passed both chiralities, max residual 3.03e-14; tiny four-card partial-rate effects at order 1e-12–1e-14. The source/native **corrected** chirality map is `rho_l=D/sqrt(2)`, `c_L=D[e,mu]/sqrt(2)`, `c_R=conj(D[mu,e])/sqrt(2)`, `C_X=-c_X/(8*pi^2*v^2)`. Existing photon source match was completed before this and must never be repeated or counted twice. `hZ` in `HZ_EQ59_PRELIMINARY_NUMERICAL_2026-11-08.md` has **corrected chirality but remains preliminary** until an independent source comparison.

**Input:** `lfv_transfer_2026/CARD_PROVENANCE.json` and `BASELINE_REPLAY.json` already replay the correct D7 `texture_0.0001` and F13 `texture_0.001` cards and original Module4 complex coefficients. The historical `scale_0.001` witnesses are different Yukawa cards. Do not reconstruct provenance, repeat old nu-fit scans, or rerun the completed 66-card physical closure/candidate-A vacuum/B/Higgs tasks.

**Write scope:** ONLY new `research/full_constraints/lfv_integrated_2026/` results and adapters, with public source scratch downloads ONLY in ignored `work/lfv_integrated_2026/`. Source code in old modules and existing evidence is read-only. One big Codex invocation, no auto-continuation, no Git operations from within Codex. A separate user action stages, reviews and pushes results. No full-access, `--yolo`, sudo, secret inspection, new model points, detector simulation or Condor.

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

## Active execution and precedence

The *current* requested work is `research/full_constraints/lfv_integrated_2026/EXECUTION_TASK.md` and **supersedes** the completed `lfv_transfer_2026/TASK.md` / `run_once.sh` and previous `PHYSICAL_CONSTRAINT_CLOSURE_EXECUTION_TASK_2026-11-08.md`. Never call these old launchers for the new task. The complete source-first research inventory remains mandatory as a reference, but new citation browsing is strictly **targeted to genuinely missing source formulas**. The user explicitly prefers one coordinated substantial task over repeated ~50k-token pilots on negligible isolated terms.

The science verdict can be `PHENO_LEADING_LFV_VALIDATED`, a narrower `SCOPED_LFV_CONSTRAINT_READY`, or an honestly `LFV_LEADING_SCOPE_INCOMPLETE`/blocked result. `physical_lfv=UNKNOWN` and `global_acceptance=null` unless rigorous stated gates are actually met; a missing model amplitude is null, not zero. A loop-factor power-counting *estimate* is not a rigorous numerical upper bound. Use existing validated source conversions and original signed amplitudes, not new arbitrary mass benchmark points.

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

Execute the single integrated task `research/full_constraints/lfv_integrated_2026/EXECUTION_TASK.md` on four frozen low-texture D7/F13 witnesses and deliver working source-validated new amplitudes and leading LFV operator constraints, with paper-appropriate stated accuracy. Preserve all unrelated branches, scans, validation receipts, Zgamma results and global-physics UNKNOWN unless scientifically justified.
