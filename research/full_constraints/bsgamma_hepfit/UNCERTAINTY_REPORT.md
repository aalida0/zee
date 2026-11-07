# Fixed-card NLO uncertainty execution

**B_FULL_RATE_BLOCKED; physical_bsgamma=UNKNOWN; theory_sigma=null;
exclusion=null. Stop this solo code stream pending specialist input.**

69 successful processes use the existing pinned executable (same binary
hash as the earlier validated execution). No matching implementation,
backend build or original receipt was changed. UNCERTAINTY_RUNS.json binds
full inputs, stdout digests, commands, correlations, covariance, Cholesky
factor, output covariance and signed shifts. Raw files are in
uncertainty_receipts/. Reproduction requires the existing scratch environment:
`python3 research/full_constraints/bsgamma_hepfit/uncertainty.py` (refuses an
existing receipt directory). NumPy is required. Central rates reproduce the
prior D7/F13 execution. An initial development invocation omitted mandatory
THDM fields; the corrected runner reuses the exact prior THDM input map.
Only successful final processes enter the evidence.

The matrix is declared in the runner before execution: central, six separate
scale endpoints, fourteen signed Cholesky directions, two BLNP directions;
each runs SM plus the same D7/F13 scalar spectra. μ0 changes mut and muw
together and recomputes NP matching using the printed running top. There
are no new scalar points. Delta always subtracts the SM from the same row.

The upstream historical card supplies BRsem, Mbkin, Mcatmuc, mupi2,
rhoD3, muG2, rhoLS3 and their true seven-by-seven correlation matrix.
We use V_ij=s_i corr_ij s_j, L=Cholesky(V), and symmetric responses along
columns of L. The partial output covariance is J J^T, with each J column
half the plus/minus rate difference. This is a linearized Gaussian
propagation of this block only, not a total theory covariance. CKM inputs
have zero widths in Flavour_Misiak.conf and are held fixed, not interpreted
as exact physical measurements. alpha_s, top, other masses and missing
cross-correlations are not included in the partial budget. The fit provenance
is the historical HEPfit card; contemporary fit equivalence is not certified.
The prior report/source lock retain the historical source attribution.

| Quantity | Partial seven-input sigma in BR |
| --- | ---: |
| SM | 6.2526014e-06 |
| d7_NO_neutral_near_heavy_07 | 7.4835558e-06 |
| d7_NO_neutral_near_heavy_07_delta | 1.2549549e-06 |
| F13_heavy_0001330 | 6.8686994e-06 |
| F13_heavy_0001330_delta | 6.2689401e-07 |

The endpoint prescription uses the ranges in
[2015 Sec.II](https://arxiv.org/html/1503.01789v2): μ0=80/320 GeV,
μb,μc=1.25/5 GeV, varying one scale at a time. These are signed diagnostic
responses, without a probability distribution or quadrature combination.

| Variation | SM shift | D7 shift | D7 delta shift | F13 shift | F13 delta shift |
| --- | ---: | ---: | ---: | ---: | ---: |
| mu0_80 | +6.66539e-06 | +3.713952e-06 | -2.951438e-06 | +4.792827e-06 | -1.872564e-06 |
| mu0_320 | -4.438869e-06 | -3.05758e-06 | +1.381289e-06 | -3.451795e-06 | +9.870744e-07 |
| mu_b_bsgamma_1.25 | -2.359206e-05 | -2.690603e-05 | -3.31397e-06 | -2.534459e-05 | -1.752529e-06 |
| mu_b_bsgamma_5 | -8.586516e-06 | -2.795491e-06 | +5.791025e-06 | -5.512607e-06 | +3.07391e-06 |
| mu_c_bsgamma_1.25 | +0 | +0 | +0 | +0 | +0 |
| mu_c_bsgamma_5 | +0 | +0 | +0 | +0 | +0 |
| BLNP_-1 | -1.878187e-05 | -2.33976e-05 | -4.615728e-06 | -2.12146e-05 | -2.432737e-06 |
| BLNP_+1 | +1.878187e-05 | +2.33976e-05 | +4.615728e-06 | +2.12146e-05 | +2.432737e-06 |

**Charm-scale limitation:** the explicit μc dependence enters Kij_2 and
P22 at NNLO, while computeParameters reads Mc directly from Mcatmuc.
Thus changing μc with that mass fixed gives exactly zero at the retained
NLO order. This is an incomplete physical charm-scale prescription, not
zero truncation uncertainty. A consistent running-mass/scheme variation
and conversion of the correlated fit would require an additional qualified
prescription; it is not guessed here.

HEPfit bsgamma.cpp:2342–2399 retains N27 proportional to
Re[C7*(2 C2-C1/3)] muG2/(3*1.131²), N77 proportional to
(|C7|²+|C7p|²) times kinetic HQE terms, and BLNPcorr*P0.
The last nuisance is propagated separately; it is not combined with the
fit block or scales. Its large signed response demonstrates NP dependence
of this **particular** nuisance only.

[Resolved-photon analysis](https://arxiv.org/html/1003.5012v2), Eq.(103),
requires distinct hadronic inputs multiplying C1/C7, C8/C7 and (C8/C7)².
Its ranges do not define a joint Gaussian covariance. Operator labels also
require a basis conversion before insertion into BMU. No public joint
model for all these terms and penguin remainders has been established in
this bounded gate. A P0-shaped scalar cannot establish it.

ONE_STATE_CONFIDENCE.md records the explicit historical confidence
calculation and its mismatch. Missing u/c, finite-ms, down-Yukawa,
independent primed, extra scalar/four-quark and Zee EW/lepton effects
remain without quantitative bounds on these cards; no claim of material
smallness is made. This gate is therefore not closed even at the two
points, and no wider model domain is certified. No physical adapter is
implemented. specialist_question.md states the exact required input;
no message has been sent. B milestones remain 2/5.

Validation: all 23 tests pass (18 preserved and 5 new), evidence verifier passes, and git diff --check passes. The executed runner snapshot is retained under uncertainty_receipts; the reproduction runner differs only by refusing an existing output directory. Both hashes are recorded.
