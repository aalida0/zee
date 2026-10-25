# Gate A2: native vertices and conditional dipole projection

Outcome: **PARTIAL**, `MATCHING_CONVENTION_UNKNOWN`. Native tree matching
passes. An independent leading dipole projection passes **under the explicit
conventions below**. Exact attribution of all those conventions to the pinned
2026/HyperIso implementation remains blocked; no Eq. (4) diagnostic is enabled.
Production LO physics, the frozen SARAH model and Modules 0–4 are unchanged.

## Native evidence

Mathematica 15.0.1 / SARAH 4.15.4 genuinely start the frozen `ZeeTypeII` model.
The original 58 queries and three additional scalar photon queries evaluate.
Raw output, numerical coefficients and logs remain in ignored
`validation/module5/local/`. The numerical export hashes its driver, raw JSON
and input rules; failed reruns remove old numerical output.

Suppressing the color delta, native all-incoming rules are

```
bar[Fu_a] Fd_b H_k+:
 PL: +i ZP[k,2] sum_rs conj[Uu[a,r]] Yu[r,s] conj[Vd[b,s]]
 PR: -i ZP[k,1] sum_rs Vu[a,s] conj[Yd[r,s]] Ud[b,r]
bar[Fd_b] Fu_a H_k-:
 PL: -i ZP[k,1] sum_rs conj[Ud[b,r]] Yd[r,s] conj[Vu[a,s]]
 PR: +i ZP[k,2] sum_rs Vd[b,s] conj[Yu[r,s]] Uu[a,r]
```

Here `Hm` is negative; `conj[Hm]` is positive. With
`conj[Uq] Yq conj[Vq]^T = sqrt(2) diag(mq)/vq`, define
`V = Vu conj[Vd]^T`. Thus the positive rule is
`i sqrt(2)/v V_ab (mu_a Y_k PL + md_b X_k PR)`;
the negative rule is `i sqrt(2)/v V_ab* (md_b X_k PL + mu_a Y_k PR)`.
The latter equals minus the conjugate positive coefficients with PL/PR
exchanged: conjugate the **Lagrangian**, then multiply by i.

`X=-ZP[k,1]/cos(beta)`, `Y=ZP[k,2]/sin(beta)` give
Goldstone `(-1,1)` and physical states
`(X,Y)=a_k(tan(beta),cot(beta))`, `a=(cos(gamma),-sin(gamma))`.
The top loop product is `V_ts* V_tb`, conjugated in the reverse decay.
No CKM factor is replaced by 1.

Using `g1 cos(thetaW)=g2 sin(thetaW)=e`, native vector currents are
`-i e Qq gamma^mu` with `Qu=2/3`, `Qd=-1/3`, and
`-i gs (Lam^a/2) gamma^mu`. The scalar current is
`-i e [p(H+) - p(H-)]^mu`; the singlet has the same unit charge.
For internal negative scalar flow this is `+i e (p+p'-2k)^mu`.
There is no colored scalar: the gluon attaches to the top line.

Eight witnesses use distinct nonzero quark masses, independent complex
right rotations, a complex common left rotation and CKM phase 1.13.
Additional cases set up/down masses to zero separately, gamma to 0/pi/2,
beta to .31/1.41 and exchange the physical rows. All 952 complex
coefficients pass; maximum absolute residual `8.909917792212513e-16`.
The base CKM product is `-0.1709236243675297+0.01771288625595481 i`.
Nondegenerate charged masses 550/900 GeV enter the loop witnesses, not
the mass-independent tree vertices. Exact beta endpoints are singular
Yukawa limits and are not evaluated at fixed nonzero quark masses.

## Independent loop reduction (retained leading top / ms=0 approximation)

Adopt metric `(+---)`, `sigma^{mu nu}=i[gamma^mu,gamma^nu]/2`,
`gamma5=i gamma0 gamma1 gamma2 gamma3`, `PR,L=(1+,-gamma5)/2`.
Write `p=p'+q`, `p^2=mb^2`, `p'^2=q^2=0`, outgoing photon
`<gamma|A(x)|0>=epsilon* exp(+iqx)` and
`F_mu_nu=+i(q_mu epsilon*_nu-q_nu epsilon*_mu)`.
Then `bar s_L sigma b_R = bar s sigma PR b`; no additional factor 1/2
or gamma5 remains. Antisymmetry supplies the factor **two** in sigma F.

Let `kappa=4 GF/sqrt(2) Vtb Vts*=2 Vtb Vts*/v^2` and assume
`H_eff=-kappa sum C_i Q_i`, `L_eff=-H_eff` for this interaction.
The one-photon operator gives

`iM_eff = +2 kappa e mb/(16 pi^2) C7 bar s sigma^{mu nu} q_nu PR b epsilon*_mu`.

The gluon replaces `e` by `gs` and inserts `T^a=Lam^a/2` on the open
quark line, without an extra Casimir. The h.c. has PL and conjugate CKM.

Here is the numerator reduction used to derive, rather than assume, the
integrands. Set top-diagram Feynman weights `alpha,betaP,z=1-alpha-betaP`,
shifted top momenta `At=(1-alpha)p'-betaP p`,
`Ab=-alpha p'+(1-betaP)p`. With vertices
`i(a PL+b PR)`, `i(a* PR+b* PL)`, the internal-flip numerator is
`mt (/At gamma^mu + gamma^mu /Ab) PR`. Between on-shell spinors it is

`mt[-2 betaP p^mu PR -2 alpha p'^mu PR + mb gamma^mu PL]`.

The external-flip numerator `/At gamma^mu /Ab PL + mt^2 gamma^mu PL`
reduces to

`2 mb[alpha betaP p'^mu-betaP(1-betaP)p^mu] PR`
`+ [mt^2+mb^2 betaP z] gamma^mu PL`.

For the scalar attachment set `A=alpha p+betaP p'`,
`Vscalar=p+p'-2A`. The corresponding numerators reduce to
`mt Vscalar^mu PR` and `mb alpha Vscalar^mu PR`.
Terms quadratic in shifted loop momentum contribute only gamma^mu.
The on-shell Ward identity fixes that vector term; the coefficient B
of `(p+p')^mu PR` fixes the transverse dipole via

`(p+p')^mu PR = i sigma^{mu nu} q_nu PR + mb gamma^mu PL`

between on-shell spinors. External-leg/vector counterterms carry no
independent transverse dipole in this on-shell projection. This is a
leading expansion in external masses/momenta over internal masses;
denominators omit external mb^2, whereas the leading chirality flip is kept.

The two Yukawa vertices, three propagators and gauge vertex give
`+e Qt` for the top diagram and `-e` for the scalar diagram before
integration, in the momentum routing just specified. The scalar vertex's
momentum sign must be retained. There is no closed-fermion-loop minus.
With the Feynman 2! included,
`2! integral d^4l/(2pi)^4 (l^2-Delta+i0)^-3 = -i/(16pi^2 Delta)`.

Let `x=mt^2/M^2`, `D=1+(x-1)t`, with t the total top weight.
Integrating the other simplex weight gives the four diagram projections

```
top_YY    = -x/4 integral t^2(1-t)/D dt
scalar_YY = -x/4 integral t(1-t)^2/D dt
top_XY    = -x/2 integral t^2/D dt
scalar_XY = -x/2 integral t(1-t)/D dt
C7 = |Y|^2 [Qt top_YY + scalar_YY] + X Y* [Qt top_XY + scalar_XY]
C8 = |Y|^2 top_YY + X Y* top_XY
```

All integrals run from 0 to 1. In particular B is positive imaginary
times these positive parameter integrals before conversion with the Gordon
identity; conversion to the displayed effective amplitude yields the negative
Wilson signs above. This sign follows from vertices, propagators, loop
integration and operator insertion, rather than agreement of scalar formulas.
With `Qt=2/3`, integration reproduces `F7_1/3,F8_1/3,F7_2,F8_2`.
The executable audit uses the four diagram integrals, never their rational/log
form. Twenty explicit Dirac-matrix on-shell comparisons check the numerator
and Gordon reductions; 70-digit integration checks 32 kernel values.
These checks establish the stated projection, not a full SM or finite-ms result.

## Pinned sources and remaining closure gap

- [Misiak et al. 2608.29863v1](https://arxiv.org/html/2608.29863v1),
  Section II Eq. (2), explicitly fixes Q7/Q8 with `mb/(16pi^2)` and
  `bar s_L sigma b_R`. Section IV Eq. (4) uses ordinary matching-scale
  shifts at 160 GeV. The inspected Letter does **not explicitly define**
  its Hamiltonian sign or sigma commutator/Fourier convention. The
  conventions used in the derivation above therefore remain assumptions
  in the exact source-to-amplitude comparison.
- [HyperIso pinned source](https://github.com/Hyperiso/Hyperiso/tree/09d26ac6e71d1528922097a896d15693589f636b):
  `docs/main.tex:696-708` prints the assumed negative Hamiltonian and an
  alpha_s/(4pi) coefficient expansion; line 697 contains an editorial
  `Check sign`. It does not explicitly give O7/O8 and sigma definitions
  in this section. `BWilsonTHDM.cpp:151-156,217-222` implements
  `lu^2 F_i_1/3-lu ld F_i_2`. Real `lu=Y,ld=-X` agrees algebraically;
  this real-only API supplies no complex CKM/phase amplitude witness.
  `THDMParametersHelper.cpp:65` uses the running matching top mass and
  one `MASS[37]`. These facts cannot certify the executable operator
  insertion/observable convention. No correction factor is inferred from
  the editorial note. Four source hashes agree with Gate A's evidence.
- Gate A's already validated historical references remain SuperIso v3.0
  0808.3144v3 Appendix C.2 Eqs. (48)–(50), and Florentino/Romao/Silva
  2106.08332v1 Section IV.C.1 Eqs. (62)–(63), Appendix A.3 (A6)–(A7).
  They are comparison targets, not the origin of this loop projection.

In the retained alpha_s^0 charged-scalar dipole approximation, no new
four-quark coefficients enter the finite effective-coefficient redefinition:
`Delta C7eff=Delta C7`, `Delta C8eff=Delta C8`. This is not an identity
for total SM coefficients or higher-order NP matching. The projection
omits ms-suppressed primed terms and internal light-quark contributions;
the native tree check itself retains all masses and arbitrary complex rotations.

Falsifiers passed: native rule sign, PL/PR swap, conjugate CKM, wrong photon
charge, wrong scalar charge, photon/gluon exchange, factor-two removal,
state interchange, gamma endpoints, beta limits, heavy-state decoupling,
and Goldstone versus physical XY sign. The Goldstone alone is not the SM
amplitude and is never added to NP. The scale test confirms that changing
only the scale label does not run mt. HyperIso R1/R6 specify 81 GeV and
cannot be substituted into Eq. (4); no scale conversion or R1/R3/R6 runtime
test has been performed. An overall external **operator** sign change is
still indistinguishable without the missing source/implementation closure.

Consequently A2.1 is PASS; A2.2 is PARTIAL (conditional amplitude check
PASS, exact external convention gate BLOCKED); A2.3 is BLOCKED. The next
necessary evidence is an explicit pinned operator/convention definition
or trusted executable amplitude insertion linking the 2026 and HyperIso
coefficients to the conventions above. Gate B runtime remains separate.
No BR, exclusion, two-state mass cut or uncertainty/likelihood is computed.
Numerical residuals are not theory uncertainties. NP NLO, running-mass
calibration, higher powers and finite-ms terms are uncomputed.

## Reproduce

```sh
python scripts/zee_module5_native_compare.py --prepare
/usr/local/bin/math -script scripts/zee_module5_charged_quark_vertices.m
python scripts/validate_zee_module5_native.py validation/module5/local/charged_quark_vertices.json
python scripts/zee_module5_native_compare.py --check
python scripts/validate_zee_module5_matching.py
```

The last command runs both required suites and both new amplitude suites,
records actual residuals and hashes in `validation/module5/native_matching.json`,
and fails if tests fail or native evidence is absent/stale. Detailed local files
are required to reproduce the live tests; absent files are explicitly skipped
by standalone test discovery and cannot produce a native physics PASS.
