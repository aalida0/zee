# Critical source rescue — published 2021 Zee mixed charged-scalar Zgamma and bounded tau-tau signals

**Branch:** `research/zee-full-constraints`.
**Starting report:** `f30131a08b947bc8c95d3c4d31881da0d1ea7f09`.
**NO NEW SCANS OR SCALAR PROPOSALS. NO BROAD MG5/CONDOR.**
**Priority:** Recover already-published Zee-specific one-loop formulas, validate their applicability, and quantify what remains missing; do NOT restart an open-ended custom one-loop derivation.

## 2026-11-07 citation-network correction — THREE published sources, not just one

The source-first survey `research/full_constraints/LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md` identified a **pre-2021 Zee-specific** off-diagonal charged-scalar result:

- **Trương Tín Thành, Lâm Thị Thanh Phương, Trịnh Thị Hồng and Huỳnh Lê Tuyết Mai**, *Bổ đính bậc một vòng cho quá trình rã h→Zγ trong mô hình Zee*, *Tạp chí Khoa học*, issue 37 (04/2019), pp.78–84. Eq.(1.12) and Table 2: off-diagonal Z scalar currents. Eq.(1.17), Table 4: i,j summed mixed charged scalar PV form factor. Figure 2 includes nondegenerate m(h1)=0.5 m(h2). It does **not** print full LoopTools PV arguments/seagull or independent Ward checks. Treat as **earlier calculation/reference only**.
- **Hue et al.**, *EPJC 78 (2018) 885*, doi:10.1140/epjc/s10052-018-6349-0, Eq.(16) and Appendix A: generic unequal-mass CP-even scalar PV form factor with documented mass arguments and charge orientation. Use for an independent kernel and normalization check.
- **Florentino/Romão/Silva (2021)** Eq.(D.20): specific Zee off-diagonal B0/C0 formula. Audit printed loop normalization and mass variables; no unproved generalization to CP-odd A.

**Mandatory gate:** compare all three sources in common signed SARAH physical conventions, first for h125 on frozen D7/F13 cards. If their conventions or PV routing disagree, record explicit derivations and controlled tests before claiming `hZgamma` physical. Extend to CP-even H only after h passes; CP-odd A is a distinct chiral/CP form-factor calculation, not obtained by replacing an external mass in a CP-even formula. Do not misrepresent the 2019 result as a fully gauge-validated independent code output.

## New, material literature finding — must inspect FIRST

The 2021 **Florentino, Romão & Silva** paper, *Off diagonal charged scalar couplings with the Z boson: Zee-type models as an example*, **EPJC 81, 1148 (2021)**, DOI `10.1140/epjc/s10052-021-09956-2`, contains a model-generalized calculation of
`phi → Z γ` including *unequal charged scalar mass eigenstates*:
- **Appendix D.3 Eq. (D.20)** explicitly gives the double sum over charged scalars with both diagonal and off-diagonal `Z H_i^+ H_j^-` couplings and the relevant `B0` and `C0` Passarino–Veltman functions.
- **Appendix D.1–D.2** fermion and W-gauge contributions; **D.4** total width formula.
- This exact article is the **same Zee charged-scalar/cascade reference already used in the project**; previous reports incorrectly characterized the *entire* mixed-state Zgamma amplitude as unavailable, whereas a published scalar-loop amplitude is available. This published expression is a *reference to validate*, not automatic proof of implementation accuracy.
- HTML source: `https://link.springer.com/article/10.1140/epjc/s10052-021-09956-2` (Appendix D, Eq.D.20).
- The paper's convention for its charged mixing `U†U`, scalar trilinear `g^{2ij}`, and `v` **must be reconciled with our native signed SARAH** `G_ij`, `Z_ij` and `Q=I`. The printed article contains potentially ambiguous mass/tau and width prefactors in adjacent expressions: **audit dimensions and compare to 2HDMC/independent standard one-state limits**; do not blindly transcribe any typo.
- Native D7 and F13 H trilinear mixed factors `G12 Z21` are nonzero. For A, restricted-model off-diagonal and diagonal couplings must be computed explicitly, not assumed from generic CP assignments. A fermion `Zγ` contribution remains, even if charged-scalar amplitude vanishes.

## Phase I — Implement and independently validate full one-loop phi→Zγ on ORIGINAL D7/F13

1. Read
`research/full_constraints/HIGGS_NEUTRAL_WIDTH_SEARCH_REPORT.md`,
`HIGGS_COVERAGE.md`,
`higgs/NEUTRAL_WIDTH_EVIDENCE.json`,
`higgs/neutral_widths.py`,
`higgs/diphoton.py`,
frozen physical cards/model vertices.
2. Derive Eq.D.20 input dictionary from exact native scalar trilinears and charged `Z` generator; match ordered `ij` sums, both scalar triangle permutations, contact/seagull terms and mass convention. Treat `m_i=m_j`, mixing endpoints and heavy scalar decoupling. Preserve complex absorptive parts for heavy H/A above threshold.
3. Implement source-pinned `B0(q²,m_i²,m_j²)` differences and `C0(MZ²,0,Mphi²,...)` via an **independent stable method** (public standard PV code if compatible, plus numerically independent 1D/2D Feynman parameters or second library). Check UV cancellation, electromagnetic Ward, photon transversality, Bose where applicable, charge and mixing symmetry, equal-mass diagonal 2HDM limit and at least one known published check/curve from the 2021 paper. Avoid unreliable generic numeric integrals at thresholds without documented contour/imaginary prescription.
4. Evaluate **complete one-loop** `h125, H, A → Zγ` W, all charged fermion, and **both mixed physical charged-scalar** sectors for D7 and F13 using a common declared physical input/scheme. For CP-odd A, include its general complex charged-lepton Yukawas consistently; if paper's fermion formula assumes diagonal CP structure, derive the correct independent scalar/pseudoscalar decomposition and check analytically. Do not import a plain 2HDM total.
5. Independently confirm the overall width/normalization against a known SM / one-charged 2HDM prediction. Output each complex signed sector and final partial width with source hash. Numerical agreement with 2 implementations is a code error only, not a theory sigma.
6. If any of the above fails (published convention ambiguity, missing gauge term, independent PV disagreement) keep `Zgamma=UNKNOWN`, document a precisely localized blocker. **Do not call the computed amplitude complete until every material one-loop sector is validated.**

## Phase II — Materiality-first width closure, without inventing exhaustive higher orders

1. Reuse exact D7/F13 known disjoint sums: D7 H/A = 11.9585831695/18.5677788929 GeV; F13 H/A = 2.25626947016/7.78229418104 GeV. Those are known *lower bounds* on total widths at the stated mixed-order width accuracy, not physical totals.
2. Add validated Zgamma only after Phase I. For remaining `A→WW/ZZ` loop, off-shell `H/A→H_i W^* / H_i^* W` tails, closed charged-pair virtual rates, finite-daughter widths, and nonresonant channels, obtain **independently justified per-card numerical contributions or rigorous/controlled upper bounds** at stated approximation order. Reconcile subtraction of the already counted on-shell channels to avoid double counting. Source-proven forbidden channels may be set to zero; unknown channels must not.
3. Compare each omitted contribution or certified bound to Γ_known and required precision for the **selected observable** `BR(phi→tau tau)`; do not require a complete all-order total width if effects can be shown quantitatively immaterial. Define a transparent *observable-specific* uncertainty tolerance from experimental likelihood/width model, not from arbitrary private percentages.
4. Consider a rigorous **conservative signal upper bound** even while Γ_total is unknown: since disjoint physical widths are nonnegative and Γ_total≥Γ_known, `BR_tau ≤ Γ_tau/Γ_known`, thus `(σ×BR)_upper ≤ σ_upper × Γ_tau/Γ_known` under source-qualified production/acceptance/width assumptions. This may establish **not excluded by that specific search** if the bound lies below its 95%-CL threshold everywhere. It cannot establish an exclusion, a complete BR or global allowedness. Test input assumptions, production uncertainties and multi-state combination.
5. The selected `ATLAS 2002.12223` analysis (HiggsBounds ID 200212223) uses **2D likelihood in ggF/bbH production**, not a single simple upper-limit curve. Dataset process and HiggsBounds runtime must be matched exactly. Its HiggsTools source includes approximate mass resolution (`relative=0.15`, `absolute=5` according to published format), and the original HiggsBounds reference documents approximate overlapping Higgs treatment, so assess D7 nearly degenerate H/A correctly, not as independent isolated exclusion curves. Cite HiggsBounds-5 paper and actual pinned JSON; the experimental analysis assumes narrow resonances, ggF Powheg and bbH MG5 aMC@NLO. There is no general guarantee that LO SusHi predictions transfer acceptances/line shape.
6. If complete physical Γ_tau / Γ_total and acceptance cannot be validated, **do not feed invented BRs** to HiggsTools. Retain `HIGGS_SCOPED_SEARCH_BLOCKED` and show precise remaining effects and an upper-bound diagnostic only with all stated assumptions. Do not fabricate tau-tau 95% CL numbers.

## Phase III — Deliverables and strict stopping criterion

- `research/full_constraints/HIGGS_ZGAMMA_2021_RESCUE.md` containing explicit derivation of 2021 Eq.D.20 ↔ SARAH matrices, published source citation, formula/typo audit, independent PV validation and numerical h/H/A widths on only original two cards.
- `research/full_constraints/higgs/zgamma.py` plus source-locked tests and execution evidence **only if validation succeeds**.
- `research/full_constraints/HIGGS_TAUTAU_MATERIALITY.md` with channel-specific missing widths/upper bounds and ATLAS ID 200212223 likelihood/overlap assumptions; if a quantified bound is not feasible, exact specialist input request rather than another custom two-loop project.
- Update `HIGGS_COVERAGE.md`, `VALIDATION_MATRIX.json`, `PROGRESS_TO_FINAL_SCAN.md` only for **passed** gates; B/LFV unchanged.
- Tests: paper 2HDM/SM limits, alternative integral representation, nonzero mixed-state effects, sign-flip/order, UV/EM Ward, thresholds, receipt hashes, missing→zero falsifier. Preserve original historical modules and native receipts. `git diff --check`, commit and push research branch only.

**Stop after this bounded source-backed one-loop rescue and materiality assessment.** A demonstrated narrow scoped tau-tau result is success; an exact amplitude mismatch or unbounded acceptance/width stopping barrier is a justified BLOCK, not grounds for several more months of infrastructure. No new parameter points, random scans, Condor, broad MG5 or final scan authorization.
