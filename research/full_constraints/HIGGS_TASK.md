# Higgs exclusion completion: full model predictions for applicable HiggsTools analyses

**Execute after reading `PLAN.md` and the B→Xsγ feasibility result.**
Use the pinned HiggsTools 1.1.3 source and frozen datasets; no scans.

## Objective

For declared experimental scope, provide complete, physically accurate predictions for every **applicable** HiggsBounds/HiggsSignals search/measurement at the stated perturbative accuracy, or mark the exact analysis `NOT_EVALUATED`. A point is allowed under the full claimed Higgs dataset only when no mandatory applicable search lacks needed predictions.

## Existing source

`module13/higgstools.py`, `module14/external.py`,
`module14/decays.py`, `module7/d4_decay_table.py`,
`module8/D5_PRODUCTION_AUDIT.md`, `module14/conditional_scan/PRODUCTION_MAP_REPORT.md`,
`module14/PHYSICS_ADAPTER_READINESS.md`, pinned HiggsTools and its HB/HS dataset metadata.

## Steps

1. **Inventory all loaded searches:** enumerate HiggsBounds limit IDs, energy, production mode, decay topology, mass and width domain, validity, observed/expected use and necessary BSM rates. Classify each as applicable, *proven* not applicable, missing rate/width, or validated. Importing an analysis database is not enough to claim its predictions are complete.
2. **h125**: model-consistent scalar mass, all necessary BRs and total width, gauge and Yukawa effective couplings, LFV Higgs modes and both H1/H2 charged-loop contributions to `h→γγ` and `h→Zγ` where materially needed. Source-check Feynman rules, one-loop normalization and SM/decoupling benchmark; do not use unphysical SPheno full-loop mass/width outputs. Validate correct HiggsSignals kappa/BR conventions and correlated fit data.
3. **heavy neutral H/A**: source-validated gg/bb/associated production at each needed experiment energy with PDF/order and uncertainty, full relevant fermion/vector/scalar and charged-scalar W decay tables including competition, total width and resonance applicability. If a required three-body/off-shell channel is relevant, calculate with a validated backend or mark incomplete.
4. **charged H1/H2**: production in each applicable HB process at original analysis collision energy; 13-TeV `pp→tbH2` is validated for only 16 old cards, not generally. Additional `tbH1`, pair, associated and other processes must be calculated only where needed and physically nonzero; do not set missing to zero. Preserve signed model coupling and charge-sum conventions. Full D4 tree 2-body decay inventory, additional loop/3-body if needed and justified accuracy.
5. Build source- and exact-card-bound input, produce `HiggsBounds` per-analysis result and `HiggsSignals` fit statistics. Validate against published 2HDM/SM limits (as appropriate limiting cases), one or more independent source calculations and original D12/D14 cards.
6. Audit theory uncertainties and production/decay correlation. Never relabel 13.6/14 rates as LHC13, extrapolate mass grids, or substitute a universal K factor. Recognize that some dedicated cascade searches may be outside available HiggsBounds datasets; scope those as `MISSING_EXPERIMENTAL_COVERAGE`, not a computed exclusion.
7. Integrate opt-in hard Higgs veto only when every claimed mandatory applicable channel is source verified; otherwise `HIGGS_PARTIAL`.

## Deliverables

`HIGGS_COVERAGE.md`, per-analysis JSON and source/input/unit/energy hashes, numerical validation controls, and a `HIGGS_FULL_COVERAGE_VALIDATED` or `HIGGS_FULL_COVERAGE_BLOCKED` verdict. Clearly distinguish no experimental search in dataset from excluded/not excluded, and do not assert complete Higgs exclusions when a needed channel has no prediction.