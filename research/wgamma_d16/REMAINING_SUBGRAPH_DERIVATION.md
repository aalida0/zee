# Continued W/G, F†F and neutral-mixing calculations

These are calculated topologies/subgraphs, **not complete physical classes**.
No full Wilson coefficient or branching ratio is released.

## GWW outer parent and its subdivergence

The next native species in `parent_integrals` has a Goldstone on the
scalar-to-photon edge, with W on both charged-current edges. Its signed
numerator, stripping `e g2² κ/(2v)`, is

\[
 +M_W^2\gamma^\mu\not{(p-l)}\not{(l+r)}P_L.
\]

A direct comparison to the native tensor product fixes the plus sign. The
same full numerator/denominator Taylor expansion, independent p/q on-shell
projection and FeynCalc d-dimensional tensor decomposition as for WWW gives

\[
 P_d^{GWW}={2x(y+z)\over d(w-x)}.
\]

TARCER reduces the actual six-propagator integral to the same five master
products. Unlike WWW its Laurent coefficients are **(0,1/4,finite)** in
units MW²; the single pole is independent of Ms². The r→∞ subloop has
logarithmic UV degree. Thus an unregulated four-dimensional GWW integral
is invalid. No pole is dropped or canceled by an invented compensator.

For a separate finite check, subtract two scalar masses **within the same
bare topology**, not two gauge-dependent physical models. Its exact UV
asymptote cancels. Put h=Ms²/MW², h0=2, and dimensionless Euclidean x,y.
With `T=x+y+1+sqrt((x−y)²+2(x+y)+1)`, independently integrate

\[
 M_W^2[I_{GWW}(h)-I_{GWW}(h_0)] =\int_0^\infty dx\,dy\,
 {xy(T+x)(h_0-h)\over T^2(x+1)^3(y+h)(y+h_0)}.
\]

This agrees with the difference of the TARCER/sector-subtracted finite
parts at both nondegenerate witnesses. Individual poles/finite parts,
errors and exact source hashes are in `gww_outer_evidence.json`. Tadpole
O(ε) and reduction-coefficient O(ε²) terms are retained as in the WWW
calculation. This mass-difference check is neither a renormalized amplitude
nor the task's matched Zee-minus-2HDM subtraction.

```bash
D16_FEYNCALC_ROOT=/path/to/FeynCalc python -m research.wgamma_d16.reproduce_gww_outer
```

The attempted pole-cancellation falsifier initially raised
`GWW poles do not cancel`: exact reduction gives 1/4, not zero.
The executable test now requires that nonzero pole and independently checks
the finite difference. This is a concrete unresolved renormalization
contribution for the complete W/Goldstone/LSZ sum.

## F†F: general-Rξ neutrino insertion

Continue the established nonlocal neutrino W self-energy with the same
stripped `g2²/(32π²)` and action convention. Internal charged-lepton and
neutrino masses are zero. Goldstone fermion couplings then vanish; ghosts
have no direct neutrino coupling. This closes this *two-point subgraph*,
not the two-loop dipole. For k=p−l the open-line identity is

\[
 \not k\not l\not k=\not p\not l\not p-2l^2\not p+l^2\not l.
\]

Partial fractions of the longitudinal W propagator give
`−[1/(k²−w)−1/(k²−ξw)]/w`. Define

\[
 V_M={1\over2\epsilon}-\int_0^1dx\,x\log{\Delta_M\over\mu_R^2},
 \quad A_M=M^2\left[{1\over\epsilon}+1-\log{M^2\over\mu_R^2}\right],
 \quad\Delta_M=x M^2-x(1-x)p^2.
\]

The longitudinal coefficient is
`−{p²[V_MW−V_sqrtξMW]−[A_MW−A_sqrtξMW]}/w`.
Combining it with the transverse `(2−d) VM_W` gives

\[
 B_\xi=-{\xi\over\epsilon}+1+
 2\int_0^1dx\,x\log{\Delta_{MW}\over\mu_R^2}
 +{p^2\over w}\int_0^1dx\,x\log{\Delta_{MW}\over\Delta_{\sqrt\xi MW}}
 +1-\log{w\over\mu_R^2}-\xi\left[1-\log{\xi w\over\mu_R^2}\right].
\]

The rational +1 from ε×UV is retained. At ξ=1 this reproduces the
established result. At p²=−w, μR²=w the finite values for ξ=.5,1,3,7 are
0.679086005312, 0.772588722240, 2.532893951073, 9.253625043019.
The UV pole and finite part are gauge dependent. Their scale derivative
is independently tested as `d Bfin/d log μR²=−ξ`. MSbar subtraction of this
subgraph is specified, but **no complete Zee electroweak/Yukawa/neutrino
renormalization scheme has been implemented**.

The missing F†F amplitude includes emission from the internal W and charged
lepton as well as the outer charged scalar, corrections to F vertices and
charged propagators, neutral-current partners where required, external
wavefunctions and counterterms. Inserting only Bξ in the frozen F†F
one-loop parent cannot supply that sum. `f_neutrino_rxi.py` leaves
`physical_C_LR=null`; it supplies no new coherent dipole row.

## Charged-scalar-only A–Z/G0 mixing: a proved zero subset

In the charged Higgs basis (G+,HD+,S+), native potential differentiation gives

\[
 G_A=i\begin{pmatrix}0&-\delta v/2&-\mu\\
 \delta v/2&0&0\\\mu&0&0\end{pmatrix},\quad
 G_{G0}=i\begin{pmatrix}0&0&0\\0&0&\mu\\0&-\mu&0\end{pmatrix},
 \quad\delta=\lambda_4-\lambda_5,\ \mu=\mu_4/\sqrt2.
\]

The Z generator is diagonal here, with equal doublet charges. Physical
mixing acts only in the (HD,S) block. Consequently GA remains strictly
Goldstone-to-physical, whereas Z and GG0 are block diagonal. For arbitrary
diagonal mass/propagator functions f,g (including unequal Goldstone and
physical masses), **Tr[GA f TZ g]=Tr[GA f GG0 g]=0** before integration.
Photon insertions Q=I preserve this disjoint support. External photon
attachments to these zero two-point insertions also vanish.

`neutral_mixing_support.py` proves both identities symbolically; tests also
use the actual frozen reconstructed potentials at both mixed witnesses,
with nonzero A-G-H and nonzero physical G0 couplings. This zero does not
eliminate A-G-H loops with W, fermion A-Z/G0 mixing, or their reducible/LSZ
partners. The complete neutral-mixing/reducible gate remains UNKNOWN.

## Validation and technical boundary

```bash
python -m unittest research.wgamma_d16.test_w_outer_projection research.wgamma_d16.test_remaining_subgraphs research.wgamma_d16.test_zee_two_loop -v
```

There is still no independently calculated ξ=.5,1,3 **full** chiral W sum,
no full F†F sum, and no mixed potential-W/charged-fermion-W closure. The
explicit GWW pole is an executable counterexample to using the two new
parents as a finite gauge-complete answer. The minimum next calculation
is the remaining native open-line numerators together with their actual
counterterm/LSZ contributions in a fixed scheme; their coefficients cannot
be recovered by fitting gauge variation or a published complete kernel.
Original modules, author sources and validated historical results remain
unchanged. No new full-rate or exclusion claim is made.
