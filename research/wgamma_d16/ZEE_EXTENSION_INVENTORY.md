# D16: published overlap and remaining Zee-specific completion

The general-2HDM result is the reference calculation. Its common-limit
comparison is documented in [EXTERNAL_2HDM_BASELINE.md](EXTERNAL_2HDM_BASELINE.md).
It proves numerical full agreement on two restricted potentials, while a
nonzero-potential HW source/paper discrepancy remains. Neither result grants
full Zee gauge matching. This inventory classifies interactions and skeletons;
it is not a complete generated list of new two-loop Feynman graphs.

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
It is currently **PROPOSED_ONLY**: neither the generic HW source normalization
nor the Zee Delta is fully validated. Define the overlap at the level of
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

The next Zee derivation should target mixed charged-current/Goldstone
mass-difference parents and the off-diagonal Z/potential sector, using the
existing tensor/subloop evidence and the published common result. Generate
all attachments and ST partners before selecting genuinely unmatched master
integrals. MaRTIn or pySecDec are options only for those masters; no new
large integration or scan was run here.

`OUT_OF_SCOPE`: pure F one-loop terms already frozen in Module3, complete
higher-order Yukawa/QED corrections, finite-neutrino/external-invariant
improvements, and a physical neutrino-fit/global-acceptance claim.
Physical Zee W Wilsons remain unavailable (`null`, `coherent_inclusion=false`).
