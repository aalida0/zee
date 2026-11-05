# D16 MASTER TASK — Complete gauge-invariant Zee-model two-loop radiative LFV

**Branch:** `research/zee-d16-wgamma-gauge-matching`.
**Validated starting physics:** D15 `ONE_LOOP_COMPLEX_DIPOLE_PASS` at `f667635`; D16 generic 2HDM reference, HW normalization and restricted Zee singlet HZ at `18b5f82`. The mixed-HZ preparatory task `D16_MIXED_HZ_TASK.md` was added at `3a18e2d`. Begin from the **current branch HEAD** rather than resetting to any historic commit.

## USER'S OBJECTIVE — ONE LARGE END-TO-END EXECUTION

**Deliver a validated, gauge-complete leading two-loop `l_i -> l_j gamma` calculation in the CP-conserving Type-II Zee model, with complex L/R amplitudes, including the genuinely new physical charged-singlet/mixed-state corrections relative to the corrected general 2HDM, and a coherent double-counting-free combination with existing one-loop/fermion-photon/scalar-photon subsets.**

This is not a request for another inventory, one arbitrary topology, or 10 small status updates. You may execute in internally staged phases, but **continue the work after each phase without waiting for approval**. Run actual calculations and tests. Commit and push reproducible progress periodically. Aim for the complete scoped `ZEE_TWO_LOOP_RADIATIVE_LFV_PASS`, not just an isolated class; preserve scientific gates even if completion proves impossible.

**Do not claim** all Zee LFV observables or full scan acceptance: three-body LFV, mu-e conversion, Higgs constraints and other operator sectors are separate. If a diagram is formally beyond the leading-order truncation, prove this with chiral/power counting and source diagrams instead of silently excluding it.

## Read before executing

- `research/wgamma_d16/HW_NORMALIZATION_AUDIT.md`
- `research/wgamma_d16/GENERIC_2HDM_CLOSURE.md`
- `research/wgamma_d16/EXTERNAL_2HDM_BASELINE.md`
- `research/wgamma_d16/ZEE_EXTENSION_INVENTORY.md`
- `research/wgamma_d16/D16_GAUGE_DERIVATION.md`
- `research/wgamma_d16/STATUS.md`
- `research/wgamma_d16/zee_singlet_hz.py`, `zee_singlet_hz.py`
- `research/wgamma_d16/parent_integrals.py`, `native_integrands.py`, `longitudinal_identities.py`, `tensor_reduction.py`
- `research/spheno_flavorkit/CROSSING_BRIDGE.md`, D15 operator validation
- `module3/CONVENTIONS.md`, `module4/MATCHING_AUDIT.md`, `module4/CHARGED_SCALAR_AUDIT.md`
- Corrected publication: Altmannshofer et al. arXiv:2410.17313v4 + JHEP July 2026 erratum, original code `https://gitlab.com/jbrod/general-2hdm-pheno` pinned `b5035cd58d2a7e4a91e9790d045df062b97adffe`. Author source stays byte-for-byte unchanged.

The corrected general-2HDM *complex* reference agreement has already been established on 39 channels (both chiralities, generic nonzero Z3,Z7) after fixing the authors' extra 1/MW² in `HW` **only in our adapter**. The source bug remains an explicit expected failure. Twelve other reference groups agree. The fully decoupled singlet is an amplitude limit, not a valid neutrino fit. A restricted `gamma=0,F=0`, nonzero portal, pure charged-singlet scalar–Z–photon class is validated; don't redo these completed checks unless a concrete physics contradiction emerges.

## PHASE I — Full *physical* charged-scalar Zγ potential class, not just a toy

**Deliver a complete, gauge-invariant bosonic h/H/A–H_a^±–(Z,γ) contribution in the physical charged basis for generic nonzero mixing gamma and potential portals.**

1. Derive all native, oriented `G_{s,ab}=d³V/(d s d H_a^- d H_b^+)`, `Z H_a^- H_b^+`, `γ H_a^- H_b^+`, `Z γ H_a^- H_b^+`, `G^0 H_a^- H_b^+`, and necessary Goldstone/gauge-fixing/ghost sources from the frozen SARAH model. Use `d=(cosγ,-sinγ)`, `T_Z=(d d†/2-sW² I)/(sW cW)`, photon `Q=I` only after checking native vertex normalization. Pin SHA/source ordering. Include `A` off-diagonal trilinears and complex external neutral Yukawas; CP conservation does not imply the off-diagonal `A` class vanishes.
2. Enumerate both scalar-loop orientations, all unequal-mass charged assignments, AZ seagull/contact, both external lepton-line orders and every longitudinal-Z/neutral-Goldstone/BRST/LSZ partner required by nonconserved off-diagonal charged current. For `M_a² != M_b²`, the commutator `[M²,T_Z]` is nonzero and a transverse-only substitution is generally invalid.
3. Derive and independently integrate the unequal-mass scalar-loop and massive Z outer master functions; preserve UV poles and `O(ε)` where needed. Verify real-photon Ward and the full Z/Goldstone ST identity. First produce nonzero off-diagonal complex `C_L,C_R`; then complete the full gauge-invariant class. Do **not** accept an inner transverse tensor without its ST partners.
4. Numerical falsifiers: `gamma=0` with portals off returns the corrected general-2HDM `HZ`; `gamma=0` with portals on returns exactly the reference doublet `HZ` + already proven unmixed singlet `HZ`; zero F is not required for neutral scalar-Z-photon diagrams if neutral Yukawas are correctly matched, but initially fix F=0 to isolate this class. Also test both charged states degenerate (basis covariance), row sign flips, `gamma -> -gamma` with consistent phase/basis mapping, portal and LFV zeros, heavy singlet decoupling, independent complex rephasings, all three decay channels.

## PHASE II — Generalize the *gauge-complete* W/charged-current 2HDM aggregate

**Deliver the additional Zee-specific h/H and charged-sector W/Goldstone/ghost/pinch/LSZ radiative amplitudes, with no naive rescaling of a whole 2HDM result.**

5. Identify the corrected paper's genuine gauge-invariant bosonic and charged-fermion aggregates vs its individually gauge-dependent pieces. Derive a matched overlap prescription using identical input EW/mass/Yukawa schemes and the strict `gamma=0, F=0, portals=0` limit. Reuse the published complete 2HDM group wherever the *entire* gauge-invariant class is demonstrably unchanged in Zee; do not double count the already validated Module4 photon classes.
6. Generate the full *new* gauge-invariant diagram set for (H_1^pm,H_2^pm) and nonzero mixing: neutral-charged derivative vertices, physical charged W currents, Goldstone mass-difference vertices, charged-sector seagulls, photon attachments on both orders, internal charged-lepton/neutrino parents, mixed-contact and pinch terms, ghost/BRST insertion kernels, and any required reducible self-energy/counterterm/LSZ partners. Use previously saved 26 regulated inner diagrams and eight fixed-r parent subloops as independent building blocks. Avoid restarting the completed 2HDM result.
7. Construct the finite *difference* `Delta_C^W = Zee - 2HDM overlap` diagram by diagram only when the subtraction acts on a matched gauge-invariant **whole set**. Do not subtract arbitrary gauge-dependent kernels or manufacture a compensator `-Delta_xi C_G`. Work with `d=4-2eps`, signed native vertices, two external scalar placements, massless neutrino approximation as defined, and same D15 operator convention.
8. Gauge check the independently computed *complete* sum at `xi = 0.5,1,3` (and additional separated value if stable), both complex chiralities and ≥2 nondegenerate spectra, with numerical uncertainty. Require full UV/local counterterm cancellation and photon Ward/ST identities. Compare the `gamma→0` result to the corrected authors' **complete** 2HDM complex amplitudes and signed EDM/diagonal limits. Reconcile remaining differences from CHK/Ilisie/Abe by diagram scope, not by fitting a kernel.

## PHASE III — Antisymmetric F-dependent charged-current LFV

9. Determine all **leading relevant two-loop** terms involving the Zee antisymmetric charged-singlet lepton Yukawa F, including mixed F–D and F–F structures as appropriate, Majorana charge orientation, nonzero charged mixing, external chirality factors and internal neutrino-mass power counting. Generate complete diagram sets and prove which terms vanish in the *massless internal neutrino approximation* vs which survive. A F=0 proof or a one-loop F–D zero is not a two-loop F-dependent proof.
10. Calculate the surviving terms and all their gauge partners, using original Zee SARAH vertices, required counterterms and the same expansion. Check rephasings, symmetry/antisymmetry, Yukawa nulls, gamma0 limit, sterile singlet decoupling and `F -> 0` reduction to corrected baseline. If a surviving required term needs new master integrals, use already verified tools (FormCalc, Mathematica/FORM, MaRTIn, pySecDec) selectively with reproducible code; don't invent integrals or drop a graph to meet a deadline.
11. Compare numerically at real model-consistent neutrino-fit inputs (NO and IO if available and valid) *without treating model-acceptance failures as amplitude failures*. Neutral Yukawa correlations must come from the frozen neutrino reconstruction. Record external chirality and finite neutrino-mass approximations explicitly.

## PHASE IV — End-to-end coherent radiative dipoles, validation and publication deliverables

12. Implement `research/wgamma_d16/zee_two_loop.py` (or equivalent) with separate complex `C_L,C_R` arrays/ledgers tagged by gauge-invariant class and exactly one coherent sum. Use source-derived conversion `C=-c/(8 pi² v²)` for the corrected general 2HDM coefficient and D15 `K2=-conj(C)` matching. Include all existing frozen one-loop, 9 fermion/photon species and 2 charged-scalar/photon contributions **exactly once**, and add only proven new electroweak contributions. Guard explicitly against summing authors' full 2HDM expression on top of these overlaps.
13. Evaluate `mu->e gamma`, `tau->e gamma`, `tau->mu gamma` branching ratios with the frozen rate convention, mass/phase-space inputs and any justified approximation error. Demonstrate coherent destructive/constructive interference. Report relative size of the new Zee-specific correction at representative actual scalar+neutrino points. This is **radiative dipoles only**, not complete LFV/global exclusion.
14. Establish a full scoped acceptance matrix: all nonzero diagram classes accounted for; signed tensor and native-vertex traceability; 2HDM common limit; unmixed singlet HZ limit; high-mass decoupling; mixing/charged-basis invariance; CP and complex chirality transforms; `F=0` null; reverse ordered amplitude; UV/ST/Ward and gauge parameter tests; independent numerical precision and uncertainty propagation. Include internal complex Wilson comparisons, not only rates. Use physically distinct masses/angles, plus amplitude fixtures with separately recorded BFB/unitarity/EWPO/vacuum status.
15. Make a reproducible, isolated CLI returning per-class complex coefficients, total, branching ratios, provenance, numerical errors and **explicit gates**. If and only if every required amplitude class passes, mark `ZEE_TWO_LOOP_RADIATIVE_LFV_PASS` for the specified approximation; do **not** mark `COMPLETE_ZEE_LFV_PASS` or `GLOBAL_ZEE_ALLOWED`. If any needed class remains blocked, its complex contribution must stay null and the purported *full* two-loop total must remain unavailable; validated *class-only* coefficients can still be returned individually.
16. Produce the calculation-facing research notes under `research/wgamma_d16/`: `ZEE_TWO_LOOP_DERIVATION.md`, `GAUGE_COMPLETION_LEDGER.md`, `BENCHMARK_CLOSURE.md`, compact evidence JSON, tests and exact source hashes. Include paper-ready LaTeX formulas and a topology/overlap table. Preserve the historic 2HDM author `HW` expected failure and source provenance; leave the external repo unchanged.
17. Once scoped complete, produce an **opt-in D14 overlay / integration proposal in research/**, with dry-run acceptance/branch-guard tests. **Do not edit or overwrite frozen Modules 0–14**, their historical frozen snapshots, the Zee Lagrangian or D15, and do not merge to main. Future module unfreeze/merge requires separate authorization.

## Autonomous execution instructions

- This is a **single multi-phase assignment**. Do not stop to ask for the next small task after finishing mixed HZ, after the first W check, after one F case, or after making a status document. Continue through Phases I → IV as evidence allows, debugging failures and executing additional necessary calculations in the same working branch.
- Prioritize *complete gauge-invariant classes* and exploit the corrected 2025/2026 general-2HDM implementation rather than recalculate already validated masters. Work on actual amplitudes first; notes summarize verified results after computations.
- Before declaring a missing term irreducibly blocked, attempt a concrete analytical and numerical reduction with the available local packages; document minimal failing integrand, source/diagram ID, attempted methods, and an executable falsifier. Never claim a cancellation by construction or fill a missing amplitude with zero/null while claiming complete.
- Commit/push verified progress in logically named milestones but **do not stop after pushing**. Keep all new code under `research/wgamma_d16/` and generated logs in ignored `local/`; preserve a clean branch at the end. Run focused tests and independent benchmarks rather than a huge unrelated revalidation.
- If a step is genuinely irreducibly blocked in the available environment, continue other independent phases where physics-valid and report precisely what remains blocked; **never fabricate a full PASS**. If no further valid progress is possible, conclude with the largest validated subset, its exact scope and minimum technical blocker rather than a generic unfinished-work summary.
- Do not run a broad parameter scan or claim phenomenological exclusions until radiative amplitude scope is validated; external `mu->e gamma` limits and complete LFV global fit belong to later scan stages.

**End state sought:** a source-pinned, analytically and numerically validated, gauge-invariant *Zee-specific leading two-loop radiative LFV* engine that reproduces corrected full general-2HDM in the strict singlet-free limit and shows the additional charged-singlet/mixed/F terms coherently without double counting.


---

## POST-`dade0f9` CONTINUATION — finish the original master task, do not reset

**Latest scientific progress:** `dade0f960a01d81aa6f53ec3e06326a015f3fa0d`.

Read `ZEE_TWO_LOOP_DERIVATION.md`, `MIXED_HZ_DERIVATION.md`, `GAUGE_COMPLETION_LEDGER.md`, `BENCHMARK_CLOSURE.md`, `zee_two_loop.py`, `w_outer_reduction.py`, and `f_current_probe.py` **before further work**.

### Already established; preserve rather than redoing
- Native unequal-mass physical charged-scalar Zγ radiative-current subset, associated off-shell Z/G0 identity, 64 native checks and complex L/R benchmarks. This is **not the full potential-mediated reducible Z sector**. The full mixing/LSZ assignment remains UNKNOWN.
- Neutral-fermion Zγ nine-species leading-expansion class; independently evaluated radial functions and source-matched signs. Light-quark perturbative numerics are explicitly illustrative.
- The quadratic `FD` zero claim is conditional on the *fermion-only* spurion U(1), massless internal neutrino limit, and quadratic Yukawa truncation. Keep those assumptions explicit; do not extend the zero to finite Majorana masses or higher Yukawa order.
- A nonzero, UV-divergent gauge-dependent `F†F` neutrino self-energy subgraph with a finite nonlocal form factor; it is not a physical two-loop dipole.
- Four actual NO/IO Module2 inverse witnesses, 70 nonduplicated *available* amplitude rows per channel, guarded partial rates; all full `C_L,C_R` and `full_BR` remain null.
- The corrected 39-channel general-2HDM baseline, HW correction and previous D15 proofs remain frozen. Do not rerun full historical calculations in each new iteration.

### PRIORITY A: actual complete `W` two-loop open-Dirac master reduction

1. Start from `w_outer_reduction.reduce_denominators()` and the native `parent_integrals.exact_parent_integrand()` with **both independent external momenta** `p,q`. Implement the **full numerator Taylor expansion and dipole projection** in `d=4−2ε`; denominator reduction alone is not adequate. Contract on-shell spinors and project the two genuinely independent complex chiral coefficients, retaining external unequal-mass order and `σ^{μν}` normalization.
2. Derive the complete set of two-loop vacuum/sunset integrals with numerator scalar products `l²,r²,l·r,l·p,l·q,r·p,r·q`. Use analytic IBP reduction (e.g. a locally available validated FORM/Mathematica reduction or Kira/LiteRed/FIRE if installed; search/validate tools **before** writing another homegrown entire solver). Treat repeated propagators, overlapping UV subdivergences and `O(ε)` terms consistently. Validate individual master integrals independently at nonexceptional Euclidean masses using numerical sector decomposition or Feynman parameters; include pole and finite parts, not just numbers.
3. Produce at least one signed nonzero `C_L,C_R` for a **fully dimensionally regulated two-loop parent topology**, tagged `TOPOLOGY_ONLY`, as a mathematical milestone. Then calculate **all crossed scalar placements, charged H1/H2 W/G derivatives, W/G species, non-Barr–Zee pinch, BRST/ghost and LSZ/counterterm partners** required for the same renormalized physical amplitude. Do not stop after the first topology.
4. Evaluate the **complete** two-loop W-class sum at `ξ=0.5,1,3` and two genuinely different complex LFV inputs. Verify independently computed UV, ST and ξ cancellations, signed electron/muon magnetic moment or published general-2HDM limits, and decoupled-singlet reduction. Do not infer missing diagrams from a compensator or fit a published kernel. Record numerical uncertainty of the cancellation and applicable truncation.
5. Use the corrected gauge-invariant common-2HDM aggregate only as a **matched complete-class** reference; never rescale the entire bosonic result by charged mixing or append already frozen photon terms again.

### PRIORITY B: `F†F` gauge/renormalization closure

6. From the actual nonlocal W-neutrino self-energy form factor in `ZEE_TWO_LOOP_DERIVATION.md`, generate **the complete charged-scalar/neutrino emission and insertion diagrams**, both internal/external photon attachments, Goldstones, physical H1/H2 with F/mixing weights, counterterms and external wave-function/LSZ diagrams. Define a renormalization and neutrino-mass scheme, including which diagrams are two-loop 1PI versus reducible terms. Do not treat isolated self-energy `1/ε` as a physical Wilson coefficient.
7. Reduce and integrate the complete two-loop F†F set in the **same** operator and expansion. Independently check `F→0`, nonzero antisymmetric F textures, charged mass degeneracies, mixing phases/signs, reverse ordering, lepton rephasing, UV/ξ cancellation and matching to the frozen one-loop F†F component without double counting.
8. If any massless-Majorana-neutrino or chiral selection identity makes a specific family vanish, prove it diagrammatically and with spinor algebra, not merely from a single contracted numerator. Preserve all nonzero diagram classes.

### PRIORITY C: complete the remaining mixed Z/potential/current scope

9. Resolve the explicitly **unassigned neutral mixing/reducible sector** in `MIXED_HZ_DERIVATION.md`; integrate or prove zero for A–Z/G0 two-point and A–G±–H± source terms required by the complete class. Verify they do not overlap with W/Goldstone/LSZ sector. Test physical S-matrix gauge independence, not only radiative current-tensor transversality.
10. Complete the mixed physical H1/H2 potential-W and charged-fermion-W gauge-invariant classes, with correct nondegenerate charged masses and off-diagonal neutral trilinears. Isolate new Zee terms via independently matched complete-class subtraction against the corrected 2HDM limit; use known validated master functions only where their extension is mathematically justified.

### PRIORITY D: guarded full interface and finish

11. After and only after every required class is computed or **proved absent** at the declared order, combine all coherent complex `C_L,C_R` with frozen one loop and validated photon/Z classes once; test `μ→eγ`, `τ→eγ`, `τ→μγ`, reverse order, rate normalizations, and physical benchmark errors. Compare full predictions only after all required terms exist. Full gauge passes must include both chiralities for independent NO/IO and spectrum witnesses.
12. Preserve the current guarded `zee_two_loop.py` behavior while any class is missing: `full_two_loop_C_LR=null`, `full_C_LR=null`, `full_BR=null`, `acceptance=false`. The available 70-row *included-only* numbers are diagnostics, **not physical exclusion predictions**. Never promote a radiative-current subset to a complete electroweak amplitude without checking reducible diagrams.
13. Update derivation/tests/evidence **after** each actual physics calculation. Keep a concise topology/IBP ledger listing explicit diagram/momentum/numerator, integral family, UV/finite, ξ, physical chiral coefficients, calculated/blocked and error, and source hash. Commit verified milestones but **continue automatically through all priorities**; do not stop after generating another summary or after a successful commit.
14. Where a full analytic two-loop reduction truly cannot be obtained, give exact failed tool method, source-derived minimal integrand and a reproducible failing numerical/analytic test. Continue other independent gauge-complete classes that are tractable. Never declare `ZEE_TWO_LOOP_RADIATIVE_LFV_PASS` without full proof, but **do not downgrade the assignment to only a smaller status task**.

**The next decisive result is not another 70-row ledger. It is an independently dimensionally regulated two-loop open-Dirac parent Wilson contribution, followed by its full W/charged/BRST/LSZ gauge completion, and the distinct nonzero F†F gauge sum.**
