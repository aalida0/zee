# Gate 7: exporting Yang–Wu Zee source with Type-II quark Yukawas

**Source patch on AF**: `python3 scripts/gate7_prepare_typeii_feynrules.py`
passed. The source `models/Zee_TypeII_FR/Lagrangian.fr` now contains
`H1[ii] - Tan[beta]*H2[ii]` (down) and
`H1bar[jj] + Cot[beta]*H2bar[jj]` (up).
See upstream original model: https://github.com/YangPhy/Zee-Model

## Scope and caveats

These Higgs-basis terms implement the **Type-II quark Yukawa pattern**;
they do not alter the parent Yang–Wu scalar potential/charged mixing.
The previously reconstructed Florentino point is **not automatically
represented by the new UFO's external parameters**. In particular:

- Yang–Wu uses physical charged `H+` PDG 227 and `h+` PDG 228,
  with charged mixing `phi` in `ZEEINPUTS[4]`.
- Florentino's heavy charged state is H2± with mixing `gamma`.
  Mapping field magnitudes suggests `phi≈pi/2−gamma≈0.4818`,
  but signs and scalar trilinears must be matched independently.
- Yang–Wu contains lepton Yukawas, and the raw supplied defaults
  are NOT neutrino/LFV-calibrated: never treat unmodified widths as physical.
- NLO source artifacts in original `ZEE_NLO` cannot be reused after
  modifying quark Yukawas. Regenerate UV/R2 with NLOCT.

## Steps on AF (if Mathematica and FeynRules are installed)

```bash
cd ~/zee
git pull --ff-only
python3 -m unittest discover -s tests -v

# Determine whether AF has an available, licensed Wolfram kernel
command -v math || command -v wolframscript || true

# Find the location of the FeynRules.m main package file
find "$HOME" -maxdepth 6 -name FeynRules.m -print 2>/dev/null | head
```

If neither kernel exists on AF, export on a machine with a licensed
Mathematica 15 + FeynRules installation, then copy the resulting
LO UFO directory into `~/zee/work/Zee_TypeII_LO_UFO` on AF.
Don't assume the laptop's FeynRules folder is visible through AF.

With a Mathematica kernel on the machine doing the export, set:

```bash
export FEYNRULES_PATH=/absolute/path/to/feynrules
export ZEE_FR_SOURCE="$HOME/zee/models/Zee_TypeII_FR"
export ZEE_UFO_OUTPUT="$HOME/zee/work/Zee_TypeII_LO_UFO"

# First verify the package and source directories, not only variable names
test -f "$FEYNRULES_PATH/FeynRules.m"
test -f "$ZEE_FR_SOURCE/ZEE.fr"
test ! -e "$ZEE_UFO_OUTPUT"

# For Mathematica kernel `math`:
math -script "$HOME/zee/scripts/gate7_export_typeii_ufo.m" \
  2>&1 | tee "$HOME/zee/work/gate7_feynrules_export.log"

# Or where only wolframscript is available:
# wolframscript -file "$HOME/zee/scripts/gate7_export_typeii_ufo.m"
```

`gate7_export_typeii_ufo.m` uses `LoadModel["ZEE.fr"]`,
`WriteUFO[LZEE, AddDecays -> False, Output -> output]` and
rejects any existing output directory. This export recipe
has NOT been executed on AF or on a Mathematica installation.
Consult the official [FeynRules Manual]
(https://cp3.irmp.ucl.ac.be/projects/feynrules/wiki/WikiStart).

## Gate: static UFO vertices and MG5 diagram generation

```bash
cd ~/zee
python3 scripts/gate7_validate_typeii_ufo.py \
  work/Zee_TypeII_LO_UFO \
  --output work/gate7_typeii_ufo_static.json

bash scripts/gate7_mg5_typeii_smoke.sh \
  "$HOME/zee/work/Zee_TypeII_LO_UFO"
```

The checker enforces both charge-conjugate vertices for each of:

- off-diagonal Z H+ h- (and conjugate);
- tb H± (and conjugate);
- tb h± (and conjugate);
- no *three-point* photon-H-h mixed vertex.

The MG5 script generates **no events** and makes three separate
directories: 4FS gg→tbH±, uubar→H+h- / H-h+, and H+→Z h+.
Both checks must pass before any rates/widths may be compared.
Even after they pass, physics still requires numerical coupling
matching to P2, gauge/Ward tests, and a complete widths/BR inventory.

## LO-to-NLO upgrade

1. Match scalar potential, Yukawas, and every essential coupling at LO.
2. Perform LO process/cross-section/width closure against independent
   analytic calculations and the existing Type-II production proxy.
3. Use NLOCT with the *modified* FeynRules Lagrangian to regenerate
   UV and R2 counterterms for QCD; verify ultraviolet and infrared
   finiteness and reduced scale dependence.
4. A directory named `ZEE_NLO` is not proof of NLO correctness for
   Type-II Yukawas introduced after the original NLO export.


## LOCAL ACTUAL EXPORT: PASS (2026-10-11, user-supplied log)

On a separate Linux workstation with Mathematica 15,
FeynRules **2.3.49**, and the modified `Zee_TypeII_FR` source:

- FeynRules and Yang/Wu `ZEE.fr` loaded successfully.
- `WriteUFO[LZEE, Output -> ... , AddDecays -> False]` completed.
- Reported 336 possible nonzero vertices; 327 calculated vertices.
- Output contains `particles.py`, `parameters.py`, `vertices.py`,
  `couplings.py`, `lorentz.py`, etc.
- `QN::NonConserv` LeptonNumber warnings appeared as expected for
  the source's Zee lepton-sector couplings; no fatal export error.
- A small `CT_couplings.py` file is present but no regenerated
  UV/R2 counterterm validation exists. **Not NLO-capable yet.**

**Observed path on local machine:**
`/home/amine/zee-local/work/Zee_TypeII_LO_UFO`.

**NOT YET TESTED:** our UFO vertex-inventory checker, AF MG5
3.5.9 import/diagram test, exact Florentino parameter mapping,
charged mass/trilinear identities, LO cross sections/widths and Ward checks.

Next: locally download `scripts/gate7_validate_typeii_ufo.py`
and run it against the exported UFO; if it passes, `scp -r`
the UFO directory to `/home/aalida/zee/work/` on AF.
Then run `scripts/gate7_mg5_typeii_smoke.sh` there.
