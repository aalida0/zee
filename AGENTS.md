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

## CURRENT TASK — independently validate published mixed Zee h/H/A→Zgamma

**Read first** `research/full_constraints/HIGGS_ZGAMMA_2021_RESCUE_TASK.md`
and `research/full_constraints/LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md`.
The current task is specifically to **execute and independently validate**
the CP-even *h* unequal-mass charged-loop sector using three prior
published sources in one exact SARAH physical convention:

1. Trương Tín Thành et al. (2019): pre-2021 Zee off-diagonal Z
   currents and Eq.(1.17) mixed scalar loop, **incomplete documented
   PV arguments**, so not a standalone validated amplitude.
2. Hue et al., EPJC 78 (2018) 885, Eq.(16), Appendix A:
   generic unequal-internal-mass CP-even PV function.
3. Florentino/Romão/Silva, EPJC 81 (2021) 1148,
   Appendix D.3 Eq.(D.20): exact Zee charged-scalar mixed form.

Start with original **D7/F13 h125**, independent SM/one-state/equal-mass/
mixing controls and stable PV/UV/EM Ward checks. Only then extend to
CP-even H using exact SARAH couplings and separate CP-odd A
structure. Reconcile source formula/width prefactors instead of
copying printed expressions uncritically. If validated, compute
original fixed-card widths and test **materiality** of remaining
tau-tau width corrections before any HiggsBounds physical claim.
No incorrect full BR from known disjoint partial-width sums.
If no full one-loop validation, report exact irreducible loop blocker
and stop. Existing SusHi, HDECAY, h/H/A gamma gamma results are
validated in scope and must not be recomputed.

**Previous LFV stage is DONE within its bounded scope at `77148f0`:**
Mitsuda–Sasaki F-only two-charged-state mu3e box matches native
generated source to 3.9e-16; Ghosal on-shell Z kernel checked, not
low-energy off-shell matching. Independent nuclear matching found a
real scalar proton/neutron exchange in pinned FlavorKit conversion
affecting scalar/vector interference. Never use that unpatched
source for a physical Zee conversion claim. FlexibleSUSY
NPointFunctions model generation was **NOT TESTED**: configuration
stopped because installed FeynArts/FormCalc were old and pin requires
FeynArts>=3.10, FormCalc>=9.8. This is a dependency block, NOT
a Zee model-physics incompatibility. Do not repeat the same setup
without a separate authorized focused prerequisites task.
LFV remains `LFV_FULL_COVERAGE_BLOCKED`; any missing two-loop
gauge contributions remain explicitly UNKNOWN.

B still `B_FULL_RATE_BLOCKED` pending Wilson-dependent
uncertainty specialist input. No HEPfit reimplementation.

No new scalar points, even pilot/large scans, Condor, broad
MadGraph integrations, false global acceptance or broken full-loop
SPheno spectrum use. Frozen Modules0–13 and
`feature/zee-d14-conditional-cascade-scan` at `133a340`
are read-only. Work in isolated research subtree on
`research/zee-full-constraints`; commit/push real source-verified
numerical results and no unsupported exclusions.

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

A source-verified B→Xsγ feasibility and full-rate path
(`FEASIBILITY_GATE.md`, `BSGAMMA_COVERAGE.md`), with executable
bounded controls only if scientifically supported. Commit and push
to this research branch. Retain unvalidated results explicitly
research-only and the original conditional pipeline unchanged.
