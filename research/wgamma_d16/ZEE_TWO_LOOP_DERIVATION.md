# Zee radiative dipoles: calculated extensions and remaining reduction

The full leading two-loop Zee calculation is **not complete**. New results
are the unequal-mass physical charged-scalar Zγ radiative current, all nine
common neutral-fermion Zγ species, an all-diagram quadratic-FD selection
rule at mν=0, and a nonzero regulated F†F gauge subgraph. The full W,
F†F and reducible sums remain unavailable. This work does not assert
`ZEE_TWO_LOOP_RADIATIVE_LFV_PASS`.

## Conventions and overlap

Use the frozen CP-conserving scalar Lagrangian, general complex D and
antisymmetric F, and
\[
 \mathcal L_D={e m_i\over2}\bar\ell_j\sigma^{\mu\nu}
 (C_LP_L+C_RP_R)\ell_iF_{\mu\nu}+\mathrm{h.c.},\qquad
 C=-{c_{\rm corrected\ 2HDM}\over8\pi^2v^2},\quad K_2=-C^*.
\]
The last map is the D15 ordered operator bridge; neither a chirality swap
nor rate-only matching is used. The corrected common reference and its
original HW expected failure are preserved byte-for-byte. The completed
39-channel comparison was not replayed.

| Set | What is used | Overlap treatment |
|---|---|---|
| Scalar one loop | seven frozen Module3/D15 rows | once, including F² and D² |
| Neutral fermion photon | nine species × h/H/A from Module4 | 27 rows; no author th/ch/bh/tauh added |
| Physical scalar photon | two charged states × h/H/A from Module4 | six rows; no author HA added |
| Neutral fermion Zγ | native neutral vertices and massive radial master below | 27 new rows; no photon part |
| Physical scalar Zγ current | full G,T matrices and unequal-mass master | three new neutral-scalar rows; no separate singlet HZ addition |
| Neutral two-point/reducible sector | not calculated/assigned completely | null; no inferred zero |
| Published hZ/kin, charged-fermion W, HW | strict 2HDM evidence retained | no mixed-Zee whole-group rescaling |
| F†F gauge correction | regulated subgraph only | no two-loop Wilson row |

`zee_two_loop.py` therefore contains **70 available rows/channel**, seven at
one loop and 63 at two loops, summed once as `included_only_C_LR`. That row
count is not a completeness argument. Every required missing class retains
`C_LR=null`, and `full_two_loop_C_LR`, `full_C_LR`, `full_BR` remain null.
The AZ and Goldstone derivation and the source-specific physical-A zero
are in [MIXED_HZ_DERIVATION.md](MIXED_HZ_DERIVATION.md).

## Common neutral-fermion Zγ calculation

Neutral quark/lepton vertices and SM neutral currents are unchanged by the
charged singlet. Inner axial Z insertions cancel between charge orientations
(one C-odd photon and a C-even axial current). The complete transverse inner
tensor annihilates longitudinal Z propagation. The two outer lepton orders
retain the vector current; the axial anticommutator vanishes in the retained
external-invariant expansion. This transfers an entire neutral-current
class, independently of F and charged mixing, not the charged/kinetic group.

Put z=mf²/Ms², r=MZ²/Ms², u=a(1−a). Replacing the massive outer propagator
in the independently signed frozen photon calculation yields
\[
 f_3=-\int_0^1da\int_0^\infty dt\,
 {t\over(t+z)(t+u)(t+ru)},\quad
 f_4=-\int_0^1da\,(1-2u)\int_0^\infty dt\,
 {t\over(t+z)(t+u)(t+ru)}.
\]
For fast evaluation integrate t analytically:
\[
 J(a)={\log(z/a)\over z-a},\quad
 R={J(u)-rJ(ru)\over1-r},\quad
 R\big|_{r=1}={z\log(z/u)-(z-u)\over(z-u)^2}.
\]
Removable equalities use series or high precision. A separate log(t)
quadrature retains the positive original two-parameter integral. Its errors
are integrated conservatively through relative positive-integrand estimates;
pointwise absolute errors near a=0 must not be confused with integrated
uncertainty. At z=1e-11,r=.4 the 45-digit independent angular calculation
agrees with the direct integral to about 1.01e-11 absolute; upstream float
dilogs lose about 5.08e-7 there. This motivates the native radial evaluation
for light species without changing the preserved upstream source.

With `v_f^Z=(T3_f−2 Q_f sw²)/(sw cw)`, `Y=C_s,ff=a+ib`,
\[
 \begin{pmatrix}C_L\\C_R\end{pmatrix}_{fZ,s}
 =-{N_c\alpha Q_f v_f^Z v_e^Z m_f\over64\pi^3m_iM_s^2}
 \begin{pmatrix}C_{s,ji}(a f_4+ib f_3)\\
 C_{s,ij}^*(a f_4-ib f_3)\end{pmatrix}.
\]
Signs and normalization reproduce the neutral Z parts of corrected
[2410.17313v4, Eqs.53–54](https://arxiv.org/html/2410.17313v4), separately
from the already frozen photon terms. Native diagonal lepton Yukawas are
used, including arbitrary phases, and all nine charged species are kept.
Illustrative light-quark perturbative loops are not hadronic precision.

## F-dependent power counting and a surviving integral

At quadratic Yukawa order, a mixed F–D contribution contains exactly one F
or F*. Under a uniform rephasing of **fermions only**, gauge vertices and
doublet Yukawas conserve fermion lepton number, while F carries two units.
Bosonic Mu4, propagators, seagulls and their mixing do not change this count.
An L-conserving charged-lepton dipole therefore requires equal numbers of
F and F* if no independent Majorana mass is inserted. This excludes the
entire quadratic FD sector, including gauge, pinch and external attachments,
at mν=0. It is not an inference from one one-loop zero. An inserted mν can
balance the spurion, but the radiatively generated mν itself is O(FD);
that mechanism has at least four Yukawas when substituted back.

F*F is allowed. Antisymmetry does not force `(F†F)_ji=0`. The massless
numerator identities `PL /n PL=0`, `PL /n PR≠0` explicitly distinguish
mixed and same-sector contractions. A concrete surviving two-loop parent
is the charged-scalar/neutrino F² dipole with a W–charged-lepton self-energy
inserted on its internal neutrino. For ξW=1 and a massless charged lepton,
\[
 \gamma^\mu\not l\gamma_\mu P_L=(2-d)\not lP_L,\qquad
 \Delta=xM_W^2-x(1-x)p^2.
\]
Strip the common g2²/(32π²) and self-energy action phase. The reduced
coefficient of `/p PL` in DR is
\[
 B(p^2)=-{1\over\epsilon}+1+
 2\int_0^1dx\,x\log{\Delta\over\mu_R^2}+O(\epsilon).
\]
The +1 is the ε×UV rational contribution. At p²=−MW², μR²=MW²,
`B_fin=4 log 2−2=0.772588722239781`; its UV pole is −1. The nonlocal
momentum dependence cannot be replaced by a constant or a physical zero.
This subgraph is gauge/scheme dependent and has **no** released Wilson
coefficient. Its external-emission, charged/Goldstone, counterterm and LSZ
partners still need calculation. A massless-neutrino approximation is no
justification for dropping the whole F†F sector.

## Concrete W reduction attempt and exact obstruction

The saved native parent was expanded in both external momenta, keeping its
unpinched charged-lepton propagator. With x=l², y=r², z=l·r, a=l·p,
b=l·q, c=r·p, its denominator family is
\[
 (x-M_W^2)(x-2b-M_W^2)(x+y-2z-M_W^2)
 (x-2a)(y-M_s^2)(y-2c).
\]
`w_outer_reduction.py` differentiates its actual rational denominators and
independently verifies the p q coefficient by a geometric-product expansion.
Partial fractions produce sunset families with a `(l−r)²−MW²` line; e.g.
the zeroth coefficient becomes
\[
 {1\over M_s^2\,l^2(l^2-M_W^2)^2[(l-r)^2-M_W^2]}
 \left({1\over r^2-M_s^2}-{1\over r^2}\right).
\]
This reduces a real missing parent, rather than requesting an unknown
compensator. The numerator still needs an open-Dirac d-dimensional dipole
projection and IBP reduction, including ε terms in subdivergences. Performing
the outer integral on a four-dimensional fixed-r finite result loses those
terms. Crossed scalar placement, physical charged parents, native BRST
insertion `−b_mu b_beta/xi`, reducible terms and LSZ must then be summed in
one renormalization scheme. Their projected values have not been derived.
No service or missing installation is being blamed for this mathematical
blocker, and no compensator was defined as minus a measured gauge variation.

The executable reproducer also evaluates the actual saved parent at three
ξ values and independent complex external vertices; these unintegrated
values are not physical dipoles or a gauge-independence test. Run

```bash
python -m research.wgamma_d16.w_outer_reduction --output research/wgamma_d16/local/w_outer_reduction.json --require-completion
```

It writes the exact attempted reduction and returns 2. The minimum next
calculation is that numerator/master reduction **together with** its crossed,
charged and LSZ set. Completing only an isolated vacuum integral cannot
establish full acceptance.
