# First executable task — B→Xsγ source-feasibility and validated-rate bridge

**Branch:** `research/zee-full-constraints`.
**Protected frozen baseline:** commit `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.
**Gate:** Do not claim physical B exclusions until the full rate and uncertainty are source justified. No new scan or Condor work.

## Start with actual backend code, not re-derivation

1. Read: `research/full_constraints/PLAN.md`, `module14/FINAL_PHYSICS_FREEZE.md`, `module5/BSGAMMA_2026_ACCURACY.md`, `module5/BSGAMMA_SCAN_TRIAGE.md`, `module14/conditional_scan/flavor.py`, `module14/external.py`, `scripts/zee_module5_bmu_nlo.py`, `validation/module5/d9b_superiso_repair.json`. Optionally read the separate `research/zee-bsgamma-rate-validation` result **read-only** for EOS/SuperIso response and 72-point diagnostic status.
2. Inspect official **SuperIso 5.0** (released 23 Nov 2025) *actual* `predict.c`, `scan_coeffs.c`, and `bsgamma` calculation and model-specific 2HDM Wilson handling. Determine EXACT input possibilities: ordinary high-scale `C4^(1),C7^(0,1),C8^(0,1)`, any primed coefficients, and two-state mixed NP structure; photon cut/CP average, theory-error APIs, SM normalization. Don't assume user-editable arbitrary coefficients or full quadratic response just from a program's name.
3. Inspect and compare **HEPfit bsgamma** and **flavio/wilson** exact external-NP interfaces, operator orders, evolved Wilson basis, perturbative implementation, mixed-source handling and theory nuisance treatment. Use one **primary** and at least one **independent check**, but no requirement to install every package.
4. Inspect arXiv:2608.29863 (main) and 2608.29864 (companion) for published LO-NP high-scale linear Eq.(4) and supporting publicly available complete nonlinear/NLO rate formula. The exact 2026 prediction has no source-verified NP-domain numerical remainder bound in previous audits. Don't claim a different older rate formula is the 2026 result.
5. Choose **one internally consistent perturbative prescription**, if available, that includes the SM+NP interference and quadratic contributions and has a defensible literature-backed theory uncertainty. If the 2026 exact prescription is not reconstructible, a documented older but *internally consistent* source-supported precision prediction can be investigated as a distinct scheme and clearly labelled, with its own experimental/SM prediction choices. It may only yield an exclusion if its own physics validation and uncertainty pass.

## Physics/model tests on existing points, not new proposals

Use only frozen original D12 and 225-scan scalar cards, and analytic 2HDM limiting cases:
- 0 NP reproduces backend SM prediction (with its stated inputs).
- H1/H2 doublet projection weights and signs; gamma endpoints and swapped-state relabelling; same-chiral combination, no hard 670-GeV cut on individual masses.
- Coherent Wilson amplitudes **before** computing the rate; equality to exact one-state Type-II matching at corresponding limit and to frozen Module5/C1 source.
- Full quadratic response checked against actual backend outputs at ±DeltaC7/8 probes, mixed cross terms and held-out physical spectra. Note source-specific phase/chirality contributions and NLO C4 inclusion if needed; never use a low-order polynomial fit as a standalone new theory prediction.
- Photon energy threshold 1.6 GeV and matching/low-scale/bottom-mass schemes; consistent uncertainties including correlations.
- Independent source/check vs SuperIso/EOS/HEPfit/flavio if different SM baselines. Decompose differences instead of arbitrarily offsetting intercepts.
- Test whether a source-consistent one-state Type-II mass bound from **the chosen backend** can be reproduced; do NOT assert the modern 670 GeV bound unless the 2026 full methodology has in fact been reconstructed.

## Results and bounded stop

Deliver `research/full_constraints/FEASIBILITY_GATE.md`, `BSGAMMA_COVERAGE.md`, version-pinned source manifest, any small benchmark/derivative controls and associated tests.
Only after passing source and numerical gates create an opt-in adapter with result fields:
- `BR_BXsgamma`, energy threshold, all NP Wilson coefficients and order, scale/scheme/PDF-like input, theory/prescription, experimental source and confidence threshold;
- `status=PHYSICAL_VALIDATED_PASS/FAIL` only where the strict complete rate gate passes;
- otherwise `status=UNKNOWN`, `exclusion=null`, `theory_sigma=null` if not source backed;
- source+card+runtime+prediction hashes and explicit omitted contributions.

**Do not begin unrelated LFV/Higgs calculations yet.**
Stop after actual public source-level audit plus a *finite* set of frozen-card checks. If no defensible full rate can be constructed, say
`B_FULL_RATE_BLOCKED` and give the exact missing piece rather than coding an arbitrary replacement or going back to two-loop derivations. Commit/push only this research branch.
