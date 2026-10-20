# E7 — 309-source neutrino-closed GENERAL-ZEE charged-width reassessment and conditional Higgs Pareto frontier

**Goal:** Challenge the headline charged cascade after E6 without rerunning scalar scans or making a false heavy HiggsBounds exclusion.

## Why the E6 Pareto frontier is insufficient for a viable-cascade claim

The E6 table used:
\(\mathcal P_{\rm B4}=\sin^2\gamma\times {\rm BR}_{\rm Gate6,nonleptonic+oldTypeII\tau}(H_2\to H_1 Z)\times {\rm BR}_{\rm Gate6,nonleptonic+oldTypeII\tau}(H_1\to tb)\).

This is a *legacy partial-channel* proxy; it does **not** include the general Zee \(Y^\ell\) and \(f\) charged-lepton widths actually selected by the E3 neutrino-mass/partial-LFV scan. The previous summary identified 7 E6-original-proxy Pareto cases, notably B4_0004143, 0004380, 0002315. If the full leptonic widths are non-negligible, the Pareto ranking can change decisively. A "strong charged cascade" publication statement is premature until this is examined.

E7 reuses the **existing source independently tested Gate B3 general-Zee charged-lepton decay module**. It makes no new flavor fit and changes no original Yukawa. It computes
\[
\Gamma(H_1^+\to\ell_a^+\nu)
={m_{H_1}\over16\pi}\left[2c_\gamma^2\sum_i|Y^\ell_{ai}|^2+
4s_\gamma^2\sum_i|f_{ia}|^2\right]
\left(1-{m_{\ell_a}^2\over m_{H_1}^2}\right)^2
\]
and for \(H_2\), interchanges \(c_\gamma^2\leftrightarrow s_\gamma^2\).

Gate6's *legacy Type-II charged-lepton tau-neutrino rate is removed*, not added again. Partial bosonic and Type-II-quark rates are carried from the original Zee scalar-input widths without supplying an unearned NLO correction. The same B3 implementation reconstructs the input neutrino matrix from the **saved original E3 selected f,Y^\ell** and checks the central mass-matrix closure to \(10^{-9}\) eV.

For each of 309:
\[
{\cal P}_{\rm B3,\ included}
=\sin^2\gamma\,\frac{\Gamma_{\rm LO}(H_2\to H_1Z)}
                     {\sum_{\rm included}\Gamma_{\rm LO}(H_2)}
             \,\frac{\Gamma_{\rm LO}(H_1\to tb)}
                     {\sum_{\rm included}\Gamma_{\rm LO}(H_1)}.
\]
The numerator \(H_2\to H_1Z\) is independently reconstructed from
\(g_{ZH_2H_1}=(M_Z/v)\sin\gamma\cos\gamma\) and exact two-body kinematics. All individual included widths, totals and ratios are revalidated and saved. **These are not complete total widths and not physical branching ratios or event yields**; uncomputed channels, NLO QCD corrections, offshell modes and hadronic production remain outstanding. The revised proxy can be larger than the old legacy one in principle: removing the erroneous Type-II tau ansatz can reduce the total widths more than the new Zee lepton rates increase them; do NOT impose that E7 must be <= B4.

**The Higgs-axis \(\Delta\chi^2_{\rm E6}\) is not recomputed**, but E7 strictly checks the entire E6 output, all 309 individual IDs and row values, E6 output SHA256, E6 summary & manifest, original E6 main and mixed-PV source code SHA fingerprints, E2/E3/E4H/E5 primary source chain, and the same 159-observable HiggsSignals dataset. This verifies that newly computed general-Zee cascade rates are paired to the **same physical original B4 potential and same optimized lepton Yukawas** that fed E6.

E7 recomputes the *two-dimensional Pareto frontier* minimizing the fixed-SM-reference HiggsSignals \(\Delta\chi^2\) and maximizing the new general-Zee included-channel cascade proxy. It labels descriptive \(\mathcal P\ge0.4\) candidates **without an experimental acceptance cut**. All 309 source rows have a null full-Zee allowed flag and null HiggsBounds excluded flag.

## One command on UChicago AF

Code:
- \`scripts/zee_gateE7_309_general_lepton_width_pareto.py\`;
- \`tests/test_zee_gateE7_309_general_lepton_width_pareto.py\`;
- \`scripts/zee_gateE7_one_shot.sh\`;
- \`.github/workflows/e7-source-regressions.yml\` — upstream standalone source-level unit/syntax CI; cannot access private AF source data.

Run in \`/home\` (not \`/data\`):

\`\`\`bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
bash scripts/zee_gateE7_one_shot.sh
\`\`\`

The **one script**:
1. Confirms E2, E3, E4H, E5, E6 and HiggsSignals dataset all present, with installed HiggsTools.
2. Runs previous B3, E5, E6 unit suites **and** the new E7 source-hash, 309-size, Pareto and width-accounting unit suite. Test failures stop before producing result data.
3. Rejects any prior nonempty E7 directory: \`work/zee_E7_309_optimized_Zee_charged_widths_Pareto_20261020_v1\`.
4. Reloads and source-pins original 309 E2/E3/E4H/E5/E6 predictions.
5. Reconstructs every selected neutrino matrix and the **general Zee** lepton widths plus all Gate6 *included* bosonic/quark channels, calculates corrected included-channel cascade proxies.
6. Writes JSONL all 309 full width partials, ranked CSV, new Pareto CSV, high-cascade descriptive CSV, \`summary.json\`, \`manifest.json\`, plus source-hashed log.
7. Prints aggregate changes and **all newly Pareto-optimal** benchmark IDs, individual \(\Delta\chi^2_{\rm E6}\), corrected cascade proxy and included \(H_2\to H_1Z\), \(H_1\to tb\) fractions.

Expected output directory:
\`\`\`text
work/zee_E7_309_optimized_Zee_charged_widths_Pareto_20261020_v1/
    E7_309_general_Zee_charged_widths_NOT_ALLOWED.jsonl
    E7_309_HS_vs_lepton_corrected_cascade_NOT_ALLOWED.csv
    E7_Pareto_HS_vs_general_Zee_cascade_NOT_ALLOWED.csv
    E7_high_cascade_descriptive_NOT_ALLOWED.csv
    summary.json
    manifest.json
\`\`\`

## What E7 **cannot** claim, and why HiggsBounds is not run yet

An official HiggsBounds output based on only the h125 state or on three heavy states with default/zero production rates would be physically **misleading**. The complete Zee model has \((h_{125},H,A,H_1^\pm,H_2^\pm)\), with neutral cross sections, neutral total widths and BRs, all relevant charged production and decays, and gauge-linked exotic cascade decays. The current code has only partial charged LO widths and an effective 125GeV HiggsSignals model; HiggsBounds is not a truthful exclusion without a model-consistent full prediction object. The genuine next calculation is to build complete neutral LO widths and collider production rates cross-checked against the mapped Zee UFO/independent MadGraph, then populate all five particles in \`Higgs.predictions\` and evaluate a *real* \`Higgs.bounds.Bounds(HBDataSet)\` with provenance-pinned data. Reference: https://higgsbounds.gitlab.io/higgstools/HiggsBoundsAPI.html .

Other complete-model bottlenecks: scheme-consistent two-charged \(B\to X_s\gamma\) (existing F3/F4b/F4c source audits currently **not strict NLO exclusion**), comprehensive \(l_i\to l_j\gamma\) Barr–Zee + \(\mu e\) conversion and neutrino fits beyond one central NO dataset, genuinely global charge-breaking vacuum minimum verification, EWPO uncertainties, and all production-width higher-order issues.

**No numerical E7 AF physics result exists at implementation time; do not invent new numbers before user executes the one-shot runner.** Existing 7-case E6 frontier is only a baseline, not an E7 prediction.

## Review of initial CI test-only discrepancy

The GitHub synthetic 7-test job initially had **6/7 passes** and one assertion-only failure: the strengthened manifest SHA-source check correctly rejected tampered sources earlier than expected. The test expected error text \`source files changed\`, but runtime emitted \`E6 completion/provenance/status mismatch\`. The code correctly failed closed. Commit 3a6b64d adjusted the assertion to recognize this precise strengthened diagnostic, without relaxing any physics gate. GitHub CI and full AF integration status must be checked separately.
