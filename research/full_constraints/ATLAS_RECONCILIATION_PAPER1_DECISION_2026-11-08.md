# Cross-repository literature-atlas reconciliation — Paper 1 decision

**8 November 2026. Evidence-only scientific decision; NO new physics run and NO scope/scan authorization.** Physics branch snapshot: `e53018e8e6f85e80555dd256551d7fb8869c7953`. Literature companion: [aalida0/zee-literature-atlas](https://github.com/aalida0/zee-literature-atlas), particularly:
- [cross-repository implementation ledger](https://github.com/aalida0/zee-literature-atlas/blob/main/reports/CROSS_REPO_ZEE_IMPLEMENTATION_RECONCILIATION_2026-11-08.md)
- [vacuum–cascade publication decision](https://github.com/aalida0/zee-literature-atlas/blob/main/reports/VACUUM_CASCADE_PAPER_DECISION_2026-11-08.md)

## What was already done (do NOT ask for another pilot)

The frozen `models/SARAH/ZeeTypeII` has genuine native SARAH charged vertices, tree cascade widths and complete on-shell two-body decay table (D3/D4), one-loop neutrino NO/IO Yukawa inverse and D12 family witnesses, coherent two-charged-state (B\to X_s\gamma) NLO matching and actually executed HEPfit studies, partial one/two-loop LFV and missing-amplitude materiality budgets, and a **genuine fixed-card flavor–cascade comparison**. D14 documents 16 saved 13-TeV and three 14-TeV 5FS LO associated-production integrations. D10 provides **sufficient exact full-field tree-global vacuum certificates** on D7, F13_1330 and an aligned control, with constructive negative controls. The full model's physical acceptance is still **UNKNOWN/null** while LFV, B uncertainty, Higgs likelihood and other hard gates remain incomplete.

The 7-Nov [`FLAVOR_CASCADE_NOVELTY_PILOT_REPORT.md`](FLAVOR_CASCADE_NOVELTY_PILOT_REPORT.md) already states **`NO_GO_CURRENT_PAPER1_CENTER`**: arbitrarily chosen flavor families can strongly change daughter BRs, while other texture families barely change the source-summed cascade BR; neither a forced correlation nor globally allowed flavor solution is established. Reproducing this pilot is NOT a next step.

## Prior art rechecked with model restrictions

- Barroso–Ferreira 2005, [hep-ph/0507128](https://arxiv.org/abs/hep-ph/0507128): Zee charge-breaking theory, stationary-depth comparison not sign definite with the cubic; not a universal all-field global certificate.
- Babu et al. 2020, [1907.09498](https://arxiv.org/abs/1907.09498), Sec. 4.3 Eqs. 4.24–4.25, Fig. 5: already study cubic-driven **charged mixing vs charge-breaking** using numerical minima in their Zee setup. Generic vacuum–mixing correlation is NOT NEW.
- Florentino–Romão–Silva 2021, [EPJC81(2021)1148](https://doi.org/10.1140/epjc/s10052-021-09956-2), Secs. 4, 6–8: same restricted Zee scalar potential, finite-start numerical charged-breaking searches, (H_2\to H_1 Z) widths, Type-II associated rates, and explicit motivation to connect neutrino/flavor sectors. This does NOT furnish a complete complex-field global certification for all their numerical benchmark points.
- 2017 [general Zee scan](https://arxiv.org/abs/1701.05345) and 2023 [LFV spectra](https://arxiv.org/abs/2303.13383) already treat radiative neutrino/LFV correlations under their assumptions; 2025 [mixed charged scalar Drell–Yan](https://arxiv.org/abs/2501.09796) includes Zee mixing but different production. No first-cascade/first-flavor-link/first-mixing-vacuum claim is defensible.
- These are **bounded source inspections**, not exhaustive 2024–2026 later-citation coverage.

## Current publication routes (release statuses)

| Route | Decision now | Why |
|---|---|---|
| Full globally constrained Zee Type-II `neutrino+LFV+cascade` scan | **BLOCKED** | Hard LFV/B/Higgs/other physical gates UNKNOWN. `global_acceptance` remains null. |
| Flavor–cascade correlation as Paper 1 centerpiece | **NO_GO_CURRENT_CENTER** | Actual fixed-card falsification/texture freedom, source prior art; already executed. |
| Restricted CP-conserving Zee **tree-level full-complex-field global vacuum** sufficient criterion, mapped to charged scalar mixing and cascade | **HOLD / NOT_YET_GO**, highest remaining conditional lead | D10 mathematical method stronger than finite-start 2021 numerical search; however method novelty, independent proof and systematic quantitative domain/observable effect are NOT yet established. |
| Collider exclusion/reach from saved LO rate maps | **NO_GO current** | No certified matched-background acceptance, 13/14 TeV likelihood or complete model acceptance. |

### Minimum bounded next scientific test (authorization still required)

Audit the D10 *existing* exact certificates independently (do not import computed LDL pivots); compare theorem and parameter domain with 2005/2020/2021, and test the source-locked necessary P2 bound from [`CANDIDATE_A_DECISIVE_REPORT.md`](CANDIDATE_A_DECISIVE_REPORT.md) against an actual stationary witness and a compact predeclared set of fixed scalar controls. The exact P2 fixed-trial-field necessary upper limit **1316.133373038139 GeV** is not a universal scalar mixing or width bound; local charged positivity extends to about 1531.297 GeV in that *one path*. A certificate failure is UNKNOWN, not exclusion.

Only if an **independently checked new analytical condition plus significant quantified physical/model-domain insight** survive the recent prior-art kill checks should Paper 1 be reconsidered as a narrow scalar-vacuum theory/phenomenology paper. Such a scoped paper would NOT need to claim full physical B/LFV/Higgs passes, but would need to label tree-level and theoretical assumptions explicitly. No new scan, sensitivity study, two-loop derivation or model change has been initiated by this note.

**Consistency rule:** repository results remain authoritative for what was actually executed; the literature atlas is authoritative for source papers and novelty gaps. This note does not modify the frozen numerical model or change any existing gate/decision receipt.


### Independent numerical arithmetic check recorded in literature atlas

A separate read-only reconstruction from committed `validation/module1/d10_vacuum_global.json` rebuilt the five floating `LDL^T` pivots of `C-epsilon J` without using D10's saved pivot arrays. The smallest D7 and F13_1330 pivots are **0.148668473145** and **0.104770108173**, and both doublet and singlet residual coefficients were positive. Details: [independent source-input spot-check](https://github.com/aalida0/zee-literature-atlas/blob/main/reports/INDEPENDENT_D10_VACUUM_NUMERICAL_SPOTCHECK_2026-11-08.md). This is **not** an independent exact-rational/Krawczyk proof or a new model certificate and does not change any frozen statuses.
