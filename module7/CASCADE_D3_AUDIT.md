# D3 charged cascade and coherent scalar–flavor diagnostic — 2026-10-27

**TREE_Z_CASCADE_WIDTH_VALIDATED; NATIVE_VERTEX_VERIFIED;
D3_COUPLED_DIAGNOSTIC_PASS.** These are scoped validation statuses.
`BR_NOT_EVALUATED`, `PHYSICAL_LHC_CLAIM_NOT_EVALUATED`,
`global_zee_acceptance=null`. None of the twelve points is declared physically viable.

## Source and amplitude audit

Florentino, Romão and Silva, [EPJC 81 (2021) 1148](https://link.springer.com/article/10.1140/epjc/s10052-021-09956-2),
[arXiv:2106.08332](https://arxiv.org/abs/2106.08332), Appendix B.1
Eqs. B.2/B.3b,c and Eqs. 72/73 are the exact sources.
They already derive this vertex, width, competing charged decays and benchmark spectra.
Their lambda denotes the **square root** of the Källén polynomial, in GeV².

With all momenta incoming, the vertex is
`-i g/(2 cw) (p_plus-p_minus)^mu G21`, `G21=-sin(2 gamma)/2`.
The frozen Module1 rows are
`ZP={{cb,sb,0},{-sb cg,cb cg,sg},{sb sg,-cb sg,cg}}`.
For positive-charge fields, doublet `T3=1/2,Q=1` and singlet `T3=0,Q=1` give
`[ZP diag(1/2-sw²,1/2-sw²,-sw²) ZP^T]23=-sin(2 gamma)/4`.
The universal electric-charge term cancels off diagonal. Thus the vertex
coefficient is `+i g sin(2 gamma)/(4 cw)` in this convention, in both orientations.
There is no extra factor of two from the Hermitian-conjugate interaction.

For the decay, crossing gives `p_plus=P`, `p_minus=-k`, and current `J=P+k`.
The on-shell polarization sum `-g_munu+q_mu q_nu/mZ²` gives
`sum|A|²=|cZ|² lambda_polynomial/mZ²`.
Using `|p|/(8 pi M²)` two-body phase space, no scalar spin average and no
identical-particle factor gives

`Gamma = sin²(2 gamma) lambda_sqrt³/(64 pi v² M³)`.

Here `cw=mW/mZ`, `g=2mW/v`, `g1=g tan(thetaW)` in the frozen on-shell tree scheme.
The code uses the stable product `(M-m-z)(M+m+z)(M-m+z)(M+m-z)` and requires
`M>m+z`; threshold/below-threshold widths are zero. Zero mixing at 0 and ±pi/2
is exact. Sign reversal and gamma→pi/2−gamma preserve the width.
Tests independently construct four-vectors and all three physical Z polarizations,
check their norms/transversality and the projector, boost to another frame,
cross both charge orientations, and compare with Eq. 72. The nearest floating-point
mass above threshold agrees with a 60-digit Decimal phase-space product.

## Actual native validation

`math -script scripts/zee_d3_cascade_vertex.m` executed successfully using
Wolfram 15.0.1 and **SARAH 4.15.4**. The frozen model was read only; all native
output is under ignored `validation/module7/local/`; no Make*, SARAH regeneration,
vacuum, Wgamma or matching scan was run. SARAH Start only initializes the model
needed for native Vertex queries.

The native EWSB queries are `conj[Hm[{2}]],Hm[{3}],VZ` and the reversed 3/2
orientation, plus the off-diagonal photon control. The returned Lorentz structures
are scalar momentum differences. Across two beta values, six gamma choices
(including both signs, zero/endpoints and the reflected angle), and two vevs,
**24 cases pass**, maximum signed coefficient residual **2.7755575615628914e-17**.
At the D2 input, both absolute Z coefficients are **0.15207461883074228**;
the analytic value is **0.15207461883074225**. Photon mixing vanishes to rounding.
The native signed coefficient agrees without an external-field rephasing.
[Native evidence](../validation/module7/native_vertex.json) retains raw expressions,
all cases, model/driver hashes, version and residuals. Tests bind this actual
execution evidence to the unchanged driver/model; tests do not pretend to rerun SARAH.

## D2 binding and results

Work is restricted to branch `feature/zee-d3-charged-cascade-width`, descended from
verified D2 **9c9630e6191d149ec23bd640ad4f327c8d4c69a8**.
Complete D2 evidence byte SHA is
`79f4164b1bf74b21576e2711960dca3a415cc9eb03f133eb5a885ad10b607b84`.
The reader verifies those bytes against the exact Git parent, the full seed byte
and canonical hashes, source-manifest hash and frozen files. D2's recorded final
validation hashes supersede its execution hashes for the runner/test only;
the task-scoped AGENTS replacement is explicitly exempt from current-file equality.
The historical AGENTS hash remains authenticated inside the parent evidence.

All **35** complete scalar inputs, including EW scheme, fit, search settings and IDs,
are independently rebuilt from the seed and declared offsets. Their canonical SHAs,
physical values, reconstruction, BFB, 55-state unitarity and STU/chi2 are checked
against D2 with exact equality. Gate counts are reconstruction 35/0, BFB 32/3,
unitarity 31/4, EWPO 35/0; cumulative **35→32→29→29**.
All **29 scoped PASS** widths are recorded; the **six FAIL** rows remain control-only
and are excluded from statistics. Neutral-only duplicates are removed from charged
statistics: **23 distinct** charged mass/mixing triples, width range
**6.073844177735318–13.607156728177802 GeV**. This source-centered development grid
is **not a probability prior or representative scan**; these extrema are not bounds.

Each of the **12** executed D2 records is linked through independently rebuilt
coefficient vectors, all three IDs, full input and Module2 hashes, scalar SHA,
unchanged NO target, flavor-derived input SHA and execution manifest. Full scalar/EW
inputs agree across the four families apart from their benchmark IDs; equal physical
inputs therefore need not have equal ID-inclusive scalar SHAs. Archived point STU/chi2
also agree with the reconstructed selected spectrum. No detailed ignored D2 outputs
are required and **zero vacuum searches are repeated**. Archived observables are
authenticated reuse, not new LFV or quark-flavor calculations.

All rows below use mH2=700 GeV, gamma=1.089, v=246.21965 GeV,
mW=80.379 GeV, mZ=91.1876 GeV. Flavor numbers are conditional LO-linear diagnostics.

| mH1 GeV | Cascade partial width GeV | Delta C7 | Delta C8 | Conditional value in 10^-4 |
|---:|---:|---:|---:|---:|
| 250 | 11.671906176399391 | -0.06428360601034018 | -0.06654336424347776 | 4.230787153913907 |
| 300 | 9.411343258642537 | -0.05955354444399845 | -0.06299918381959017 | 4.182878900268742 |
| 350 | 7.1240428396019855 | -0.055903518399357255 | -0.06008467298268906 | 4.145521835221139 |

Across these three scalar choices, increasing mH1 lowers the gauge width and the
conditional linear value while making C7/C8 less negative. This is a conditional
association in three selected spectra, not a population correlation or flavor cut.
At each fixed spectrum all four families have exactly **zero** spread in gauge width,
C7, C8 and the conditional linear value. A pure gauge width cannot respond to
homogeneous lepton Yukawas at fixed masses/mixing.

The four independent inverse directions instead yield four distinct D matrices.
For 250/300/350 GeV, the mu→eγ subset max/min ratios are
**1.0017378781 / 1.0029859620 / 1.0002408157**; h→eτ partial-width ratios are
**68.75839892 / 101.93674716 / 67.27640478**. The latter remains tiny in absolute
units. All three radiative subset BRs and nine Higgs LFV widths per family are retained
in the CLI comparison; the compact report selects the principal contrasts.
The unchanged NO target closes, but no official joint neutrino likelihood is inferred.

## Validation and reproduction

**16 scoped tests PASS**, zero failures/errors/skips. Falsifiers cover complete
seed/evidence/source hashes, stale scalar hashes, masses/mixing/vev, IDs, family
coverage/duplicates, nonfinite and duplicate JSON, threshold, invented total width/BR/
allowed/completeness flags, and a 1e-12 violation of fixed-spectrum C7 invariance.
Across all 35 spectra the independent Eq. 72 maximum absolute discrepancy is
8.881784197001252e-15 GeV; explicit polarized four-vectors differ by at most
1.0658141036401503e-14 GeV (relative 1.1922751531745212e-15).
The exact commands executed are:

```sh
math -script scripts/zee_d3_cascade_vertex.m
python -m unittest discover -s tests -p 'test_module7_cascade_z.py' -v
python -m unittest discover -s tests -p 'test_module7_*.py' -v
python -m module7.cascade_z --input module7/example_cascade_input.json --output validation/module7/local/cascade_example.json
python -m module7.d3_cascade_compare --seed module3/example.json --d2-evidence validation/module6/d2_scoped_scan.json --output validation/module7/local/d3_cascade_comparison.json
git diff --check
```

[Compact report](../validation/module7/cascade_d3.json) records hashes, numeric
residuals, all 35 spectrum widths/eligibility, 12 linkage records and family contrasts.
Local CLI outputs and logs are ignored. Frozen Modules 0–6 and model are unchanged.

## Publication decision and blockers

D3 is the first shared scalar/flavor/collider **diagnostic in this repository**.
It establishes no new decay formula and no publication novelty beyond the
[2017 general-Zee study](https://arxiv.org/abs/1701.05345) or the 2021 cascade paper.
New coherent flavor–collider correlations require constrained neutrino/LFV sampling
and observable collider rates. Next work needs all competing H2 modes (tb,
Wh/H/A, H1+h/H and leptonic modes), H1 decay tables, a physical cascade BR and
production rates. Never set the cascade BR to one or normalize it using tb alone.
Detector simulation is unnecessary merely to tabulate parton-level rates;
LHC reach/exclusion claims remain unevaluated.

All twelve scalar vacuum gates remain **UNKNOWN**; full LFV including Wgamma and
physical B→Xs gamma remain incomplete, with the 2026 filter readiness false.
RG closure, joint neutrino likelihoods, uncertainties and population sampling remain
open. `BR_NOT_EVALUATED`, `PHYSICAL_LHC_CLAIM_NOT_EVALUATED`,
`global_zee_acceptance=null` apply throughout.

IO inventory: the genuinely available tracked input is
`module2/data/nufit60_ic19_io.json`, explicitly **NuFIT 6.0 (2024), IC19 without SK,
IO diagonal Gaussian approximation**, sourced to the v60 parameter-table PDF.
The D2 seed supplies only its illustrative NO complex target; no sourced coherent
IO target is supplied here. The parser's support for NuFIT 6.1 is not an available
official 6.1 joint-profile dataset. No NO→IO relabeling or IO execution is performed.
