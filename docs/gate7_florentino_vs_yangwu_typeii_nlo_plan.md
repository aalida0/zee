# Gate 7: LO FeynRules source adaptation, NLO roadmap, literature conventions

## AF process-generation result, 2026-10-11

The user cloned `https://github.com/YangPhy/Zee-Model` at
`~/zee/external/Zee-Model` and MG5_aMC 3.5.9 successfully loaded
`ZEE_UFO` (after legacy auto-convert) and generated:

- `u u~ > H+ h-`: 3 tree diagrams.
- `u u~ > H- h+`: 3 tree diagrams.
- 2 subprocesses total, 6 diagrams; output succeeded.

This is proof of **import and matrix-element generation**, NOT a verified
cross section or physically matched 300/700 GeV benchmark.

Both `ZEE_UFO` and `ZEE_NLO` have the `Z H+ h-` vertex.
`ZEE_NLO/CT_vertices.py` and `ZEE_NLO/CT_couplings.py` contain
QCD UV/R2 counterterms, but **zero** physical `tb H+` and `tb h+`
interactions. The original CTs are invalid after changing the Yukawas.

## What was actually used by Florentino, Romao and Silva?

Published reference: https://doi.org/10.1140/epjc/s10052-021-09956-2
(authoritative revised journal version of arXiv:2106.08332).

Section 3 uses a **Type-II two-Higgs-doublet model plus one singly charged
scalar singlet**, CP-conserving, with Z2 respected in the scalar/quark
subsector. The paper explicitly states its quark Yukawas in eqs (38)–(39):

`-L_Y = Qbar_L tilde(Phi2) Y_u u_R + Qbar_L Phi1 Y_d d_R + h.c.`

and physical charged Yukawas proportional to cosγ H1+ − sinγ H2+.
Appendix A of the published paper gives physical-potential inversion;
its authors used FeynMaster (QGRAF+FeynRules+FeynCalc) for vertices;
used HiggsBounds and dedicated flavor/oblique/theory checks;
for tbH+ production plots they imported published cross sections
(Refs 51,52), rather than identifying a distributed MG5 UFO.
Their section 8 explicitly says a full quark/lepton flavor fit was
**outside their scope** and Type-II quark assumptions cannot simply
be asserted as a complete realistic neutrino-mass fit.

## Why the Yang/Wu UFO is not automatically the Florentino benchmark

Yang/Wu's `ZEE.fr` is in the Higgs basis with fields H1 (vev-carrying)
and H2 (zero vev). In `Lagrangian.fr`, `yukq` couples quarks only
to H1. Thus physical charged H± and h± **lack tb vertices**.

The Type-II quark Yukawas in the Higgs basis are:

`Phi1 = cosβ H1 − sinβ H2`
`Phi2 = sinβ H1 + cosβ H2`
`-L_Y ⊃ (√2/v) Qbar_L [(tilde H1 + cotβ tilde H2) M_u u_R`
`                   + (H1 − tanβ H2) M_d d_R] + h.c.`

Thus we can retain the original vev-doublet quark Yukawa terms
and extend *only the Higgs-basis zero-vev doublet components*.

The source uses physical charged `H+` (PDG 227) and `h+` (PDG 228):
`H2[1] = cosφ H+ + sinφ h+`, with the charged singlet
`eta+ = -sinφ H+ + cosφ h+`.
Florentino's convention uses H1=cosγ HD+ + sinγ chi+,
H2=−sinγ HD+ + cosγ chi+.
Matching *magnitudes* gives φ≈π/2−γ≈0.481796 rad;
the difference in relative signs can be handled by field rephasing.

The Yang/Wu scalar potential is in a different parameter basis;
it needs a **full scalar potential/charged-mass/trilinear match**
to the reconstructed Florentino physical P2-like point. Naive
translation of its quartic names is incorrect.

## Generated source-only patch

New helper `scripts/gate7_prepare_typeii_feynrules.py` copies the
four original FeynRules source files to `models/Zee_TypeII_FR`,
patching just the up/down quark Higgs-basis fields:

- `H1[ii] -> (H1[ii] - Tan[beta]*H2[ii])` in down Yukawas
- `H1bar[jj] -> (H1bar[jj] + Cot[beta]*H2bar[jj])` in up Yukawas

It fails if source terms are missing or if output already exists;
it NEVER changes upstream `external/Zee-Model` or copies old CT files.
It does **not** export a UFO. User has to use FeynRules/Mathematica
to derive a LO UFO and verify all interactions and masses.

```bash
cd ~/zee
git pull --ff-only
python3 -m unittest discover -s tests -v
python3 scripts/gate7_prepare_typeii_feynrules.py \
 --source external/Zee-Model --output models/Zee_TypeII_FR
grep -n 'Tan\[beta\]\|Cot\[beta\]' models/Zee_TypeII_FR/Lagrangian.fr
```

## LO acceptance and NLO plan

1. Check FeynRules Hermiticity, particle/mass definitions, scalar
   potential/neutral and charged rotations. Match the Gate-6
   numerical benchmark (β=1.394, α=1.398, γ=1.089, masses 300/700).
2. Export a new LO UFO and verify tbH+ and tbh+ vertices exist,
   Z H+h- still exists, and no off-diagonal photon scalar current.
3. MG5 independently reproduce analytic partial widths, 14 TeV
   Type-II mixing-rescaled associated-production at matched parameters,
   and 80/100 TeV Z-mediated DY at matched EW inputs.
4. Generate and validate a gauge-complete charged-Higgs cascade
   (including spin correlations, all modes, electroweak Ward tests).
5. For NLO QCD, **rerun FeynRules+NLOCT** on the **modified** renormalizable
   Lagrangian; regenerate UV/R2 counterterms for massive tops/bottoms
   and scalar quark Yukawas. Verify NLO MG5 diagram/subtraction tests,
   UV and IR cancellations, LO/NLO scale dependence and an independently
   trusted 2HDM NLO limit.
6. An `NLO` directory name or presence of CT files in the **unmodified**
   model is not evidence that our Type-II extension is NLO-ready.

**Priority:** LO model/benchmarks first. NLO counterterms after source
stabilization and Lagrangian closure. The physical Zee lepton/neutrino
sector is a separate, explicit scope choice; the Florentino Zee-type
scalar/quark phenomenology did not claim it was fit.
