# Executed SusHi production and HDECAY partial-width bridge — 2026-11-07

**Result: four independently validated neutral production predictions, eight
cross sections; no newly usable physical Higgs exclusion.** SusHi 1.7.0 runs
on both original D7/F13 NO/low_joint witnesses. Rebuilt anyHdecay 1.1.0 runs
its frozen HDECAY 6.60 R2HDM interface on D7. Transferable partial widths and
native Zee additions are calculated, but full Zee widths remain INCOMPLETE.
`HIGGS_FULL_COVERAGE_BLOCKED`, `physical_higgs=UNKNOWN`, `exclusion=null`,
`global_acceptance=null`; no scan is authorized.

All work is under `research/full_constraints/`. Starting HEAD was
`f44588262728c99ca2d342f438c04c8651924ad5` on
`research/zee-full-constraints`. The frozen `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`
object remains present and unchanged. Modules0–13, D14 sources, saved
collections, production maps and historical receipts were not edited.
B and LFV retain their independent BLOCKED gates. The HEPfit rate task is
queued, not canceled or executed in this session.

## Executed production

All cross sections are inclusive **pp at 13,000 GeV**, in pb. These are QCD
LO results: coherent massive t,b,c loops for ggF and 5FS bottom annihilation
for bbH. Electroweak corrections are disabled. They are independent public-code
calculations, not reused MG5 numbers or tabulated ScannerS rates.

| Card/state | Mass [GeV] | ggF [pb] | Numerical integration error [pb] | bbH [pb] | Numerical integration error [pb] |
| --- | ---: | ---: | ---: | ---: | ---: |
| D7 H | 492.430783100 | 2.32581373 | 1.21866e−6 | 0.00284816445 | 2.04892e−9 |
| D7 A | 493.161317402 | 4.06750239 | 2.13153e−6 | 0.00309843975 | 2.22851e−9 |
| F13 H | 707.081937864 | 0.0159280599 | 8.55250e−9 | 0.0138685780 | 9.35326e−9 |
| F13 A | 792.259349963 | 0.0146694072 | 7.77352e−9 | 0.00802913282 | 5.31643e−9 |

PDF: **MMHT2014lo68cl**, data version 3, central member 0, ID 25000,
five active flavours, αs(MZ)=0.135. The downloaded official PDF archive
matches **every installed file** byte for byte. SusHi runs αs at one loop
from the PDF's MZ normalization, rather than interpolating the PDF's tabulated
αs at the process scale. Central ggF μR=μF=M/2; central bbH μR=M, μF=M/4.
The actual αs(μR), reconstructed cards and output parameters are retained.

ggF uses mt(pole)=172.4 GeV and OS mb=4.78 GeV for both the bottom Yukawa
and loop propagator (`RENORMBOT 1=0, 4=4.78`). Charm input is
mc(mc)=1.273 GeV; SusHi's native conversion gives **mc(pole)=3.20168553 GeV**
with this LO PDF/αs choice. This large scheme conversion is exposed, not
replaced silently by 1.273 in the independent comparison. bbH instead uses
MSbar mb(mb)=4.183 GeV evolved at one loop with nf=5 to μR;
mb(μR)=2.54321103, 2.54295750, 2.48343830, 2.46547734 GeV in table order.
The normalization uses GF=1/(sqrt(2) v²), v=246.21965 GeV.
SMINPUTS' inverse electromagnetic coupling is 137.035999084; SusHi's derived
MW=81.5528202 GeV does not enter these pure-QCD rates and is **not** transferred
to the native EW/decay scheme (MW=80.379 GeV).

SusHi includes c,t,b in this configuration. The u,d,s amplitude diagnostic,
using the frozen D4 light reference masses at this same LO normalization,
shifts ggF by +1.115e−5, −2.734e−6, +9.568e−5 and +1.067e−4 respectively.
These are recorded omissions at the scoped CTB accuracy, not an unqualified
full-loop claim or a rigorous higher-order materiality bound.

## Yukawa and CP matching

Native ZH rows are `(cos a,sin a),(-sin a,cos a)` and the physical ZA row is
`(-sin b,cos b)`. SusHi uses `(-sin aS,cos aS),(cos aS,sin aS)`.
**aS=a+π/2** preserves the native H and rephases h by −1. A is not rephased.
With `L=−S qbar(C PL+C* PR)q`, native `C_A=+i (m_q/v) kappa_A`:

| Card | kappa_Ht | kappa_Hb | kappa_At | kappa_Ab |
| --- | ---: | ---: | ---: | ---: |
| D7 | +0.943353397891 | −1.066319901771 | +0.896276702518 | +1.115726870051 |
| F13 | +0.185948166778 | −5.310190292356 | +0.188403702414 | +5.307751319043 |

Fresh SARAH 4.15.4 extraction evaluates both PL/PR quark vertices, both
charged-W vertices, Hhh and AhZ on the **two original saved cards**.
All 28 signed complex coefficients agree with independent model expressions;
maximum absolute residual 1.84742e−13. SusHi's executed `HGGSUSY` values
also match these normalized quark vertices. No charged mass eigenstate is
passed to a neutral production table. The charged singlet does not alter
these tree neutral quark vertices, but affects decay competition and higher
orders.

## Independent numerical and uncertainty checks

An independent C++/LHAPDF convolution uses Simpson integration of τLij.
The Python control uses the previously validated scalar/pseudoscalar form
factors with the actual SusHi quark schemes:

    sigma_gg = GF alpha_s²/(512 sqrt(2) pi) |sum_q kappa_q Ahalf_q|² tau Lgg
    sigma_bb = pi sqrt(2) GF/(6 M²) mb_MSbar(muR)² kappa_b² tau Lbb

The bb luminosity contains both beam orders once. ggF relative residuals
are 1.050–1.082e−6; bbH residuals 1.453–1.555e−6. Doubling quadrature
resolution changes the gg luminosity by at most 3.04e−10. Small pb-conversion
constant differences and native integration/printed precision are retained;
numerical residuals are not theory errors. Actual top-only, bottom-only,
charm-only, bottom-sign-flip and all-couplings-doubled SusHi controls pass
the complex amplitude scaling, interference and bbH square-law checks on
**each** original mass/CP assignment. Four additional executed unit-quark
coupling controls reproduce the CP-even SM quark limit or the corresponding
unit-pseudoscalar reference, with the original masses held fixed.
All four masses exceed 2mt; complex
threshold form factors are retained.

The shipped 125-GeV 2HDM example provides an additional reference assignment.
Its LO term evaluated with NLO PDFs is 10.1762262 pb. The fresh LO run with
those PDFs gives 10.1171817 pb because SusHi evolves αs at one loop for an
LO request, versus the example's NLO evolution. Explicit translation by
`(0.127396078/0.127025994)^2` gives 10.1762194014 pb, relative residual
−6.681e−7. The raw 0.58% difference is documented, not hidden as integration
error. This reference-only αs translation is not a model K factor.

Seven-point μR/μF variations are executed by SusHi at each original card;
the multipliers are (½,½),(½,1),(1,½),(1,1),(1,2),(2,1),(2,2) relative to
each process's central scales. For bbH the central absolute μR/μF is 4;
the multiplier-ratio restriction applies relative to that central choice.
All 50 MMHT Hessian error members are independently convolved at LO;
their αs values are checked equal to member 0, permitting luminosity-ratio
transfer. PDF errors below are symmetric 68% Hessian estimates,
`sqrt(sum(pair_plus−pair_minus)^2)/2`.

| Card/state | ggF scale −/+ [pb] | ggF PDF [pb] | bbH scale −/+ [pb] | bbH PDF [pb] |
| --- | ---: | ---: | ---: | ---: |
| D7 H | −0.539645 / +0.764323 | 0.0467964 | −0.000609478 / +0.000517728 | 0.0000828799 |
| D7 A | −0.943950 / +1.337072 | 0.0819182 | −0.000662304 / +0.000562457 | 0.0000902507 |
| F13 H | −0.00387558 / +0.00559641 | 0.000413582 | −0.00221850 / +0.00176247 | 0.000525431 |
| F13 A | −0.00362103 / +0.00525783 | 0.000415634 | −0.00115820 / +0.000896958 | 0.000333738 |

These are separate scale envelopes and PDF estimates, not Gaussian total
uncertainties. Parametric mt/mb/αs uncertainties, their covariance, higher-order
QCD/EW/Zee corrections and signal acceptance/line-shape uncertainties remain
unqualified. No hard exclusion is based on these central LO predictions.

## Executed HDECAY transfer and Zee additions

The public [anyHdecay interface](https://jonaswittbrodt.gitlab.io/anyhdecay/)
identifies its frozen SM/R2HDM HDECAY version as 6.60. We rebuilt commit
`137b6991cafcd32770e64b2b5979de80db1e44af`, pinning the N2HDECAY shared core
to `5233a141a82674f6adf0bce0343a808ee7bf535a` and hashing auxiliary archives
and every generated Fortran routine. The R2HDM wrapper uses NNLO=1,
three-loop αs initialization/mass evolution, nf(gg)=5, off-shell switches
IONSH=IONWZ=0, and IOELW=0. Source inspection confirms IOELW multiplies
the EW corrections: they are disabled here. This is HDECAY's channel-specific
QCD approximation, not a uniformly NNLO Zee calculation.

D7 input uses the original neutral masses, tanβ, m12², shifted angle, and
the exact charged-doublet curvature mass
`mD²=cos²γ mH1²+sin²γ mH2²`, mD=521.242316759 GeV.
This **control input** preserves the doublet potential; it is not a new
Zee spectrum or a physical replacement of its two charged states.
SM inputs: αs(MZ)=0.118, mb(mb)=4.183, mc(mc)=1.273, ms=0.0935,
mt(pole)=172.4, inverse α=137.035999084, GF from native v, MW=80.379,
MZ=91.1876; lepton masses are the frozen D4 values. W/Z widths and CKM
entries retain the pinned wrapper defaults (listed in the retained driver).
Production and decay αs choices are distinct, explicitly recorded schemes.

The rebuilt package passes **6,301 assertions at 100 shipped R2HDM reference
points**. Its old Catch harness required `CATCH_CONFIG_NO_POSIX_SIGNALS`
with current glibc; only harness compilation is changed. No physics routine
is patched.

Transferable D7 partial widths (GeV), extracted as **R2HDM BR × R2HDM total**:

| Channel | H | A |
| --- | ---: | ---: |
| tt | 10.8758512872 | 17.4903948042 |
| bb | 0.00823442796 | 0.00921460727 |
| cc | 0.000533507302 | 0.000486131688 |
| ss | 2.89515e−6 | 3.37141e−6 |
| gg | 0.0353317714 | 0.0623983970 |
| WW / ZZ | 0.0757547258 / 0.0361230680 | absent at tree CP-conserving accuracy |
| hh | 0.000608127238 | forbidden at tree scalar CP accuracy |
| hZ | absent at tree scalar CP accuracy | 0.0656930403 |

HDECAY also returns A→HZ* =2.23144e−13 GeV for this tiny D7 splitting;
it is retained. The independent derivative of the native neutral potential
and identical-h factor reproduce H→hh; the independent gauge-current formula
reproduces A→hZ. The H WW/ZZ widths divided by the executed same-mass SM
control both equal sin²(β−α)=0.00231502915314. The published-code QCD quark
widths are transferred with their complete Type-II quark couplings, including
source top/bottom terms; bb is not approximated by a universal SM rescaling.

Native D4 scalar-vector kernels, crossed to neutral parents and checked
against the fresh SARAH coefficients, give charge-summed additional widths:

| Original card | H→H1±W∓ [GeV] | A→H1±W∓ [GeV] |
| --- | ---: | ---: |
| D7 | 0.926020108092 | 0.939356739808 |
| F13 | 1.053423746950 | 6.154915041028 |

Both H2±W∓ channels and all charged-scalar pair channels are closed on shell
on these cards; actual thresholds are recorded, not inferred from absent
outputs. Diagonal and LFV lepton widths are freshly evaluated with the
original D12 **general complex** D matrix and native Module3 kernels. Each
off-diagonal lepton pair includes both charges once; diagonal channels do
not receive that factor. The Type-II HDECAY lepton widths are discarded.
Neither the R2HDM single-charged scalar γγ/Zγ loops nor its charged-W channels
are copied into the Zee sum.

The known disjoint D7 sums are **11.9584845277 GeV (H)** and
**18.5675702523 GeV (A)**. They are **not physical total widths or BR
normalizations**. The R2HDM totals 11.0337212446 and 17.6297056084 GeV are
explicitly rejected as Zee totals. R2HDM BR sums equal one; no incomplete
Zee sum is normalized to one. No library numerical error estimate is returned
for these widths; a theoretical width uncertainty has not been supplied.

Missing-width ledger: full Zee H/A γγ with both charged states and general
leptons; Zγ with mixed charged currents; consequential off-shell/finite-daughter
charged-W contributions; loop-induced A→WW/ZZ and other EW channels at the
target accuracy/materiality; omitted light u/d modes and their materiality;
order/parametric/scale uncertainties. H/A charged-pair and other closed
on-shell thresholds do not by themselves bound off-shell effects.
The existing complete leading h125 γγ result is retained and regression-tested;
its mixed-current Zγ and coherent full-width/likelihood gate remain open.
The [HDECAY paper](https://arxiv.org/abs/1801.09506) and inspected source
support this partial-width transfer, not a full Zee total-width claim.

## HiggsTools consumer gate

The evidence contains one updated status per **310 actual limit IDs for
each D7/F13 card**, plus pinned HB/HS dataset commits. Source bytes match the
previous inventory. Results remain `NOT_APPLICABLE` only where already proved;
all potentially applicable incomplete signals remain `MISSING_PREDICTION`.
**Zero complete signals are connected; zero exclusions become genuinely
usable in this milestone.** Production availability is not an analysis BR.
8-TeV rates, other production modes, h125 STXS/widths, heavy-neutral competing
widths, charged gaps, Γ/M/NWA/interference/acceptance and confidence qualification
are still required where applicable. No missing prediction becomes zero.

## Provenance, build findings and reproduction

- SusHi [official release archive](https://sushi.hepforge.org/downloads/SusHi-1.7.0.tar.gz):
  SHA256 `509b59fe56a1dbc4274871a5f84150e0ad91b61ef44908b6aa772f2d7c6a183a`.
  The homepage was access-denied, but this exact archive downloaded successfully.
- GNU Fortran 11.4.0; first compilation fails on legacy dormant fourth-generation
  real/complex call mismatches. `F77FLAGS=-fallow-argument-mismatch` compiles
  successfully, without changing Fortran source. Active 2HDM calls use complex
  arguments and pass the signed native validation. LHAPDF runtime/library and
  PDF data paths must be set explicitly. Logs retain the failed and successful build.
- LHAPDF 6.5.3 source archive SHA256
  `57435cd695e297065d53e69bd29090765c934936b6a975ff8c559766f2230359`.
  SusHi's bundled analytic integrals (`integrals=2`) need **no LoopTools**.
- Official MMHT archive SHA256
  `9586f40e3f620039f5bf082ef52281485a50c915abf44f365db87d44c896990f`.
- GPLv3 notices are present for LHAPDF and the anyHdecay wrapper; SusHi's
  top level supplies citation/use instructions without a separate license file.
  Component provenance/notices remain upstream. No third-party source or binary
  is vendored; only our adapters, generated cards, numerical outputs and logs
  are committed.

Machine evidence: [SUSHI_EVIDENCE.json](higgs/SUSHI_EVIDENCE.json).
Source and receipt digests: [SUSHI_SOURCE_MANIFEST.json](higgs/SUSHI_SOURCE_MANIFEST.json).
[SUSHI_RUNS.tar.gz](higgs/SUSHI_RUNS.tar.gz) contains 224 generated run/build/native
receipts (52 fixed-card production/control/scale executions, full reconstructed
cards, stdout, μR profiles, HDECAY output and native vertices). No scalar
proposals, scans, Condor jobs or MG5 integrations were run.

Build from the pinned archives in `/tmp/zee-sushi-execution`:

```bash
cd /tmp/zee-sushi-execution/SusHi-1.7.0
./configure
make -j2 LHAPATH=/home/amine/codes/Herwig/herwigpp/lib F77FLAGS=-fallow-argument-mismatch
```

From the repository root, with the two saved environment paths exported:

```bash
export LD_LIBRARY_PATH=/home/amine/codes/Herwig/herwigpp/lib
export LHAPDF_DATA_PATH=/home/amine/codes/Herwig/herwigpp/share/LHAPDF
g++ -O2 -std=c++17 research/full_constraints/higgs/lo_luminosity.cpp \
  -I/home/amine/codes/Herwig/herwigpp/include \
  -L/home/amine/codes/Herwig/herwigpp/lib -lLHAPDF \
  -o /tmp/zee-sushi-execution/lo_luminosity
python -m research.full_constraints.higgs.sushi_study \
  --sushi /tmp/zee-sushi-execution/SusHi-1.7.0/bin/sushi \
  --luminosity /tmp/zee-sushi-execution/lo_luminosity \
  --out /tmp/zee-sushi-execution/REPLAY
python -m unittest research.full_constraints.higgs.test_sushi \
  research.full_constraints.higgs.test_higgs -v
git diff --check
```

Use a fresh output directory: the executables reject existing run directories.
For anyHdecay, configure the pinned source checkout with the locally pinned
dependency sources; this prevents its upstream CMake from fetching unpinned
dependency heads. From the repository root:

```bash
cmake -S /tmp/zee-sushi-execution/anyhdecay-src \
  -B /tmp/zee-sushi-execution/anyhdecay-REPLAY-build \
  -DFETCHCONTENT_SOURCE_DIR_N2HDECAY=/home/amine/Tools/ScannerS/build/_deps/n2hdecay-src \
  -DFETCHCONTENT_SOURCE_DIR_C2HDM_HDECAY=/home/amine/Tools/ScannerS/build/_deps/c2hdm_hdecay-src \
  -DFETCHCONTENT_SOURCE_DIR_SHDECAY=/home/amine/Tools/ScannerS/build/_deps/shdecay-src
cmake --build /tmp/zee-sushi-execution/anyhdecay-REPLAY-build --target anyhdecay -j2
g++ -O2 -std=c++17 research/full_constraints/higgs/anyhdecay_driver.cpp \
  -I/tmp/zee-sushi-execution/anyhdecay-src/include \
  /tmp/zee-sushi-execution/anyhdecay-REPLAY-build/lib/libanyhdecay.a \
  -lgfortran -lquadmath -o /tmp/zee-sushi-execution/anyhdecay-REPLAY
/tmp/zee-sushi-execution/anyhdecay-REPLAY \
  1.115726870050509 37805.29796645005 493.16131740168134 \
  521.2423167588017 492.4307830996228 125.0 2.362705101041322 1
```

The native input JSON, source directories, driver arguments and build logs
are bound by the source manifest and raw archive. With `native_inputs.json`
restored into the work directory, the fresh native comparison is reproduced by
`ZEE_SUSHI_NATIVE_OUT=/tmp/zee-sushi-execution math -script research/full_constraints/higgs/native_sushi_vertices.m`.
**26/26 repository Higgs tests pass**, including signed/CP
and interference falsifiers, PDF/order/energy/source/scheme/mass rejection,
actual output/hash tampering, native vertex sign injection, partial-width
normalization checks and incomplete-width rejection. No B/LFV test stream
is run. These checks establish the scoped predictions above; they do not
advance the full Higgs exclusion milestone to complete.
