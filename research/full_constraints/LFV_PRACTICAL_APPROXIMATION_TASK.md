# LFV practical-source implementation: four existing Zee witnesses, justified approximations

**Date:** 2026-11-07. **Starting branch:** `research/zee-full-constraints`, HEAD `041751f57af6145be8585e0873b7b25253dc429a`.
**User decision:** Continue the Zee Type-II charged-Higgs cascade phenomenology project using **published, explicitly justified leading-contribution approximations**, not attempting to calculate every two-loop diagram.
**This authorizes only the bounded fixed-card LFV technical task described here. NO new parameter points, pilot/full scan, Condor or collider simulation.**

## Read first / model freeze

Read in order:
1. `AGENTS.md` and `LFV_PUBLIC_CODE_REUSE_AUDIT_2026-11-07.md`.
2. `LFV_COVERAGE.md`, `LFV_SOURCE_TO_CODE_REPORT.md`, `lfv/LFV_OPERATOR_MATRIX.json`, `lfv/LFV_FIXED_CARD_RESULTS.json`, `lfv/experiments.json`, `lfv/sources.json`.
3. `LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md`; actual full texts for the components used; 2017 full-Zee scan and 2023 Zee leading-LFV work.
4. Frozen native `models/SARAH/ZeeTypeII/ZeeTypeII.m` and original existing **D7/F13 × NO/IO** physical tree/Yukawa cards. Their hash and operator conventions must be tracked. Do NOT take loop-generated SPheno poles or full-spectrum widths at face value.

The native frozen dipole definition is
`L_D=(e*m_i/2) bar(l_j) σμν (C_L P_L+C_R P_R) l_i Fμν + h.c.`.
`F=2 f_Chen`. Both H1/H2 must participate with their signed doublet/singlet mixing; general complex D/F, Type-II quark Yukawas. Never apply one physical Type-II 670 GeV mass bound independently to two eigenstates.

## Scope: simple phenomenology-grade LFV, not universal two-loop closure

Primary target on **four existing cards only**: `μ→eγ`, `τ→eγ`, `τ→μγ`, `μ→3e`. Include `μ−e` conversion in Al/Ti/Au as a **separate bounded stage** if operator matching actually qualifies. Record other tau 3-body channels as optional unless they can be reused with near-zero additional work.

- Use **existing source-matched one-loop Zee dipoles** as starting point, including h/H/A and mixed H1/H2. Do NOT recalculate validated Module3/4 photon subsets.
- Use **published leading Barr–Zee 2-loop neutral/photon and charged/photon contributions** already validated in Module4. Inspect the 2025 general-2HDM complete two-loop code **and its 2026 erratum**; map only missing **nonoverlapping** terms with explicit sign, phase, mass and charged mixing convention.
- Approximation is acceptable if each omitted **potentially leading** amplitude has (a) an external/published quantitative suppression argument valid for our Type-II Zee cards, (b) a verified analytic parametric bound with actual saved couplings/masses, or (c) a fixed-card independent benchmark/test showing omission cannot change a stated exclusion decision over the declared uncertainty. **Never invent 1%/10% bounds.** Relative numerical importance of *calculated subsets alone* cannot bound unknown contributions, and a near-cancellation needs more care.
- Specify clearly: LO 1-loop LFV + selected leading two-loop dipoles, tree+one-loop `μ→3e` operators, which gauge/Goldstone/ghost sectors are omitted and why; no full fixed-order NNLO claim.
- Per-observable statuses `VALIDATED_SCOPED_RATE`, `UNVALIDATED_APPROXIMATION`, `UNKNOWN`, `EXCLUDED_BY_VALIDATED_SCOPE` only with robust and physically calibrated confidence. For an observable missing important terms, keep `physical_lfv=UNKNOWN`, `exclusion=null`. Conditional source-level plots are permissible if visibly labeled **NOT an allowed-region claim**.

## Phase A — minimal dependency repair and generated comparison (bounded!)

1. Keep all installs and outputs in a **new isolated user/scratch subtree** (no sudo, no git-tracking of downloaded software). Use existing Mathematica 15.0.1, SARAH 4.15.4 and pin FlexibleSUSY `913bbbf107d2b4aa2741dfbaa87c780853e39ca4`. Official FeynArts **>=3.10**, FormCalc **>=9.8**; verify actual latest available source version/hashes rather than assuming old archives qualify. Verify `Needs["SARAH\`"]`, `Needs["FeynArts\`"]`, `Needs["FormCalc\`"]` independently in the exact invoked kernel. Previous setup stopped *before Zee model generation* at missing FeynArts.
2. Attempt only **one** exact Zee model adapter/generator for `BrLToLGamma`, `BrLTo3L`, `LToLConversion`, using **existing physical saved spectra**; preserve per-coefficient outputs, per-diagram namespace/field lists and source hashes. If creating a valid generator requires unsupported full-loop spectrum physics, bypass that via controlled physical input or record the blocker; never feed false SPheno output. Do not spend unlimited time repairing the backend. On real architecture failure, stop and use published FlavorKit-generated coefficients plus rate cross-checks.
3. **Mandatory source coverage audit**: FlexibleSUSY `BrLTo3L/NPointFunctions.m` and `LToLConversion/NPointFunctions.m` explicitly remove some loop-vector topologies. Determine whether their output plus photon form factors covers the actually leading Zee structures; inventory W, Goldstone/ghost, charged and neutral sectors. Compare complete ordered scalar/vector/tensor, photon and box coefficients to SARAH-generated `CalculateTreeS4L`, `CalculatePeng*4L`, `CalculateBox4L` where possible. Preserve any disagreement; don't patch to force equality. Full LFV one-loop status is not a green code build.

## Phase B — source-backed approximate rates; priority to radiative decays

4. For `μ→eγ`, `τ→eγ`, `τ→μγ`, output complex `C_L,C_R` contribution ledger: 1-loop neutral, H1/H2 doublet and singlet, validated photon-Barr–Zee; remaining 2HDM gauge Z/W/kinetic, Zee F-sector W and mixed currents **explicitly blank or bounded**. Map external published formulae only after a fixed-card, one-state/zero-F, CP-phase and decoupling test. DO NOT double count Module4 neutral photon.
5. Compare completed/justifiably approximated radiative amplitudes to source-pinned experimental 90% CL bounds in `lfv/experiments.json`. For each fixed card produce conditional BR and a missing-amplitude materiality threshold: what coherent `ΔC_L,R` could change the limit decision? Use triangle/Cauchy bounds where available and show cancellations and appropriate experimental reference. A `BR` calculated from partial coefficients is a **diagnostic**, not a validated exclusion. If the card is far below the bound with no bound on missing gauge pieces, still `UNKNOWN`.
6. For `μ→3e`, prioritize tree h/H/A neutral exchange plus photon K1/K2 and signed **full** vector/scalar/tensor coefficients from FlavorKit. Use published Mitsuda–Sasaki F-only mixed box as a control (already independently matched), not a substitute for doublet/neutral boxes or gauge-penguin interference. Compare to FlexibleSUSY and independent rate engine (flavio `BR(mu->eee)`) with an explicit WET operator dictionary (chiral order, complex conjugation, signs, GeV^-2, scale, identical-lepton factors). Include zeroing-one-operator tests and real complex interference controls. No incoherent BR addition.
7. If time and coverage allow, conversion: retrieve WET scalar/vector/dipole coefficients and match through `flavio/wilson` and **MuonBridge/MuonConverter**. Historical FlavorKit `MuEconversion.f90` swaps scalar proton/neutron and breaks scalar–vector interference: **DO NOT consume original conversion rates**. Flavio GitHub issue #126 documents older normalization and neutron-isospin bugs repaired by #132, but current source still needs nonzero signed one-operator and mixed-interference benchmarks. Source-internal conversion output alone not independent. Explicit nuclear isotope/capture/overlap and matching scale.

## Phase C — decisive model-physics release or honest bounded stop

8. Deliver ***per-card*** `C_L,C_R`, partial contributions, selected `BR` with stated perturbative accuracy, the experimental input/CL and an explicit **omission/magnitude/sensitivity ledger**. If some channels can be safely used as hard vetoes (including a **validated above-bound** result robust under remaining coherent amplitudes), distinguish them from a complete LFV PASS. If no quantitative omission bound can be obtained, report honest `UNKNOWN` and propose the smallest specialist question (not new original two-loop derivations).
9. Produce `research/full_constraints/LFV_PRACTICAL_IMPLEMENTATION_REPORT.md` and source-bound JSON under `research/full_constraints/lfv/`, plus independently executable tests/logs where actual physics was run. Tabulate `what reused | what newly computed | independent check | approximation | error/materiality | physical status`. Record reproducible dependency source hashes and installation commands; do not commit externally downloaded package code.
10. Update `LFV_COVERAGE.md`/milestone **only if** a genuine independently validated observable qualifies. Preserve **all frozen Modules0–13 and D14**, the old feature branch at `133a340`, B/Higgs/vacuum statuses and `global_acceptance=null`. No generation/parameter scan/production.
11. **Stop rule:** maximum one isolated FlexibleSUSY dependency/model-adapter attempt and one fixed-card independent rate comparison cycle; if incomplete gauge pieces could change exclusions and cannot be bounded, record concrete values/unknown rather than escalating to a large tensor project. The deliverable is physics progress toward the simple neutrino+LFV-informed cascade paper, not another unbounded calculation chain.

**Success:** at least one scientifically justified Zee LFV observable for four existing cards, or a precise, bounded short-list of missing amplitude terms and practical public-code path. The final scan requires separate explicit authorization, and a scoped LFV PASS is not global flavor viability.
