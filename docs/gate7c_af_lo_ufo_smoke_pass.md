# Gate 7C: modified Zee-Type-II LO UFO imported and diagrams generated on AF

**Status: LO_IMPORT_AND_DIAGRAM_GATE_PASS; numerical physics matching PENDING.**

## User-provided AF log (2026-10-11)

`bash scripts/gate7_mg5_typeii_smoke.sh ~/zee/work/Zee_TypeII_LO_UFO`
completed using MG5_aMC v3.5.9 on login01:

| Test | Result |
|---|---|
| UFO static vertex count | 517 |
| Z H+ h- and conjugate | V_406, V_408 |
| tb H± and conjugate | V_288, V_309 |
| tb h± and conjugate | V_297, V_318 |
| Off-diagonal photon-H-h 3-point | none |
| `gg -> t~ b H+` and conjugate | 8 diagrams each |
| `u u~ -> H+ h-` and conjugate | 6 diagrams each |
| `H+ -> z h+` | 1 diagram |

MG5 automatically converted the freshly exported model on first import;
subsequent import/reconstructed process definitions succeeded.
The lepton-number-violation information message is consistent with
charged-singlet Zee Yukawas, not an error.

**Clarification:** Original Yang/Wu UFO earlier produced 3 diagrams
for each `u u~ -> H+ h-`; Type-II Yukawa extension now produces 6.
The additional diagrams must be examined: a raw all-diagram
cross section is **not** automatically equal to the pure
`Z* -> H+ h-` analytic result. For the DY comparison, isolate
the Z-mediated contribution or compare a sufficiently light-quark
Yukawa-suppressed limit and explicitly verify interference.

## Necessary physical parameter mapping

Yang/Wu's source uses the Higgs basis (`Hv`, `HH`), while
Florentino et al. use the original vev-split 2HDM fields.
With `Phi1=cosβ Hv−sinβ HH` and
`Phi2=sinβ Hv+cosβ HH` the doublet quartics must transform.
New script `scripts/gate7_map_p2_to_yangwu.py` computes
`ZEEINPUTS[1..4]` and `ZEELAMS[1..7]` from
our existing Gate-6 benchmark and checks five independent
mass/potential identities. New unit tests check exact
quartic polynomial equality for arbitrary **complex** doublets.

For beta=1.394 and gamma=1.089, charged mixing is
`phi=pi/2−gamma=0.48179632679 rad`. Up to a sign rephasing,
Yang/Wu heavy `H+` (PDG 227) is Florentino `H2+`,
while light `h+` (PDG 228) is Florentino `H1+`.

Example numerically derived (dimensionless) external quartics:

`ZEELAMS[1]=2.39677936`, `ZEELAMS[2]=2.71011596`,
`ZEELAMS[3]=-0.37353220`, `ZEELAMS[4]=0.03776437`,
`ZEELAMS[5]=1.04821563`, `ZEELAMS[6]=-0.18783090`,
`ZEELAMS[7]=4.473`.

Doublet Higgs-basis internal quartics are
`Z1=0.25782059`, `Z4=-1.14552191`,
`Z5=-1.06176138`, `Z6=-0.02121823`.

Run on AF:

```bash
cd ~/zee && git pull --ff-only
python3 -m unittest discover -s tests -v
python3 scripts/gate7_map_p2_to_yangwu.py \
  --output work/gate7_yangwu_p2_mapping.json
```

## Physics validation still required

1. **Build an MG5 parameter card** with the transformed quartics
   and masses—not raw Florentino λ_i in `ZEELAMS`!
2. Match EW input scheme, CKM, charged and neutral mixing signs.
3. Test numerical `ZH+h-`, tbH±, h125 H+h- trilinears
   against independent analytic couplings/widths.
4. Check pure Z-mediated mixed-pair amplitude vs analytic DY
   (not blindly the 6-diagram all-orders tree sum).
5. **Lepton sector:** Yang/Wu UFO has independent `ZEEYUKAWAF`
   and `ZEEYUKAWAY`. Their raw defaults (often 1) are NOT
   neutrino/LFV-calibrated and are not Type-II charged lepton
   couplings. Use explicit controlled lepton parameters,
   not defaults, before interpreting H1/H2 branching ratios.
6. Gauge/Ward tests, complete widths, EW/flavor/direct-search
   constraints, and new NLO QCD UV/R2 counterterms remain pending.

**Do not start large MG5 event generation or Delphes yet.**


## Gate 7C next: parameter-matched diagnostic card

New utility `scripts/gate7_make_diagnostic_param_card.py` takes
the MG5-produced `Cards/param_card.dat` as a template and replaces
the model's own `ZEEINPUTS`, `ZEELAMS`, `MASS`, `ZEEYUKAWAF`,
and `ZEEYUKAWAY` entries using the Higgs-basis mapping.

To isolate the Type-II **scalar/quark/lepton** test limit, it sets
the antisymmetric Zee lepton Yukawas `f_ab=0` and the extra doublet
charged-lepton Yukawas to `−tanβ √2 m_l/v` on diagonal, off-diagonal
zero. As a result **radiative neutrino masses vanish**, so it is
**NOT a realistic full Zee neutrino model**. Treat this solely as
an internally controlled tree-level amplitude/width diagnostic.

The script deliberately leaves all existing `DECAY` widths in the
MG5 template unchanged. They are **stale defaults** and MUST NOT
be interpreted as physical widths or used in resonance studies.

```bash
cd ~/zee
git pull --ff-only
python3 -m unittest discover -s tests -v
python3 scripts/gate7_map_p2_to_yangwu.py \
    --output work/gate7_yangwu_p2_mapping.json
python3 scripts/gate7_make_diagnostic_param_card.py \
    --template work/gate7_mg5_typeii_smoke/Associated_4FS/Cards/param_card.dat \
    --output work/gate7_typeii_diagnostic_param_card.dat \
    --acknowledge-unfitted-neutrino-sector
```

Expected charged masses: `MASS[227]=700`, `MASS[228]=300`.
Expected mixing: `ZEEINPUTS[1]=1.394`,
`ZEEINPUTS[3]=0.004`, `ZEEINPUTS[4]≈0.48179632679`.
Expected `ZEELAMS`: `(2.39677936, 2.71011596, −0.37353220,
0.03776437, 1.04821563, −0.18783090, 4.473)`.

**Next after card generation:** compare numerical LO couplings
and partial widths (not merely static diagrams) to Gate-6 analytical
results; handle the six-diagram mixed pair properly, then run
EW/CKM matching and gauge tests before physical cross sections.


## Gate 7D: user ran parameter mapping and diagnostic card on AF

On 2026-10-11 the user ran both scripts successfully:

- `gate7_map_p2_to_yangwu.py`: scalar external inputs
  `ZEEINPUTS=(1.394,1.398,0.004,0.4817963267948966)`;
  `ZEELAMS=(2.396779362019555,2.7101159644251087,
   -0.3735321954718115,0.03776437207458772,
   1.0482156279254127,-0.187830901992651,4.473)`.
- Higgs-basis internal quartics:
  `(Z1,Z4,Z5,Z6)=(0.25782059008508423,
  -1.145521910262999,-1.0617613842555145,
  -0.021218226720188617)`.
- Potential/mass identity residuals:
  Z1=0, Z4=-8.88e-16, Z5=-4.44e-16, Z6=2.78e-16,
  μzee=-1.14e-13 GeV.
- `gate7_make_diagnostic_param_card.py` produced
  `work/gate7_typeii_diagnostic_param_card.dat`;
  Zee singlet antisymmetric lepton Yukawas f_ab=0
  (no neutrino masses); charged lepton Yukawas Type-II.
- Existing DECAY widths in generated diagnostic card are
  deliberately stale and MUST be recomputed.

**Status:** analytical parameter map PASS, input-card write PASS.
Not yet a MadGraph numerical amplitude/width match or a physical point.

## Run Gate 7D MadWidth benchmark test (new scripts)

MadWidth command syntax from Alwall et al.
`arXiv:1402.1178`: `compute_widths [particle] --path= --output=`
and `--body_decay=2` limits calculations to 2-body modes.

```bash
cd ~/zee
git pull --ff-only
python3 -m unittest discover -s tests -v
source ~/fccee_zh/scripts/setup_key4hep.sh
bash scripts/gate7_run_madwidth.sh \
   2>&1 | tee work/gate7_madwidth_wrapper.log
```

Output `work/gate7_madwidth/madwidth_output_param_card.dat`
is written separately from the original diagnostic input card.
`work/gate7_madwidth/width_comparison.json` contains the five
independent LO tree-level partial-width comparisons:
1. heavy→light+Z (~9.411 GeV analytic Gate6 reference)
2. heavy→tb (~1.558 GeV)
3. heavy→W+neutral heavy (~1.071 GeV)
4. heavy→light+h125 (~0.267 GeV)
5. light→tb (~0.09095 GeV).

Default gate threshold |ΔΓ/Γ|<20% is deliberately loose to flag
major normalization/sign/kinematics inconsistencies; it is NOT
a theory uncertainty estimate or proof of physical validity.
Any failure (including a MadWidth parser/compatibility failure)
must be examined rather than loosening this threshold blindly.
