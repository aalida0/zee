# Complete original SARAH ZeeTypeII one-loop dipole and mu3e assembly

**10 November 2026 | Major milestone: native one-loop photon OA1+OA2 and source-level mu3e evaluated; full physical LFV remains UNKNOWN.**

This calculation was executed directly in the current assistant runtime with the two user-supplied **SHA256-locked native source archives**: original SARAH 4.15.4 `generated.f90`, `couplings.f90`, `loops.f90` and original `FlavorKit_Observables_ZeeTypeII.f90` / `LowEnergy_ZeeTypeII.f90`. Previous audit projected all OA2 dipoles out, leaving only q2=0 monopoles. This continuation **recovered the original C-integral helper functions from the end of generated.f90 and compiled the full unchanged CalculateGamma2l** with all OA2lSL/SR source terms active.

## Primary execution

The native photon source was run with all exact four frozen `D7 NO/IO`, `F13 NO/IO` complex D/F Yukawa matrices and original mixed charged masses, massless neutrinos, fixed source EW inputs and alpha(MZ)=1/127.95. The original source conversion `K2=-OA2/(2 e m_mu)` was used without hand-chosen sign, as confirmed in the uploaded model-specific LowEnergy file.

The full original unmodified native `Calculate_Lto3Lp` subroutine was compiled and run with original direct Z, box, scalar-penguin, tree and q2=0 K1 plus **new nonzero native K2**. Both source dipoles and all source complex contact terms were retained with interference. Independently coded Python matches the **16/16** original compiled Fortran results to maximum relative discrepancy **4.2e-16**.

| Frozen card | Complete generated one-loop source BR(mu->e gamma) | Assembled generated one-loop source BR(mu->3e) |
|---|---:|---:|
| D7 NO | 1.66491921e-19 | 1.08828659e-21 |
| D7 IO | 1.15779980e-18 | 7.52936205e-21 |
| F13 NO | 4.29892238e-20 | 4.54615814e-22 |
| F13 IO | 1.42668207e-19 | 1.45713157e-21 |

**Caution:** These are actual generated **one-loop approximation values**, not certified complete full Zee physical rates and not a GLOBAL_PASS. Scalar-penguin Q-scale scheme, finite-q2 K1 and missing electroweak/mixed two-loop contributions still prevent a physical uncertainty/acceptance claim.

## Independent dipole phase and coupling checks

Reran the original full gamma2l source for **four choices per card**: full D/F, F-only, D-only and zero. F/D separation is additive as predicted for massless neutrinos (residual < 5e-15). F-only native K2L exactly reproduces

```
K2L_F = (F^dagger F)_(e mu) * [sin(gamma)^2/mH1^2+cos(gamma)^2/mH2^2] / (192*pi^2)
K2R_F = (m_e/m_mu)*K2L_F
```

with maximum complex relative residual **3.36e-16**, including NO/IO phases and both charged physical states. This independent Lavoura-type check establishes the native source's *restricted* charged F contribution in a consistent dipole convention. Previous alternative A2R notation had opposite sign and chirality labels: do not mix without operator mapping. **6 new regression tests passed**: original source SHA, four nonzero full dipoles, 16 native-vs-Python rates, F analytic limit, F/D additivity, missing dipole sufficient budget.

## Experiment-based sufficient missing dipole norm budget

Using published **MEG II 2025** BR(mu->e gamma)<**1.5e-13 (90% CL)** [EPJC 85 (2025) 1177, DOI 10.1140/epjc/s10052-025-14906-3], and the source convention `C=alpha(MZ)*m_mu^5/(4*Gamma_mu_LO)`, triangle inequality gives a sufficient condition for acceptance independent of unknown relative phase:

```
||Delta K2_missing||_2 < sqrt(1.5e-13/C) - ||K2_one_loop||_2
```

| Card | sufficient missing K2 norm budget, GeV^-2 | budget / source 1-loop K2 norm |
|---|---:|---:|
| D7 NO | 1.323128851e-12 | 948.2 |
| D7 IO | 1.320844432e-12 | 358.9 |
| F13 NO | 1.323815212e-12 | 1867.0 |
| F13 IO | 1.323232542e-12 | 1024.4 |

**These numbers are thresholds for sufficient conditional pass, not estimates of missing amplitudes.** Do not assert a missing two-loop bound has been proven. Likewise, the source's mu3e values are below the existing SINDRUM **1e-12** upper limit but remain model-source diagnostics, not a full uncertainty-qualified result.

## Reproducibility and remaining physics blockers

Executable scripts, source integrals extraction, independent original Fortran/Python observable replay, four card complex coefficients, budgets, and 6 passing tests are saved in conversation download `zee_lfv_full_oa2_one_loop_continuation_2026-11-10.zip`. It does not redistribute original uploaded private generated Fortran. The ZIP must be combined with existing source and audit bundles as in its README.

- Missing **Zee charged-gauge and mixed F/D two-loop dipole** quantitative uncertainty and complete higher-order radiative LFV acceptance.
- Missing **finite-q2 virtual photon** control for light charged lepton loops in physical mu3e phase space.
- Scalar penguins still Q sensitive; source scale cancellation/counterterms or conservative omission criterion must be demonstrated.
- Complete type-II coherent conversion with original full semileptonic Wilsons, corrected scalar proton/neutron matching, heavy-quark/gluon QCD and nuclear uncertainties still not established.
- Input scheme is fixed audit electroweak masses and alpha(MZ), not a complete fitted EW uncertainty model.

**Final gate: SOURCE_ONE_LOOP_MU3E_DIP0LE_DONE; PHYSICAL_LFV_UNKNOWN; global_acceptance=null.** Do not advertise accepted points, exclusions or a fully constrained scan based solely on these results.
