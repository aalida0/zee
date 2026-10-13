# Gate A1R: physical inclusive Bbar -> Xs gamma pilot

Status: IMPLEMENTED, NOT YET EXECUTED on AF. This is a physical
branching-ratio pilot through the original SuperIso v5 observable
routine, not an extracted Zee exclusion.

## Published reference observables

- HFLAV latest results https://hflav.web.cern.ch/results :
  B(B->Xs gamma, E_gamma > 1.6 GeV) = (3.49 +/- 0.19)*1e-4.
- SM NNLO Misiak, Rehman, Steinhauser, arXiv:2002.01548:
  B_SM = (3.40 +/- 0.17)*1e-4 at E_gamma > 1.6 GeV.
- Single Type-II 2HDM historical Misiak and Steinhauser,
  arXiv:1702.04571 / EPJC 77 (2017) 201:
  mH+ > 570--800 GeV at 95% CL, METHOD DEPENDENT.
  This is a methodological control, NOT a universal Zee mass bound.

**The experimental average and SM theory have different uncertainties,
correlations and provenance. Do not apply either quoted uncertainty as a
naive 95%-CL cut to our own model prediction.**

## Real observable implementation

C driver: scripts/gateA1r_superiso_br_pilot.c
Python: scripts/gateA1r_run_br_pilot.py
Tests: tests/test_gateA1r_run_br_pilot.py

The driver links against the PROVENANCE-PINNED isolated A1M SuperIso-v5
library (libisospin.a) and runs actual:

  Init_param -> slha_adjust -> CW_calculator(muW)
  -> C_calculator_base1(muW,mub) -> Cprime_calculator(muW,mub)
  -> bsgamma(C0b,C1b,C2b,Cp,mub,muW)

Pinned vendor source bsgamma.c fixes E0=1.6 GeV, with perturbative
and nonperturbative matching and RG evolution. This is NOT a toy
BR proportional only to the squared LO C7.

Cases:
  S: SM from original SuperIso, SM=1.
  V: one Type-II charged Higgs with Yukawa lambda_u=cot(beta),
     lambda_d=-tan(beta), isolated A1M matching.
  A: same single Type-II case, but overwrite ONLY NNLO charged-Higgs
     matching coefficients C2w[3..8] with EXACT original 2012 KIT
     Mathematica cH[2,3..6] and raw cH[3,7/8].
     Set C2w[i] = C2w_SM[i] + C2_KIT_charged[i].

LO and NLO matching, all SM input parameters, physical SuperIso kernel,
and full single Type-II charged state remain IDENTICAL between V and A.
No author coefficient is converted into effective basis before injection;
the original vendor RG function does that itself. The bsgamma kernel
internally calls CW_calculator to obtain LO charged-Higgs matching for
nonperturbative Kt0; our single-state param still has the same charged
state, so that internal call includes it consistently at LO.

User already evaluated original c2HDM.m with Mathematica, and the
runner uses the resulting exact-SHA256 original numerical data. It
refuses wrong muW, running mt(muW), tanbeta or mH, rather than mixing
different definitions and scales. The original source SHA256 is

  cb2d1328bc2542a6324e73efe6f89c43381efdc93db5e3b0ca8348db980645d8

Four original controls: 300, 700, 1000, 2000 GeV.
Additional 580-GeV V-only historical control. SM case too.

## Run on AF

    cd /home/aalida/zee
    git switch gateA1p-independent-hepfit-typeii-matching
    git pull --ff-only
    python3 -m unittest discover -s tests -p 'test_gateA1r_run_br_pilot.py' -v

    python3 scripts/gateA1r_run_br_pilot.py \
      --vendor-root work/gateA1m_isolated_nlo_v1/isolated_superiso \
      --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
      --authors-source work/gateA1q_original_nnlo_v1/c2HDM.m \
      --kit-provenance work/gateA1q_original_nnlo_v1/kit_source_provenance.json \
      --authors-values work/gateA1q_original_nnlo_v1/original_mathematica_values.txt \
      --existing-result work/gateA1p_hepfit_typeii_v1/result.json \
      --output-dir work/gateA1r_observable_v1 --make-if-missing

If the pinned library is absent, only the already isolated SuperIso
tree is built. If the compiler fails, provide the compiler stderr;
do not replace the library with another SuperIso version.

To prepare the four original NNLO reference text files with NO
compiler or observable evaluation, append --prepare-only.

Results: work/gateA1r_observable_v1/gateA1r_br_pilot.json;
raw 17-digit BR, matching and low-scale Wilson diagnostics are in
work/gateA1r_observable_v1/br_raw_driver_output.log.

CAUTION: If the SuperIso SM defaults produce a different matching
scale or running mt from A1P, the author-NNLO mode HALTS
with A1R_ORIGINAL_INPUT_MISMATCH. This must be resolved by
regenerating the original Mathematica inputs, not bypassing a guard.

## Hard remaining scientific gates

- Verify actual compiled SM result against published benchmark, accounting
  for legacy SuperIso inputs, nonperturbative prescription and scheme.
  The runner's broad 2.5e-4 to 4.5e-4 SM sanity range is NOT a precision
  or exclusion criterion.
- Compare vendor V and original KIT A physical branching fractions
  at each mass and understand the residual.
- Validate complete observable predictions with an independent
  implementation or independently published parameter-matched benchmark.
- Perform appropriate scale, SM-input, and theoretical uncertainty analysis
  and define the statistical treatment for the HFLAV measurement.
- Only then extend to 2-state Zee-type scalar sector via SUM OF
  COEFFICIENTS, not a weighted average of branching ratios.
- The bsgamma() internal high-scale recalculation for the
  nonperturbative Kt0 term must be made LO-consistent with the two-state
  matching before even a provisional Zee 2-state BR calculation.
- A full Zee neutrino-mass-model claim additionally needs neutrino
  oscillation and lepton-flavor-violation checks. Type-II QUARK
  couplings alone do not force the excluded Zee-Wolfenstein lepton texture.

No physical allowed/excluded Zee point can be inferred from the pilot.
