# Large Zee campaign — numerical findings and decisive original-potential audit

**Data:** user-provided UChicago AF stdout, October 2026. The original saved large-scan stage outputs live under `/home/aalida/zee/work/zee_large_integrated_20261020_v1/`. Repository snapshot used by that run: `6fc90b7040c813b37a6edd0250208b2a7117b9d2`. No new AF execution was performed by this GitHub commit.

## What the first 20,000-proposal campaign actually found

- 20,000 B4 proposal attempts from **two correlated B1 seeds**, yielding **5,557 retained coarse scalar/EWPO bins**. The sample is adaptive, not an unbiased prior or parameter-space coverage.
- Of those screened bins **5,471** reconstruct the *two C2–C5 selected counterfactual scalar-potential variants* at tree level; **30** diverse candidates were selected. This filtering must not be mistaken for a physical exclusion of the remaining B4 points.
- All recorded stages completed and passed contract integrity checks: C1 90 RGE trajectories, C2 240 paired scalar-potential trajectories, C3 60 complex BFB, C4 60 running 55-channel unitarity, C5 60 charge-breaking-inclusive numerical vacuum searches, D1 150 saved neutrino/partial-LFV configurations, D2 22 partially optimized spectra.
- The 60 *counterfactual* scalar-potential tests divide into **42** C4-running-screen pass with no C5 deeper potential witness; **11** C4-running-screen pass with explicit deeper-tree-vacuum witnesses; **7** C4-running-screen fail without such witnesses.
- Among the 30 spectra: **20** pass the paired diagnostic screens in both counterfactual variants; **2** in one variant; **5** have a deeper tree-vacuum witness in both variants; **3** fail the paired running-theory diagnostic in both variants. Thus **22** have at least one **counterfactual** diagnostic variant worth further examination, NOT 22 physically viable ORIGINAL B4 potentials.

Top included-channel cascade proxies (not complete BRs/cross sections):

| candidate | mH1 GeV | mH2 GeV | B3 included-channel production-weighted cascade proxy | legacy B→Xsγ conditional BR |
|---|---:|---:|---:|---:|
| B4_0000331 | 213.601 | 690.151 | 0.6742320 | 0.000394208 |
| B4_0004105 | 216.218 | 669.188 | 0.6722387 | 0.000399432 |
| B4_0001117 | 208.652 | 706.170 | 0.6704868 | 0.000391468 |
| B4_0001040 | 208.652 | 677.575 | 0.6683945 | 0.000393519 |

The first 30-candidate table compares **incommensurate** LFV objectives: `best_partial_LFV_score_NOT_A_LIKELIHOOD` is the **B2 original subset** (mostly original one-loop), while `D2_optimized_partial_score_NOT_A_LIKELIHOOD` is the **D1 extended joint partial LFV** (coherent included fermion-photon Barr–Zee and neutral-tree 3l terms). Across the 22 D2 rows, D2 values are all larger than B2 values (about 27 to 1e5 times), but that is **not evidence of optimizer deterioration**. D2's implementation explicitly verifies `optimized_joint_score <= starting_same_D1_joint_score` up to tolerance. Compare with the actual D1 `joint_incomplete_LFV_score_NOT_EXCLUSION` minimum over B2 roots, **never the B2 smaller-definition column**.

None of the partial LFV scores establishes physical CLFV acceptance. The "under one" values lack important electroweak, charged-scalar and Z-mediated two-loop amplitudes, mu-e conversion, three-body loop contributions, and full experimental likelihood.

## Why a second complete B4 scan is the wrong next calculation

The 22/30 label uses **two potentials with adjusted singlet/2HDM quartics and soft terms**, rather than the source B4 point whose scalar parameters were saved and whose legacy quark-flavor number appears in the joined table. Mixing these interpretations is not a valid *model-point* classification.

Moreover, the D2 optimized f/Y changes the full one-loop RG trajectories. Original C1–C4 running evaluations used saved B2 textures, not the optimized D2 Yukawas. The old C4 "pass" must therefore be **retested**, not inherited by optimized points.

We therefore implemented ONE source-locked, model-complete **numerical diagnostic** targeted at the original 30 points instead of a further larger adaptive proposal stage.

## One decisive AF follow-up command

New script: `scripts/zee_postscan_original_B4_and_optimized_Yukawa_audit.py`
and `tests/test_zee_postscan_original_B4_and_optimized_Yukawa_audit.py`.

From the same AF checkout and environment as the successful 20,000-proposal run:

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source .venv-flavor-f1/bin/activate
set -o pipefail

# One regression + one complete 30-scalar / 22-Yukawa paired rerun.
python -m unittest discover -s tests \
  -p 'test_zee_postscan_original_B4_and_optimized_Yukawa_audit.py' -v

python -u scripts/zee_postscan_original_B4_and_optimized_Yukawa_audit.py \
  --campaign-dir work/zee_large_integrated_20261020_v1 \
  --output-dir work/zee_postscan_original_B4_20261020_v1 \
  --uv-steps 24 --orbit-samples 2048 \
  --vacuum-multistarts 128 --vacuum-maxiter 1000 \
  2>&1 | tee work/zee_postscan_original_B4_20261020_v1_run.log
```

The runner:
1. Fails closed if the saved campaign, 676/676 Q4v13 report, original B4 30-point table, D1 or D2 provenance SHA do not match.
2. Reads all 30 **original** B4 points and original B2 rank-1 f/Y.
3. Recomputes the original (not counterfactual) one-loop general-Zee running to 10 TeV with all complex quartic BFB and 55-channel tree unitarity, including 24/48-step numerical agreement. This is not threshold-matched NLO running.
4. Performs a new 128-multistart charge-breaking-inclusive six-real-field numerical tree-vacuum search on each original B4 scalar potential. A **deeper potential witness** is actual evidence against the original EW minimum in the assumed tree potential; absence of a found witness still does not prove global stability.
5. For each of the 22 D2-optimized Yukawa solutions, **recomputes the identical D1 joint incomplete-LFV score** from saved complex f/Y arrays, checks the D1 baseline reference, then reruns 24/48-step original-potential RGE with the optimized Yukawas. **No B2 rank-1 theory pass is silently transferred to a different f/Y.**
6. Writes a 30-row joined CSV separating original-source B2 rank1 and D2 optimized-fY theory results.

### Results to share

```bash
cat work/zee_postscan_original_B4_20261020_v1/result.json
cat work/zee_postscan_original_B4_20261020_v1/original_B4_30_and_optimized_fY_22_NOT_ALLOWED.csv
```

The key output numbers are `original_B4_B2rank1_sampled_RGE_and_no_deeper_tree_witness` and `original_B4_optimized_fY_sampled_RGE_and_no_deeper_tree_witness`, which are **not equal to the earlier 22 counterfactual survivors unless independently demonstrated**. The D1-over-D2 improvement factors explicitly use the SAME joint partial LFV score.

### Scope of certification

Even if all 30 original B4 points pass these numerical diagnostic tests, the Zee parameter-space **allowed/excluded** scan remains blocked by a calibrated two-charged (B\to X_s\gamma) likelihood, full CLFV, general neutrino oscillation fits, complete HiggsTools/decays, hadronic cross sections, global vacuum proof, and proper threshold-matched quark/RGE conventions.

This is the decisive **interpretability repair** for the existing large scan, not a claim that more numerical optimization can by itself solve all missing physics.
