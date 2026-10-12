# Gate A1P — independent HEPfit Type-II LO/NLO/NNLO matching benchmark

**Scope:** Independent matching-level comparison for the Type-II charged-Higgs
contributions to B -> Xs gamma at 300, 700, 1000 and 2000 GeV.
**Not** a complete independent NNLO branching-ratio prediction, and
**not** a Zee benchmark exclusion.

## Literature and independent reference

Thomas Hermann, Mikołaj Misiak and Matthias Steinhauser,
[arXiv:1208.2788](https://arxiv.org/abs/1208.2788),
JHEP 11 (2012) 036, computed three-loop charged-Higgs matching.
The HEPfit Collaboration independently implements the Type-II
LO/NLO/NNLO Wilson coefficients in THDMMatching::setWCbsg:
https://github.com/silvest/HEPfit/blob/master/THDM/src/THDMMatching.cpp.

HEPfit indices 6 and 7 in its 0-based Misiak operator basis
correspond to C7 and C8. We compare C7 and C8 at all three orders,
C4 at NLO, and C3-C6 at NNLO: **44 comparisons** over four masses.

HEPfit's code is GPL. Gate A1P fetches only the original source file
at runtime under the ignored work/ folder, pins its Git blob to
8029be52c3e2f83490dfe3199f80e5db484dd23b, extracts the
unaltered upstream method, and generates a small self-contained
C++ test harness linked to GSL. The original third-party source
is not copied into this Zee GitHub repository.
See upstream HEPfit doc/COPYING for terms.

This procedure constitutes an independent **matching formula**
implementation, not an independent RG or inclusive decay-rate code.

## Inputs, conventions and caveats

- Frozen Type-II Yukawa texture: lambda_u=cot(beta),
  lambda_d=-tan(beta); beta=1.394 radians.
- muW=2*mW=160.7384 GeV.
- Candidate running mt(muW)=163.10709645657502 GeV. **Important:
  this number was inferred from SuperIso LO C7 matching**, and
  has NOT been independently checked against SuperIso's
  running-top prescription. All NLO/NNLO coefficient comparisons
  at this stage are conditional on that common mass input.
- The A1M isolated SuperIso 5.0 library includes the confirmed
  four-line NLO clipping correction. The official vendor tree
  is not modified.
- HEPfit original values and A1M charged-Higgs delta coefficients
  are compared at the same parameters and on the same Ci^(n)
  basis, before multiplication by powers of alpha_s/(4 pi).
- The SuperIso A1L driver is run at gamma=0, so the light
  charged Higgs contribution is the pure Type-II limit.
- Pilot comparison tolerances: LO abs 1e-7 / rel 1e-6;
  NLO abs 0.002 / rel 0.5%; NNLO abs 0.35 / rel 3%.
  **These exploratory tolerances are not publication-level
  precision standards**. Every NNLO residual exceeding 1% relative
  (when its coefficient magnitude exceeds 1e-3) is separately
  recorded as a precision-review flag, even if the broad pilot
  tolerance technically passes. Any discrepancy must be audited
  for scheme and NNLO expansion differences before final validation.

## AF run

Requires Python, GNU C/C++, curl, GSL headers/library, and the
existing Gate A1M source and static library. Activate a CERN LCG
view providing GSL if the host C++ environment lacks it.

    cd /home/aalida/zee
    git fetch origin gateA1p-independent-hepfit-typeii-matching
    git switch gateA1p-independent-hepfit-typeii-matching

    python3 -m unittest discover -s tests \
      -p 'test_gateA1p_hepfit_typeii_matching.py' -v

    bash scripts/gateA1p_run_hepfit_matching.sh \
      /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
      work/gateA1p_hepfit_typeii_v1

    cat work/gateA1p_hepfit_typeii_v1/result.json

Runner provenance: SHA for original HEPfit source and generated
reference, build logs, standalone ref program output per mass,
SuperIso A1M matching program output per mass, comparison JSON,
and source/binary hashes.

To verify the actual SuperIso mt(muW) before a stronger physics
claim, inspect the top running-mass expression in the audited
SuperIso src/wilson.c. Once verified, rerun in a fresh output
directory with this optional environment variable:

    GATE_A1P_MT_MUW_GEV=<verified_mt_muW> \
      bash scripts/gateA1p_run_hepfit_matching.sh \
      /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
      work/gateA1p_hepfit_typeii_verified_mass

The comparator writes a result JSON and returns a nonzero status
when matching differences exceed the tolerances. Do not silence
mismatches with an undocumented common scale factor.

## AF recovery: reference compiled, runtime GSL missing

The first AF attempt successfully downloaded and SHA-validated the
HEPfit source and compiled the C++ reference, but execution stopped
with:

    ./hepfit_matching: error while loading shared libraries:
    libgsl.so.28: cannot open shared object file

This is a missing **runtime loader search path** for the linked GSL
SONAME, not a physics result. The generated matching executable and
source are already present, so do **not** rerun source preparation
into the original output directory.

The repair is in
`scripts/gateA1p_resume_hepfit_matching.sh`: it checks the same
pinned HEPfit source/provenance, detects the exact GSL SONAME,
searches the GSL pkg-config package location, gsl-config prefix,
compiler paths and inherited library paths, then sets an
environment-scoped LD_LIBRARY_PATH. It refuses missing dependencies
rather than replacing the GSL formula with a different implementation.

The new runner also compiles
`gateA1p_superiso_top_mass.c` against the same A1M SuperIso library,
evaluating **the actual function from wilson.c:1599**:

    running_mass(param->mtmt, param->mtmt, mu_W,
                 param->mass_top_pole, param->mass_b, param)

This measured value replaces the provisional LO-inferred
163.10709645657502 GeV value in the independent HEPfit matching
program. The old and new values are compared in a separate
`mass_input_provenance.json` file.

Run on the **existing AF directory**:

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only

bash scripts/gateA1p_resume_hepfit_matching.sh \
  /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
  work/gateA1p_hepfit_typeii_v1

cat work/gateA1p_hepfit_typeii_v1/mass_input_provenance.json
cat work/gateA1p_hepfit_typeii_v1/result.json
```

If the required exact SONAME remains missing in the configured
library roots, first inspect:

```bash
ldd work/gateA1p_hepfit_typeii_v1/hepfit_matching
pkg-config --variable=libdir gsl
pkg-config --libs gsl
```

Find the directory containing the required `libgsl.so.28` and
pass it to the same resume command as:

```bash
GATE_A1P_GSL_LIBDIR=/absolute/directory/containing/libgsl.so.28 \
  bash scripts/gateA1p_resume_hepfit_matching.sh \
  /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
  work/gateA1p_hepfit_typeii_v1
```

The code requires the matching **real** GSL SONAME and does not
substitute a symlink to a mismatched ABI. The upstream HEPfit matching
formulas are not modified.

## AF GSL -> OpenBLAS loader follow-up (19:05)

The AF runtime check resolved the exact GSL SONAME:
`libgsl.so.28` from the Key4hep 2026-02-01 GCC 14.2.0 build.
The next missing transitive library is `libopenblas.so.0`, even
though the loader output identifies its real installation:

```text
/cvmfs/sw.hsf.org/key4hep/releases/2026-02-01/x86_64-almalinux9-gcc14.2.0-opt/openblas/0.3.30-fvauzm/lib/libopenblas.so.0
```

The continuation runner now resolves **both** exact libraries
from the same architecture/release build, checks all remaining
shared-library dependencies, and writes
`hepfit_runtime_library_paths.txt` and
`hepfit_runtime_ldd.log`. It does not relink or alter the
original HEPfit formulas. The previous run stopped before writing
the top mass or coefficient-comparison JSON.

Use the **same** existing source/executable output directory
(no re-download or A1M rebuild):

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only

GATE_A1P_OPENBLAS_LIBDIR=/cvmfs/sw.hsf.org/key4hep/releases/2026-02-01/x86_64-almalinux9-gcc14.2.0-opt/openblas/0.3.30-fvauzm/lib \
bash scripts/gateA1p_resume_hepfit_matching.sh \
  /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
  work/gateA1p_hepfit_typeii_v1

cat work/gateA1p_hepfit_typeii_v1/mass_input_provenance.json
cat work/gateA1p_hepfit_typeii_v1/result.json
```

The explicit OpenBLAS path is optional if automatic discovery
succeeds; it is recommended in this AF environment because the
path was established by the actual loader report. If the loader
still fails, inspect the saved final ldd log before changing
any scientific settings.

## AF independent comparison: 44 rows, genuine NNLO discrepancies

The independent AF run now reaches all 44 comparisons. The exact
running top from SuperIso is `163.10709645657508 GeV`, differing
from the previous LO-inferred value by `5.68e-14 GeV`. The LO and
NLO charged-Higgs Wilson coefficients reproduce independent HEPfit
to machine precision at 300, 700, 1000, and 2000 GeV.

However, the old output `INDEPENDENT_HEPFIT_MATCHING_PILOT_WITH_NNLO_PRECISION_FLAGS`
had **13 serious NNLO precision flags but zero failures**, solely
because its NNLO pilot absolute tolerance was an excessive 0.35.
This could be misread as a successful NNLO physics validation.

Observed NNLO differences (SuperIso minus HEPfit):
- 300 GeV: C3=-0.00748607, C4=+0.01826369,
  C7=-0.02254191, C8=-0.04409420 (4.66% relative C8).
- 700 GeV: C3=-0.00733374, C4=+0.02278235,
  C7=+0.00047316, C8=-0.03832802 (1.29% relative C8).
- 1000 GeV: C3=-0.00580022, C4=+0.01929193,
  C7=+0.00025675, C8=-0.02784503.
- 2000 GeV: C3=-0.00299341, C4=+0.01091455,
  C7=-0.00004363, C8=-0.01259418.

At **all four masses** we independently verified:

    ΔC5^(2) = -ΔC3^(2)/10
    ΔC6^(2) = -3 ΔC3^(2)/16

(to numerical precision, where Δ means SuperIso minus HEPfit).
The C5 and C6 differences are thus downstream algebraic
consequences of the C3 difference. The independent discrepancies
to audit are C3, C4, and the dipole remainders at NNLO.

The A1P checker now reports
`INDEPENDENT_HEPFIT_NNLO_DISCREPANCIES_BLOCK_PHYSICS_VALIDATION`
with **nonzero** exit status for any >1% flagged NNLO
coefficient, even when the exploratory tolerance count is zero.
It does **not** rescale/patch any physical coefficient. A new
source-only postprocessor reads the already completed A1P
`result.json`, displays the C3->C5/C6 identities and source
lines in both source files, verifies hashes, and writes
`nnlo_diagnostic.json` and `nnlo_matching_source_excerpts.txt`.

No library rebuild or HEPfit rerun is needed:

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_gateA1p_nnlo_discrepancy_diagnosis.py' -v
python3 scripts/gateA1p_diagnose_nnlo_discrepancies.py \
  --existing-result work/gateA1p_hepfit_typeii_v1/result.json \
  --superiso-a1m-source work/gateA1m_isolated_nlo_v1/isolated_superiso/src/wilson.c \
  --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
  --hepfit-source work/gateA1p_hepfit_typeii_v1/HEPfit_THDMMatching.cpp \
  --hepfit-provenance work/gateA1p_hepfit_typeii_v1/hepfit_provenance.json \
  --output work/gateA1p_hepfit_typeii_v1/nnlo_diagnostic.json \
  --source-excerpts work/gateA1p_hepfit_typeii_v1/nnlo_matching_source_excerpts.txt

cat work/gateA1p_hepfit_typeii_v1/nnlo_diagnostic.json
cat work/gateA1p_hepfit_typeii_v1/nnlo_matching_source_excerpts.txt
```

The excerpts allow checking exact v5 C3/C4 terms and
HEPfit's independent analytic expressions without changing
either vendor source. Relative mismatch alone does not imply
a large change in the final observable: all coefficients are
defined at their perturbative order and their contributions
carry powers of alpha_s/(4 pi). Conversely, small absolute
numbers do not excuse lack of matching validation.

**Status: NNLO matching unresolved; physical BR and Zee
allowed/excluded decisions remain blocked.**

## Independent external physics validation STILL necessary

1. Check exact top-mass scheme and scale, basis and perturbative
   normalization across both implementations; repeat matching
   around NNLO interpolation boundaries.
2. Obtain a **full independent Type-II NNLO B -> Xs gamma curve**
   (with documented SM masses, alpha_s, photon-energy threshold,
   nonperturbative terms, QCD evolution and uncertainties).
   Matching-only agreement does not verify a final branching ratio.
3. Check all primed coefficients and contributions outside the
   projected quark sector of the Zee model.
4. Quantify matching/low-scale variations, experimental averages,
   and correlated theory uncertainties before deriving exclusions.

Misiak and Steinhauser, [arXiv:1702.04571](https://arxiv.org/abs/1702.04571),
EPJC 77 (2017) 201, report Type-II 95%-CL lower mass bounds
570–800 GeV depending on statistical construction (583 GeV
conservative two-sided). Those bounds are **not** a numeric
rate reference and cannot be imposed directly on the mixed
two-charged-state Zee model.

**Status: independent Type-II matching test created, AF execution
pending; Zee BR remains a provisional candidate.**
