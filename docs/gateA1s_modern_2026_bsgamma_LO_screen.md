## User-executed A1S result and post-run assessment (13 October 2026)

Gate A1S actually ran on AF:

    STATUS GATE_A1S_2026_MODERN_EQ4_LO_LINEARIZED_ZEE_SCREEN_NOT_EXCLUSION

    mH      dC7_LO              dC8_LO              Eq4 BR *1e4
    300    -0.116249118178    -0.112989421480       4.77333714609
    670    -0.0461729790719   -0.0514806431451      4.04413024110
    700    -0.0436165310583   -0.0489292812783      4.01686392687
    1000   -0.0268581378129   -0.0315087201513      3.83662158831
    2000   -0.00958410462722  -0.0119866333575      3.64745185843

    mH1=300, mH2=700, gamma=1.089
    w_light=0.2147133902; w_heavy=0.7852866098
    Zee dC7=-0.0592117200769; dC8=-0.0626838511569
    Zee Eq4 predicted BR=4.17928885635e-4

This is 0.68928885635e-4 above the new experimental
3.49e-4 average. If and ONLY IF we pretend that the
0.14e-4 SM theory error and 0.19e-4 experimental error
are independent, fully applicable to the linearized BSM
approximation, and Gaussian, the discrepancy would be

    z_naive = (4.17928885635-3.49)/sqrt(0.14^2+0.19^2)
            = 2.92061.

This is NOT a model exclusion significance. In fact, the
SAME naive diagnostic gives z=2.3479 at mH=670 and
z=2.2324 at mH=700 for pure Type-II, despite the 2026
authors' FULL 2HDM analysis quoting a 670-GeV 95% CL
lower mass limit. This is a direct warning that the
generic LO-linearized Eq4, NP higher-order differences
and/or statistical prescription MUST NOT be treated as
their actual model-specific 95% CL likelihood.

**Non-commensurate perturbative comparison, NOT an error model:**

For reference only, compare the A1S linearized Eq4 NP shift
relative to the 2026 SM constant with the A1R full legacy
vendor single-TypeII BR shift relative to the legacy SM.
These are from different perturbative schemes and hadronic
input implementations, so the relative differences cannot
be converted into a theoretical uncertainty or correction
factor:

    mH       legacy NP shift*1e4     2026 Eq4 LO shift*1e4    difference
    300      1.1290725865           1.2333371461             +9.23%
    700      0.3968852492           0.4768639269            +20.15%
    1000     0.2383289497           0.2966215883            +24.46%
    2000     0.0813689353           0.1074518584            +32.06%

DO NOT obtain the 2026 full Zee BR by adding the weighted
legacy single-state BR shifts to the new 2026 SM value:
nonlinear terms in the full rate and newer charm-mass
matrix elements make this scientifically uncontrolled.
Likewise, DO NOT average full BRs of two charged states.

**Machine-checkable sensitivity diagnostic committed after user A1S run:**

    scripts/gateA1t_check_2026_screen_vs_legacy_shifts.py
    tests/test_gateA1t_check_2026_screen_vs_legacy_shifts.py

Runs only on already-produced JSON files; NO new AF physics
generation, Mathematica, or SuperIso calculation:

    cd /home/aalida/zee
    git switch gateA1p-independent-hepfit-typeii-matching
    git pull --ff-only
    python3 -m unittest discover -s tests \
      -p 'test_gateA1t_check_2026_screen_vs_legacy_shifts.py' -v
    python3 scripts/gateA1t_check_2026_screen_vs_legacy_shifts.py \
      --legacy-A1R work/gateA1r_observable_v1/gateA1r_br_pilot.json \
      --modern-A1S work/gateA1s_modern_2026_v1/modern_2026_LO_Zee_screen.json \
      --output work/gateA1s_modern_2026_v1/legacy_vs_modern_shift_diagnostic.json

Expected status:

    GATE_A1T_LO_VS_LEGACY_NP_SHIFT_DIAGNOSTIC_NOT_PRECISION_OR_EXCLUSION

The comparison script checks matching scale mu0=160,
source mass grids, Type-II tanbeta, 2026 Eq4 coefficients,
mixing unitarity and predicted mixed-state Eq4 closure.
It never produces a physical 95% CL allowed/excluded label.

**Next full-physics milestone:** obtain or reproduce updated 2026
full-TypeII BR(mH) as a function of charged mass and a matched
flavour likelihood. Then compute BOTH mixed charged-Higgs contributions
with consistent NLO/NNLO matching, RG, nonperturbative and quadratic
new-physics effects. The known full-TypeII 670-GeV 95% CL
threshold is not enough to assign a two-state bound. Existing
A1S indicates 300+700, gamma=1.089 requires close scrutiny.

# Gate A1S — updated 2026 B -> Xs gamma LO screen for Zee-type scalar sector

## Modern benchmark: authoritative primary reference

M. Misiak et al., The Inclusive Bbar -> Xs gamma Decay Rate with Higher
Precision, arXiv:2608.29863v1 (30 August 2026):
https://arxiv.org/html/2608.29863

2026, Eq. (1): experimental B = (3.49 +/- 0.19) x 10^-4.
2026, Eq. (3): SM B = (3.54 +/- 0.14) x 10^-4.
Photon cut: E_gamma > 1.6 GeV.
2026 full 2HDM Type-II analysis: charged-Higgs M > 670 GeV at 95% CL.

2026, Eq. (4): for generic small new-physics matching shifts at
EXACT mu0 = 160 GeV, the approximate formula is

   B(Bbar -> Xs gamma) * 1e4 =
            (3.54 +/- 0.14) - 8.51 Delta_C7 - 2.16 Delta_C8.

The 2026 authors say this EQ4 NEGLECTS terms QUADRATIC in the NP
Delta_C7/8, and that a more refined BSM calculation should add
higher-order matching. Their quoted 670 GeV Type-II bound DOES
include the known 2HDM higher-order effects. Thus NO point may
be excluded from Eq4 alone without defining a defensible
uncertainty treatment and checking the linearization.

This August 2026 study supersedes our 2020 (3.40 +/- 0.17)x1e-4
SM benchmark for publication. The historical benchmark remains
useful ONLY as a legacy-SuperIso internal calibration.

## User-confirmed A1R original-observable pilot

SuperIso v5, with vendor or authenticated KIT-original 2012 NNLO
matching C3-C6 and RAW C7/C8 substitutions, gives

    STATUS GATE_A1R_SINGLE_TYPEII_OBSERVABLE_BR_PILOT_AWAITING_INDEPENDENT_ERROR_BUDGET

    SM   0.0003382457724

    mH     vendor full BR       original KIT C2 substituted BR
    300     0.00045115303105    0.00045115104112
    700     0.00037793429732    0.00037793243506
    1000    0.00036207866737    0.00036207719938
    2000    0.00034638266593    0.00034638190480

The KIT substitution changes these observable values by only
0.00022-0.00049 percent RELATIVE. No new physical exclusion
follows from this tiny difference.

Old SuperIso SM BR is 0.516 percent BELOW the 2020 reference and
4.450 percent BELOW the August 2026 SM reference. We MUST NOT
correct our vendor results by merely multiplying by 3.54/3.382:
the 2026 update changes exact-charm NNLO interferences,
kinetic-scheme SM input normalization and nonperturbative terms,
not just an overall normalization factor.

## A1S independent modern screen via original LO Wilson coefficients

Added:
- scripts/gateA1s_probe_modern_2026_lo.c
- scripts/gateA1s_run_modern_2026_screen.py
- tests/test_gateA1s_modern_2026_screen.py

C matching probe links exactly to the previously source-pinned
A1M SuperIso v5 src/libsuperiso.a (same headers, same original
vendor source), uses the actual running mt, and computes SM
and Type-II single charged-Higgs LO matching at mu0=160 GeV,
returning Delta_C7, Delta_C8 after subtracting SM.
The Type-II quark couplings are lambda_u=cot(beta),
lambda_d=-tan(beta).

For two charged mass eigenstates with doublet contents

   w1=cos(gamma)^2, w2=sin(gamma)^2,

combine Wilson coefficients AT MATCHING SCALE:

   Delta_Ci^Zee =
         w1*Delta_Ci^TypeII(mH1) +
         w2*Delta_Ci^TypeII(mH2),   i in {7,8}.

Then use the independent AUGUST 2026 generic Eq4 exactly once
with the mixed DELTA_C7/8.

This is NOT a weighted average of independently calculated
branching ratios, and no old SuperIso BR is mixed into the
modern 2026 SM central value. It is a linearized, LO-new-physics
screen and is NOT a full NNLO Zee observable.

Default illustrative benchmark:
mH1=300 GeV; mH2=700 GeV; gamma=1.089 rad;
tanbeta=5.597170833164245. In addition to the 4 original A1P
masses, we probe 670 GeV as a reference to the modern full-TypeII
bound (but DO NOT equate the generic LO approximation with
the 2026 team's full NNLO exclusion).

## AF commands

    cd /home/aalida/zee
    git switch gateA1p-independent-hepfit-typeii-matching
    git pull --ff-only

    python3 -m unittest discover -s tests \
        -p 'test_gateA1s_modern_2026_screen.py' -v

    python3 scripts/gateA1s_run_modern_2026_screen.py \
        --vendor-root work/gateA1m_isolated_nlo_v1/isolated_superiso \
        --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
        --output-dir work/gateA1s_modern_2026_v1 \
        --mH1 300 --mH2 700 --gamma 1.089 \
        --tanbeta 5.597170833164245

Outputs after execution:
work/gateA1s_modern_2026_v1/modern_2026_LO_Zee_screen.json
work/gateA1s_modern_2026_v1/matching_raw.log
Compiled C probe: work/gateA1s_modern_2026_v1/gateA1s_probe_lo

The implementation prints all LO coefficients, w1 and w2, and
the resulting LINEARIZED Eq4 value in units 1e-4. It records
source and binary checksums and explicitly states:

    GATE_A1S_2026_MODERN_EQ4_LO_LINEARIZED_ZEE_SCREEN_NOT_EXCLUSION
    FULL_2026_NNLO_BR_VALIDATED False
    ZEE_EXCLUSION_CALCULATED False

## Gate A1S / 2026 precision requirements before flavor-exclusion scan

- Run the actual AF C probe and regression tests. Synthetic
  endpoint/degenerate-mass unit tests alone are not full numerical
  original-source validation.
- Verify exactly the 160 GeV matching scale and correct Q7/Q8
  operator normalization in the 2026 paper and SuperIso at LO.
- Determine when quadratic NP terms omitted in Eq4 materially
  modify benchmarks (especially low charged-Higgs masses).
- Reproduce a 2026 Type-II benchmark with the appropriate FULL
  NNLO observable and error prescription before promoting
  any 2026 generic LO-screen to a 95% CL exclusion.
- For the Zee scalar-sector scan, include the two charged
  matching contributions and an uncertainty/correlation analysis.
  For a COMPLETE Zee neutrino model also impose neutrino
  oscillation and LFV checks; quark Type-II constraints do not
  automatically fix leptonic couplings.

Gate A1S Python and C code are COMMITTED, not yet executed on AF.
No Zee point is certified allowed or excluded.
