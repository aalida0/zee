# D5 production audit — 2026-10-28

**D5_UFO_VERTEX_PASS; D5_EXECUTED_PARTON_LO_RATE_PASS; D5_CHAIN_LO_ARITHMETIC_PASS.**
These certify the stated LO parton-level reference benchmarks and conditional
arithmetic. **D5_NOVELTY_NOT_ESTABLISHED** remains. Full LFV and the 2026
linearized flavor filter are false; global Zee acceptance is null. All D2 vacuum
results remain UNKNOWN and physical 2026 B→Xsγ is incomplete.

## Executed rates

Both charged final states and both incoming beam orders are included exactly once.
Errors below are actual MG5 integration errors, not scale/PDF/theory uncertainties.
mH2=700 GeV, beta=1.394, gamma=1.089; 13.6 TeV pp, stable external scalars/top.

| mH1 [GeV] | P1 Z-only mixed pair [pb] | P2 gb associated, 5FS [pb] |
|---:|---:|---:|
| 250 | 0.00016119 ± 1.7615e-07 | 0.0045246 ± 8.2534e-06 |
| 300 | 0.0001344 ± 1.3494e-07 | 0.0045246 ± 8.2534e-06 |
| 350 | 0.00011155 ± 1.1348e-07 | 0.0045246 ± 8.2534e-06 |

P3 is optional and **not executed**: a separate massive-bottom 4F PDF/card setup
was not configured. Its entries remain null with this reason. 4FS and 5FS overlap;
never add them. The real-data schema is explicitly `d5-real-two-process-1.0.0`,
separate from the synthetic three-process arithmetic schema. No dummy 4FS rates.
Identical P2 results are expected: only the unused H1 mass changes, with the
same hard gb amplitude, all other inputs and random seed.

Actual audited UFO process syntax (P1 and P2 have separate generated directories):

```text
define q = u1 u2 d1 d2 d3
define qb = u1bar u2bar d1bar d2bar d3bar
# P1 (separate output directory)
generate q qb > z > hm3c hm2 QCD=0
add process q qb > z > hm3 hm2c QCD=0
add process qb q > z > hm3c hm2 QCD=0
add process qb q > z > hm3 hm2c QCD=0
# P2 (separate output directory)
generate g d3 > u3 hm3 QCD=1 QED=1
add process g d3bar > u3bar hm3c QCD=1 QED=1
add process d3 g > u3 hm3 QCD=1 QED=1
add process d3bar g > u3bar hm3c QCD=1 QED=1
```

## Native model, mapping and independent checks

`math -script scripts/zee_d5_export.m` performed a fresh SARAH 4.15.4 export using
Wolfram 15.0.1 and the unchanged ZeeTypeII source, model SHA256
`78d6b48232f9a75a21b058301d9233dba3ed067e21f534d27c0d6f415484aa4d`.
All export files/cards/logs are ignored under validation/module8/local/.
The pre-existing SARAH installation output was not used as a certified model.

`python -m module8.ufo_audit` evaluated all exported parameters/couplings and
performed **5904 signed numerical comparisons across 36 cards**:
all twelve D2 families at both D4 Yukawa scales, plus complex non-aligned and
signed/endpoint mixing controls. Every external LHA address is mapped explicitly,
serialized at 17-digit round-trip precision and reloaded before evaluation.
The source and two shifted spectra pass Module1 Hessian, tadpole and signed
mixing closure. No sample card or guessed external mass/potential input is used.
M112/M222/MCS2/M12Sq are absent from the UFO interaction parameter list; Module1
reconstructs them and checks the physical spectrum rather than inventing LHA inputs.

Native charged fields are Hm2/Hm3 with charge -1 and Hm2c/Hm3c with charge +1;
the scalar PDG signs must not be used to guess their physical charge. MG lowercases
these names. Both signed CKM orientations and all quark/lepton flavor pairs and
charge conjugates are compared with independent D3/D4 amplitudes. UFO FFS chains
use spinor indices (2,1); SARAH's exporter explicitly reverses PL/PR in that basis
(madgraph.m lines 126–127). Vector SSV coefficients use their actual ordered
H-,H+,V momentum difference, with the exporter vector sign convention. Photon
universality gives R Q Rᵀ=Q: its mixed coupling is exactly zero analytically;
numerical off-diagonal residual is 5.55e-17. The Z mixed coefficient
has the source -sin(2gamma)/2 normalization. Maximum signed quark/lepton residuals
are 2.78e-17/6.94e-18; physical-parameter
residual is 5.68e-14 GeV.

`python -m module8.mg_matrix_checks` independently executed Python/ALOHA amplitudes.
The qqbar Z amplitude agrees with the analytical spin/color normalization.
The gb amplitude agrees with a separate explicit two-diagram Dirac trace and
gluon Ward identity. The two P2 charges agree at the same partonic momenta. Fixed-mass
mixing controls reproduce sin²(2gamma) for P1 and sin²(gamma) for P2, including
negative gamma and zero/endpoints. Physical thresholds are mH1+700 and
172.4+700 GeV. Controls vary the production basis and do not assert viable scalar points.

`python -m module8.partonic_checks` independently integrates the analytical Z-only
partonic result against the actual PDF grid, both incoming beam orders and both
final charges. 100×100 and 180×180 Gaussian quadratures agree closely; every MG
P1 rate agrees within five actual integration errors (individual deviations are in
JSON). These independent numbers are checks, not substituted generator results.

## Generator scheme and authenticity

MG5 3.6.7 from the official tagged commit
`0e6c945573c8bab6246b9a172c219a7754125f51`; LHAPDF 6.5.6 compiled locally;
GNU Fortran 11.4.0. No unknown binaries or alternate Zee model were sourced.
The GitHub archive's missing .git metadata triggers its generic development banner;
all **846** relevant source files were independently compared byte for byte with
the official Launchpad 3.6.7 release: zero differences. The warning remains in logs.

PDF: [NNPDF30_lo_as_0130](https://lhapdfsets.web.cern.ch/current/NNPDF30_lo_as_0130/NNPDF30_lo_as_0130.info),
member 0, ID **263000**, five flavors, LO alpha_s from the PDF interpolation,
alpha_s(PDF MZ=91.199997)=0.130; alpha_s(700)=0.0982405554087.
muR=muF1=muF2=700 GeV fixed; scale/PDF variations not evaluated. Light and bottom
kinematic masses are zero; mt=172.4 GeV. Independent Yukawa masses are D4's
one-loop MS evolution to 700 with alpha_s(91.1876)=0.118:
mt,Y=148.0414556305571, mb,Y=2.69162343131315 GeV. Exact D4 complex unitary CKM
and full general-Zee leptons are retained. No Yukawa mass is silently replaced
by a pole or flavor matching input. H1/H2/top widths are zero for the hard
process; Z width is 2.4952 GeV. Other native defaults are bound in the cards.

Madevent requires a numerical MASS 24 entry even though MWm is internal in this
UFO: the checked dependent value 80.379 was added to local cards only. A pilot
with only q-qbar or g-b beam ordering had no automatic mirror process, so final
cards explicitly include both beam orders. Preliminary six-flavor-PDF diagnostics
were superseded by all six five-flavor runs. Neither pilot set is promoted here.

P1 is the separately justified Z-only contribution for conserved massless quark
currents. The full model also allows Yukawa quark exchange and neutral-scalar
s-channel diagrams, excluded here; no mixed photon diagram contributes. This is
not a claim for the full-model inclusive unequal-pair cross section.

`module8.run_capture` launches the real generated executable, captures original
and normalized cards, native results, event banners/output, logs, source/matrix
manifests, full D4 bytes, UFO audit, PDF grid and generator archives with SHA256.
`module8.real_run_validation` independently verifies these artifacts, actual
energy/scales/PDF, zero external widths, both charges/beam orders, banner agreement,
finite integration statistics and the independent amplitude/convolution gates.
It rehashes the retained launcher, generator archive and immutable generated
matrix/source files against the captured inputs. Generated run_card.inc and
param_card.inc constants change between spectra and are checked through active
banner cards; integration .dat files are historical manifest entries only.
Madevent resets the on-disk seed to zero after execution; the validator requires
actual banner seed 4154 against the original card. Hashes bind the full D4 ledger,
not just the displayed BR rows. No arithmetic test can grant generator PASS.
Native results have finite printed precision; BR multiplication adds no physics precision.

## Conditional decays and publication decision

Across the exact twelve D4 families, BR2(H1Z)×BR1(tb) ranges
**0.776529026347–0.817638084189**;
BR2(H1Z)×BR1(tb)² ranges
**0.774061538641–0.813770411038**.
P1 gives t anti-t b anti-b Z and contains two H1 decays. P2 gives t anti-t b Z
or t anti-t anti-b Z and retains the associated top; the PDF bottom remnant is
not a resolved final-state spectator. Optional 4FS would add an explicit spectator
bottom. No Z/top/W BR, detector acceptance, shower, background or exclusion enters.
D4 BRs are on-shell tree two-body values, not NLO physical decay probabilities.
Conditional rate errors rescale integration errors only and assign no BR theory
uncertainty. They use the fixed D4 daughter-scale Yukawa inputs for decay and the
700 GeV Yukawa inputs for hard production; no extra charge factor is applied.

[The literature decision](PRIOR_ART.md) records the 2021 tbH/cascade precedent,
the 2017 general-Zee flavor scan, and the 2025 charged-scalar DY/mixing analysis.
These LO rates do not establish signal novelty or measurable discrimination of
D4's minute family differences. A useful first paper requires new constrained
neutrino/LFV flavor–collider correlations. No discovery or exclusion claim follows.

## Reproduction and scoped verification

Use a fresh clone on feature/zee-d5-parton-production from the verified D4 base.
Install only the named official sources into ignored local/, download the named
central PDF .info/member-0000 files and pdfsets.index, and compile pdf_bridge.cc
against that local LHAPDF. Native export refuses existing output directories.
The process generator writes executable cards into local/ using audited names.
The original captures used the GitHub tag source; the helper uses its verified
equivalent official release. Both archives must retain their recorded names
MG5_v3.6.7.tar.gz and MG5_release_v3.6.7.tar.gz. The independent MG checker imports
the extracted GitHub directory mg5amcnlo-mg5amcnlo-0e6c945 under local/.
These are reproduction steps for fresh outputs; validation of retained runs starts
with real_run_validation and does not regenerate their directories.

```sh
math -script scripts/zee_d5_export.m
python -m module8.ufo_audit
python -m module8.generate_processes
python -m module8.run_capture P1 source d5_v2_source
python -m module8.run_capture P2 source d5_v2_source
# Execute the source matrix/convolution checks before the shifted spectra.
python -m module8.mg_matrix_checks
python -m module8.partonic_checks
python -m module8.run_capture P1 mH1_m50p0 d5_v2_low
python -m module8.run_capture P2 mH1_m50p0 d5_v2_low
python -m module8.run_capture P1 mH1_p50p0 d5_v2_high
python -m module8.run_capture P2 mH1_p50p0 d5_v2_high
python -m module8.real_run_validation
python -m unittest discover -s tests -p 'test_module8_production_composition.py' -v
python -m unittest discover -s tests -p 'test_module8_*.py' -v
python -m module8.build_report
git diff --check
```

**11 scoped tests pass**, including **7 required arithmetic tests** plus new
energy/PDF/scale/cut/LHA-duplicate and analytical-threshold/mixing falsifiers.
An executable-source mutation test confirms that a valid historical manifest
cannot conceal a modified retained matrix source.
Arithmetic fixes reject 14 TeV inputs, duplicated spectrum/family tuples with
unique IDs, and nonzero errors on zero central rates. Raw logs and huge generator
outputs stay ignored. Compact evidence and all source hashes are in
[the D5 ledger](../validation/module8/d5_production.json).
