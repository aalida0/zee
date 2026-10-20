# E2 completed — 309 original-potential numerical survivors; one E3 multi-Yukawa campaign

## E2 AF results, 20 October 2026

User-supplied UChicago AF stdout:

- \`E2_B2_REFERENCE_REPRODUCED 40 OF 40\`.
- E2 completed **245/245** previously missing numerical original-tree-potential vacuum searches with original B2 single f/Y source recipe.
- **203/245** found **no** deeper tree potential after 128 multistarts, **42/245** produced an explicit deeper-potential witness.
- Combined with E1's original 150 C5 searches (**106** no witness; **44** deeper witnesses), the source-pinned union is **395/395** RGE-qualified original B4 points with finite numerical tree-vacuum search:
  - **309/395** (78.23%) with NO deeper tree potential witness in this finite search;
  - **86/395** (21.77%) with an explicit deeper witness.
- Relative to the full **5,557 distinct adaptive scalar+EWPO coarse bins**: **395/5557** (7.11%) passed the chosen 10 TeV one-loop BFB and full 55-channel unitarity diagnostic under **one** exact-central-neutrino B2 f/Y family; **309/5557** (5.56%) also had no deeper tree minimum *found*.
- E2 status \`E2_ALL_395_ORIGINAL_B4_VACUA_NUMERICAL_AUDIT_NOT_ALLOWED\` and summary location:
  \`/home/aalida/zee/work/zee_E2_complete_395_original_vacua_20261020_v1/summary.json\`.
- **Zero** full-Zee allowed/excluded classifications are available; the computed no-witness result is NOT a global stability certificate and the 10 TeV cutoff is an *assumed theory-validity requirement*.

The E1 sample of first 150 was ranked toward higher cascade proxies. Its deeper-witness rate (44/150 = 29.3%) differs from E2's remaining 245 (42/245 = 17.1%). These are **not** confidence intervals for global survival or meaningful prior-independent frequencies.

## Next priority: test *actual lepton Yukawa choices* in the 309 original potentials

Before another B4 proposal run, the key unknown is whether the original B4 potential still has acceptable RG behavior using the *same* complex f,Y matrices selected by better neutrino/flavor reconstruction, rather than borrowing its previous RG classification from one fixed f,Y seed.

E3 is a **single 309-spectrum, resumable joint neutrino/LFV/RGE campaign**. It uses existing verified physics code without modifying matching formulas:

1. Verify complete E2 status, archived exact original B4 309-row source CSV, 395-row numerical original-vacuum ledger, and checksum for every E2 result. Verify original source PyR@TE one-loop complex-Zee \`RGEs.py\` SHA and full 676/676 numeric source test.
2. Generate **300 exact-central-neutrino B2 Yukawa families per original scalar point** (309×300 = 92,700 trials), scanning both complex \(f\)-null-direction quadratic roots and four complex \(Y\) homogeneous modes, with the already implemented flavor and perturbative prefilters. Retain **five** per spectrum ranked by the **B2 one-loop subset only**. The E1 original \`strength=0\` f/Y family is always generated and its original partial score is rechecked exactly.
3. For those **five** saved B2 roots, compute the **larger D1 coherent partial score**: included one-loop radiative modes + fermion-photon Barr–Zee + neutral tree-only three-lepton decays, checking exact-central-neutrino closure.
4. Optimize the best **two** families locally using the **D2 exact-neutrino nullspace parameterization** and 240 objective evaluations per start. D2's score remains a **partial**, source-checked LFV objective, not physical likelihood.
5. Add the source-implemented **D4 W-photon Barr–Zee amplitude subset** coherently, selecting whichever of the two optimized families has the smaller **extended** incomplete score. This is a controlled sensitivity study only: full two-loop diagrams, Z penguins, box terms and mu-e conversion remain absent or unvalidated. D4 W-photon source is not a full gauge-invariant physical LFV prediction.
6. **Crucial physics cross-check:** rerun the generated full original one-loop Zee RGE with the selected optimized f,Y matrices. Require 24/48-step agreement, all sampled complex-scalar sufficient BFB tests and 55-channel tree-unitarity through 10 TeV. A failed 10 TeV diagnostic under this one chosen optimized f,Y **does not** exclude the corresponding scalar spectrum or the broader lepton-Yukawa family. Do not silently import E1's RG pass from the unoptimized f/Y.
7. Keep all E3 records in a fsynced per-candidate checkpoint. \`--resume\` only when script, E2 summary, source \`RGEs.py\`, Q4v13 and numerical settings fingerprints agree. Never overwrite completed E1/E2 records.
8. Record exact per-candidate B2/D1/D2/D4 scores, optimized f/Y, source RGE diagnostics, and the ranked original B4 spectra, with explicit **NOT_ALLOWED**/unknown physics status.

If fewer than five B2 roots are available for a spectrum, it receives a diagnostic warning without an experimental exclusion; all 309 scalar spectra must be represented.

### Run one E3 campaign on a compute node / AF batch

The integrated optimization is substantially heavier than E1/E2. Prefer a UChicago AF compute allocation or batch job rather than an interactive shared login node. The commands below assume you already have the original existing checkout and the same Python environment.

~~~bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source .venv-flavor-f1/bin/activate
set -o pipefail

python -m unittest discover -s tests \
  -p 'test_zee_gateE3_309_multiroot_flavor_optimized_RGE.py' -v

python -u scripts/zee_gateE3_309_multiroot_flavor_optimized_RGE.py \
  --e2-dir work/zee_E2_complete_395_original_vacua_20261020_v1 \
  --output-dir work/zee_E3_309_multiroot_flavor_optimized_20261020_v1 \
  --neutrino-trials 300 \
  --B2-top 5 \
  --optimize-starts 2 \
  --optimizer-maxeval 240 \
  --uv-steps 24 \
  --orbits 2048 \
  --seed 20261014 \
  2>&1 | tee work/zee_E3_309_multiroot_flavor_optimized_20261020_v1_run.log
~~~

If interrupted, append \`--resume\` with all other options and the same original \`--output-dir\`. The file \`E3_309_spectrum_checkpoint.jsonl\` contains durable per-candidate records.

The final summary is:

\`\`\`text
work/zee_E3_309_multiroot_flavor_optimized_20261020_v1/summary.json
work/zee_E3_309_multiroot_flavor_optimized_20261020_v1/E3_ranked_309_original_flavor_RGE_NOT_ALLOWED.csv
\`\`\`

**Status:** Implemented in GitHub, not yet executed on UChicago AF. All unit tests are synthetic contract tests (not validation of a complete physical Zee flavor likelihood).

## The remaining publication-blocking physical work

The E3 scan does **not** complete the physical constraint pipeline. Even an extremely small D4 partial score does not establish lepton-flavor acceptance, because diagrams may interfere in both directions. The most important *missing* physics calculations are:

- Independently complete and source-validate the full Zee CLFV amplitudes and joint likelihood (all relevant one- and two-loop contributions, mu-e conversion and three-lepton final states, neutrino nuisance oscillation inputs including IO).
- Assemble the two-charged-Higgs **modern** B→Xsγ prediction at consistent NLO/NNLO Wilson evolution, operator schemes, matching and observable normalization, with theory-error treatment. Earlier 40/40 high-scale matching agreement does NOT establish full-rate agreement.
- Model-complete neutral and charged scalar **widths, HiggsTools production and decay predictions**, existing direct Higgs/charged-Higgs exclusions and LHC signal estimates.
- Proof/independent bounded numerical test of full scalar global vacuum conditions; C5 no-witness numerical search is not a global certificate.
- Perturbative-scale target and EFT/threshold assumptions must be stated, not silently inherited as universal exclusions.

E2 completes an important scalar inventory, E3 can test whether *its Yukawa selections* retain 10 TeV running consistency; neither can certify \`FULL_ZEE_ALLOWED\`. Avoid generating more B4 proposals before addressing model-complete experimental constraints.
