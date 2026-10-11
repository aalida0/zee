# Gate A1M — controlled isolated SuperIso v5 NLO diagnostic

Gate A1L on the AF **passed** matching-superposition closure for
mH1=300 GeV, mH2=700 GeV, beta=1.394, gamma=1.089; LO weighted
shifts at muW=160.7384 GeV were dC7=-0.059186694,
dC8=-0.062660749. However, source-hashed
`src/wilson.c` **b3679eec2244917bf062420e69730f91e2bb32a679febd5d0d28db6af5b707bd**
incorrectly clips nonzero NLO `C7H_1/C8H_1/C9H_1/C10H_1` to
zero because `C0w[7..10]` is still zero at the limiter.
Compiled one-charged matching confirmed zero NLO dC7/dC8.
These facts prevent trusting a native v5 BR as a physics exclusion.

This PR does not modify the official vendor archive, does not
include copyrighted vendor source code, and does not claim physical
Zee `BR(B->Xs gamma)`. It builds an independently tracked,
**separate source directory**, removing **only four known premature
limit statements** after exact, version-pinned SHA256 and line-content
checks. The result is a controlled *diagnostic variant*, not a
certified upstream bugfix.

## AF execution

```bash
cd /home/aalida/zee
git fetch origin gateA1m-superiso-isolated-nlo-repair
git switch gateA1m-superiso-isolated-nlo-repair

python3 -m unittest discover -s tests \
  -p 'test_gateA1m_superiso_isolated_nlo.py' -v

bash scripts/gateA1m_run_isolated_nlo.sh \
  /home/aalida/opt/zee_tools/SuperIso_v5.0 \
  work/gateA1m_isolated_nlo_v1

cat work/gateA1m_isolated_nlo_v1/result.json
cat work/gateA1m_isolated_nlo_v1/source_patch_provenance.json
```

Use a **new output directory for each run**: existing patched trees
cannot be overwritten. Builds use `make -j1` because the vendor v5
static archive recipe is not parallel-safe. No 2HDMC is needed for
this matching-level diagnostic. The runner verifies that both
the official vendor `src/wilson.c` SHA and existing
`src/libsuperiso.a` SHA are unchanged.

## Acceptance checks and interpretation

The comparison consumes full `C_i^{(0,1,2)}` for i=1..10 at one
common matching scale, for a native and isolated build:

- Every Standard Model coefficient must be unchanged.
- LO and NNLO coefficient vectors must be unchanged.
- NLO coefficients other than C7,C8,C9,C10 must be unchanged.
- For native SuperIso, dC7^(1)=dC8^(1)=0 for each single-H+ state.
- For the isolated variant, dC7^(1),dC8^(1) must be nonzero for
  both charged masses.
- Coherent mixing interpolation at NLO must close for C7–C10.
- The existing Gate A1L native pure-H1 and pure-H2 endpoint
  checks must still pass.

**These necessary tests are not enough to validate physical
NLO/NNLO matching.** A removed limiter may restore a formal expression
without establishing correct perturbative coefficients, conventions,
thresholds, missing higher-order effects or numerical stability.

## Next, before a physics exclusion

1. Validate charged-Higgs NLO formulas against independent reference
   results, notably the Misiak/Steinhauser Type-II calculations,
   ensuring conventions for \(C_i^{(0,1,2)}\), \(\alpha_s/4\pi\),
   running top mass, and matching scale.
2. Independently validate the unmodified SM rate and a *single-state*
   Type-II 2HDM BR curve at several charged masses using
   documented \(E_\gamma>1.6\) GeV.
3. Audit `Cprime_calculator` and the full
   `CW_calculator -> C_calculator_base1 -> bsgamma` path, then
   implement Zee matching at the common \(\mu_W\) before RG evolution.
4. Quantify \(\mu_W,\mu_b\) and parametric/perturbative uncertainties
   and use a consistent experimental world average/covariance.
5. Verify no missing Zee-specific charged-singlet Yukawa couplings
   enter the quark loop beyond doublet projections for the chosen
   Type-II quark assignment.
6. Do not average branching ratios and do not use the 551/563 GeV
   LO effective masses as physical constraints.

A future physical BR output must be clearly labeled a *candidate*
until the Type-II and independent-reference controls pass.

**Gate A1M is a source and coefficient diagnostic only.**
