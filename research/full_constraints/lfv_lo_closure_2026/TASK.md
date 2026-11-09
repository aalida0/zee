# Publication-scoped leading LFV operator closure — one coordinated execution

**Date:** 9 Nov 2026. **Branch:** research/zee-full-constraints.

**Physics objective:** For EXACTLY the four frozen low-texture Zee Type-II witnesses (D7 NO/IO texture_0.0001, F13 NO/IO texture_0.001), produce the **leading** signed Wilson coefficients, interference and experimentally normalized rates for `mu -> 3e` and `mu N -> e N` (Al first), or an unambiguous operator-by-operator blocker. This work supports a charged-Higgs cascade phenomenology paper; it is NOT a new all-orders Zee flavor-theory paper.

**The user's explicit priority:** ONE substantial execution with multiple independently useful outputs. **Do not** spend the whole execution on source re-audits, setting up failed FlexibleSUSY, or custom general-Rxi 2-loop renormalization. Deliver calculated coefficients or a specific reproducible incompatibility. No new scan, masses, detector simulation or collider production.

## Input locks, conventions, existing implementation

- Read root AGENTS.md and `research/full_constraints/lfv_precision_scope_2026/LFV_PERTURBATIVE_SCOPE_DECISION_2026-11-08.md` and `research/full_constraints/lfv_integrated_2026/{RESULT.json,TRIAGE.md,OPERATOR_LEDGER.json,INPUT_MANIFEST.json,TEST_RESULTS.json}`. All these reports exist; do not rewrite them.
- Reuse already source-verified `module3` one-loop dipoles, `module4` photon Barr-Zee subsets, and `research/full_constraints/lfv_transfer_2026/zgamma/CONTINUATION_RESULT.json`. Do not duplicate radiative calculations, or re-run four-card provenance reconstruction. `hZ` remains preliminary.
- Four-card D12 original source `validation/module12/d12_benchmarks.json` SHA256 `f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8`; exact low-texture witnesses already mapped in `research/full_constraints/lfv_transfer_2026/CARD_PROVENANCE.json` and `BASELINE_REPLAY.json`. The older `scale_0.001` witnesses are NOT the same Yukawa matrices.
- Native `D=-sin(beta)*Ye+cos(beta)*Ye2`, `F=2*f_Chen` antisymmetric, charged rotations `H_D+=cos(gamma) H1+ - sin(gamma) H2+`, `S+=sin(gamma) H1+ + cos(gamma) H2+`. Native lepton flavor order e,mu,tau; neutral 2HDM `rho_l=D/sqrt(2)`; do NOT use previously erroneous `rho_l^dagger=D/sqrt(2)`.
- Source assets already exist in `research/full_constraints/lfv/source_to_code.py`, `LFV_OPERATOR_MATRIX.json`, `LFV_SOURCE_TO_CODE_REPORT.md`, `LFV_COVERAGE.md`, `reference/lfv/scripts/zee_lfv_backend.py`, `research/full_constraints/lfv/flavio_dipole_control.py`, frozen FlavorKit and source pin manifests. Source-to-native mapping of the `F`-only four-lepton box was partially independently validated. Do not rederive it from scratch.
- The generated public FlavorKit `MuEconversion` has a **verified scalar proton/neutron interchange**; **do not** call it physically correct. Apply correction only in the new isolated adapter with explicit p/n-current testing.
- The 2023 Heeck–Thapa **dipole-dominance** conversion relation is NOT a general Type-II Zee result. Also, do NOT apply the 2017 paper's special quark-Yukawa restriction to this Type-II model.
- All new code/data only in `research/full_constraints/lfv_lo_closure_2026/`. Read-only imports permitted from frozen modules and original source fixtures. Downloaded pinned public source only in ignored `work/lfv_lo_closure_2026/`. No changes to `module*/`, `validation/`, prior research folders, sources, root AGENTS, git or credentials.

## One integrated execution: five deliverable phases

### Phase A: build a *working* shared Wilson-coefficient adapter
1. Define canonical complex operator basis, scale, chirality, index direction, dimension and normalization for `mu->e gamma`, off-shell photon `K1` (anapole), `K2` dipole, four-lepton S/V/T, and semileptonic scalar/vector/gluon operators. Link every coefficient to original source generator equation or verified native action.
2. Import exact four frozen texture cards and existing dipole coefficients as immutable inputs. For each operator, record `VALIDATED`, `CANDIDATE_UNVALIDATED`, `NOT_AVAILABLE` with source and independent control; absent coefficients are **null, never zero**. Include complex phases and both lepton chiralities.
3. Unit tests: no double counting, one-sided flavor switches, mass-dimension consistency, scalar mixing and exchange limit, complex conjugation and controlled rephasing. Prevent normalization shortcuts.

### Phase B: source-validated `mu->3e` leading amplitude
1. Compute native tree h/H/A scalar exchange (including identical electron exchange) and independently compare to frozen analytic source; then import and check full signed off-shell photon `K1`, dipole `K2`, relevant `Z` penguins, all contributing `D/F` scalar boxes, including both physical charged eigenstates.
2. Reuse existing ten-operator/fourteen-operator trace rate and the restricted Mitsuda–Sasaki 2001 `F` box, but verify **each nonzero Wilson structure and its relative phase**. An independent numerical control for two distinct complex nonzero cards or nontrivial synthetic controls is required before promoting the operator vector. Compute interference with identical-particle symmetry, not sum of positive partial rates.
3. Produce explicit four-card `mu->3e` coefficients and rate **only if** all materially leading operators at the declared accuracy are source-validated; otherwise `mu3e_rate=null`, with signed validated partial groups retained as diagnostics and a minimal mismatched/evidence case.

### Phase C: Type-II `mu -> e` conversion on aluminium
1. Include the complete **leading relevant UV operator inventory**: dipole, off-shell photon monopole, low-`q²` Z penguin, neutral h/H/A scalar exchange with Type-II u/d/s Yukawas, heavy-quark/gluon matching where needed, and the relevant semileptonic boxes. Match relevant QED/QCD evolution and operator basis using published KKO/Crivellin or pinned verified compatible `flavio`/`wilson` source.
2. Implement explicit nuclear `Z g_{p} + N g_{n}` scalar contraction and signed vector/scalar/dipole interference in a NEW adapter; test nonzero scalar-only, vector-only, dipole-only, scalar+vector phases, and exchange p ↔ n. Do not silently use the uncorrected generated FlavorKit `MuEconversion` code. Quote isotope, capture rate, overlap integrals, matching scale and uncertainties.
3. Output a **physical conversion rate only if** the leading semileptonic Wilson vector is complete and matching validated, otherwise null and show actual per-group signed coefficients and known partial contributions. A dipole-only conversion number can be labeled DIAGNOSTIC only.

### Phase D: quantitative reality checks, no new two-loop campaign
1. Use `lfv_precision_scope_2026/SCOPE_DIAGNOSTICS.json` and source-hashed `F^\dagger F` one-loop reference to classify gauge dressing beyond the leading one-loop prescription. Examine possible *new* enhanced/chirality/top- or tau-mass-flip two-loop invariants, and distinguish mathematical proof of absence from source-backed numerical smallness and heuristic power counting.
2. If a genuinely potentially leading unknown group exists, mark it `UNRESOLVED_POTENTIALLY_LEADING` with the exact flavor tensor, topology and missing gauge/counterterm partners; **do not attempt a full general-Rxi two-loop calculation**. Such uncertainty prevents a full physical LFV pass but should not prevent completing the rest of the deliverables.
3. Do not introduce arbitrary 1%/10% missing-loop uncertainties, or pretend the conditional 1.36e-12 GeV^-2 norm budget is a bound on omitted amplitudes.

### Phase E: paper-relevant decision, not overclaiming
1. For D7 NO/IO, F13 NO/IO, generate a CSV/JSON table with `mu->e gamma`, `mu->3e`, `mu->e conversion (Al)`, optional tau dipoles if source-validated; each includes complex operators, rate or null, source/accuracy, experimental limit + date/CL, and status. The same rate calculator can compute diagnostic partial rates, but these must be labeled **PARTIAL_DIAGNOSTIC**, never interpreted as physical exclusions.
2. Distinguish `SCOPED_LEADING_CALCULATION_READY` from `PHYSICAL_LFV_PASS`. The latter requires all declared mandatory processes complete with defensible theoretical uncertainty; if not, `physical_lfv=UNKNOWN`, `global_acceptance=null`. Clearly list exactly which source-matched one-loop terms remain if any.
3. Recommend the minimum next scientific action: (i) validated new LO operators already sufficient for a publishable **qualified** cascade study, or (ii) a *single* precise specialist question to close one missing genuinely leading coefficient; don't recommend another indiscriminate two-loop sweep. Do not run mass scan.

## Efficiency / execution stop criteria

Work sequentially but **do not stop the entire task on the first blocked coefficient**. If a symbolically gauge-unsafe operator or unavailable source is found, log the exact missing source/normalization and continue other phases. Do not spend >one third of the total execution on pure literature audits, installs or repair of the known failed FlexibleSUSY/Package chain. Prioritize code that produces numerical coefficient values and independent tests. No requested deadlines or unverified time estimates. End with the **best physically meaningful achieved result**, not an empty plan.

## Deliverables, with concrete filenames

Inside this new directory only:
`RESULT.json` (explicit complete/partial/blocker status);
`EXECUTION_REPORT.md` (executed numerical physics, independent controls and limits);
`WILSON_BASIS.md`;
`WILSON_LEDGER.json` (complex individual terms or nullable missing sources);
`BENCHMARK_LFV.csv`;
`MATERIALITY.json` (numerical scales vs limits, no invented missing bounds);
`TEST_RESULTS.json`;
`REPRODUCE.md`;
readable adapters/tests (`*.py`) and `TRIAGE.md`.
Execute focused tests; `git diff --check`; preserve pre-existing uncommitted files. Print file list and the final scientific verdict. **Do not stage, commit or push.**

**Failure handling:** `SOURCE_BLOCKED`/ `LEADING_OPERATOR_INCOMPLETE` is a legitimate science verdict; a passed *algebraic or rate kernel test* is **not** a matched physical observable. No manual switching to fully permissive mode, no unauthorized source-package modifications.
