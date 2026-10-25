# Module 0 conventions and diagnostic review

Current acceptance requires one complete invocation of the committed runner
in a newly empty workspace. Detailed output is preserved locally under
`validation/module0/local/runs/`; concise current reports and essential
fixtures are tracked. Legacy timestamped directories remain locally ignored
and contribute no acceptance. `STATUS.md` identifies the current invocation.

This is a finite, reproducible validation of the specified Zee Lagrangian.
It establishes neither phenomenological acceptance nor a complete RG,
vacuum, collider, LFV, SPheno or FlavorKit implementation. Archived numerical
fixtures are tests of analytic identities, not mocked SARAH outputs.

## The physical Majorana mass correspondence

The original four-component declaration was `Fv -> {vL,0}`. The corrected
declaration is `Fv -> {vL,conj[vL]}`. There is still only the original left
Weyl neutrino. No right-handed neutrino, tree mass, operator, gauge charge,
Yukawa coupling or scalar-potential term was introduced. The correction
identifies the external field as self-conjugate in SARAH, which is essential
for its Majorana external-field factors and both charge orientations.
The original calculation is retained in the first full run. The isolated
Majorana namespace initially differed by model name and spinor packaging;
after correction it differs from production by model name only. The
variant manifest proves this and hashes every production model file.

Write the mass operator as

\[
\mathcal L_m=-\tfrac12\nu_L^T\epsilon M\nu_L+\mathrm{h.c.}
\]

For a self-conjugate four-component spinor \(N=(\nu_L,\nu_L^\dagger)^T\),
the coefficient of \(\bar N P_LN\) is \(M\); the coefficient of
\(\bar N P_RN\) is \(M^*\). The two scalar chiral form factors therefore
carry conjugate matrices. SARAH's raw `SelfEnergy1LoopSum[[...,1]]`
uses the product `CpR_i conj(CpL_j)`: call this raw form factor
\(S_{SL}\), without the universal \(1/(16\pi^2)\).
The opposite scalar chirality uses `CpL_i conj(CpR_j)` and is \(S_{SR}\).

The propagator pole is the zero of the inverse propagator. With the SARAH
self-energy convention, its mass matrix is

\[
M_{1L}=M_0-\frac12\left[
 \Sigma_{SL}^*+\Sigma_{SR}
 +\frac12\{\Sigma_L^T M_0+\Sigma_R M_0+
 M_0\Sigma_R^T+M_0\Sigma_L\}\right].
\]

This convention is independently fixed by the **local mass constructor**
`Package/SPheno/SPhenoLoopMasses.m`, rather than selecting a sign or
conjugation by agreement with an E3 benchmark. The closure runner verifies
the exact source anchors for the two chiral products and
`mat1 = mat1a - 0.5_dp*(Conjg(SigSL) + SigSR + &`, and records the SHA256.
This is a source convention check, **not a SPheno generation or run**.

Here \(M_0=0\). Wavefunction contributions multiply \(M_0\); inserting
the induced mass in them would be a higher-order calculation. Evaluation
at \(p^2=0\) is appropriate for the leading radiative mass with massive
charged internal particles. Thus the fixed conversion is

\[
\delta M=-\frac{S_{SL}^*+S_{SR}}{32\pi^2}
         =-\frac{S_{SL}^*}{16\pi^2}.
\]

The second equality is checked numerically, not assumed: the two opposite
chirality products are evaluated independently using extracted physical
vertices. The raw form factor is also compared to SARAH's complete generated
sum. Its self-conjugate external factor 2 and the diagram symmetry factors
1/2 give one contribution per charged-scalar orientation.

In the diagonal charged-lepton basis let
\(F=F_{\rm SARAH}\), \(D=-s_\beta Y_e+c_\beta Y_{e2}\). Independently
expanding the component Lagrangian gives
\(\mathcal L\supset F_{\ell i}e_\ell\nu_iS^+
-D_{\ell i}e_\ell^c\nu_iH_D^-+\mathrm{h.c.}\).
For the stated charged-field rows

\[
Z_P=\begin{pmatrix}
c_\beta&s_\beta&0\\
-s_\beta c_\gamma&c_\beta c_\gamma&s_\gamma\\
s_\beta s_\gamma&-c_\beta s_\gamma&c_\gamma
\end{pmatrix},
\]

the physical all-incoming vertices in the order used by the loop generator
have, for `Fv_i,bar[Fe_l],Hm_k`,
\(C_L=-iD_{\ell i,k}\),
\(C_R=-iF_{i\ell}^* Z_{P,k3}\), and for
`Fv_i,Fe_l,conj[Hm_k]`,
\(C_L=-iF_{i\ell}Z_{P,k3}\),
\(C_R=-iD_{\ell i,k}^*\), where
\(D_{\ell i,k}=Z_{P,k1}Y_{e,\ell i}+Z_{P,k2}Y_{e2,\ell i}\).
All 72 complex coefficients per E3 point are checked against these
identities. SARAH may reorder the requested fields; chirality extraction
uses the returned structure.

Adding the two charge orientations yields

\[
(S_{SL})_{ij}=c_\gamma s_\gamma\sum_\ell m_\ell
 (F_{i\ell}^*D_{\ell j}^*+F_{j\ell}^*D_{\ell i}^*)
 [B_0(0,m_\ell^2,m_1^2)-B_0(0,m_\ell^2,m_2^2)].
\]

Since the difference in square brackets is \(-I_\ell\),

\[
(\delta M)_{ij}=\frac{\sin2\gamma}{32\pi^2}\sum_\ell m_\ell I_\ell
(F_{i\ell}D_{\ell j}+F_{j\ell}D_{\ell i}),\qquad
I_\ell=\int_0^1 dx\log\frac{x m_\ell^2+(1-x)m_1^2}
                                  {x m_\ell^2+(1-x)m_2^2}.
\]

The E3 convention is \(F=2f_{E3}\), \(D=\sqrt2Y_{E3}\).
The finite closed-form logarithm and independently endpoint-adapted
quadrature both reproduce this expression. In the massless-lepton kernel
limit \(I_\ell=\log(m_1^2/m_2^2)\); the explicit chirality-flip factor
\(m_\ell\) remains. Degenerate charged masses, zero mixing, zero F and
zero D give zero. Charged-state exchange and its mixing-sign change
leave the result invariant. The full loop inventory is generated without
an internal-particle restriction; at zero tree neutrino mass only the two
charged-scalar terms survive in the scalar mass form factor. W terms
are independently evaluated as zero; neutral terms have explicit zero
internal neutrino mass.

Complex covariance provides a phase-sensitive check. Rephasing both
left leptons by a diagonal unitary P and the singlet charged-lepton Weyl
fields by P* preserves the real diagonal charged masses and transforms
\(F\to PFP\), \(D\to P^*DP\), \(M\to PMP\).
The actual SARAH-generated matrix is reevaluated after this change.
The closure also compares the complete complex mass matrix, a complex
CP-sensitive invariant, and the Takagi rotation, not just mass singular
values. The final matrix tolerance is 5e-11 eV and relative 1e-8; raw
chirality/amplitude residual tolerances are 1e-16 GeV. Exact residuals
and all benchmark inputs are archived.

The earlier `...PHASE_SIGN_DERIVATION_PENDING` A/B status is deliberately
retained as the acceptance status of **that diagnostic alone**. Only
`zee_sarah_majorana_closure.m` can issue the physical-mass closure PASS.
An old A/B or static-test PASS cannot substitute for this last check.

## Scalar and current conventions

The independent polynomial in `zee_sarah_module0_native.m` implements
\(H_1^\dagger H_1\), \(H_2^\dagger H_2\),
\(H_1^\dagger H_2\), and
\(\mu_4 S^-(H_1^+H_2^0-H_1^0H_2^+)\) plus its conjugate.
It includes the original negative K12 term and all singlet quartics.
It is not read from a SARAH matrix. Differentiation independently checks
the CP-even, CP-odd and complex charged Hessians, tadpole stationarity,
Goldstones and charged diagonalization. All charge-conserving unordered
3- and 4-scalar tuples (217) are compared with actual SARAH vertices at
two unrelated Lagrangian points, including zero and Goldstone couplings.
The real scalar rotation signs are used identically in both expressions.
Landau gauge removes only the explicit SARAH gauge-fixing mass term.

The all-incoming photon rule fixes the derivative convention:
\(-ie(p_+-p_-)\). Expansion of \(|D_\mu H|^2\) fixes
W+ h H- to \(-ig_2/2\) times the doublet overlap and
W+ A H- to \(+g_2/2\) times the overlap, multiplying
\(p_{h/A}-p_{H^-}\). The conjugate current and returned momentum
structure are also checked. The singlet has no SU(2) overlap.
Z and photon physical charged vertices have separate numerical checks.

With complex quark rotations defined by
\(V_u^* M_u U_u^\dagger=\operatorname{diag}(m_u)\),
\(V_d^* M_d U_d^\dagger=\operatorname{diag}(m_d)\), set
\(K=V_uV_d^\dagger\). For `bar[Fu_i],Fd_j,H_k+`, the independent
Type-II chiral coefficients are
\(C_L=i\sqrt2 m_{u_i}K_{ij}Z_{P,k2}/v_2\),
\(C_R=-i\sqrt2 K_{ij}m_{d_j}Z_{P,k1}/v_1\).
Both orientations, both chiralities and all nine generation pairs
are checked with nontrivial independent complex left/right rotations.
General complex lepton rotations, Ye2, antisymmetric F and both neutral
lepton chiralities are checked in the integrated tree-lepton runner.

## Complete CheckModel diagnostic disposition

The complete console and separate message stream are archived. In the
observed run there is one Wolfram diagnostic, `PossibleTerms::NonSUSY`,
listing the following nine candidate missing terms. The runner accepts
exactly this reviewed list; any different or additional diagnostic
leaves gate 1 PARTIAL. SARAH itself warns that this non-SUSY candidate
enumeration is imperfect. All other CheckModel sections and their output
are preserved, including anomaly, charge, mixing, VEV, matrix, parameter
and particle-definition checks.

| Candidate | Disposition |
|---|---|
| d q H2* | Wrong-Higgs down Yukawa; deliberately excluded by the selected Type-II quark sector. |
| H1 q u | Wrong-Higgs up Yukawa; deliberately excluded by the selected Type-II quark sector. |
| d S-* u* | Opposite dotted/undotted Weyl spinors cannot form a Lorentz scalar without a derivative/vector; not a renormalizable scalar Yukawa invariant. |
| H1 H1 S-* | Identical commuting scalar doublets contracted with epsilon vanish. |
| H2 H2 S-* | Same antisymmetric zero as above. |
| H1 H1 H1* H2* | Lambda6-type hard doublet quartic; excluded from the specified potential. |
| H1 H2 H1* H1* | Hermitian conjugate Lambda6-type term; excluded. |
| H1 H2 H2* H2* | Lambda7-type hard doublet quartic; excluded. |
| H2 H2 H1* H2* | Hermitian conjugate Lambda7-type term; excluded. |

No candidate was inserted to silence the diagnostic. The general Ye2
sector means this selected Type-II quark/scalar ansatz is not a claim of
an exact symmetry protecting its form under RG evolution. RG closure was
not requested or established. Messages saying a mass matrix "seems not
to be reducible" are informational statements about connected blocks;
the independent Hessians, ranks, Goldstones and spectra test those blocks.

## SPheno

`models/SARAH/ZeeTypeII/SPheno.m` is absent. No valid SPheno source tree
or executable was identified in the capability inventory. SARAH's
**generator package** is present; that is not an installed SPheno.
No `MakeSPheno`, native compilation, SPheno executable or FlavorKit run
was attempted. This gate is BLOCKED, independently of the physics gates.

## Historical width reference

The existing benchmark test stored 9.411343197933336 GeV for
H2 -> H1 Z. A separate 70-digit calculation with the historical fixed
`G12=0.1520746183402528` reproduces 9.4113431979333376 GeV. The current
point-dependent identity `(MZ/v) sin(gamma) cos(gamma)` instead gives
`g12=0.15207461883074222657` and 9.41134325864253927 GeV for the exact
stated inputs. This explains the 6.07092e-8 GeV discrepancy without
changing a model coupling or loosening a tolerance. The machine-readable
derivation is `width_reference_derivation.json`. The corrected test uses
that independently computed width, with an additional point-variation
regression so a historical constant cannot silently reappear.
