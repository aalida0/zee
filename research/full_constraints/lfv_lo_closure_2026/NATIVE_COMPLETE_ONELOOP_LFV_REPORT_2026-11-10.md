# Four-card Zee Type-II LFV: original one-loop observables complete within stated approximation

**10 November 2026. Outcome: SOURCE_ONELOOP_PASS; FULL PHYSICAL LFV UNKNOWN.**

## Previously overlooked source dipole is now compiled and evaluated

The missing original Passarino-Veltman Cxx dipole functions were at the bottom of the existing SARAH 4.15.4 generated FlavorKit_LFV_ZeeTypeII.f90 (approximately lines 49501–50348). They were NOT absent from the three-file source bundle. We have now compiled and executed the complete original CalculateGamma2l without projecting out OA2, at all four frozen D7/F13 NO/IO cards. The exact LowEnergy_ZeeTypeII source K2 mapping is -OA2/(2 e m_parent). Independent Module3 Lavoura formulas reproduce K2L(native)=-C_R(Module3), K2R(native)=-C_L(Module3).

## Source one-loop numerical results

| Channel | D7 NO | D7 IO | F13 NO | F13 IO |
|---|---:|---:|---:|---:|
| mu -> e gamma BR | 1.5545e-19 | 1.0810e-18 | 4.0139e-20 | 1.3321e-19 |
| mu -> 3e BR, K1(q2=0) | 1.0883e-21 | 7.5294e-21 | 4.5462e-22 | 1.4571e-21 |
| mu-e conversion Al27, historical nuclear model | 4.7321e-22 | 3.0853e-21 | 2.3737e-21 | 7.2053e-21 |
| mu-e conversion Au197, historical nuclear model | 6.9893e-22 | 4.5497e-21 | 6.3468e-21 | 1.9220e-20 |
| tau -> e gamma BR | 7.4333e-18 | 4.4348e-17 | 3.2533e-21 | 5.5211e-21 |
| tau -> mu gamma BR | 3.0408e-15 | 3.4857e-15 | 5.8043e-20 | 6.8605e-20 |

All rates above are native one-loop calculations under explicit generator approximations, NOT all-order physical Zee predictions or certified modern conversion predictions. The frozen full F and D matrices were used; Type-II quark inputs have illustrative CKM and running masses. No new scan.

## Executable rate verification

- Original model-specific Calculate_LLpGamma Fortran versus independent width: 12/12 PASS, maximum relative residual 3.85e-15.
- Original Calculate_Lto3Lp with K1, K2, signed Z and local operators versus independent Python: 20/20 PASS.
- Original and scalar-proton/neutron-corrected Calculate_MuEconversion versus independent Python: 32/32 PASS, worst relative residual 3.5e-14.
- Analytic source dipoles in mu/tau channels: 12/12 PASS; mu-e complex residual <=2e-14 and worst tau-e 2.6e-7 (small finite-mass approximation).
- Final derived-input clean-directory tests: 7/7 PASS, all 128 deliverable files verified via SHA-256.

Native mu3e uses direct generated O4l only: separately generated crossed O4l arrays go into another three-body flavor channel and must not be added to the identical-electron rate. The original generated conversion had the scalar nucleon interchange N*gp + Z*gn; the source code rate replay corrects it to Z*gp + N*gn. Nuclear vector currents are unmodified.

## Quantitative relevance of unsettled one-loop scalar sector

Dropping scale-dependent scalar penguins changes the source one-loop mu3e rates by <=5.3e-10 relative and historical source conversion <=3.7e-5 relative. A LO c/b/t trace-anomaly scalar test contributes at most 3.52e-6 of the source vector amplitude (D7), and <8.1e-8 for F13. These are materiality checks, NOT fully matched QCD/nuclear uncertainties or formal proofs of counterterm cancellation.

## Existing experimental bounds and missing-amplitude test

MEG II: BR(mu->e gamma) < 1.5e-13 at 90% CL (EPJC 2025, DOI 10.1140/epjc/s10052-025-14906-3). SINDRUM: mu->3e < 1e-12. SINDRUM II: mu-e conversion in GOLD <7e-13. One-loop four-card rates are all far below the corresponding bounds; an Al rate is NOT compared directly with an Au limit.

A sufficient, phase-independent dipole remainder budget is ||Delta K2|| < (sqrt(BR_limit/BR_1loop)-1) ||K2_1loop||. In the card order D7 NO/IO, F13 NO/IO, the missing-amplitude thresholds are 981, 371, 1932 and 1060 times the observed one-loop norm. THESE ARE THRESHOLDS, NOT ESTIMATES OR BOUNDS ON THE OMITTED TWO-LOOP DIAGRAMS.

## What is still *not* physically closed

1. Zee-specific charged-singlet/mixed F-D and W/gauge bosonic two-loop radiative amplitudes and independent perturbative uncertainty bounds.
2. Finite-q2 monopole matching for light internal leptons in mu3e; QED radiative corrections.
3. Scalar-penguin scale dependence: counterterm/scheme validation or justified absolute uncertainty.
4. Conversion QED/QCD running, heavy-quark/gluon Wilson matching, modern hadronic/nuclear uncertainties, and precision CKM scheme; the current coherent rates use a historical nuclear approximation.
5. Remaining tau three-body LFV modes and other nonmuon LFV observables.

**Machine gate:** source_one_loop_experimental_checks=PASS_WITHIN_APPROXIMATION, physical_lfv=UNKNOWN, global_acceptance=null. No broad scan can be labeled FULL_LFV_PASS from these results.

Private downloadable source-replay package is named zee_lfv_native_one_loop_full_replay_2026-11-10.zip; original five user Fortran files are NOT included, and their source hashes remain pinned in the previous source manifests.
