# Gate E4B — 2026 precision \(B\to X_s\gamma\) observable integration

## Scientific status (19 October 2026)

**NOT yet an implementation of the Misiak et al. (2026) full NNLO inclusive branching ratio.** We have a finished, source-verifying integration harness, but an independently validated 2026 observable and likelihood are still missing. The code **must not** label any Zee spectrum experimentally allowed/excluded before that prerequisite is met.

**Why this is a real dependency:** arXiv:2608.29863v1 contains:
- SM \(E_\gamma>1.6\) GeV BR \((3.54\pm0.14)\times10^{-4}\).
- experimental BR \((3.49\pm0.19)\times10^{-4}\).
- Eq. (4): \(10^4 BR = 3.54 - 8.51\,\Delta C_7(160\text{ GeV}) - 2.16\,\Delta C_8(160\text{ GeV})\), *linear in LO NP only*; the paper explicitly omits quadratic NP terms there.
- the full Type-II 2HDM 95% CL mass bound \(M_{H^\pm}>670\) GeV, from the **complete higher-order Type-II calculation**, *not* Eq. (4).

The paper is five pages and does not itself give enough machine-readable matrix-element tensors, kinetic/HQE inputs and correlated nuisance likelihood to reproduce the generic full observable. The publicly surfaced [BSGammaFourBody repository](https://github.com/LarsTMoos/BSGammaFourBody) contains **specific NLO four-/five-body integrals**, not the entire 2026 precision prediction. The existing public flavio/EOS/SuperIso programs also must NOT be presented as incorporating the 2026 exact-charm higher-order update without explicit validation.

References:
- 2026 Letter: https://arxiv.org/html/2608.29863 (Secs. II–IV, Eq. (4), Fig. 3)
- KIT preprints: TTP26-033 and related TTP26-034 exact-charm higher-order paper.
- Lars T. Moos, four-/five-body source subset: https://github.com/LarsTMoos/BSGammaFourBody
- E4A committed matched Wilson vectors: \`work/gateE4a_large_matching_typeII_27_v1/summary.json\`.

## What we implemented now

\`scripts/zee_gateE4b_2026_observable_validation.py\` is an **observable-level acceptance and Zee evaluation harness**, not a substitute for the missing NNLO engine. It refuses to run a 2026 physical prediction unless both a genuine external backend and independent **numerical** author Type-II benchmark curve are available.

It performs, in ONE run:
1. Load the actual E4A summary, SHA-lock its bytes, check 27 unique Zee spectra, 648 full three-order Wilson rows, 216 actual source calls, 5,184 coefficient entries and correct weighted NP at each original \(\gamma\).
2. Interrogate an external executable that reports supported numerical capabilities and its basis-map source. The input is JSON to stdin; output is exactly one JSON object to stdout for each request.
3. Reproduce the published full SM central BR and theory sigma at \(E_\gamma>1.6\) GeV **numerically**, not by string label.
4. Reproduce >=6 independently provided, source-referenced **Type-II 2026 NNLO numerical mass-curve holdouts**, including masses 550, 650, 670, 700 and 800 GeV. The holdouts must come from independent author-supplied raw table or verified source output, NOT fabricated via digitizing the plot or from this backend itself. Numeric agreement is required without re-tuning backend parameters to this curve.
5. Run 15 Type-II mass/CL queries around the published 670 GeV boundary at \(\tan\beta=50\), verifying a monotone 95% CL transition near that benchmark **using the actual backend confidence procedure**, not imposing a guessed generic \(\Delta\chi^2=3.84\) or a naïve central BR threshold.
6. Independently validate the **actual raw A1M source basis** before two charged scalar extrapolation. Raw SuperIso \(C_3\ldots C_6\) NNLO coefficient differences relative to published original-author conventions were found in A1Q. Passing 5,184 algebraic coefficients does not establish correct physical effective Wilson matching. The external backend must implement a source-documented mapping; for each of the 27 Zee points, \(\gamma=0,\pi/2\) must reproduce the separately computed pure Type-II observable at its physical charged mass and \(\tan\beta\) before allowing mixed-gamma predictions.
7. If all pass, calculate 27 **two-charged** rates including SM×NP, NP×NP and correlated theory uncertainty in ONE observable per spectrum. These are **not** a global Zee viability label: neutrino likelihood, complete LFV, quark FCNC, HiggsTools, vacuum and RG thresholds remain separate.

One large regression \`tests/test_zee_gateE4b_large_observable_acceptance.py\` feeds deliberately **synthetic** NNLO JSON responses through 27 Zee spectra, six independent numeric fixture Type-II points, the limit scan and negative controls: wrong SM normalization, wrong author holdout, wrong 670 CL transition, wrong A1M basis/pure-state conversion. Its success tests interface integrity **only** and must NEVER be cited as reproducing the 2026 calculation.

## Minimal external backend contract

The manifest is a UTF-8 JSON with the following schema. **These values are placeholders and MUST NOT be filled with guesses.**

\`\`\`json
{
  "protocol": "zee-bsgamma-2026-nnlo-backend-v1",
  "published_source": "arxiv:2608.29863",
  "full_2026_inclusive_observable": true,
  "supports_full_np_interference": true,
  "supports_correlated_theory_likelihood": true,
  "matching_basis_input": "A1M_SuperIso_v5_CW_calculator_raw_operators_1to8_orders_0to2",
  "implementation_source": "AUTHOR_IMPLEMENTATION_COMMIT_AND_SOURCE_DESCRIPTION",
  "validated_operator_basis_conversion_source": "SOURCE_DOCUMENT_EXPLAINING_SCHEME_AND_NNLO_OPERATOR_TRANSFORM",
  "command": ["/ABSOLUTE/PATH/TO/REAL/2026/OBSERVABLE/EXECUTABLE"]
}
\`\`\`

An independently supplied author numerical reference file:

\`\`\`json
{
  "independent_from_tested_backend": true,
  "source_reference": "arxiv:2608.29863",
  "confidence_procedure": "DOCUMENTED_EXACT_AUTHOR_CL_PROCEDURE",
  "pure_typeII_numerical_reference": [
    {"mass_GeV": 550.0, "tanbeta": 50.0, "BR": "AUTHOR_NUMERIC_VALUE"},
    {"mass_GeV": 650.0, "tanbeta": 50.0, "BR": "AUTHOR_NUMERIC_VALUE"},
    {"mass_GeV": 670.0, "tanbeta": 50.0, "BR": "AUTHOR_NUMERIC_VALUE"},
    {"mass_GeV": 700.0, "tanbeta": 50.0, "BR": "AUTHOR_NUMERIC_VALUE"},
    {"mass_GeV": 800.0, "tanbeta": 50.0, "BR": "AUTHOR_NUMERIC_VALUE"},
    {"mass_GeV": 1000.0, "tanbeta": 50.0, "BR": "AUTHOR_NUMERIC_VALUE"}
  ]
}
\`\`\`

Do not commit such a manifest declaring successful \`full_2026_inclusive_observable:true\` until there is a genuine executable. The above document is an illustrative **invalid** placeholder, not a source claim.

Backend requests and responses use the \`protocol\` and \`action\` keys, 160 GeV matching scale and 1.6 GeV photon-energy cut:

\`\`\`text
ACTION = describe
RESPONSE validated_capabilities:
   SM_2026_NNLO
   TypeII_2026_NNLO
   Zee_two_mixed_charged_from_raw_3order
   source_approved_A1M_basis_map
   correlated_95CL

ACTION = predict_sm
RESPONSE BR, sigma_theory, fully_correlated_with_SM_nuisances

ACTION = predict_typeii
REQUEST mass_GeV, tanbeta
RESPONSE BR, sigma_theory, fully_correlated_with_SM_nuisances

ACTION = typeii_excluded_95
REQUEST mass_GeV, tanbeta
RESPONSE excluded_95 (bool), confidence_procedure matching author reference

ACTION = predict_twocharged_from_raw_superiso
REQUEST mH1_GeV, mH2_GeV, tanbeta, gamma,
    matching_raw_basis, coefficient_rows list of 24 entries:
    order, operator, SM, NP_light, NP_heavy
RESPONSE BR, sigma_theory, fully_correlated_with_SM_nuisances

ALL responses MUST include:
   protocol: zee-bsgamma-2026-nnlo-backend-v1
   action: [the matching requested action]
   scientific_precision_level: FULL_2026_NNLO
\`\`\`

**Note:** An external executable calling itself \`FULL_2026_NNLO\` is not scientific proof. Real source provenance, independent numeric author curve and scheme-map audit are essential. The harness supplies fail-closed numerical checks, but cannot automatically authenticate an author's identity or independently prove the physical completeness of a black-box backend.

## AF run with currently available files

The following command is **source readiness only** and deliberately produces a blocked report, not a new physics prediction:

\`\`\`bash
cd /home/aalida/zee
git pull --ff-only
python3 -m py_compile \
    scripts/zee_gateE4b_2026_observable_validation.py \
    tests/test_zee_gateE4b_large_observable_acceptance.py
python3 -m unittest discover -s tests \
    -p 'test_zee_gateE4b_large_observable_acceptance.py' -v &&
python3 -u scripts/zee_gateE4b_2026_observable_validation.py \
    --e4a-summary work/gateE4a_large_matching_typeII_27_v1/summary.json \
    --audit-only \
    --output-dir work/gateE4b_2026_observable_SOURCE_BLOCKED_v1
\`\`\`

When and ONLY when a validated 2026 backend and reference file become available:

\`\`\`bash
python3 -u scripts/zee_gateE4b_2026_observable_validation.py \
    --e4a-summary work/gateE4a_large_matching_typeII_27_v1/summary.json \
    --backend-manifest /PATH/TO/AUTHOR_BACKEND_MANIFEST.json \
    --author-reference /PATH/TO/INDEPENDENT_AUTHOR_NUMERICAL_REFERENCE.json \
    --output-dir work/gateE4b_2026_FULL_AUTHOR_VALIDATED_v1
\`\`\`

## Practical source request to the authors (NOT sent)

> Dear Prof. Misiak and collaborators,
>
> I am studying the inclusive \(\bar B\to X_s\gamma\) constraint on a Zee-extended two-Higgs-doublet model with two charged mass eigenstates. I have source-checked the one- to three-order charged-Higgs matching contributions at \(\mu_0=160\) GeV, but would like to avoid combining an older SuperIso rate with your updated 2026 Standard Model prediction. Would it be possible to share either the numerical routine (or response coefficients) for your updated full observable as a function of \(C_{7,8}(\mu_0)\), including quadratic NP terms, higher-order NP matching conventions, and the relevant theory nuisance correlations? Separately, could you share a small machine-readable table of your full Type-II \(B\to X_s\gamma\) mass curve (for example at 550, 650, 670, 700, 800, and 1000 GeV, \(\tan\beta=50\)) and the confidence-limit prescription behind the 670 GeV bound? This would permit an independent implementation and a controlled extension to two mixed charged scalars.
>
> Thank you for considering the request.
>
> Best regards,

If no author code exists, the only honest alternative is a substantial independent calculation implementing the updated QCD matrix-element tensors, exact-charm terms, kinetic/HQE inputs, nonperturbative treatment and matching/scale correlations. It is a separate computational project. An implementation of the published generic **linearized** Eq.(4) (already E3) is not that calculation.
