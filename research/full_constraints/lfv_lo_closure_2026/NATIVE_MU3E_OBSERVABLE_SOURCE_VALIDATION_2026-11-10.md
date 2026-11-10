# Exact ZeeTypeII mu3e rate assembly: source verification (10 November 2026)

**VERDICT: NATIVE OBSERVABLE ASSEMBLY VERIFIED; PHYSICAL LFV UNKNOWN.**

## Verified source files

The user-supplied model-specific SARAH 4.15.4 observable sources passed their recorded SHA-256 checks:

- FlavorKit_Observables_ZeeTypeII.f90: b179e6fea1fe3afe08e34e6d481380b7d4b669ffb904898ac6ee6f8555aa3784
- LowEnergy_ZeeTypeII.f90: cf3552d25de21a6df0869d1fc013dded8efe26206195a08f84ab6ec251d63727

The model-specific routine **Calculate_Lto3Lp** is present and called from LowEnergy_ZeeTypeII.

## Source assembly and previously unresolved crossing convention

LowEnergy_ZeeTypeII defines, for each chirality:

    O4lX = BO4lX + PSO4lX + PVO4lX + TSO4lX + TVO4lX.

It also explicitly normalizes the photon form factors:

    K1L = OA1L / sqrt(4*pi*Alpha_MZ)
    K2L(2,:) = -OA2lSL(2,:) / (2*sqrt(4*pi*Alpha_MZ)*mf_l_mz(2))

and similarly for right chirality. Thus the native minus sign and muon mass must be used when recovering original raw OA2.

**The direct O4lX arrays are passed to Calculate_Lto3Lp.** Crossed O4lXcross arrays are passed to a different observable, Calculate_LtoL1L2L2, for mixed-flavor three-body modes. The previously proposed *manual sum of direct and crossed source groups for mu3e* is incorrect and must not be done.

## Actual compiled original source benchmark calculation

The unchanged Calculate_Lto3Lp subroutine was extracted from the exact uploaded original file and compiled using gfortran -O0 -fcheck=all. It was evaluated for the **four frozen exact D7/F13 low-joint cards** in five modes: (1) photon K1 only, (2) Z only, (3) photon+Z, (4) photon+Z+direct box/tree/scalar-penguin, and (5) the latter without the scale-unstable scalar-penguin. Each mode is calculated twice: native compiled Fortran and independent Python translation of the full quadratic and interference expression.

**20/20 original Fortran versus Python rate comparisons PASS, maximum relative residual 4.14e-16.** An additional 10 focused unit tests PASS, including exact source coefficients, phase transformations, direct/crossed guard, dipole normalization guard, and original nuclear scalar-source bug.

Crucial restriction: **K2L/R set to zero as a diagnostic because the prior native Gamma2l projection discarded original OA2. This is NOT a physical prediction or justified neglect of a dipole.** The monopole K1 is only q²=0. Scalar penguins retain scale/scheme uncertainty.

| Card | photon K1 only (K2=0) | photon + Z + direct local sources (K2=0) |
| --- | ---: | ---: |
| D7 NO | 7.86182415e-25 | 7.43906017e-25 |
| D7 IO | 2.86276170e-24 | 2.73426277e-24 |
| F13 NO | 5.76739243e-24 | 1.72785964e-22 |
| F13 IO | 1.74163277e-23 | 5.21749817e-22 |

These are **restricted source diagnostics, neither physical branching ratios nor upper/lower bounds on the full process**. The relative difference with/without the provisional scalar penguins is below 1e-5 *in these K2=0 diagnostics* only.

## Independently confirmed original conversion scalar proton/neutron interchange

The exact original source Calculate_MuEconversion uses

    Lcont = (Z+N)*(g0LV+g0LS) + (Z-N)*(g1LV-g1LS),

where g0LS=(gSp+gSn)/2, g1LS=(gSp-gSn)/2. Thus its scalar term is **N*gSp+Z*gSn**, but the physical scalar current is **Z*gSp+N*gSn**. The vector term is correctly ordered. Correct scalar nucleon matching must use the previously developed native adapter rather than the unmodified source.

## Reproducibility and remaining physical limits

Conversation attachment: zee_lfv_native_mu3e_observable_replay_2026-11-10.zip. Includes Python source replay and regression suite, prior complex coefficient JSON, tree source JSON, model-specific original-Fortran-vs-Python receipts, Al scalar mismatch test and README. The original user-supplied Fortran ZIP is intentionally NOT redistributed.

Still needed: the **native OA2 dipole** (not previously evaluated), finite-q² photon form factors, scalar-penguin renormalization or valid error budget, complete Type-II conversion heavy/gluon/nuclear interference, and materiality of missing Zee-specific radiative higher-order amplitudes.

**Final:** physical_mu3e_BR=null, physical_Al_rate=null, physical_lfv=UNKNOWN, global_acceptance=null. No scan filtering or physical exclusion.


## Conditional mu3e bound from an independent radiative-LFV upper limit

For the **restricted original FlavorKit source observable**, the common K2 norm contributes to both mu->e gamma and the mu->3e virtual-photon dipole. Comparing exact source coefficients:

    R = BR(mu->3e)_dipole / BR(mu->e gamma)
      = alpha_MZ^2/[8*pi*alpha_0] * [16 ln(m_mu/m_e)-22]/3
      = 0.00702805204358

for explicit diagnostic alpha_MZ=1/127.95 and alpha_0=1/137.035999084, with equal muon normalization.

**Without assuming dipole phases**, the amplitude triangle inequality gives within this same *truncated, common one-loop source observable*:

    BR(mu->3e)_trunc <=
       [ sqrt(BR(mu->3e)_K2=0,local) + sqrt(R*BR(mu->e gamma)_upper) ]^2.

The local K2=0 inputs here are the source-compiled K1(q2=0)+Z+direct box/tree/scalar groups. A purely **hypothetical** BR(mu->e gamma) <= 1e-13 gives four source-truncated upper envelopes:

| D7 NO | D7 IO | F13 NO | F13 IO |
|---:|---:|---:|---:|
| 7.02850936e-16 | 7.02892880e-16 | 7.03502327e-16 | 7.04016822e-16 |

This **does not establish an experimental or physical mu3e bound**, because: the radiative premise is hypothetical, complete Zee mixed/gauge two-loop radiative amplitudes are unbounded, K1 finite-q2 not certified, scalar scheme not fixed and other omitted amplitudes may be material. It is a concrete route to avoid phase-by-phase recombination of dipoles *after* a complete source-qualified radiative calculation and controlled source-truncation uncertainty have been demonstrated.

400 random complex-phase tests (100/card) verified the original quadratic source rate respects the amplitude-norm upper inequality. Together with 10 earlier checks, **13 focused unittest cases PASS** and all compiled original Fortran-vs-Python 20 diagnostics PASS. Source result saved in the conversation package as CONDITIONAL_RADIATIVE_TO_3E_SOURCE_ENVELOPE_2026-11-10.json.

**No change to physical_lfv=UNKNOWN or global_acceptance=null.**
