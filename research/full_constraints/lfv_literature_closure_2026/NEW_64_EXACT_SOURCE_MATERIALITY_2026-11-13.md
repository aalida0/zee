# 13 November 2026 — 64 original Zee Yukawa source LFV materiality audit

**Result:** `LEADING_SOURCE_LFV_SCREEN_COMPATIBLE_64_OF_64` within the previously executed original one-loop FlavorKit approximation, **not** a full physical LFV constraint. All `physical_LFV` and `global_acceptance` fields remain `null`.

## Actual new calculation and provenance

Recovered the authentic GitHub Actions run **43130710614**, artifact **13904373448** `zee-exact-64-inputs-NOT-native-LFV-rates`. Original inputs: 16 full-tree-vacuum-certified scalar spectra times two neutrino mass orderings and two independent texture seeds. **All 64 per-file SHA-256 hashes were checked against their original manifest**, and the 16 scalar source hashes were cross-checked against `module14/conditional_scan/candidate_followup.json` (`CERTIFIED_VACUUM_APPROX_BSG_16`; pinned dataset hash `2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9`). All source `FZEE`/imaginary entries form full complex antisymmetric matrices, and `YEE2`/imaginary entries were read without truncating phases. The user-owned original five-file Fortran archive and its source-generated **64 signed Wilson coefficient outputs are not in this artifact**. Do not confuse input provenance with a fresh one-loop execution.

The native SPheno.m matching is `Ye=YeSM/cos(beta)-tan(beta)*Ye2` and `D=-sin(beta)*Ye+cos(beta)*Ye2`. Therefore off-diagonal `D_ij=Ye2_ij/cos(beta)`. The 64 input cards yield these **actual** maxima:

| 64-source quantity | Maximum |
|---|---:|
| `abs(D[e,mu])` | `1.8377546644496057e-18` |
| `abs(D[mu,e])` | `3.705370968959021e-18` |
| `abs((F†F)[e,mu])` | `3.5464912863668254e-05` |
| `max(abs(F))` | `9.58245247622679e-03` |
| Leading `abs(C_R^F)` in GeV^-2 | `2.8080130687996046e-14` |

For the previously checked native convention (massless neutrino, leading singlet `F†F`):
```
C_R^F = -(F†F)[e,mu] / (192*pi^2) *
        (sin(gamma)^2/mH1^2 + cos(gamma)^2/mH2^2)
```
The maximum is point **15591 / NO / 20261111** and is **48.71** times smaller than the frozen MEG-II dipole-norm limit `1.367785824084e-12 GeV^-2`. This is a **single F-only dipole component**, not the complete source amplitude; multiple terms can interfere. The source-level 64-card audit has eight executed synthetic, source, hash and limit tests in the archived code package; no original frozen functions modified.

## Existing (not newly executed) source one-loop rate evidence

The independent **12 November original model-specific Fortran** 64-card replay is documented in `../lfv_64_native_2026/ACTUAL_64_SOURCE_ONE_LOOP_MU3E_CONVERSION_2026-11-12.md`.

| Mode | Max 64-card source one-loop rate | Source-matched observed 90%-CL limit | Source approximation result |
|---|---:|---:|---|
| `mu -> e gamma` | `1.6273e-15` | `1.5e-13` | 64/64 nominal compatible |
| `mu -> 3e` | `1.0729e-17` | `1e-12` | 64/64 nominal compatible |
| `mu Au -> e Au`, **historical** corrected p/n nuclear scheme | `2.7637e-17` | `7e-13` | 64/64 nominal compatible |

From these *maxima*, conditional sufficient missing-process-amplitude-to-original ratios `sqrt(limit/max_rate)-1` are **8.60, 304.3 and 158.1**, respectively. These are **not computed upper bounds on missing physical amplitudes**.

## Published-formula transfer already validated

- Herrero-Garcia et al., JHEP04(2017)130, Sec.3.3, arXiv:1701.05345, leading Zee LFV including F bilinears, texture restrictions.
- Primulando, Julio and Uttayarat, EPJC82(2022)253, Eqs.(31)-(43), arXiv:2201.01960, dipole, off-shell photon and scalar conversion; restricted family Z2. Type-II quarks allowed in their quark sector.
- Heeck and Thapa, PLB841(2023)137910 Eq.(5), arXiv:2303.13383: dipole-only aluminum relation, **not** full Type-II Zee conversion.
- Altmannshofer et al., JHEP06(2025)156 with JHEP07(2026)184 erratum, arXiv:2410.17313v4: source-pinned corrected pure-2HDM two-loop Yukawa/gauge coefficient groups; `../lfv_2hdm_gitlab_reuse_2026/OFFICIAL_CORRECTED_GITLAB_LFV_REUSE_REPORT_2026-11-10.md`. Four **older** texture pure-2HDM proxy ratios (2-loop/1-loop coefficient norm) are `3.06e-10, 9.78e-11, 4.91e-11, 4.84e-11`; not computed on the new 64 nor on the full Zee singlet sector.
- KKO PRD66(2002)096002 nuclear formalism and existing `conversion_kko.py` implement complex scalar, vector and dipole interference; reproduce Al dipole-only `CR/BR=0.00265647` but do not map signed 64 UV Wilson coefficients.

## Exact remaining STOP barriers — no invented completion

1. Genuine two-charged-scalar Zee `F` plus W/Goldstone two-loop dipoles: a **new** possible leading/chirality-enhanced invariant cannot be excluded by setting direct neutral `D[e,mu]` small; either quantify it or justify excluding it under an explicitly declared leading-order accuracy.
2. Import original **signed complex 64-card UV Wilson coefficients** from the private source-derived Fortran run to the independent conversion convention, test one operator and interference at a time; complete QED/QCD/LEFT running, CKM input and modern nuclear uncertainties if claiming a **physical** conversion exclusion.
3. Apply relevant tau LFV, semileptonic and EDM observable cuts for a broader/full-LFV claim. Existing one-loop three-muon source approximation remains compatible only within scope.

**Scientific release:** The source one-loop LFV screen for the three specified muon observables is **COMPLETE WITH DECLARED APPROXIMATIONS**; `full_Zee_LFV=UNKNOWN` and `global_zee_acceptance=null`. No global paper scan may be labeled fully experimentally allowed on this evidence alone. No numerical missing amplitude or 64-conversion EFT rate was computed in this audit.

Reproducible complete eight-test source/SLHA-input audit, 16 scalar hash-pinned mass/mixing ledger, original 64-card source-verified numerical materiality record, and methods note are in the companion downloadable `zee_lfv_finish_20261113.zip` created in this conversation. The original GitHub Actions 64-input artifact is the necessary external source input; its bytes are **not** committed to the repository.
