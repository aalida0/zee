# Signed complex tau radiative LFV: corrected author-source reconciliation

**10 November 2026. Exact corrected 2HDM source complex neutral-fermion Barr–Zee group retrieved; independent Zee analytic one-loop compared. This is NOT original native SARAH complex-coefficient replay and NOT full Zee LFV.**

## Executed source and physics scope

- Verified `general-2hdm-pheno` GitLab master commit prefix `b5035cd5` and SHA256 of corrected `thdm.py`: `9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193`.
- Frozen Zee benchmark archive hash `f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8`, exact original four D7/F13 NO/IO cards.
- Extracted **complex** original corrected authors' neutral-fermion source groups `cR_llpg_th/ch/bh/tauh` and `cL_llpg_th/ch/bh/tauh` by executing the original unchanged `cR_llpg` and `cL_llpg` with the existing source-closure decomposition helper. No upstream code modified or republished.
- For the neutral Type-II limit, mapped `rho_l = D/sqrt(2)` using native RH-row/LH-column, and used the authors' *internally evaluated* MSbar `mt,mc,mu(mt),mb,ms,md(mt)` for diagonal `rho_u=m_u(mt)*cot(beta)/v`, `rho_d=-m_d(mt)*tan(beta)/v`. Fixing this input was essential.
- For signed matching, corrected native `K2L=+cR/(8*pi²*v²)`, `K2R=+cL/(8*pi²*v²)`; native-to-Module3 `CL=-K2R, CR=-K2L`.
- The Zee one-loop complex reference comes from `module3.core.dipole_ledger`, independently validated against original generated one-loop formulas but **not** the exact, currently absent complex native tau source payload. Native original SARAH source one-loop **BRs** and the previously certified partial rates are used as comparisons, not treated as complex inputs.

## Numerical comparison: after correcting quark mass running

| Witness | Module3 1-loop BR / native original 1-loop BR, tau->e gamma | signed (Module3 1L + corrected author neutral BZ) BR / saved partial tau->e gamma | 1-loop ratio, tau->mu gamma | signed partial ratio, tau->mu gamma |
| --- | ---: | ---: | ---: | ---: |
| D7 NO | 1.0000031 | 1.0151102 | 0.98943255 | 1.0043764 |
| D7 IO | 1.0000031 | 1.0151059 | 0.98943254 | 1.0043948 |
| F13 NO | 1.0000005 | 1.0156001 | 0.98943251 | 1.0045924 |
| F13 IO | 1.0000012 | 1.0154204 | 0.98943245 | 1.0045878 |

**Before corrected MSbar Type-II quark Yukawas**, the signed combined BR/source partial ratios were approximately **1.139–1.143** for tau->e gamma and **1.125–1.130** for tau->mu gamma. The source-matched running input reduced the systematic mismatch to **~1.5–1.6%** and **~0.44–0.46%**. In all eight comparisons the documented PLUS native K2 convention reproduces the saved partial rate more closely than flipping the neutral BZ sign.

The remaining differences are not numerical precision errors that can be set to zero: analytic one-loop external-mass scheme and electroweak input details remain. A rate match does not by itself establish the relative phase with an independent tree-level amplitude.

The machine-readable GitHub Actions JSON contains all original complex `cL/cR` neutral-BZ source coefficients, mapped Module3 dipoles, signed plus and sign-flipped controls, and the six internally running quark masses. This does **not** include the missing fully compiled original SARAH complex tau K2 source arrays.

## Reproducibility

GitHub Actions run: https://github.com/aalida0/zee/actions/runs/42822430407

- 5 focused source-locked regression tests PASS (SHA, original benchmark order, independent one-loop BR residual, signed correction, running mass scheme and fail-closed global status).
- Both `Gamma_l_to_lp_gamma`-related `cR/cL` methods in the corrected current public author source are used via `source_decomposition`. Full method group closure is independently enforced inside that helper.
- CI re-clones and SHA-checks the pinned upstream file, runs the bridge, executes tests and uploads a JSON artifact. No new parameter scan or collider simulation.

From the root with the exact SHA-locked corrected GitLab repository cloned locally:

```sh
python3 -m research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_signed_complex_wilson_bridge --source /path/to/general-2hdm-pheno --commit b5035cd5 --output tau_signed_complex_wilson_bridge.json
ZEE_2HDM_PINNED_SOURCE=/path/to/general-2hdm-pheno python3 -m unittest research.full_constraints.lfv_2hdm_gitlab_reuse_2026.test_tau_signed_complex_wilson_bridge -v
```

## Scientific limit and next step

This comparison is a strong cross-check of complex neutral-fermion BZ *source reuse* and correct quark-running conventions. It does NOT source-match all two-loop Zee charged singlet F, mixed charged/gauge bosonic/seagull groups or off-shell photon K1, Z and box terms. It does not demonstrate that physical tau LFV constraints pass.

**Specific next data item:** archive the full original generated native SARAH `CalculateGamma2l` **complex K2L/K2R for tau->e gamma and tau->mu gamma** (for each of the four cards), with exact native input and compiler hashes, then use the explicit signed original Wilsons with the corrected 2HDM BZ and verify exact complex—not just BR—closure. Only after that should the exact three-body integrator implement coherent dipole+tree interference, followed by full generated off-shell photon/Z/box matching.

**Gate: CORRECTED_AUTHOR_TAU_COMPLEX_NEUTRAL_BZ=SOURCE_EXECUTED; ANALYTIC_ZEE_ONELOOP=SOURCE_RATE_CROSSCHECKED; ORIGINAL_SARAH_TAU_COMPLEX_WILSON=NOT_ARCHIVED; FULL_ZEE_LFV=UNKNOWN; GLOBAL_ACCEPTANCE=null.**
