# Gate A: charged-scalar LO matching

Outcome: `LO_MATCHING_ONLY`; downstream mapping is
`MATCHING_CONVENTION_UNKNOWN`. No branching ratio, exclusion, or globally
accepted Zee point is calculated. Gates B/C are outside this Gate A run.

## Source checks

- [Mahmoudi, arXiv:0808.3144v3](https://arxiv.org/pdf/0808.3144v3),
  SuperIso **v3.0**, Appendix C.2 Eqs. (48)–(50), Table 1: all four
  rational/log kernels agree, including signs and the factor 1/3 for YY.
  The initial candidate's v3.4, C.1.2 and equation references were incorrect.
- [Florentino, Romao, Silva, arXiv:2106.08332v1](https://arxiv.org/pdf/2106.08332v1),
  Appendix **A.3**, Eqs. (A6)–(A7), and Section IV.C.1 Eqs. (62)–(63):
  charged-state couplings and the sum over states are established prior art.
  The initial candidate's Appendix B.3/C references were incorrect.
- [HyperIso v1.0.3](https://github.com/Hyperiso/Hyperiso/tree/v1.0.3)
  annotated tag `5a93aca5e28011df3a348954cdc7c7c330ea2169`, peeled commit
  `09d26ac6e71d1528922097a896d15693589f636b`, resolved with `git ls-remote`.
  Read-only raw source inspection, **not** a checkout/build/runtime test:
  `BWilsonTHDM.cpp` lines 151–156, 217–222 uses
  `lu^2 F_i^(1)/3 - lu ld F_i^(2)`;
  `special_SM.cpp` lines 873–896 has the same four kernels.
  Algebraic identification is `lu=Y`, `ld=-X` for real Type-II couplings.
  `THDMParametersHelper.cpp` line 65 uses the matching top mass divided by
  `MASS[37]`, a single charged-Higgs mass; this does not establish a Zee API.
  The manifest confirms R1/R6 use 81 GeV by default. No R1/R3/R6 was run.

File SHA256 values are in `validation/module5/results.json`. Raw downloads
are temporary audit material, not vendored dependencies.

## Frozen model and signed coefficients

The frozen SARAH Yukawa terms are `-Yd conj[H1].d.q + Yu H2.u.q` plus h.c.;
quarks couple to different doublets. `module4/couplings.py:rotations`
gives physical charged rows
`(-sin(beta) cos(gamma), cos(beta) cos(gamma), sin(gamma))` and
`(sin(beta) sin(gamma), -cos(beta) sin(gamma), cos(gamma))`.
The SARAH basis is `(conj[H1p],conj[H2p],conj[Sp]) -> Hm`;
`Hm[1]` is the Goldstone, `Hm[2,3]` the two physical states.

Thus, with `a=(cos(gamma),-sin(gamma))`, projections give
`X=-ZP[k,1]/cos(beta)=tan(beta) a_k` and
`Y=ZP[k,2]/sin(beta)=cot(beta) a_k` (one-based indices).
For each state the implementation evaluates

`Delta C_i = |Y_k|^2 F_i^(1)(x_k)/3 + X_k Y_k* F_i^(2)(x_k)`,
`x_k=[mt_MSbar(mu0)/mH_k]^2`, and sums over k.

Consequently `XY*=a_k^2`, `|Y|^2=a_k^2 cot(beta)^2`, with positive
mixing weights. The second state's two minus signs do not reverse XY.
All four kernels are negative for positive x, so both coefficients are
negative in this real Type-II convention. No common heavy-mass replacement
or separate one-Higgs mass bound is used.

The orientation `XY*` is source-checked against Eq. (62); real inputs cannot
numerically distinguish it from `X*Y`. The production API rejects complex
inputs and makes **no** claim to validate arbitrary complex Zee couplings.
No archived native charged-quark SARAH vertex was available in this
checkout; the existing Module 4 vertex script queries neutral quarks and
charged leptons, not charged quarks. This audit checks the frozen Yukawa
source and rotation algebra; native amplitude closure remains pending.

## Independent numerical verification

Let `D=1+(x-1)t`. Independent 90-digit quadrature uses

```
F7_1 = -x/4 integral_0^1 t(1-t)(3-t)/D dt
F8_1 = -3x/4 integral_0^1 t^2(1-t)/D dt
F7_2 = -x/6 integral_0^1 t(3-t)/D dt
F8_2 = -x/2 integral_0^1 t^2/D dt
```

Analytic integration gives the published kernels; the integrands also prove
their signs without subtracting nearly equal rational/log terms. At x=1
the values are `(-5/48,-1/16,-7/36,-1/6)` in the order above. Expanding
`(1+t(x-1))^-1` and integrating each polynomial gives the Taylor coefficients.
The candidate's six-degree series/direct switch missed a 2e-11 relative
target at x=1.0442 (F8_1 residual 5.823064253007715e-11).
The revised degree-20 series applies for `|x-1|<0.25`; tests cover both
adjacent floating-point numbers at each switch, and the old failure point.

Checks also cover independent signed two-state coefficients, frozen
rotation projections, degenerate masses, exchanged masses/mixing,
pure-doublet/singlet limits, heavy-mass decoupling, tan(beta) dependence,
complex-input rejection, and CLI rejection of malformed input.
These checks establish numerical consistency on the tested domain, not
uniform accuracy over every finite positive floating-point mass ratio.

## Mass scheme and downstream mapping barrier

The user supplies `mt_MSbar_GeV` **at** `matching_scale_GeV`; the code cannot
infer that scale from a number or convert a pole mass. Changing only the
scale label leaves the coefficients unchanged. The example's 163 GeV at
160 GeV is an illustrative asserted running input, not a calibrated SM
parameter determination. Both states use the same supplied scale.

[Misiak et al., arXiv:2608.29863v1](https://arxiv.org/html/2608.29863v1)
Eq. (2) defines unprimed Q7/Q8 with `e/(16 pi^2)` and `gs/(16 pi^2)`
times `mb sbar_L sigma b_R`. The historical operator also includes an
ms chirality term, which this implementation omits. LO charged-scalar
matching adds no four-quark coefficients in the retained approximation,
so ordinary/effective dipole shifts coincide at this order; this statement
must not be extended to higher orders.

HyperIso's pinned `docs/main.tex` writes the conventional
`-4 GF/sqrt(2) Vtb Vts* sum C_i O_i` Hamiltonian, but retains an explicit
`Check sign` editorial marker. Agreement of its matching kernels alone
does not close operator normalization, sigma/CKM conventions and the
full native vertex-to-Hamiltonian comparison. No numerical conversion
factor is inferred from the historical printed Hamiltonian.
Therefore exact end-to-end matching is **uncertified**. Neither 2026
Eq. (4) nor HyperIso receives these output coefficients.

Next: close the native charged-quark amplitude/operator normalization,
then perform Gate B on the pinned release, including official runtime
references and an actual supported two-state/complex injection audit.
Only after that mapping may Gate C evaluate a conditional linear screen.
Legacy SuperIso NLO context bugs/NNLO differences are historical unresolved
issues; no old runtime comparison was repeated and no additive BR shift
was made. No uncertainty covariance or likelihood is constructed.
