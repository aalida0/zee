# Gate B1 — Zee model scalar/EWPO/neutrino candidate search

## Physics goal and current status

**Goal:** find fully allowed parameter points maximizing
`BR(H2+ -> H1+ Z)`, and ultimately
`sigma(pp -> tb H2+) * BR(H2+ -> H1+ Z) * BR(H1+ -> tb)`.

**Current status:** Gate B1 is a **candidate pre-screen**, not a
global-fit or exclusion tool. Code is committed, but the AF scan,
synthetic B1 tests and benchmark ranking have **not yet been run**.
There are currently **zero verified fully allowed Zee points** from this
workflow; this is NOT evidence that none exist.

A1V has *actually* run successfully on AF at the 300/700 GeV
benchmark, finding
`BR(B -> Xs gamma)=0.000393119540782089` in the legacy
two-state SuperIso implementation. This observable is not the modern
NNLO result, has no calibrated full theory/experimental likelihood,
and does not constitute an exclusion or pass.

## Why neither stock 2HDMC nor ScannerS can perform the whole scan

- The physical Zee spectrum has TWO charged scalar mass eigenstates
  mixed from doublet/singlet; the pure 2HDM has only ONE.
- Stock **2HDMC** computes 2HDM spectrum/widths, constraints and
  theory checks. **ScannerS** supports its documented scalar models.
  Neither should be fed a physical Zee `mH1` or `mH2` as if this
  represented all mixed charged scalars.
- **Use a Zee-specific scalar potential as the primary engine**
  (Gate 6 generalized to arbitrary physical inputs), including
  singlet-dependent quartics, full Zee charged mass matrix,
  conservative BFB and 19 scalar-scattering eigenvalue constraints.
- The B1 CSV `doublet_subsector_2HDMC_INPUT_ONLY.csv` exports
  `lambda1..lambda5,lambda6=lambda7=0,m12sq,tanbeta` and the
  **UNMIXED doublet charged entry**
  `m_HD^2=mH1^2*cos(gamma)^2+mH2^2*sin(gamma)^2`.
  This can be independently checked using 2HDMC's GENERAL
  potential parametrization, but **2HDMC results are not full Zee
  constraints, widths or charged Higgs bounds**.
- **HiggsTools is compatible with externally supplied models**,
  including more than one charged scalar, provided the full masses,
  decay widths, production cross sections and neutral/charged
  effective couplings are supplied. This requires the complete
  Zee-model prediction stage first. HiggsTools does not generate the
  one-loop Zee neutrino mass matrix.

References:
- 2HDMC: https://arxiv.org/abs/0902.0851
- ScannerS: https://arxiv.org/abs/2007.02985
- HiggsTools custom input:
  https://higgsbounds.gitlab.io/higgstools/alternative_input.html

## Implemented B1 seed scan

1. Random 8D neighborhood of the Florentino-inspired benchmark
   (mH1,mH2,mHheavy,mA,beta,alpha,gamma,m12sq); conservative
   singlet quartics retained near the known benchmark.
2. Check exact Zee tree-level scalar reconstruction and **sufficient
   but not necessary** quartic BFB; all scalar scattering eigenvalues
   below `8*pi`. Does not prove global vacuum.
3. Check **complete scalar S,T,U** with both published
   3D correlated Gaussian oblique fits (Gate A1H).
4. Given one fixed normal-ordering experimental-central-value
   Majorana mass matrix, construct rank-two antisymmetric Zee f
   and solve the one-loop matrix equation
   `Mnu = kappa(mH1,mH2,gamma) * (f Ml Y + (f Ml Y)^T)`.
   Require exact complex-matrix reconstruction, rank 5, finite Y.
   This shows **neutrino oscillation mass/mixing compatibility for
   one algebraic seed**. It is NOT a fit to experimental covariance
   nor proof of LFV viability. The four complex Yukawa null
   directions are not yet varied.
5. At the *same candidate masses and angles*, compute a subset
   of tree tau-LFV and coherently combined scalar one-loop radiative
   amplitudes. These values are labeled `NOT_FULL`; missing
   two-loop Barr-Zee and other diagrams may interfere.
6. Rank survivors by the **partial-width conditional fraction**
   `Gamma(H2->H1Z)/sum_of_INLCUDED_two_body_widths`.
   This is generally an **upper-bound proxy** for the full BR when
   further positive channels are added (within the LO width
   approximation), not a predicted full physical BR.
   The coupling is now computed point by point as
   `g_ZH1H2=(mZ/v)sin(gamma)cos(gamma)` (replacing the
   previously hardcoded `gamma=1.089` value).
7. Export all surviving candidate records, a ranked table,
   2HDMC doublet-only inputs, and the four-column flavor input
   for applying A1V to identical charged-sector parameters.

The `kappa` source and lepton convention follow Chen
[arXiv:2508.18757](https://arxiv.org/abs/2508.18757).
Florentino et al. [arXiv:2106.08332](https://arxiv.org/abs/2106.08332)
omitted neutrino/LFV bounds from their charged cascade scan.
Herrero-Garcia et al. [arXiv:1701.05345](https://arxiv.org/abs/1701.05345)
already performed a Zee neutrino/LFV scan, so a new standalone
neutrino fit is not novel. **Novelty would have to come from their
intersection with cascade benchmarks and full experimental constraints,
or a substantially improved collider strategy.**

## AF run

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only

python3 -m unittest discover -s tests \
   -p 'test_gateB1_zee_candidate_scan.py' -v

python3 scripts/gateB1_zee_candidate_scan.py \
   --points 300 --seed 20261013 --top 20 \
   --quadrature-nodes 96 \
   --output-dir work/gateB1_zee_seed_scan
```

Look for:

```
STATUS GATE_B1_ZEE_SCALAR_EWPO_NEUTRINO_CANDIDATES_NOT_GLOBAL_ALLOWED
COUNTS ...
RANKED_CANDIDATE_ROWS ...
PHYSICALLY_ALLOWED_POINTS unknown
HIGGSTOOLS_NOT_YET_RUN True
MISSING_FLAVOUR_AND_NEUTRINO_LIKELIHOOD True
```

Files:
- `ranked_screened_candidates_NOT_ALLOWED.csv`
- `all_screened_candidates_NOT_ALLOWED.csv`
- `candidate_flavor_inputs.csv`
- `doublet_subsector_2HDMC_INPUT_ONLY.csv`
- `summary.json`

Inspect the top provisional candidates:

```bash
head -n 8 work/gateB1_zee_seed_scan/ranked_screened_candidates_NOT_ALLOWED.csv
```

Reuse the A1V implementation to calculate the legacy flavor
observable on this **pre-screened** grid:

```bash
python3 scripts/gateA1v_run_legacy_response.py \
  --vendor-root work/gateA1m_isolated_nlo_v1/isolated_superiso \
  --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
  --a1u-result work/gateA1u_legacy_zee_br_v1/legacy_two_state_br.json \
  --output-dir work/gateA1v_B1_flavour \
  --grid-csv work/gateB1_zee_seed_scan/candidate_flavor_inputs.csv \
  --max-points 1000 --skip-scale-diagnostic
```

This computes flavor-observable values for the exact candidate
masses and mixing. It **does not implement a calibrated flavor
95% CL exclusion**.

## Next mandatory physics implementation: full experimental filter

Before publishing any *allowed* benchmark table:

1. Complete general Zee leptonic Yukawa scan, varying antisymmetric
   f textures, Yukawa nullspace solutions, PMNS uncertainties,
   Dirac/Majorana phases and neutrino mass ordering. Test
   oscillation likelihood and cosmology with explicitly stated data.
2. Finish LFV predictions: neutral tree and one-/two-loop
   radiative LFV (notably Barr-Zee), charged scalar leptonic
   contributions and widths, mu->3e, mu-e conversion,
   tau decays, universality, relevant EDMs. Source-validate all
   interference and phase conventions.
3. Calculate full scalar couplings, production and total widths
   from a gauge-complete Zee UFO/analytic model. Use proper
   HiggsTools custom model predictions (neutral + both charged
   states), and report coverage of each actual experimental limit.
4. Improve B->Xs gamma beyond A1V diagnostic with defensible
   theory uncertainty and experimental likelihood; add other
   significant flavor observables.
5. Confirm a global neutral vacuum; run broader potential scans
   including k1,k2,k12,lambdaC and theoretical perturbativity.
6. Benchmark ranking should be carried out **after** experimental
   selection, and optimize both true BR and actual LHC signal rate.
   Current B1 ranking is only to prioritize these expensive checks.

## Current illustrative anchor, NOT an allowed point

| mH1 | mH2 | beta | gamma | Partial BR(H2->H1Z) | Partial BR(H1->tb) |
|---:|---:|---:|---:|---:|---:|
| 300 GeV | 700 GeV | 1.394 | 1.089 | ~0.7624 | ~0.9559 |

These partial fractions originate from the historical Gate6 included
channel inventory; charged-singlet leptonic widths and all full model
experimental fits were absent. **A valid benchmark table of fully
allowed points does not yet exist**.

Stop/go: If no sample points survive even the scalar+EWPO screen,
widen the physically motivated scalar scan or reconsider the model
and cascade; do NOT simply loosen experimental constraints.
