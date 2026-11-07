# Next decisive task: source-matched COMPLETE one-loop Zee mu→3e coefficients and conversion cross-check

**Branch:** `research/zee-full-constraints`
**Baseline:** `b8629b330f5ac62817d96c8a89c2f6206c51c3e2`
**Source-first literature audit:** `research/full_constraints/LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md`.

## Aim — a real physics calculation, not another paper inventory

Use published *model-specific* results and a second independent executable to construct and cross-check **the complete Zee tree-plus-one-loop `mu→3e` operator vector at declared accuracy**, on the original D12 D7/F13 benchmark/family cards. In parallel qualify **one-loop `mu→e` conversion matching** and reproduce/explain the historical FlavorKit gold-target scalar-isovector 6.972% discrepancy. Preserve complex interference, neutrino/charged-scalar mixing, exact model couplings, and physical input conventions. Do not claim full LFV exclusion: missing *two-loop* `Wγ` / charged-current Barr–Zee groups remain outside this one-loop stage unless independently validated.

A **partial operator coefficient is NOT a complete μ→3e one-loop amplitude**. The current `module14/lfv.py` tree-only observable must remain DIAGNOSTIC_ONLY until all mandatory pieces and interference are included.

## Mandatory read-before-code / sources

Read:
- `research/full_constraints/LFV_EXECUTION_REPORT.md`
- `research/full_constraints/LFV_COVERAGE.md`, `LFV_VALIDATION.json`, `LFV_TASK.md`
- `research/full_constraints/LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md`
- `module4/amplitudes.py`, `module4/charged_scalar.py`, `module14/lfv.py`, exact D12 cards/receipts, original FlavorKit-generated `Lto3Lp`/`MuEconversion` code and branch evidence.
- **Bilenky & Santamaria, NPB 420 (1994) 47**, doi:10.1016/0550-3213(94)90375-1, Eqs (4.8–4.17), (4.20–4.21), Sec 6. Its *heavy unmixed singlet EFT* is an analytic **F-sector decoupling limit**, NOT exact finite-mass two-state mixing.
- **Mitsuda & Sasaki, PLB516 (2001) 47**, doi:10.1016/S0370-2693(01)00842-5, Eq (16), Eqs (26–28): mixed-charged-state `F^4` μ3e box. Paper's old **incoherent rate assumption** is not acceptable for general complex Zee amplitudes; compare the **complex operator coefficient**.
- **Ghosal, Koide & Fusaoka, PRD64 (2001) 053012**, doi:10.1103/PhysRevD.64.053012, Eqs (4.1–4.7): finite-mass mixed charged-scalar *on-shell q²=mZ²* LFV Z vertex; do **not** extrapolate it directly to q²≈0 for mu-e conversion or μ3e.
- **Crivellin et al. JHEP05(2017)117**, doi:10.1007/JHEP05(2017)117: complete low-energy μ→e EFT operator basis, QED/QCD running and nuclear matching.
- **Primulando, Julio & Uttayarat, EPJC82 (2022)** doi:10.1140/epjc/s10052-022-10189-0, Eqs(35–43): restricted-texture conversion operator reference, not universally transferable.
- **Khasianevich et al. CPC (2024) 109244**, doi:10.1016/j.cpc.2024.109244: `FlexibleSUSY/NPointFunctions` generic LO/one-loop `BrLTo3L`/`LToLConversion`, public `https://github.com/FlexibleSUSY/FlexibleSUSY`. Document whether model generation truly supports the present SARAH Zee model; actual executable matters.
- **Altmannshofer et al. JHEP06(2025)156**, doi:10.1007/JHEP06(2025)156, 2HDM two-loop `mu→eγ`, public pinned `general-2hdm-pheno`. The existing neutral fermion/photon terms were ALREADY matched in Module4; **NO double counting**. Its charged/W potential two-loop terms are NOT automatically Zee.

## Phase 1 — exact operator coverage map and source checks (strictly bounded)

1. Produce a **diagram → Wilson coefficient** table covering:
   - tree neutral `H/A` scalar 4-lepton exchange, full chirality;
   - off-shell photonic dipole `A_{L/R}` and monopole `K1_{L/R}`;
   - off-shell `Z` penguin `F_{L/R}`, including two mixed charged scalars and doublet Yukawas;
   - scalar penguin and all interfering 4-lepton box structures (one/two charged states, doublet Y, antisymmetric singlet F, complex phases).
   - conversion: quark scalar/vector/dipole/gluon Wilsons, nuclear target and signs, threshold running.
2. For each amplitude label `ALREADY_VALIDATED`, `PUBLISHED_MODEL_LIMIT_ONLY`, `GENERATED_SOURCE_UNVALIDATED`, `MISSING`. Explicitly trace external chirality, scalar mixing, mass routing, relative `i` factors, conjugations and q². Check *both* charge orientations, and operator normalization against the source and the already independently verified Lto3Lp spin traces.
3. No wholesale 2HDM-to-Zee substitution, no arbitrary formula from on-shell `Z→μe` used off shell, and no paper called 'complete' when it assumes one doublet-lepton Yukawa, F≈0, or incoherent box rates.
4. Stop Phase 1 after documented matrix; no repeat survey of hundreds of papers. Use the existing 2026-11-07 audit.

## Phase 2 — run an independent source-pinned complete one-loop backend

1. **First choice:** fixed-source FlexibleSUSY NPointFunctions (pin commit/release and FeynArts/FormCalc dependencies), generating the Zee `μ→3e` **tree+one-loop** coefficients and `μ→e` conversion. Reuse exact original masses/mixing/Yukawa cards, ***no*** full-loop SPheno pole masses or widths (known unphysical), no new random Zee spectrum. Inspect actual generated FeynArts diagrams and coefficient arrays: verify gauge+Goldstone/ghost contributions, external self-energies, gauge choice, q² approximation, and all lepton-chirality/operator contributions.
2. If native FlexibleSUSY cannot accept this original SARAH Zee model at frozen physical input, make **one** source-correct build/setup attempt plus **one** focused repair. If still blocked, report exact failure, not fabricated numerical output. Fall back to **independently recomputing the specific mixed-state F box and Z penguin from their original published equations** and compare to current generated FlavorKit on original cards. A published restricted limit is useful evidence but is NOT a complete model calculation.
3. At fixed original D7/F13 cards, output **actual numerical complex Wilson coefficients** for each matched operator, not just BRs, including source executable/stdout/input hashes. Compare individual diagrams/kernels and full summed coefficient vectors to the existing native FlavorKit/SARAH generated operators.
4. For `μ→e` conversion, repeat both vector-isovector and scalar-isovector gold (Au) control at independent nucleon-current level; explicitly trace proton/neutron interchange and resolve the existing `1.06972357425` rate ratio without claiming it is a random model uncertainty. Check other nuclei only as original fixed target/control cases.
5. Test exact one-state limits, F→0, equal charged masses, mixing endpoint/exchange, external complex phase covariance, SU(2) Ward identities and gauge parameter cancellation where measurable, known Kuno–Okada dipole normalization and interference. Keep original 73/75 historical branch-name assertions unchanged and report separately.

## Phase 3 — physically honest integration and finish

- Only if a complete **tree+one-loop** model operator vector is independently source-verified, expose an isolated research adapter `LFV_ONE_LOOP_MATCHED` with declared missing higher-order (`Wγ`, charged-current etc). Evaluate one-loop `μ→3e` on *existing cards only*, with experimental input and uncertainty qualification. Do **not** declare `LFV_FULL_COVERAGE_VALIDATED` while materially interfering two-loop contributions may dominate.
- If any complete coefficient sector cannot be generated/validated, do not construct an incoherent or tree-only 'physical BR'; return `LFV_ONE_LOOP_BLOCKED` and the exact missing coefficients. The already validated one-loop subsets remain useful.
- Output `research/full_constraints/LFV_SOURCE_TO_CODE_REPORT.md`; `lfv/LFV_OPERATOR_MATRIX.json`; `lfv/LFV_FIXED_CARD_RESULTS.json` with actually computed complex values (or explicit `null` for missing), source pins, tests and logs. Update the overall status only if truly passed.
- **Hard stop:** do not begin any new standalone two-loop derivation, new scalar proposal, exploratory or final parameter scan, Condor, MG5 production, SPheno full-loop mass use, or modification to frozen Modules 0–13. No global acceptance.
- After one bounded execution or explicit build failure, **stop and report findings**. Commit/push only research branch.

**Success = a validated complete one-loop operator vector, OR a precise nontrivial source/physics blocker with already published F-box/Z matching evidence.** A few new lines of code or more tests alone are not success.
