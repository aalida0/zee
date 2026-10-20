# E5 completed — 309 real conditional HiggsSignals χ² and E5A driver audit

## UChicago AF results, 20 October 2026

User executed \`scripts/zee_gateE5_309_h125_higgssignals_effective.py\` successfully using locally built HiggsTools 1.3, E2/E3/E4H source spectra and full HSDataSet. Parsed all 309 stdout entries:

- \`E5_STATUS E5_309_HIGGSSIGNALS_EFFECTIVE_125_ONLY_APPROX_NOT_ALLOWED\`;
- \`E5_SM_HIGGSSIGNALS_CHI2 153.71818977959504 N_OBSERVABLES 159\`;
- 309 distinct source original B4 scalar/Yukawa configurations evaluated;
- \(\Delta\chi^2=\chi^2_{\rm 125\ eff}-\chi^2_{\rm SM}\) from SAME 159-observable dataset:
  - minimum 0.07766062152816744, median **112.9894424884094**, mean **259.14069303750836**, maximum **1089.0452164319008**;
  - descriptive thresholds \(\Delta\chi^2\le 1\): 16; \(\le 4\): 29; \(\le 10\): 50; \(>100\): **155**. **No threshold is a confidence-level exclusion**.
  - best E5 record \`B4_0011305\`, \(\chi^2=153.7958504011232\), \(\Delta\chi^2=0.07766062\);
  - other near-SM source IDs \`B4_0011188\` (0.07888508), \`B4_0011208\` (0.07911125), \`B4_0005263\` (0.12828149), \`B4_0011609\` (0.36885784), \`B4_0003873\` (0.52257240);
  - original two charged-cascade priorities \`B4_0006862\`: **23.106815667928032**, \`B4_0006962\`: **126.90211129524931**;
  - worst \`B4_0016199\` 1089.04521643, \`B4_0016080\` 1086.04600308.

This is the first significant Higgs signal-strength discrimination of the E2/E3 309 source population; previous all-309 LFV ratios and sampled RGE status did not constrain \(\kappa_b\) / total widths. **But** it is a conditional **125-only effective-coupling** calculation; full charged Zee scalar contributions to \(\gamma\gamma,Z\gamma\), heavy scalar signal rates and HiggsBounds remain absent. Do not claim 155 experimentally excluded or 29 physically allowed points. Even a large \(\Delta\chi^2\) relative to the *fixed SM*, without validated full-model predictions and statistical nuisance profiling, does not define an automatic 95% CL acceptance threshold.

## Why E5A, before altering the scan or LFV optimizer

The E4H-derived user alignment audit found:
- \(|\beta-\alpha|\) 0.00201/0.04826/0.16922 rad min/median/max;
- \(\kappa_V\) 0.9857/0.9988/0.999998;
- \(\kappa_b\) 0.0176/0.7181/1.0419;
- **258/309** \(|\kappa_b-1|>0.1\).

High-\(\tan\beta\) misalignment can suppress \(\kappa_b\) even if \(\kappa_V\simeq1\); its effect on \(hbb\) partial width and **all** signal strengths through the total width is likely important. But *we must measure, not presume* this dominates the actual correlated HiggsSignals chi2. General charged-lepton \(Y^\ell\) can also strongly alter \(\kappa_\tau,\kappa_\mu\), and top coupling and gauge couplings play roles.

\`scripts/zee_gateE5a_309_higgssignals_drivers.py\` performs one **309-point E5 chi2 source-closure plus counterfactual HiggsSignals sensitivity campaign**. No E2/E3/E4H/E5 source file is modified.

- Check actual E5 summary, 309-row source evidence SHA, HSDataSet all-file SHA manifest, E5 saved code SHA, HiggsTools compiled module locations, E2/E3/E4H original potential and Yukawa hashes.
- **Reproduce the original E5 \(\chi^2\) for every one of 309 cases** within \(5\times10^{-6}\), and reproduce all saved total widths, before any counterfactual evaluations. Fail closed if HSDataSet/library/source drift.
- Restore **one** of these coupling groups to SM=1 while retaining *all other original optimized model inputs*: \((bb,ss,dd)\); \((tt,cc,uu)\); \((ee,\mu\mu,\tau\tau)\); \((WW,ZZ)\). Each restoration is explicitly **NOT an original physical Zee scalar potential/Yukawa model**. The difference in chi2 is a sensitivity diagnostic. Negative \(\Delta\chi^2_{\rm reset}=\chi^2_{\rm reset}-\chi^2_{\rm full}<0\) means the SM coupling replacement improves the fit under the stated approximation, not an allowed alternative Zee point.
- For six BEST and six WORST cases and B4_0006862/B4_0006962, compute **per-analysis correlated chi2** with the actual documented \`signals.measurements()\` \`Measurement(pred)\` API and dataset references. This accounts for correlations **within each experimental analysis**. Do NOT use \`chisqContributions()\` to summarize global chi2: it ignores correlations between submeasurements. Do not assume the sum of per-analysis deltas equals the global HiggsSignals delta if any cross-analysis correlations exist.
- Save source-pinned checkpoint after every case, ranked CSV with reconstructed \(\kappa\), original \(\Delta\chi^2\), and each diagnostic reset shift; final \`summary.json\` includes descriptive fractions and approximate correlation of \(\lvert\kappa_b-1\rvert\) with E5 delta chi2. No CL cut or experimental exclusion.

Official API: https://higgsbounds.gitlab.io/higgstools/HiggsSignalsAPI.html (Measurement.__call__, measurements(), reference(), loadedFrom(), id(), chisqContributions ignores correlations).

## AF commands, same validated venv + HiggsTools + HSDataSet

\`\`\`bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source .venv-flavor-f1/bin/activate
set -o pipefail

python -m py_compile \
  scripts/zee_gateE5a_309_higgssignals_drivers.py \
  tests/test_zee_gateE5a_309_higgssignals_drivers.py

python -m unittest discover -s tests \
  -p 'test_zee_gateE5a_309_higgssignals_drivers.py' -v

python -u scripts/zee_gateE5a_309_higgssignals_drivers.py \
  --e2-dir work/zee_E2_complete_395_original_vacua_20261020_v1 \
  --e3-dir work/zee_E3_309_multiroot_flavor_optimized_20261020_v1 \
  --e4h-dir work/zee_E4h_309_direct_h125_20261020_v1 \
  --e5-dir work/zee_E5_309_h125_HiggsSignals_effective_v1 \
  --hs-dataset /home/aalida/tools/hsdataset \
  --output-dir work/zee_E5a_309_HiggsSignals_drivers_v1 \
  2>&1 | tee work/zee_E5a_309_HiggsSignals_drivers_v1_run.log
\`\`\`

Use \`--resume\` only if interrupted and all source inputs remain byte-identical. No need to rerun E5. Note that this is heavier than simply reading its CSV because it performs four additional actual HiggsSignals evaluations per point.

Expected outputs:

\`\`\`text
work/zee_E5a_309_HiggsSignals_drivers_v1/
  manifest.json
  E5A_309_checkpoint.jsonl
  E5A_309_HS_sector_sensitivity_NOT_ALLOWED.jsonl
  E5A_309_ranked_drivers_NOT_ALLOWED.csv
  E5A_selected_measurement_drivers_NOT_GLOBAL_CL.json
  summary.json
\`\`\`

Status: committed; AF tests and numeric E5A rerun NOT yet performed.

## Decision after E5A

If the bottom reset significantly lowers chi2 across the high-penalty models and this remains true with the correct 125-GeV charged-scalar loop contributions, prioritize a **joint HiggsSignals-aware original-scalar scan** emphasizing alignment and cascade. Crucially, suppressing \(\kappa_b\) shifts all Higgs branching ratios via \(\Gamma_h\); an optimization of \(|\beta-\alpha|\) alone may sacrifice cascades unnecessarily. The physical constraint is the correlated signal-strength likelihood.

If the diagonally general lepton Yukawas instead dominate, target Higgs plus LFV **joint neutrino-exact Yukawa** minimization for the same original potential, then rerun full 10 TeV BFB/unitarity, E4H and h125 \(\chi^2\) with the newly selected matrices. The original E2 "no deeper tree witness" status remains only a finite numerical diagnostic.

**Publication blockers persist:** charged-scalar hγγ/hZγ loop amplitudes from independently derived trilinears, heavy-state HiggsBounds, complete LFV/oscillation likelihood with IO+nuisances, scheme-consistent precision \(B\to X_s\gamma\), global vacuum proof, validated full decay widths and production. A limited h125 effective model with a good \(\Delta\chi^2\) is not a fully allowed Zee point.
