# Physical charged-scalar/photon matching

Matching status: **VALIDATION_PASS** in the same external-invariant expansion
as the validated Module4 fermion/photon subset. All h/H/A × physical H1/H2
rows are included coherently, including the proven zero A rows. The full
prediction remains **PARTIAL / INCLUDED_TOPOLOGIES_ONLY**. W matching remains
**BLOCKED_GAUGE_MATCHING**, with identical excluded candidates. Goldstone
loops belong to that blocked sector, not the physical H1/H2 calculation here.

## Native input and charge conventions

Use the actual frozen scalar potential, positive physical masses and the
Module3 sigma, photon and external-fermion conventions. Let

```
V contains s H-_a G_s,ab H+_b; G_s=G_s^dagger, in GeV.
s H-_a H+_b vertex = -i G_s,ab.
photon H-_a H+_b = -i e (p_plus-p_minus)_mu delta_ab.
two-photon H-_a H+_b = +2i e^2 g_mu nu delta_ab.
s bar(l_j) l_i = -i X_s,ji,
X_s,ji=C_s[j,i] PL+C_s[i,j]* PR.
```

The three- and four-point photon rules are freshly extracted from native
SARAH and numerically checked, including off-diagonal entries. The charged
particle has Q=+1; each photon brings a charge and the complete loop has Q².
The seagull factor two is the two-photon derivative of the kinetic term.
There is no color factor and no Majorana or extra antiparticle multiplier.

`couplings.trilinears` differentiates the charged mass matrix in the gauge
basis and rotates **both** charged legs by the frozen ZP. Independent
invariant-polynomial differentiation and native raw vertices already check
the h/H/A diagonal and off-diagonal couplings. The physical sector is rows
2,3 of SARAH Hm, while row1 is G-. The implementation reconstructs the
tree scalar parameters from the provenance-validated full scalar record;
no invented trilinear, inverse neutrino solver or new fit enters.

## Off-diagonal interactions and CP

In the mass basis the scalar propagator, photon vertex and seagull are
diagonal. A loop with one neutral trilinear therefore selects G_s,aa. An
off-diagonal trilinear cannot close either triangle or the seagull bubble,
even for degenerate masses. This is a flavor trace, not neglect of mixing.
The invariant scalar sum is

```
Tr[G_s F2(M_charged^2/M_s^2)]
 =sum_a G_s,aa F2(m_a^2/M_s^2).
```

Under an arbitrary complex unitary charged basis change, rotate both M² and
G before evaluating the matrix function. Tests verify this identity even
when the transformed matrices are dense. Dropping off-diagonal G in an
arbitrary non-mass basis would be wrong. Native off-diagonal trilinears are
nonzero in the tested spectra and retained in these checks.

In the frozen CP-conserving scalar potential, G_A is imaginary
antisymmetric in the real mass basis: its diagonal is zero. Hence A exchange
in this photon topology vanishes despite nonzero A-H1-H2 interactions.
Scalar QED produces no epsilon tensor and no independent pseudoscalar inner
form factor. Complex external h/H Yukawas still supply both complex CL,CR,
including an axial external vertex; no phase or CP contribution is discarded.
Off-diagonal Z currents and mixed charged-current topologies are outside this
photon subset and remain explicitly unevaluated.

## Independent two-triangle plus seagull calculation

The inner vertex is derived without imposing a transverse projector. Use
Euclidean incoming photon momenta p,q, r=p+q and D_l=l²+m². Stripping
(eQ)² G, the dimensionally regulated tensor integrand is

```
(2l+p)_mu (2l+2p+q)_nu / [D_l D_(l+p) D_(l+r)]
+(2l+2q+p)_mu (2l+q)_nu / [D_l D_(l+q) D_(l+r)]
-2 delta_mu nu / [D_l D_(l+r)].
```

These are the two photon orderings and the photon seagull. Contracting a
photon with a scalar current gives the difference of its adjacent inverse
propagators. The two triangles reduce to differences of bubble integrals;
translation invariance of dimensional regularization and the seagull cancel
the remainder. Both photon Ward identities follow. A hard cutoff shift or
omission/doubling of the seagull would invalidate this argument.

There is also an executable finite Feynman-parameter tensor check. For
a,b>=0, a+b<=1, define

```
R=a p+b r, Delta=m²+a p²+b r²-R²,
A=p-2R, B=2p+q-2R.
```

The first triangle, in units 1/(16 pi²), is
`integral_da_db [-2 delta log(Delta/m²)+A_mu B_nu/Delta]`, plus its common
UV constant. The second uses p↔q and mu↔nu. The seagull is
`+2 delta integral_0^1 dx log[(m²+x(1-x)r²)/m²]`, with the opposite UV
constant. The UV coefficients are +1,+1,-2 and cancel exactly.

The reduction uses the regulated identity
`integral L_mu L_nu/(L²+Delta)^3 = delta_mu nu/4 integral 1/(L²+Delta)^2`.
Setting d=4 in a divergent angular average prematurely would lose finite
terms. `scalar_qed_tensor` integrates these finite expressions and checks
Ward contractions, Bose symmetry and quadrature convergence at several
off-shell configurations. Removing or doubling the seagull is a falsifier.

Taking p soft, this tensor is
`2 [(p.q)delta_mu nu-q_mu p_nu] integral u/(m²+u q²) dx + O(p²)`,
u=x(1-x). A symmetric finite derivative of the **unprojected** diagram sum
tests that coefficient. With one real incoming photon q_in and virtual
outgoing photon k, the Minkowski effective vertex is therefore

```
i Gamma_mu nu = i (g_mu nu k.q_in-k_mu q_in_nu) S_s(k²),
S_s(k²)=alpha Q² G_s,aa/(2 pi) integral_0^1 u/(m_a²-u k²) dx.
```

The scalar loop has no closed-fermion-loop minus. For spatial photon
components the native vertices and Wick rotation give -i(eQ)²G/(16pi²)
times the Euclidean all-incoming tensor. Changing the virtual photon from
incoming to outgoing reverses that tensor, producing the displayed +i S.
Thus the sign is fixed before comparison with any moment or squared rate.
The transverse inner vertex kills the gauge-dependent longitudinal part of
the outer photon propagator. This is electromagnetic gauge consistency of
the physical scalar/photon subset, not full electroweak two-loop completion.

## Outer matching and signed dipole

The two external-lepton attachment orders and the emitted operator vertex
are exactly those independently derived in `MATCHING_AUDIT.md`. In
particular q_in=-q_out, the outer numerator is X[/k,gamma_nu], the outer
electric charge is Q_l=-1, and Hermitian conjugation routes
CL with C_s[j,i], CR with C_s[i,j]*. The radial integral is positive:

```
J(u)=integral_0^infinity dt/[(t+M_s²)(m_a²+u t)]
    =log[m_a²/(u M_s²)]/(m_a²-u M_s²).
```

Consequently, before introducing a named kernel,

```
C_X = -alpha Q² G_s,aa/(32 pi³ m_i) C_s^X integral u J(u) dx.
F2(z)=-1/2 integral u log(z/u)/(z-u) dx=(f(z)-g(z))/(2z),
z=m_a²/M_s²,
CL = +alpha Q² G_s,aa/(16 pi³ m_i M_s²) C_s[j,i] F2(z),
CR = +alpha Q² G_s,aa/(16 pi³ m_i M_s²) C_s[i,j]* F2(z).
```

F2<0 for positive z. The dimension is GeV^-2. A positive scalar trilinear
and positive scalar Yukawa produce a negative diagonal moment. There is no
additional 1/2 for a complex charged scalar. The two orientations and
seagull were already counted in the inner vertex.

An independent numerical two-loop parameter integral uses
t/M_s²=y/(1-y): `F2=-1/2 integral dx dy u/[z(1-y)+u y]`. It calls neither
the logarithmic production kernel nor an analytic Haber kernel. The exact
charged/neutral mass ratio is retained. External invariants in loop
denominators are neglected consistently with the existing Module4 matching;
the parent mass in normalization and the massive radiative phase space are
retained. This is not an exact finite-external-mass two-loop calculation.

## Independent published comparisons

Ilisie, JHEP04(2015)077 (1502.04199), Eqs.13,20,27, gives the same inner
vertex with `G=v lambda_sH+H-`, and the moment
`alpha m_l²/(8 pi³ M_s²) Re(y_l) lambda F2`. With
`y_l=v C_ll*/m_l` and `a_l=m_l² Re(CL+CR)` this matches the derived dipole,
including its sign and the purely axial external zero magnetic moment.

Arhrib–Baek, PRD65(2002)075002 (hep-ph/0104225), Eqs.3–6, independently
gives a generic scalar-loop vertex and signed moment. Its conventions are
`lambda_tilde=v G`, normalized external `lambda_mu=v Re(C_ll)/m_l`,
and `F_PRD=integral u log(z/u)/(z-u)=-2 F2`. Substituting
`GF=1/(sqrt(2)v²)` in Eq.5 reproduces the same result. No MSSM texture,
sfermion color multiplicity or old scan is imported into the Zee model.
The source's displayed approximate F(1) is not used as a precision fixture;
the actual parameter integral is used. PDF hashes are pinned in sources.json.

## Validation, preservation and output

`tests/test_module4_charged_scalar.py` covers full diagram Ward/Bose checks,
soft-vertex extraction, three independent kernel representations, signed
published moments, scalar/pseudoscalar external limits, Q² falsifiers,
complex unitary basis changes, nonzero off-diagonal couplings, degenerate
spectra and fixed-trilinear decoupling, dimensions, six NO/IO solutions and
all channels, rephasing, reverse-channel hermiticity and coherent interference.

`pre_charged_baseline.json` pins the pre-existing 34-row ledger and two W
candidates for each of 18 witness/channel records at commit3326982. Tests
verify that all these signed components remain bit-for-bit unchanged. The
new six scalar rows include four h/H entries and two zero A entries. Each
channel now has 40 coherent entries and the same two excluded W candidates.
No prior fermion coefficient or blocked W kernel is changed.

```
bash scripts/run_module4_validation.sh --all-tests
python -m module4.interface --input module4/example.json \
  --output validation/module4/local/example_output.json
```

Actual residuals and signed NO/IO examples are exported to
`validation/module4/charged_scalar_matching.json` and results.json. The full
runner makes a fresh native extraction, runs unchanged Module3 tests in the
exact tagged context, and runs current compatibility/regression tests on the
required feature branch. Logs, source PDFs and full raw dumps remain local
and ignored. No partial rate establishes experimental allowance or exclusion.
