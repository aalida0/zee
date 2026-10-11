# Public original Zee-model UFO located (2026-10-11)

**Finding: YES. A public FeynRules-based original Zee UFO exists.**

- Source: https://github.com/YangPhy/Zee-Model
- Alternative mirror/account: https://github.com/ycwu1030/Zee-Model
- LO UFO: https://github.com/YangPhy/Zee-Model/tree/master/ZEE_UFO
- NLO-oriented UFO: https://github.com/YangPhy/Zee-Model/tree/master/ZEE_NLO
- FeynRules sources: `ZEE.fr`, `Particles.fr`, `Parameters.fr`, `Lagrangian.fr`.
- Repository names authors Yang Ma and Yongcheng Wu, FeynRules implementation
  version 1.1.0 dated 2021-02-24 in `ZEE.fr`.

## Static inspection: positive matches

`ZEE_UFO/particles.py` defines **two distinct physical charged species**:

| Name in MadGraph | PDG | Interpretation here |
|---|---:|---|
| `H+` / `H-` | ±227 | heavy state H2± |
| `h+` / `h-` | ±228 | lighter state H1± |

`ZEE_UFO/vertices.py`: `V_364 = Z h- H+` and
`V_366 = Z h+ H-` are exactly the tree off-diagonal
Z-charged-scalar vertices required for the cascade.
`couplings.py`: `GC_216`, `GC_217` are proportional to
`ee*cphi*sphi/(2*sw*cw)` up to signs/imaginary factor,
confirming a genuine electroweak mixing-induced coupling.
`ZEEINPUTS[4] = phi` is this model's charged mixing angle;
`MASS[227] = MHpH` (heavy default 2000 GeV),
`MASS[228] = MHp` (light default 120 GeV).
`ZEEYUKAWAF` provides f_eμ, f_eτ, f_μτ;
`ZEEYUKAWAY` provides a 3x3 lepton-Yukawa matrix.
FeynRules `Lagrangian.fr` includes full scalar kinetic/potential and
charged-singlet/lepton interactions.

## Critical mismatch with our benchmark — NO tbH± Yukawa

**The publicly supplied UFO does not have physical `tb H+` or
`tb h+` vertices.** This was checked by enumerating all
`ZEE_UFO/vertices.py` entries involving bottom, top, and
either charged scalar: zero matches. The NLO-oriented UFO
likewise has zero such vertices. By contrast, `t b G+`
and `t b W+` Standard Model vertices exist.

`Lagrangian.fr` shows that the quark Yukawas involve only `H1`
(the vev-carrying doublet in the model's Higgs basis), with no
independent `H2` quark Yukawas. Thus the charged scalars
**do not couple to tb** in this model as published.

Consequences:

1. Use the UFO as a **starting point for mixed-pair electroweak
   production** `pp -> H+ h-` and the charge-conjugate process
   and for `H+ -> Z h+` vertex/kinematic validation.
2. The raw UFO **CANNOT** reproduce the dominant associated
   `pp -> t b H2` channel and **CANNOT** produce `H1 -> tb`.
3. Modify the *FeynRules quark-sector Lagrangian* to include
   Type-II Yukawa couplings to both original scalar doublets,
   rotate consistently to the Higgs basis, and re-export.
   Do not patch a single UFO vertex by hand.
4. Derive a consistent **parameter mapping** between the
   source Higgs-basis angles (`alpha`, `beta`, `alphabeta`,
   charged mixing `phi`) and Florentino et al. P2 (`alpha`,
   `beta`, `gamma`). With `H2[1] = cphi*HpH+sphi*Hp`,
   the heavy state's doublet component is `cos(phi)` and
   the P2 heavy doublet fraction is `-sin(gamma)`,
   so at the level of component magnitudes
   `phi ≈ pi/2 - gamma` (not `phi=gamma`); signs and other
   scalar parameter conventions require independent matching.
5. The source UFO uses a Higgs-basis scalar-potential parameterization
   which differs from P2's physical beta/alpha parameterization.
   Do not set old P2 quartics directly without transformation.
6. Even if the UFO loads in MG5, it does **not** establish
   gauge/Ward checks, physical masses from a common potential,
   LFV/neutrino constraints, or NLO validity of our benchmark.

## Proposed safe MG5 smoke test on ATLAS AF

Clone the public repository under `~/zee/external/` (no /data work).
Use an independent model name and avoid changing generated files:

```bash
cd ~/zee
mkdir -p external
git clone https://github.com/YangPhy/Zee-Model.git external/Zee-Model
source ~/fccee_zh/scripts/setup_key4hep.sh
MG5_BIN=/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/madgraph5amc/3.5.9-3xnfke/bin/mg5_aMC
cat > /home/aalida/zee/work/gate7_existing_zee_ufo.mg5 <<'EOF'
set automatic_html_opening False
import model /home/aalida/zee/external/Zee-Model/ZEE_UFO
display particles
display interactions
generate u u~ > H+ h-
add process u u~ > H- h+
output /home/aalida/zee/work/Gate7_Zee_UFO_DY_smoke -f
EOF
"$MG5_BIN" /home/aalida/zee/work/gate7_existing_zee_ufo.mg5
```

**Important:** this is an *unexecuted* smoke-test recipe; public
UFO model may require `auto_convert_model` or other compatibility
adjustments on MG5 v3.5.9. No events are required in this test.
Do not run full event generation or collider phenomenology until
model mapping and charged Yukawa validation are complete.
