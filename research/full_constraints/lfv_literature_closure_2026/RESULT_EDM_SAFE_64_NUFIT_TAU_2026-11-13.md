# Zee Type-II: electron EDM discovery and neutrino-exact LFV texture repair — 13 Nov 2026

**Scientific verdict:** a new previously untested electron EDM requirement is decisive for the intentionally engineered LFV-suppressed texture family. A **three-complex-zero alternative** preserves the neutrino fit and eliminates the dominant transferred top Barr–Zee EDM, while respecting the observed JILA EDM bound in the source-pinned **pure 2HDM proxy** at all 64 fixed original scalar points. **The full mixed Zee EDM and the full physical LFV constraints remain UNKNOWN.**

## Source and reproducibility

1. Original old 64 complete complex Zee F and Ye2 inputs recovered from GitHub Actions [43130710614](https://github.com/aalida0/zee/actions/runs/43130710614), artifact `13904373448` (input-only).
2. Four original D7/F13 controls and corrected published general 2HDM source: Altmannshofer *et al.* JHEP06(2025)156 + JHEP07(2026)184 erratum, GitLab commit `b5035cd58d2a7e4a91e9790d045df062b97adffe`, `thdm.py` SHA256 `9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193`.
3. Original 64 corrected-author 2HDM pure-doublet EDM control completed via Actions [43491612392](https://github.com/aalida0/zee/actions/runs/43491612392). **62/64 exceed** `4.1e-30 e cm` JILA bound; largest `7.848655529075659e-26 e cm`, at historical 14187 IO 20261112. This is a **model-specific red flag but not a complete Zee exclusion**. Neutral-scalar top Barr–Zee directly transfers to the present Type-II quarks; charged gauge sectors need Zee-adapted amplitudes.
4. Original Zee inverse has **four complex homogeneous parameters** `z`. Use the exact Moore–Penrose solution of 3 independent complex linear constraints `D[e,mu]=D[mu,e]=D[e,e]=0`; preserve full original neutrino matrix (not a refit to different oscillation inputs). This leaves **one complex homogeneous direction**. New candidate generation and pinned corrected 2HDM EDM run: Actions [43492562878](https://github.com/aalida0/zee/actions/runs/43492562878), artifact `zee-edm-suppressed-64-new-textures-conditional-only` containing all 64 complex `F,D`, exact inputs, original nu fit observables and official source group decompositions.
5. Independent original NuFIT 6.1 original 1D + 3D (IC24) archive replay and direct Lavoura one-loop and neutral h/H/A tree threebody calculations in companion source package. **64/64** NuFIT scoped pass (maximum 3D local Δχ² `0.008665105952105456`, maximum 1D `0.007934626059483918`).
6. An attempted **fourth exact zero `D[tau,e]=0`** on the same fixed original F and neutrino target was *not rank independent*: 64/64 do **not** have four complex rank, under the declared rank tolerance. Actions [43493504025](https://github.com/aalida0/zee/actions/runs/43493504025) correctly reports **0/64 solutions**, all `FAIL_OR_UNKNOWN`. No rank-four solution is claimed, no forced pseudoinverse. Leave original robust 3-zero solution intact.

## Verified new 64 texture results

| Test | Original 64 | New 64 |
|---|---:|---:|
| Neutrino reconstructed and perturbative | 64/64 | **64/64** |
| NuFIT6.1 scoped 1D+3D checks | Selected legacy | **64/64** |
| Electron EDM (published *full 2HDM proxy*, not full Zee) | **62/64 proxy above limit** | **64/64 proxy below limit** |
| Largest absolute EDM proxy | `7.84866e-26 e cm` | `2.095744439644144e-30 e cm` |
| Largest Zee one-loop BR(mu→eγ), independent Lavoura α(0) | `1.56956e-15` | `1.5695621739876047e-15` |
| Largest Zee one-loop BR(tau→muγ) | `5.6328e-13` | `5.632837831228439e-13` |
| Largest Zee one-loop BR(tau→eγ) | `1.1232e-15` | `1.1231476732270806e-15` |
| Largest neutral tree-only BR(tau→3mu) | `9.14655e-13` | `9.146947711015468e-13` |
| Largest neutral tree-only BR(tau→e mu+mu−) | `1.999e-15` | `1.9990642113645225e-15` |
| Max Yukawa modulus | -- | `0.020625826000695638` |

New pure-2HDM EDM source group maxima: one-loop `2.109467e-30 e cm`, neutral tau Barr–Zee `9.738018e-32`, neutral top Barr–Zee `3.123189e-40`. This explicitly confirms **the large old top Barr–Zee term has vanished** with `D[e,e]=0` in the CP-conserving scalar / real Type-II quark setup. The **one-loop EDM is still nonzero** through the `D[e,tau] D[tau,e]` products and leaves only ~factor-two headroom at the worst benchmark under this proxy.

The separate five new tree neutral-scalar three-body channels were evaluated with exact 4-spin traces, crossed identical-lepton interference and finite lepton masses in `module3.tree` basis, quadrature order 14:
- `mu→3e`: largest `6.1655e-50`.
- `tau→3mu`: largest `9.14695e-13`.
- `tau→3e`: largest `1.97627e-22`.
- `tau→mu e+e−`: largest `1.24974e-19`.
- `tau→e mu+mu−`: largest `1.99906e-15`.

**These are tree-only subsets. They must never be summed incoherently with other penguins/boxes for a physical BR.**

The source-derived original 64 *complete one-loop* mu3e and historical Au conversion rates from 12 Nov cannot be copied to the **new** Yukawa matrices. The corrected pure-2HDM EDM proxy includes one physical charged doublet, NOT the original Zee singlet and second mixed charged Higgs eigenstate. Full Zee **mixed-F gauge and complete two-loop EDM materiality** is uncomputed. For conversion modern EFT/LEFT, heavy quark/gluon, CKM and nuclear errors remain unvalidated, as well as new 64 source-native SPheno rates.

## Practical completion

New `stage_edm_repaired_native_64.py` takes the new 64 original source-hashed family JSON and the **user's ORIGINAL native validated ZeeTypeII tree-scheme SPheno SLHA template**, reconstructs `Ye2 = cos(beta) D + sin(beta) YeSM`, writes 64 complete mass/Yukawa input cards using the already validated `set_model_blocks`, and hashes each card. For the native evaluation the user must run the original five-source, corrected-nuclear Fortran executable already described in `../lfv_64_native_2026/README_AND_PHYSICS_GATE_2026-11-12.md`.

For CI only, `.github/workflows/zee-lfv64-edm-staged-native-inputs.yml` writes a **SYNTHETIC_CI_NOT_FOR_PHYSICS** structural staging artifact using original synthetic template and explicitly records that the staged cards are NOT physically executed.

**Do not silently claim a complete LFV exclusion from these source-checked subsets.** Present the experimental screen as 'leading Zee one-loop radiative LFV + selected published pure-doublet 2-loop EDM proxy, with first-principles neutrino reconstruction and standard Zee tree-level three-body contributions.' That is a valid, scoped publication-level benchmark computation, not a full Zee global-allowed benchmark decision. Remaining hard physics barriers are new 64 one-loop native mu3e/conversion, full Zee EDM mixed F/gauge materiality, and relevant tau/off-shell conversion loops.
