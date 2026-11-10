> **SUPERSEDED — 10 November 2026:** The PDF-v4 Barr–Zee numerical values below were replaced by the *executed, corrected authors' thdm.py* source comparison. The prior neutral numbers are wrong for current-source use. **Use [AUTHOR_CORRECTED_2HDM_SOURCE_RECONCILIATION_2026-11-10.md](AUTHOR_CORRECTED_2HDM_SOURCE_RECONCILIATION_2026-11-10.md)** and its machine gate instead. Signed native K2 matching also requires the corrected PLUS convention. This historical report is retained for audit provenance only. Full Zee LFV remains UNKNOWN.

# Zee LFV two-loop source correction and charged-scalar audit — 10 November 2026

**Physics gate: SOURCE-MATCHED RESTRICTED 2HDM SUBSETS; FULL ZEE TWO-LOOP UNKNOWN; GLOBAL_PASS=null.**

## Necessary numerical correction

The earlier neutral-fermion Barr–Zee source implementation had two errors against [Altmannshofer et al., arXiv:2410.17313v4](https://arxiv.org/pdf/2410.17313), Eqs. (54)–(55), PDF pages 13–14:

1. The prefactor must be `N_c alpha Q_f/(2 pi)`, not `N_c alpha Q_f/(4 pi)` (factor two).
2. The CP-odd scalar has `q_A2=i`, hence `q_A2^2=-1` versus `|q_A2|^2=1`. The previous code swapped these quantities in the relevant complex Yukawa products for both up-type and down-type fermion formulas.

**All previous neutral-fermion Barr–Zee numbers are superseded.** Recomputed original four exact complex D7/F13 cards:

| Card | Corrected native K2 neutral-fermion BZ norm [GeV^-2] | Superseded former value [GeV^-2] |
| --- | ---: | ---: |
| D7 NO | 1.017935394e-25 | 2.506807413e-25 |
| D7 IO | 8.520133890e-26 | 2.098212151e-25 |
| F13 NO | 2.537902351e-28 | 1.152018740e-27 |
| F13 IO | 6.550779147e-28 | 2.973573959e-27 |

The corrected result remains tiny relative to the native one-loop dipoles, specifically **because the direct e-mu neutral Yukawa entries of the frozen textures are near-zero**. It is not a universal Zee-model result.

## New, explicitly restricted charged-fermion two-loop diagnostic

Implemented source Eqs. (56)–(58) for pure-2HDM charged Higgs / t,b,c,tau loops, with corrected dilogarithm `f5,f6` kernels. For a **diagnostic only**, evaluate independently at physical masses mH1 and mH2 weighted by the doublet-Yukawa fractions `cos(gamma)^2`, `sin(gamma)^2`. This reproduces both unmixed 2HDM endpoints but **has not been shown to be a gauge-invariant subset of full Zee** and omits all genuinely singlet F, mixed H/W/seagull, and off-diagonal ZH1H2 diagram classes.

| Card | Doublet-projected charged-fermion K2 norm [GeV^-2] | (corrected neutral norm + charged diagnostic norm)/native one-loop norm |
| --- | ---: | ---: |
| D7 NO | 1.317109501e-25 | 1.673341e-10 |
| D7 IO | 1.102428249e-25 | 5.311188e-11 |
| F13 NO | 5.879593141e-28 | 1.187104e-12 |
| F13 IO | 1.517631983e-27 | 1.681992e-12 |

This ratio is a *sum-of-norms numerical diagnostic for only the included terms*, not an error bound on missing amplitudes.

## Exact Zee mixed charged-scalar tree vertices (not loops)

From H1 = cos(gamma) H_doublet + sin(gamma) S and H2 = -sin(gamma) H_doublet + cos(gamma) S, with T3=(1/2,0):

```
g_ZH1H2 = -g/(2 cos(thetaW)) sin(gamma) cos(gamma)
mu4 = -sqrt(2)/v * (mH1^2-mH2^2)*sin(gamma)*cos(gamma)
```

| Family | g_ZH1H2 | mu4 [GeV] | abs(mu4)/mH2 |
| --- | ---: | ---: | ---: |
| D7 | -0.09016 | 272.4 | 0.511 |
| F13 | -0.1521 | 1026 | 1.175 |

Nonzero off-diagonal gauge and large dimensionful mixing interactions **invalidate an assumption that pure 2HDM formulas exhaust Zee charged/gauge two-loop graphs**. Their actual two-loop integrals and gauge-completed amplitudes remain uncalculated.

## Materiality and current science decision

Existing source-validated one-loop `mu->e gamma` rates are 4.3e-20 to 1.16e-18 for the four cards. The sufficient conditional missing-dipole amplitude thresholds from MEG II are about **359–1867 times** the one-loop norms. This is substantial experimental margin, but *it does not impose a bound on unknown Zee mixed charged-gauge contributions*, which may involve flavor tensors not tied to direct D_e_mu. No physical 90% CL pass follows automatically.

The author [erratum JHEP07(2026)184](https://doi.org/10.1007/JHEP07(2026)184) and [current GitLab code](https://gitlab.com/jbrod/general-2hdm-pheno) are public; the corrected repo was **not directly executed** in this environment. The equations used above are sourced from the **v4 (May 2026) PDF**, and the July erratum needs a separate exact-source comparison.

## Reproducibility

The chat artifact `zee_lfv_two_loop_source_correction_2026-11-10.zip` contains:
- original frozen F/D spectra and native one-loop K2 source inputs;
- corrected neutral fermion `gamma,Z` two-loop code;
- prior **known-wrong** expressions, retained only for regression;
- charged-fermion pure-2HDM formula with Zee doublet projections;
- independently reconstructed mixed charged Z gauge vertex and mu4;
- 12 passing focused unit tests and SHA-256 manifest.

Independent clean-directory ZIP replay **PASS: 12 tests and all hashes verified**. All outputs keep `physical_lfv=UNKNOWN` and `global_acceptance=null`. No large scan authorized.

**Scientific next requirement:** source-based complete two-loop Zee mixed charged/gauge operator calculation *or* a defensible, independently derived bound on those missing dipoles, plus mu3e finite q2 and conversion hadronic/scheme uncertainty. Stop representing the small evaluated 2HDM subsets as a proof of full Zee two-loop completeness.


## Further result: exact single-external-neutral-LFV Barr–Zee topology selection rule

From the same native RH-row/LH-column scalar vertices, for any off-diagonal flavor i!=j:

- `Yh_ij = -sin(beta-alpha)*D_ij/sqrt(2)`,
- `YH_ij = +cos(beta-alpha)*D_ij/sqrt(2)`,
- `YA_ij = -i*D_ij/sqrt(2)`.

Accordingly, *all* diagrams containing **one external flavor-changing neutral h/H/A Yukawa vertex** factor `D_e_mu` or `D_mu_e`, **regardless of whether the inner bosonic loop contains a W, H1/H2, or the off-diagonal ZH1H2 gauge vertex**. Their single-neutral-LFV amplitude vanishes for the exact direct-Yukawa-zero texture. Numerically the four frozen cards have maximum |D_e_mu| and |D_mu_e| of **3.067e-19, 1.986e-19, 9.583e-21, 2.443e-20** respectively, at numerical-floor level. This is a flavor-factorization statement, NOT an evaluation or amplitude upper bound for all Zee two-loop processes.

**Not covered** by that selection rule: charged-H_i/neutrino/W LFV topologies involving F and D without a direct neutral e-mu Yukawa vertex, multi-insertion e↔tau↔mu diagrams, higher-loop dressing of existing F†F / DD† chains, and radiative generation of tiny direct texture entries. They remain the physics-completeness blocker.

New portable code `neutral_single_lfv_selection_rule.py` verifies the h/H/A off-diagonal vertices and exact-zero projection. The updated archive now has **17 focused unittest cases PASS**, plus 16 SHA-256 manifest checks in a clean-directory replay. Independent conditional missing-amplitude diagnostic finds the tightest snapshot margin in mu->e gamma: **359–1867 times native one-loop norm** (not a bound on the actual missing amplitudes). Source-result details are included in the conversation's `zee_lfv_two_loop_source_correction_2026-11-10.zip` archive.

**Unchanged gate: physical_lfv=UNKNOWN and global_acceptance=null.**
