# E3 completed (309/309) and E4H direct h(125) LFV extension

## Verified user AF result — 20 October 2026

Original uploaded UChicago AF \`E3\` stdout: one line for each 309 spectra, all reported \`MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED\`, \`ORIGINAL_OPTIMIZED_RGE_10TEV True\`, end status \`E3_309_ORIGINAL_MULTIROOT_D1_D2_D4_OPTIMIZED_RGE_PARTIAL_NOT_ALLOWED\`.

Independently parsed all 309 numerical W-photon extended partial LFV scores:

| Statistic | Score |
|---|---:|
| Minimum | 1.6836847469e-6 |
| Median | 2.3975174779e-3 |
| Maximum | 0.7236445557 |
| <0.001 | 118/309 |
| <0.01 | 220/309 |
| <0.1 | 294/309 |
| <1 | 309/309 |
| Optimized original f,Y source model, 24/48-step sampled BFB & 55-channel running to chosen 10 TeV | 309/309 |

Former B4 anchors: \`B4_0006862\` partial score 5.3612490555e-4; \`B4_0006962\` partial score 7.2229744861e-3; both optimized-source RGE \`True\`.

**Interpretation:** The selected neutrino-compatible solutions are numerically compatible with the IMPLEMENTED one-loop + fermion-photon + W-photon Barr-Zee *subset* score and a chosen original scalar running criterion. This DOES NOT imply all 309 pass LFV; no full two-loop, mu-e conversion, loop/box \`ell->3ell\`, Higgs direct search, HiggsTools, modern quark flavor, full widths or global vacuum proof is present in E3.

The 309 points are selection-biased by B4, exact-central NO neutrino input, only top five B2 roots and two D2 local starts; \`309/309\` is not a physical parameter-space survival fraction.

## Why E4H is the highest-value next calculation

The E3 optimized \`f,Y\` solutions were optimized using **low-energy LFV**; off-diagonal physical **125 GeV Higgs** couplings were *not* included. The pre-existing source-checked \`zee_gateD5_h125_direct_LFV_27.py\` derives exact tree partial widths for:

\`h->e mu\`, \`h->e tau\`, \`h->mu tau\` (both charge-conjugate states and exact lepton masses).

Therefore a low-energy LFV partial score of \`0.001\` could coexist with a direct Higgs decay far beyond published limits. Before attempting another neutrino/flavor optimizer, quantify this potential clash on **all 309 source E3 optimized Yukawa solutions**.

### External experimental source references, observed 95% CL

No interpretation is made as a full likelihood/CL recast. The published branching-ratio comparisons depend on production and acceptance assumptions, and cannot be combined as independent simple 95% thresholds.

- **CMS HIG-22-002 (2023)**: \`BR(h->e mu) < 4.4e-5\`. Source https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-22-002/index.html
- **ATLAS JHEP 07 (2023) 166**: \`BR(h->e tau) < 0.0020\`; comparison \`BR(h->mu tau) < 0.0018\`. Source https://doi.org/10.1007/JHEP07(2023)166
- **CMS HIG-20-009 (2021)**: \`BR(h->mu tau) < 0.0015\` and comparison \`BR(h->e tau) < 0.0022\`. Source https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-20-009/index.html

Current E4H reference thresholds: CMS eμ \`4.4e-5\`; ATLAS eτ \`0.0020\`; CMS μτ \`0.0015\`. Alternate collaboration limits are recorded but not statistically combined. Reference thresholds are used only to flag **tension under SM-like production and partial-width assumptions**, not claim exclusions.

### Physics and calculation

For \(\mathcal L\supset-h\,\bar\ell_i(C_{ij}P_L+C_{ji}^*P_R)\ell_j\), the source D5 exact two-charge partial width is

\[
\Gamma_{ij}={\sqrt{\lambda(m_h^2,m_i^2,m_j^2)}\over8\pi m_h^3}
\left[(|C_{ij}|^2+|C_{ji}|^2)(m_h^2-m_i^2-m_j^2)
-4m_i m_j\,\mathrm{Re}(C_{ij}C_{ji})\right].
\]

The existing \`h125_widths\` routine uses exact complex Zee neutral physical Yukawa couplings and measures the SM reference width plus the *difference in diagonal lepton partial widths* and the new LFV partial widths. All nonleptonic widths remain SM-like. It records \(\kappa_V,\kappa_t,\kappa_b\) (Type-II-like quark ansatz) to expose possible production/decay deviations.

**Crucial**: Higgs searches bound \(\sigma(pp\to h)\times {\rm BR}(h\to\ell_i\ell_j)\) in analysis categories with acceptances. Using a published 95% BR limit as if \(\sigma=\sigma_{\rm SM}\) for arbitrary \(\kappa_{V,t,b}\), altered \(h\to gg/\gamma\gamma\), or extra Higgs decays is not valid model-wide exclusion. This gate reports the source physical partial widths and reference ratios, and sets all physical allowed/excluded fields to \`null\`.

## One AF run (full 309-source E4H)

Committed:
- \`scripts/zee_gateE4h_309_direct_h125_lfv_screen.py\`
- \`tests/test_zee_gateE4h_309_direct_h125_lfv_screen.py\`

\`\`\`bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source .venv-flavor-f1/bin/activate
set -o pipefail

python -m unittest discover -s tests \
  -p 'test_zee_gateE4h_309_direct_h125_lfv_screen.py' -v

python -u scripts/zee_gateE4h_309_direct_h125_lfv_screen.py \
  --e2-dir work/zee_E2_complete_395_original_vacua_20261020_v1 \
  --e3-dir work/zee_E3_309_multiroot_flavor_optimized_20261020_v1 \
  --output-dir work/zee_E4h_309_direct_h125_20261020_v1 \
  2>&1 | tee work/zee_E4h_309_direct_h125_20261020_v1_run.log
\`\`\`

\`--resume\` is available with the same existing output directory, and the source hashes + script SHA must agree. If the E2/E3 dirs differ on AF, adjust only to the actual successful completed results, not a failed prior output.

On completion:

\`\`\`text
work/zee_E4h_309_direct_h125_20261020_v1/
  summary.json
  E4H_309_checkpoint.jsonl
  E4H_309_complete_h125_direct_LFV_NOT_ALLOWED.jsonl
  E4H_309_ranked_direct_h125_LFV_NOT_ALLOWED.csv
  manifest.json
\`\`\`

The headline result is the count \`direct_Higgs_reference_tensions_NOT_physical_excluded\`, not how many \`full_Zee_allowed\`.

## What E4H changes strategically

1. If many of the 309 candidates exceed the direct 125 GeV LFV reference screens, **the E3 Yukawa optimizer's target is insufficient**. Its objective must include direct-Higgs partial rates and eventually real \(\sigma\times{\rm BR}\), not more local minimizations of the old D4 score.
2. If almost all satisfy the reference screens, h125 direct LFV may not be the dominant issue **for these specific optimized Yukawas**. Proceed to full CLFV amplitudes, \(B\to X_s\gamma\), HiggsTools and the gauge-complete scalar decay/production backend.
3. The next paper cannot claim an allowed-Zee envelope until all remaining exclusions are independently computed and scheme/uncertainty-consistent.

**Status:** Implementation committed; numerical E4H AF campaign and regression tests not yet executed. No physics survivor-count prediction is made before those results.
