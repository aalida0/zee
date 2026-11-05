# D16 external 2HDM: resolve HW dimensional mismatch and certify generic common limit

**Starting commit:** `0894175b64395a5ef25d0cb236f38f81a14ace89` on `research/zee-d16-wgamma-gauge-matching`.

## Current verified scope

- Author's corrected external reference `general-2hdm-pheno` pinned at `b5035cd58d2a7e4a91e9790d045df062b97adffe`; paper arXiv:2410.17313v4 and July 2026 JHEP erratum reviewed.
- Full complex group totals agree for all three LFV channels at two constrained `Z3=Z7=0` strict-2HDM potentials; their `HW` term vanishes so they are **not generic validation**.
- At nonzero `Z3/Z7`, 12 out of 13 author terms agree to ≤7.25e-13 relative (group scoped); `HW` source uses an **extra `1/MW²`** compared with the corrected published equation. Source `thdm.py:1510,1791` and printed paper v4 Eq.65/66; author's EDM HW code `thdm.py:1224` does not have that extra factor.
- Independently observed `HW_code = HW_paper/MW²` for both chiralities and three channels; common dimensionful rescaling changes the dimensionless author `c_HW` by 1/4. Other groups retain their expected homogeneity.
- Native vertices: 128 coefficient substitutions PASS; frozen Modules0–14/D15 untouched; no physical Zee W Wilsons released.
- `EXTERNAL_2HDM_BASELINE.md`, `ZEE_EXTENSION_INVENTORY.md`, `external_2hdm.py` contain exact maps.

## Gate H1: isolate the source/paper inconsistency without masking it

1. Read the **actual pinned** source around `cR_llpg_HW`, `cL_llpg_HW`, `f11`, and EDM `HW`, plus 2026 erratum and corrected v4 equations. Derive the physical dimensions of the complete `HW` graph class from native scalar trilinear `G_s` (mass), neutral LFV Yukawa (dimensionless), `f11` arguments/definition, (v,M_W,m_{H_k},m_i), and operator coefficient convention. Keep explicit both L and R and complex conjugations.
2. Show whether the apparently extra (M_W^{-2}) can be absorbed into a *different convention for* `f11` or `G_s`, or whether it unambiguously violates homogeneity in the source. Derive at least one **independent** analytical or integral-based normalization check (not copying a code line or relying only on comparing two transcriptions). For example, use the analogous independently normalized EDM charged-Higgs/W topology where appropriate and a strict CP/diagonal operator limit, carefully accounting for operator normalizations. If that comparison is physically nonidentical, explain why and choose a stronger independent check.
3. Preserve the pinned upstream GitLab checkout **unaltered**. Make a source-preserving *research adapter* (e.g. `external_2hdm_hw_override.py`) that reports `AUTHOR_UNMODIFIED`, `PAPER_CORRECTED_HW` and their difference as distinct candidates. Reconstruct the coherent dimensionless sums from **captured author groups** by replacing ONLY `HW` with an independently derived paper expression; avoid monkeypatching `thdm.py` or changing its source. Label the corrected aggregate `2HDM_REFERENCE_PAPER_NORMALIZATION_CONDITIONAL` until H1 independent confirmation is complete. Do not expose as full Zee Wilson.
4. Verify dimensionless homogeneity under simultaneous mass and vev rescalings, separately vary (Z3) and (Z7), both signs, phases, scalar mass, (M_W) and angles in a physically consistent mapped 2HDM input, and run all 3 complex LFV channels. Avoid using arbitrary inconsistent mass/scalar-potential combinations to claim a model benchmark is allowed.

## Gate H2: complete generic strict 2HDM agreement

5. Using the **same native field-basis mapping** already established, add ≥3 independent `Z3/Z7≠0` strict singlet-free potentials with nonzero complex LFV (D), and the previously tested `Z3=Z7=0` cases as control. Independently check native `G_h,G_H,G_A` against Higgs-basis (Z3,Z7), scalar Hessian and EW inputs. Accept only model-consistent spectra; document scalar constraints separately.
6. Compare all 13 complex author groups and corrected-paper groups (two chiralities, three decay channels, coherent totals). Their difference should be localized **solely** to the audited HW term, not accidentally canceled by another contribution. Include a leave-one-out and `HW=0` falsifier. Distinguish the author's leading-mass truncation from frozen Module3 finite one-loop internal/daughter mass effects.
7. Prove and record the **operator conversion** `C_L/R = -c_L/R/(8*pi²*v²)` against independent signed amplitudes or operator definitions (existing source proof may suffice if directly cross-checked). Do not claim the authors' complete two-loop derivation has been independently reproduced merely because our implementation shares their master functions.

## Gate H3: advise on Zee-specific extension after H1–H2

8. Revisit `ZEE_EXTENSION_INVENTORY.md` and partition terms by *gauge-invariant complete class*, including physical H1/H2, F, mixed charged-current parents, off-diagonal Z currents and H1-H2 trilinears. Identify a minimal **nonzero, genuinely Zee-specific** class to compute, preferably with known analytic master integrals inherited from the corrected general 2HDM result. Calculate one testable class only when its gauge-invariant diagram partners are accounted for.
9. Do not multiply the whole 2HDM `W` result by (d_a²) or add an entire 2HDM answer atop Module4 validated photon/one-loop terms. A subtraction `C_Zee=C_2HDM+Delta_Zee` is allowed only after proving overlap and gauge independence of the correction.
10. Leave `research.wgamma_d16.matching` physical `C_L,C_R=null` and `coherent_inclusion=false` until full Zee-specific gauge completion is established. No D14 integration.

## Deliverables

- `HW_NORMALIZATION_AUDIT.md` with exact paper/erratum and code lines, dimensions, source-pinned reproduction, reasoned choice of normalization and independent check.
- A minimal executable regression: `python -m unittest research.wgamma_d16.test_hw_normalization -v` (or equivalent). Expected failing original source case must be recorded, not silently suppressed.
- `GENERIC_2HDM_CLOSURE.md` with generic nonzero-potential complex benchmark table, per-group differences, code hashes and limitations. Overall status separate from Zee acceptance.
- Updated `ZEE_EXTENSION_INVENTORY.md` with **prioritized smallest physically complete new class**, not another broad unsorted diagram list.
- Reproducible compact evidence JSON. Stay in `research/wgamma_d16/`, use ignored local scratch, keep author source and frozen modules unchanged. Commit/push focused work on existing branch.

**Priority:** Establish the corrected generic 2HDM common baseline before resuming a bespoke Zee two-loop outer integral. If genuine ambiguity remains, preserve the mismatch and draft a short, reproducible GitLab issue/email to the authors **without sending it**. Never claim `WGAMMA_GAUGE_MATCHING_PASS` for Zee based solely on external 2HDM matching.
