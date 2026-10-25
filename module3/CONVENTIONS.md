# Module 3 mathematical contract

Use GeV, radians, positive real diagonal charged-lepton masses, and frozen
`SARAH_ZeeTypeII_Florentino_v1`. No change to the scalar potential, Type-II
quarks, or Modules 0–2 is made. Lambda6/7 RG closure remains unproved.

## Vertices and phases

Let `S=diag(sqrt(2)*m/v)`, `Ye=c_beta*S-s_beta*D`, and
`Ye2=s_beta*S+c_beta*D`. The Weyl singlet index is the row of D.
Define `L=-s bar(e)_a [C_ab PL+C_ba* PR] e_b`. The neutral matrices are

```
C_h = cos(beta-alpha) diag(m/v) - sin(beta-alpha) D/sqrt(2)
C_H = sin(beta-alpha) diag(m/v) + cos(beta-alpha) D/sqrt(2)
C_A = -i D/sqrt(2)
```

The last sign follows from conjugating the neutral doublet in the frozen
Yukawa Lagrangian. Changing the overall sign of a real neutral field changes
both vertices and no observable here. The physical charged rows have doublet
fractions `(cos(gamma),-sin(gamma))` and singlet fractions
`(sin(gamma),cos(gamma))`. All-incoming SARAH chiral coefficients are pinned
in `validation/module0/CONVENTIONS.md`; dividing their common vertex factor
gives Lavoura's charged interaction
`H+ bar(N_k)(L_ki PL+R_ki PR)e_i`, with
`L_ki=-s F_ki`, `R_ki=-d D_ik*`. Neutrino mixing gives respectively
`U.T F` and `U.dagger D.dagger`; unitarity removes U from pure contractions
at zero neutrino mass. No extra Majorana factor two multiplies a charged
lepton dipole. Mixed F-D chirality flips require a neutrino mass insertion.

The exact historical conversions `F=2 f_Chen`, `D=sqrt(2) Y_Chen` are tested
against both archived complex E3 input fixtures before any legacy comparison.
The frozen SARAH real/complex source identities and archived neutrino closure
are available; raw numerical neutral/charged `Vertex[]` outputs and the CP-odd
vertex archive are absent in this snapshot. Therefore a new direct archive
comparison is **not certified**. The mapping gate is PARTIAL for that reason,
despite passing the available component and phase checks. No fresh SARAH or
SPheno run is claimed.

Lepton rephasing acts as `F -> P F P`, `D -> P* D P`. Dipoles for `i -> j`
transform as `P_j* P_i`; widths are invariant. Complex conjugation, chirality
exchange under `C -> C.dagger`, and mass-weighted reverse-channel hermiticity
are independently checked, rather than checking absolute values alone.

## Neutral tree amplitudes

For `i- -> a-(p1) b-(p2) b+(p3)`, define
`Gamma_ab=C_ab PL+C_ba* PR`. The amplitude, up to an irrelevant common phase,
is the coherent sum over s=h,H,A of

```
 (ubar_a Gamma_ai u_i)(ubar_b Gamma_bb v_b)/(m_s²-s23)
 -(ubar_b Gamma_bi u_i)(ubar_a Gamma_ab v_b)/(m_s²-s13).
```

Both terms exist also when a differs from b for unrestricted Yukawas. The
minus sign comes from exchanging fermion contractions. Contact Wilson
coefficients are the products of chiral vertices divided by `m_s²`, without
an extra half. A half in `J²/(2m_s²)` is canceled by the two contracted currents.
Spin averaging divides by two. Phase space divides by `2!` when a=b, after
squaring the antisymmetrized amplitude. The code uses physical final masses
and full real scalar propagators; the interface stays away from on-shell
scalar poles. There are no widths hidden in the propagators.

The differential rate is

```
dGamma/(ds23 dz) = sqrt(lambda(M²,ma²,s23)*lambda(s23,mb²,mb²))
                  * mean_spin|M|²/(512 pi³ M³ s23).
```

An explicit 16-spin-state calculation checks the tensor contraction. An
independent massless contact integral gives `M^5 |g_LL|²/(6144 pi³)` for one
direct chiral operator and distinct negative leptons. For identical negative
leptons, the LL/RR weights are one half and the LR/RL weights are one. The
legacy A1d implementation uses `D_PP'=-g_PP'/2` but retains the same rate
prefactor; its simple same-vertex contact rate is four times smaller than the
spinor calculation. Module 3 does not inherit that normalization. This is a
documented reference discrepancy, not an edit of the frozen baseline or a
claim that all conventions in the paper are identical to the legacy code.

All five returned three-body rates are **TREE_SUBSET_ONLY**. Non-dipole
photon/Z penguins, dipole exchange, boxes and their interference are absent.

## Radiative operator and one-loop diagram set

The common convention, for ordered flavor-changing transitions, is

```
L_eff = e m_i/2 bar(l_j) sigma_munu (CL PL+CR PR) l_i F_munu + h.c.
Gamma(i -> j gamma) = alpha m_i^5/4 (1-m_j²/m_i²)^3 (|CL|²+|CR|²).
```

CL,CR have dimension GeV^-2. The second equation is verified with a massive
Dirac trace over the two photon polarizations. The diagonal g-2 continuation
counts its Hermitian operator once: `a=m_i² Re(CL+CR)`. Counting an additional
h.c. here would introduce a spurious factor two; the initial validation test
exposed and corrected that test normalization.

Starting from [Lavoura v1](https://arxiv.org/abs/hep-ph/0302221), equations
26–43, use `C_here=-sigma_Lavoura/(i*m_i)`. The common phase is fixed by
the scalar and pseudoscalar g-2 parameter integrals. The neutral diagram has
`QF=-1,QB=0`, `L_ki=C_ki`, `R_ki=C_ik*`. For each internal flavor, let
`lambda=L_kj* L_ki`, `rho=R_kj* R_ki`, `upsilon=R_kj* L_ki`,
`zeta=L_kj* R_ki`. Then

```
CL_neutral = sum_k [(rho+lambda*m_j/m_i) A(t)
                   +upsilon*m_k/m_i B(t)]/(16 pi² m_s²)
CR_neutral = same with lambda<->rho, upsilon->zeta.
```

Independent positive parameter integrals define the kernels:

```
A(t) = 1/2 integral_0^1 dx x²(1-x)/(1-x+t*x)
B(t) =     integral_0^1 dx x²/(1-x+t*x)
Ac(t)= 1/2 integral_0^1 dx x²(1-x)/(x+t*(1-x)).
```

At unity they are `(1/24,1/3,1/24)`. The analytic implementation uses
100-digit arithmetic near removable cancellations, tested at unity and its
adjacent floating-point value. At zero neutrino mass `Ac=1/12`, so

```
CL_charged = -[d² (D D.dagger)_ji + (m_j/m_i) s² (F.dagger F)_ji]
             /(192 pi² m_H²)
CR_charged = -[s² (F.dagger F)_ji + (m_j/m_i) d² (D D.dagger)_ji]
             /(192 pi² m_H²).
```

The F and D terms have the same charged-boson charge and common sign. Their
opposite dominant chiralities are retained, including daughter-mass flips.
The legacy A1e neutral and A1f doublet amplitudes agree after a common minus
conversion, whereas A1c singlet agrees without that minus. Consequently the
historical coherent assembly has a relative-sign conflict with this mapping.
It is tested and recorded, never silently reused. The leading internal-tau
limits also agree, with signed complex phases, with the mapped component
expressions in [Herrero-Garcia et al. v2](https://arxiv.org/abs/1701.05345v2),
equations 3.13–3.19. Their restricted flavor texture is not imposed here.

The diagram set includes h,H,A with all internal charged-lepton flavors,
H1/H2 with pure F and pure D, and the external-leg photon attachments already
combined into Lavoura's finite gauge-invariant expression. At m_nu=0 the
W/Goldstone flavor-changing term vanishes by unitarity, neutral gauge vertices
are flavor diagonal, and a physical H-W-photon tree vertex vanishes by charged
Goldstone orthogonality. There is no extra one-loop scalar contribution at
this order in that approximation. Finite-neutrino-mass mixed chirality and
GIM terms, and external-invariant corrections, are not computed. The latter
approximation is checked against unexpanded Feynman parameters at 80 GeV;
the interface requires every scalar mass >=20*m_tau. This is not a rigorous
per-point error bound. **Exact one-loop completeness remains UNKNOWN**;
the stated leading scalar diagram set passes its available tests.

## Two-body widths and universality

For one orientation of `s -> i- j+`, with
`lambda=(m_s²-(mi+mj)²)(m_s²-(mi-mj)²)`,

```
Gamma = sqrt(lambda)/(16 pi m_s³) *
 [(|Cij|²+|Cji|²)(m_s²-mi²-mj²)-4 mi mj Re(Cij*Cji)].
```

LFV output sums the two charge orientations. These are leading partial
widths, with no inferred scalar total width or branching ratio.

Let `w=sin²(gamma)/mH1²+cos²(gamma)/mH2²`. Fierz matching the singlet exchange
gives `deltaG_ab/G=|F_ab|²*w/(4 sqrt(2) GF)`. The leading rate shifts are
`r_ab=2 deltaG_ab/G`. The three squared coupling-ratio shifts are respectively
`r_tau_e-r_mu_e`, `r_tau_mu-r_mu_e`, `r_tau_mu-r_tau_e`. These restore the
muon-GF subtraction absent in a texture with f_e_mu=0. This calculation is
**SUBSET_DIAGNOSTIC**: D operators, mixed F-D interference, and dimension-six
squared rates are omitted. No precision experimental comparison is made.

## Missing physics and data

The machine-readable inventory lists absent fermion-gamma, W-gamma,
charged-scalar-gamma, Z-photon and W-Z Barr-Zee contributions, remaining
two-loop matching, non-dipole three-body contributions and interference,
mu-e conversion (including tree semileptonic scalar exchange), QED effects,
and the finite-mass and universality omissions above. No numerical
cancellation in this subset is a cancellation claim for the full Zee model.
`COMPLETE_LFV=false`; global acceptance is null. No public LFV limit, likelihood,
or phenomenological exclusion is included. The official authentic NuFIT 6.1
archive validation remains an external-data task in frozen Module 2.
