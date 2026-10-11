# Gate A1D — Neutral tree LFV: reproducibility and physics boundary

**Status: neutral-tree-only calculation, NOT a full lepton flavour fit.**
Stacked on Gate A1C (PR #3). Input is the Gate A1B hierarchical
normal-ordering neutrino seed with max|Y^ell|~9.46e-6.

## Analytic sources, conventions and reference closure

Chen 2025 arXiv:2508.18757 Eq.(4) defines
`-L = bar(l_R)Y^ell l_L (H2^0+iA)+h.c.`,
with **no extra sqrt(2)** in the physical coupling. The effective
two-neutral-scalar mixing convention follows Florentino et al.
arXiv:2106.08332 Eqs.(21),(27),(28). With delta=beta-alpha
(Florentino, not the conventional 2HDM alignment naming):

- `h125 = cos(delta) H1 - sin(delta) H2`.
- `Hheavy = sin(delta) H1 + cos(delta) H2`.
- `C_h = cos(delta)*diag(mell)/v - sin(delta)*Y`.
- `C_H = sin(delta)*diag(mell)/v + cos(delta)*Y`.
- `C_A = i*Y`.

For a neutral scalar `S`, the charged-lepton vertex is
`-S bar(ell_i)[C_ij P_L + C_ji* P_R] ell_j`.

Using the coherent sums and identical-particle symmetry factors of
Herrero-Garcia et al., JHEP04(2017)130, arXiv:1701.05345,
Eqs.(3.8)-(3.9), the implementation reproduces
**Chen Table I NO** from its *printed, rounded* parameters with
its 150 GeV H and 200 GeV A illustration:

| Decay | Chen published | Our rounded-input reconstruction |
| --- | ---: | ---: |
| tau->3mu | 3.9e-10 | 3.785e-10 |
| tau->e mu mu | 4.7e-10 | 4.581e-10 |

Both agree within 3% (published entries are rounded). This cross
check tests the chirality coefficients and normalization, not the
full observable at all orders.

## Actual project scalar candidate (still unvalidated)

Use `mh=125, mH=580.7, mA=633.7` GeV;
`alpha=1.398, beta=1.394`; v=246.21965 GeV.

The Gate A1B minimum-norm Yukawa seed yields:
- `BR(tau->3mu)_{neutral_tree} ≈ 1.637e-23`.
- `BR(tau->e mu mu)_{neutral_tree} ≈ 2.859e-26`.

Belle II has `BR(tau->3mu)<1.9e-8` (90% CL), JHEP09(2024)062:
https://docs.belle2.org/pub_data/publications/4379/

**IMPORTANT:** These computed quantities are not necessarily upper
or lower bounds on the full Zee amplitudes because loop and dipole
contributions interfere; a small tree amplitude is NOT proof of
complete LFV viability. This gate also neglects phase-space charged
lepton masses and QED radiative corrections.

## Run on AF

```bash
cd /home/aalida/zee
git fetch origin gateA1d-neutral-tree-tau-lfv
git switch gateA1d-neutral-tree-tau-lfv
python3 -m unittest discover -s tests -p 'test_gateA1d_neutral_tree_lfv.py' -v
python3 scripts/gateA1d_neutral_tree_lfv.py \
  --output work/gateA1d_neutral_tree_lfv.json
```

Next physics gate: compute the complete one-loop neutral and charged
dipoles including both Y and f, plus two-loop Barr-Zee diagrams
with the Type-II quark sector, cross-validated against a published
LFV benchmark. Then revisit the physical widths and rate envelope.
