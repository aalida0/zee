# Independent critical referee review — Type-II-quark Zee charged-scalar cascade phenomenology

**Audit freeze:** 11 November 2026  
**Target:** a credible, ordinary phenomenology manuscript (e.g. EPJC), *not* a new NNLO precision calculation  
**Code branch:** `research/zee-full-constraints`; frozen original model/scan modules and `main` unchanged.

## Referee recommendation: **MAJOR REVISION**, not ready to submit as a fully constrained scan

A conditional, numerical study can be written now, and the program is substantially advanced. But a manuscript advertised as a new **fully allowed Zee scan with HL-LHC discovery/exclusion reach** would not survive rigorous review, because the analyzed scalar and lepton families are **selected**, important independent Higgs/LFV constraints are **not evaluated on the new cards**, and theoretical production uncertainties are **unmeasured**.

There is no need to calculate a new complete three-loop B amplitude, derive every electroweak two-loop LFV tensor, or perform detector-level ATLAS simulation to produce a reasonable paper. There **is** a need to describe a reproducible perturbative approximation, consistently classify missing leading constraints, demonstrate the physics advance beyond 2017/2021/2023, and limit collider claims to what the generated samples support.

## 1. Closest published prior art — reject obvious novelty claims

| Source | What was already done | What might be new in our restricted calculation |
|---|---|---|
| Herrero-García, Ohlsson, Riad, Wirén, **JHEP 04 (2017) 130**, https://arxiv.org/abs/1701.05345 | Full *general* Zee scan, one-loop neutrino masses, LFV including tri-lepton and conversion, Higgs LFV and EW/heavy scalar effects. | They did not present a dedicated 13/14 TeV LO `tbH2→tbH1Z` production/cascade map tied to these Yukawa textures. An intersection of their flavor coverage with our scalar/collider rates could be new **if actually demonstrated**. |
| Florentino, Romão, Silva, **EPJC 81 (2021) 1148**, https://arxiv.org/abs/2106.08332 | **Same** `H2±→H1±Z` mechanism, Zee Type-II quark/scalar truncation, B→Xsγ, h→Zγ, direct scalar searches, tree-level benchmarks. **Explicitly excludes neutrino oscillation / lepton flavor sector** (Sec III). | A source-matched analysis incorporating actual neutrino-compatible lepton Yukawas and a collider-rate map beyond their scalar-only benchmarks is plausible. Not the decay mechanism or basic mixing coupling. |
| Heeck and Thapa, **PLB 841 (2023) 137910**, https://arxiv.org/abs/2303.13383 | Explicit analytic general Zee neutrino inverse and LFV-suppressing flavor-texture zero constructions, targeted perturbations and broad scans. | Combining a *specified* subset of these textures with 2021 cascade scalar rates, physically qualified searches, and up-to-date flavor data. **Not** the existence of texture zeros or the pseudoinverse itself. |
| Barman, Dcruz, Thapa, **JHEP 03 (2022) 183**, https://arxiv.org/abs/2112.04523 | Neutrino-compatible Zee textures, scalar collider/low-energy constraints and g-2 phenomenology. | Show a different collider final state and a direct comparison with their benchmark assumptions. |
| Schmidt and Vandeleur, **JHEP 06 (2026) 006**, https://doi.org/10.1007/JHEP06(2026)006 | EFT running of Zee neutrino parameters and potential radiative instability of specific tuned benchmarks. | Test if local tuned neutrino textures are stable to variations/running; do not claim an exact symmetry or all-scale naturalness. |
| Degrande et al., **JHEP 10 (2015) 145**, https://doi.org/10.1007/JHEP10(2015)145 | Systematic 4FS vs 5FS charged-Higgs production at NLO(+PS), scheme and bottom-kinematic differences. | A clearly qualified *LO 5FS baseline* in our mixed Zee state. An NLO/4FS comparison requires actual generator results, not a generic K factor. |
| Misiak et al. (2026), https://arxiv.org/abs/2608.29863 | Updated B→Xsγ SM with **leading-NP** Eq.4 | Two mixed charged states matched coherently, tested against independent BMU/SuperIso and HEPfit source. This is an implementation input, **not** a new B result in the paper. |

The longer `research/full_constraints/LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md` reviews 27 source papers and is **not exhaustive**. The publication novelty audit must not claim no further relevant paper exists.

## 2. What is actually implemented and rerun now

All new scripts are isolated under
`research/full_constraints/pheno_paper_2026/`.
Their approximation scope is machine-readable in
`APPROXIMATIONS_REVIEW_REGISTRY.json` (**18 per-observable/method gates** including the 2015 4FS/5FS comparison and the missing heavy-Higgs exclusion).

**Source-locked calculation:**
- Exactly **16** original Zee scalar spectra with source-matched D10 sufficient *tree*-vacuum certificates, plus original tree BFB/unitarity/EWPO checks.
- The unchanged original MG5_aMC 3.6.7 5FS `gb→tH2` integration gives true **13 TeV LO** rates for all 16; it also gives independently integrated **14 TeV LO** rates for exactly **15591, 2264, 15673**. No rates interpolated to the remaining thirteen 14 TeV cards.
- **64 new** deliberately constructed neutrino-consistent Yukawa families, two orderings and two seeds per scalar. Actual complete on-shell tree D4 decay branching fractions are used with the scalar-specific actual production cross section. The full reconstructed 64-family source is regenerated in CI, not replaced by the historical four-family widths.
- The 2026 Misiak leading-new-physics B formula is applied to both charged scalar mixing fractions; source-defined Gaussian screening uses separate one-sided and two-sided confidence conventions (10/16 and 16/16 screened).
- Three spectra **11016, 14074, 15673** survive a *non-probabilistic* historical-method stress scenario. This is **not** a theory covariance or bound on omitted NNLO new-physics corrections.
- The public Higgs/LFV gate gives **64/64** selected one-loop/specific Barr–Zee dipole screens below MEG II, and direct h125 LFV partial-width materiality below published experimental thresholds, but **full LFV and heavy-Higgs exclusions remain UNKNOWN**.

**Actual CI:** 
- https://github.com/aalida0/zee/actions/runs/43103815814 (full 64 rebuilt, 16/3 MG5 source join, five tests and figures, successful).
- https://github.com/aalida0/zee/actions/runs/43104370522 (same with Z→ee+μμ branching and five tests, successful).
- https://github.com/aalida0/zee/actions/runs/43105830163 (checks fixed-scalar flavor-cascade differences; five tests, 64 cards, source actual collider join, successful).
- https://github.com/aalida0/zee/actions/runs/43105442361 (12 real scalar proposals, all five per-arm accounting tests and source-matched worker pass; **12/12 had scalar vacuum NOT_EVALUATED** because earlier scalar cuts already reject them; smoke test only).
- https://github.com/aalida0/zee/actions/runs/43106385178 (51 genuine local scalar evaluations around three original centers; tree gate and leading B check; three tests, successful).

### Benchmark table: 15673

| Observable | Actual result and scope |
|---|---:|
| mH1±, mH2± | 714.508, 1277.363 GeV |
| Heavy H, A masses | 1271.991, 1183.578 GeV |
| `σ13(pp→tbH2±)` | **2.9876 fb**, original 5FS LO |
| `σ14(pp→tbH2±)` | **4.2345 fb**, independently integrated 5FS LO |
| `BR(H2→H1Z)*BR(H1→tb)` | **0.3928266–0.3928373**, newly reconstructed four neutrino families, complete on-shell two-body tree widths |
| `σ14*BRcascade` | **1.663424–1.663470 fb** |
| Before Z/top decays, 3000 fb^-1 | **4990–4990 events**, raw |
| After Z→ee or μμ, before top decays/selections | **~335.8 events**, using PDG `BR_Zee+μμ=0.067294` |
| LO-NP B Eq4 Gaussian pull | **+1.25336** |
| One-sided + two-sided 95% *LO-NP Gaussian screen* | **inside both** |
| All three historical method differences treated adversarially | **survives this explicitly non-physical stress diagnostic** |
| Tree scalar 1%-scale perturbation pilot | **12 of 17 locally sampled cards** pass original tree theoretical gates and one-sided published-order B screen |
| Absolute collider exclusion / global Higgs / complete LFV | **NOT CERTIFIED** |

**Rate caveats:** the 14 TeV 4990 is *not* a detector-event yield, cannot be called an exclusion, and does not yet multiply top-decay branching fractions. The ~335.8 Z-dilepton figure still precedes top decays, reconstruction, kinematics, trigger, b tagging, backgrounds, pile-up, and analysis acceptance. A rate of N selected events would be `L σ BR_Z BR_tops ε_detector`, not `L σ` alone.

## 3. Most serious referee discovery: direct flavor effect on the collider branching rate is tiny

Holding the original scalar card fixed and comparing the source D14D four families with the independently constructed LFV-suppressed new families, the **maximum absolute fractional difference** in the tree `BR(H2→H1Z)*BR(H1→tb)` product (relative to the original-family mean) is:

| Scalar ID | Max source-observed fractional difference |
|---|---:|
| **15673** | **7.469671×10⁻⁴ = 0.07470%** |
| 15591 | 3.791975×10⁻⁴ = 0.03792% |
| 2264 | 2.719509×10⁻⁴ = 0.02720% |
| 14074 | 1.267904×10⁻³ = 0.12679% |

The source production rate is independent of the new lepton homogeneous coefficients at this quark-level order. Hence the tuned flavor textures **do not noticeably enhance this cascade at fixed scalar parameters**. This is expected physically: the gauge cascade coupling and dominant heavy-quark production/decay are controlled mostly by scalar mixing, masses, and Type-II quark Yukawas, not direct `e-μ` Yukawa entries.

**Referee objection, severity HIGH:** A statement that flavor-safe textures directly produce a substantial collider-rate enhancement would be **contradicted** by the computed examples. A stronger, testable paper claim is **allowed-region intersection**: the regions favored by scalar and flavor constraints may restrict the scalar mass/mixing combination that determines the cascade rate. That intersection has **not yet been established as a representative fully allowed scalar-space map**; the 16+64 cases are engineered examples and cannot show a global allowed volume. This must be the centerpiece of the next production scan, not rhetoric about an automatic flavor-collider correlation.

## 4. Reviewer objections ranked by scientific severity

### MAJOR / essential before an unqualified exclusion or globally viable benchmark

**M1 — Heavy neutral Higgs *observed exclusions* missing for the actual new flavor card; source tree widths now available.**
At 15673 the heavy H and A have masses ~1272 and 1184 GeV. A native source-matched **all-64 new Yukawa** on-shell tree two-body H/A width ledger was successfully executed (GitHub Actions 43107900340). For the 15673 NO seed-20261111 family the *known disjoint tree width sums* are 67.7062 GeV (H) and 52.1010 GeV (A), already **Γ_known/M=5.32% and 4.40%**, with source H1±W∓ fractions 60.22% and 49.81%, and tt fractions 39.31% and 50.03%. The **tree-level positive-denominator upper bounds** on BR(H→ττ), BR(A→ττ) are respectively 1.951×10^-8 and 6.975×10^-9. These are *not complete total widths*, not loop-/QCD-improved physical branching fractions, and without source-qualified pp→H/A production and the correct observed search category they are not an experimental limit. Existing SusHi external-production receipts still cover original D7/F13, not the new 15673 family. **Heavy H/A→H1W and tt observed searches are materially more relevant than ττ.** Missing channels must never be assigned zero, and h125 near-alignment alone is insufficient.

**M2 — Leading non-dipole LFV missing on new textures.**
The full native SARAH one-loop `mu→3e` and `mu-e` conversion operators have been validated only on **old D7/F13 flavor cards**, while the new 64 matrices are different. In the new set only coherent selected dipoles and neutral tree `mu3e` are computed; photon off-shell monopoles, box operators, Z penguins and coherent conversion nuclear matching could invalidate a subset. Gauge-complete Zee mixed two-loop LFV is not covered. With no numerical upper bound on *leading* omitted operators, the phrase “satisfies all LFV constraints” is unsupported.

**M3 — No representative final constraint application across scalar space.**
The original source series contains 225 already scalar-preselected workers, 33 vacuum PASS and 192 UNKNOWN, with 16 intersections of tree-vacuum PASS and nominal B-compatible; this is **not** an unbiased global model-space distribution. The 64 new neutrino families solve exact direct-zero constraints and are explicitly targeted; their 64/64 success says an algebraic construction exists, not that a fraction of general randomly chosen couplings survives. Do not pool overlapping prior arms. The independent `scan_accounting.py` accounts per arm and preserves FAIL/UNKNOWN/ERROR/unprocessed separately, with Wilson intervals that apply only to source-defined within-arm processed scalar pass proportions.

**M4 — Neither theoretical nor experimental HL-LHC reach yet computed.**
At 14 TeV genuine 5FS LO cross sections exist for three selected scalar spectra only. Scale/PDF bands, 4FS/NLO scheme validation, on-shell/off-shell cascade corrections and detector/background model are unquantified. `10` or `100` selected events can be discussed as illustrative required efficiencies, but cannot be presented as 95% CL exclusion or discovery. 2015 Degrande et al. explicitly study the 4FS/5FS NLO discrepancy and bottom-quark kinematics; **0.2% MC numerical error is not the theory uncertainty**.

**M5 — Neutrino mass priors and tuned textures.**
One-loop neutrino mass closure at NuFIT secondary best-fit is necessary but not a multi-observable oscillation likelihood and does not automatically impose cosmological `sum mnu`, `0nubb` or RG stability. Since the inverse algebraic flavor construction sets two complex Yukawa entries exactly to zero, demonstrate at least local robustness and disclose this as a flavor-texture **ansatz**; do not advertise naturalness or generic distributions. Existing 2023 literature has already derived strong texture suppressions.

### NEW heavy-neutral H/A tree decay pilot (source-checked)

A separate 64-family **full on-shell tree two-body** ledger now includes
six quark and six lepton channels, H→WW/ZZ/hh, A→hZ,
H/A→H1W/H2W (both charges) and open charged-scalar pairs with
source-checked scalar trilinears. Distinct physical channels are counted
once, finite thresholds and model Yukawas are retained, and any open
unimplemented on-shell neutral transition is flagged `MISSING_ON_SHELL`.
No physical total width or observed HiggsTools limit was inferred.

Source and tests:
`research/full_constraints/pheno_paper_2026/heavy_HA_tree_widths.py`,
`test_heavy_HA_tree_widths.py`, GitHub Actions:
https://github.com/aalida0/zee/actions/runs/43107900340
(3/3 structural tests, regenerated all 64 family cards, complete tree
width inventory PASS).

| Source scalar 15673 | H | A |
|---|---:|---:|
| Mass [GeV] | 1271.991 | 1183.578 |
| Sum of positive calculated tree partial widths [GeV] | 67.7062 | 52.1010 |
| tt fraction of tree sum | 39.31% | 50.03% |
| H1±W∓ fraction of tree sum (both charges) | **60.22%** | **49.81%** |
| Tree BR(ττ) upper bound by known positive sum | ≤1.951e-8 | ≤6.975e-9 |

**Referee implication:** The known tree-width sums alone imply Γ_known/M≈5.3% (H) and 4.4% (A), meaning a narrow-zero-width experimental limit could be inappropriate. Searching only H/A→ττ would miss the dominant
tree channel structure of this benchmark. Full rates for `H/A→H1W`
and `H/A→tt`, with production, QCD widths and actual limits, are the
priority for a credible scalar-exclusion statement.

### MEDIUM / publication quality and theory limitations

**m1 — SM and Higgs couplings.** The 64 h125 known-channel sums (e.g. ~4.12944 MeV for 15673) are *not* model total widths. Width-independent ratios are valid restricted diagnostics; no complete HiggsSignals/HiggsBounds 95% inference. These calculations may suffice as transparency checks in a carefully *conditional* rate/benchmark paper, but not a global constraint pass.

**m2 — B→Xsγ perturbative statistics.** Our 2026 Eq4 LO-NP calculation is explicitly recommended for generic near-SM BSM models. It is enough at a declared leading-NP order with method sensitivity, but the two-sided/one-sided Gaussian distinction matters: 15673 passes both, 15591 fails the one-sided. Do not try to convert a compiled 2025 SuperIso NLO rate and 2026 NNLO SM marginal error into a fake full physical likelihood. Do not impose the one-state Type-II 670-GeV exclusion on individual mixed eigenmasses.

**m3 — Potential constraints.** The D10 original global tree minimum sufficient certificate is strong *at those isolated source cards*. It does not establish the same property after RG or quantum corrections. UNKNOWN should be retained for cards not certified by the tree-only algorithm.

**m4 — Production normalization.** The source includes both H2 charge conjugates and both incoming beam orders once. Other processes, 4FS vs 5FS PDF differences, kinematic b-jet acceptance, EW corrections and scale variations are not included. Never add a standard 2HDM K-factor to the mixed Zee state without verifying the coupling structure and perturbative setup.

**m5 — Paper's novelty.** The 2021 article already reports the cascade, and the 2017+2023 articles already report flavor-safe Zee solutions. An EPJC referee will reasonably ask for a quantitatively demonstrated intersection and a genuinely new observable pattern not shown in those prior publications. A table of 16 hand-selected points plus raw 14 TeV events is not by itself conclusive novelty.

## 5. Implemented reproducible code (all on research branch)

- `APPROXIMATIONS_REVIEW_REGISTRY.json`: per-observable scope, literature justification and skeptical-referee objection (18 gates).
- `paper_gate.py`: strictly joins scalar+exact 13/14 source MG5 with newly computed 64-family D4, leading-NP B and null physics status. Outputs JSON, CSV and reviewer notes. New PDG Z-dilepton raw counts and per-source fixed-scalar flavor-impact numerics.
- `test_paper_gate.py`: five fail-closed source and numerical tests; reject missing/duplicate/tampered 64 source cards, unrealistic 14 TeV interpolation and global acceptance.
- `paper_figures.py`: source-label 13 TeV conditional rate vs mass; 3 genuine 13/14 rate comparison only.
- `scan_accounting.py`: preserves deterministic multi-arm proposal schedule and each denominator; distinguishes PASS/FAIL/UNKNOWN/ERROR and unknown experimental acceptance. Requires source scalar/config SHA.
- `test_scan_accounting.py`: five fail-closed synthetic fixture tests (fixtures explicitly not physical points).
- `local_scalar_neighborhood.py`: recomputes actual complete tree scalar gating and published leading-NP B on 51 source-centered points, without Yukawa/production transplants.
- `test_local_scalar_neighborhood.py`: three source/determinism/limited-prior tests.

**Executed CI:**
- https://github.com/aalida0/zee/actions/runs/43105830163 — all five paper tests, 64 families, tables and plots, PASS.
- https://github.com/aalida0/zee/actions/runs/43106385178 — 51 authentic bounded local scalar screens, three tests, PASS.
- https://github.com/aalida0/zee/actions/runs/43105442361 — 12 actual D14 scalar proposal/worker/accounting smoke tests, five tests, PASS. **12/12 proposals failed before vacuum**; should not be mistaken as a physics survey.

Most important local scalar results (**17 deterministic perturbations including original each**):
- 15673: 12 tree-scalar PASS, 1 vacuum UNKNOWN, 4 FAIL; **12/17** pass the one-sided *source-order B* screen plus original tree gates.
- 15591: 13 tree-scalar PASS, 4 vacuum UNKNOWN; **2/17** pass one-sided B screen plus tree gates.
- 14074: 11 tree-scalar PASS, 6 FAIL; **11/17** pass one-sided B screen plus tree gates.

This supports *local continuity* of the source-defined scalar/B screen at 15673, **not full model allowed volume**, since neutrino/LFV/Higgs and any new production are absent on changed scalar cards. It is a sensible small-sample proposal design check for a future real scan.

## 6. Minimum paper-size research still required — not a precision paper

1. **Choose final physics scope**. For a *conditional benchmark paper*, title/abstract and captions must be honest that full B/Higgs/LFV and detector-level exclusions are not claimed. For a paper advertising “allowed parameter space,” add proper heavy-Higgs and leading new-family 3-body LFV/conversion operator constraints before publishing.
2. **Validate a representative scan in the model's actual restricted domain** with two separate priors: broad control and production-targeted. Run enough accepted points for a stable distribution, accounting for rejected scalar proposals and different arm densities; show sensitivity to choice of prior and algebraic flavor texture ansatz. Do not turn 64 intentionally generated safe textures into a probability.
3. **Complete heavy H/A physical branching fractions and observed limits** for the shortlisted new spectra using public HiggsTools. The **tree on-shell channel ledger is now done for all 64**. Finish missing positive loop/QCD/off-shell contributions, production `pp→H/A` at the declared LO/NLO order, and observed `tt` and `H1W` limits (ττ is tree-suppressed for 15673). A modern all-orders H/A calculation is not necessary, but incomplete width sums cannot be normalized as BRs.
4. **Transfer existing one-loop `mu→3e` and `mu-e` conversion operators** to the actual new Yukawa cards with independent normalization checks. Do not restart negligible 2-loop gauge topology calculations unless leading materiality shows a risk.
5. **Add a leading production systematic study** at 14 TeV for 15673: 7-point `muR,muF` LO scale variations and at least PDF replicas or a 4FS/NLO comparison. These are ordinary pheno requirements, not a precision paper.
6. **Make the genuinely new plot**: source-defined *viable-scalar mass/mixing/cascade-rate intersection* under the chosen leading-order constraints. Compare with 2021 scalar-only ranges. If the intersection yields no nontrivial restriction or no new observable, change the hypothesis rather than overstate novelty.

## 7. An acceptable paper structure

**Working title (conditional):** *Neutrino-consistent flavor textures and charged-Higgs cascades in the Type-II-quark Zee model: a leading-order LHC study*.

**Proposed sections:** (i) constrained Zee scalar/quark/lepton conventions and neutrino inverse; (ii) declared perturbative-order constraints with approximation matrix; (iii) sampling methodology and cutflow with prior sensitivity; (iv) flavor-conditioned viable scalar/cascade rates and 2021 comparison; (v) actual 13/14 TeV rates and decay topologies; (vi) benchmark recommendations, theory uncertainties and falsifiable LHC follow-up; conclusions.

**Recommended benchmark now:** 15673, conditional at declared order (mH2=1277.36 GeV, sigma14 LO=4.2345 fb, ~1.66345 fb inclusive H1 tbZ cascade, ~336 raw Z-dilepton events at 3000 fb^-1). 15591 is yield-focused but fails the one-sided Gaussian B screen; 14074 has a good source-order B-screen but no actual 14 TeV integration. None has full Higgs and LFV 95% certification.

### Decision

**Paper hypothesis potentially publishable, current full-constraints/manuscript claim NOT ACCEPTED.** The numerical/implementation platform and paper figures are now credible **at a declared source-defined LO**. We should stop NNLO perfectionism but cannot stop short of materially relevant leading Higgs/LFV exclusions or call preselected examples globally allowed. The direct **0.03–0.08%** flavor dependence of the charged cascade branching ratio is a crucial negative result: do not build novelty around a nonexistent direct enhancement.

The objective is a *decisive intersection plot* and an honest rate/constraints analysis, not new loop integrals.
