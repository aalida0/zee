# Zee Barr–Zee dipole program — kernel-first validation

**Current state (13 October 2026):** dimensionless fermion-photon
loop functions `f(z)` and `g(z)` are committed for AF
regression. **Physical Barr–Zee `C_L,C_R` amplitudes and LFV
exclusions are NOT implemented.** This work is an incremental
scientific calculation, NOT a complete experimental constraint.

## Independent mathematical source

Howard E. Haber, *Evaluating integrals arising from Barr–Zee
diagrams* (March 2024),
https://scipp.ucsc.edu/~haber/webpage/BarrZee.pdf

Let `u=x(1-x)`, `z=m_f²/m_phi² > 0`. Haber Eqs. (1),
(39) and (40) give:

```
g(z) = (z/2) integral_0^1 [ ln(u/z)/(u-z) ] dx

f(z) = (z/2) integral_0^1 [ (1-2u)*ln(u/z)/(u-z) ] dx

f(z) = z*(2+ln z) + (1-2z)*g(z)
```

The apparent `0/0` at `u=z` is removable. With
`t=(u-z)/z`, the `g` integrand is
`(1/2)*ln(1+t)/t`, which permits stable series evaluation
at `t≈0`. The implemented `scipy.integrate.quad` splits
the integration at both roots of `u=z` when `z<1/4`.
Only real positive z are supported.

Published exact regression identities from Haber:
- `g(1/4) = ln(2)`.
- `f(1/4) = 1/2`.
- `g(1) ≈ 1.1719536193`.
- `f(1) ≈ 0.8280463807`.
- Near small `z`, `f,g ~ (z/2)ln²(z)`
  (not accurate for finite z if subleading logs matter).

The tests also implement an **independent direct quadrature**
using the original `z*log(u/z)/(u-z)` integrand, not merely the
identity used in code. Tests have been committed; AF must execute
them before a production scan uses the values.

A local SciPy 1.17.0 numerical check of the quadrature produced
`g(.25)=0.6931471805599457`,
`g(1)=1.1719536193447295`,
`f(.25)=0.5000000000000002`,
`f(1)=0.8280463806552705`.

## AF tests + run WITHOUT redoing neutrino simulations

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source ~/fccee_zh/scripts/setup_key4hep.sh

python3 -m unittest discover -s tests \
  -p 'test_zee_barr_zee_kernels.py' -v

python3 -m unittest discover -s tests \
  -p 'test_zee_pipeline.py' -v

python3 scripts/zee_barr_zee_kernels.py \
  --points work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --output-dir work/zee_barr_zee_math_B4pilot
```

The standalone program writes 30 spectra × 3 neutral bosons
(`h125,H,A`) × 3 nominal charged fermions (`t,b,tau`)
= **270 loop entries**. No physical `mu->e gamma` rate is
derived from those entries.

The unified driver has an optional `barr_zee_kernel_diagnostic`
stage, activated by the committed
`configs/zee_pipeline_partial.json`; it does not activate
`full_LFV.enabled`. To use the unified driver with this new stage,
pick a **new empty** output directory, e.g.

```bash
python3 scripts/zee_pipeline.py \
  --points work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --settings configs/zee_pipeline_partial.json \
  --output-dir work/zee_pipeline_b4pilot_v3
```

To avoid recomputing the existing diagnostic pipeline, execute
the standalone kernel as above instead.

## Required work before plugging f/g into physical dipoles

1. Fix **one complete Higgs-basis Yukawa and charged-scalar
   mixing convention** (Chen 2025 / Florentino 2021).
2. Derive fermionic scalar and pseudoscalar Barr–Zee photon
   contributions to `C_L,C_R`, including relative CP signs,
   complex Yukawa indices, electromagnetic-charge and color
   factors. Normalize explicitly to Herrero-García et al.
   (2017) Eq.(3.11)-(3.12) used by the B2 backend.
3. Validate the full fermionic amplitude at a **published**
   Type-III/Type-II 2HDM benchmark, including h/H/A cancellations.
   The loop-function checks in this document are necessary
   but not enough.
4. Add **W**, charged-scalar, Z-exchange diagrams as appropriate
   for the Zee spectrum and check electromagnetic Ward identities.
   A convenient reference for the relevant general 2HDM top and
   W contributions is S. Davidson,
   *mu->e gamma in the 2HDM: an exercise in EFT*,
   EPJC 76, 258 (2016), https://arxiv.org/abs/1601.01949.
5. Interfere the validated Barr–Zee `C_L,C_R` amplitudes with
   the existing coherent one-loop `C_L,C_R`, not rates.
   Add 3lepton penguins/boxes and `mu-e` conversion afterward.

**STOP:** No numerical `f(z),g(z)` entry here is an
experimentally excluded or allowed Zee model point.
