# E1: one large original-Zee scan of all 5,557 archived B4 points

## Why E1 is needed

The original B4-v2 postscan completed. The user supplied its complete results (source-pinned original B4 mass model and Q4 one-loop scalar/Yukawa RGEs).

- **30** physically ORIGINAL B4 scalar configurations, **22** optimized D2 f/Y families rechecked.
- **2** original configurations survived the stringent *chosen* 10 TeV sampled running BFB + 55-channel tree-unitarity + absence of a deeper **numerical** tree-vacuum witness.
- **0/30** had a deeper tree-vacuum witness in the finite minimization search. This is **not** a global vacuum proof.
- **28/30** had a first sampled tree-unitarity failure below 10 TeV. **25/30** had the RGE trajectory terminate early from the numerical perturbativity heuristic; **5/30** reached 10 TeV, but three of those five violated unitarity before the endpoint.
- The top-cascade candidates `B4_0000331`, `B4_0001040` and `B4_0001117` violate full 55-channel unitarity at ~862, 758 and 789 GeV respectively, relatively close to their heavy charged-Higgs thresholds. `B4_0004105` first violates it at ~4.54 TeV. B4 ranked primarily by the cascade proxy, *not* by ultraviolet resilience.
- The two original-potential diagnostic survivors are:

| Candidate | mH1± (GeV) | mH2± (GeV) | tanβ | gamma | max recorded 55-channel eigenvalue | D2 incomplete-LFV score | D1/D2 same-score gain |
|---|---:|---:|---:|---:|---:|---:|---:|
| B4_0006862 | 301.6653 | 653.4880 | 7.1146 | 1.0770 | 13.9341 (<8π) | 5.68904e-4 | 2067.66 |
| B4_0006962 | 212.3850 | 740.7361 | 6.7648 | 1.1015 | 23.9214 (<8π) | 4.13632e-4 | 2753.35 |

Across the **22** matched D1 vs D2 partial joint-objective comparisons, the optimization improvement factors range from 1,175.92 to 2,429,598.96, median ~26,419.88. This demonstrates large improvement in **the implemented incomplete-LFV objective**, not a physical CLFV exclusion likelihood. Source B2 subset scores and D2 joint scores are *not commensurate*.

Crucial: the old 30 points were a **biased top-cascade shortlist** chosen from **5,557** scalar/EWPO-screened B4 bins. The 2/30 count does not estimate the fraction of all Zee points satisfying a physical constraint or a Bayesian/flat-prior volume. The 10 TeV target is a *chosen theory-validity criterion*, not a requirement for every TeV-scale collider EFT or model interpretation.

## One decisive broader investigation rather than another serial micro-pilot

New single-command E1 runner: `scripts/zee_gateE1_original_5557_running_funnel.py`. Reuse the **entire already generated 5,557-point B4 archive**. This is the original scalar model in every row: **no C2 counterfactual quartic rescaling**.

The runner checks the saved campaign manifest, B4 summary SHA, full source Q4v13 RGEs.py SHA and 676/676 numerical source audit, plus the previous completed v2 postscan and both original survivor anchor mass spectra. It **fails closed** on stale sources or incomplete data. No need to regenerate 20,000 B4 proposals.

1. For **every** saved scalar/EWPO-screened B4 point, reconstruct all original scalar model quartics and masses from the B4 source, and independently test the complete **55-channel** tree-scalar scattering condition at the heavy charged threshold (`mH2`). Reapply a sampled physical-orbit quartic BFB test using the source's sufficient analytic lower bound.
2. For the subset passing those matching-scale screens, attempt **one deterministic, neutrino-mass-exact, perturbative B2 f/Y** from the same originally validated neutrino central input. A missing f/Y solution for that single choice is **not** an exclusion of the larger Zee Yukawa family. LFV scores at this stage remain an incomplete objective.
3. Run the **original** generated Q4v13 complete one-loop RGEs with that specific B2 family through the **chosen** 10 TeV scale with 24 RK4 steps, sampled-complex-quartic sufficient BFB and the full 55-channel unitarity matrix at every step. **Only those provisionally passing are rerun with 48 steps** to guard against coarse-step false positives. Record source failure / matching-scale failure / RGE failure / resolution inconsistency distinctly in an all-5,557 JSONL audit ledger.
4. Only the **150 highest-cascade** among the double-resolution passing original spectra (if that many exist) undergo the relatively expensive 128-multistart six-real-field charge-breaking-inclusive **tree** vacuum search. A found deeper witness invalidates that EW vacuum within the tested tree potential, while *no witness found is not a global certificate*.
5. Rank up to **100** B4 original model points that passed RGE through 10 TeV and had no deeper tree-vacuum witness found, using cascade proxy plus coarse-mass/mixing diversity. Write source-identical **full original B4 CSV rows** and their **actual neutrino-closed f/Y** into downstream-readable JSON. This is a target for a later multi-solution flavor/HiggsTools/width scan, not allowed models.

**If there are more than 150 full-RGE passes, only the top 150 by collider proxy are vacuum tested**. The others remain `vacuum_not_evaluated`, not classified as failures. The summary reports this count.

## AF command — one full 5,557-point test

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source .venv-flavor-f1/bin/activate
set -o pipefail

# Contract regression, then ONE large 5,557-point source-pinned physics run.
python -m unittest discover -s tests \
  -p 'test_zee_gateE1_original_5557_running_funnel.py' -v

python -u scripts/zee_gateE1_original_5557_running_funnel.py \
  --campaign-dir work/zee_large_integrated_20261020_v1 \
  --postscan-result work/zee_postscan_original_B4_20261020_v2/result.json \
  --output-dir work/zee_E1_all_5557_original_running_20261020_v1 \
  --uv-steps 24 --orbit-samples 512 \
  --vacuum-multistarts 128 --vacuum-maxiter 1000 \
  --max-vacuum-followup 150 \
  2>&1 | tee work/zee_E1_all_5557_original_running_20261020_v1_run.log
```

The new output directory must be empty; do not overwrite the completed B4, C1–C5 or original-B4-v2 artifacts. The script works under `/home`, not `/data`.

## Files and interpretation

- `summary.json`: exact source/input SHA provenance, number of B4 bins, full matched tree and RG running screening cutflows, candidate counts, missing-constraint flags.
- `E1_all_5557_original_model_scalar_RGE_diagnostics.jsonl`: all 5,557 candidates with explicit matching-scale screen / single-B2-texture / one-loop-RGE result, with no physical allowed/excluded labels.
- `E1_vacuum_tested_original_models.json`: vacuum evidence for the top at most 150 qualified RGE spectra; also retains explicit negative witnesses if present.
- `E1_100_original_10TeV_RGE_vacuum_diagnostic_shortlist_NOT_ALLOWED.csv`: up to 100 diverse original scalar-potential models, prioritized for the physical collider cascade, not experimentally allowed.
- `E1_100_original_B4_full_source_NOT_ALLOWED.csv`: **exact** canonical original B4 input rows/observable columns for the chosen shortlist.
- `E1_source_exact_neutrino_solutions_for_100_ranked_NOT_ALLOWED.json`: same actual single f/Y complex matrices, not generic f/Y reused across distinct spectra.

## Scientific limitation

The scan tests a *single* reconstructed, exact-central-neutrino (f,Y) realization for a scalar spectrum, so failure may reflect that choice, and is not a complete theory exclusion. The unitarity condition is tree level applied along one-loop, approximately matched running; gauge and quark Yukawa matching remain illustrative. The zero-witness vacuum result is finite-field numerical evidence, not a rigorous proof. The NLO/NNLO (B\to X_s\gamma) flavor likelihood, complete two-loop LFV, neutrino likelihood with uncertainties and ordering, full HiggsTools and physical widths and cross sections remain pending. Even a 5,557-point success must not be reported as physical allowed Zee parameter space.

**Do not interpret 10 TeV as a fundamental required UV cutoff.** An interesting collider benchmark may still be predictive in a more restricted validity domain. If the E1 survivor count is sparse, the later scan should *sample preferentially from surviving original B4 quartic configurations* instead of maximizing the cascade proxy alone.
