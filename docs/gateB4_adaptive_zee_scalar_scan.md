# Gate B4 — adaptive Zee scalar/theory/EWPO exploration

## Why B4 was needed

The initial B1 300-point pilot had 2 surviving scalar/EWPO spectra:
**candidate 0 was the manually inserted anchor**, and only candidate
32 was independently sampled. This DOES NOT mean the model has only
two viable points or that only 0.67% of parameter space is allowed.

B1 independently perturbed correlated physical masses, beta, mixing
angles and a soft term. It also fixed the Zee singlet quartics. Most
points failed the sufficient scalar BFB/unitarity screen.

B4 uses **12 adapted parameter-space directions**:
`mH1,mH2,mh2,ma,beta,alpha-beta,gamma,M_soft^2,ln(lambdaC),
ln(k1),ln(k2),k12/min(k1,k2)`, where
`M_soft^2=m12sq/(sin(beta)*cos(beta))`.
Positive singlet quartics and `|k12|<min(k1,k2)` are built into the
proposal parameterization (a **sufficient but not necessary** BFB
subcondition). The complete already implemented scalar-theory
screens must still pass; the code DOES NOT loosen theoretical cuts.

Multiple independent chains start from the B1 **screened** candidates.
The scanner mixes single-coordinate, block, and occasional global
moves. It adjusts global proposal scale using blockwise
theory+EWPO-screen acceptance. A binned deduplication collects
distinct points for follow-up; a mass/mixing-diverse shortlist
prevents retaining only tiny variations of one spectrum.

**Not an MCMC posterior, random uniform sample, parameter-space
volume estimate, new exclusion, or globally unbiased optimizer.**
It is explicitly a constrained candidate-discovery method.

## Source of physics calculations

The B4 scanner reuses:
- Gate6 **exact Zee scalar mass reconstruction**, conservative
  sufficient quartic stability, four scalar scattering sectors and
  tree unitarity.
- Gate A1H scalar oblique `S,T,U` and two published correlated
  95% 3D Gaussian-fit ellipsoids.
- Gate6 LO included decay inventory, with the **obsolete Type-II
  charged-lepton tau partial width removed**. The resulting
  BR and sin²(gamma)-weighted cascade proxy are upper-bound-style
  diagnostics conditional on the included LO channels, NOT physical
  branching ratios or actual hadronic cross sections.

B4 explicitly writes the scanned values of
`lc,k1,k2,k12` in every output row. Gate B3 was amended to
**read those columns rather than silently overwriting them with
the B1 fixed constants**. The B2 and B3 input formats remain
compatible (after passing matching B4 shortlisted inputs).

## Current status and how to run

The scanner, B3 quartic handoff and regression tests are committed.
The adaptive algorithm has been smoke-tested locally against stub
theory/EWPO backends. **The source-physics-dependent regression suite
and full run require execution on AF**; a stub smoke test is not
evidence of any physically accepted candidate.

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source ~/fccee_zh/scripts/setup_key4hep.sh

python3 -m unittest discover -s tests \
  -p 'test_gateB4_adaptive_zee_scalar_scan.py' -v

# First: smaller, real-physics pilot.
python3 scripts/gateB4_adaptive_zee_scalar_scan.py \
  --seed-csv work/gateB1_zee_seed_scan/all_screened_candidates_NOT_ALLOWED.csv \
  --steps 1200 --chains 12 --top 30 \
  --quadrature-nodes 96 --random-seed 20261013 \
  --output-dir work/gateB4_zee_adaptive_pilot
```

Only if the tests and pilot behave sensibly:

```bash
python3 scripts/gateB4_adaptive_zee_scalar_scan.py \
  --seed-csv work/gateB1_zee_seed_scan/all_screened_candidates_NOT_ALLOWED.csv \
  --steps 10000 --chains 16 --top 50 \
  --quadrature-nodes 96 --random-seed 20261013 \
  --output-dir work/gateB4_zee_adaptive_scan
```

Outputs (every row marked `NOT_ALLOWED`):
- `summary.json`: stage rejection counts, adapted step history,
  unique coarse-cell count, exact missing constraints.
- `all_screened_candidates_NOT_ALLOWED.csv`: retained distinct
  scalar/EWPO survivors, including quartics.
- `ranked_by_cascade_proxy_NOT_ALLOWED.csv`: top mass/mixing-weighted
  nonleptonic **partial-channel proxy**.
- `ranked_by_cascade_BR_NOT_ALLOWED.csv`: highest nonleptonic
  conditional `H2 -> H1 Z` fraction proxy.
- `diverse_candidates_for_B2_NOT_ALLOWED.csv`: a smaller,
  mass/mixing-diverse full scalar input table.
- `flavour_inputs_selected.csv`: masses, mixing and tanbeta for
  applying legacy A1V SuperIso to the SAME selected scalar inputs.

Inspect:
```bash
cat work/gateB4_zee_adaptive_pilot/summary.json
head -n 8 work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv
```

A high scanner acceptance rate means the **proposal** is efficient,
not that the physical model is mostly allowed. Conversely, a low
acceptance rate does not imply exclusion.

## Hand off a selected subset to B2 and B3

Use the SAME `diverse_candidates_for_B2_NOT_ALLOWED.csv` file
for both B2's neutrino-compatible Yukawa construction and B3's
general-Zee charged leptonic widths:

```bash
python3 scripts/gateB2_zee_neutrino_family_scan.py \
  --b1-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --trials-per-candidate 100 --top 5 --seed 20261014 \
  --output-dir work/gateB4_zee_adaptive_pilot/B2_flavour

python3 scripts/gateB3_general_zee_charged_lepton_widths.py \
  --b1-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --b2-json work/gateB4_zee_adaptive_pilot/B2_flavour/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --top 5 \
  --output-dir work/gateB4_zee_adaptive_pilot/B3_widths
```

B2 still fits **one fixed normal-ordering target** and applies
partial LFV diagnostics, NOT a full neutrino likelihood. The updated
B3 width inventory remains leading-order and includes only listed
channels. Neither is a viability certification.

## Paper 1 threshold

A standalone constraints paper cannot rely solely on a large adaptive
list of pre-screened points. The minimum physics work is:

1. General-Zee full neutrino parameter variation (including Majorana
   phases and alternate ordering) and independently validated LFV,
   including Barr-Zee, mu -> 3e, mu-e conversion and universality.
2. Model-complete decays, model-compatible HiggsTools predictions,
   and contemporary direct Higgs/charged-Higgs bounds.
3. Proper matched 2026 two-state B -> Xs gamma likelihood with
   transparent perturbative/hadronic uncertainties.
4. More complete vacuum and flavor symmetry consistency checks.
5. Physically allowed point set and post-constraint envelope of
   sigma(tbH2) * BR(H2->H1Z) * BR(H1->tb).
   Show constraint-ablation shifts, flavor–cascade correlations and
   credible future sensitivity forecasts.

References: Florentino et al. arXiv:2106.08332; Herrero-Garcia
et al. arXiv:1701.05345; Chen arXiv:2508.18757.
