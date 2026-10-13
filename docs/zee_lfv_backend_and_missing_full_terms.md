# Zee LFV backend — B5 partial implementation and complete-LFV roadmap

## Scope and honesty gate

**Committed code, requires AF regression + physical run.** This is NOT
a complete general-Zee LFV prediction, exclusion or likelihood. All
files and report statuses contain `NOT_ALLOWED`. The pipeline
`full_LFV.enabled` **must stay false** and raising it true still
throws an explicit unsupported-backend error.

Instead of producing more separate "allowed benchmark" lists, the
existing `scripts/zee_pipeline.py` now calls
`scripts/zee_lfv_backend.py` as its **extended partial LFV adapter**.
The adapter consumes the exact B2 complex `f,Y^ell` solutions and
candidate scalar masses/angles; it does not repeat neutrino fitting.

## What B5 computes

- **Tree-level neutral** h(125)/H/A exchange with coherent scalar
  interference and full complex couplings for
  `mu->3e`, `tau->3e`, `tau->3mu`, `tau->mu ee`,
  `tau->e mu mu`.
  Formula: Herrero-Garcia et al.,
  [arXiv:1701.05345](https://arxiv.org/abs/1701.05345),
  Eq. (3.8)-(3.9). Validated against existing A1D tau->3mu and
  tau->e mu mu results; **NOT** a complete physical 3-body decay
  (no virtual-photon, Z penguin, box, and interference).
- **Coherent scalar one-loop radiative** `mu->e gamma`,
  `tau->mu gamma`, `tau->e gamma`: reused from B2's already
  assembled neutral/charged loops rather than independently
  recalculated. Still **missing the full two-loop Barr-Zee**.
- **Charged-singlet f-only universality, leading order**:
  muon lifetime/Fermi constant and
  `(g_tau/g_mu)^2,(g_tau/g_e)^2,(g_mu/g_e)^2` shifts from
  [arXiv:1701.05345](https://arxiv.org/abs/1701.05345),
  Eq. (3.28)-(3.33). The original simplified Eqs. (3.31)-(3.32)
  set `f_e_mu=0`; because our B2 allows generic antisymmetric
  `f`, this implementation restores the **negative muon-decay
  shift** to the first two ratios:
  ```
  k = sqrt(2)/G_F * (sin²gamma/mH1² + cos²gamma/mH2²)

  delta_GF_mu² = k |f_e_mu|²
  delta_(g_tau/g_mu)² = k (|f_e_tau|² - |f_e_mu|²)
  delta_(g_tau/g_e)²  = k (|f_mu_tau|² - |f_e_mu|²)
  delta_(g_mu/g_e)²   = k (|f_mu_tau|² - |f_e_tau|²)
  ```
  Charged-doublet `Y^ell` contributions and their SM
  interference are **not** included here.

These shifts are standalone model-component diagnostics; they
must not be used as an experimental universality pass/fail test.

## Experimental 90% CL reference numbers, NOT complete exclusions

- `mu->3e` < 1.0e-12 (SINDRUM 1988).
- `tau->3mu` < 1.9e-8 (Belle II 424/fb published result).
- `tau->3e` < 2.7e-8 (Belle), `tau->mu ee` < 1.8e-8,
  `tau->e mu mu` < 2.7e-8. These are historical single-analysis
  references and must be checked against 2026 combinations
  before final physics conclusions.
- `mu->e gamma` < 1.5e-13 (MEG II, EPJC 2025),
  already sourced in B2 and reused here.

Sources:
- [SINDRUM mu->3e](https://doi.org/10.1016/0550-3213(88)90462-2)
- [MEG II EPJC (2025)](
  https://doi.org/10.1140/epjc/s10052-025-14906-3)
- [HFLAV tau LFV compilation](https://hflav-eos.web.cern.ch/hflav-eos/tau/end-2023/lfv-combinations.html)
- [Belle II tau->3mu update](https://inspirehep.net/)

No `BR_tree/experimental_limit < 1` is a full-model pass:
interference between tree, photon-penguin and box terms can change
the total rate.

## Run now on the existing successful B2 pilot outputs (no rescanning)

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source ~/fccee_zh/scripts/setup_key4hep.sh

python3 -m unittest discover -s tests \
  -p 'test_zee_lfv_backend.py' -v
python3 -m unittest discover -s tests \
  -p 'test_zee_pipeline.py' -v

python3 scripts/zee_lfv_backend.py \
  --points work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --b2-json work/zee_pipeline_b4pilot_v1/B2_neutrino/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --output-dir work/zee_lfv_B5_b4pilot_v1
```

Outputs:
- `lfv_partial_3lepton_universality_NOT_ALLOWED.csv`
  (one row per stored Yukawa solution; should be 150 here).
- `all_partial_LFV_details_NOT_ALLOWED.json`
  full complex-`Y` matched result and separate partial channel rates.
- `summary.json` completeness contract.

With the config `extended_partial_LFV.enabled=true` (committed),
the same backend automatically runs in a **NEW** single-entry pipeline:
```bash
python3 scripts/zee_pipeline.py \
  --points work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --settings configs/zee_pipeline_partial.json \
  --output-dir work/zee_pipeline_b4pilot_v2
```

Keep `full_LFV.enabled=false`; no full-model acceptance can be
asserted from the partial predictions.

## The next scientific implementation (not yet in this commit)

1. **Barr-Zee LFV dipoles:** all numerically relevant neutral
   scalar-mediated fermion (top,bottom,tau), W, and charged-scalar
   contributions for the chosen scalar potential and Type-II-like
   QUARK couplings. Fix independent helicity conventions; compare
   against explicit published full-Zee benchmark amplitudes and
   CP-even/odd decoupling limits. Summing branching ratios instead
   of amplitudes is unacceptable.
2. **Full three-lepton amplitudes:** tree neutral, photon-penguin
   dipole and non-dipole, Z-penguin, box with coherent interference.
   This is essential for making a **physical mu->3e** comparison.
3. **Muon-to-electron conversion:** scalar-mediated *quark* Yukawa
   operators from Type-II-like quarks, photonic dipole/non-dipole,
   nuclear overlap inputs (Au current, Al projection). The dipole-only
   0.0027x approximation from Heeck & Thapa 2023 assumes a
   different restricted quark-coupling setup and **must not be
   used as our full Type-II-like Zee prediction**.
4. **Full universal muon/tau decays:** include charged-doublet
   `Y^ell` contributions, chirality and neutrino-flavor sums, the
   measured effective G_F, and the correlated experimental ratios.
5. **Current/forecast likelihoods:** dated experimental inputs,
   CL convention, correlated observables and theory uncertainties,
   then *only then* set `full_LFV.enabled=true`.

### A critical physics detail

A "large" cascade BR alone does not constitute a neutrino-flavor
consistent benchmark: it must retain a **single common Zee scalar,
quark, and lepton Lagrangian** and use complete charged decay
inventory. The lepton Yukawa structures are explicitly general
(Type-III-like) in the charged-lepton sector; imposing a naive
exact Type-II Z2 symmetry on the leptons would prevent realistic
oscillation data.
