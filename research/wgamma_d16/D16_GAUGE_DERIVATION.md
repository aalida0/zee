# D16: regulated inner tensors and calculated parent subloops

Physical status: **BLOCKED_GAUGE_MATCHING**. This continuation computes actual
integrals; it does not supply physical W Wilson coefficients. Starting evidence
is `4221e39`; the task clarification is `6e49ab8`. Earlier B/C reductions, the
26-graph count, and the 58-vertex extraction were reused, not repeated.

## 1. Source, routing and signs

`native_integrands.py` constructs vertex products from the already saved
`native_vertices.json`, in its returned field order. The native keys are
`sWW`, `sGG`, `sWG`, `photonWW`, `photonGG`, `photonWG`,
`sPhotonWG`, `photonPhotonWW`, `photonPhotonGG`, and `sGhost`/
`photonGhostMinus/Plus`. Their potential/mixing/EW relations were already
validated at the two source spectra. In particular, the Goldstone trilinear is
**independent of xi**: `V_sGG=-i Ms² kappa/v`; its propagator mass is
`xi mW²`. The ghost trilinear **does** contain xi.

All vertex momenta enter. External photons leave with `q,k`, scalar momentum
`r=q+k` enters. The three geometrical edges `(s,q),(q,k),(k,s)` carry
`l,l-q,l-r`. For positive orientation the negative/positive fields are:

| Vertex | Negative field momentum | Positive field momentum |
|---|---|---|
| s | -l | l-r |
| q | q-l | l |
| k | r-l | l-q |

The other orientation reverses charge, with the geometrical momenta fixed.
The propagators are `i/(p²-xi mW²)` for G and ghosts, and
`-i g_ab/(p²-mW²)` for W at xi=1. Every closed ghost loop has an extra minus.
The four ghost loops are the two FP species and their two arrow orientations;
they are not scalar-QED loops and have no photon seagull here. Each saved
FeynArts graph has unit net combinatorial factor in these labeled amplitudes.

The existing actual FeynArts expressions are
`local/fa-inner.m` and `local/fa-inner-amplitudes.m`; their historical hashes
are preserved in `evidence.json`. The mapping used by the *new* numerator
products is:

| FeynArts numbers | Native edges (a,b,c) or contact |
|---|---|
| 1,2 | GGG |
| 3,4; 5,6 | gWm; gWmC |
| 7,8 | GWG |
| 9,10 | GGW |
| 11,12 | WGG |
| 13,14 | GWW |
| 15,16 | WWG |
| 17,18 | WGW |
| 19,20 | WWW |
| 21;22 | scalar; W two-photon seagull |
| 23,24;25,26 | s-k-WG; s-q-WG contacts |

The FeynArts SM expressions provide graph identity/routing only. No SM
coupling or FeynArts amplitude is imported into the new computation. Native
products retain all `i` factors; strip only `e² kappa/v`. The final tensor
normalization is `i e² kappa/(16 pi² v)` times our reduced PV tensors.
For example, GGG has numerator
`Ms²(2l-q)^mu(2l-2q-k)^nu`; the G seagull is `-2 Ms² g^mu nu`.
The mixed s-photon-WG contact numerator at xi=1 is `-mW² g^mu nu`,
and the W two-photon contact is `4 mW²(1-d) g^mu nu`.

## 2. Dimensional integration, including finite rational terms

Use `d=4-2 eps`, Minkowski metric (+---), MSbar scale `mu`, and the normalized
PV measure `(mu² exp(gamma_E))^eps d^d l/(i pi^(d/2))`. `1/eps` is kept
separately. Physical loop factors use the corresponding MSbar convention.
No momentum cutoff or unregulated divergent-loop quadrature is used.

For denominators `D_i=(l+a_i q+b_i k)²-m_i²`, Feynman parameters give

```
R = -sum x_i (a_i q+b_i k),   l=t+R
Delta = sum x_i m_i² - sum_{i<j} x_i x_j (p_i-p_j)².
```

For a Wick tensor of rank `2h`, with the parameter `Gamma(n)` included, the
integrated coefficient of each metric pairing is

```
(-1)^(n+h) Gamma(n-h-2+eps) Delta^(2+h-n-eps)/2^h.
```

If `a=2+h-n>=0`, its Laurent coefficients are

```
pole   = Delta^a/(2^h a!)
finite = pole [H_a - log(Delta/mu²)].
```

For `a<0` it is finite and equals
`(-1)^(n+h) Gamma(-a) Delta^a/2^h`.
Every polynomial in d is retained through differentiation: its epsilon
coefficient adds `-2 d/d(d) pole|d=4` to the finite term. In particular,
the finite rational terms in WWW and its seagull are not discarded.

`contract()` performs an abstract Einstein-index network contraction: a
closed metric trace is d. `reduce_rank2()` provides a minimal independent
quadratic reduction. `reduce_general()` uses shifted polynomial/Wick moments
through the ranks required by longitudinal W numerators. They agree exactly
on every xi=1 graph. Parameter integrals use nested Gauss-Legendre rules;
order doubling is reported as a convergence estimate, not a rigorous bound.
Spacelike virtual photons keep every parameter Delta positive.

## 3. Actual xi=1 answer and independent source comparison

The output basis is
`g, q^mu q^nu, q^mu k^nu, k^mu q^nu, k^mu k^nu`.
The q^mu structures are saved and are dropped only when attaching a real,
transversely polarized photon. No published A/P/B/C relation is imposed in
either integrand construction or integration.

Define `a=T_kq/2`, `b=T_kk/2`, and
`U(Ms²)=(T_g+q.k T_kq)/2`. The native result is affine in Ms².
At xi=1, independently extract

```
c = -[U(M2²)-U(M1²)]/(M2²-M1²)
p = [U(M1²)-c(r²-M1²)]/k².
```

These reproduce **all four** coefficients in Abe's Eq. 3.8--3.14, after
calculation: `a=4(-4 J1+6 J2+Ms² J2/mW²)`, `p=3 J1`,
`b=-3 J1`, `c=-J1`. The factor two comes from Abe's prefactor
`e² kappa/(8 pi² v)`. The new tests use two different spacelike kinematics
and the mass pairs `(125,437)` and `(172,653)` GeV. The reproducible ledger
also uses the two original complex LFV examples, with their actual native
EW constants and h/H masses. Comparisons occur **after** native integration;
`source_tensors()` is never called by the integral engines.

For one additional transparent numerical witness, with
`mW=80.379, Ms=125, q²=0, k²=-7000, q.k=-1200` in GeV units, the finite tensor is

```
g   = -9940.6113528625 GeV²
qq  = -2.56636964005766
qk  =  0.01260493758895
kq  = -11.0709773414850
kk  = -2.49284083745547.
```

## 4. General xi: integrated longitudinal terms and exact UV cancellation

The propagator is expanded by the identity

```
D_xi(p) = -i[(g-pp/mW²)/(p²-mW²) + pp/(mW²(p²-xi mW²))].
```

Every term is reduced with the same DR formula; apparent power divergences
of the separated unitary pieces are retained. There are 71 denominator/mass
pieces across the 26 graphs. Their sum at xi=1 agrees with the simpler
direct Feynman-gauge calculation. At arbitrary symbolic xi, the integrated
pole of each group is as follows (all other tensor pole coefficients vanish):

| Group | Coefficient of g/eps |
|---|---|
| two GGG | `2 Ms²` |
| G seagull | `-2 Ms²` |
| four ghost triangles | `-xi mW²` |
| GGW + WGG, both orientations | `2 xi mW²` |
| GWW + WWG, both orientations | `-3 xi mW²` |
| GWG + WGW | `0` |
| two WWW | `3 mW²(xi²+xi+4)` |
| W seagull | `-3 mW²(xi²+3)` |
| four s-photon-WG contacts | `-mW²(xi+3)` |
| **sum** | **0 exactly** |

`exact_uv()` proves this by integrating pole polynomials with rational
simplex moments, retaining arbitrary q²,k²,q.k,Ms²,mW²,xi. This is stronger
than a floating-point pole cancellation at a selected spectrum.

The finite inner tensor is gauge dependent, as an off-shell Green function
can be. For the numerical witness above, its kq coefficient is
`-10.1030019273939` at xi=.5 and `-12.4312844098315` at xi=3. This is a
**computed** W/G/ghost/mixed sum, not a compensator inferred from the known
Goldstone variation. The h/H tensors are attached separately to both
complex chiral currents in the ledger; these are fixed-momentum inner
amplitudes, not dipole Wilson coefficients.

## 5. Contracted native vertices and what they leave behind

With incoming `(p,a,b)` at photon,W-,W+ and `p+a+b=0`, direct contraction
of the native triple vertex, stripping ie, gives

```
a_alpha Gamma^(mu alpha beta) = T(b)^(mu beta)-T(p)^(mu beta)
T(p) = p² g-pp.
```

Including the native photonWG mass vertex and the inverse Rxi W operator
`K_W(b)=(b²-mW²)g-(1-1/xi)bb` gives

```
a.Gamma/(ie) - mW Gamma_gammaGW/(ie)
    = K_W(b)-T(p)-bb/xi.
```

`K_W(b)` pinches an internal W, `T(p)` is the external photon inverse,
and **`-bb/xi` remains** as a gauge-fixing/ghost insertion kernel. It cannot
be discarded by quoting an electromagnetic Ward identity.

For the scalar derivative vertex, with `pW=-r-pG`, direct native algebra is

```
pW.V_sG-W+ = i mW kappa/v (r²-pG²)
pW.V_sG-W+ + mW V_sGG - mW V_sghost
  = i mW kappa/v [(r²-Ms²)-(pG²-xi mW²)].
```

This shows the scalar and Goldstone inverse propagators, and the native
ghost mass source. It is an algebraic component of the ST calculation,
**not the full multi-leg BRST functional identity**.

New source extraction is limited to the eight previously unqueried `s G H`
vertices and the generated gauge-fixing/gauge-transformation expressions.
`st_sources.json` saves their native order and unreduced expressions. All
16 numerical checks (eight vertices, two spectra) confirm

```
V_sG-Ha+ = -i (Ms²-MHa²) (ZH_s dot ZP_Ha,doublet)/v
```

and its charge conjugate, with worst residual `2.28e-13` GeV. Thus the
physical charged-parent derivative identity retains
`(r²-Ms²)-(pH²-MHa²)`; an unweighted charged mixing sum cannot eliminate
mass-dependent parent integrals. The generated SARAH gauge-fixing is
linear in the gauge-eigenstate charged fields and rotates to
`F-=partial.W-+i xi mW G-`, `L_GF=-F+ F-/xi` with the native W rotation.
Its raw form is retained rather than silently changing to a nonlinear
electromagnetic gauge. The saved `GaugeTransformation` entries contain the
interaction parts; derivative ghost transformations must also be retained
in constructing the full ST insertion functional.

## 6. Calculated open-lepton parent, pinch and mixed subloops

This is new loop work, distinct from importing Abe's pinch. Let the scalar
couple first on the incoming lepton line. At fixed outer scalar momentum r,
the charged propagator has momentum `p-r`, mass `mj`; the internal neutrino
has `n=p-l`. Bosons carry `l,l-q,l-r`. The exact missing two-loop integrand
has the factors

```
 integral d^d r d^d l /(2pi)^(2d)
  [ V_s(ac) D_a(l) V_gamma(ab)(-q) D_b(l-q) D_c(l-r) ]
  * ubar_j Gamma_b [i slash(p-l)/(p-l)²] Gamma_c
      [i(slash(p-r)+mj)/((p-r)²-mj²)] (-i X_s) u_i
  * i/(r²-Ms²),
```

with native charges `(a+,c-)` at s, `(a-,b+)` at the photon,
and `(b-,c+)` at the lepton currents. `Gamma_W=-i g2 gamma PL/sqrt(2)`;
the daughter Goldstone current is `-i g2 mj PL/(sqrt(2)mW)`, its conjugate
at the first current is proportional to PR. `exact_parent_integrand()`
is executable for general xi and independent complex L/R, with every
denominator and the unpinched charged propagator present. It is an integrand
witness, not a prescription to integrate divergent terms in four dimensions.

For WWW the inner tensor, stripping `e g2² mW² kappa/v`, reduces to

```
N_mu = [-slash(l+q) slash(n) gamma_mu
        +(2-d)(2l-q)_mu slash(n)
        +gamma_mu slash(n) slash(2q-l)] PL
     = 2 n² gamma_mu PL + N_mu^rem,

N_mu^rem = [-slash(p+q) slash(n) gamma_mu
            +(2-d)(2l-q)_mu slash(n)
            +gamma_mu slash(n) slash(2q-p)] PL.
```

The first term cancels the neutrino propagator algebraically. Its triangle
integral is calculated directly as `-2 integral_simplex 1/Delta`, **not** as
minus any Goldstone gauge variation or as minus the inner P form factor.
The remainder is separately integrated as a box; its rank-two moment is
`-g/(2 Delta)`. Keeping `n²` in the original box gives the same pinched
triangle to `1.6e-18` at the first witness. The finite reduced WWW subblock
has maximum component `2.21786051836567e-4 GeV^-2` and the pinched triangle
coefficient is `-1.47047104678369e-4 GeV^-2`.

All eight W/G species assignments of this parent placement are evaluated
at xi=1 with their native tensors, Goldstone currents and phases. Their
numerators are of degree at most three, so their convergent box integrals
use `N(R)/Delta² - laplacian_M N(R)/(4 Delta)`. The centered Hessian is exact
for those polynomials. A separate explicit gamma reduction of WWW agrees
with the native tensor contraction. Both spectra and independent complex
chiral attachments are retained in `gauge_ledger.json`.

The WWW subloop is also integrated at xi=.5,1,3, without separating divergent
unitary pieces: the complete Rxi box is UV convergent. Set `n0=i t0` after
shifting to the neutrino momentum; all massive-line energy shifts are below
their masses at the saved witnesses, so this contour is safe. Scrambled
Sobol quadrature, six independent replicates and antithetic directions give
the finite epsilon^0 coefficient and a replicate standard error. This is
cross-checked against the regulated parameter calculation at xi=1. Its
statistical uncertainty is insufficient for precision cancellation tests;
it is recorded as such, and no gauge-matching claim uses it.

## 7. Specific unresolved calculation

The first nonzero missing *complete* topology is the outer r integration of
the explicit parent just written, projected with both scalar placements
and combined with charged-H and reducible/external contributions. It is not
an unavailable software service. Its inner subloop is now evaluated, so the
remaining obstruction is the unimplemented **d-dimensional two-loop outer
Dirac projection and ST/LSZ subtraction**, not an unknown inner W kernel.

The `-bb/xi` insertion kernel above and the nonzero native `sGH` couplings
are concrete terms preventing closure by simply keeping the computed
transverse inner A. At fixed r the parent integral is UV finite. That does
not establish cancellation of vector/local outer UV poles: O(eps) inner
terms can multiply outer poles. The opposite scalar placement, mixed/charged
parents away from xi=1, external charged-lepton self-energy photon
attachments and counterterm/LSZ terms have not been dimensionally integrated
and summed. Their projected finite transverse remnants have not been shown
to vanish. There are no direct tree ghost-lepton currents; ghost parents
here mean the BRST insertion/contact kernels, not a fabricated such vertex.

Consequently neither side-by-side physical chiral dipoles nor the required
independent identity `Delta_xi C_remaining=-Delta_xi C_G` has been established.
The left side stays null. The implementation never negates the diagnostic
Goldstone variation to fill it. No physical W coefficient is exposed and
there is no D14 integration.

The next concrete step is to reduce the outer r integral of
`exact_parent_integrand()` in a d-dimensional open-Dirac basis, retaining
external inverse propagators until the crossed/LSZ sum. Then add the charged
parent mass terms from `st_sources.json`, rather than imposing the old xi=1
neutral C relation at general xi. Only after the full projected UV/xi sum
closes can the frozen D15 crossing and Module4 operator be used to release
physical CL,CR.

## 8. Published comparisons and reproduction

The new independently integrated xi=1 *inner* tensor agrees with
[Abe et al., 1311.4704v3, Eqs. 3.8--3.14](https://arxiv.org/html/1311.4704v3).
The correction [JHEP04(2016)161](https://doi.org/10.1007/JHEP04(2016)161)
remains required for its B.8 radial formula. The new calculation has not
independently integrated the entire pinched physical two-loop set, so the
historical CHK/Ilisie/Abe kernel differences are not newly arbitrated here.
Their source hashes and the prior conditional radial checks are preserved.
Matching a finite off-shell Green function does not resolve the extra
diagrams contributing to a physical LFV S-matrix element.

```
python3 -m research.wgamma_d16.tensor_reduction
python3 -m research.wgamma_d16.parent_integrals --require-completion
python3 -m unittest research.wgamma_d16.test_regulated -v
python3 -m research.wgamma_d16.regulated_pilot
python3 -m research.wgamma_d16.regulated_pilot --require-completion
```

The flagged commands write the real integrals and return 2 because complete
physical matching is still blocked. Detailed logs remain in ignored `local/`;
the compact, source-bound regulated results are in `gauge_ledger.json`.
To repeat only the **new** eight mixed source queries:

```
math -script research/wgamma_d16/extract_st_sources.m
python3 -m research.wgamma_d16.check_st_sources
```

That optional check uses the already installed SARAH and tracked native
physical inputs. It does not regenerate a model, rebuild any code, or
repeat the completed vertex inventory.
