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
a third-party library is an acceptable substitute. Obtain the source
from KIT's **TTP12-029 -> Source** listing; if it downloads an archive,
extract the original `c2HDM.m` to

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
