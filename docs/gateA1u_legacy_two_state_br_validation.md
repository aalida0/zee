## A1U AF physical context diagnostic (13 October 2026): revised two-stage check

The user reran the 11 synthetic A1U tests: **11/11 PASS**.
The first physical run in the no-reload branch then printed

    A1U_NO_RELOAD_CONTEXT_INVARIANCE_FAILED
    SM=0.00039250054453230092
    H1=0.00039369511227532023
    H2=0.00039296216778595783

This mismatch is **real, at observable/numerical level** but does
NOT establish an intrinsic model-context dependence inside
bsgamma(). The previous A1U code claimed these BR evaluations used
identical mixed *low-scale* Wilson vectors; inspection of the actual
C driver showed that was FALSE. The routine real_br() always
re-ran C_calculator_base1() in the context-specific parameters, so
these were only identical *high-scale* coefficients. Thus, either
parameter dependence in the RG routine, or in the observable
function, or both could cause the 1.2e-6 difference.

The corrected physical diagnostic is now staged:

**Stage 1 (RG):** Use exactly identical MIXED high-scale C0/C1/C2
vectors. Evolve them three times under param.SM and charged-Higgs
mass contexts SM/H1/H2. Compare ALL 1..10 low-scale LO/NLO/NNLO
coefficient arrays and log

    RG_MAX_ABS_DELTA_H1, RG_MAX_ABS_DELTA_H2.

If either maximum exceeds 1e-10, hard stop with
A1U_FIXED_HIGH_RG_CONTEXT_DEPENDENCE_NEEDS_SOURCE_AUDIT. This
identifies the RG/context stage, not an alleged internal
bsgamma bug.

**Stage 2 (physical bsgamma):** Independently hold *identical*
low-scale LO/NLO/NNLO arrays AND Cp fixed, and evaluate the
original unchanged bsgamma() under SM/H1/H2 parameter contexts.
Log

    FIXED_LOW_BR_SM, FIXED_LOW_BR_H1, FIXED_LOW_BR_H2.

In no-reload mode, differences larger than 2e-12 hard-stop with
A1U_FIXED_LOW_BSGAMMA_CONTEXT_DEPENDENCE_NEEDS_SOURCE_AUDIT.
In verified affine reload mode, only the internal term is
interpolated while all low-scale coefficients stay fixed.

All diagnostic numbers are printed BEFORE a stage failure; the
full A1R physical endpoint checks remain mandatory after both
stages pass. The Python parser also requires/stores diagnostic
values and rejects inconsistent RG or observable-stage records.
No change to pinned SuperIso vendor physics source or library.
This is new GitHub code and has NOT YET run on the AF.

IMPORTANT: Do NOT respond to the failed numerical audit by
loosening tolerances or interpolating physical single-state BRs.
Determine the source of dependence, then validate the correct
model-consistent evolution/observable against A1R endpoints.

## A1U AF source preflight fix (13 October 2026)

On AF, the 8 existing Python tests all passed. The physical driver
did NOT start because the runner unconditionally required an
internal CW_calculator() call inside pinned SuperIso v5 bsgamma().
The PREVIOUS A1R source audit reported
bsgamma_internal_CW_reload_detected=false.

This was another inherited v3-style source assumption, NOT a
numerical mismatch and NOT evidence that SuperIso omits NP
matching. Two modes are now supported and explicitly recorded:

- **INTERNAL_CW_MODE=none**: If the actual v5 bsgamma() contains no
  internal CW_calculator() reload and no unresolved C0w index uses
  or direct param->SM/mass_H access, compute the mixed LO/NLO/NNLO
  Wilson arrays and evolve them normally. Evaluate the unchanged
  physical bsgamma() with the IDENTICAL mixed low-scale vectors under
  three SM/H1/H2 source-parameter contexts. Require
  |BR_SMcontext−BR_H1context| <= 2e−12 and likewise H2context,
  then take the SM-context mixed BR DIRECTLY (no interpolation).
  Any context dependence causes HARD failure.
- **INTERNAL_CW_MODE=reload**: If the pinned source contains one
  internal CW_calculator() call and the source guard identifies
  affine LO C7/C8 dependence, interpolate ONLY the internal
  reload contribution at fixed MIXED low-scale coefficients,
  as specified below. This branch retains the original
  strict source preflight.

A1U additionally checks that the preceding A1R source audit's
detected reload boolean agrees with the independent A1U source
classification. The C program requires the audited mode as an
explicit positional input, prints INTERNAL_CW_MODE=..., and the
Python parser checks it before accepting the observable.
Numerical gamma=0, gamma=pi/2, equal-mass, SM and independent
single-state closure to AF A1R is MANDATORY for either mode.

No project/vendor source was modified, only the A1U driver
and its audit/test harness. Three new tests exercise no-reload
source semantics, strict numerical context invariance, and
fail-closed mismatches. **This fix has not yet been run on AF.**

# Gate A1U: FULL LEGACY SuperIso v5 two-charged-Higgs observable

## Motivation and status

Gate A1T was executed on AF and reported:

  STATUS GATE_A1T_LO_VS_LEGACY_NP_SHIFT_DIAGNOSTIC_NOT_PRECISION_OR_EXCLUSION

The LO 2026 Eq.(4) NP shifts relative to the modern SM reference
and the *full legacy* SuperIso single-state NP shifts relative to
the legacy SM are not equivalent perturbative calculations:

     mH       legacy NP shift*1e4     2026 Eq4 LO shift*1e4     relative
     300      1.129072587            1.233337146              +9.2345%
     700      0.3968852492           0.4768639269             +20.152%
    1000      0.2383289496           0.2966215883             +24.459%
    2000      0.08136893525          0.1074518584             +32.055%

The previous A1S Zee two-state result is the **linearized**
2026 Eq.(4) BR = 4.17928885635e-4 for (mH1,mH2,gamma,tanbeta)
=(300,700,1.089,5.597170833164245).
The 2.92061 naive Gaussian pull is NOT a calibrated 95%-CL exclusion.
The 2026 2HDM-II 670-GeV bound refers to the authors' dedicated
higher-order implementation, not a simple Eq.(4) Gaussian cut.
Reference: Misiak et al. arXiv:2608.29863 (August 2026).

The required next discriminating calculation is a TRUE
two-charged-state physical BR with the existing fully compiled
legacy SuperIso-v5 observable kernel and BOTH new-physics
matching vectors at LO/NLO/NNLO. Do not create a weighted
average of two individual FULL branching ratios.

**Gate A1U's existing 8 tests passed on AF; the actual observable
run stopped at its mistaken mandatory internal-CW-reload source guard.
Conditional no-reload treatment is now committed but NOT YET AF-tested.**
When executed, it will calculate the real legacy SuperIso
physical two-state BR with three mandatory independent closure
checks. It CANNOT be interpreted as a 2026-compatible NNLO
precision result or a Zee scalar-sector exclusion.

## Model matching

The light/heavy charged Higgses H1,H2 have Type-II quark
Yukawas proportional to their doublet mixing fractions.
The charged-singlet carries no direct quark Yukawa.

For each LO, NLO, NNLO coefficient (including primed dipoles):

    C_i^Zee(muW) =
        C_i^SM(muW)
      + cos(gamma)^2 [ C_i^singleTypeII(mH1,muW) - C_i^SM(muW) ]
      + sin(gamma)^2 [ C_i^singleTypeII(mH2,muW) - C_i^SM(muW) ].

Then evolve ONE mixed vector to mub and evaluate the full
original vendor inclusive observable: perturbative, electromagnetic,
non-perturbative, and quadratic Wilson interference terms.

No original KIT matching substitution is needed for this
FIRST physical two-state observable pilot; A1R already showed
that the original NNLO charged-Higgs matching changes vendor
single-state full BR by <0.0005% in relative terms.
A later matching-systematics scan can test that at two-state
level as needed. A1U uses the exact compiled pinned A1M
isolated SuperIso-v5 archive and NLO clipping fix.

## Important nonperturbative / electromagnetic issue

Some SuperIso versions implement a direct CW_calculator() reload
inside bsgamma() for LO C7/C8 used in Kt0 and Cem, but the pinned
v5 A1R source audit does NOT detect such a call. The implementation
MUST branch according to the authenticated ACTUAL source, and
verify numerical parameter-context invariance when no reload exists.
The treatment below applies ONLY to source-verified reload mode.

The source-guarded A1U treatment keeps IDENTICAL mixed LOW-scale
Wilson arrays in THREE bsgamma evaluations with different internal
high-scale matching contexts SM, singleH1, singleH2:

    Bint_SM  = bsgamma(C^Zee_low, param.SM=1)
    Bint_H1  = bsgamma(C^Zee_low, param.SM=0,mH=mH1)
    Bint_H2  = bsgamma(C^Zee_low, param.SM=0,mH=mH2)

Then, IF AND ONLY IF the original pinned vendor bsgamma source has
the confirmed AFFINE dependence on these internal reloaded LO
Wilson coefficients (as in Kt0 and Cem),

    B_legacy_Zee = Bint_SM
                  + w1 (Bint_H1 - Bint_SM)
                  + w2 (Bint_H2 - Bint_SM).

This is NOT a weighted average of independently calculated
single-charged-Higgs FULL branching ratios: all three
bsgamma() evaluations here receive exactly the SAME mixed
low-scale Wilson arrays, including NP interference/quadratic
terms. The only changing component is the reloaded high-scale
context INSIDE the unchanged kernel.

The dedicated source guard checks that bsgamma has exactly
one internal CW_calculator call, uses only C0w[7]/C0w[8] in
its internal expressions (ignoring local storage declarations),
finds Kt0 and Cem, rejects direct mass_H/SM access outside
matching, and rejects obvious nonlinear C0w powers/products.
This scan is a necessary conservative preflight and not a
general symbolic proof; significant source differences must
be manually reviewed and not bypassed.

## Mandatory numerical physical closure

For benchmark (300,700,gamma=1.089, tanbeta=5.59717),
A1U evaluates four compiled-control scenarios:

1. Genuine mixed 300/700, gamma=1.089.
2. SAME masses, gamma=0 -> must reproduce A1R full single
   300-GeV vendor BR = 4.5115303105e-4.
3. SAME masses, gamma=pi/2 -> must reproduce A1R full single
   700-GeV vendor BR = 3.7793429732e-4.
4. Degenerate masses 700/700, gamma=1.089 -> must reproduce
   the SAME A1R full 700-GeV vendor BR independently of gamma.

Additionally, independently evaluate the two corresponding
pure-state observables via the C driver and compare them with
the actual prior A1R measured values; compare SM with
3.382457724e-4.

Status "GATE_A1U_FULL_LEGACY_SUPERISO_TWO_STATE_BR_ENDPOINT_CLOSED_NOT_2026_EXCLUSION"
is issued ONLY if all these explicit physical control gates pass.
Any endpoint/source discrepancy MUST stop rather than returning
a misleading mixed BR.

## AF run

    cd /home/aalida/zee
    git switch gateA1p-independent-hepfit-typeii-matching
    git pull --ff-only

    python3 -m unittest discover -s tests \
       -p 'test_gateA1u_legacy_two_state_br.py' -v

    python3 scripts/gateA1u_run_legacy_two_state_br.py \
       --vendor-root work/gateA1m_isolated_nlo_v1/isolated_superiso \
       --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
       --a1r-result work/gateA1r_observable_v1/gateA1r_br_pilot.json \
       --output-dir work/gateA1u_legacy_zee_br_v1 \
       --mH1 300 --mH2 700 --gamma 1.089 \
       --tanbeta 5.597170833164245

Expected completion status, not yet observed:

    GATE_A1U_FULL_LEGACY_SUPERISO_TWO_STATE_BR_ENDPOINT_CLOSED_NOT_2026_EXCLUSION

Result files:
- work/gateA1u_legacy_zee_br_v1/legacy_two_state_br.json
- work/gateA1u_legacy_zee_br_v1/a1u_raw_vendor_output.log

## Publication-grade limitations

- This implements the LEGACY compiled SuperIso-v5 full observable,
  not the newly upgraded exact-charm NNLO SM calculation from
  Misiak et al., arXiv:2608.29863.
- Never add the legacy NP mixed BR shift to the new 2026 SM
  central value without a matched perturbative calculation.
- Compare the genuine full LEGACY two-state result to the A1S
  2026 LO linearized screen to estimate *sensitivity to the
  approximation*, NOT to estimate a calibrated model error.
- A full 2026-compatible two-state prediction with correlated
  perturbative/hadronic nuisance variations and a documented
  likelihood is needed before allowed/excluded points, and
  source-level compatibility of quark/lepton Zee Yukawas,
  neutrino masses, and LFV is still needed for full-model claims.

**NO allowed/excluded Zee point, full modern NNLO validation,
or 95%-CL result is asserted by Gate A1U.**
