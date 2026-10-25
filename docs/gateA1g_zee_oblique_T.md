# Gate A1G — Zee scalar oblique T: resolve an important literature discrepancy

This is a *single-observable theory consistency audit*, not an S/T/U
electroweak precision acceptance test.

## Critical finding: factor of FOUR in the charged-pair term

The model-general gauge-boson self-energy derivation of
Grimus, Lavoura, Ogreid, Osland,
[arXiv:0711.4022](https://arxiv.org/abs/0711.4022),
Eq.(48b), and [arXiv:0802.4353](https://arxiv.org/abs/0802.4353),
Eq.(28), has

`-2 * |(Udagger U)_[H1,H2]|² * F(mH1²,mH2²)`.

For Zee charged-scalar mixing in Florentino et al.,
[arXiv:2106.08332](https://arxiv.org/abs/2106.08332),
Eq.(24),(26), `(Udagger U)_[H1,H2]=-sin(gamma)cos(gamma)`.

Thus the correct model-general coefficient is
`-2*sin(gamma)^2*cos(gamma)^2*F(mH1²,mH2²)`.

In contrast, Herrero-García et al.,
[arXiv:1701.05345](https://arxiv.org/abs/1701.05345),
Appendix A Eq.(A.1), uses `-1/2*sin²gamma*cos²gamma*F`
and **explicitly notes in footnote 13** that their reference
Grimus gives `-2`. This coefficient changes the benchmark T by
~0.36. We adopt Grimus's general formula, keeping the alternative
ONLY as an audit comparison.

## Model, inputs and numerical results

Scalar candidate from Gate6:
`mh125=125, mH=580.7, mA=633.7, mH1+=300, mH2+=700` GeV.
`alpha=1.398, beta=1.394, gamma=1.089` rad.

**Florentino alignment** uses `cos(beta-alpha)≈1`
for `h125`; it is the complementary convention to that
used in Herrero's Appendix A. The implementation maps
the neutral mixing angles explicitly, including
SM reference-Higgs subtraction.

For the electroweak normalization, use `MW=80.379 GeV`,
`MZ=91.1876 GeV` and `sW²(onshell)=1-MW²/MZ²≈0.223013`.
The physical Grimus T is approximately **-0.0049022**.
The alternative Herrero coefficient gives approximately
**+0.3553858** at identical inputs. Never treat the
latter as independent evidence for exclusion without
resolving the formula conflict.

The test suite checks:
1. F positivity, symmetry and the smooth equal-mass limit.
2. Correct `Udagger U` charged mixing overlap and `-2` factor.
3. Standard two-Higgs-doublet limit when the singlet decouples.
4. Independence of gamma when charged masses are degenerate.
5. Custodial/fully degenerate scalar limit giving T=0.
6. Numerical reference values for both literature coefficients.

## Run on AF

Stacked after Gate A1F PR #6:

```bash
cd /home/aalida/zee
git fetch origin gateA1g-zee-oblique-T-audit
git switch gateA1g-zee-oblique-T-audit
python3 -m unittest discover -s tests -p 'test_gateA1g_zee_oblique_T.py' -v
python3 scripts/gateA1g_zee_oblique_T.py \
    --output work/gateA1g_zee_oblique_T.json
```

## What has NOT passed

- **S and U** are not computed. Consequently the **correlated
  three-parameter electroweak fit has NOT been applied**.
- Quoted Gfitter STU central values and covariances are not
  appropriate for an isolated scalar T acceptance claim; the
  model's S, T and U must be treated together:
  https://project-gfitter.web.cern.ch/Oblique_Parameters/
- Scalar EW input scheme and higher-order effects require
  documentation/consistency before publication.
- HiggsTools limits, full B->Xs gamma, global vacuum,
  full Barr-Zee LFV and physical cascade rate are still open.

The **next physics gate is to implement S, U** from the same
Grimus reference (or independently verify Herrero's B22
expressions) and evaluate a properly correlated joint S/T/U
test. *Do not declare the scalar benchmark EW-allowed yet.*
