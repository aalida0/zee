# F21 — Wide stratified charged-Higgs and scalar-space campaign (25 Oct 2026)

## Why F20 is geographically narrow in parameter space

The successful F20 HTCondor campaign evaluated 20,000 proposals
but started each chain from three F18 source-matched points with
mH2 around 880 GeV. Gate B4's default per-iteration
mass step was **6 GeV**, and beta step **0.00045 radians**;
even thousands of proposals remain near the starting heavy-Higgs
region. Its 5075 screened records and 120 exact fixed-NO partial
LFV fitted Yukawa solutions are genuine *screened* calculations,
not a global allowed parameter-space scan.

User's F20 corrected merger returned 34 no-deeper-witness
(partial numerical tree-vacuum only) + below-historical-reference
partial LFV scores. Among those:
- 3/B4_0003477: H1=280.58 GeV, H2=837.85 GeV,
  BR(H2->H1 Z) included~0.7615,
  BR(H1->tb) included~0.9813,
  sin^2 gamma weighted and f/Y-adjusted included-channel
  cascade proxy~0.6280 (**not a physical pb cross section**),
  LO-linearized Bsgamma 4.06576 x 1e-4, no calibrated CL.
- 0/B4_0004694: H1=263.43 GeV, H2=818.20 GeV,
  f/Y-adjusted included-channel proxy~0.6260, LO-linearized
  Bsgamma 4.07017 x 1e-4. Its coherent partial LFV including
  W-photon Barr-Zee is ~0.02736 x reference, much larger than
  the earlier no-W diagnostic (~0.000137), demonstrating why
  incomplete LFV estimates must not be promoted to exclusions.

## F21 physically reconstructed stratified design

Six independent CERN HTCondor shards each execute 6000
independent stratified draws plus 4000 locally correlated
custodial/near-alignment draws, **60,000 total proposals**.

Independent axes (the generator spans the full intervals,
but passing solutions are NOT guaranteed across every bin):

| Parameter | Scan window | Physical treatment |
|---|---|---|
| `mH1` | 200–1200 GeV | Log-uniform subject to H2>H1+mZ+14 |
| `mH2` | 450–2500 GeV | FIVE stratified bins: 450–700, 700–1000, 1000–1400, 1400–1900, 1900–2500 |
| `tanbeta` | 0.7–35 | Log-uniform FIVE independent bins |
| `gamma` | 0.08–1.49 radians | FOUR independent bins; charge-mixing convention fixed to first quadrant |
| `mh2`, `ma` | 180–2600 GeV | Vary relative to the doublet-charged mass-scale with multiple width/splitting families |
| `alpha-beta` | ~±0.13 radians | Near-alignment Gaussian plus bounded tails |
| `m12sq` | dimensionful, correlated to doublet mass | Scanned soft offset around doublet mass^2, not fixed original F18 value |
| `lc,k1,k2` | positive spanning O(0.02–10) | Log-uniform singlet quartics |
| `k12` | signed up to 0.75 min(k1,k2) | Full Zee charged-doublet/singlet quartic variation |

The doublet-sector diagonal mass scale
`mD^2=mH1^2*cos(gamma)^2+mH2^2*sin(gamma)^2` is used
for correlated *proposals* for `mh2`, `ma`, and the soft
term. This avoids the ineffective strategy of choosing arbitrary
uncorrelated multi-TeV scalars that necessarily generate huge 2HDM
quartics. **No special acceptance is granted**: Gate6 independently
rebuilds quartics, tests sufficient BFB/tree 8pi unitarity; Gate A1H
calculates Gfitter 2026/PDG 2025 correlated scalar STU before recording
any point. Physically forbidden bins can have ZERO surviving points.

The local stage chooses an already passing seed **uniformly by occupied
heavy-mass bin**, not by number of accepted points, to avoid converging
back onto the original ~800 GeV region.

At every screened point calculate independent analytic Type-II two
charged LO C7/8 and 2026 **linearized** Bsgamma (mt input 163 GeV).
This is NOT a 2026 NNLO exclusion, confidence contour, scheme error,
or validated surrogate of the absent original SuperIso kernel.

Per shard, choose **40 candidate spectra stratified by heavy mass,
tanbeta and gamma bins**, fit exact *fixed normal-ordering central*
neutrino matrix with complex f/Y, optimize coherent partial LFV,
and recompute B3 f/Y-dependent conditional charged cascade widths.
Add coherent W-photon Barr-Zee amplitudes from F19b backend.
Then run C5 on **12 representative spectra**, 64 starts each, to
search for explicit deeper tree scalar field configurations.
No deeper witness != a proven globally stable EW vacuum.
At high H2 mass, flag GammaH2(included)/mH2>10%: a broad
resonance undermines narrow-width cascade interpretations.
Neither this width nor the BR proxy is a full MadWidth model.

**Totals: 60k proposals, up to 240 independent complex neutrino/LFV
fits, up to 72 six-field vacuum witness searches.**

Scientific gap remains the same: updated neutrino likelihood over
CP phases and optionally IO, complete radiative LFV/conversion,
matched higher-order mixed-state Bsgamma, HiggsTools/direct limits
and physical QCD-corrected pp rates. F21 is ONE coverage extension,
not a substitute for the P0 calculation programme.

## Stage once on local Ubuntu

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only

# Updated physics source archive (include all original F20/F19 dependencies).
tar -czf ~/F21_scripts_bundle.tar.gz scripts

scp ~/F21_scripts_bundle.tar.gz \
  scripts/zee_paper1_F21_condor_worker.sh \
  scripts/zee_paper1_F21_prepare_submit_lxplus.sh \
  scripts/zee_paper1_F21_merge_six_stratified_mass_shards.py \
  aalida@lxplus.cern.ch:~/
```

No user-facing microgate sequence. The consolidated GitHub CI
compiles the new source/merge Python and Bash syntax. The big jobs
perform the complete physics checks automatically, preserving
failed worker diagnostics as tarball records.

## One LXPLUS submit command

```bash
bash ~/zee_paper1_F21_prepare_submit_lxplus.sh
```

It verifies the original five F18-F19d JSON source hashes and the
F20 corrected merged **scalar-projection** CSV SHA from the F20 report.
That F20 CSV does NOT contain the full `alpha,m12sq,lc,k1,k2,k12`
potential input needed for reliable re-seeding. F21 consequently
draws new independent wide proposals and only uses the **full exact F19**
source scalar potential as an initial-failure recovery seed. The
F20 CSV is a source-hashed prior screening/provenance dataset, not
an assumed complete quartic input. Original sources are read-only. New immutable AFS job home:
`~/zee_F21_wide_stratified_20261025`.
New EOS archive:
`/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024/F21_wide_stratified_20261025`.

Review jobs with `condor_q $USER`; only six archives named
`F21_result_shard_0.tar.gz`.. `5.tar.gz` after all
successful transfers prove work done. Exit code inside archive,
not queue absence, confirms actual numerical success.

## One final merge after SIX successful shard archives

```bash
export F21_EOS=/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024/F21_wide_stratified_20261025

PYTHONPATH="$HOME" python3 \
 ~/zee_paper1_F21_merge_six_stratified_mass_shards.py \
 --eos "$F21_EOS" \
 --out "$HOME/zee_F21_wide_merged_20261025"

python3 - <<'PY'
import json
from pathlib import Path
d=Path.home()/"zee_F21_wide_merged_20261025"
j=json.loads((d/"F21_WIDE_PRODUCTION_summary_NOT_ALLOWED.json").read_text())
for k in (
 "total_independent_stratified_and_local_proposals",
 "total_scalar_EWPO_screened_distinct_per_shard_not_physical_allowed",
 "accepted_strata_record_count_not_allowed_volume",
 "complex_neutrino_fixed_NO_partial_LFV_fits_completed",
 "vacuum_multistart_searches_attempted",
 "vacuum_no_deeper_witness_AND_LFV_partial_score_lt1_subset_NOT_ALLOWED",
):print(k,j[k])
PY

head -n 11 \
 "$HOME/zee_F21_wide_merged_20261025/F21_WIDE_vacuum_LFV_triaged_cascade_NOT_FULL_ALLOWED.csv"
```

The merger is fail-closed on source mismatch and any missing or
failed worker. It records how many points were attempted and passed
in each mass shell, tanbeta and gamma slice. The resulting scatter
plots show **exploratory screened distributions, not confidence
regions, exclusion limits or unbiased physical allowed volume**.

## Final publication decision

Compare H2 mass shells including >1 TeV with the 2026 LO flavor
diagnostic. If apparent heavy-Higgs regions survive scalar BFB/STU,
partial LFV and numerical vacuum screening, prioritize only a
small *mass-stratified* shortlist for rigorously implemented
full flavor, neutrino fit, HiggsTools and real `sigma x BR`.
No point is fully allowed merely because F21 has a positive
multi-gate screen. Avoid another larger scan before finishing
the decisive higher-order quark and lepton flavor calculations.
