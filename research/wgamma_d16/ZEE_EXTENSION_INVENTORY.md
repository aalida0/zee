# D16: published overlap and remaining Zee-specific completion

The general-2HDM result is the reference calculation. Generic complex
common-limit closure now passes with the source-preserving, independently
audited HW normalization replacement; the original source still fails its
normalization check. See [GENERIC_2HDM_CLOSURE.md](GENERIC_2HDM_CLOSURE.md) and
[HW_NORMALIZATION_AUDIT.md](HW_NORMALIZATION_AUDIT.md). Neither grants full
Zee gauge matching. This inventory classifies complete classes and remaining
interactions; it is not a complete generated list of all new two-loop graphs.

## Priority 1 — complete unmixed-singlet HZ class, now calculated

The smallest new nonzero class is available **without charged mixing or F**:
take gamma=0, Mu4=0, F=0 and real nonzero singlet portals K1,K2,K12. H2 is
a physical SU(2) singlet with Q=Y=1, mass M_S; H1 is the doublet. The singlet
has `t_Z=(T3-Q sw²)/(sw cw)=-sw/cw` and scalar trilinears

```
G_h,SS = ca (K1 v1-K12 v2) + sa (K2 v2-K12 v1),
G_H,SS = -sa (K1 v1-K12 v2) + ca (K2 v2-K12 v1),
G_A,SS = 0.
```

The new two-loop class contains neutral-scalar exchange to the external LFV
line, a **charged-singlet triangle in both orientations**, one real photon,
one exchanged Z, the **AZSS contact/seagull**, and both outer lepton-line
attachment orders. Neither a triangle alone nor one outer order is the class.
In this restriction the singlet current and mass commute, there are no
off-diagonal Z currents, no singlet W current, no charged-singlet Yukawa, and
no G0SS coupling. Both gauge-current Ward identities of the complete scalar
tensor hold. Thus longitudinal Z propagation annihilates the inner tensor;
no W/Goldstone/ghost/LSZ remainder is required to complete **this Abelian
scalar-current class**. Portals arise from gauge-invariant doublet bilinears
times |S|²; the neutral trilinears are not added by hand. This proof ceases
to apply to mixed charged states. It does not prove gauge completion of any
other Zee class.

The calculation inherits a scalar master with a direct independent radial
representation. With `x=M_S²/M_k²`, `y=M_Z²/M_k²`, `u=a(1-a)`,

```
f10(x,y) = [f9(x/y)-f9(x)]/(1-y)
         = - integral_0^1 da u integral_0^infinity dt
                 t/[(t+x)(t+y u)(t+u)].
```

The second form follows by partial fractions of the massive outer propagator
starting from the already signed, independently integrated frozen scalar-QED
photon kernel `f9=-2 F2`. It remains regular at y=1. This is an independent
integral check, rather than another call to the author f10 function.

The inner Z-current replacement has factor `t_Z/Q` on **both triangles and
the contact**. For the electron/muon/tau line, the vector current relative
to its Q=-1 photon current is `-v_e^Z/2`; the positive massive radial kernel
is `-f10`, so those minus signs cancel. The axial outer-current contribution
cancels between the two outer orders for this CP-even scalar tensor. Hence
the isolated class in the frozen operator convention is

```
C_X^(S Z) = -alpha v_e^Z t_Z/(64 pi^3 m_i)
            sum_k G_k,SS Y_X,k f10(x_k,y_k)/M_k²,
Y_L,k=C_k,ji, Y_R,k=C_k,ij*.
```

This also follows from the validated doublet HZ expression by replacing its
charge factor `(cw²-sw²)/(sw cw)=2 t_Z,doublet` with `-2 sw/cw`, **only for
this diagonal scalar-current class**. It is not a rescaling of the kinetic
or W aggregate. The photon singlet class is already in Module4 and is not
added again. The new HZ term has no overlap with that photon class.

`zee_singlet_hz.py` evaluates this restricted class using native scalar
reconstruction, full trilinear matrices and the radial kernel, and rejects
gamma!=0 or F!=0. G_h/G_H also pass an independent singlet-leg derivative of
the full potential Hessian. For the evidence fixture (G1 doublet potential,
M_S=540 GeV, K1=.3,K2=.18,K12=-.04), its class-only coefficients are:

| Channel | C_L [GeV^-2] | C_R [GeV^-2] |
|---|---|---|
| mu→e | 4.57150e-14+2.39789e-14i | 5.81312e-14-2.01365e-15i |
| tau→e | -1.78956e-14+9.58271e-15i | 1.36003e-15+1.76578e-15i |
| tau→mu | 3.62834e-15-1.74182e-16i | 1.48732e-15-7.96068e-15i |

Scalar-current Ward residuals are <=5.59e-16, while omitting the seagull
leaves .1127. Zero portals give exact zero; increasing M_S tenfold reduces
the coefficient norm by .02312, consistent with power/log decoupling at
fixed portal trilinears. The independent radial result agrees with author
f10 and with the difference of frozen F2 integrals. These are class-level
leading-external-invariant coefficients, not physical full Zee W Wilsons.
They are retained only in research evidence, `coherent_inclusion=false`.

## Subsequent priorities — complete classes before general amplitudes

1. **General mixed scalar–Z–photon potential class.** Include both diagonal
   states and all off-diagonal G_k,ab and Z_ba currents, both triangle
   orientations, AZ contact, both outer orders, and any longitudinal-Z/G0
   partners required when mass and Z-current matrices no longer commute.
   The equal-mass/diagonal masters above are useful limits; simply inserting
   off-diagonal couplings into f10 is not established. This is the smallest
   next general-mixing extension with a tested nonzero seed class.
2. **Potential charged-scalar–W class.** Extend audited HW using physical
   H1/H2 derivative currents, G_k,ab and mass-dependent Goldstone partners.
   Include charged-current parent placements, contact and outer attachments;
   prove the ST-completed aggregate. Reuse f11 only in proved diagonal/common
   limits. The earlier inner/parent tensors remain regression evidence.
3. **F and mixed F-D charged-current classes**, with neutrino orientation,
   external chirality, reducible attachments and LSZ/counterterm bookkeeping.
   These require a separately generated complete diagram set and cannot be
   inferred from diagonal doublet weights. Preserve the existing one-loop F
   ledger and avoid its overlap.

This ordering puts a small proved nonzero Zee-specific set ahead of a full
bespoke W integration. No whole-2HDM W rescaling or entire-answer addition is
authorized by it.

## Transfer without a new integral

`2HDM_COMMON`: neutral fermion/photon and neutral fermion/Z-photon loops retain
the same native neutral vertices and SM charges. The photon part is already
validated in Module4. Keep its light species, which the reference's leading
heavy-species approximation omits. Do not append the author's whole neutral
fermion sum to the existing coherent ledger.

`2HDM_COMMON`: the charged-scalar/photon **kernel**, with its triangles and
seagull, transfers to each physical charged mass using the actual diagonal
trilinear. The two eigenstates are already included by Module4. This transfer
is a universal scalar-QED statement, not a mixing rescaling of the full bosonic
result. A single off-diagonal trilinear with two identity photon currents is
`VANISHES_PROVED`; adding a nontrivial Z or W current changes that argument.

`2HDM_COMMON`: the existing 26 W/Goldstone/ghost inner tensors survive with the
same neutral VEV overlap. Their exact identifiers are listed in
`external_2hdm_inventory.json`. They check the transferable tensor pieces but
must not be added to the published completed 2HDM result. The eight existing
fixed-r W/G parent subloops likewise provide common-limit checks; they are
not eight new physical Wilson terms.

The completed neutral-only hZ diagrams can transfer with matched neutral
couplings. The remaining kinetic result is kept as its published aggregate
until its charged-sector dependence is decomposed and completed in Zee.
No full-W transfer by a single doublet weight has been established.

## Charged-current and potential extension

For physical charged rows, write

```
d=(cos gamma,-sin gamma), s=(sin gamma,cos gamma)
R_ba(Ha+)=-d_a D_ab*, L_ba(Ha+)=-s_a F_ba.
```

Photons couple as `e delta_ab`. For positive fields the Z charge matrix is
`e/(sw cw) [d_a d_b/2-sw² delta_ab]`, with the all-incoming momentum/sign
orientation fixed by the native vertex. Its off-diagonal elements do not
vanish at generic mixing. W-neutral-Ha derivative vertices carry `d_a`;
Goldstone-Ha-neutral vertices carry the corresponding mass differences.
These relations were independently checked in the preserved native evidence.

`ZEE_EXTENSION_REQUIRED` includes:

- All physical H1/H2 charged-current parents, both neutral-scalar placements,
  charged-fermion W subloops and their mass-dependent sums. Even where two
  doublet vertices produce d_a², this is a diagram-level fact requiring a
  completed class, not permission to multiply the entire W contribution.
- Diagonal and off-diagonal matrices
  `G_s,ab=d³V/(ds dHa- dHb+)`, rotating both charged legs. Mu4 and K1,K2,K12
  generate new entries. h/H have real symmetric matrices; A can have
  imaginary off-diagonal entries although its diagonal entries vanish.
- Mixed H1/H2 Z-photon and W charged-scalar loops, including associated gauge
  seagulls and Goldstone parents. Off-diagonal G and off-diagonal Z currents
  can close a loop with unequal charged masses. The equal-charge photon
  selection rule does not eliminate these terms.
- Antisymmetric F vertices and mixed F-D charged-neutrino/lepton graphs,
  including external chirality and Majorana orientation bookkeeping. At
  zero neutrino mass some one-loop F-D products vanish; that fact alone is
  not a proof that every two-loop F-dependent gauge-completed class vanishes.
- The full ST/BRST and ghost/gauge-fixing insertions for the physical charged
  parents, external/reducible photon attachments, counterterms and LSZ terms
  required by on-shell matching. The charged singlet has no SU(2) VEV and no
  direct charged-W ghost coupling; its hypercharge currents and mixing still
  modify the completed identities. Do not invent ghost-singlet Yukawas.

`VANISHES_PROVED`: photon-W-physical-Ha mass vertices vanish because each
physical charged row is orthogonal to the doublet VEV. The CP-conserving A
has zero pure W/G/VEV-ghost inner contribution. Neither statement eliminates
A mixed-H1/H2 diagrams or derivative W-Ha-neutral interactions.

The old six parent categories retain their identifiers. `P_Zee_completion`
is explicitly a new charged-sector extension; the other five retain common
core checks but require the physical charged remainder before a Zee sum is
accepted. Nothing in the old standalone gauge-dependent source-A or
Goldstone-only diagnostic is a legitimate subtraction coefficient.

## Matching and subtraction boundary

A future strategy is
`C_Zee = C_2HDM(common reference) + Delta_C(singlet,mixing,F)`.
It is currently **PROPOSED_ONLY** for the full Zee amplitude: generic HW
normalization is resolved in the research adapter, but only the restricted
unmixed-singlet HZ part of the Zee Delta is validated. Define the overlap at the level of
complete gauge-invariant classes with matched renormalized masses, vertices
and EW inputs. Derive the expanded Zee classes and subtract their analytic
strict-limit common classes using the same regulator, counterterms and LSZ
prescription. Prove that their difference is finite, gauge independent and
vanishes in the singlet-free limit. Prove both complex chiralities separately.

For an eventual frozen-ledger integration, replace only the proved overlap
or subtract it once: retain existing one-loop, all nine fermion/photon species
and both charged-scalar/photon states. Append only separately validated missing
classes; do not append the entire 2HDM answer. Never subtract gauge-dependent
bare W kernels, the conditional source-A coefficient, or an imposed negative
Goldstone gauge variation.

The next general-mixing Zee derivation should target the off-diagonal
Z/potential class first, then mixed charged-current/Goldstone mass-difference
parents, using the restricted class, existing tensor/subloop evidence and
the published common result. Generate
all attachments and ST partners before selecting genuinely unmatched master
integrals. MaRTIn or pySecDec are options only for those masters; no new
large integration or scan was run here.

`OUT_OF_SCOPE`: pure F one-loop terms already frozen in Module3, complete
higher-order Yukawa/QED corrections, finite-neutrino/external-invariant
improvements, and a physical neutrino-fit/global-acceptance claim.
Physical Zee W Wilsons remain unavailable (`null`, `coherent_inclusion=false`).
