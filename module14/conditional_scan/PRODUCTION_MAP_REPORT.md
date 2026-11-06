# D14D actual production map and independent 14 TeV pilot

**PRODUCTION_MAP_13TEV_COMPLETE** — actual, validated rates for all 16 scalar points.
**PRODUCTION_14TEV_PILOT_COMPLETE** — three separately executed 14 TeV benchmarks.

This is a conditional collider-rate data bundle. Physical B→Xsγ is **UNKNOWN**,
LFV is partial, HiggsTools coverage is incomplete, and `global_acceptance=null`.
Production scale/PDF and decay theory errors are unmeasured. These truth-level
LO rates and complete on-shell tree two-body BRs supply no experimental
sensitivity, exclusion or discovery statement.

## Scope and immutable evidence

The original 13 TeV runs for 15591, 2264 and 15673 are reused byte-for-byte,
including their receipts and native statistical errors. Exactly **16 new native
integrations** were executed: the other 13 shortlisted points at 13 TeV, and
15591, 2264 and 15673 at 14 TeV. No interpolation, mass-only card edits, energy
rescaling, broad scan, vacuum search, flavor backend calculation, new collection,
author outreach or Condor submission was performed.

The full immutable 225-point / 900-family AF dataset was read locally from
`/tmp/zee-d14c-dataset.json`, SHA256
`2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9`.
Its original COMPLETE collection identity, input/gate/source hashes, all family
records, neutrino closure and complete D4 channel ledgers were revalidated by
unchanged `candidate_export.audit`. This does not claim a new AF collection.
Original Modules 0–13, Module14 workers, historical source/data/evidence,
D14C receipts and acceptance logic are unchanged.

## Fixed calculation and independent validation

MG5_aMC 3.6.7, the exact real SARAH Zee UFO, LHAPDF 6.5.6 and frozen
NNPDF30_lo_as_0130 member 0 (ID 263000) are SHA checked against D5/D6.
The runtime gate compares 827 official source files plus the launcher against
the pinned release archive. The LO 5FS process definition is exactly:

```text
generate g d3 > u3 hm3 QCD=1 QED=1
add process g d3bar > u3bar hm3c QCD=1 QED=1
add process d3 g > u3 hm3 QCD=1 QED=1
add process d3bar g > u3bar hm3c QCD=1 QED=1
```

Both H2 charges and both incoming beam orders occur once. Native hm3 is H2−.
The top and hard H2 are stable; light hard quarks including b are massless,
mt,kin=172.4 GeV. No 4FS addition, shower, detector simulation or acceptance
factor is included. Beams are 6500+6500 GeV or 7000+7000 GeV. Fixed
muR=muF1=muF2=mH2; LO PDF alpha_s uses alpha_s(MZ)=0.130. Independent
quark Yukawa masses follow the unchanged D4 running prescription at mH2,
with its separate alpha_s(91.1876)=0.118. Yukawas are frozen within each
integration. Seed 4154 and 5000 requested events reproduce the D14C recipe.

All 64 full family cards were rebuilt from actual scalar and complex Yukawa
records, with scalar closure, LHA round trips and finite-coupling checks.
Both signed tbH2 chiral coefficients and conjugates were checked against the
frozen UFO. **320** MG/ALOHA versus independent D5 Dirac-trace controls test
both charges for every family at original gamma, zero, ±pi/2 and negative
original gamma, including Ward and sign/endpoint checks. Each scalar's four
production amplitudes agree to relative 1e-13. The quark projection is
−sin(gamma); the cascade's separate sin(2gamma) coupling vanishes at zero
and ±pi/2. No mixing endpoint was promoted into a cascade benchmark.

Every native run is checked independently against its retained command,
input/output SHA256s, full original/normalized/banner cards, generator version,
process list, beam energies, fixed scales, PDF, cuts, source manifests and
compiled source snapshots. Result-file, log and banner rates agree within
their print precision. Samples range from 133710 to 178452; reported relative
integration errors range from 0.158% to 0.220%. These errors are numerical,
not production theory uncertainties. Full model LHA values and **all non-beam
run settings** are also checked for equality between each 13/14 TeV pair.

## Ranked 13 TeV map

The scalar order below uses the maximum of the four family sigma × BR values;
family-specific ranks (1–64) use their own actual sigma × BR. The scalar order
is identical for the four families. Family spread reflects distinct inputs,
not a theory error. The linked per-family tables retain individual H2 total
widths, complete cascade BRs, decay/source/SM hashes, exact family/Yukawa
bindings and numerical proxy errors. H1 decay BRs are supplied **separately**;
no H1, Z, top or W decay BR is multiplied into the cascade rates.

| Scalar rank | ID | mH2 [GeV] | sigma LO [pb] | Numerical error [pb] | sigma × tree BR range [pb] |
|---:|---:|---:|---:|---:|---:|
| 1 | 15591 | 1035.704 | 0.011868 | 2.1971e-05 | 0.0038693686–0.0038697429 |
| 2 | 8850 | 1077.158 | 0.0098719 | 1.9948e-05 | 0.0034582357–0.0034585032 |
| 3 | 2264 | 1165.975 | 0.0050014 | 8.8007e-06 | 0.0018437592–0.0018438048 |
| 4 | 14984 | 1174.493 | 0.0051763 | 9.8053e-06 | 0.0016887713–0.0016888501 |
| 5 | 4611 | 1091.178 | 0.0053337 | 1.066e-05 | 0.001458727–0.0014591515 |
| 6 | 15673 | 1277.363 | 0.0029876 | 5.9189e-06 | 0.0011763772–0.0011764769 |
| 7 | 14074 | 1419.362 | 0.0021975 | 4.8299e-06 | 0.00034343018–0.0003434898 |
| 8 | 3693 | 1220.240 | 0.0016031 | 3.0624e-06 | 0.00031987689–0.00031988119 |
| 9 | 9454 | 1183.380 | 0.00070111 | 1.108e-06 | 0.00017413634–0.00017414674 |
| 10 | 2616 | 1536.119 | 0.00025799 | 4.9211e-07 | 7.4819886e-05–7.4820315e-05 |
| 11 | 8294 | 1447.183 | 0.00026348 | 5.5838e-07 | 7.4657987e-05–7.4660089e-05 |
| 12 | 14187 | 1528.451 | 0.00022983 | 4.2261e-07 | 6.875987e-05–6.87605e-05 |
| 13 | 16385 | 1467.900 | 0.00023003 | 3.9393e-07 | 5.7179647e-05–5.717999e-05 |
| 14 | 13345 | 1440.892 | 0.0001849 | 3.7906e-07 | 5.0758987e-05–5.0759612e-05 |
| 15 | 11016 | 1785.058 | 4.6678e-05 | 8.8109e-08 | 1.0321365e-05–1.0321435e-05 |
| 16 | 14555 | 1360.627 | 1.4114e-05 | 2.7316e-08 | 4.2491783e-06–4.2495273e-06 |

The leading rate is 15591, followed by 8850. The different tanbeta and gamma
values make production non-monotonic in mass; BR-only ordering does not give
the rate ordering. This finite shortlist defines neither an optimum nor a
mass exclusion boundary.

## Actual 14 TeV comparison

| ID | Actual sigma(13 TeV) [pb] | Actual sigma(14 TeV) [pb] | Numerical error at 14 TeV [pb] | sigma14/sigma13 ± numerical error* |
|---:|---:|---:|---:|---:|
| 15591 | 0.011868 | 0.016244 | 3.119e-05 | 1.368723 ± 0.003651 |
| 2264 | 0.0050014 | 0.0069852 | 1.4167e-05 | 1.396649 ± 0.003750 |
| 15673 | 0.0029876 | 0.0042345 | 7.6722e-06 | 1.417358 ± 0.003805 |

*Ratio errors propagate the native integration errors in uncorrelated
quadrature. These are separate actual integrations with the same seed recipe;
inter-run covariance was not measured and is explicitly null. This assumption
is not a calibrated theory confidence interval. The measured ratios are
process/spectrum specific and must not reweight the other 13 points.

No seven-point scale pilot, PDF ensemble, higher-order correction, luminosity
yield or leptonic final-state estimate is included. Scale/PDF/decay theory-error
fields remain null; scale sensitivity is NOT_EVALUATED. No PDG branching
fraction is needed or silently assumed.

## Unresolved physics and plots

The original sample has 33 sufficient-vacuum PASS and 192 UNKNOWN points.
Its published linear LO-NP B diagnostic gives 77 APPROX_COMPATIBLE and 148
APPROX_DISFAVORED, with **physical B classification UNKNOWN for all 225**.
The six nominal-compatible sub-TeV opportunities 3582, 3821, 6850, 11920,
13512 and 17671 remain vacuum UNKNOWN, without production in this task.
Earlier bounded searches for three gave no sufficient PASS certificate or
credible deeper witness; they are not repeated or promoted here. See the
preserved [D14C follow-up](CANDIDATE_FOLLOWUP.md).

LFV omitted amplitudes and the original incomplete charged/heavy-neutral
HiggsTools coverage remain recorded per family. The HiggsTools H1/H2 production
interface is not rerun or completed by this H2-only sidecar. Nominal flavor
compatibility and a sufficient tree vacuum certificate do not establish
physical flavor acceptance, full LFV/Higgs compatibility, loop/thermal vacuum
stability or a globally viable benchmark.

- [13 TeV cascade rates](production_map_plots/cascade_rates_13TeV.png): all four families; numerical errors only.
- [Production versus mass](production_map_plots/production_mass_13TeV.png): color tanbeta, size |gamma|.
- [Original conditional scalar scatter](production_map_plots/conditional_vacuum_scatter.png): vacuum and nominal B diagnostics; six unresolved opportunities circled.
- [Actual 13/14 TeV comparisons](production_map_plots/production_13_vs_14TeV.png): three independently integrated spectra and measured ratios.

SVG versions accompany each PNG. Every figure states the conditional scope
and missing physics; no detector-constraint or experimental-sensitivity claim
is made.

## Artifacts and reproduction

- [production_map_13_14.json](production_map_13_14.json): 19 scalar rates, 76 family rows, full mapping/amplitude evidence, native receipt bindings, limitations and unresolved opportunities.
- [13 TeV per-family CSV](production_map_13TeV_families.csv) and [14 TeV per-family CSV](production_map_14TeV_families.csv).
- [Scalar-rate CSV](production_map_scalar_rates.csv), ordered by actual cascade rate within each energy.
- [Table hashes](production_map_hashes.json) and [plot hashes](production_map_plots/plot_hashes.json).

Raw cards, integration statistics/events, logs, generated/compiled code,
source snapshots and SHA receipts remain ignored in
`validation/module8/local/d14d/`. Original D14C artifacts remain in
`validation/module8/local/d14c/`. No native binary or log is committed.
The JSON includes the source, runtime, card, result, banner and receipt hashes;
family binding hashes include scalar, full Yukawas, module2 input, card, energy
and scalar-level receipt. Four family rows share one scalar integration;
they are not four independent hadronic integrations. Byte-identical native
artifacts require preservation of these local directories; the committed
bundle audits their hashes but does not redistribute the external runtime.

Re-export the preserved evidence on this host without generator reruns:

```bash
python -m module14.conditional_scan.production_map_export \
  --dataset /tmp/zee-d14c-dataset.json --output /tmp/d14d-fresh-export
MPLCONFIGDIR=/tmp/zee-d14d-mpl python -m module14.conditional_scan.production_map_plot \
  --input /tmp/d14d-fresh-export/production_map_13_14.json \
  --output /tmp/d14d-fresh-plots
D14C_DATASET=/tmp/zee-d14c-dataset.json \
  python -m unittest discover -s tests -p 'test_module14_conditional_*.py' -v
git diff --check
```

The exporter refuses an existing export directory and deterministically
serializes the same validated inputs. PNG/SVG rendering additionally depends
on Matplotlib/font versions; hashes capture the delivered artifacts.

To reproduce **new integrations**, provision the pinned runtime and original
D14C artifacts under the documented absolute checkout path, verify the dataset
SHA, and use a fresh, nonexistent `validation/module8/local/d14d` workspace.
Preserve rather than overwrite this task's native artifacts. The commands
below are finite manual commands on this host or an identically provisioned
AF shell; they never call Condor. The runtime gate deliberately fails if
pinned assets are absent. No transfer or remote-data availability is assumed.

```bash
python -m module14.conditional_scan.production_map_run map \
  --dataset /tmp/zee-d14c-dataset.json
REPO="$PWD"
( cd validation/module8/local/d14d
  PYTHONPATH="$REPO" python -m module14.conditional_scan.production_map_run matrix )
for point in 8850 4611 14984 9454 3693 14555 14074 13345 8294 16385 14187 2616 11016; do
  python -m module14.conditional_scan.production_map_run run --point "$point" --energy 13 || break
done
for point in 15591 2264 15673; do
  python -m module14.conditional_scan.production_map_run run --point "$point" --energy 14 || break
done
# Then run the exporter and plotting command above, with fresh output paths.
```

Each run refuses existing process directories; native failures retain their
artifacts. Missing receipts export NOT_EVALUATED/null rates and a PARTIAL gate,
never interpolated values or zeros. A fresh statistical reproduction produces
new receipt hashes and slightly different numerical estimates. The three
D14C 13 TeV receipts remain fixed provenance and are not regenerated by these
commands.

## Completion audit

Validation passed: **26 conditional tests with no skips**, including every new
native integration and deterministic full-bundle re-export, plus **four unchanged
D5 native-gate tests**. All four figures were visually checked; `git diff --check`
passes.

Both technical production completion gates pass. Full source/input and decay
binding, family amplitude equality, charges/beam orders, native artifact origin,
13/14 model/setting equality, numerical consistency and missing-data semantics
are checked. Focused tests cover wrong beam energies/PDF/scales/cuts, tampered
input/output/compiled-source hashes, duplicate process definitions, family
bindings, baseline preservation, all new native rates and deterministic exports.
All original physics limitations remain explicit. No further integrations or
physics scans are required for this bounded task.
