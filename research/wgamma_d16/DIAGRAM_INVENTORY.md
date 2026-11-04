# Diagram and native-vertex inventory

**Complete inner 1PI skeleton inventory; incomplete general-xi physical parent
completion. Gate A is BLOCKED_GAUGE_MATCHING.** No graph below has been
independently loop-integrated in D16. The enumeration does not certify a
complete physical LFV subset.

`inventory.inner_diagrams()` enumerates 26 labeled graphs per CP-even scalar.
An independent run of the existing FeynArts3.9 SM topology model gives the
same 26: 20 triangles and six bubbles. This cross-check uses SM connectivity
only; no SM/2HDM coupling is substituted for a Zee vertex. The actual 58 Zee
vertex queries and their returned tensor orderings are archived in
`native_vertices.json`. Detailed dumps and the generated amplitudes remain
in ignored `local/`.

## Inner graphs and counting

Take external vertices s, q (real photon) and k (virtual photon) as labeled.
The three triangle edges are (s,q), (q,k), (k,s). W denotes the charged vector,
G the **charged Goldstone**, never a physical charged Zee scalar.

| Edge assignment | Scalar vertex | Real-photon vertex | Virtual-photon vertex | Charge orientations |
|---|---|---|---|---:|
| WWW | sWW | photonWW | photonWW | 2 |
| WWG | sGW | photonWW | photonWG | 2 |
| WGW | sWW | photonWG | photonGW | 2 |
| WGG | sGW | photonWG | photonGG | 2 |
| GWW | sWG | photonGW | photonWW | 2 |
| GWG | sGG | photonGW | photonWG | 2 |
| GGW | sWG | photonGG | photonGW | 2 |
| GGG | sGG | photonGG | photonGG | 2 |
| c-minus loop | sGhostMinus | photonGhostMinus | photonGhostMinus | 2 arrow orientations |
| c-plus loop | sGhostPlus | photonGhostPlus | photonGhostPlus | 2 arrow orientations |

The two charged Faddeev–Popov species are independent Grassmann fields;
they are not one scalar species with an arbitrarily assigned degeneracy.
Each closed ghost loop has a minus sign. Each listed oriented triangle has
symmetry factor one. Do not multiply their sum by another global factor two.

| Bubble/contact class | Count | Native sources |
|---|---:|---|
| sWW with photonPhotonWW | 1 | `sWW_k`, `photonPhotonWW` |
| sGG with photonPhotonGG | 1 | `sGG_k`, `photonPhotonGG` |
| s-photon-WG contact with other photon-WG | 4 | `sPhotonWG_{k,c}`, `photonWG_1`, `photonWGconj_1`; two labeled photon choices, two charges |

These complex charged-pair bubbles each have symmetry factor one. Their
relative signs follow from the **signed vertices below**, propagator phases
and momentum numerators; a scalar-QED seagull sign cannot be transferred to
the W seagull. Linear gauge fixing has no two-photon ghost seagull. A
renormalizable scalar kinetic term has no s-photon-WW or s-photon-GG vertex.
The independent topology enumeration provides a check on these absences.

All 26 entries have `status=NOT_EVALUATED`. A graph with a known nonzero
vertex is never entered as numeric zero because its integral is missing.

## Actual signed native rules

Use all incoming momenta and returned field order; \(\kappa_s\) is the neutral
VEV overlap. (e=g_2\sin\theta_W=g_1\cos\theta_W\) and (m_W=g_2v/2\) in the
native numerical comparisons. The charged basis is Hm1=G-, Hm2=H1-, Hm3=H2-.

| Vertex order | Rule (tensor stripped only as stated) | xi dependence |
|---|---|---|
| s, W-, W+ | \(+i\,2m_W^2\kappa_s/v\ g_{\alpha\beta}\) | none |
| s, G-, G+ | \(-i M_s^2\kappa_s/v\) | none; G propagator has mass squared xi*mW² |
| s, G-, W+ | \(-ig_2\kappa_s/2\ (p_s-p_{G^-})_\alpha\) | W/G propagators |
| s, G+, W- | \(-ig_2\kappa_s/2\ (p_{G^+}-p_s)_\alpha\) | W/G propagators |
| photon, W+, G-; conjugate | \(+ie m_W g_{\mu\alpha}\) | W/G propagators |
| s, photon, W+, G-; conjugate | \(+ie g_2\kappa_s/2\ g_{\mu\alpha}\) | W/G propagators |
| photon, G-, G+ | \(-ie(p_+-p_-)_\mu\) | G propagators |
| photon, photon, G-, G+ | \(+2ie^2g_{\mu\nu}\) | G propagators |
| s, antighost-minus, ghost-minus; plus species | \(-i\xi_W m_W^2\kappa_s/v\) | **vertex and propagators** |
| photon, antighost-minus, ghost-minus | \(-ie p_{c,\mu}\) | ghost propagators |
| photon, antighost-plus, ghost-plus | \(+ie p_{c,\mu}\) | ghost propagators |

For photon(mu), W-(alpha), W+(beta), the returned three-vector vertex is

\[
ie\{g_{\mu\beta}(p_\gamma-p_+)_{\alpha}
+g_{\alpha\beta}(p_+-p_-)_{\mu}
+g_{\mu\alpha}(p_--p_\gamma)_{\beta}\}.
\]

For photon(mu), photon(nu), W-(alpha), W+(beta), it is

\[
ie^2[-2g_{\mu\nu}g_{\alpha\beta}
+g_{\mu\alpha}g_{\nu\beta}+g_{\mu\beta}g_{\nu\alpha}].
\]

The source JSON retains the full unsimplified rules, including momentum
structures and both chiral projectors. Independent reconstruction, not a
2HDM table, checks the scalar trilinear. Actual native symbolic ghost rules
retain `RXi[Wm]`. 444 coefficient checks use two spectra, signed charged
mixing, generic complex D and antisymmetric F, at xi=.5,1,3. These are tree
vertex checks; they do not evaluate a gauge-dependent loop.

## Zee-specific reductions and physical zeros

The Goldstone row of ZP is (cos beta, sin beta, 0). Physical rows are

```
(-sin beta cos gamma,  cos beta cos gamma, sin gamma)
( sin beta sin gamma, -cos beta sin gamma, cos gamma)
```

The native photon-W-Ha coupling is proportional to
\(v_1ZP_{a1}+v_2ZP_{a2}=0\) for a=2,3. Thus physical H1/H2 cannot replace
G on a photon-WG transition in this inner class, for either sign of gamma.
The charged singlet has no VEV or SU(2) charged current. These facts prove
the reduction of the **inner connectivity** to doublet W/G/ghost rules.
They do not prove reuse of a completed 2HDM LFV kernel.

The AWW and AGG rules are exactly zero. AGhost coefficients are proportional
to \(v_1ZA_{21}+v_2ZA_{22}=0\); AWG likewise vanishes by neutral/charged
Goldstone orthogonality. Those are physical zeros in the stated scalar CP
limit, not missing calculations. They do not set the h/H complex axial
lepton couplings to zero.

For charged-current **parent** graphs the physical charged states do matter.
The native sWHa derivative overlap is
\(ZH_{s1}ZP_{a1}+ZH_{s2}ZP_{a2}\). Actual H-lepton vertices contain both
\(-id_a D_{ab}P_L\) and \(-is_a F_{ba}^*P_R\), where
\((d_1,d_2)=(\cos\gamma,-\sin\gamma)\) and
\((s_1,s_2)=(\sin\gamma,\cos\gamma)\).
The exact unweighted sums are \(\sum d_a^2=\sum s_a^2=1\),
\(\sum d_as_a=0\). A charged propagator with mass-dependent weights prevents
using the last identity without first performing its pinch reduction.

## Outer attachments and pinch parents still required

Every inner graph attaches to the two photon/lepton orderings in
`DERIVATION.md`, with its s propagator and general complex LFV vertex. The
exact B identity needs both. The exact C identity needs the h/H sum.

The four illustrative parent drawings in Abe Fig3 involve sWW/photonWW,
mixed sWG/photonWG and scalar sGG/photonGG vertices, with W/G charged lepton
currents; each needs charge conjugates and outer orderings. Their **published
xi=1 sum** is used only as a source-tensor check of the P cancellation.
No individual signed parent integral is claimed as derived here.

The machine inventory keeps separate mandatory unresolved entries for:

- `P_WWW`, `P_WG`, `P_GG`: those three parent families and both orientations.
- `P_longitudinal_xi`: extra general-xi longitudinal and ghost/Goldstone
  pieces; the xi=1 source explicitly does not enumerate these.
- `P_Zee_completion`: native charged H1/H2 derivative-current parents;
  determine whether their pinched pieces enter the target subset or cancel.
- `P_LSZ_audit`: determine the external self-energy/reducible-photon and
  counterterm pieces required by the on-shell Slavnov–Taylor reduction.

Their enumeration, relative signs, and external-line reductions in general
xi are **not complete**. Assigning them zero would falsely close Gate A.
`require_complete` raises on missing or unavailable graph data. In particular,
the full LFV subset cannot yet be declared closed under gauge transformations.
