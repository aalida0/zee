# E1 result interpretation and E2: complete all 395 original Zee tree-vacuum searches

## AF E1 results received (20 October 2026)

User-provided stdout from the **successful** UChicago AF E1 5,557-point full original-B4 funnel:

| Diagnostic | Cases | Meaning |
|---|---:|---|
| Original scalar/EWPO-screened distinct B4 bins | 5,557 | Adaptive B4 candidate archive, not a flat-prior scan |
| Source-pinned one-loop RGE+BFB+55-channel unitarity to chosen 10 TeV target, 24/48-step agreement | **395** | Uses one exact-central-neutrino B2 Yukawa family |
| Matching-scale 55-channel failures | 0 | No E1 matching-scale 55-channel failures in stdout; source logs show all tested reached this prefilter |
| E1 first-stage C5 charge-breaking-inclusive multistart tree-vacuum checks | 150 | Highest-cascade 150 of the 395 RGE successes |
| Explicit lower-potential witness | **44** | Tested original tree potential; not necessarily bounded/global proof |
| No deeper potential found within numeric search | **106** | Does NOT establish global vacuum stability |
| RGE successes without any C5 test | **245** | Status UNTESTED, **NOT excluded** |
| 40 mass-diverse E1 shortlist | **40** | Diversity thinning of the 106 no-witness cases; 66 other no-witness cases are NOT excluded |
| Fully experimental Zee allowed points | **unknown** | Missing complete LFV, precision B→Xsγ, HiggsTools, global vacuum, production |

RGE-screened fraction: 395/5557 ≈ **7.11%**, only descriptive for this adaptive B4 archive.
Among the *cascade-prioritized 150*, numerical no-witness fraction 106/150 ≈ **70.67%**, lower-witness fraction 44/150 ≈ **29.33%**. **Do not extrapolate** these to the other 245 without evaluation or call them experimental acceptance fractions.

Two previously identified viable *numerical* original-potential candidates, **B4_0006862 and B4_0006962**, reappear in the no-deeper-witness E1 cohort. They still lack a complete modern flavor/CLFV/Higgs likelihood.

## Why E2 is the efficient one large next task

Another 20,000-proposal B4 scan, or repeating 5,557 C4 RGE trajectories, would be wasteful. Instead, commit a second large *single* E2 calculation:

- Reuse exact source SHA hashes and all 5,557 ledger rows, 395 previous RGE passes and 150 complete C5 evaluations.
- Select precisely the **245 original B4 potential** points that passed both RGE resolutions but were **never** vacuum tested.
- Reconstruct the same *deterministic strength=0* B2 \(f,Y\) Yukawa texture for each; validate that the partial LFV value equals the original E1 per-point ledger; BEFORE the expensive run also check the stored E1 40 complex \(f,Y\) matrices and their neutrino-closure+partial-LFV scores against fresh source recomputations.
- Run exact original C5 six-real-field multistart tree potential, 128 starts (+EWSB seeds), maxiter=1,000, and the same per-candidate SHA-derived random seed as E1. A lower potential is positive evidence of an undesirable vacuum for the assumed original tree potential, while no lower value is **not** a mathematical global certificate.
- Append each result to an fsynced checkpoint file; a failed remote job can run again with \`--resume\`, after exact input SHA/source/settings checks. No existing E1/old postscan file is overwritten.
- Merge 150 old + 245 new = **395** unique vacuum outcomes, split by explicit deeper witness vs no found witness, preserve a **complete source-identical B4 CSV for *all* no-witness points** and an optional top-100 *diverse* collider shortlist. Store matched actual B2 textures for the top-100 to facilitate follow-up full LFV/Higgs computations.
- Refuse publication-ready allowed/excluded classification. The later analysis should run multi-root/NO+IO neutrino/LFV and model-complete widths and precision two-charged Higgs flavor likelihood; their absence is physics work, not scan statistics.

The 44/106 findings are *from E1's prioritized first 150*, while E2 may discover a very different distribution in the lower-cascade remaining 245. Do not predict E2 survival rate from E1's fraction without doing E2.

## AF execution: one campaign, safely resumable

This is a **new** stage; it is committed to GitHub but **not executed by GitHub**.

~~~bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source .venv-flavor-f1/bin/activate
set -o pipefail

# The regression exercises 5,557/395/150/245 source partitioning,
# checkpoint safety, numeric status semantics, and final 395-row merger.
python -m unittest discover -s tests \
  -p 'test_zee_gateE2_complete_395_original_vacua.py' -v

python -u scripts/zee_gateE2_complete_395_original_vacua.py \
  --campaign-dir work/zee_large_integrated_20261020_v1 \
  --postscan-result work/zee_postscan_original_B4_20261020_v2/result.json \
  --e1-dir work/zee_E1_all_5557_original_running_20261020_v2 \
  --output-dir work/zee_E2_complete_395_original_vacua_20261020_v1 \
  --vacuum-multistarts 128 \
  --vacuum-maxiter 1000 \
  --seed 20261020 \
  2>&1 | tee work/zee_E2_complete_395_original_vacua_20261020_v1_run.log
~~~

**Important:** If the successfully completed E1 output is under a different version, change \`--e1-dir\` to that actual folder. The first failed E1 directories are NOT acceptable, because E2 requires an E1 summary with complete 395/150 records and SHA fingerprints.

If the E2 process is interrupted, DO NOT delete its output or launch a different input campaign. Resume with exactly the same command plus \`--resume\`; source and settings checks prevent mixing unrelated results. Do not use \`--resume\` after a completed \`summary.json\`.

## E2 output contract

\`\`\`text
work/zee_E2_complete_395_original_vacua_20261020_v1/
  manifest.json                            # pinned E1 source identity, settings
  E2_missing_245_original_B4_vacuum_checkpoint.jsonl
  E2_all_395_original_B4_vacuum_evidence.jsonl
  E2_all_original_B4_no_deeper_witness_NOT_ALLOWED.csv
  E2_diverse_top100_original_B4_NOT_ALLOWED.csv
  E2_top100_one_B2_Yukawa_texture_NOT_ALLOWED.json
  summary.json
\`\`\`

Summary reports total numerical C5 witness count for the entire 395 population; no-witness count; number of mass-diverse representatives and source SHA provenance. The first 150 E1 outputs are reused but never modified.

**E2 is still theory-diagnostic, not publication-grade viability:** incomplete full Zee LFV, modern matched two-charged B→Xsγ rate and error budget, model-complete HiggsTools and total widths, hadronic production, and mathematical global-minimum proof remain unresolved. A one-loop RG trajectory to 10 TeV is a chosen perturbative-validity benchmark, not an experimentally required UV cutoff.

## Post-E2 direction

With all 395 original spectra classified by the *same* finite numeric tree-vacuum diagnostic, pick a broad set of no-witness original B4 source rows. For those, perform **multiple** exact-neutrino \(f,Y\) families including both mass orderings and realistic neutrino nuisance inputs; optimize and source-pin full model LFV; rerun RGEs with the actual optimized Yukawas; compute complete physical scalar widths, HiggsTools input and reliable production cross sections; finish NLO/NNLO B→Xsγ matched likelihood.

The constraints cannot be replaced by more proposal statistics. The key result from E2 is a complete, reproducible physics evidence pool, not a physical allowed-point count.
