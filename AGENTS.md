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

## CURRENT TASK — practical Zee LFV with justified published approximations

**User approved continued LFV technical research** using published
leading-contribution approximations; **not** a new point/parameter
scan and not a wholesale paper-scope or collider-analysis authorization.

READ `research/full_constraints/LFV_PRACTICAL_APPROXIMATION_TASK.md`
**first** and `LFV_PUBLIC_CODE_REUSE_AUDIT_2026-11-07.md`,
`LFV_COVERAGE.md`, `LFV_SOURCE_TO_CODE_REPORT.md`, and
the original source-lock JSONs. Follow the staged stop rules.

**Immediate bounded target:** Repair newer FeynArts (>=3.10) /
FormCalc (>=9.8) setup for pinned FlexibleSUSY `913bbbf`
in an ISOLATED user/scratch directory. The previous attempt
detected SARAH but stopped before Zee generation due to old/missing
dependencies; it did not disprove Zee compatibility. Compare
its generated radiative/3-body/conversion Wilson coefficients
with the existing saved SARAH/FlavorKit source on **original
D7/F13 NO/IO cards** only. Save individual complex operators,
diagram topology inventory, source hashes and failed checks.

Then use source-verified existing one-loop Zee/selected
Barr–Zee contributions; check missing gauge/charged groups
and the **post-2026-erratum general-2HDM code** only for
non-duplicated transferable terms. Compute `μ→eγ`,
`τ→eγ`, `τ→μγ`, `μ→3e` with explicit coherent
interference and **materiality bounds** for omitted terms.
Conversion via flavio/wilson/MuonBridge is optional
follow-up only if complete correct EFT vector obtained;
original FlavorKit conversion has scalar proton/neutron
interchange, so don't use unpatched results. A green
compiler, a partial amplitude, or numerical stability is
NOT a physical exclusion. Use documented phenomenological
approximation if it cannot change observable's decision;
otherwise keep `UNKNOWN`.

Do NOT recalculate validated Module3/4 dipoles, photon
Barr–Zee, F-only 3-body box or Higgs widths. No full two-loop
program without separate user decision. Keep full-LFV
status BLOCKED until physically covered; B flavor
uncertainty, Higgs full signals and vacuum global remain
UNKNOWN. Final `global_acceptance=null`.

Branch `research/zee-full-constraints` only.
Modules0–13, frozen D14 data/scanners and
`feature/zee-d14-conditional-cascade-scan` at `133a340`
remain read-only. No new scalar point (pilot or final),
parameter scan, Condor, large MG5 or submission.
Record actual numerical inputs/sources, tests and caveats;
commit/push to research branch in English.

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

`research/full_constraints/LFV_PRACTICAL_IMPLEMENTATION_REPORT.md`
with actual version-pinned software results and four-card
per-observable Wilson/rate/omission evidence, or a precise,
bounded code/model compatibility blocker. Follow the
`LFV_PRACTICAL_APPROXIMATION_TASK.md` stop rules; no global
LFV PASS, B/Higgs relabel, or scan authorization.
