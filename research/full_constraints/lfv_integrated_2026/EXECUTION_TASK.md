# Zee Type-II integrated LFV closure: one coordinated, publication-scoped execution

**Date:** 2026-11-08. **Research branch:** `research/zee-full-constraints`. **Research objective:** a source-validated leading-contribution LFV constraint prescription for a non-detector-level phenomenology paper on `H2± -> H1± Z`. This **one large task** consolidates radiative LFV, the materially relevant Zee singlet/gauge issue, leading mu->3e, mu-e conversion and an auditable four-card physics verdict. It must do **actual numerical physics**, not another literature-only report or another 70k-token baseline-replay exercise.

## Scientific decision / success conditions

**Best possible outcome:** `PHENO_LEADING_LFV_VALIDATED`, meaning all contributions *material at the explicitly declared leading accuracy* for the specified charged-lepton processes were coherently included or shown legitimately beyond that accuracy, their conventions and physical rates independently validated, and numerical theory/systematic uncertainties sufficient for the stated per-card comparisons. A justified, explicitly qualified `SCOPED_LFV_CONSTRAINT_READY` for a subset of processes is useful even if others remain UNKNOWN. All-order, universal, or NNLO claims are NOT required.

**Honest fallback:** `LFV_LEADING_SCOPE_INCOMPLETE`, listing exact missing source amplitudes, numerical consequences/conditional sensitivity, and a *single concise specialist question* if new two-loop renormalization is genuinely indispensable. An unvalidated or missing coefficient must be stored `null` with reason, NEVER zero. A source-matched numerical subset may say `VALIDATED_SUBSET` without declaring a complete physical BR or pass.

**Forbidden:** asserting global allowed benchmark(s) from partial LFV, pretending a loop-factor guess is a rigorous bound, extrapolating four texture cards to a universal full scan, source-matching only absolute rates rather than signed complex amplitude, doubling existing photon terms, redoing candidate-A/vacuum/B->Xsγ/Higgs pipelines, generating new scanner points, Condor/production/Delphes/ATLAS detector work, or performing an open-ended custom two-loop tensor calculation by default.

**Execution budget:** ONE coherent Codex execution, progressing through all phases and leaving partial **working** code/data for each independently finished component. No outside orchestrator retries automatically. Do not spend the task repeatedly downloading archived papers or rebuilding broken SPheno/FormCalc/FlexibleSUSY environments. Prefer direct reuse of validated source code; if a one-loop generator cannot yield model-specific operators from existing checked generated code, record it and move to other sectors. Avoid large Monte Carlo integrations or additional benchmarks. Provide concise checkpoints in `CHECKPOINT.md` and finish with a working reproducible deliverable, not just an outline.

## Prerequisites already completed — READ, DO NOT REEXECUTE

- Root `AGENTS.md`, `research/full_constraints/LFV_COVERAGE.md`, `LFV_SOURCE_TO_CODE_REPORT.md`, `LFV_PUBLIC_CODE_REUSE_AUDIT_2026-11-07.md`, `LFV_2HDM_TO_ZEE_PRIMARY_SOURCE_REUSE_AUDIT_2026-11-08.md`.
- `lfv_transfer_2026/NEUTRAL_YUKAWA_ORDERED_MAPPING.md` (the **corrected** source map), `lfv_transfer_2026/zgamma/CONTINUATION_REPORT.md`, `CONTINUATION_RESULT.json`, `CONTINUATION_TESTS.json`, `zgamma/continue_zgamma.py`. Zgamma was **validated** with 2 complex source controls / both chiralities at max residual 3.03e-14; do not rederive or rerun the complete source comparison except a cheap regression. Its four-card partial-rate shifts were +1.02229e-12, +8.05537e-13, -7.35462e-15 and +5.48923e-14, **NOT theoretical uncertainty on omitted sectors**. Already included Module4 photon contributions must not be counted again.
- `lfv_transfer_2026/HZ_EQ59_PRELIMINARY_NUMERICAL_2026-11-08.md` contains a **corrected** preliminary neutral hZ calculation. It is source-evaluated but **not independently tested against the author `hZ` group**. Do not reuse its older reversed chirality or erroneous interference.
- `lfv_transfer_2026/CARD_PROVENANCE.json`, `BASELINE_REPLAY.json`, `INPUT_SHA256.json`, `lfv/TEXTURE_MATERIALITY_REPRODUCED.json`, `lfv/TEXTURE_COUPLING_AUDIT.json` contain four fully hash-replayed low-texture physical cards. The historical `scale_0.001` D12 cards have **different Yukawa matrices** and must never be substituted.
- `module14/physics_adapters/lfv_reference.py`, `lfv_reference_evidence.json` already contain source-vs-native signed, complex photon 2HDM comparisons. Existing Module3 and Module4 results are read-only; `module4/amplitudes.py` source structure can be imported but **not modified**.
- The old F-only mixed H1/H2 box was already matched to Mitsuda–Sasaki 2001 on 28 controls; 10 four-lepton contact-action rates and relative phase cases already independently checked. Reuse instead of rederiving. Existing FlavorKit generated Zee one-loop coefficients are **not yet independently validated as a complete signed physical vector**; the public `MuEconversion.f90` scalar proton/neutron interchange is already diagnosed.
- Prior pilot's `F-dagger-F` gauge renormalization has an uncompleted W-neutrino self-energy pole and GWW subdivergence: these are NOT a finite zero, and should **not** trigger an open-ended full R-xi derivation.

**Unmodified inputs:** exactly the four D7/F13 NO/IO low-texture records, **D7 `texture_0.0001`**, **F13 `texture_0.001`**, from the pinned original `validation/module12/d12_benchmarks.json` SHA256 `f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8`. Source-hashed scalar cards, full `D,F,Ye,Ye2`, neutral masses, mixing and existing baseline are already pinned. A quick SHA check is sufficient; do NOT spend tokens re-deriving original provenance or scanning new mass points.

## Source and physical conventions — never improvise

Frozen operator (GeV, flavor ordering e,mu,tau):

    L_dip = (e*m_mu/2) bar(e) sigma^(mu nu) (C_L P_L + C_R P_R) mu F_(mu nu) + h.c.
    [C_L]=[C_R]=GeV^-2; sigma^(mu nu)=i[gamma^mu,gamma^nu]/2.

Correct general-2HDM to frozen Zee neutral Higgs-basis mapping:

    rho_l = D/sqrt(2)          (NOT rho_l^dagger = D/sqrt(2)
    c_L(mu->e gamma) uses D[e,mu]/sqrt(2)
    c_R(mu->e gamma) uses conj(D[mu,e])/sqrt(2)
    C_L/R = -c_L/R/(8*pi^2*v^2), with matching projector, flavor and photon conventions.
    D = -sin(beta)*Ye + cos(beta)*Ye2; F = 2*f_Chen is antisymmetric.
    H_D+ = cos(gamma)*H1+ - sin(gamma)*H2+
    S+   = sin(gamma)*H1+ + cos(gamma)*H2+.

Use **complex** `(C_L,C_R)` and full coherent amplitude before any BR. Always record which source equation, matching scale and mass/Yukawa renormalization scheme a coefficient uses, and whether the source is leading accuracy or formally corrected. Existing code sources use some approximate running `m_t,m_b`; do not mix input schemes silently. Physical lepton widths and experiment/CL must be versioned, not inferred from missing outputs. Extra-doublet quark Yukawas follow Type II, **not** the negligible-quark Yukawa assumption in Heeck–Thapa 2023. One-state Type-II charged-Higgs mass exclusions cannot be applied independently to both Zee eigenstates.

## Phase 1 — integrate completed radiative pieces and finish neutral hZ (highest probability of closure)

1. Create independent adapter only under `research/full_constraints/lfv_integrated_2026/`. Read existing validated per-card Zgamma coefficients; recheck SHA and names and protect from duplication. Preserve the original outputs unchanged.
2. Independently evaluate the **complete standalone hZ** Eq.(59) contribution of Altmannshofer et al., arXiv:2410.17313v4, corrected 2026 erratum where applicable, with both complex chiralities. Compare to the pinned author `thdm.py` **nonzero complex** `cL_llpg_hZ/cR_llpg_hZ` for two controls. Also test h-H alignment, swap direct Yukawa entries, gamma independence of the neutral sector and no-LFV zeros. Reuse the published f7 numerical quadrature already in the preliminary hZ note; independent control means comparing a separate source coefficient assembly, not two calls to the same adapter.
3. On pass, give four-card new complex `C_L,R^hZ` and interference with **baseline + Zgamma** (not with an arbitrary old scale card); else `hZ=null` and exact reproducible mismatch.
4. Preserve older validated `neutral lepton/quark photon` and `charged scalar photon` Module4 rows **once each**. Tag actual inclusion and *not*-included terms with rigorous source IDs.
5. End Phase 1 with a completely reproduced scoped radiative ledger `dipole_terms.json`, with each physical channel `mu->e gamma`, `tau->e gamma`, `tau->mu gamma` where available; no classification of complete LFV yet.

## Phase 2 — remaining doublet electroweak groups, prioritize full gauge-invariant units

Source: corrected full general 2HDM `Altmannshofer et al. JHEP06(2025)156` + `JHEP07(2026)184`, pinned author `jbrod/general-2hdm-pheno`, commit `b5035cd58d2a7e4a91e9790d045df062b97adffe`, `thdm.py` SHA256 `9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193`. Focus only on actual **leading-source aggregates and materially relevant groups**, not all diagrams in the paper.

Classify these full groups in a table with **source-verified original 2HDM limit, Zee state/coupling map, missing partners, and priority**:

- charged-fermion W-H+ source `tHp,cHp,tauHp`; include both H1/H2 with physical doublet and singlet projections *only if* the full set of source vertices maps and gauge and flavor composition survives the reduction. Explicit source limit `F=0,gamma=0`, 2HDM original single charged state, charged-state interchange and distinct Yukawa phases.
- whole gauge-invariant `kin` group including `f8e` with charged-Higgs dependence, W/G/ghost, complete source Eqs.(59)–(60). Do not separately import Wgamma or simply substitute `m_H1` for source charged mass; scalar/gauge mixing is nontrivial in Zee.
- mixed `HZ` charged-scalar Zgamma potential, including off-diagonal `Z H1 H2` and unequal-mass triangle kernels (Florentino–Romão–Silva 2021 App. D.3), orientations and partner insertions. No one-state rescaling as full Zee.
- `HW` charged-scalar W/potential group, whose public `thdm.py` contains a documented dimensional normalization discrepancy: **source-code anomaly must be isolated in a pure 2HDM reference control first**; do not import questionable code as trusted physics.
- external-mass/neutrino corrections and QED running are accuracy uncertainties only if quantitatively justified at declared approximation.

Implement only those groups for which a **source-matched, gauge-invariant transfer** is possible in the existing code without a new bespoke general-R-xi 2-loop calculation. Require at least two nonzero independent source comparisons for each claimed transferred coefficient, **both chiralities**, signed phases and one-state decoupling. A verified 2HDM limit is necessary but not enough to certify mixed Zee gauge completion.

For every other group, record `NOT_IMPLEMENTED`, specific missing physics and either (a) supported omission because it is beyond the explicit leading prescription, or (b) quantitative independently justified *bound* on its total relevant complex amplitude, or (c) `UNRESOLVED_POTENTIALLY_LEADING`. A guessed relative loop factor is a **diagnostic scale**, never a bound and never a physical PASS gate.

If a gauge-invariant closed form requires a large new symbolic tensor/renormalization project, **stop that subtask** and proceed to the three-body/conversion phases. Do not consume the whole run on a single sector.

## Phase 3 — Zee-specific singlet F, mixed charged current: the actual physics decision

The four cards suppress direct `D[e,mu],D[mu,e]`, but `F†F[e,mu]` is nonzero. The project already includes the `F†F` one-loop dipole; the mixed F-D chirality flip vanishes in the massless-neutrino approximation at one loop. Higher loops, W/G/ghost and mixed gauge insertions require care.

- **Enumerate** the flavor tensors and all *potentially leading* independent chirality structures entering `mu->e gamma`, `mu->3e` and conversion, including neutrino-mass-suppressed F-D, charged-current, wavefunction/reducible, and scalar-mixing insertions. For each list source, chirality and coupling powers, parametric mass scales and mandatory cancellation partners.
- **Separate** true new leading source structures from gauge-dressed perturbative corrections to already retained `F†F` one-loop structures. Compare to the explicitly stated leading 2HDM and 2023 Zee phenomenology truncation, **with the actual Type-II Yukawas**; do NOT invoke the latter paper's suppressed-quark-Yukawa or alignment assumptions unless verified on the exact card.
- Test whether an omitted leading term can introduce enhancements (m_tau/m_mu, m_top/m_mu, tanbeta, log ratios, small neutral direct Yukawa or cancellations), new flavor invariants or imaginary CP phases. Use dimensional/gauge/chiral reasoning to make a **testable ranking**, not an unsubstantiated 1% or 10% uncertainty. For four cards compute only source-backed coupling invariant magnitudes, one-loop reference norms and their relative sensitivity to existing 90% CL limits. Stored "missing-norm budget" is **a sufficient conditional threshold**, NEVER an estimate of missing amplitude.
- Where genuinely new finite mixed Zee gauge coefficients are source-matched in prior archives, attempt one controlled analytic/numerical transfer and independent gauge test. **DO NOT RESTART** the multi-month unfinished general-R-xi W/GWW divergence project merely for strict two-loop completeness. If no source-backed finite gauge-invariant expression or defensible materiality bound exists, `F_GAUGE=UNRESOLVED` and request one narrow expert input; keep full physical verdict UNKNOWN.

The key science output of this phase is whether the *declared leading accuracy* is physically justified for the actual texture cards and whether any unresolved term can flip a desired exclusion. It is not formal two-loop completion.

## Phase 4 — leading mu->3e and selected tau three-body operators, not rate-only clones

Use already generated SARAH/FlavorKit Zee coefficients *as source candidates*, with frozen physical masses/complex Yukawas; use verified `CalculateTreeS4L`, existing tested `K1,K2`, restricted Mitsuda–Sasaki F-only H1/H2 box and existing trace-validated 14-operator rate as benchmarks. The operator set includes 2 K1 (photon monopole) + 2 K2 (dipole) + 4 scalar + 4 vector + 2 tensor coefficients.

- For `mu->3e`: source-match **tree h/H/A**, photon K1/K2, low-momentum Z/scalar penguins, neutral/charged/mixed F/D boxes, including identical final-state exchange, complex phases and physical lepton masses. Check gauge cancellations with counterterms where relevant and the signed interference of the full vector. Do not transplant a published on-shell `Z->l l'` q^2=mZ^2 result as q^2≈0 conversion or three-body loop input.
- Retain the old 28 F-only box controls and 10 contact-action checks, but do not mistake those for whole model validation. Use an independent reference for at least two nonzero *mixed* operator examples (e.g. `flavio` WET four-lepton evaluation) after explicitly mapping normalization, ordering and QED scale.
- Compute physically scoped 4-card BRs only when the complete **leading-level** operator vector with interference and experimental input matches. If off-shell monopole, gauge penguin/box or relative phases cannot be source-matched, emit partial amplitude ledger and `mu3e=UNKNOWN`, do not silently drop terms. For tau 3-body, include those modes for which the exact same validated operator/rate basis applies; otherwise mark as not assessed with possible impact.

**No new FlexibleSUSY/FormCalc rebuild**: known SARAH+FeynArts+FormCalc same-kernel dependency failure was fully documented already; avoid redundant installs. If a generic 1-loop generator is demonstrably required, record one minimal reproducible workaround or precise blocker, but preserve time for the integrated result.

## Phase 5 — mu-e conversion in Al first, other targets optional

Source level: Kitano–Koike–Okada (hep-ph/0203110), Crivellin et al. JHEP05(2017)117, `flavio`/`wilson`, `FlexibleSUSY`, or `MuonBridge` where actually installed and source-verified. We need full **UV semileptonic** dipole/photon, Z penguin, neutral-scalar tree to u,d,s, quark boxes (incl Type-II), heavy-quark/gluon matching when required, QCD running and nuclear response where claimed, with complex interference.

**Known source bug**: public FlavorKit `MuEconversion` uses `(Z+N)g0S-(Z-N)g1S` with `g1S=(gp-gn)/2`, equivalent to `Z gn+N gp` instead of the physical `Z gp+N gn`; the original project independently reproduced it. Do not use original conversion predictions without correcting the scalar p/n contraction in an **isolated adapter** and testing nonzero scalar+vector interference against independently specified KKO nuclear currents. Do not overwrite public upstream code or the frozen generated sources.

Priority Al, then Ti or Au only if complete and inexpensive. State isotope, capture rates, overlaps, nuclear uncertainties, operator scale and matching signs. If a complete semileptonic vector is unavailable, **conversion remains UNKNOWN**, regardless of an approximate `CR(muAl->eAl)=0.0027 BR(mu->e gamma)` in the 2023 Zee paper: its negligible extra-doublet quark Yukawas differ from our Type-II setup. The dipole-only relation is a **diagnostic**, not a model-wide constraint.

## Phase 6 — paper-suitable integrated decision table and constraints gate

For exactly four frozen texture cards report a machine-readable coherent matrix of:
- `mu->e gamma`, `tau->mu gamma`, `tau->e gamma`, `mu->3e`, Al conversion, plus materially relevant universality, `h->mu e` and selected tau modes if native validated inputs available.
- for each `observable`: signed `C_L,C_R` or full WET operator vector, groups included, groups omitted and *why*, CP phases/interference, accuracy, fixed masses/Yukawa hashes, numerical controls, experimental source/date/CL, BR or conversion rate only when warranted, scheme uncertainty, and `status=VALIDATED_SCOPED / CONDITIONAL / UNKNOWN / PHYSICAL_FAIL` as justified.
- `PHYSICAL_FAIL` only if an experimental exclusion is established **robustly against all uncomputed interfering terms** or by a complete physically validated observable. Partial BR>limit **alone** cannot establish exclusion if arbitrary cancellation remains.
- `PHYSICAL_PASS` for LFV only if **every stated mandatory LFV process** is sufficiently complete at the *declared leading phenomenology accuracy* and limitations cannot reverse classifications. Otherwise LFV=UNKNOWN. This is **not** B, Higgs or vacuum global viability.
- `global_acceptance=null` for all four unless some separate, pre-existing fully validated *hard failure* justifies a specific `GLOBAL_FAIL`. Do not globally promote any witness, regardless of a very tiny partial mu->e gamma BR.
- Provide clear recommendation: can the planned **scan+charged cascade paper** cite a well-defined leading LFV prescription? Which contributions remain blocking **a publishable paper claim** versus only blocking strict two-loop completeness? Show exact 2017 and 2023 Zee model restrictions so they are not falsely used as blanket cover.

**If full integrated closure cannot be reached**, still provide a complete honest `TRIAGE.md`: sectors solved in this execution, ranked blockers by actual potential impact and coding effort, *one* sharply specified specialist calculation needed next, and whether a scientifically honest paper could proceed with conditional bounds rather than an invented excluded/allowed region.

## Deliverables: publishable research engineering, not narration

Write only under `research/full_constraints/lfv_integrated_2026/`:

- `EXECUTION_REPORT.md`: detailed result/limits, real calculations performed, precise published equations, independent controls, main physics verdict and paper implications.
- `RESULT.json`: final status from `PHENO_LEADING_LFV_VALIDATED` / `SCOPED_LFV_CONSTRAINT_READY` / `LFV_LEADING_SCOPE_INCOMPLETE` / `SOURCE_DISCREPANCY` / `EXECUTION_BLOCKED`. Include `model_scope`, `accuracy_scope`, `four_cards`, `new_validated_groups`, `unvalidated_groups`, `observable_coverage`, `physical_lfv`, `global_acceptance`, `source_hashes`, `tests_passed`, `calculations_executed`. Do not report `new_validated_groups` except with independent source-backed numerical tests.
- `INPUT_MANIFEST.json`, `DIPOLE_TERMS.json`, `OPERATOR_LEDGER.json`, `CARD_CONSTRAINT_MATRIX.csv`, `MATERIALITY.json` with *nullable* missing amplitude entries and complete provenance; do not reproduce megabytes of immutable baseline or downloaded copyrighted papers.
- `REPRODUCE.md` with exact commands/source checkout hashes/machine versions/dependency preconditions and reproducible reference-point tests.
- `test_*.py`, research-only adapters, `TEST_RESULTS.json`, `TEST_LOG.txt`, `TRIAGE.md` and `CHECKPOINT.md`; include tests for complex chiralities, field phase flips/rephasings, `F=0`, `gamma=0`, singlet decoupling, swapped H1/H2, one-sided D[e,mu]/D[mu,e], source 2HDM limit, gauge-invariant group completeness, no photon double-count, and nonzero complex interference. Mark nonexecuted checks as NOT_TESTED, not PASS.

**Git discipline:** do NOT modify root `AGENTS.md`, frozen `module0`–`module14`, `validation/`, old completed research folders, `models/` or experimental snapshots; all experimental adapters and tests are inside new result directory. Public files can be read from existing cache or downloaded **only** into ignored `work/lfv_integrated_2026/`, source/hash pinned. Use workspace-write sandbox, no unsafe full-access, no `--yolo`, no sudo, no credential inspection. Do not stage, commit or push yourself. After finishing, run focused tests and `git diff --check`, verify only allowlisted research files changed, print paths and short final scientific verdict. A separate user review/commit follows; do NOT rerun automatically if a source, math or permission test fails.

## Most important reviewer stop rule

This project is a *charged scalar cascade phenomenology* paper, **not a comprehensive two-loop LFV methods paper**. Make a stringent, honest choice of **which contributions are physically leading at our declared accuracy**. Do not waste an entire long execution attempting a diagram family that would make the paper no more publishable. When a leading, genuinely Zee-specific gauge amplitude has no source-verified finite answer, preserve it as a blocker and continue to finish other feasible constraints. **Useful partial physics completion is preferred to 100 pages of repeated UNKNOWN justifications.**
