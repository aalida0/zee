# ATLAS VBF h125 → bb: observable-specific materiality gate

**Decision: `H125_ABSOLUTE_MU_BLOCKED`.** The measurement needs control on
the MeV scale, not an assumed 40-keV completeness target. Nevertheless no
certified bound on the full signed missing width, or on its associated rate
uncertainty, was obtained from the inspected sources and existing fixed-card
implementations. Absolute model rates, μ, exclusions and theory σ remain null.
No HiggsSignals model call was made. This is an implementation/qualification
obstruction, not a claim that the amplitudes are unpublished or incalculable.

Only original D7/F13 NO/low_joint cards were inspected. The starting branch
was `fe35251`, with the width evidence from `654794f` retained unchanged.
Read AGENTS, the observable task, signal-strength/Zγ reports, execution and
coverage reports, and the literature rescue audit. B/LFV/vacuum work was not
restarted. Frozen calculations, inputs and branch remain untouched.

## Measurement and precision requirement

First set the operational question: can a **qualified rate interval**, including
signed width changes, numerator/reference uncertainty and acceptance bias, be
compared with this experiment's one-error endpoints? Do not require 1% accuracy
or choose a nuisance width to obtain agreement. The endpoint distances below
are the available budget with all other inputs fixed; several independent
missing contributions must share it. Endpoint containment is not a physical
PASS or a confidence construction for the model.

[ATLAS 2011.08280v2](https://arxiv.org/html/2011.08280v2),
DOI 10.1140/epjc/s10052-021-09192-8, sections 3, 7–9, Tables 4–6:
125-GeV signal templates, 13 TeV, 125.9 fb⁻¹ all-hadronic data combined with
the complementary VBF+photon analysis. The combined result is
μ=0.99 (+0.36/−0.34). This is a profiled signal-rate measurement; its discovery
significance of 2.9σ is not an exclusion of either Zee card. The 10-GeV
massResolution in the HS JSON is an assignment/resolution parameter, not
a physical Higgs width. A MeV-width resonance remains narrow relative to it.

HiggsTools 1.1.3 source `71a93a82f34fb120e3095460e52cb15b7bffcea0`,
HS dataset `3c6c2538d9ba0549ea0559cf9b38c18eb80c3af1`, exact ID
201108280, `h125/bb_vbfH_LHC13_ATLAS_126.json`, uses only `vbfH,bb`.
Its observation is **[1.41293909217521, 2.16, 2.94032044699598] pb**.
Inspected `JsonSupport.cpp:38–51` and `RateMeasurement.cpp::evaluate`:
missing `ref` defaults to the reference process rate, and model signal strength
is multiplied by it before comparing absolute rates. Source hashes were replayed.
Native SMHiggsEW gives **3.782 pb × 0.58238441 = 2.20257783862 pb**.
Thus the native normalized endpoints are **[0.641493375, 0.980669088,
1.334945079]**. Neither 2.16 nor the paper's slightly different nominal
reference is a replacement for this normalization.

For matched production and decay references,

`μ = RσVBF RΓbb ΓSM/ΓZee`.

Let S be the retained known-channel sum, Δ the signed change required to obtain
the physical total, and ε an aggregate multiplicative numerator/reference
change (a diagnostic variable, **not an assigned random error**). The directly
normalized rate diagnostic is

`r(Δ,ε) = 3.782 pb × RσVBF × Γbb/(S+Δ) × (1+ε)`.

This avoids substituting a common-order SM ledger for SMHiggsEW. That ledger
has BRbb=0.591951409, differing from native BRbb by a factor **1.016427293**.
Its conditional μ at Δ=0 would be 1.050318059/0.990202551. The corresponding
native rate diagnostics are below; **none is a physical model prediction**.

| Conditional diagnostic / endpoint budget | D7 | F13 |
| --- | ---: | ---: |
| S [MeV], not certified total | 4.280495766 | 4.005236276 |
| r(0,0) [pb] | 2.351410300 | 2.216826091 |
| μnative(0,0) | 1.067571942 | 1.006468898 |
| Signed Δ at upper one-error rate endpoint [MeV] | −0.857330837 | −0.985527222 |
| Signed Δ at lower one-error rate endpoint [MeV] | +2.843096390 | +2.278765862 |
| Multiplicative rate changes reaching endpoints, Δ=0 | −39.91%, +25.04% | −36.26%, +32.64% |
| Δ at upper/lower Gaussian 95% surrogate endpoints [MeV] | −1.552355172 / +10.185417248 | −1.598635652 / +8.755717233 |

The last row extrapolates the asymmetric errors by 1.959963985 solely as a
sensitivity diagnostic. The pinned JSON supplies no exact profiled 95% rate
interval. This surrogate is **not** an official ATLAS confidence interval,
a model exclusion, or a justification to cut on a Gaussian χ². The actual
profile likelihood/covariance would be required for such an interpretation.

[The curve](higgs/H125_VBF_BB_CONDITIONAL.png) and
[numeric evidence](higgs/H125_VBF_BB_MATERIALITY.json) show r(Δ,0) normalized
to the native reference. The bounded domain runs from minus the retained
WW+ZZ subtotal to the lower one-error crossing. It illustrates removal of
that subtotal through the measured sensitivity scale; it is not a width prior,
allowed interval, uncertainty band or parameter-space scan. Numerator errors
multiply each curve by 1+ε. No physical uncertainty is inferred from its range.

## What the existing inputs and published methods actually bound

All extra scalar masses exceed mh. For a heavy scalar of mass m and
0≤q²≤mh², the exact tree propagator satisfies

`|1/(m²−q²)| ≤ 1/(m²−mh²)`.

This is a genuine bound on one propagator, **not a decay-width bound**.
For H1 it is 1.358462820e−5 / 3.206936918e−6 GeV⁻² (D7/F13).
The worst relative difference from its leading contact value 1/m² is
21.226% / 5.011%. Values for all four masses are recorded in JSON. These
remainders concern a propagator, not the uncertainty on a full observable.
They are finite and vanish in the heavy-mass limit. The current coefficients,
spin/color/flavor sums and physical phase-space norm must still multiply them.

The actual native Frobenius norms are
`||F||=(1.62245309e−4,1.62245309e−3)` and
`||D||=(1.53644394e−3,1.24758682e−4)` for D7/F13.
They support investigating a conservative norm bound; they do not bound the
Type-II quark currents, Higgs trilinears, or full interfering amplitude by
themselves. No small-F/D estimate is promoted into a total-width error.

The source review was targeted and timeboxed, not an unrestricted loop search:

| Full text inspected | Exact result and applicable content | Transfer limitation |
| --- | --- | --- |
| [Bilenky–Santamaria, hep-ph/9310302v1](https://arxiv.org/abs/hep-ph/9310302), DOI 10.1016/0550-3213(94)90375-1 | Eqs. (3.8–3.11), (4.20–4.21): heavy unmixed charged singlet, antisymmetric LL coupling, gauge-invariant EFT through dimension six | The leading dimension-six four-lepton term has no physical Higgs insertion. Expanding (3.9) generates Higgs-dependent higher-dimensional terms. Neither a second doublet nor the full two-state scalar/current amplitude is supplied. Section 6 explicitly drops physical Higgs terms in its phenomenological reduction. |
| [Herrero-García et al., 1701.05345v2](https://arxiv.org/html/1701.05345v2), DOI 10.1007/JHEP04(2017)130 | Eqs. (65–67): mixed charged-scalar four-lepton operators with both doublet and singlet currents; (35–36): general radiative neutrino mass before their texture reduction | Footnote 8 excludes quark–lepton interactions from that analysis. A Higgs insertion in the propagator is proportional to `−P G P`, with distinct daughter invariant masses. Constant four-lepton coefficients alone do not supply h→4f, scalar radiation or gauge-current interference. Do not import their subsequent zero-texture assumptions. |
| [Prophecy4f 3.0, 1912.02010v1](https://arxiv.org/html/1912.02010v1), DOI 10.1016/j.cpc.2020.107336 | Section 2, Eq. (1), Fig. 1: coherent WW/ZZ-mediated 4f with off-shell gauge bosons and QCD/EW corrections in its supported models | External fermions are massless and scalar-pair-mediated four-fermion decays are excluded. It can control the SM WW/ZZ norm, but its built-in 2HDM result is not a general Zee bound. No code was installed or run. |
| [Kniehl–Spira, hep-ph/9505225v1](https://arxiv.org/abs/hep-ph/9505225), DOI 10.1007/s002880050007 | Section 2.1, Eqs. (1–2): soft external Higgs insertion by appropriate bare-parameter derivatives | The theorem is at zero Higgs momentum. A derivative of a fitted neutrino mass with physical masses/mixing held fixed is not the derivative of the native Lagrangian, and does not bound the 125-GeV form factor. |
| [Schmidt–Vandeleur, 2512.17235, published version](https://doi.org/10.1007/JHEP06(2026)006) | Eq. (2.20), section 3.1 Eqs. (3.1–3.2): Zee neutrino mass and dimension-five matching with both lepton Yukawas | Matching/running of masses is published; it is not an executed finite-momentum hνν bound for these cards. Their section 3 states the EFT truncation at dimension five. Do not add EFT running and the same full mass loop twice. |

These sources have versioned full-text hashes in JSON. Fresh reference checks
confirm 2017 ref. 95 → Bilenky–Santamaria and ref. 54 → He–Majee 1111.2293;
the 2026 paper's ref. 11 cites the 2017 work. This selected incoming/outgoing
check supplements the already-read rescue audit. It is not an exhaustive
citation census, and no literature-absence claim is made.

## Exact remaining physics input and its numerical target

Use physical final states, not an incoherent list of parent pseudo-widths:

* `h→W(*)H_i*→4f`, both charged states and native F/D/quark currents;
  the W may be on shell. Include gauge/Goldstone completion where needed.
* `h→Z(*)A*→4f`, and neutral/charged scalar-pair exchange, including H and
  off-diagonal charged trilinears. A CP-even H has no CP-conserving tree hZH
  vertex; its virtual contributions occur through scalar-pair or radiation
  topologies, not an invented hZH coupling.
* Scalar radiation from the Yukawa-produced fermions and all identical-final-state
  permutations; leptonic, semileptonic and hadronic states.
* SM–BSM and BSM–BSM interference in common final states. WW/ZZ interference
  must also be reconciled with the retained HDECAY pseudo-channel approximation.
* Leading radiative Majorana `h→νν`. SM `ZZ*→4ν` already belongs to the
  four-fermion set. Inclusive radiation/Dalitz corrections must not duplicate
  already-counted Zγ or ordinary partial widths.

For a complete exclusive four-fermion amplitude define
`A=∫|MSM|² dΦ/(2mh)` and `B=∫|MBSM|² dΦ/(2mh)`, with the same flavor,
color and symmetry conventions. Cauchy–Schwarz gives the rigorous structure

`|δΓ4f| ≤ B + 2√(AB)`.

The retained WW+ZZ proxy is **0.944081484 / 0.946266428 MeV**. If it were
certified as the appropriate A, sufficient B targets to stay inside the closer
one-error endpoint would be **137.291 / 173.995 keV**, before reserving any
budget for invisible width, ordinary-channel uncertainties or acceptance.
These are **requirements, not achieved bounds**, and A is not yet a certified
coherent inclusive norm. This quantifies the missing input more appropriately
than demanding an arbitrary 1% width calculation. A usable next input is a
certified A and an upper bound on B for the complete set above, plus the
disjoint invisible contribution. Scalar propagator bounds and known couplings
are available, but no source-matched complete current/phase-space norm with
the required interference was executed. A new general 1→4 generator is outside
this task and was not started.

No tree neutral hνν Yukawa exists at massless-neutrino tree order. That fact
does not set the radiative Majorana width to zero. A soft-Higgs derivative
would follow the two native vevs along the h direction, holding Lagrangian
couplings fixed, and differentiate charged-lepton masses, the charged-scalar
mass matrix, its mixing and eigenvalues (the scalar insertion is G). It cannot
hold the fitted spectrum fixed or simply set `Yhνν=mν/v`; flavor cancellations
in a mass need not persist in a derivative. The inspected EFT and soft theorem
do not bound the finite-momentum remainder here.

For a convention `L=−h νᵀYν/2+h.c.`, the massless Majorana width is
`mh Tr(Y†Y)/(16π)`. With every other missing effect set to zero, reaching the
lower one-error endpoint requires `||Y||F=0.0338124 / 0.0302712`. This is a
coupling sensitivity target only. The actual finite-momentum Y, its norm bound
and the loop width remain null. No neutrino-mass power-counting guess, broken
SPheno result, or unrestricted loop calculation was used.

## Ordinary-channel uncertainty and acceptance

[HDECAY 1801.09506v1](https://arxiv.org/html/1801.09506v1#S2.SS5),
DOI 10.1016/j.cpc.2018.12.010, section 2.5 distinguishes factorizing QCD
corrections from non-factorizing EW corrections. Its doublet-model estimates
do not certify a mixed-Zee Gaussian nuisance. The pinned 6.60 receipts and
corrected charm conversion are preserved. Native κb matching is already
checked; no Type-II lepton total is transferred.

The known bb fractions are 0.623180/0.586155, gg fractions 0.066336/0.078678.
A correlated fractional bb correction x changes the diagnostic rate by
`(1+x)/(1+fbb x)`, not merely by `1/(1+fbb x)`; a gg correction y alone gives
`1/(1+fgg y)`. The charm correction already applied shifted S by −1.634% /
−1.914%. The ledger/native BR mismatch is 1.643%. These source/scheme shifts
are much smaller than the endpoint budgets, but neither is a theory σ.
Parametric masses/αs, QCD truncation and Zee EW corrections need a justified
correlated interval; no arbitrary common 5/10% error is assigned. The roughly
several-percent discussion for 2HDM cannot be asserted as a rigorous Zee bound.

At tree order the native hVV vertex has the SM Lorentz structure and a common
κW=κZ. Thus a constant κV rescaling preserves the VBF and VBF+photon template
shapes at that order. The all-hadronic analysis requires pT(bb)>150 GeV and
has 0.8% inclusive VBF selection efficiency; an inclusive σ ratio is not a
general validation of shape-dependent BSM corrections. ATLAS section 7 fixes
ggF/VH/ttH contributions to SM and reports that adding a correlated 100% ggF
uncertainty changes the expected μ error by 0.01. This is useful evidence of
weak ggF sensitivity, **not a measured bias bound or a new model nuisance**.
The unqualified D7 LO ggF ratio is about 0.904; the full ggF×BR alteration and
its regional template response are not inferred from that number alone.
VH/ttH are described as negligible in the all-hadronic fit; the combined
photon channel and model uncertainty still require matching. There is no
demonstrated mandatory detector recast at tree order, but acceptance bias is
not assigned a numerical bound. The first stopping obstruction is the missing
qualified rate interval; the JSON must not be evaluated as a physical constraint.

For a deliberately broad **scale diagnostic** Δ=±(WW+ZZ proxy), conditional μ
ranges are D7 [0.87466,1.36966] and F13 [0.81413,1.31781]. Both sit within
the Gaussian 95% surrogate; D7 can cross an upper one-error endpoint. This
motivated electroweak-width scale is not a physically certified uncertainty
envelope. Hence no robust physical exclusion/non-exclusion follows. The rate
near the retained sums would be weakly constrained, and this analysis is not
an efficient reason to chase sub-percent terms. A paper should prioritize
qualified h→γγ, LFV h or charged-H2 observables over extending this weak gate;
their own prediction and acceptance requirements still apply.

## Checks and release

`python -m unittest research.full_constraints.higgs.test_h125_signal_strength -v`
passes all seven existing checks, including raw receipt normalization, original
cards/source binding, charm/production controls and rejection of incomplete totals.
The new diagnostic independently checks endpoint inversions by numerical bisection
(max absolute residual 1.735e−18 GeV) and propagator extrema on a 1001-node
kinematic grid against the analytic monotonic bound. These are numerical/algebraic
checks, not validations of an uncomputed physical amplitude. The conditional plot
was rendered and visually inspected. No source evidence or old result was rewritten.

Reproduce with `MPLCONFIGDIR=/tmp/zee-vbf-mpl python -m
research.full_constraints.higgs.vbf_bb_materiality` (one shell line), using the
pinned runtime and full-text files identified in the JSON. Also run
`git diff --check`. The calculation writes only the new materiality JSON and plot.
The accompanying validation log records the actual commands and results.

| Gate | Evidence | Decision / next decisive input |
| --- | --- | --- |
| Measurement identity and absolute normalization | Actual ATLAS full text, native JSON/source/ref replay | PASS, scoped data interpretation |
| Observable-specific sensitivity | Exact inverse rate plus independent bisection | PASS, conditional diagnostics only |
| Full virtual/invisible signed-width bound | Restricted EFTs inspected; propagators bounded; complete A/B and Y absent | UNKNOWN / STOP: complete current norm and finite-momentum Majorana bound at the stated budgets |
| Theory/reference/acceptance interval | Scheme displacement calculated; no qualified covariance/bias bound | UNKNOWN / STOP before a likelihood |
| `RATE_THEORY_VALIDATED` | No complete interval | Not attained |
| `MEASUREMENT_SCOPED_EVALUATED` | Zero model HS calls | Not attained |
| Model excluded/not excluded by this measurement | No qualified physical prediction | UNKNOWN |

Release only this sensitivity study and precise missing-input specification.
Keep `H125_ABSOLUTE_MU_BLOCKED`, `HIGGS_FULL_COVERAGE_BLOCKED`,
`B_FULL_RATE_BLOCKED`, `LFV_FULL_COVERAGE_BLOCKED`, vacuum/global UNKNOWN.
No milestone increment, new parameter point, scan, generator campaign, Condor,
heavy H/A loop work or final-scan authorization follows.
