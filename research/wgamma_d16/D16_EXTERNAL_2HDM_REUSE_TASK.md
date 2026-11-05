# D16 rescue: use the published gauge-complete general-2HDM LFV calculation first

## Key primary reference (identified 2026-11-05)

**W. Altmannshofer, B. Assi, J. Brod, N. Hamer, J. Julio, P. Uttayarat, D. Volkov,**
*Electron EDM and Γ(μ→eγ) in the 2HDM*, JHEP 06 (2025) 156, **arXiv:2410.17313**.
**MANDATORY ERRATUM** JHEP 07 (2026) 184, published 2026-07-21, correcting LFV equations (5.7) and (5.8) in earlier versions.
Public Python repository: **https://gitlab.com/jbrod/general-2hdm-pheno**. GitLab displayed most recent commit **b5035cd5** (“Corrected further errors in l -> l' gamma Wilson coefficients”) when researched 2026-11-05; verify full hash, commit date, current HEAD, and changes in the cloned source rather than assuming an abbreviation pins everything.

The paper reports a **complete leading two-loop calculation** for radiative LFV in the unconstrained 2HDM with general complex Yukawas. It uses generalized Rξ gauge, verifies gauge independence and highlights the necessity of charged-Higgs diagrams for gauge-independent bosonic contributions. Its diagrams were generated using qgraf, calculated with MaRTIn/FORM, and the paper specifies background-field gauge for simpler electroweak calculations.

## Why this fundamentally changes D16

Our old workflow independently integrated 26 gauge-sector inner diagrams, but has not completed the two-loop outer/parent/charged/LSZ gauge-invariant combination. The published work already derives the **2HDM** gauge-complete answer including charged physical scalars. It should be the first implementation/reference to test; do not continue a bespoke two-loop outer integration before performing the following feasibility/overlap audit.

The Zee model includes a charged singlet with physical H1± and H2± and additional antisymmetric F Yukawas. Therefore, the publication is **NOT** a validated full Zee-model LFV backend. We must identify precisely which two-loop diagrams transfer unchanged and which require additional charged-singlet/mixed charged-scalar computations, including potential-specific trilinears. Never naively sum two copies of the full 2HDM result or rescale the entire gauge-invariant set by cos²γ/sin²γ.

## Phase A — reproduce CORRECTED author implementation (smallest task)

1. Clone the author repo in ignored `research/wgamma_d16/local/general-2hdm-pheno` or separate external directory (never vendor unreviewed large copies into main branch). Record full commit SHA, license, code versions, python/scipy/numpy versions, historical LFV correction commits, paper's 2026 erratum and any relevant changed equations. Pin the tested reference.
2. Run author-provided `example.py` and at least two independent complex LFV configurations, extracting **complex two-loop dipole coefficients** and the coherent rates separately if accessible. If only rates are public, inspect the code to locate the actual coefficient functions without modifying the author copy; do not claim signed complex amplitude validation from positive rates.
3. Read 2025 paper sections 3, 4, 5 (especially gauge/kinetic and charged-sector contributions, equations 5.9–5.19 and 2016/2026 errata as appropriate), its complete diagram definitions and 2026 correction. Establish observable and Wilson normalization, lepton label conventions, γ-matrix/σ/e signs, weak input scheme, mixing angles, complex conjugations and external masses. Derive an analytic mapping to frozen D15/Module4; verify at least two independent complex-chiral test inputs. Preserve physical rates only as cross-check.
4. Write `EXTERNAL_2HDM_BASELINE.md` and an executable, minimal test. If repo changed after 2026 erratum, establish that code actually incorporates the correction; do not rely solely on dates.

## Phase B — prove the strict general-2HDM limit of our Zee model

5. Construct a mathematically consistent *formal amplitude comparison* with the charged singlet decoupled and no antisymmetric singlet Yukawas: e.g. F=0, vanishing charged doublet-singlet mixing γ (specify convention), suppress singlet-mediated couplings and make sure extra singlet scalar-potential interactions do not feed the targeted amplitudes. This is not a neutrino-fit benchmark; do not call it an allowed Zee point.
6. Map h/H/A masses and mixing, all neutral/charged Yukawas, electroweak inputs, charged mass m_H± and potential trilinears to the paper's Higgs-basis general-2HDM parameters (ρ^l/u/d, q_ki, Z_i as needed). The 2025 code uses generic 2HDM, not a Type-II-only texture; match our *general complex* D, quark Type-II restriction and CP-conserving neutral sector without inventing charged scalar couplings. Independently check the generated SARAH vertices for this strict limit.
7. Compare **each accessible gauge-invariant group** in the authors' 2HDM calculation (one-loop, fermion/photon, full bosonic gauge+charged set, potential/charged set) with our frozen validated scalar one-loop and 2-loop subsets. Define a double-counting ledger. Do **not** compare separately gauge-dependent W kernels or infer a gauge-invariant W-only coefficient where authors only supply a gauge-invariant sum.
8. Test complex L and R with phases, the authors' `Gamma_l_to_lp_gamma` / Wilson rate conversions, null/decoupling limits and m_H± dependence; preserve all unmatched differences with exact minimal inputs and source locations.

## Phase C — classify the *new Zee-specific* two-loop correction

9. Inventory all diagrams in our D16 calculation that survive once charged singlet/mixing and F are nonzero, versus the full 2HDM classes in the paper. Include physical H1/H2 currents, mixing-weighted W couplings, diagonal and off-diagonal charged trilinears, ghost/gauge-fixing parents, and any new charged F Yukawa classes. Mark each `2HDM_COMMON`, `ZEE_EXTENSION_REQUIRED`, `VANISHES_PROVED`, `OUT_OF_SCOPE`.
10. Propose a subtraction/matching strategy `C_Zee = C_2HDM(reference overlap) + ΔC_Zee(singlet/mixing)` only if the overlapping gauge-invariant class is **proved** and the remaining correction is itself gauge-independent or gauge-completed. Do not subtract gauge-dependent bare W kernels or pretend the extra singlet pieces are automatically finite.
11. Use our 26 independently calculated inner diagrams and 8 parent subloops to verify transferable tensor pieces and new mixing terms, but avoid rerunning giant integrations unless needed. Prioritize validating the **full gauge-independent 2HDM limit against the authors' code** before generalizing.
12. If actual new Zee two-loop integrals remain, consider **MaRTIn** (https://gitlab.com/manstam/martin, qgraf+FORM, external-momentum expansion) or **pySecDec** (https://github.com/secdec-research/secdec, regulated master integrals), both for specific unmatched diagrams, not as blind replacements for the proven author's analytic answer.

## Reports, safety and branch

- First deliverable: **PASS/FAIL/BLOCKED** reference-code reproduction + source-pinned **exact** 2HDM-limit coefficient comparison. This may allow D16 strategy to change before further custom work.
- Secondary: full 2HDM-vs-Zee diagram/parameter mapping and a sharply delimited list of actual missing Zee-only terms; precise next derivation for those terms.
- Preserve `matching.py` with physical `C_L=C_R=null` and `coherent_inclusion=false` until **Zee-specific** gauge-complete matching passes. Author's 2HDM code alone is NOT `WGAMMA_GAUGE_MATCHING_PASS` for Zee.
- Keep all work under `research/wgamma_d16/` and ignored `local/`; no modification to frozen Modules0–14 or D15, no D14 integration, no large scan.
- If the author code cannot be fetched on a restricted worker, record exact network/access diagnostics and use a user-supplied archive or a functioning machine; do not fake source code or silently substitute 2025 equations that the 2026 erratum corrected.
- Commit and push verified progress to `research/zee-d16-wgamma-gauge-matching`, including exact source citations and provenance.

**Highest-priority action: download and execute the corrected public implementation on two relevant 2HDM benchmarks.**
