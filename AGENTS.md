# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## CURRENT TASK — 2021 published Zee Zgamma expression, not a new loop program

**READ FIRST**:
`research/full_constraints/HIGGS_ZGAMMA_2021_RESCUE_TASK.md`.
Previous completed stage: `f30131a` executes D7/F13 HDECAY
and independently validates H/A→γγ (35 tests).
The ATLAS `tau tau` ID `200212223` observed search is still blocked
by incomplete widths and acceptance/uncertainty; no physical BR,
observed ratio or global pass.

**CRITICAL NEW SOURCE**: Florentino, Romão & Silva,
*EPJC 81 (2021) 1148*, Appendix D.3 Eq.(D.20) ALREADY derives
`phi→Zγ` with off-diagonal `Z H1^+ H2^-` and unequal-mass
charged-scalar loops using B0/C0. Appendices D.1–D.4 contain
fermion/W formulas and widths. This is our *own 2021 Zee/cascade
model reference*. Do NOT call mixed-state Zgamma absent in public
literature or start an unbounded custom one-loop derivation.
Translate published conventions to native SARAH, audit potential
printed equation typos and independently validate source formulas
and scalar/gauge/fermion contributions on **original D7/F13 only**.

After validating the one-loop Zγ partial widths, quantify whether
other missing A→VV, finite-width charged-W tails and uncertainties
materially affect `BR(H/A→tau tau)`. A controlled upper-bound
comparison `Γ_total ≥ ΣΓ_known` may be reported *only with exact
nonnegative-channel and production/acceptance qualifications*.
Do not normalize an incomplete width sum or fabricate physical
HiggsBounds exclusion. Account for D7 H/A near degeneracy and
the two-production-mode ATLAS likelihood.

B `B_FULL_RATE_BLOCKED` after pinned HEPfit NLO,
69 nuisance runs and a precise specialist request; STOP solo
flavor-rate reimplementation until specialist input.
LFV `LFV_FULL_COVERAGE_BLOCKED` pending substantive gauge
operator work. Original Modules0–13, final D14 production/scan and
`feature/zee-d14-conditional-cascade-scan` at `133a340`
remain frozen.

No new Zee parameter points, pilot/full scans, Condor submissions,
broad MG5 generation, SPheno full-loop substitutions, missing→zero
or global-pass claims. Work only on original fixed D7/F13 cards,
on branch `research/zee-full-constraints`, commit/push source-
validated results; all docs/commits in English.

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
