## NEXT GATE: independent NUMERICAL original Mathematica comparison

The static source adjudication on AF passed:

    STATUS GATE_A1Q_ORIGINAL_C3_C4_LOG_ARGUMENT_AND_C8_SIGN_STATIC_MATCH_CONFIRMED
    AUTHOR_FORMULA cH[2,3] line 168
    AUTHOR_FORMULA cH[2,4] line 178
    AUTHOR_FORMULA cHeff[2,7] line 756
    AUTHOR_FORMULA cHeff[2,8] line 757
    ORIGINAL_C3_C4_LOG Log[mu^2/mt^2]
    ORIGINAL_C8_C5_SIGN 20
    HEPFIT_C8_C5_SIGN -20
    NNLO_VALIDATED False

This settles the source-level *log argument* and C8 effective
rotation coefficient, NOT the full numerical matching.

**NEW numeric comparator** added to this branch, with
scripts/gateA1q_eval_authors.wls (original Mathematica evaluator),
scripts/gateA1q_compare_original_mathematica.py (source-provenance,
original-input and basis checks, runnable on AF), and eight offline
regression tests.

The Wolfram evaluator loads the ORIGINAL exact SHA256 c2HDM.m with
Get[] and uses independent input values from the existing 44-row
A1P matching comparison, rather than copying library formulas.
It uses exact decimal-rational inputs and

    Au = AuC = cot(beta)
    Ad = AdC = -tan(beta)
    r = mt(muW)^2 / mH^2
    u = 1 - 1/r
    ubar = 1 - r

with unchanged muW and running mt(muW). It evaluates at
mH = 300, 700, 1000, 2000 GeV:

    LO:   cHeff[0,7/8]
    NLO:  cHeff[1,7/8]
    NNLO: cH[2,3/4/5/6], cHeff[2,7/8]
    raw NNLO dipoles: cH[3,7/8]

Thus 12 original-source coefficients per mass, 48 total.
The original authors' effective basis is compared with

    SI_C7eff = SI_raw_C7 + y_j SI_Cj
    SI_C8eff = SI_raw_C8 + z_j SI_Cj
    HF_C7eff = HF_C7_returned
    HF_C8eff = HF_C8_returned + 40*HF_C5 at NNLO

because HEPfit's actual C8 source rotation uses
z5=-20, while the authors and SuperIso use z5=+20.
The HEPfit direct dipole checks undo the appropriate actual
source rotation. The authors' original inverse-QCD-coupling
dipole operator normalization is accounted for by comparing
only the README-defined effective coefficients of the SAME
perturbative order (and treating raw three-loop dipoles
separately, with their explicit loop-index mapping).

**Run now on the AF:**

~~~bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only

python3 -m unittest discover -s tests \
  -p 'test_gateA1q_compare_original_mathematica.py' -v

python3 scripts/gateA1q_compare_original_mathematica.py \
  --authors-source work/gateA1q_original_nnlo_v1/c2HDM.m \
  --kit-provenance work/gateA1q_original_nnlo_v1/kit_source_provenance.json \
  --existing-result work/gateA1p_hepfit_typeii_v1/result.json \
  --output-dir work/gateA1q_original_nnlo_v1
~~~

If the AF has a working wolframscript executable, this
creates original_mathematica_values.txt and
original_vs_A1P_NNLO_numeric.json. Otherwise the runner
explicitly reports A1Q_WOLFRAMSCRIPT_UNAVAILABLE.
To prepare a portable exact input set without evaluation:

~~~bash
python3 scripts/gateA1q_compare_original_mathematica.py \
  --authors-source work/gateA1q_original_nnlo_v1/c2HDM.m \
  --kit-provenance work/gateA1q_original_nnlo_v1/kit_source_provenance.json \
  --existing-result work/gateA1p_hepfit_typeii_v1/result.json \
  --output-dir work/gateA1q_original_nnlo_v1 --prepare-only
~~~

Transfer source c2HDM.m, exact JSON input and the project
Wolfram .wls file to a machine with licensed Mathematica 15.
Run the printed wolframscript -file ... command there, then
copy only original_mathematica_values.txt to AF and run
the normal command with

    --authors-values work/gateA1q_original_nnlo_v1/original_mathematica_values.txt

If Wolfram evaluation errors or unresolved symbols appear,
preserve them; do NOT relabel them as matching discrepancies.
The raw numeric output contains strictly tagged records
and the Python comparison refuses missing, duplicate, extra
or nonfinite author values.

The result status
GATE_A1Q_ORIGINAL_MATHEMATICA_NUMERICALLY_COMPARED_NOT_BR_VALIDATED
means a numerical comparison was completed; it does NOT
prejudge whether implementations agree. Source tests and
the numerical run must be checked before assigning a stricter
matching pass/fail verdict. Publication-grade flavour
constraints still require calibrated complete BR and uncertainty.

## AUTHOR-SOURCE GATE A1Q: C3/C4 logarithm and C8 sign decided in original code

The user executed the exact official KIT c2HDM.m source inspector on AF:

    OK
    ORIGINAL_KIT_SHA256_CONFIRMED cb2d1328bc2542a6324e73efe6f89c43381efdc93db5e3b0ca8348db980645d8
    SOURCE_EXPRESSION C3_NNLO found 1 lines 168
    SOURCE_EXPRESSION C4_NNLO found 1 lines 178
    SOURCE_EXPRESSION C7_NNLO_effective found 1 lines 756
    SOURCE_EXPRESSION C8_NNLO_effective found 1 lines 757
    SOURCE_EXPRESSION C8_NNLO_raw found 1 lines 742
    FULL_NNLO_MATCHING_VALIDATED False

**Important original-source evidence:**

- cH[2,3] (line 168) and cH[2,4] (line 178) contain literal
  Mathematica logarithms Log[mu^2/mt^2]. HEPfit's source uses
  lstmu=2*log(mu/mt), while SuperIso A1M instead writes the
  NNLO C3/C4 coefficient multiplying log((mu_W/mass_H)^2),
  with the previously measured sign relation. Therefore the
  **scale-log argument** in HEPfit agrees with the original author,
  but the numerical sign/normalization of the complete coefficients
  still requires an actual Mathematica evaluation and basis check.

- cHeff[2,8] at line 757, **verbatim**:

      cHeff[2,8] = ( cH[3,8] + cH[2,3] - 1/6*cH[2,4] + 20*cH[2,5] - 10/3*cH[2,6] ) ;

  The original author thus unambiguously applies +20*cH[2,5]
  in its effective chromomagnetic combination. This agrees with
  the effective basis in SuperIso A1M and disagrees with the
  **-20*C5 term** in the corresponding HEPfit NNLO source
  assignment. This is a concrete **source-level implementation
  inconsistency** in HEPfit that should be independently numerically
  tested before making an upstream bug report or modifying its code.

- cHeff[2,7] at line 756 uses the standard vector
  -1/3*C3 -4/9*C4 -20/3*C5 -80/9*C6, consistent in both
  libraries after basis mapping.

- The original cH[3,8] at line 742 contains piecewise three-loop
  expansions with mass ratio r. A static symbolic listing is not a
  numerical validation of the expansion or physical branching ratio.

**NEW fail-closed static source adjudicator:**

~~~bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_gateA1q_adjudicate_original_source.py' -v

python3 scripts/gateA1q_adjudicate_original_source.py \
  --authors-source work/gateA1q_original_nnlo_v1/c2HDM.m \
  --kit-provenance work/gateA1q_original_nnlo_v1/kit_source_provenance.json \
  --superiso-source work/gateA1m_isolated_nlo_v1/isolated_superiso/src/wilson.c \
  --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
  --hepfit-source work/gateA1p_hepfit_typeii_v1/HEPfit_THDMMatching.cpp \
  --hepfit-provenance work/gateA1p_hepfit_typeii_v1/hepfit_provenance.json \
  --output work/gateA1q_original_nnlo_v1/original_vs_implementations_static.json
~~~

Expected:

    STATUS GATE_A1Q_ORIGINAL_C3_C4_LOG_ARGUMENT_AND_C8_SIGN_STATIC_MATCH_CONFIRMED
    ORIGINAL_C3_C4_LOG Log[mu^2/mt^2]
    ORIGINAL_C8_C5_SIGN 20
    HEPFIT_C8_C5_SIGN -20
    NNLO_VALIDATED False

Seven new tests verify both original logarithms, +20 sign,
comment/duplicate robustness, opposite-sign rejection and
mandatory source provenance. **The test suite has not yet run
on AF.**

**Next:** Independent numerical Wolfram evaluation of original
c2HDM.m at fixed mass/scale and Type-II quark Yukawas. Original
symbolic functions use Au, AuC, Ad, r, mu and mt; evaluate with
documented parameter replacements, check output reality, and
match loop/order normalization to original paper Eq. (3).
Only after numerical closure can Gate A1Q be called a full
NNLO matching pass or used for observable-level validation.

## AF ORIGINAL c2HDM.m FETCH SUCCESS — authenticate and inspect formulas

**KIT authoritative source was obtained on the AF**, reported:

    STATUS GATE_A1Q_KIT_ORIGINAL_SOURCE_FETCHED_NOT_EVALUATED
    AUTHOR_SOURCE_URL https://www.ttp.kit.edu/Progdata/ttp12/ttp12-029/c2HDM.m
    C2HDM_SHA256 cb2d1328bc2542a6324e73efe6f89c43381efdc93db5e3b0ca8348db980645d8

This fully clears **source acquisition**, NOT Mathematica evaluation or
NNLO matching/physical BR verification. The original source must remain
on the AF in the uncommitted work/ directory.

The new read-only inspector, introduced after AF source acquisition,
pins the EXACT original SHA256 above, checks the original KIT URL
against kit_source_provenance.json and extracts source assignments for

    cH[2,3], cH[2,4], cHeff[2,7], cHeff[2,8], cH[3,8].

It carefully removes nested Mathematica comments/strings before finding
literal assignments, records source locations and short unmodified
formula excerpts, and lists occurrences of Log, mu, mt, r, ubar,
and three-loop expansion functions. A literal-assignment match is
static *source evidence*, not a proof of mathematical equivalence.
If the source uses general rules rather than literal assignments,
the missing-expression flag must not be interpreted as missing physics.

**Run on AF using the source ALREADY downloaded; no refetch/build:**

~~~bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only

python3 -m unittest discover -s tests \
  -p 'test_gateA1q_inspect_original_mathematica.py' -v

python3 scripts/gateA1q_inspect_original_mathematica.py \
  --authors-source work/gateA1q_original_nnlo_v1/c2HDM.m \
  --kit-provenance work/gateA1q_original_nnlo_v1/kit_source_provenance.json \
  --output work/gateA1q_original_nnlo_v1/source_formula_inspection.json
~~~

Expected result:

    GATE_A1Q_ORIGINAL_SOURCE_AUTHENTICATED_STATIC_INSPECTION_NO_NNLO_PASS

The inspector prints the relevant source line numbers and first 220
characters of definitions, with complete excerpts (capped at 1300
characters per assignment) in source_formula_inspection.json.
Share the console output and, if needed, relevant source excerpts
for an exact Wolfram numerical cross-check. It intentionally does
not copy the complete external Mathematica implementation into git.

**Next hard physics gate:** Independently numerically evaluate the
*original* c2HDM.m Wilson coefficients, including exact mapping
of original P7/P8 inverse-alpha_s normalization to the coefficients
used by HEPfit and SuperIso. Compare C3/C4 logs and C8 +20*C5
with absolute benchmark values and controlled scale variation.
No matching patch/exclusion until this gate is passed.

# Gate A1Q — original 2012 NNLO theory reference

## Purpose / current status

**STATUS: BLOCKED — the original c2HDM.m file has not been independently
retrieved and its expressions have NOT been evaluated.** This is an
intentionally hard scientific gate, not a software malfunction.

Gate A1P established source-hashed LO/NLO cross-checks, localized
C3/C4 NNLO log differences analytically, found HEPfit's unusual
NNLO chromomagnetic `-20*C5` term, and explained the small
C7/C8 finite-polynomial differences by differing decimal precision.
None of those results alone establishes the physically correct full
NNLO matching or the full branching ratio.

## Original primary sources

- Hermann, Misiak, Steinhauser, *Bbar -> Xs gamma in the 2HDM up to NNLO*,
  arXiv:1208.2788v2, [HTML](https://arxiv.org/html/1208.2788).
- Official KIT TTP12-029 supplementary
  [readme.pdf](https://www.ttp.kit.edu/Progdata/ttp12/ttp12-029/readme.pdf).
- Official KIT [Programs and Data catalogue](https://www.ttp.kit.edu/progdata),
  entry **TTP12-029** with a **Source** link to the original
  Mathematica supplementary material (file `c2HDM.m`).

The 2012 paper Section 2.1, Eq. (3) uses matching coefficients
C_i^(H,n) with the original dipole operators normalized using
inverse QCD coupling powers. The authors' README explicitly defines

    C7_eff = (4*pi/alpha_s) * C7 + sum_{j=1..6} y_j C_j
    C8_eff = (4*pi/alpha_s) * C8 + sum_{j=1..6} z_j C_j

with

    y = (0,0,-1/3,-4/9,-20/3,-80/9)
    z = (0,0, +1,-1/6, +20,-10/3)

and r=mt(mu0)^2/MH^2, ubar=1-r.

In HEPfit's pinned THDMMatching::setWCbsg source, the NNLO C8
coefficient adds **-20 * C5**, in apparent contradiction to
the author's documented standard effective definition **+20 * C5**.
SuperIso's C_calculator_base1 applies **+20 * C5**. Before treating
this as a physics bug, the original author's full coefficient
definitions and perturbative normalization must be evaluated.

For C3/C4, HEPfit uses

    C_i^(2)_HEPfit = [n_i(r) + d_i(r)*ln(mu0^2/mt(mu0)^2)]/tanbeta^2

while pinned SuperIso A1M uses

    C_i^(2)_SI = [n_i(r) - d_i(r)*ln(mu0^2/MH^2)]/tanbeta^2.

The eight A1P differences are numerically identical to the
analytic predicted difference to 4.2e-16. **The original 2012
source, not agreement between the two implementations, must
adjudicate the correct log scale and sign.**

## Source intake protocol

The author `c2HDM.m` file is **not yet available in this repository
or via the present retrieval interface**. No code reconstructed from
a third-party library is an acceptable substitute. The official
[KIT catalogue](https://www.ttp.kit.edu/progdata) lists
**TTP12-029 -> Source**. Direct retrieval was blocked in the chat-side
web interface, but the AF can independently resolve and download the
actual official link using the NEW vetted intake tool:

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
python3 -m unittest discover -s tests \
    -p 'test_gateA1q_fetch_kit_source.py' -v
python3 scripts/gateA1q_fetch_kit_source.py \
    --output-dir work/gateA1q_original_nnlo_v1
cat work/gateA1q_original_nnlo_v1/kit_source_provenance.json
```

The script parses the Source hyperlink specifically under TTP12-029
rather than guessing filenames, follows ONLY HTTPS URLs on the
official KIT TTP domain, processes TAR/ZIP/GZIP/Mathematica bytes in
memory without extracting arbitrary archive paths, checks the expected
original Mathematica symbol names, and writes the source alongside
an archive/original-file SHA256 provenance manifest. It does NOT
claim numerical NNLO matching verification. There are ten offline
retrieval/parser regression tests (not yet run on AF).

If the new official catalogue responds with HTTP 403 or cannot
identify the source hyperlink, the retrieval script falls back to
the **official TTP12-029 supplementary directory** documented by
the public README location. It enumerates the actual directory
hyperlinks to find c2HDM.m, without fabricating a filename.
If the old directory also denies access, preserve both errors and
do not replace the original with a third-party transcription.
The fallback route and original catalogue error are recorded in the
resulting provenance manifest when retrieval succeeds.

Obtain the source from KIT's **TTP12-029 -> Source** listing; if it
downloads an archive, extract the original `c2HDM.m` to

    work/gateA1q_original_nnlo_v1/c2HDM.m

Record the exact download URL, downloaded archive checksum, file
checksum, retrieval date and any archive manifest. For first intake,
use the script without the author source. Once obtained, supply
`--authors-source`, `--authors-origin-url` and optionally an
**independently verified** known SHA256. A SHA256 supplied by the
operator only pins bytes; it does NOT authenticate official origin.

**Existing pinned-source and README convention diagnostic**:

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
python3 -m unittest discover -s tests \
    -p 'test_gateA1q_author_reference_intake.py' -v

python3 scripts/gateA1q_author_reference_intake.py \
    --superiso-source work/gateA1m_isolated_nlo_v1/isolated_superiso/src/wilson.c \
    --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
    --hepfit-source work/gateA1p_hepfit_typeii_v1/HEPfit_THDMMatching.cpp \
    --hepfit-provenance work/gateA1p_hepfit_typeii_v1/hepfit_provenance.json \
    --output work/gateA1q_original_nnlo_v1/intake.json
```

Expected status with no author file:

    GATE_A1Q_BLOCKED_ORIGINAL_AUTHOR_SOURCE_NOT_SUPPLIED

When the **official archive** has been obtained, repeat with
`--authors-source work/gateA1q_original_nnlo_v1/c2HDM.m` plus
`--authors-origin-url 'ACTUAL_RESOLVED_KIT_SOURCE_URL'`.
The source-intake tool only recognizes expected Mathematica symbols,
checks content hashes and records the inherited source conventions.
It never claims the Mathematica formulas were numerically evaluated.

## Gate A1Q pass criteria (not yet satisfied)

1. Independent origin verification for original c2HDM.m and SHA256
   manifest, with the source kept outside version control or
   distributed only in accordance with source licensing.
2. Reproduce its C3/C4 NNLO values at four masses and the exact
   `mu0=160.7384 GeV`, `mt(mu0)=163.10709645657508 GeV`
   scale convention, after exact operator/basis matching.
3. Independently evaluate `cHeff[2,8]` and compare the C5
   contribution to the author's +20 definition and the
   HEPfit code's -20 at the exact same perturbative order.
4. Validate C7/C8 three-loop finite terms `cH3uuL`, `cH3duL`
   at 300, 700, 1000, 2000 GeV within declared expansion accuracy.
5. Show matched renormalization/operator conventions and
   measured numerical differences; no source patches made just to
   force agreement.

If any input or formula is missing, the gate remains BLOCKED.
Even a passed A1Q is not a full Type-II inclusive
BR(B->Xs gamma) validation and cannot authorize a Zee benchmark
allowed/excluded classification.

## Model-scope reminder

The scalar sector of a **2HDM + singly charged SU(2)-singlet**
permits H2+ -> H1+ Z. To claim the **full Zee neutrino-mass
model**, one must also specify antisymmetric LL eta+ Yukawas
and sufficient second-doublet leptonic Yukawa structure to
reproduce neutrino data. A fully restrictive Type-II Yukawa
structure in the lepton sector can coincide with the excluded
Zee-Wolfenstein neutrino texture. Type-II **quark** Yukawas
alone may be chosen in a general-Zee model, but the lepton
sector must be treated independently and consistently.
