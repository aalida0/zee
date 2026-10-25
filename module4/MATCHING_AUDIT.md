# Signed photon matching audit, revision 2

Fermion/photon matching is **VALIDATION_PASS** in the frozen operator and
external-mass expansion. Its coefficients are included coherently. The
mass/Yukawa scheme is still nominal, so the topology and overall prediction
remain PARTIAL. W matching is **BLOCKED_GAUGE_MATCHING**; no W coefficient is
included. This audit supersedes the earlier blanket quarantine, while
retaining the literal Davidson comparison as a reproducible source conflict.
No frozen file or definition is changed. The subsequent charged-scalar
matching is in [CHARGED_SCALAR_AUDIT.md](CHARGED_SCALAR_AUDIT.md); the
fermion derivation and blocked W matching below are unchanged.

## 1. Sources actually compared

Exact PDF SHA256 pins and versions are in `sources.json`; PDFs, page renders
and extracted text are in ignored `validation/module4/local/`.

| Source | Equations used | What is compared |
|---|---|---|
| Davidson, EPJC76(2016)258, 1601.01949 | 15,16,18,21,23,24 | Native Yukawa dictionary, Lagrangian A-to-C conversion, literal one/two-loop signs |
| Ilisie, JHEP04(2015)077, 1502.04199 | 4,9,11,12,19,21,25,26,28 | Signed effective triangle, diagonal moment, W effective form factor |
| Athron et al., EPJC82(2022)229, 2110.13238v3 | 51–54,63–65 | Independent neutral photon contribution and Phi/dilog kernels |
| Chang, Chang, Chou, Keung, PRD63(2001)091301, hep-ph/0009292v3 | 6–10 | Independent axial triangle and positive pseudoscalar moment; scalar sign discussed preceding Eq.6 |
| Chang, Hou, Keung, PRD48(1993)217, hep-ph/9302267 | 6–19 | Reduced transition amplitudes, complex chiral structure, W/photon diagram classes |
| Abe et al., JHEP01(2014)106, 1311.4704v3 (2016 corrections) | 3.8–3.16,B.7–B.8 | Off-shell W tensors and explicit pinch cancellation |
| Athron et al., JHEP01(2022)037, 2111.10464v2 | B.27,B.28 | Auxiliary LFV comparison; this is JHEP, not the requested EPJC paper |

The 2022 EPJC and independent PRD identifiers above are the resolved working
interpretation of the request. No GM2Calc binary or historical scan is run;
the independent EPJC equations are evaluated directly, separating photon
from Z exchange and omitting its SM subtraction for this component check.

## 2. Fixed field, charge and operator conventions

Use metric (+---), epsilon^0123=+1, gamma5=i gamma0 gamma1 gamma2 gamma3,
PL/R=(1-/+gamma5)/2, sigma^mu nu=i[gamma^mu,gamma^nu]/2, e>0,
F_mu nu=partial_mu A_nu-partial_nu A_mu. Gamma traces include
`tr(gamma0 gamma1 gamma2 gamma3 gamma5)=-4i`.

The actual native SARAH rules, now including fermion/photon vertices, are

```
s bar(l_j) l_i : -i X_ji, X_ji=C_s[j,i] PL + C_s[i,j]* PR
s bar(f) f    : -i (a-i b gamma5), C_s[f,f]=a+i b
A_mu bar(f) f : -i e Q_f gamma_mu
Q_e=Q_mu=Q_tau=-1; Q_up=+2/3; Q_down=-1/3.
```

Both photon chiralities are checked: SARAH gives +i e for charged leptons,
-2i e/3 for up quarks, +i e/3 for down quarks. The same real e is used in
the Module3 operator. The native h/H/A matrices, Type-II quark couplings and
both charged Hermitian orientations remain those in `CONVENTIONS.md`.

For an **emitted** photon, q=p_i-p_j, the created photon field has wave
exp(+i q.x). Substitution of its F_mu nu into i L_eff gives

```
i M_operator = +e m_i epsilon_mu* q_nu
                ubar_j sigma^mu nu (CL PL+CR PR) u_i.
```

This sign is checked directly with the gamma matrices, not inferred from a
rate. Dirac conjugation obeys gamma0 sigma^dag gamma0=sigma and
gamma0 PR gamma0=PL. Consequently conjugating Davidson Eq.16 sends AL to CL
and AR to CR, without swapping labels:

```
CL = -4 sqrt(2) GF/e AL*, CR = -4 sqrt(2) GF/e AR*.
```

This conversion itself is unchanged. A common field rephasing flips both
ends of a real scalar exchange and cannot change a dipole sign.

## 3. Factorized fermion two-loop derivation

Route the virtual photon **out of** the inner triangle into the external
lepton line with momentum k. The source effective vertex defines the real
photon as **incoming** q_in; for the decay q_in=-q. Keeping a source's
incoming photon tensor while using an outgoing dipole vertex loses a minus.

With u=x(1-x), the two orientations of the closed fermion loop give

```
i Gamma^mu nu = i T^mu nu(k,q_in) S(k^2)
             + i epsilon^mu nu rho sigma k_rho q_in_sigma P(k^2)
T^mu nu(k,q_in)=g^mu nu k.q_in-k^mu q_in^nu
S(k^2)=alpha Nc Q_f^2 m_f a/pi integral_0^1 (1-2u)/(m_f^2-u k^2) dx
P(k^2)=alpha Nc Q_f^2 m_f b/pi integral_0^1 1/(m_f^2-u k^2) dx.
```

The signed triangle reduction uses the native scalar vertex
`-i(a-i b gamma5)` and two `-i e Q_f gamma` vertices. The closed fermion
loop contributes -1 and there are three i(/ell+m)/(ell^2-m^2+i0)
propagators. Their combined prefactor for the scalar trace is -e^2 Q_f^2 a
before the momentum integral. The four-gamma trace supplies the scalar
weight 1-2u; the gamma5 trace supplies the epsilon tensor and unit weight.
The reversed two-photon orientation equals the first: two vector currents
give no Furry cancellation. The factor two is already in S,P and is never
multiplied in again. The color trace is Nc. At k^2=0 these reduce to
S=2 alpha Nc Q_f^2 a/(3 pi m_f), P=alpha Nc Q_f^2 b/(pi m_f).
Ilisie Eqs.11,12 and the independently normalized PRD axial form factor
Eq.8 provide the same S,P. This inner one-loop reduction is source checked;
the independently executable new calculation is the outer matching below.

Attach the scalar and photon in **both** orders on the external fermion
line, retaining the Yukawa chirality and dropping external invariants in
denominators. The numerator is

```
X /k gamma_nu + gamma_nu (-/k) X = X [/k,gamma_nu].
```

It is a commutator, not twice one attachment. After q_in=-q and Wick
rotation, at Euclidean K^2=1 the exact angular average is

```
< X [/k,gamma_nu] T^mu nu(k,-q) > = +i sigma^mu nu q_nu X
< X [/k,gamma_nu] epsilon^mu nu rho sigma k_rho (-q)_sigma >
                                      = (scalar result) (-i gamma5).
```

`matching_audit.outer_projection` checks these matrix identities for
independent complex left/right couplings and momenta. Thus the inner
pseudoscalar multiplies +i b on PL and -i b on PR. No diagonal-limit
assumption was used to route chirality or choose the relative i.

All six remaining i factors can also be kept explicitly:

| Outer ingredient | Factor |
|---|---|
| External lepton/photon | -i e Q_l gamma, Q_l=-1 |
| LFV Yukawa | -i X |
| Internal external-line fermion | i /k / k^2 |
| Virtual photon propagator | -i g/k^2 |
| Scalar propagator | i/(k^2-M_s^2) |
| Inner effective vertex | i times the incoming-photon tensors above |

Their scalar i-factor product is +1. The angular numerator, Wick measure i,
and the minus from k^2-M_s^2 leave **+e Q_l** times the positive Euclidean
radial integral. Since Q_l=-1, the dipole coefficient is negative for a
positive product of scalar Yukawas. This is an action/charge calculation,
not selection of the sign which agrees with a plotted moment.

The remaining radial integral is elementary and positive:

```
J(u)=integral_0^infinity dt/[(t+M_s^2)(m_f^2+u t)]
    =log[m_f^2/(u M_s^2)]/(m_f^2-u M_s^2)
f(z)=m_f^2/2 integral (1-2u) J(u) dx
g(z)=m_f^2/2 integral J(u) dx, z=m_f^2/M_s^2.
```

The executable independent integral uses t/M_s^2=y/(1-y), giving
`f,g=z/2 integral dx dy (1-2u,1)/[z(1-y)+u y]`; it does not call a
logarithmic or analytic Barr–Zee kernel. Both integrals are positive.
Matching to the emitted operator therefore gives

```
CL(f,s)=-alpha Nc Q_f^2/(8 pi^3 m_i m_f)
         C_s[j,i] (a f(z)+i b g(z))
CR(f,s)=-alpha Nc Q_f^2/(8 pi^3 m_i m_f)
         C_s[i,j]* (a f(z)-i b g(z)).
```

The dimension is GeV^-2. External flavor ordering, its conjugate reverse
channel, and the two chiralities are kept separately. Rephasing gives
P_j* P_i for either coefficient; diagonal internal vertices are invariant.

## 4. Diagonal and source comparisons; disposition of the -1

For C_ll=a_l+i b_l, use the frozen diagonal continuation once:

```
a_l = m_l^2 Re(CL+CR)
    =alpha Nc Q_f^2 m_l/(4 pi^3 m_f)
       [-a_l(Yukawa) a_f f(z)+b_l(Yukawa) b_f g(z)].
```

Hence a real scalar is negative and a pseudoscalar with same-sign axial
couplings is positive. Ilisie uses y_f in front of PR, so
`y_f=v C_ff*/m_f`; its F1=-f, F1_tilde=g reproduce the equation including
general complex diagonal couplings. No full-model SM subtraction is made.

The 2022 EPJC Phi function is independently evaluated using Eqs.63–65 and
Phi(1,z,z)=Phi(z,z,1). Eqs.53,54 then give `z F_even=-f` and
`z F_odd=+g`. Using mW^2 sW^2=pi alpha v^2 in Eq.51 reproduces the same
prefactor. Its Z term and SM subtraction are deliberately separated.
The independent PRD calculation uses L=+i m_f A_f/v fbar gamma5 f s,
so b_f=m_f A_f/v. Its Eqs.9,10 have `z F(z)=2g(z)` and yield the same
positive axial moment with exactly the same charge/color multiplicities.

Literal Davidson16+21/23, with its declared -i F Yukawa rule and the
Lagrangian conversion in section2, still gives the **opposite** two-loop
coefficient. Eq.18, by contrast, reproduces the positive scalar one-loop
logarithm in Module3. Thus changing one common sigma, e, Hermitian-ordering
or A-to-C convention would break the one-loop comparison: it cannot repair
the relative sign. The fermion/photon diagram set is the same, so omitted
W or Z diagrams cannot explain a factor -1 in this isolated component.

The audit therefore records a **relative source-equation sign conflict**
for the literal Davidson one/two-loop transcription, consistent with a
missing overall two-loop minus under the stated conventions. It does not
assert an author-confirmed erratum or silently alter the primary paper.
The physical implementation is supplied by the explicit outer calculation
above, cross-checked against the three independent signed moment formulas.
The old legacy fermion coefficient happens to have this physical sign,
although its stated A-to-C conversion is wrong; numerical legacy agreement
is a consequence, not the basis for accepting it. No foundation correction
branch is required because no new frozen-stage inconsistency was found.

## 5. W discrepancy: exact origin at the form-factor level

Keep three explicitly different constructions. Let
`G_goldstone=(f-g)/(2z)`, with Haber's h=z^2 d(g/z)/dz (negative).

```
K_CHK    =3 f+23 g/4+3 h/4+G_goldstone       [CHK14+18, Davidson24]
K_Ilisie =15 f/2+2 g+G_goldstone            [Ilisie21,28]
K_Abe    =3 f+5 g+G_goldstone               [soft-photon transverse GammaA, Abe3.9]
```

The Ilisie identity follows by symmetrizing its x-polynomial:
`<x[3x(4x-1)+10]>=19/2-15u`. It is independently integrated before
symmetrization. Abe's J1,J2 soft-photon integrals are
`J1=1/2 integral dx/D`, `J2=1/4 integral u dx/D`,
`D=1-k^2 u/mW^2`, leading to `GammaA=integral[-8+6u+(M_s^2/mW^2)u]/D`.
Ilisie's corresponding symmetrized transverse numerator is
`-19/2+15u+(M_s^2/mW^2)u`. They differ **before** the outer integration.
In particular,

```
K_CHK-K_Abe    =3/4 (g+h)
K_Ilisie-K_Abe =3/2 (3f-2g)
K_CHK-K_Ilisie =3/4 (h+5g-6f).
```

At z=0.413, these are

| Kernel / difference | Value |
|---|---:|
| K_CHK | 6.038191222471141 |
| K_Ilisie | 5.975256416364089 |
| K_Abe | 5.788407631919363 |
| CHK-Abe | 0.249783590551779 |
| Ilisie-Abe | 0.186848784444727 |
| CHK-Ilisie | 0.062934806107052 |

The old signed ratio -1.01053256994 combines the old overall-sign mismatch
with the magnitude ratio K_CHK/K_Ilisie. The approximately 1% is a
mass-dependent **effective-form-factor/subset difference**, not a universal
normalization, charge, color or factor-two error. Its exact algebraic origin
is established. It is not justified to identify this whole difference with
one omitted gauge-dependent term merely because one paper discards such
terms: the discarded non-transverse structures require their own projection.

## 6. Independent off-shell gauge check and remaining W blocker

Abe3.8 has transverse A, non-transverse P g^mu nu, B p2^mu p2^nu and
C [(p1+p2)^2-M_s^2]g^mu nu tensors. For G=photon,
`GammaP=3J1`. Its Eq.3.16 pinch contribution is exactly
`-3J1 p2^2 g^mu nu` with the same prefactor, canceling the P term.
The audit integrates J1,J2 for several genuinely off-shell momenta, contracts
the tensors with both photon momenta, and verifies the cancellation. A bare
transverse projection alone would conceal the sizable Ward violation of P;
both the before and after residuals are recorded.

This is an independent numerical **source-tensor Ward check**, not a fresh
calculation of every W/Goldstone/ghost/pinch graph in arbitrary R_xi gauge.
B requires external-line Dirac projection; C requires the neutral mixing
sum rule after the propagator cancels. Native scalar vertices verify
`G_sG+G-=M_s^2 kappa_s/v`, `g_sWW=2mW^2 kappa_s/v` and
`sum_s kappa_s C_s[j,i]=0`. These are necessary, not sufficient, conditions.

The exact missing calculation is: evaluate and project the complete
off-shell W/Goldstone/ghost diagrams plus the matching non-Barr–Zee pinch
terms for general Zee LFV chiral vertices; demonstrate the B,C reductions,
verify independence of R_xi at the retained external-mass order, and identify
which transverse kernel belongs to that completed set. Until then **all W
candidates remain UNKNOWN and excluded**. No arbitrary difference between
the three kernels is added as a finite correction. Charged-scalar/photon
matching is now separately validated in CHARGED_SCALAR_AUDIT.md. Zgamma,
WZ and the other missing electroweak amplitudes remain unimplemented.

## 7. Regressions and reproducibility

```
bash scripts/run_module4_validation.sh --all-tests
python -m module4.tagged_regression
python -m unittest discover -s tests -p 'test_module4_*.py' -v
python -m module4.interface --input module4/example.json \
  --output validation/module4/local/example_output.json
```

The full runner starts SARAH once and executes the unchanged Module3 suite
in an ephemeral isolated clone at exactly tag
`zee-lfv-module3-components-v1`/48735439..., with its original branch name
`feature/zee-lfv-module3`. No existing checkout is switched. The remaining
regression tests and new Module4 compatibility tests run on
`feature/zee-barrzee-module4`. No inherited branch guard is changed,
spoofed, waived or counted as an expected failure. Both contexts' actual
counts, failures, errors and skips are reported separately.

New regressions include the emitted operator vertex, sigma/HC and gamma5
identities; outer attachment ordering; positive double parameters versus
analytic kernels; three independent signed diagonal formulas; complex tau
and unrestricted NO/IO witnesses; reverse-channel hermiticity, rephasing,
charge/color and CP-odd falsifiers; coherent interference with frozen
one-loop terms; exact W differences and the scoped off-shell Ward check.
Each channel includes seven frozen one-loop, 27 validated fermion/photon
and six subsequently validated charged-scalar/photon components. The two W
candidates stay separate. Partial rates remain
**INCLUDED_TOPOLOGIES_ONLY** and imply neither allowance nor exclusion.
