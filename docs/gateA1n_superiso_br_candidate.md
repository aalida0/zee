# Gate A1N — SuperIso v5 inclusive BR candidate and Type-II controls

**Purpose:** quantify how the confirmed SuperIso v5.0 charged-Higgs
NLO clipping defect affects **candidate** inclusive (B\to X_s\gamma)
calculations, then validate the actual SM and Type-II limits before any
Zee exclusion. **No allowed/excluded decision is made in this gate.**

Preceding validated work:
- Gate A1J: official SuperIso 5.0 `./sm.x` gives
  `BR(b->s gamma)=3.382e-04` for (E_\gamma>1.6\) GeV.
- Gate A1L: entire matched Zee Wilson-coefficient vector closes
  exactly at gamma 0, pi/2 and 1.089; original native C7/C8 NLO
  charged contributions are incorrectly zeroed.
- Gate A1M: in a separate **version-hash-pinned** SuperIso copy,
  removal of exactly four NLO limiter statements restores
  \(\Delta C_7^{(1)}(300)=1.7331863494\),
  \(\Delta C_7^{(1)}(700)=0.9519167622\),
  \(\Delta C_8^{(1)}(300)=0.7628644096\),
  \(\Delta C_8^{(1)}(700)=0.5332732317\).
  All SM, LO, NNLO and unrelated NLO matching entries remain unchanged.

## AF commands

Use the **existing**, successfully built Gate A1M isolated library.
No source modifications, new patch, or installation are made here.

```bash
cd /home/aalida/zee
git fetch origin gateA1n-superiso-br-candidate-controls
git switch gateA1n-superiso-br-candidate-controls

python3 -m unittest discover -s tests \
  -p 'test_gateA1n_br_candidate_controls.py' -v

bash scripts/gateA1n_run_br_candidate.sh \
  /home/aalida/opt/zee_tools/SuperIso_v5.0 \
  /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
  work/gateA1n_br_candidate

cat work/gateA1n_br_candidate/result.json
```

The runner confirms A1M source-hash provenance; it separately links
the external C driver to the official and isolated libraries, then
calls the complete SuperIso workflow at the same scale:

```text
CW_calculator(2, C0w, C1w, C2w, muW, &param)
    -> coherent mixing of matched SM+H1+H2 coefficient vectors
    -> C_calculator_base1(...)  [QCD evolution]
    -> Cprime_calculator(...)   [stock SuperIso convention]
    -> bsgamma(...)             [Egamma>1.6 GeV]
```

The frozen input is beta=1.394 rad, gamma=1.089 rad,
mH1=300 GeV, mH2=700 GeV and Type-II quark couplings
lambda_u=cot(beta), lambda_d=-tan(beta).
The 2HDM matching flag `THDM_model=2` is a path selector,
NOT a native Zee-model implementation.

Checks run for the official/unmodified and isolated libraries:
- SM inclusive BR equals Gate A1J `sm_output.log` to rounding tolerance.
- Source-only NLO repair leaves the SM rate unchanged for all
  five tested (muW,mub) combinations.
- Direct pure-Type-II 300/700/1000/2000 GeV controls.
- Explicit gamma=0 and gamma=pi/2 BR endpoints agree with the
  corresponding one-charged Type-II rates.
- The two-state candidate rate is computed only **after**
  matching coefficients are added *before* RG and BR.
- `muW`: nominal 2*mW, half, double.
- `mub`: nominal mb_pole/2, ×0.8, ×1.5 (avoid excessive
  strong coupling in sub-GeV-scale comparisons).
- Original-vs-isolated flavour effects and the approach of
  the 2000-GeV Type-II result to the SM are reported.

**Validation stops** if the SM driver fails baseline closure,
a matching endpoint fails, the original/isolated SM differs,
unexpected primed coefficients appear, or the BR is nonfinite.

The resulting `BR` values are explicitly **CANDIDATES**. Do not
call the benchmark excluded/allowed or use them for publication,
even if the output passes. A pure Type-II numerical *control* is
not an independent reference calculation.

## Remaining required gates

1. Obtain a known Type-II NNLO reference **prediction curve**
   for multiple charged-Higgs masses at the **same top-mass scheme,
   photon-energy threshold, alpha_s, masses and SM inputs**.
   A published *lower bound* like 570–800 GeV alone is not a
   numerical prediction to validate line-by-line.
2. Independently validate the charged-Higgs NLO and NNLO Wilson
   matching against the calculations of Hermann, Misiak and
   Steinhauser (arXiv:1208.2788), not merely against a SuperIso
   version exhibiting the same formula family.
3. Check SuperIso's `Cprime_calculator` / Type-II and Zee
   chirality-changing contributions, missing off-diagonal
   charged-singlet couplings, and matching thresholds.
4. Quantify numerical and perturbative scale dependence and
   theoretical/experimental covariance, then construct a
   documented CL consistency test.
5. Compare to at least one independent implementation and
   establish numerical uncertainties before declaring a
   model point allowed or excluded.

External reference SM prediction:
Misiak, Rehman, Steinhauser,
[JHEP 06 (2020) 175](https://arxiv.org/abs/2002.01548),
`BR(B->Xs gamma)=(3.40 +/- 0.17)e-4` at
`Egamma>1.6 GeV`. This is **context**, not a guaranteed
identical-SM-input validation of our SuperIso configuration.
