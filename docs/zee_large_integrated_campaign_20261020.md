# One large Zee experiment: 20,000 proposals → matched 30-spectrum full diagnostic campaign

**Status:** Implemented as one AF invocation; **NOT executed by this GitHub edit**. All physics outputs are marked **NOT_ALLOWED** or **UNKNOWN**, not publication-ready model exclusions.

## Goal

Stop proliferating small gate-specific pilots. Run one substantial, provenance-locked integrated *exploratory* scan. Discover **fresh** scalar/EWPO-screened spectra with B4, choose 30 diverse spectra that also admit the **two existing C2/C3/C4/C5 counterfactual scalar-potential configurations** at tree level, and evaluate the widest available model diagnostics across a common candidate/Yukawa cohort.

This is a **biased constrained candidate-discovery exercise**, not a uniform parameter scan, Bayesian posterior, physically allowed-volume estimate, statistical significance calculation, or claim that all required physical constraints are complete. C2 potential variants are **counterfactual** at fixed masses; they must not be conflated with the original B4 model point. Surviving the numerical charge-breaking search does not prove a global minimum.

## One AF command

At UChicago AF, use the existing tested source checkout, the Q4v13 **676/676** source-validated PyR@TE one-loop RGE generator output, B1 theory/EWPO seeds, isolated A1M SuperIso, and A1U legacy reference. No code executes on \`/data\`.

~~~bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only

# Activate the AF Python environment providing numpy, scipy, and
# the existing project's vendor dependencies.
source .venv-flavor-f1/bin/activate

# One command: includes the upstream regression suite and all physics stages.
python -u scripts/zee_large_integrated_campaign.py \
  --output-dir work/zee_large_integrated_20261020_v1 \
  2>&1 | tee work/zee_large_integrated_20261020_v1_run.log
~~~

**Do not run multiple pilot commands and do not manually launch F4c again.** This is one integrated test. If \`.venv-flavor-f1\` lacks scientific dependencies provided by Key4hep, establish the existing documented AF environment prior to this launch; do not silently replace PyR@TE sources or scientific inputs.

The runner uses these existing AF paths by default:

- B1 seeds: \`work/gateB1_zee_seed_scan/all_screened_candidates_NOT_ALLOWED.csv\`
- Pinned generator: \`work/zee_section8_Q4_pyrate_v4/generator_output\`
- Validated full complex Q4v13: \`work/zee_section8_Q4_pyrate_v4/large_integrated_v1.json\`
- Pipeline settings: \`configs/zee_pipeline_partial.json\`
- A1M source provenance and A1U legacy reference: paths already saved in the above JSON.

Override any default only if its original AF file was relocated, using \`--seed-csv\`, \`--generator-output\`, \`--q4v13-report\`, \`--settings\`.

The command launches, checks and joins:

| Internal stage | Configuration | Intended evidence |
|---|---|---|
| Regression preflight | B4/B2/B3/B4C/pipeline/C1–C5/D1/D2 | Detect existing implementation regressions before doing physics work |
| B4 adaptive | 20,000 proposals, 16 chains, 96 STU quadrature nodes | Theory/EWPO candidate discovery, not physical acceptance fraction |
| Tree-variant audit | all B4 coarse-binned survivors | Select 30 source-reconstructed spectra compatible with both chosen counterfactual potential definitions; **biased selection** |
| Existing \`zee_pipeline.py\` | 300 B2 neutrino trials per spectrum, top 5 saved roots | 9,000 algebraic trials; B3 widths (150 paired roots), partial B5 LFV; preliminary fermion Barr–Zee subset; source-pinned A1V legacy quark flavor (30); B4C strict join |
| C1 | 30 spectra × 3 roots | 90 matched-source one-loop UV trajectories and RK4 refinement |
| C2 | 30 spectra × 8 potential variants | 240 source-RGE paired-variation trajectories |
| C3 | 30 × 2 variants, 2,048 sampled field orbits | 60 full-complex running-quartic sufficient-BFB diagnostics |
| C4 | 30 × 2 variants, 55 channels | 60 running complex scalar tree-unitarity checks, refined RK4 |
| C5 | 30 × 2, 128 multistarts per potential, max 1,000 iterations | 60 6-real-orbit, charge-breaking-inclusive *numerical* tree-vacuum searches; negative witness is decisive, no witness is not a global proof |
| D1 | 30 spectra × 5 saved B2 f/Y pairs | 150 joint *partial* LFV diagnostic scores and theory-case associations |
| D2 | up to 30 theory-diagnostic surviving spectra × 2 optimization roots | Exact-neutrino-closure partial LFV optimization; candidate count not hard-coded to historical 27 |

**One invocation, one independent result directory, one complete manifest.** This deliberately does not expand B2 to both mass orderings or add a full neutrino likelihood: those are unimplemented physical calculations, not settings that more CPU would fix.

## Two necessary source fixes incorporated

1. \`zee_gateC2_paired_uv_rescue.py\` previously required all historical C1 rank1 pilot trajectories to hit a 4π coupling boundary below 10 TeV. For a **new scan**, reaching the target scale without a crossing is a legitimate numerically converged outcome. C2 now checks a *source-matched C1 boundary and driver* **or** a *source-matched endpoint status*; any inconsistent outcome still fails closed. Its regression tests include both branches.
2. \`zee_gateD2_neutrino_exact_partial_LFV_optimization.py\` previously demanded exactly the historical 27 C4/C5 diagnostic survivors. It now accepts any **nonempty** dynamically selected cohort up to 30, without weakening the 150-root provenance checks, and never reclassifies the points as physically allowed.

The C1→C2 provenance contract still expects exactly 90 C1 source trajectories (30 spectra × three neutrino roots), and D2 still expects exactly 150 saved D1 flavor configurations (30 × five roots). These counts are **software input-integrity checks, not physical survivor-count requirements**.

## Output inspection

On completion, the runner writes:

~~~text
work/zee_large_integrated_20261020_v1/
  manifest.json
  campaign_result.json
  B4_diverse_tree_consistent_30_NOT_ALLOWED.csv
  joined_30_scalar_campaign_prioritization_NOT_ALLOWED.csv
  joint_60_scalar_running_vacuum_variants_NOT_ALLOWED.csv
  source_regressions.log
  B4_adaptive/summary.json
  partial_constraint_pipeline/manifest.json
  partial_constraint_pipeline/B4C_joint_audit/...
  C1_model_RGE/summary.json
  C2_paired_UV/summary.json
  C3_complex_BFB/summary.json
  C4_55channel_unitarity/summary.json
  C5_charge_breaking_vacuum/summary.json
  D1_joint_partial_LFV/summary.json
  D2_neutrino_partial_LFV_optimization/summary.json
  [one log per internal stage]
~~~

At the end of the single run, the only outputs needed for initial scientific interpretation are:

~~~bash
cat work/zee_large_integrated_20261020_v1/campaign_result.json
cat work/zee_large_integrated_20261020_v1/manifest.json
head -n 12 work/zee_large_integrated_20261020_v1/joined_30_scalar_campaign_prioritization_NOT_ALLOWED.csv
~~~

The runner prints:

~~~text
ZEE_LARGE_CAMPAIGN_STATUS LARGE_ZEE_EVIDENCE_CAMPAIGN_COMPLETED_NO_ALLOWED_POINT_CLASSIFICATION
ZEE_DIAGNOSTIC_CANDIDATES <N> OF 30
ZEE_FULL_ALLOWED_POINTS UNKNOWN
~~~

\`ZEE_DIAGNOSTIC_CANDIDATES\` means there is at least one paired source-tested potential that passed the **sampled** running BFB/unitarity screens *and* has no explicit deeper tree-vacuum witness, **not** that the original Zee model point is globally stable or flavor/Higgs-experiment allowed.

## Fail closed and source integrity

- Prior to computing any physics, ensure the exact 676/676 Q4v13 report SHA matches the existing immutable generated \`RGEs.py\`.
- Verify B1 input and isolated A1M/A1U files; run selected existing module regression tests.
- Reject a missing/duplicate B4 selected ID, missing B2 root, missing B3/A1V/B4C stage, mismatched C1→C5 input SHA, incomplete C1 90/C2 240/C3–C5 60/D1 150 diagnostic cohorts.
- Record the repository HEAD, exact source/manifest hashes and each subprocess command/exit code plus stage result SHA in \`manifest.json\`.
- Write all artifacts under the project \`/home\` tree; no code is executed on \`/data\`. Refuse nonempty output directory to protect previous results.
- Any failed scientific runner (including prior unmodified C3/C4/C5 constraints) aborts the campaign with the specific traceback and stage log; **never count a partial campaign as completed**. Do not silently disable difficult physics checks to force a pass.

## What one large run CAN and CANNOT solve

This integrated campaign produces a much stronger common-spectrum physics inventory than repeated eight-benchmark or 27-point F4 scans: the same scalar masses, quark flavor, lepton Yukawa choices, running complex scalar stability/unitarity and charge-breaking witnesses are tracked across all stages.

It **cannot** solve still-unimplemented physics simply by increasing MC statistics or running 20,000 proposals. Specifically:

1. Exact full neutrino oscillation likelihood and both NO/IO with phases are not yet implemented.
2. Complete LFV including all two-loop Barr–Zee/W/Z/charged-scalar diagrams, conversion, box contributions and independent external limits remains unvalidated.
3. Zee HiggsTools predictions require **complete** h/H/A/H1/H2 widths/couplings/cross sections, not B4/B3 partial-channel fractions.
4. A consistent two-charged-scalar precision \(B\to X_s\gamma\) likelihood requires the missing full inclusive amplitude/rate/scheme check; F4c's quadratic EOS diagnostic and A1V legacy output are not exclusions.
5. A finite, bounded charge-breaking search does not prove global vacuum stability; running-to-10-TeV in the one-loop generator is not threshold-complete UV consistency.
6. Cross sections \(\sigma(pp\to tbH_2)\) and a complete decay inventory are not computed.

**Publication-ready allowed/excluded points: UNKNOWN.** Large-campaign diagnostic survivors are prioritized for the independent missing full constraints, not substituted for them. The single test is a substantive large-sample exploration, not a promise that 20,000 proposals can replace theoretical calculations.
