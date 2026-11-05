# Regulated WWW outer parent (continuation of ne829da1)

**TOPOLOGY_ONLY, ξW=1.** This is a new integrated two-loop Pauli form
factor, not a physical W-class coefficient. Full gauge completion is open.
Historical inner calculations and common-2HDM results were not rerun.

## Native open line and projection

Use the momentum routing of `parent_integrals.exact_parent_integrand`,
`n=p-l`, and the native numerator

\[
 N^\mu=-({\not l}+{\not q}){\not n}\gamma^\mu
 +(2-d)(2l-q)^\mu{\not n}
 +\gamma^\mu{\not n}(2{\not q}-{\not l}).
\]

The saved native WWW product is **+2 MW² N PL** when its common
`e g2² κ/(2v)` is stripped. A direct matrix test fixes that sign.
Expand the *entire* `N PL (slash(p-r)+mi) X` numerator and all six
propagators to external degree one, with independent p and q. The mass
term contributes a vector form factor; its degree-one momentum correction
has an odd vacuum tensor and cannot contribute to the leading Pauli form
factor. The unpinched charged propagator is retained. Open-line γ5 is
anticommuting; no anomalous trace occurs in this topology.

FeynCalc 10.2.1 `FCMultiLoopTID` aborts on this parent (`Contract::fail`).
The reproducible alternative uses its `Uncontract`, `Tdec` and
`DiracSimplify`, with d retained throughout; no homemade IBP solver is used.
The exact p/q polynomial coefficients are saved in `w_outer_evidence.json`.
Writing the integrated numerator as

\[
 a_p\gamma^\mu\not p+b_p\not p\gamma^\mu+c_pp^\mu
 +a_q\gamma^\mu\not q+b_q\not q\gamma^\mu+c_qq^\mu,
\]

on-shell unequal-mass Dirac equations and the chiral Gordon identity give
the coefficient of **i σμν qν PR** as `cp/2+bp+bq-aq`. Vector and qμ
form factors are kept distinct: an isolated non-Ward-complete parent cannot
be matched by projecting only a real-photon helicity amplitude.

Set x=l², y=r², z=l·r, w=MW². The resulting d-dependent rational
numerator is supplied explicitly by `dipole_numerator()` and checked
symbolically against the independent FeynCalc output. Its finite d=4 limit is

\[
 P_4={x\over3}+3z-{4z^2\over3y}+{wz\over x-w},\qquad
 I_W=\int_{l,r}^{\rm PV}{P_d\over
 x y(x-w)^2(y-M_s^2)[(l-r)^2-w]}.
\]

This is a leading external-invariant expansion, with mν=0. It preserves
external flavor order and both scalar Yukawa entries. The parent with the
scalar on the opposite end follows by Hermitian line reversal, q→−q and
flavor exchange; the real master then multiplies YL instead of YR. This is
a line-reversal relation, not a second independent integration or a test of
the other charged/Goldstone diagrams.

## IBP and poles

Partial fractions leave only two-loop vacuum sunsets and factorized
tadpoles. TARCER 2.0 reduces all repeated indices to five products/masters:
`Ah Aw`, `Aw²`, `S(w,0,0)`, `S(w,Ms²,0)`, `S(w,w,Ms²)`.
Exact rational d-dependent coefficients are in the evidence JSON. Its
Källén chart is singular at Ms²=4w; the direct integral remains regular.
No exceptional-chart coefficient is silently evaluated or clamped.

TARCER uses raw π-normalized loop measures: its tadpole is i times the
PV tadpole, and its raw sunset is minus the PV sunset. These phases are
converted explicitly in `w_master_reduction.m`.

The independent Euclidean sunset evaluation retains both UV orders. In
six Hepp sectors its parameter integral is

\[
 e^{2\gamma_E\epsilon}\Gamma(-1+2\epsilon)
 \sum_{(a,b,c)}\int_0^1dt\,dv\,t^{-1+\epsilon}
 { [a+t(b+vc)]^{1-2\epsilon}\over(1+v+tv)^{2-\epsilon}}.
\]

Subtract the t=0 endpoint before expanding. With
`F=M/B²`, `L=log B−2 log M`, the three parameter coefficients are
`I[-1]=sum a`, `I[0]=sum integral[F0 L0+(F−F0)/t]`,
`I[1]=sum integral[F0 L0²/2+(FL−F0L0+(F−F0)log t)/t]`.
The sunset coefficients are
`−I[-1]/2`, `−I[0]/2−I[-1]`,
`−I[1]/2−I[0]−(2+ζ2)I[-1]`.
Zero-mass endpoints are evaluated by their continuous zero limits.
The single-mass master independently equals
`(−1/2,−3/2,−7/2−π²/4)` at unit mass and scale.
Tadpoles retain O(ε); rational reduction coefficients retain O(ε²).
The combined **1/ε² and 1/ε coefficients cancel identically**, including
the d-dependent projection. Finite individual master values, poles and
propagated quadrature estimates are recorded separately.

## Independent finite integral and sign

Subgraph and overall power counting of the projected integral establish
UV convergence; the Taylor-expanded massless lines are IR integrable.
Only after that proof may its d=4 limit be used for a second integration.
With Euclidean x,y>0, A=x+y+w, T=A+sqrt(A²−4xy), angular integration gives

\[
 I_W=\int_0^\infty dx\,dy\,
 {2xy\over T^2(x+w)^2(y+M_s^2)}
 \left[{4x\over3T}-3+{w\over x+w}\right].
\]

This representation calls neither TARCER nor a sunset master. Its integrand
is negative for positive masses. In units MW² I_W the two witnesses give
−0.544417391141419 (Ms=125 GeV) and −0.306387593731176
(Ms=310 GeV), MW=80.379 GeV. Differences from the sector/IBP route are
1.32e−13 and 2.24e−10, within propagated quadrature estimates.

The remaining outer scalar propagator/fermion/scalar-Yukawa product is +i;
the two PV loop factors give −1. Thus `iM=−i pref integral N`, and
`integral N=i sigma q IW YR+vector` gives the signed Pauli bookkeeping pair

\[
 C^{\rm WWW,pair}_{L,R}=
 {g_2^2\kappa M_W^2\over v m_i(16\pi^2)^2}
 I_W\,(Y_L,Y_R).
\]

These complex numbers are labeled **topology_C_LR**, never physical_C_LR.
They obey the mass-weighted reversed-flavor relation and scale as mass^-2.
No complete-class gauge cancellation or observable rate is inferred.

## Reproduce and remaining work

Use the official FeynCalc tag `Release-10_2_1` (loader and TARCER source
SHA256 checked by the runner). Keep it outside frozen code; no vendoring.
If necessary load its TARCER add-on once and run `GenerateTarcerMX[]`.

```bash
D16_FEYNCALC_ROOT=/path/to/FeynCalc python -m research.wgamma_d16.reproduce_w_outer
python -m unittest research.wgamma_d16.test_w_outer_projection -v
```

The runner checks every Wolfram result file: a kernel abort can exit zero
without producing one. Detailed logs/masters live in ignored `local/` and
are SHA-bound by the new evidence. No old evidence is overwritten.

The next obstruction is **diagram closure**, not this WWW vacuum master:
all W/G species and both placements, physical charged derivative parents,
pinch, BRST/ghost insertions, external-emission, renormalized self-energies
and LSZ must be calculated in one scheme. Their projected numerators are
not inferred from this ξ=1 result. ξ=.5,1,3 cannot be called a physical
gauge test until that sum exists. F†F and mixed potential-W/fermion-W
classes remain independent missing amplitudes. All full C and BR stay null.
