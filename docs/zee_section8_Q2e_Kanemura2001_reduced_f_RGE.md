# Q2e — first source-pinned Zee-specific one-loop RGE (restricted real f)

**Status: new code and 11 regression tests committed; AF integrated validation still pending.** Not a complete general-complex Zee RGE calculation and not an allowed benchmark.

## Literature breakthrough

Kanemura, Kasai, Lin, Okada, Tseng and Yuan, *Phenomenology of Higgs bosons in the Zee-Model*, Phys. Rev. D **64** (2001) 053007, [arXiv:hep-ph/0011357v2](https://arxiv.org/abs/hep-ph/0011357), gives explicit one-loop RGEs in Appendix A, including:
- **(A1)–(A3)**: gauge beta coefficients (22/3,-3,-7) with SM-normalized g1 = gprime.
- **(A4)–(A11)**: restricted scalar doublet and charged-singlet quartic RGEs, without general lambda6/lambda7 and without general Yukawa couplings.
- **(A12)**: top Yukawa-only beta.
- **(A13)**: singlet antisymmetric leptonic f beta, in the paper's restricted real-coupling convention.

The authors explicitly say in Sec. III that they **neglect all ordinary Yukawas except top** in their RGEs, and **neglect f numerically** although its beta is printed. Their scalar potential sets lambda6=lambda7=0, and omits the general complex lambda10 portal. These are not the full general-Zee interactions used in our B2 solutions.

The original Eq.(A13) (D = 16 pi² d/dln(mu)):
```
D f_ij = -[(3/2) gprime² + (9/2) g2²] f_ij
         +4 (sum_kl f_kl f_kl) f_ij
         -4 sum_kl f_ik f_kl f_lj.
```
For **real** 3x3 antisymmetric f, with q = sum(i<j) f_ij²:
```
f³ = -q f,     sum_ij f_ij² = 2q,
D f = [-3/2 gprime² - 9/2 g2² + 12 q] f.
```
This is an independent algebraic constraint any full Zee RGE generator MUST match in the restricted real-f / no-other-lepton-Yukawa limit, subject to checking interaction normalization.

**Do not replace complex f products with the real-f expression.** In our neutrino solutions f and Pi1/Pi2 are complex; conjugation and lepton-matrix terms are essential. The 2001 equation is NOT a substitute for full complex Zee beta_f.

## Implementation

New files:
- `scripts/zee_section8_Q2e_kanemura2001_reduced_f_RGE.py`: separate direct-matrix A13 and 3D analytic beta, A1–A3/A12, one-loop coupled RK4, real-only guard, all physical completeness flags false.
- `tests/test_zee_section8_Q2e_kanemura2001_reduced_f_RGE.py`: 11 tests for source coefficients, cubic identity, orthogonal lepton-basis covariance, f=0 stability, A12, analytic one-loop gauge running, RK4 step-halving, complex rejection, and physical status.

For the **synthetic** real f with entries (f12,f13,f23)=(.001,-.002,.003), illustrative couplings (gprime,g2,g3)=(.36,.65,1.18) and yt=.95 at 700 GeV, an independent numerical cross-check yields |f|(10 TeV)/|f|(700 GeV) ~ **0.96592**. This ~3.4% decrease arises mainly from gauge running in this restricted historical system, not a prediction for any saved complex B2 solution.

## One user-preferred AF command

The **existing** consolidated Q2 runner now includes these tests and computes the new source-limited f evolution. No separate repeated commands:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 scripts/zee_section8_run_integrated_Q2_validation.py \
  --output-dir work/zee_section8_Q2_integrated_v4
```

Expected: **125 required** tests (prior 114 + new 11), **16 SciPy Barr–Zee subset** tests, **141 total** if SciPy remains available; all 20 prior complex B2 bridges still checked, but kept **separate** from the real-f historical RGE. New markers:
```
Q2E_KANEMURA2001_REDUCED_REAL_F_RGE_PASS True
Q2E_REAL_F_SCALE_RATIO 0.9659...
Q2E_GENERAL_COMPLEX_F_AND_YUKAWA_RGES_AVAILABLE False
FULL_ZEE_ALLOWED False
```

These outcomes remain expected, not yet actually validated by AF on the new commit. The runner refuses to overwrite v3.

## Major next gate, not another toy numerical scan

1. Build/generate beta_f and beta_Pi1, beta_Pi2 for **complex three-family couplings** with a complete single Lagrangian, including charged singlet f normalization. Follow the published 2001 real limit and the 2010 FLS f=0 pure-2HDM Yukawa limit. Cross-check two independent techniques (e.g. PyR@TE3 and RGBeta); code/model-file actually required, not just library names.
2. Derive beta_lambda6 and beta_lambda7 (and lambda10) for the generic scalar/fermion Zee theory. Q2d proved nonzero source spurions in all 20 solutions but did not derive their coefficients.
3. Only after cross-checks run matched physically fitted Zee lepton solutions, quark mass/CKM, LFV, b->s gamma and FCNC likelihood. In strongly mixed spectra with nonhierarchical states avoid invoking heavy-singlet-first EFT matching without controlled error.

**Current classification:** Q1–Q2d structural + truncated numerical tests PASS, Q2e published reduced real-f RGE implementation pending AF, **FULL GENERAL COMPLEX ZEE RGEs NOT YET COMPLETE**.
