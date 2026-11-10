# Source-replayed complex Zee τ radiative LFV and updated three-lepton interference

**10 November 2026. Original SARAH 4.15.4 one-loop τ K2 coefficients recovered from the user's uploaded Fortran ZIP. FULL ZEE LFV remains UNKNOWN.**

## Source identity and local execution

The user uploaded `zee_lfv_source_bundle(1).zip`. Its member SHA-256 hashes agree **exactly** with the previously pinned source:

| User-uploaded member | Original generated source | SHA-256 |
|---|---|---|
| generated.f90 | FlavorKit_LFV_ZeeTypeII.f90 | `2d30006d8d4759b2b7bfe76e2e4795bd2cf2f19ef5cb5772390ed3155b1bc41d` |
| couplings.f90 | Couplings_ZeeTypeII.f90 | `a0de851498f3e68e7421538098b3979381a3ecf5245021fce9d1c2df46a42e8c` |
| loops.f90 | LoopFunctions.f90 | `8142a813fcc00283d1de2865266be04ff1de25c09422b24b04d57523a6595a24` |

In the assistant's local runtime, an isolated reproduction harness copied the *unaltered body* of the generated `CalculateGamma2l`, the original required model-specific coupling subroutines, native generated PV integrals and original monopole/finite-mass helper functions. It supplied only a minimal `Control` module as a compilation scaffold. It compiled at `gfortran -O0 -fcheck=all`, reconstructed the four saved D7/F13 scalar and complex F/D input cards, and ran both tau channels with `CalculateGamma2l(gt1=final,gt2=3,gt3=final,OnlySM=.false.)`.

The original mapping is

```
K2L = -OA2lSL / (2 e m_tau)
K2R = -OA2lSR / (2 e m_tau)
alpha_EM = 1 / 127.95,  m_tau = 1.77686 GeV
Gamma_tau = hbar / (290.3 fs)
BR(tau -> ell gamma) = alpha_EM * m_tau^5/(4 Gamma_tau) *
                        (|K2L|^2 + |K2R|^2)
```

**This was a reproducible original-source fragment replay, NOT an unchanged full SPheno installation/run.** The source fragment SHA256 is `e52dc223421b571e9d94727a01253620d83131f128a40c6d34644ab1d1ccc046`, and the frozen numerical input `cards.dat` SHA256 is `1472e0741671bd8e832e256ddafc371562ea446c3d7bba3ec0c7ae5fe21dde0c`.

## Native one-loop complex coefficients

All dipoles have dimension GeV^-2. Each complex entry is (real, imaginary).

| Card | Process | K2L (real, imaginary) | K2R (real, imaginary) | Native BR |
|---|---|---|---|---:|
| D7 NO | tau->e gamma | (2.256164655e-14,-3.360474075e-15) | (-1.739793020e-16,1.077285663e-15) | 7.959960741e-18 |
| D7 NO | tau->mu gamma | (1.269847183e-14,-2.345444176e-14) | (-3.133966310e-13,-3.382401272e-13) | 3.256188574e-15 |
| D7 IO | tau->e gamma | (4.981084646e-14,-2.502290938e-14) | (-2.034034978e-15,-6.364049338e-17) | 4.749019714e-17 |
| D7 IO | tau->mu gamma | (-7.105615386e-16,-2.052144912e-14) | (2.359507003e-13,-4.341149820e-13) | 3.732630816e-15 |
| F13 NO | tau->e gamma | (-4.515143002e-16,1.560776402e-16) | (6.529807160e-19,-4.635283726e-18) | 3.483795869e-21 |
| F13 NO | tau->mu gamma | (-1.295620315e-16,2.611432632e-16) | (1.350127853e-15,1.471180246e-15) | 6.215498953e-20 |
| F13 IO | tau->e gamma | (-5.697942206e-16,2.502274785e-16) | (8.729014850e-18,3.355995804e-19) | 5.912304963e-21 |
| F13 IO | tau->mu gamma | (1.479501732e-17,4.092644780e-16) | (-1.031341050e-15,1.892586158e-15) | 7.346604088e-20 |

Maximum relative discrepancy against the PREVIOUS original SPheno source rate gate is **2.848e-6** (8/8 channels). The earlier rate values were rounded, so differences at this level should not be interpreted as new theory effects.

## Independent signed complex checks executed locally

On precisely the same compiled original routines and four cards, three further input modes were replayed:

- FULL F+D, F_ONLY, D_ONLY, and ZERO.
- **Original full complex coefficient = F_ONLY + D_ONLY - ZERO** to max **2.046e-16 relative**, for all 16 chiral complex source coefficients; ZERO amplitudes exactly vanish.
- **Independent signed analytic F-only**: `K2L = (F^dagger F)[ell,tau]/(192 pi^2) * [sin(gamma)^2/mH1^2 + cos(gamma)^2/mH2^2]`; max complex relative discrepancy **5.287e-16** over 8 benchmark/channel pairs.
- **F-only K2R external mass flip**: `K2R = (m_ell/m_tau) K2L`, max relative discrepancy **4.193e-16**.
- These checks validate complex signs/chiral assignments, not merely BR magnitudes. They do not certify full two-loop Zee LFV.

A source-free local reproduction ZIP (available in the ChatGPT response) includes `build_native.py`, original-source-extraction recipe, `native_driver.f90`, `cards.dat`, and regression scripts. It **does not redistribute** any user-uploaded original Fortran code. A clean-room extraction/rebuild/replay passed with a fresh working directory in the assistant runtime.

## Re-integrated into the GitHub three-body calculation

The eight native K2 complex pairs and matching source receipts were committed to

`research/full_constraints/lfv_2hdm_gitlab_reuse_2026/ORIGINAL_NATIVE_TAU_K2_REPLAY_2026-11-10.json`.

The native JSON passes the repo's fail-closed `tau_native_sarah_complex_import.py` original-source hash and one-loop radiative norm gates. A new independent Module3 comparison tests the original complex one-loop dipole at the chiral-amplitude level, without pretending the authors' corrected 2HDM code contains the Zee F coupling.

The published corrected `general-2hdm-pheno` authors' **neutral-fermion Barr-Zee** complex coefficients are added in the source-audited signed convention; the result is passed to the existing full-mass constant-dipole plus neutral h/H/A tree amplitude. The exact spin-summed complex interference integral and phase-free bounds are reevaluated for all four benchmarks and four tau three-body final states.

GitHub Actions source-import and analytic comparison **4/4 PASS**; the coherent amplitude regression **6/6 PASS**, two complete four-card scans PASS:

https://github.com/aalida0/zee/actions/runs/42828683295

The key result: replacing the previous Module3 approximate one-loop input by **original generated complex K2** changes the restricted photon-dipole BR by **at most 6.585e-9 relative** (largest D7 IO tau->3e), because the much larger included neutral-fermion BZ dominates this particular four-card set.

### Native-one-loop+neutral-BZ, exactly integrated constant-dipole+tree subset

| Card | tau->3mu dipole-only | tau->3mu neutral tree | relative-phase envelope for these TWO terms only |
|---|---:|---:|---|
| D7 NO | 4.180659037e-14 | 8.066207952e-16 | [4.249856653e-14,4.272785580e-14] |
| D7 IO | 4.786837821e-14 | 1.201634827e-15 | [4.843285345e-14,4.970717263e-14] |
| F13 NO | 5.572214252e-18 | 2.898158205e-21 | [5.549102482e-18,5.601122339e-18] |
| F13 IO | 6.380055599e-18 | 6.859465498e-21 | [6.338860013e-18,6.434970115e-18] |

These are **not full physical BRs**. Even after original complex K2 recovery, source-level phase identity between the scalar and photon four-component operator conventions needs an independent check to publish a fixed **signed** interference rate, and full Zee amplitudes would still require off-shell K1/K2, Z penguins, boxes and gauge-complete Zee mixed charged/gauge two-loop matching.

The imported source contract deliberately records `input_phases_independently_verified=false` because a JSON source hash and BR norm alone cannot authenticate its phases. This does **not contradict the separate local original-Fortran source-fragment execution documented above**. The CI itself replays only the source-free analytical comparison and the imported source rates; the private original Fortran files remain local.

## Final research status

**NATIVE_SARAH_TAU_COMPLEX_ONELOOP_RECOVERED_AND_VALIDATED_IN_SOURCE_FRAGMENT_REPLAY.** The old missing native complex-one-loop-input blocker is cleared for D7/F13 NO/IO.

**FULL_ZEE_LFV=UNKNOWN; GLOBAL_ACCEPTANCE=null.** Additional genuine two-loop mixed scalar/gauge diagrams, off-shell operator matching, remaining three-body and conversion terms and theory uncertainties remain outstanding. No new scan was authorized or run.
