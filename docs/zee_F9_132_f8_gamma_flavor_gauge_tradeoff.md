# F9 — Interpret the complete F8 flavor/gauge mixing counterfactuals without fake exclusions

## Grounded finished F8 AF results (2026-10-20)

The user executed F8, with **309/309 original Zee models and 132 fixed-mass gamma evaluations**. The archived old-vendor SuperIso rate was compared to a **same-vendor** pure Type-II charged Higgs at mass 670 GeV and exactly the original model's tanβ. F8 closed historical F6 source results and mixing endpoints. The robust *within-legacy-kernel* statement is:

\[
R_{670}^{\mathrm{legacy}}=
\frac{\mathcal B_{\mathrm{Zee,legacy}}-\mathcal B_{\mathrm{SM,legacy}}}
{\mathcal B_{\mathrm{TypeII,670,legacy}}-\mathcal B_{\mathrm{SM,legacy}}}.
\]

The 309 ratios: **min 0.9811634, median 1.3446051, max 1.9732448**, 307/309 strictly **>1** and two <1. The two exceptions are **B4_0011208** R=0.9811634 and **B4_0011188** R=0.9885117. The primary \`B4_0004143\` was R=1.172658, conditional E6 HiggsSignals Δχ²=0.770875, E7 included-channel cascade proxy=0.591985. Six original E7 Pareto source diagnostics:

| B4 candidate | E6 Δχ² (not CL) | E7 cascade included-channel proxy (not σBR) | F8 same-legacy R670 |
|---|---:|---:|---:|
| 0004143 | 0.770875 | 0.591985 | 1.172658 |
| 0003582 | 0.296666 | 0.530008 | 1.308303 |
| 0003854 | 0.286807 | 0.522630 | 1.308309 |
| 0004380 | 12.311260 | 0.604982 | 1.372056 |
| 0002315 | 15.338535 | 0.621959 | 1.437373 |
| 0017640 | -0.904071 | 0.366096 | 1.435025 |

**No Type-II 670GeV 95% CL limit has been applied to Zee**. That published value comes from the more recent 2026 Type-II precision calculation, which uses a different higher-order input/matching/error model. The F8 comparison is *not* a surrogate for the 2026 full inclusive Zee-model likelihood. **No Zee source model is validated allowed/excluded.**

The F8 source log's last lines do NOT print the **individual 132 gamma scans**, only \`GAMMA_COUNTERFACTUALS 132\`. Therefore conclusions about gamma deformations below R=1 while retaining a nonzero cascade gauge coupling cannot be made from the pasted log alone; the F9 code MUST actually read the prior saved F8 counterfactual CSV.

## F9 source-locked task

F9 reads only completed F8 archive:

\`\`\`text
work/zee_F8_309_670TypeII_same_kernel_mixing_20261020_v1/
   summary.json
   manifest.json
   F8_309_Zee_legacy_vs_670TypeII_NOT_EXCLUSION.jsonl
   F8_309_legacy_typeII_670_same_kernel_DIAGNOSTIC.csv
   F8_six_fixed_mass_gamma_counterfactual_NOT_MODEL_POINTS.csv
\`\`\`

It requires exact saved SHA256 for all three F8 output datasets, exact F8 driver SHA fingerprint and summary/manifest agreement; checks complete 309 distinct original models and full 132 counterfactual rows; validates each original model's old-vendor SM and Type-II mass-670 comparator, reconstructed R, original gamma gauge rotation, and source evidence; verifies **6×(21 equally spaced gamma-grid points + original gamma)**, including endpoints and exactly one original per benchmark, with original full SuperIso BR reproduced at the exact original gamma. It rejects any false allowed/excluded labels, missing/unphysical output, wrong Yukawa/mass/tanβ original link or source inconsistency.

For **each six Pareto source benchmarks** compute the 22 counterfactual responses:

- Same-vendor old inclusive flavor comparator \(R_{670}^{\rm legacy}(\gamma)=(\mathrm{BR}_{\rm old}(\gamma)-\mathrm{BR}_{\rm old,SM})/(\mathrm{BR}_{\rm old,TypeII670}-\mathrm{BR}_{\rm old,SM})\).
- \(G(\gamma)=\sin^2(2\gamma)\), *normalized charged off-diagonal Z gauge coupling squared*, not full width/BR.
- \(P(\gamma)=\sin^2(\gamma)\sin^2(2\gamma)\), *purely geometric production-doublet-times-Z-gauge factor*, **not** hadronic production, cross section, width or complete charged cascade rate. Its analytic absolute maximum \(P_{\rm max}=16/27\) at \(\sin^2\gamma=2/3\). Using \(P\) for full production is not justified without the charged-Higgs collider production process and Yukawa structure.
- Relative gauge \(G(\gamma)/G(\gamma_\mathrm{original})\) and relative geometric \(P(\gamma)/P(\gamma_\mathrm{original})\). These are exact **ratios of geometry only** and do not contain the E7 general Zee widths for hypothetical gamma variations.

For each original candidate: independent Pareto frontier minimizing \(R_{670}^{\rm legacy}\) and maximizing retained squared gauge \(G/G_0\); best flavor response with *no geometric requirement*, and with **at least 50%, 80% and 95%** of the original \(G\) and separately \(P\). Count how many six source families have any gamma with \(R<1\) and geometry retention above these illustrative percentages.

Only the **exact original gamma** represents a previously computed scalar spectrum + E3 neutrino/Yukawa solution. The other 21 deformations hold masses and tanβ fixed, do not reconstruct a valid scalar potential, neutrino \(f,Y^\ell\), \(\mu_4\), RGE/BFB, vacuum, any LFV or corrected charged widths. Hence they are only **counterfactual source probes**: even \(R<1\) in a scan cannot be labeled viable/allowed, and the threshold R=1 is not a 2026 95% CL cut. The post-F9 decision is where to conduct a **NEW physically constrained scalar + flavor optimization**.

F9 also names the two untouched source exceptions B4_0011208/0011188 and saves their original E6 fit and E7 included-cascade proxy, allowing a fair tradeoff check before abandoning the population.

## ONE UChicago AF command

\`\`\`bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
bash scripts/zee_gateF9_one_shot.sh
\`\`\`

This validates existing F8 regression tests plus eight new F9 synthetic full-archive/metadata/geometry/no-exclusion regressions. It then **reads** source-pinned 309+132 F8 results and writes a NEW, nonoverwriting report. **No SuperIso vendor re-execution or expensive new physics scan is required.**

Outputs under \`work/zee_F9_132_original_F8_gamma_geometry_tradeoff_20261020_v1/\`:

- \`F9_132_gamma_legacy_flavor_gauge_geometry_NOT_PHYSICAL.csv\`
- \`F9_six_gamma_Pareto_geometries_NOT_PHYSICAL.csv\`
- \`F9_six_priority_gamma_tradeoff_NOT_ALLOWED.json\`
- \`summary.json\` and \`manifest.json\` with exact source SHA provenance.

The final stdout identifies the only two original R<1 spectra with E6/E7 axes, lists the six gamma tradeoffs and counts how many could *hypothetically* reduce the legacy rate below its old Type-II reference at 50/80/95% of the original gauge or geometric \(P\).

**F9 synthetic CI alone does not reproduce the private AF vendor/source outputs.** Only the user's AF execution will report actual gamma tradeoff values. Do not invent F9 numerical conclusions.

## Critical review limitations

The 2026 Type-II 670 GeV limit is based on a modern model-specific inclusive \(B\to X_s\gamma\) prediction; our F8/F9 are same-kernel *legacy comparative diagnostics*, NOT a replacement for up-to-date Zee \(B\to X_s\gamma\) higher-order matching and correlated nuisance likelihood. The full paper still needs actual five-state HiggsBounds, production and complete decay widths, neutrino/LFV including Barr–Zee and mu-e conversion, and a global vacuum proof. Even a favorable fixed-mass gamma slice cannot directly become an allowed Zee-model point.

**Scientific recommendation:** Only begin a NEW scalar-potential and optimized neutrino/LFV scan after seeing F9's signed flavor–gauge geometry tradeoff; don't assume that dialing gamma alone rescues the benchmark, and don't repackage the legacy comparison as an exclusion contour.
