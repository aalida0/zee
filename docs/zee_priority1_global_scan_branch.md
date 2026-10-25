# Priority-1 global Zee scan branch — truthful implementation ledger

**Branch:** \`feature/global-scan-priority1\` from original
\`gateA1p-independent-hepfit-typeii-matching\`. This is deliberately a
small new software layer, NOT a replacement for E2–F9 physics computations.

## What is actually implemented in this branch

| Requested module | Code | Physics status |
|---|---|---|
| Neutrino + both orderings | \`validate_neutrino()\` enforces exact mass closure and provenance-linked NO/IO fit input | **Full global oscillation likelihood NOT written here.** E3 implements exact central mass matrix and partial LFV but not full oscillation likelihood. |
| Complete LFV | \`validate_lfv()\` requires coherent one+two-loop results, conversion overlap, complete channels and per-channel limits | **Missing full amplitudes, interference and independent benchmarks.** Existing D1/D2/D4, B5, E4h remain partial. |
| Modern two-charged B→Xsγ | \`validate_bsgamma()\` checks 1.6 GeV cut, complete matched inclusive BSM rate, same-scheme SM/TypeII controls, calibrated BSM errors and provenance | **Modern full matching/NNLO BSM rate NOT implemented.** Historical SuperIso full legacy F6 and F7/F8 diagnostics cannot be used as modern exclusions. |
| Five-state widths | \`validate_decays()\` enforces h,H,A,H1,H2 masses, complete-channel declaration, off-shell/QCD validation and sum(partials)=total | **Model-specific full neutral+charged widths not implemented.** E7 corrects included charged leptonic widths only. |
| Hadronic production | \`validate_production()\` checks full scalar coverage, positive pb inputs, collider energy, uncertainty and independent generator provenance | **Zee hadronic cross sections not yet generated/validated.** Never substitute sin²γ for pb. |
| HiggsTools | **Actual Python API adapter implemented:** builds Higgs.tools.Input.predictionsFromDict with five scalar masses, total widths, explicit BR and hadronic rates; calls Higgs.bounds.Bounds and Higgs.signals.Signals | Runs only if genuinely complete five-state widths, production and compatible mode maps are supplied; no artificial zero-rate heavy states. |
| Top-level join | \`scripts/zee_priority1_cli.py\` | Source SHA manifest and blocked-reason JSONL, not a physical allowed-space scan. |

All outputs hardcode \`full_Zee_allowed_or_excluded: null\`. This is
intentional: the physics inputs do NOT exist yet. A green unit test shows
that code/contract logic works, **not** that NNLO flavor or full Zee rates
are independently validated.

### Why this is not falsely advertised as "Priority 1 complete"

Implementing two-charged modern NNLO \(B\to X_s\gamma\) in the matched
2026 scheme, missing Zee LFV two-loop amplitudes/interference, accurate
off-shell neutral+charged widths, and hadron production predictions
requires dedicated scientific implementation and independent physical
controls. No short Python wrapper can reproduce these calculations.
Passing text booleans like \`scheme_matched_two_charged_inclusive_rate=true\`
does not independently certify such a backend: the source provenance,
reference validation, physical implementation and uncertainties must
be audited before manuscript claims.

## Small JSON source contract

Original points are accepted as B4 scalar/EWPO CSV (read-only). Each
independent backend may supply a **real calculated** JSON object
(not a manually fabricated pass) with:

\`\`\`json
{
  "schema_version": 1,
  "stage": "bsgamma",
  "provenance": {
    "source": "validated physical NNLO model calculation with source revision",
    "validation_report": "independent same-scheme SM and TypeII controls"
  },
  "records": [
    {
      "candidate_id": "B4_0004143",
      "scheme_matched_two_charged_inclusive_rate": false
    }
  ]
}
\`\`\`

The shown \`false\` correctly gives
\`BLOCKED_MODERN_TWO_CHARGED_MATCHING\`; do NOT change it to true to
make the result look complete. Analogous \`stage\` names are:
\`neutrino\`, \`lfv\`, \`decays\`, \`production\`. Full field structures
are documented in \`scripts/zee_priority1_contracts.py\`.

For HiggsTools input, model-sourced \`decays.particles\` is keyed by
\`h,H,A,H1,H2\`, with \`mass_GeV\`, \`total_width_GeV\` and
\`partial_widths_GeV\` keyed by **official HiggsTools decay-mode
identifiers**. Each model-sourced \`production.particles\` is keyed
by the same five particles and mode names, with \`sigma_pb\`,
\`uncertainty_pb\` and \`collider\`. The adapter checks exact masses and
sum(partials)=total and refuses to call HiggsTools if the source has not
affirmed complete mode coverage and validated HiggsTools naming. Actual
HiggsTools independently checks mode parsing/availability.

Reference API:
https://higgsbounds.gitlab.io/higgstools/alternative_input.html
and https://higgsbounds.gitlab.io/higgstools/HiggsBoundsAPI.html .

## One AF command: smoke test

\`\`\`bash
cd /home/aalida/zee
git switch feature/global-scan-priority1
git pull --ff-only
bash scripts/zee_priority1_one_shot.sh
\`\`\`

This compiles all five new Python modules, runs 22 source-safe and numerical tests
and evaluates a one-line original-B4-style *synthetic* scalar CSV. All
five missing full-physics backends are correctly marked BLOCKED and
\`Zee_allowed_or_excluded\` remains null. **This smoke test is not physics
research output.**

For actual previously screened input B4 points:

\`\`\`bash
python3 scripts/zee_priority1_cli.py \\
  --points work/zee_large_integrated_20261020_v1/B4_adaptive/all_screened_candidates_NOT_ALLOWED.csv \\
  --out work/zee_priority1_B4_full_population_initial_contracts_v1
\`\`\`

This lists all B4 points and which absent Priority-1 computations need
to be added; it does not rerun their EWPO/scalar RGE or find viable
points. Provide \`--bsgamma\`, \`--lfv\`, \`--neutrino\`,
\`--decays\`, \`--production\` with source-produced exports as backends
are finished. \`--require-all-inputs\` makes missing files fatal.
HiggsTools API evaluation additionally requires **BOTH**
\`--higgsbounds-data /path/to/HBDataSet\` and
\`--higgssignals-data /path/to/HSDataSet\`; both are loaded just ONCE.

Do not feed 5–10M points to this current in-memory CSV validator at
once. This is a first-priority **component adapter**, not the future
chunked, resumable HTCondor production scanner (Priority 3).

## Additional genuine numerical components

`scripts/zee_priority1_neutrino_gaussian.py` performs a complex symmetric
Majorana Takagi diagonalization in both NO and IO, reconstructs three
physical mixing angles, the Dirac phase, the physical mass splittings and
a supplied 5-dimensional positive-definite correlated Gaussian
chi-squared. It checks the full complex mass-matrix reconstruction and
explicitly labels the Gaussian result as **not a full non-Gaussian
oscillation likelihood**. Zero lightest mass is supported. No
experimental central values or covariances are invented; the actual
oscillation-data release is a required independent input.

`scripts/zee_priority1_coherent_lfv.py` computes real coherent
radiative LFV branching ratios from supplied full complex left/right
Wilson amplitudes, including interference (not a sum of independent
sub-rates). It refuses to certify the radiative rate unless all six
neutral/charged one-loop and fermion/W/scalar Barr–Zee contribution
classes are explicitly present, in a common validated operator
convention. It still does **not generate** the missing two-loop
amplitudes, mu-e nuclear overlap or 3-body flavor rates. Those need
independent code. Unit tests include cancellation of two amplitudes.

**GitHub Actions:** 22 tests currently green (12 backend/interface
contracts + 10 complex-matrix/LFV interference numerical regressions).
These tests do not establish that any physical Zee configuration is
allowed.

## Actual next scientific implementation tasks

1. Build and independently validate modern matched Zee two-state flavor
   amplitudes and NLO/NNLO inclusive matrix elements and theory covariance;
   do not use F7 additive legacy-NP to modern-SM approximation.
2. Implement/calibrate both neutrino orderings, oscillation likelihood
   and full LFV amplitude interference (including nuclear conversion).
3. Implement all physical neutral/charged decay rates, thresholds, QCD,
   off-shell and HiggsTools mode mapping with independent MadWidth checks.
4. Generate quark/lepton/gauge-consistent hadronic cross sections
   (ggF, bbH, associated H±, relevant cascades, etc.) with MG5/NLO
   provenance, PDFs, uncertainties, matching/normalization controls.
5. Only after genuine backends pass independent SM/Type-II and
   model-specific controls, activate the full HiggsTools comparison and
   build an appropriately calibrated combined likelihood.

The current project may still yield a constraints and cascade
phenomenology paper, but **as of this commit not a single benchmark is
certified fully allowed**.
