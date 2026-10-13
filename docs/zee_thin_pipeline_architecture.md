# One-entry Zee model constraint pipeline

**Purpose:** keep the paper code thin, explicit and auditable.

The user supplies a CSV of scalar parameter points and one JSON
configuration; the orchestrator calls the verified calculation backends.
It does **not** reimplement HiggsTools, SuperIso or theoretical widths.

## Implemented today

```text
Input parameter points (previous B1/B4 theory+EWPO screened CSV)
                  |
                  v
      scripts/zee_pipeline.py
                  |
     +------------+-------------+
     |            |             |
  B2 neutrino    B3 widths     A1V legacy patched SuperIso
  matrix and     from exact    source-checked two-charged B->Xs gamma,
  partial LFV    B2 f/Y       NOT 2026 calibrated exclusion
     |            |             |
     +------------+-------------+
                  |
            B4C joined audit
                  |
       manifest.json + one joined CSV
       physical_allowed_points = null
```

The pipeline invokes existing internal project modules via
`subprocess`. All calculations keep their existing unit tests.
This avoids introducing a second implementation of neutrino-mass
reconstruction, charged scalar widths, or Wilson coefficients.

At this stage the user should supply already theory+EWPO-screened
points (e.g. B4 shortlist). The B4 adaptive scanner remains an
independent way to *propose* points. We should not accidentally
describe arbitrary input points as having passed scalar theory or
oblique constraints; there is no automatic fresh B4 screening in
the new orchestrator yet.

### Run from the existing AF repository

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source ~/fccee_zh/scripts/setup_key4hep.sh

python3 -m unittest discover -s tests \
  -p 'test_zee_pipeline.py' -v

# inspect plan and dependencies, no physics evaluated
python3 scripts/zee_pipeline.py \
  --points work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --settings configs/zee_pipeline_partial.json \
  --output-dir work/zee_pipeline_b4pilot_v1 \
  --dry-run

# RUN B2 + B3 + source-pinned A1V SuperIso + strict B4C join
python3 scripts/zee_pipeline.py \
  --points work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --settings configs/zee_pipeline_partial.json \
  --output-dir work/zee_pipeline_b4pilot_v1
```

The output directory must be new or empty to prevent mixing outputs
from different points/settings. The script validates ID uniqueness,
finite inputs, positive masses, charged-mixing ranges and
`tanbeta = tan(beta)` consistency; it fingerprints CSV, settings,
commands and output artifacts and writes each backend's terminal
output into a stage-named log.

```text
work/zee_pipeline_b4pilot_v1/
  manifest.json
  neutrino_and_partial_LFV.log
  general_Zee_leptonic_widths.log
  SuperIso_legacy_two_charged.log
  joint_provenance_audit.log
  B2_neutrino/
  B3_widths/
  A1V_legacy_superiso/
  B4C_joint_audit/
    joint_scalar_neutrino_width_flavour_NOT_ALLOWED.csv
    summary.json
```

Every calculation is tagged **PARTIAL_DIAGNOSTICS**;
`full_model_allowed_points:null` is deliberate. We do not have
a full Zee experimental likelihood.

The JSON file `configs/zee_pipeline_partial.json` contains
pinned relative paths to the audited local SuperIso source tree
and A1M/A1U source-and-validation reports, so the user does not
have to retype the lengthy commands.

To use a new parameter-point CSV, only change `--points` and
use a NEW `--output-dir`.

## Future adapter interface (physics still required)

**Neutrino/LFV:** Today's B2 does algebraic exact reconstruction
for *one fixed* neutrino mass matrix, plus partial one-loop LFV.
A complete external or internal Zee LFV calculator will need both
neutrino mass orderings, oscillation likelihoods, phases,
Barr-Zee dipoles, mu->3e and mu-e conversion, charged-current
universality and other relevant observables. It must expose a
validated per-point likelihood result with source references.

**SuperIso:** The existing A1V patch is a source-pinned legacy
two-charged-Higgs **diagnostic**. Its output does not include
a 2026 NNLO calibrated allowed/excluded decision. The next
adapter must use a perturbatively consistent full BSM treatment
and independent validation before contributing to a global fit.

**HiggsTools:** According to official documentation,
`Higgs.predictions.Predictions` allows arbitrary BSM scalar
predictions, while `Higgs.bounds.Bounds` and
`Higgs.signals.Signals` compare those predictions to direct
searches and Higgs signal-rate measurements. HiggsTools does
**not** supply the general-Zee model implementation.
We must build and validate the model-to-HiggsPredictions adapter:
all neutral and charged scalar masses, widths, mixing, couplings,
physical BRs, production cross sections, and relevant cascade
channels, while tracking unimplemented search topologies.
DO NOT create the API input from B4 nonleptonic proxy or partial
B3 width inventory and label it a complete experimental test.

A future adapter may call the local HiggsTools Python binding
directly, preferably reusing one initialized Bounds and Signals
object per batch. See
https://higgsbounds.gitlab.io/higgstools/HiggsBoundsAPI.html and
https://higgsbounds.gitlab.io/higgstools/HiggsSignalsAPI.html .

**Theoretical scalar/EWPO:** Existing Gate6/B4 calculations are
usable candidate generation; they need validation against full
vacuum structure and careful treatment of conservative sufficient
BFB conditions for a publication-grade global exclusion.

**Production:** Real sigma(pp->tbH2) requires a separate
cross-section calculator and uncertainty envelope; the current
sin^2(gamma)-weighted proxy is *not* sigma.

## Scientific output sought for Paper 1 (no Delphes)

When EVERY relevant adapter is independently validated, add a
central driver that does per-point:
1. scalar potential and unitarity/vacuum consistency,
2. correlated electroweak constraints,
3. neutrino oscillation likelihood with full Yukawa freedom,
4. complete CLFV and universality,
5. model-specific HiggsTools checks,
6. modern precision B->Xs gamma and other quark flavor bounds,
7. physical widths and hadronic production rates.

Publishable deliverables:
- a novel surviving/excluded mass/mixing envelope,
- largest **fully constrained physical** cascade signal rate,
- constraint-ablation contributions and correlated
  neutrino/LFV--collider observables,
- projected Mu3e/Mu2e/COMET/Belle II sensitivity against surviving
  large-cascade candidates,
- a public benchmark database with transparent theory uncertainties.

Do not call the present 30 scalar points experimentally allowed.
The orchestrator is infrastructure, NOT the main paper result.

## Version pinning

Each production-quality scan must retain:
- source commit hash of this `zee` repository,
- checked vendor versions and source patches for SuperIso,
- HiggsTools release and data-set versions,
- neutrino global-fit version and nuisance input,
- model UFO and decay/cross-section generator versions,
- numerical options, random seeds and parameter priors.

**Literature:** Florentino–Romão–Silva arXiv:2106.08332;
Herrero-García et al. arXiv:1701.05345;
Chen arXiv:2508.18757;
HiggsTools arXiv:2210.09332; SuperIso arXiv:0808.3144.
