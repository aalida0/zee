# Gate A1L — native SuperIso v5 charged-Higgs NLO anomaly and external Zee matching pilot

**Status: SOURCE-LEVEL BUG CANDIDATE + EXTERNAL MATCHING DIAGNOSTIC,
NOT A PHYSICAL `BR(B->Xs gamma)` AND NOT AN ALLOWED ZEE BENCHMARK.**

This gate continues draft PR #11, which mapped the actual installed
SuperIso 5.0 source. The official SM baseline on AF gave
`BR(b->s gamma)=3.382e-4` and passed the source-verified SM smoke gate.

## The NLO source-order issue to reproduce

In the vendor `src/wilson.c` `CW_calculator`:

1. At roughly line 1596, all Wilson arrays `C0w[ie]`,
   `C1w[ie]`, `C2w[ie]` are initialized to zero.
2. After calculating `C7H_1`, the code tests
   `abs(C7H_1)*alpha_s/(4*pi) > abs(C0w[7])`, and when true
   multiplies `C7H_1` by `abs(C0w[7])/abs(C7H_1)`.
3. The first assignment `C0w[7]=C7SM_0+C7H_0` occurs
   **only after this check**, later in `CW_calculator`, after the limiter.
   Thus for nonzero `C7H_1`, the limiter forces it to zero.
   Analogous limiter expressions apply to `C8H_1`,
   `C9H_1` and `C10H_1`.
4. This does NOT prove every NLO coefficient vanishes:
   `C4H_1` is separately assembled. The vendor also constructs
   explicit NNLO `C3H_2` through `C8H_2` terms.

The bug candidate is physically serious. An apparent NLO/NNLO
`BR(B->Xs gamma)` from the unmodified release cannot be accepted
for model exclusion until its native NLO behavior is resolved and
independently validated.

Gate A1L writes a source-hashed JSON audit. No vendor source
is modified, and the driver deliberately reproduces the
**unmodified** library's result. This allows an objective numerical
test of whether NLO charged `C7,C8` are zero after matching.

## External matching pilot: three full vectors

The new `gateA1l_zee_superiso_matching_pilot.c` links directly
against the built `src/libsuperiso.a` without 2HDMC. It initializes
`struct parameters` using vendor `Init_param/slha_adjust`,
chooses the model's Type-II Yukawa couplings explicitly,
`lambda_u=cot(beta)`, `lambda_d=-tan(beta)`,
and evaluates the native `CW_calculator` at common
`muW=2*mW`, first for SM and then for a single charged
mass at 300 and 700 GeV.

For the LO, NLO and NNLO coefficient vectors separately,
the mixing prescription is

```text
C_Zee^(order,i) = C_SM^(order,i)
  + cos(gamma)^2 * (C_TypeII(mH1)^(order,i) - C_SM^(order,i))
  + sin(gamma)^2 * (C_TypeII(mH2)^(order,i) - C_SM^(order,i)).
```

This is **not** a weighted sum of *branching ratios*.
The two one-charged states have the correct doublet fractions
for Type-II quark couplings. The test checks all operator
indices 1..10, perturbative orders 0..2, with 0 and pi/2
mixing endpoints and the actual gamma=1.089 benchmark.

The `THDM_model=2` flag selects the native positive-THDM
matching path, *not* a built-in complete Zee model.
This pilot does not claim a validation of the full Type-II
2HDM against 2HDMC; that remains a required independent control.

## AF commands

```bash
cd /home/aalida/zee
git fetch origin gateA1l-superiso-charged-matching-diagnostic
git switch gateA1l-superiso-charged-matching-diagnostic

python3 -m unittest discover -s tests \
  -p 'test_gateA1l_superiso_matching_pilot.py' -v

bash scripts/gateA1l_run_superiso_matching_pilot.sh \
  /home/aalida/opt/zee_tools/SuperIso_v5.0 \
  work/gateA1l_superiso_pilot

cat work/gateA1l_superiso_pilot/vendor_nlo_audit.json
cat work/gateA1l_superiso_pilot/result.json
```

The default runner compiles outside the vendor tree, and writes
the SM, gamma=0, gamma=pi/2 and benchmark matching tables to
`work/gateA1l_superiso_pilot/`. It records archive and pilot hashes.

A **numerical pilot PASS** only means (a) matching-vector
superposition and pure-doublet limits close, and (b) the
vendor bug candidate is corroborated by zero charged `C7/C8`
NLO differences; it does **not** mean NLO is correct.

## Subsequent Gate A1M, contingent on these checks

- Reproduce native SuperIso's complete one-charged Type-II
  matching vector using independent published analytic
  LO/NLO formulas, including `C4,C7,C8` and NNLO where justified.
- Make a minimal, **separate version-pinned source copy**
  of SuperIso, protect against unintended changes, and repair the
  NLO limiter with clear comparison tests; avoid guessing
  whether it should cap relative to `C0w` before a proper audit.
- Validate a single-Type-II `BR(B->Xs gamma)` curve against
  a known published calculation and scale variations before
  using it as a Zee constraint.
- Audit `Cprime_calculator` (charged scalar contributions),
  evolution to `mu_b`, interference with the SM,
  perturbative order/scheme, `E_gamma>1.6 GeV`, and
  current experimental/theory uncertainty.
- Combine the complete corrected matching vectors and evaluate
  the physical Zee rate; **never** average two final rates.
- Cross-check with an independent implementation/tool
  before calling the 300/700 GeV point allowed or excluded.

## Scientific caveat

SuperIso's `predict.x` supports injecting *low-scale* (C_7,C_8),
not generic un-evolved high-scale (\Delta C_7(\mu_W)). Feeding
the pilot output directly into `predict.x` would use inconsistent
operator/scale conventions. The pilot deliberately does not do that.

Source: uploaded actual official SuperIso v5.0 `src/wilson.c`
excerpts from Gate A1K; Florentino et al., arXiv:2106.08332
for Zee charged mixing. 
