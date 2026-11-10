# Zee Type-II LFV continuation: original photon monopoles and QED higher-order logarithm

**10 November 2026 | New source-executed and CI-tested subsets. FULL_ZEE_TWOLOOP=UNKNOWN, PHYSICAL_LFV=UNKNOWN, GLOBAL_ACCEPTANCE=null.**

## Scope / scientific decision

This calculation **does not** claim to evaluate the genuinely missing Zee charged-Higgs–W/Goldstone/seagull mixed electroweak two-loop dipoles or their gauge completion. Those topologies require a new coherent two-loop amplitude calculation with both charged mass eigenstates and their off-diagonal gauge couplings, plus renormalized source-matched signs.

Two source-anchored tasks **were** completed:

1. Extract and validate the full complex one-loop photon monopole `OA1L,OA1R` in the original **SHA256-locked SARAH 4.15.4 ZeeTypeII CalculateGamma2l** for the frozen D7/F13 NO/IO benchmarks. The original one-loop complex K2 was recovered previously. Combine K1/K2 in a signed *photon-only* 3-body observable based on the original SARAH/FlavorKit convention.
2. Evaluate the **universal, diagonal QED anomalous-dimension contribution** to the low-energy dipole between m_W and m_tau. This is a genuine, restricted QED higher-order effect when applied to the one-loop matched operator; it is **not** the complete two-loop electroweak Zee result and excludes mixing from other LFV operators.

## Original source provenance

The original user-supplied Fortran source is **not** redistributed in the public repository.

| Original user file | SHA-256 |
| --- | --- |
| generated.f90 (FlavorKit_LFV_ZeeTypeII.f90) | `2d30006d8d4759b2b7bfe76e2e4795bd2cf2f19ef5cb5772390ed3155b1bc41d` |
| couplings.f90 (Couplings_ZeeTypeII.f90) | `a0de851498f3e68e7421538098b3979381a3ecf5245021fce9d1c2df46a42e8c` |
| loops.f90 (LoopFunctions.f90) | `8142a813fcc00283d1de2865266be04ff1de25c09422b24b04d57523a6595a24` |

The hash-checked original source fragments are compiled locally with `gfortran -O0 -fcheck=all`, preserving the generated `CalculateGamma2l` and its original source coupling, monopole, and PV-integral helper bodies. The four benchmark input-card byte hash is `1472e0741671bd8e832e256ddafc371562ea446c3d7bba3ec0c7ae5fe21dde0c`. This is an isolated original-source *fragment replay*, not a regenerated model or unmodified complete SPheno binary.

The independent public SARAH `Photon_wrapper.m` (Zee-Toolbox blob `8fd5c9cd798b533704f7a6bc67a1f7e690d2772b`) defines:

```
K1L = OA1L/e; K1R = OA1R/e
K2L = -OA2lSL/(2 e m_parent); K2R = -OA2lSR/(2 e m_parent)
```

For all eight tau channels, native K1 satisfies the full complex F+D decomposition to relative residual <= **2.132e-16**. ZERO source amplitudes vanish, and for the pure charged-singlet F topology:

```
K1L(F) = -(2/3) K2L(F)
K2L(F) = (F^dagger F)[daughter,tau]/(192 pi^2)
         * (sin(gamma)^2/mH1^2 + cos(gamma)^2/mH2^2).
```

The numerical F-only ratio residual is <= **2.300e-16**. This complex sign agreement is an independent constraint on the charged-scalar photon topology, not proof that all electroweak two-loop terms vanish.

## Original FlavorKit three-lepton photon-source calculation

The original generated on-shell K1/K2 rates were mapped using the source operator definitions. The independently accessible `Calculate_Lto3Lp` / `Calculate_LtoL1L2L2` SARAH FlavorKit observables are in the older public Zee-Toolbox blob `0ad7d169c92117d1253f274684f5bc9197c67bb4`. This is an **independent historical observable convention** whose photonic source formula was cross-checked with explicit Dirac spinor amplitudes. The currently uploaded bundle includes Gamma2l, not the *model-specific current-version* three-body observable body; do not present this transfer as a complete original model-specific three-body execution.

With `e²=4*pi*alpha(MZ)` and final leptons taken massless except as collinear regulators:

```
tau -> 3l:  D = (|K2L|²+|K2R|²) [16 log(m_tau/m_l)-22]/3
            V = |K1L|²+|K1R|²
            I = -4 Re(K2L K1R* + K2R K1L*)

tau -> l_a^- l_b^- l_b^+, a != b:
            D = (|K2L|²+|K2R|²) [(16/3) log(m_tau/m_b)-8]
            V = (2/3)(|K1L|²+|K1R|²)
            I = -(8/3) Re(K2L K1R* + K2R K1L*)

Gamma_photon = (4 pi alpha)² m_tau^5 / (512 pi³) (D+V+I).
```

The independent spinor test confirms the **-4** coefficient, provided the `i sigma^{mu nu} q_nu` phase and K2 opposite chiral pairing are treated consistently. A failed early test subtracted an asymptotic leading-log approximation from a low-order collinear numerical quadrature; the corrected regression computes both components with the **same** quadrature. This correctly isolates the finite interference and passes CI.

### One-loop native photon K1+K2, and K1 plus restricted corrected neutral-fermion BZ K2

`K1` is the **original one-loop** full F+D source, with no extra two-loop monopoles. `K2` is either the original native one-loop or the coherent native one-loop plus the independently gauge-invariant **neutral-fermion-only** Barr–Zee contributions from the pinned corrected authors' `general-2hdm-pheno`. The latter excludes all mixed charged Zee gauge/fermionic two loops.

| Card | BR_photon-only(τ→3μ), native 1L | Relative K1 effect in native 1L photon | BR_photon-only(τ→3μ), native 1L + neutral-fermion BZ K2 | Relative K1 effect with BZ |
| --- | ---: | ---: | ---: | ---: |
| D7 NO | 9.36608e-18 | +19.824% | 4.46927e-14 | +0.2235% |
| D7 IO | 1.04444e-17 | +16.564% | 5.12585e-14 | +0.1760% |
| F13 NO | 1.43343e-22 | -3.928% | 5.94528e-18 | +0.0322% |
| F13 IO | 1.84643e-22 | +4.699% | 6.81920e-18 | -0.00147% |

| Card | BR_photon-only(τ→3e), native 1L + corrected neutral BZ | BR_photon-only(τ→eμμ), same subset | BR_photon-only(τ→μee), same subset |
| --- | ---: | ---: | ---: |
| D7 NO | 5.19120e-16 | 1.01262e-16 | 2.05071e-13 |
| D7 IO | 3.09530e-15 | 6.03760e-16 | 2.35293e-13 |
| F13 NO | 6.66707e-20 | 1.30070e-20 | 2.73243e-17 |
| F13 IO | 4.06232e-19 | 7.92506e-20 | 3.13498e-17 |

**These are photon-only SOURCE-APPROXIMATE branching-fraction contributions.** They must not be added to the separately computed exact-finite-mass neutral-tree/dipole interference tables, which used a different alpha and matrix-element approximation, without an explicit common convention and re-integration. Neutral scalar tree, charged and neutral box, Z penguins, off-shell q²-dependence, QED long-distance, and genuine Zee-specific two-loop mixed scalar/gauge sectors are absent.

## Universal QED LL dipole evolution: restricted two-loop contribution

Reference: **Ardu, Davidson, Lavignac**, *Constraining new physics models from mu->e observables in bottom-up EFT*, EPJC **84 (2024) 458**, Eq. **(4.4)**, DOI `10.1140/epjc/s10052-024-12782-x`. The homogeneous low-energy QED dipole anomalous dimension contains the universal factor

```
C_D(m_tau) / C_D(m_W) ≈ 1 - [16 alpha(0)/(4 pi)] log(m_W/m_tau)
                         = 0.9645825297250689
pure 1L |C_D|² rate factor = 0.9304194566508134.
```

This is a fixed-alpha, first-order-log calculation, with matching at mW; not the `mheavy -> mW` evolution, not resummed to all orders and with no operator mixing. It scales the original **one-loop** native K2, leaving the separately already two-loop neutral-fermion BZ coefficients unchanged to avoid spuriously treating its RG correction as another two-loop term. Therefore partial-rate shifts are small when BZ dominates.

| Card | ΔBR/BR for τ→eγ restricted native 1L + neutral BZ | ΔBR/BR for τ→μγ same restricted combination |
|---|---:|---:|
| D7 NO | -0.09298% | -0.09375% |
| D7 IO | -0.09301% | -0.09371% |
| F13 NO | +0.16858% | +0.03534% |
| F13 IO | +0.09049% | +0.03562% |

The sign of a *partial* coherent rate shift may be positive despite a less-than-one 1L amplitude scaling because of interference with the fixed BZ amplitude. These are **not** full two-loop Zee radiative rates, and their smallness does not bound the missing gauge-complete mixed graphs.

## Reproducibility and risk controls

- Native photon 6 independent tests PASS (source F/D, exactly-zero and F-only analytic identities, rephasing, signed photonic Dirac interference, provenance and missing rates). Run: https://github.com/aalida0/zee/actions/runs/42833910221
- Corrected authors' 2HDM source, native K1 and QED LL workflow PASS, five source-locked BZ and four QED tests PASS. Run: https://github.com/aalida0/zee/actions/runs/42834587155
- Executable code: `tau_native_monopole_source.py`, `tau_qed_dipole_ll_diagnostic.py`, and their tests in this directory, with frozen source K1 and K2 JSON and all provenance assertions.
- No private generated Fortran was pushed; no frozen physics modules, previous result gates, or scan inputs were modified. Separate source-free reproduction package may be used locally with the user's original hash-pinned source.

## Remaining full-Zee gauge-completion requirements

1. Derive or generate a gauge-complete set of genuine **mixed (F,H^pm_{1,2},W^pm,G^pm)** two-loop diagrams, including their seagulls, counterterms, charged-gauge/Goldstone mixing and all flavor tensors, and independently test cancellation of `xi` gauge dependence. A doublet-only projection of pure 2HDM charged-Higgs loops is NOT source-complete for this Zee model.
2. Include the non-diagonal `Z H_1^+ H_2^-` charged current and tree potential `mu4` that alter mixed charged states, where allowed by the full two-loop topology. The 2021 charged-scalar cascade analysis (arXiv:2106.08332) determines these **vertices**, not their two-loop LFV amplitudes.
3. Independently match all complex Wilson coefficients in a single renormalized operator convention. Close the remaining four-lepton contact/Z/box interference, finite-q² K1 corrections, QED/QCD mixing, and nuclear hadronic uncertainty before using mu->3e and Al conversion as complete scan cuts.
4. For the user's intended **phenomenological scan-and-cascade paper**, separate rigorously assessed constraints from explicitly conditional estimates; do not claim full global LFV pass while missing new amplitudes remain uncontrolled.

**Final research gate: NATIVE_TAU_K1_K2_SOURCE_REPLAY_PASS; CORRECTED_NEUTRAL_BZ_RESTRICTED_PASS; QED_DIAGONAL_LL_RESTRICTED_PASS; ZEE_GAUGE_COMPLETED_TWOLOOP_NOT_CALCULATED; PHYSICAL_LFV=UNKNOWN; GLOBAL_ACCEPTANCE=null.**
