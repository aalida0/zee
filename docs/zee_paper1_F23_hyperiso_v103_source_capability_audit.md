# HyperIso v1.0.3 feasibility audit for the F22 general Zee charged-Higgs paper

**Date:** 2026-10-25. **Verdict:** USE AS A SECOND higher-order cross-check and a candidate C++ two-state Wilson-observable engine, NOT a native/general-Zee plug-in, NOT a validated Misiak-2026 NNLO exclusion.

## Audited sources (exact public tag)

- Original release tag: `Hyperiso/Hyperiso@v1.0.3`, source commit `09d26ac6e71d1528922097a896d15693589f636b` (PyPI signed release).
- Project/paper: https://hyperiso.in2p3.fr/ ; https://arxiv.org/abs/2607.18222 .
- Native matching: `Hyperiso/Hyperiso/core/src/PhysicalModel/domain/WCoef/BSM/BWilsonTHDM.cpp`.
- Scalar THDM input: `.../Helper/BSM/THDMParametersHelper.cpp`.
- Inclusive operator response: `Hyperiso/Hyperiso/core/src/BusinessLogic/domain/Decays/BXsDecay.cpp`.
- C++ injection: `Hyperiso/Hyperiso/core/src/PhysicalModel/domain/WilsonMatchingPatch.h`, `.../BusinessLogic/adapters/ObservableInterface.h/.cpp`, `.../PhysicalModel/adapters/WilsonInterface.cpp`.
- Packaged Python API: `.../core/src/Python/src/wilson/binding_wilson.cpp`; C++ matching-patch API is **not bound** in 1.0.3 Python (the unrelated `CustomWilsonGroupConfig` *is* bound but defaults to **identity running**, so does not automatically inject into the physical SM B-operator sector).
- Native reference: `reproducibility/manifest.json`, `reproducibility/expected_outputs/observables_sm_nnlo.txt` (SM `BR_B__Xs_gamma=0.00032967` at the *tag's reference inputs*), `reproducibility/expected_outputs/wilson_b_thdm_spectrum_nnlo.txt` (native single charged Type-II B-sector NNLO WC reference).
- Installation metadata: https://pypi.org/project/pyhyperiso/1.0.3/ (`pyhyperiso==1.0.3`, requires Python >=3.10,<3.13; tagged Linux wheels for 3.10/3.11/3.12).
- Modern independent precision target: Misiak et al., https://arxiv.org/abs/2608.29863 , SM `(3.54+-0.14)e-4`, experimental `(3.49+-0.19)e-4`, single-TypeII mH+>670 GeV 95% CL. Paper appeared AFTER HyperIso 1.0.3 and must not be assumed implemented.

## Established source-level capability

1. HyperIso includes `C3_THDM` through `C8_THDM` with explicit LO/NLO/NNLO charged-Higgs matching terms where the particular operator order is nonzero. In particular C7/C8 define all LO, NLO and NNLO high-scale functions; C4 NLO and C3/C4/C5/C6 NNLO are present. These are *fixed published-era source implementations*, not an independent 2026 algorithm.
2. `THDMParametersHelper.cpp` reads a **single charged Higgs MASS[37]**, quark Yukawa factors `YU[2,2]`/`YD[2,2]`, `tanbeta=MINPAR[3]`; thus the native THDM input is **one charged state**. Merely passing the two charged masses/angle in separate Zee SLHA blocks cannot enable the mixed spectrum automatically.
3. The `BXsDecay` C++ observable reads `WGroup::B` LO/NLO/NNLO coefficients, BPrime, and matching Cw, and evaluates quadratic Wilson interference plus QCD/nonperturbative contributions. Its old SM reference `3.2967e-4` is ~6.9% below the 2026 published 3.54e-4, for possibly both model-input and theory-update reasons. HyperIso v1.0.3 is NOT certified as the 2026 theory.
4. The **public C++** `WilsonMatchingPatch` is additive on specific operator/order/contribution; `ObservableInterface::add_matching_patch()` sends it through the actual observable Wilson builder. Unlike `CustomWilsonGroupConfig`'s identity running, this is the promising way to supply genuine NP shifts to the standard B-operator RG/BR engine. Must validate patch registration, convention, running, and order composition at numerical runtime.
5. The **Python wheel's** `binding_wilson.cpp` exposes lambda-defined `CustomWilsonGroupConfig` but **does not expose** `WilsonMatchingPatch` or `ObservableInterface::add_matching_patch`. Thus v1.0.3 Python alone cannot safely implement the above physical injection just by registering a custom group. A **C++ bridge** is preferable; alternatively develop bindings and recompile source.
6. MARTY interfaces to generic BSM matching at LO and thus cannot automatically provide our Zee mixed-spectrum NLO/NNLO. Using MARTY with `--order NNLO` does not make BSM matching NNLO.

## Correct two-state charged matching for the specific Type-II-quark Zee ansatz

At fixed `mu_W`, same beta, same running top, and **for each perturbative operator/order**:

```text
DeltaCi_Zee^(k)(muW)
   = cos(gamma)^2 * DeltaCi_TypeII^(k)(mH1, tanbeta, muW)
   + sin(gamma)^2 * DeltaCi_TypeII^(k)(mH2, tanbeta, muW)
   k in {LO, NLO, NNLO}; i=3..8 where contributions exist
Ci_total = Ci_SM + DeltaCi_Zee (with consistent alpha_s/(4pi) order weights)
```

This form assumes exactly our **CP-conserving Type-II quark** Zee charged mixing ansatz; it is not a general arbitrary flavor Yukawa ansatz. Mass and Yukawa dependence are evaluated for each physical eigenstate, not by averaging branching ratios or setting a mass-averaged charged Higgs.

**Do not do**
`BR_Zee = cos²(gamma)*BR_TypeII(mH1) + sin²(gamma)*BR_TypeII(mH2)`.
Quadratic interference and the shared SM baseline make that false.

Scientific implementations must check:
- `gamma=0` -> exact single H1 Type-II; `gamma=pi/2` -> H2 Type-II;
- `mH1=mH2` -> single-state Type-II (mixing independence);
- `mH1,mH2` large -> decoupling to same-scheme HyperIso SM;
- `C7,C8` LO comparison with our independently coded F19d at EXACT `mt(muW)` and matching conventions, not just sign;
- C3..C8 NLO/NNLO order definitions and C7/C8 **raw vs effective basis**; compare to original SuperIso F3, HyperIso tagged single Type-II and independently source-pinned HEPfit;
- source/tag SHA, matching/running scales, QCD mass schemes and gamma normalizations;
- reference SM, same-scheme Type-II curve and whether it reproduces known (old vs 2026) single-TypeII bounds with a real nuisance/likelihood before any 95% CL;
- quadratic two-state Wilson response, not Gamma/BR linearization;
- cross-code disagreement is not a probabilistic error bar.

## Recommended *small* executable integration, then 9 -> 157

**Stage A** (Ubuntu CPython3.10+): source-locked HyperIso v1.0.3 smoke on SM and single Type-II, reproduce tagged R3/R6 reference outputs and identify the exact B-operator matching convention, order, and normalization. Not the paper exclusion result.

**Stage B**: implement one C++ bridge using the documented public `ObservableInterface::add_matching_patch` to add two-state complex `DeltaC_{3..8}^{(0,1,2)}` BSM at **matching level** to native SM coefficients, then read `BXsDecay`. Extract single-TypeII matching vectors separately from **the same HyperIso THDM kernel** at mH1 and mH2 (do not substitute our F19d analytical input as a higher-order coefficient). Compile with tagged C++ core. Crosscheck source-pinned F3 SuperIso plus independent HEPfit matching algebra.

**Stage C**: take frozen F22 priority 9 actual physical spectra, evaluate HyperIso old-era coherent two-state BR as a **conditional** observable. If pure Type-II, equal mass, gamma endpoints, basis, scales, and old reference checks pass, propagate same engine to all 157, and then decide whether a 2026-calibrated prediction/likelihood can be created. Prefer explicit separation between legacy HyperIso theory and any modern public Misiak 2026 NP Wilson response.

**Stage D**: do not call anything a 2026 robust experimental exclusion until full 2026 theory/bound calibration with appropriate uncertainties. HyperIso and SuperIso share substantial formula ancestry; a crosscheck between them is valuable implementation-wise but not fully theoretically independent.

## Environment

CERN LXPLUS output shown in F21c traceback used Python 3.9. `pyhyperiso==1.0.3` requires 3.10+ and provides no cp39 wheel. Ubuntu 22.04 default Python3.10 is a convenient first machine:

```bash
python3 --version
python3 -m venv ~/.venvs/hyperiso-v1.0.3
source ~/.venvs/hyperiso-v1.0.3/bin/activate
python -m pip install --upgrade pip
python -m pip install 'pyhyperiso==1.0.3'
python -c "import pyhyperiso; from pyhyperiso.Core import HyperisoMaster; from pyhyperiso.Observable import ObservableInterface; print(pyhyperiso.__version__)"
```

For **CLI** `hyperiso-ui` build the native `BUILD_WITH_CLI=ON` CMake target: the published PyPI packaging describes Python bindings and does NOT specify a Python console-script entry point. Do not assume `hyperiso-ui` binary is installed with pip.

**Feasibility verdict:** **YES as a substantial C++ source-level NLO/NNLO crosscheck / possible two-Higgs BR kernel**, NO as a one-command complete Zee/2026 NNLO likelihood or native F22 ingestion. The proof still requires executing the matching-patch physics integration against actual linked tagged libraries; no model allowed points have been established.
