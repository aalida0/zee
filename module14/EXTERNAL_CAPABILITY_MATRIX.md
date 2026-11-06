# Public capability source audit (2026-11-06)

Outcome: **REFERENCE_ONLY / ZEE_ADAPTER_UNVALIDATED** for the new public
backends. No new amplitude or vacuum search has been implemented. Existing
D13 HiggsTools diagnostics remain operative with their original limitations.
All inspected source-file hashes are in `public_source_lock.json`; third-party
source and binaries have not been vendored. Probe results never assert a
physical PASS. No tool here supplies a calibrated 2026 Zee B-rate uncertainty.

| Tool and inspected version | Actual source inspected / inputs | Coverage and decision |
|---|---|---|
| [general-2hdm-pheno b5035cd58d2a7e4a91e9790d045df062b97adffe](https://gitlab.com/jbrod/general-2hdm-pheno/-/tree/b5035cd58d2a7e4a91e9790d045df062b97adffe), Apache-2.0 | thdm.py cR_llpg/cL_llpg/Gamma_l_to_lp_gamma, f8e, example.py; Higgs-basis rho matrices, three neutral states, **one** MHp, Z3/Z7, GeV inputs | Corrected radiative LFV control only. No Fzee, charged-singlet potential or two charged eigenstates. No Zee amplitude integrated. |
| SARAH **4.15.4**, archive SHA `4ab8f01ebe866cce954bc292118b5976913a2800efc6eeb2ad2e926a98fc42eb`; SPheno **4.0.5**, archive SHA `3f84a6c3e47f40e0dd1bcccb88eb08a1d0a65aa3d8e42504befdfc3d47ec9529` | Installed Gamma2l.m, Lto3Lp.f90, MuEconversion.f90; actual generated Zee LowEnergy/FlavorKit_LFV/RunSM Fortran, original model and SPheno.m. Source availability does not establish redistribution licensing: no code copied. | Generic one-loop operator framework; existing research scalar dipole subset has scoped comparisons. Additional LFV observables, neutrino/scheme completeness and a production adapter remain UNVALIDATED. |
| [Vevacious++ 657cf31c2489892d1862cd7ba21511e6f2ba863f](https://github.com/jwittbrodt/VevaciousPlusPlus_Development/tree/657cf31c2489892d1862cd7ba21511e6f2ba863f), GPL-3.0-or-later | README.txt, THDM.vin, PHCRunner.cpp, PolynomialSystemSolver.cpp; model-specific potential and LHA blocks | Included THDM potential has only phi1/phi2 field variables. It omits Zee charged-singlet/charged/CP directions. No usable Zee potential or benchmark comparison established. Numerical non-discovery remains UNKNOWN. |
| [HomotopyContinuation.jl 0cbf1e27d062d7eb01d962c3b948c39444c9a62c](https://github.com/JuliaHomotopyContinuation/HomotopyContinuation.jl/tree/0cbf1e27d062d7eb01d962c3b948c39444c9a62c), Project.toml **2.22.4**, MIT | src/certification.jl: square-system checks, solution intervals and Krawczyk certification | A root certificate is not an exhaustion proof. No Julia executable/full gauge-reduced Zee polynomial adapter is available here; no vacuum search executed. |
| SARAH/SPheno one-loop decays | Installed SPhenoLoopDecays.m and saved full-build/reduced-build evidence | Existing Zee full build failed on undeclared ZRUNoMatrix/ZRUNoMatrixc in neutrino final states. Reduced build disables loop decays. No validated Zee one-loop width or h125 gamma-gamma correction to integrate. |
| HiggsTools **1.1.3**, GPL-3.0 | Actual installed Higgs.tools.Input.py (SHA in lock), local source, module13/higgstools.py and module14/external.py | Explicit widths/BR/cross-section input is supported. Existing approximate h125 use retained. Missing charged loops/neutral widths/production stay DIAGNOSTIC_ONLY or NOT_EVALUATED. Supplied charged production now requires an artifact-bound contract. |

## Corrected LFV control and model gap

The [publisher erratum](https://link.springer.com/article/10.1007/JHEP07(2026)184)
was read, including the PDF. The pinned April 30 correction diff changes
one-loop signs and fermion-loop prefactors/conjugations. Source structures
were checked against corrected Eqs. (5.7)/(5.8) and the bracketed Phi2 term
in f8e; this is a partial source check, not a complete symbolic validation.
The [paper](https://arxiv.org/html/2410.17313v3) explicitly requires complete
bosonic gauge-invariant groups. Individual W/Z/photon terms must not be
removed to manufacture a Zee result.

The **unchanged upstream example** completed, exit 0. Its input even uses
`melectron=511e-5`; it was deliberately not silently corrected. Measured
partial widths (GeV), recorded with complex coefficients in
`public_lfv_control.json`:

| Channel | Original-example result |
|---|---:|
| mu -> e gamma | 2.3799715772393228e-24 |
| tau -> e gamma | 1.7353342836749715e-21 |
| tau -> mu gamma | 5.92354251264994e-22 |

All three rate identities close exactly at recorded precision. Setting only
lepton off-diagonal rho entries to zero gives exactly three zero rates,
as required by flavor conservation at this upstream spectrum. These checks
supply a reproducible control, **not an independent nonzero published
benchmark comparison**. A full Zee decoupling/convention map has not been
established. Neutral fermion-loop terms are candidates for later matched
reuse; none was spliced into Module4. Missing singlet-F amplitudes, mixed
charged states and their potential/gauge contributions remain UNKNOWN.

Reproduce only against already pinned local source:

```sh
python3 -m module14.public_reuse probe --tool general_2hdm --source PINNED_SOURCE --output NEW_REPORT.json
python3 -m module14.public_reuse lfv-control --source PINNED_SOURCE --output NEW_CONTROL.json
```

This interface downloads nothing and accepts no physics cards or proposals.
There is no assumed upstream self-test suite: example execution, our rate
identity and the analytic null are separately identified.

## Existing Zee FlavorKit evidence, inspected read-only

A separate preexisting `research/zee-spheno-flavorkit-pilot` checkout contains
experimental generated Zee Fortran and saved comparisons. The inspected
checkout commit, generated/source hashes and **only the four original D12
card comparisons** are recorded in `public_spheno_evidence.json`. All nine
recorded helper-source hashes and three frozen-reference hashes matched;
the frozen reference hashes also match this checkout. No native executable
was built or run during this task, and no additional benchmark was created.

That research evidence derives `K2L=-conj(C_L), K2R=-conj(C_R)` with matched
mass normalization for a patched scalar one-loop subset. For the four
original cards, maximum neutral-component relative residual is about
6.81e-11, charged about 2.62e-15. Unmatched full-input shifts reach 1.97e-7;
these are **not theory uncertainties**. Reconstructed native rates agree
within 2.59e-9 relative output rounding. Its loop-function precision patches
and generated-source changes are experimental and not upstream stock code.

Actual Lto3Lp source consumes K1/K2, scalar/vector/tensor four-lepton
operators and interference. MuEconversion consumes lepton-quark operators
and nuclear inputs. Their presence is not a per-operator Zee validation.
No new mu->3e or conversion constraint is enabled. The separate
[FlavorKit paper](https://arxiv.org/abs/1405.1434) and
[one-loop decay framework](https://arxiv.org/abs/1703.09237) describe generic
capabilities, not a successful full Zee backend.

## Vacuum and Higgs integration gates

Vevacious source invokes external PHC/HOM4PS tooling; the build instructions
include automatic dependency downloads. No build/install was attempted.
A Zee adapter would need a checked full real-field potential, gradients,
charged/CP directions, gauge reduction, energy normalization and a verified
deeper-stationary witness protocol at existing D10 PASS/UNKNOWN points.
Those model gates are absent. Executing its two-field THDM example would
not test Zee applicability and would violate the active no-vacuum-search
scope. Both proposed Zee benchmark comparisons remain NOT_EVALUATED.

HomotopyContinuation's [certification contract](https://www.juliahomotopycontinuation.org/HomotopyContinuation.jl/stable/certification/)
applies to supplied solutions of square polynomial systems. Singular roots,
gauge orbits and positive-dimensional sets require separate treatment.
No certificate of root exhaustion or global Zee vacuum is asserted.

HiggsTools' [explicit-input interface](https://higgsbounds.gitlab.io/higgstools/alternative_input.html)
can consume independently validated corrections later. Until such inputs
exist, retain the frozen complete **on-shell tree two-body** D4 widths.
All 19 production integrations are historical evidence and were not rerun.
