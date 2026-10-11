# Gate A1P — independent HEPfit Type-II LO/NLO/NNLO matching benchmark

**Scope:** Independent matching-level comparison for the Type-II charged-Higgs
contributions to B -> Xs gamma at 300, 700, 1000 and 2000 GeV.
**Not** a complete independent NNLO branching-ratio prediction, and
**not** a Zee benchmark exclusion.

## Literature and independent reference

Thomas Hermann, Mikołaj Misiak and Matthias Steinhauser,
[arXiv:1208.2788](https://arxiv.org/abs/1208.2788),
JHEP 11 (2012) 036, computed three-loop charged-Higgs matching.
The HEPfit Collaboration independently implements the Type-II
LO/NLO/NNLO Wilson coefficients in THDMMatching::setWCbsg:
https://github.com/silvest/HEPfit/blob/master/THDM/src/THDMMatching.cpp.

HEPfit indices 6 and 7 in its 0-based Misiak operator basis
correspond to C7 and C8. We compare C7 and C8 at all three orders,
C4 at NLO, and C3-C6 at NNLO: **44 comparisons** over four masses.

HEPfit's code is GPL. Gate A1P fetches only the original source file
at runtime under the ignored work/ folder, pins its Git blob to
8029be52c3e2f83490dfe3199f80e5db484dd23b, extracts the
unaltered upstream method, and generates a small self-contained
C++ test harness linked to GSL. The original third-party source
is not copied into this Zee GitHub repository.
See upstream HEPfit doc/COPYING for terms.

This procedure constitutes an independent **matching formula**
implementation, not an independent RG or inclusive decay-rate code.

## Inputs, conventions and caveats

- Frozen Type-II Yukawa texture: lambda_u=cot(beta),
  lambda_d=-tan(beta); beta=1.394 radians.
- muW=2*mW=160.7384 GeV.
- Candidate running mt(muW)=163.10709645657502 GeV. **Important:
  this number was inferred from SuperIso LO C7 matching**, and
  has NOT been independently checked against SuperIso's
  running-top prescription. All NLO/NNLO coefficient comparisons
  at this stage are conditional on that common mass input.
- The A1M isolated SuperIso 5.0 library includes the confirmed
  four-line NLO clipping correction. The official vendor tree
  is not modified.
- HEPfit original values and A1M charged-Higgs delta coefficients
  are compared at the same parameters and on the same Ci^(n)
  basis, before multiplication by powers of alpha_s/(4 pi).
- The SuperIso A1L driver is run at gamma=0, so the light
  charged Higgs contribution is the pure Type-II limit.
- Pilot comparison tolerances: LO abs 1e-7 / rel 1e-6;
  NLO abs 0.002 / rel 0.5%; NNLO abs 0.35 / rel 3%.
  **These exploratory tolerances are not publication-level
  precision standards**. Every NNLO residual exceeding 1% relative
  (when its coefficient magnitude exceeds 1e-3) is separately
  recorded as a precision-review flag, even if the broad pilot
  tolerance technically passes. Any discrepancy must be audited
  for scheme and NNLO expansion differences before final validation.

## AF run

Requires Python, GNU C/C++, curl, GSL headers/library, and the
existing Gate A1M source and static library. Activate a CERN LCG
view providing GSL if the host C++ environment lacks it.

    cd /home/aalida/zee
    git fetch origin gateA1p-independent-hepfit-typeii-matching
    git switch gateA1p-independent-hepfit-typeii-matching

    python3 -m unittest discover -s tests \
      -p 'test_gateA1p_hepfit_typeii_matching.py' -v

    bash scripts/gateA1p_run_hepfit_matching.sh \
      /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
      work/gateA1p_hepfit_typeii_v1

    cat work/gateA1p_hepfit_typeii_v1/result.json

Runner provenance: SHA for original HEPfit source and generated
reference, build logs, standalone ref program output per mass,
SuperIso A1M matching program output per mass, comparison JSON,
and source/binary hashes.

To verify the actual SuperIso mt(muW) before a stronger physics
claim, inspect the top running-mass expression in the audited
SuperIso src/wilson.c. Once verified, rerun in a fresh output
directory with this optional environment variable:

    GATE_A1P_MT_MUW_GEV=<verified_mt_muW> \
      bash scripts/gateA1p_run_hepfit_matching.sh \
      /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
      work/gateA1p_hepfit_typeii_verified_mass

The comparator writes a result JSON and returns a nonzero status
when matching differences exceed the tolerances. Do not silence
mismatches with an undocumented common scale factor.

## Independent external physics validation STILL necessary

1. Check exact top-mass scheme and scale, basis and perturbative
   normalization across both implementations; repeat matching
   around NNLO interpolation boundaries.
2. Obtain a **full independent Type-II NNLO B -> Xs gamma curve**
   (with documented SM masses, alpha_s, photon-energy threshold,
   nonperturbative terms, QCD evolution and uncertainties).
   Matching-only agreement does not verify a final branching ratio.
3. Check all primed coefficients and contributions outside the
   projected quark sector of the Zee model.
4. Quantify matching/low-scale variations, experimental averages,
   and correlated theory uncertainties before deriving exclusions.

Misiak and Steinhauser, [arXiv:1702.04571](https://arxiv.org/abs/1702.04571),
EPJC 77 (2017) 201, report Type-II 95%-CL lower mass bounds
570–800 GeV depending on statistical construction (583 GeV
conservative two-sided). Those bounds are **not** a numeric
rate reference and cannot be imposed directly on the mixed
two-charged-state Zee model.

**Status: independent Type-II matching test created, AF execution
pending; Zee BR remains a provisional candidate.**
