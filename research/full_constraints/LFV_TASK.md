# LFV completion: operator-by-operator validation and genuine hard exclusions

**Execute only after reading `PLAN.md` and the B→Xsγ feasibility result.**
No new parameter scans, and the original Modules0–13 and D14 evidence are read-only.

## Scope

Build a source-justified coherent Zee LFV calculation with explicit, publication-grade defined perturbative accuracy:
- `μ→eγ`, `τ→eγ`, `τ→μγ`: all leading one-loop amplitudes, relevant two-loop Barr–Zee/bosonic groups and their complete gauge/IR cancellations, H1/H2 charged-singlet/doublet mixing, antisymmetric `Fzee`, and neutral scalar Yukawas;
- `μ→3e`, `τ→3e`, `τ→3μ`, `τ→μee`, `τ→eμμ` as applicable: tree scalar exchange, electromagnetic and Z penguins, boxes, and exact complex interference at supported order;
- `μ→e` nuclear conversion: dipole, scalar/vector lepton-quark operators, matching and nuclear overlaps for declared target(s);
- explicit differentiation of 90% CL experimental limits from forecasts; model-specific charged/neutrino-induced channels versus neutral 2HDM subset.

## Existing source

`module14/lfv.py`, `module4/interface.py`, `module3/`,
`module14/public_spheno_evidence.json`,
`module14/physics_adapters/lfv_reference_evidence.json`,
`module14/physics_adapters/spheno_build_evidence.json`,
`module14/PHYSICS_ADAPTER_READINESS.md`.
SARAH 4.15.4 / SPheno 4.0.5 / FlavorKit source pinned in module14.
`general-2hdm-pheno` GitLab SHA
`b5035cd58d2a7e4a91e9790d045df062b97adffe`,
2026 erratum doi 10.1007/JHEP07(2026)184.
2017 full Zee paper JHEP04(2017)130 as **independent model source**, not an assumed codebase.

## Work

1. Produce a diagram/operator matrix: each necessary topology, original source reference, order, model fields, QED gauge group and current implementation; list exact missing contributions and which can interfere. Do not call a source's `mu→3e` routine complete without matching its scalar/penguin/box Wilson coefficients.
2. Reproduce existing Module4 complex amplitude controls; ensure the upstream neutral fermion/photon two-loop subset is not double counted. Translate phases and conjugation at **coefficient level**, not only final BR.
3. Use full generated FlavorKit operators where possible, but SPheno **full-loop pole spectrum/decays are currently UNAVAILABLE** (pathological 10^6 GeV widths, neutrino-mass input schemes). Do not use these unphysical outputs. An operator-only fixed-physical-scheme backend can be valid only after independent amplitude/source and IR/Ward tests.
4. Include `Fzee` and both charged mass eigenstates in complete gauge-invariant sets; check gamma endpoints, antisymmetry F, neutrino-massless limit, helicity/chirality, and tree-limits. Validate the *entire claimed set* on original D12 cards plus documented published limits.
5. Experimental inputs must have source/date/nuclear target and CL. Propagate justified uncertainties and interference; signed complex coefficient output necessary to avoid spuriously positive rate sums.
6. Adapter must validate source hashes, full card (including neutrino family), matching schemes, units, and operator coverage. A single missing material term yields UNKNOWN. Only fully validated scoped observable gets actual physical comparison `PASS/FAIL`; total LFV hard gate requires every declared mandatory channel.

## Deliverables

`LFV_COVERAGE.md` with every operator and row `VALIDATED/UNVALIDATED`, original reference and test. Code only under `research/full_constraints/` or optional strict `module14/physics_adapters/`, no edits to frozen upstream modules. Focused tests and explicit full/full-blocked status `LFV_FULL_COVERAGE_VALIDATED` or `LFV_FULL_COVERAGE_BLOCKED`. Preserve `globally_allowed=null` until all mandatory constraints pass; do not turn a partial BR > bound into a physically rigorous FAIL if omitted diagrams can destructively interfere.