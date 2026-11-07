# Executed HEPfit B→Xsγ calculation — 2026-11-07

**HEPFIT_RUNTIME_PASS. INDEPENDENT_RATE_EXECUTABLE.** The coherent bridge
passes implementation checks. **INDEPENDENT_RATE_MISMATCH** describes the
physical-rate comparison with the preserved SuperIso prescription; it does
not describe a failure of the matching identities.
**UNCERTAINTY_CALIBRATION_BLOCKED / B_FULL_RATE_BLOCKED.**
`physical_bsgamma=UNKNOWN`, `theory_sigma=null`, `exclusion=null`.

37 HEPfit processes completed successfully on the two original D12 scalar
cards and their fixed-card/algebraic controls. Two additional fresh D9B
SuperIso processes reproduce the original two-state rates. The output is
an independently executed **finite-cut central branching ratio** in the
declared prescription, not a full-model exclusion. No scan or new scalar
proposal, production run, LFV/Higgs study, SusHi/HDECAY execution or
frozen-source edit occurred.

## Reproduction and actual build

[REPRODUCE.md](REPRODUCE.md) gives the build/run commands.
[SOURCE_LOCK.json](SOURCE_LOCK.json) binds 346 build/rate/configuration files,
the exact HEPfit commit `322bd73a2dadd94ce94a6d71cb79d616e569120a`, its gslpp
gitlink `f5b059e…`, dependency archives and the small local patch.
Before patching, 1,430 extracted code/table/CMake files matched their Git
blob IDs in the pinned recursive tree, including all three task-provided
SHA256 pins. No full third-party source tree or binary is distributed.

The upstream CMake `NOMCMC=ON`, `BAT_INSTALL=OFF` configuration succeeded.
StandardModel, THDM, Flavour, LeptonFlavour and LoopFunctions libraries
compiled. The client links these libraries and RGESolver's gslpp objects;
it does not invoke BAT, MCMC or the upstream Analysis target.
[BUILD_RECEIPT.json](BUILD_RECEIPT.json) records actual GCC 11.4.0,
CMake 3.22.1, ROOT 6.32.12, Boost 1.74 and per-target flags/library hashes.
The required RGESolver dependency was built at `d1eb755…`, with the same
gslpp gitlink as HEPfit. Its reported `rgesolver-config --version` is
pkg-config's **0.29.2**, not the physics-library version; the commit is the pin.

The first client link failed because the preinstalled AlmaLinux ROOT needs
`libtbb.so.2` and `libgsl.so.25`. The focused environment fix used the
SHA-verified Ubuntu `libtbb2 2020.3-1ubuntu3` package and the existing Herwig
GSL **2.7** shared library in scratch. The link selects that GSL SONAME
explicitly; `LD_LIBRARY_PATH` supplies ROOT's indirect TBB dependency.
HEPfit/RGESolver compilation used installed **2.7.1 headers**, runtime is
**2.7**, as recorded separately. ROOT/GSL original archives and actual
libraries are hashed. This is an environment-specific receipt, not a claim
that arbitrary ROOT/GSL installations are interchangeable.

There is one audited algorithm-preserving source change:
[initialize_matching.patch](initialize_matching.patch) initializes the
THDMMatching coefficient arrays to zero and its four cache keys to -1.
The pinned constructor left these primitive members uninitialized, while
`CMbsg()` reads every operator slot. An actual placement-construction
falsifier with previously nonzero storage returns
`C1_LO=C1_NNLO=0.00047679227941176469` with the **original** constructor;
the patched constructor returns exactly zero. See
[the unpatched witness](receipts/initialization-falsifier.log).
No loop function, matching formula, running, normalization or matrix element
is changed. The original first one-state run happened to have zero unused
slots; it is superseded by the initialized final executions.

The custom vector uses WilsonTemplate's deep **copy constructor**, never
assignment of live coefficient objects (upstream has owning pointers and
no deep assignment operator). Repeated matching/rate calls execute normally.
[linked-symbols.log](receipts/linked-symbols.log) identifies the actual
THDMMatching, CoherentMatching, HeffDB1 and Bsgamma methods in the executable.
Preliminary driver/input failures are retained as development receipts;
only `execution/` and its success-recorded commands form accepted run evidence.
An initial parallel SuperIso archive build was corrupt; the **serial `-j1`**
rebuild is the one used. Both transcripts are preserved losslessly as gzip.
[SUPERISO_SOURCE_RECEIPT.json](SUPERISO_SOURCE_RECEIPT.json) verifies all 75
distributed files against a fresh archive-plus-frozen-patch replay, with zero
mismatches; the original archive and frozen client are separately hashed.

## One-state benchmark and perturbative prescription

The reference is HEPfit's source-attributed **Misiak et al. 2015 NNLO
Type-II table**, `THDM/tabs/bsgammatable.dat`, with nuisance set to zero.
`bsgammaTHDM.h:22–26` identifies its origin and NNLO order.
The [publication](https://arxiv.org/html/1503.01789v2), Sections II/V,
uses Eγ>1.6 GeV and central scales μ0=160 GeV, μb=μc=2 GeV.
Its SM reference is `(3.36±0.23)×10^-4`. These historical results are used
only to qualify this reference, not as a modern Zee likelihood.

The direct kernel uses the pinned upstream Bsgamma/THDM Misiak input cards,
with μt=μw=160 GeV, μb=2 GeV and μc=1.99999999 GeV (upstream's numerical
separation of the two low scales). We explicitly set **FlagMtPole=true**:
the historical card's 173.2 GeV is a pole mass. Current HEPfit defaults to
MSbar; accepting that default would misinterpret the input. The resulting
mt_MSbar(160)=164.29247164143644 GeV and alpha_s(160)/(4π)=0.008689679873480773.
Every final stdout includes the complete input map, actual complex 3×3 CKM,
running masses/scales, normalization, all eight high/low order-tagged Wilson
entries, P_LO/P_NLO/P_NNLO and separate EM/Vub/power terms.

| Original-card one-state control | tanβ | M [GeV] | Published NNLO table | Direct HEPfit stock NNLO | Direct HEPfit NLO numerator |
| --- | ---: | ---: | ---: | ---: | ---: |
| D7, mH1 endpoint | 1.1157268701 | 298.7266553 | 4.64575862097e-4 | 4.65800563532e-4 | 4.82481452322e-4 |
| F13, mH1 endpoint | 5.3077513190 | 572.2316244 | 3.87730347625e-4 | 3.89717074046e-4 | 4.02809191181e-4 |

The published table is **actually evaluated** through HEPfit and independently
interpolated in Python; residuals are ≤5.5e-20 in BR. This reproduces the
tabulated one-state prediction, not an independent recomputation of its NNLO
kernels or interpolation error. The direct stock-NNLO kernel differs by
0.264% / 0.512%; the NLO-numerator result differs by 3.85% / 3.89%.
No precision equality with the publication is asserted. The table does not
expose a per-run input/scale covariance or an NLO counterpart, and the two
perturbative prescriptions cannot be certified equal by this interpolation
test. Thus the **matched independent same-order physical benchmark remains
unestablished**, despite the numerical table reproduction and working rate.
No one-state confidence bound has been reproduced (`NOT_EVALUATED`).

Executed direct SM: stock NNLO `3.3692203695280618e-4`, NLO numerator
`3.4914232437401022e-4`. The stock-NNLO SM residual to the quoted historical
central value is `9.22037e-7`; closeness is not a replacement for matched
physical inputs or a source-matched uncertainty analysis.

`Bsgamma::computeThValue()` always asks for NNLO. The accepted research
NLO branch instead evaluates the public `P(E0,μb,μc,NLO)` and `N(E0,μb)`
with the same normalization. `P_NLO=P0+a_b(P11+P21)+Vub_NLO+a_em EW_NLO`;
all P12/P22/P32 and Vub_NNLO terms are absent. HEPfit's retained HQE/EM,
semileptonic and running prescriptions are not re-expanded into a uniformly
truncated QCD+QED/HQE theory. FOUR_BODY is false; EW matching is partial
(source header explicitly says it is missing). The native approximate
`C7p=(ms/mb) C7+evolved_primed` rule is retained, whereas D9B omits primed
terms. General complex/primed matching is not validated.

## Coherent Zee adapter and measured rates

The frozen BMU evaluator supplies **ordinary**, unweighted
ΔC7,8^(0), ΔC4,7,8^(1), with the matching top and scale printed by HEPfit.
For the real, top-only, leading-EW/pure-QCD domain,

`ΔC_i = cos²γ ΔC_i^II(mH1) + sin²γ ΔC_i^II(mH2)`.

`driver.cpp::CoherentMatching` starts with StandardModelMatching once,
adds one NP eight-operator vector, converts ordinary to effective dipoles
at each retained order and applies alpha_s(μ0)/(4π) **once** to the NLO
matching. It retains C4 and RG-induced C3–C6. NP NNLO matching is explicitly
zero; stock-NNLO outputs on these bridge runs are **mixed-order diagnostics**,
not accepted NNLO Zee predictions. The generic DC7-only API is never used.

| Original D12 card | HEPfit research NLO BR | Fresh D9B SuperIso NLO BR | HEPfit − D9B |
| --- | ---: | ---: | ---: |
| D7 | 4.17955384241e-4 | 4.22625081294e-4 | −4.66969705284e-6 |
| F13 | 3.83711422745e-4 | 3.88665197906e-4 | −4.95377516152e-6 |

These HEPfit values use its reference SM/hadronic inputs and the **original
scalar cards**; they do not overwrite the D12 prediction prescription.
Both SuperIso values reproduce the archived D12 results at printed precision.
SM-zero, both endpoints, mass exchange with γ→γ+π/2, equal masses, native
HEPfit versus independent BMU matching, signed C4/C7/C8 probes and a held-out
joint C7/C8 point passed. Largest stored implementation residual is
5.82e-17. These tolerances are numerical, not theory uncertainties.
Coherent minus weighted-one-state BR is −1.59324e-7 (D7) / −6.41083e-8
(F13), demonstrating the required nonlinear interference.

At fixed original cards, recomputing matching/top at μ0=120/200 GeV gives
D7 BR `4.19413826178e-4 / 4.16902059517e-4` and F13
`3.85512528699e-4 / 3.82473132128e-4` (see exact receipts for rounding).
These are scale sensitivities, **not a sigma**. No scalar crosses a top
threshold in these cards. Near mt/M=1 and generally separated-threshold
accuracy are not newly certified; no extra scalar masses were generated.

## Discrepancy without an intercept adjustment

Both calculations use negative-Hamiltonian BMU/NDR matching, coherent NP
vectors and a 1.6-GeV cut. Shared physical-input/NP-vector runs align pole
top, alpha_s(MZ), MZ, bottom/charm/strange inputs, Wolfenstein inputs,
semileptonic BR, kinetic bottom/HQE values, μb=2.3937494653 GeV and μc=2 GeV.
They inject **identical D9B ordinary NP matching**, so NP matching is no
longer a possible explanation of those particular residuals. HEPfit then
gives D7/F13 `4.19857276033e-4 / 3.85040864091e-4` and SM
`3.49881227074e-4`. Agreement still is not exact.

The residual is measured by the exact identity, with H/S denoting kernels:

`BR_H−BR_S = (n_H−n_S)(P_H+N_H) + n_S(P_H−P_S) + n_S(N_H−N_S)`.

Here `P_S=P0+P1+P_em`; n is the actual semileptonic/CKM/EM prefactor.
No term is fitted. Values below are BR differences in units of 10^-6.

| Shared-input/shared-NP card | Normalization | Perturbative incl. EM | Power | Sum |
| --- | ---: | ---: | ---: | ---: |
| D7 | +7.208383 | −10.702489 | +0.726301 | −2.767805 |
| F13 | +6.610632 | −10.939239 | +0.704272 | −3.624334 |

Source-located reasons for retaining a residual:

- `HEPfit bsgamma.cpp::C_sem` uses the charm input at μc and the
  0.903/−0.588 kinetic fit, with coefficients partly obtained by private
  communication (`bsgamma.h::C_sem`). SuperIso `bsgamma.c::C_BXlnu` uses
  mc(3 GeV), mb_MSbar+0.37 and its 0.849/−0.92 fit. Shared-input
  C_sem is **0.5636114624 versus 0.5734569447**, producing different n.
- Running/pole-conversion prescriptions remain different. At the same
  172.57-GeV pole top, HEPfit mt(160)=163.6853691 GeV, D9B
  163.1658730 GeV. The shared NP vector removes this difference from NP
  matching, but not from SM matching/running. MW is HEPfit's SM prediction
  versus SuperIso's input 80.3692 GeV; it is printed, not silently tuned.
- HEPfit `computeCoeff`, `EW_NLO`, `Vub_NLO`, `N_27`, `N_77` retain
  approximate primed terms, explicit Vub contributions, partially hardcoded
  EW (`C7_1ew=4.868`) and kinetic HQE terms. SuperIso's core uses its
  `P_em` and high-scale Kc/Kt power term with lambda2/mc(mc)^2.
  HEPfit `N_27` fixes its charm normalization to **1.131 GeV**. These are
  different prescriptions even after shared public inputs.

The exact decomposition explains where the measured rate difference enters;
it does not claim every residual has been isolated into a single mass-scheme
conversion. Implementing a common complete EW/HQE scheme would change the
physics calculation and is beyond this bounded bridge. Backend spread is
not used as an uncertainty.

## Defensible uncertainty gate and remaining work

The source provides real uncertainty ingredients, but no defensible **combined
Zee NLO theory sigma** has been established. The historical input card has
a correlated seven-parameter semileptonic/HQE block and `BLNPcorr` width
0.05. In the kernel `N=N_27+N_77+BLNPcorr*P0`; the nuisance multiplies the
dipole-dominated P0. Separately, the NNLO Type-II table has a 7% model
nuisance. That error belongs to the table's calculation. Transferring it
to a different NLO two-state Wilson-vector calculation is unsupported.
The [resolved-photon reference](https://arxiv.org/abs/1003.5012) establishes
nonlocal corrections from operators other than Q7; a single P0-shaped
nuisance is not a demonstrated covariance over altered C4/C7/C8 ratios.

A physical prescription must jointly propagate documented correlated input
priors **in one chosen rate scheme**, calibrate perturbative residuals at
that same NP order, and include Wilson-dependent power/resolved-photon
uncertainty with justified correlations. Scale variation and omitted-order
estimates must remain distinct from parametric priors. The current 120/200
controls omit μb/μc and scheme/remainder calibration and cannot supply
that budget. The 2015 NNLO SM/table errors, 2026 SM sigma, SuperIso 4%,
backend spread and a fitted intercept are all rejected as substitute Zee
NLO errors. No numerical NP sigma is assigned.

The materiality domain here consists only of the two saved spectra:
D7 (298.73,532.93 GeV; γ=1.31652785; tanβ=1.11573) and F13
(572.23,873.21 GeV; γ=1.08895009; tanβ=5.30775), plus exact algebraic
one-state/equal-mass/exchange controls. Matching/rate implementations have
been checked there; a full omitted-effect **materiality bound** has not.
Internal u/c, full finite-ms/down-Yukawa and primed sectors, additional
scalar/four-quark structures, electroweak/Zee-lepton effects and wider
threshold domains retain the blockers in the parent coverage ledger.

Before exclusion: close the independent same-order one-state physical
benchmark and these uncertainty/materiality gates, choose correlated theory/
experimental statistical treatment and reproduce the chosen scheme's
published one-state confidence bound. These dependencies were not achieved
in this bounded execution, so no physical exclusion or global acceptance
is attempted.

## Verification

[HEPFIT_EXECUTION.json](execution/HEPFIT_EXECUTION.json) contains only actual
success-recorded runs and parsed numbers, with full stdout/input hashes.
[tests.log](receipts/tests.log): **18 tests pass, zero skips**. Source,
photon-cut, order/operator, extra-alpha_s, missing-C4-map, duplicate-SM and
uncertainty-promotion falsifiers are included. The original evidence verifier
passes; frozen Modules0–13/D14, original receipts and the completed Higgs
stage remain unchanged. The B milestone count remains **2/5**, because
the matched physical-reference and NP-uncertainty milestones remain open.
