# D16 signed reductions and unresolved gauge completion

Historical starting evidence. The subsequent independent regulated inner
calculation and actual parent subloops are documented in
[D16_GAUGE_DERIVATION.md](D16_GAUGE_DERIVATION.md) and `gauge_ledger.json`.
Statements below about unevaluated inner integrals describe the earlier
milestone; complete physical gauge matching remains blocked.

Status: **BLOCKED_GAUGE_MATCHING**. The new results below are exact outer-line
B/C reductions and conditional source-tensor checks. The 26 inner graphs have
not been independently integrated. No physical W Wilson coefficient is supplied.

## Conventions and amplitude class

Keep the frozen Module4 action

\[
\mathcal L_D={e m_i\over2}\bar\ell_j\sigma^{\mu\nu}
(C_LP_L+C_RP_R)\ell_i F_{\mu\nu}+\mathrm{h.c.},
\quad \sigma^{\mu\nu}={i\over2}[\gamma^\mu,\gamma^\nu],
\]

with metric (+---), positive e, positive diagonal lepton masses and
\(q=p_i-p_j\) emitted. D15's proved source bridge remains
\(K_{2L/R}=-C_{L/R}^*\) in the same parent-mass normalization. Nothing in
this investigation changes that bridge or infers a sign from a rate.

The target is neutral h/H exchange, one real photon, a virtual photon, and
the W/charged-Goldstone/ghost inner sector plus its necessary pinch parents.
Use linear electroweak \(R_\xi\) gauge. The physical A has zero couplings
to WW and to the pure Goldstone sector in this CP-conserving scalar model.
Complex h/H LFV vertices still have both independent chiralities.
Scalar/fermion physical charged-particle loops already validated in Module4
are separate contributions. hZgamma and charged-current Barr–Zee graphs are
not included merely by changing the exchanged photon's mass.

The final radial diagnostics neglect external invariants in loop denominators,
as Module4 does. The B/C proofs below retain the exact unequal external
masses; do these cancellations **before** making that expansion.

## B: exact cancellation between both LFV photon attachments

Let \(k\) leave the inner loop and enter the external lepton line. The scalar
carries \(q+k\). Strip common vertex and propagator phases and define

\[
X_s=L_sP_L+R_sP_R,
\quad S_a(r)=(\not r-m_a)^{-1},
\]
\[
J_s^\nu=\bar u_j\left[
\gamma^\nu S_j(p_j-k)X_s+X_sS_i(p_i+k)\gamma^\nu
\right]u_i.
\]

Both electromagnetic charges are the same. In the first term use
\(\not k=(\not p_j-m_j)-S_j^{-1}(p_j-k)\). In the second use
\(\not k=S_i^{-1}(p_i+k)-(\not p_i-m_i)\). The external Dirac equations give

\[
k_\nu J_s^\nu=-\bar u_jX_su_i+\bar u_jX_su_i=0.
\]

No \(m_i=m_j\), Hermitian Yukawa texture, CP restriction on L/R, soft-photon
limit, or neutral-scalar sum was used. Therefore
\(\Gamma_s^B k^\mu k^\nu J_{s\nu}=0\) **for each scalar before integration**,
for arbitrary scalar form factor \(\Gamma_s^B\). The longitudinal part of
the outer photon propagator also drops out. A single attachment fails this
identity; that is an executable falsifier. Merely saying that a scalar chain
has no sigma matrix would be insufficient for unequal-mass LFV.

`algebra.py` independently implements Weyl-basis on-shell spinors, both massive
propagators and unrestricted complex L/R. Tests include mu/e and tau/mu mass
ratios and independent virtual momenta, rather than checking a scalar kernel
after B has already been deleted.

## C: inverse scalar propagator and the full neutral sum

With \(\delta=\beta-\alpha\), the actual native Yukawas and WW overlaps are

\[
\kappa_h=\cos\delta,\quad\kappa_H=\sin\delta,
\quad C_h=\cos\delta\,{M_\ell\over v}-\sin\delta\,{D\over\sqrt2},
\quad C_H=\sin\delta\,{M_\ell\over v}+\cos\delta\,{D\over\sqrt2}.
\]

Thus \(\sum_s\kappa_s C_s=M_\ell/v\). For \(i\ne j\), both
\(\sum_s\kappa_s C_s[j,i]\) and
\(\sum_s\kappa_s C_s[i,j]^*\) vanish independently.

In Abe's photon source tensor at xi=1,
\(\Gamma^C=-J_1(k^2,(q+k)^2;m_W^2)\) is independent of the neutral mass.
Its factor \([(q+k)^2-M_s^2]\) cancels the scalar propagator. The remaining
current is linear in X, with external-line masses and denominators independent
of s. Therefore the full C contribution vanishes for off-diagonal LFV after
the h/H sum, with unequal, nondegenerate scalar masses. This proof is tied to
that source coefficient; general-xi mass independence is not assumed.

Removing H leaves a nonzero C remainder in the test. For diagonal magnetic
moments the **full scalar** sum is \(m_\ell/v\), not zero. Abe's axial EDM sum
does not establish cancellation of that diagonal scalar term. Consequently
our diagonal source-A continuation is only a conditional check, not a
derivation of the complete W magnetic moment.

## P and the scope of the electromagnetic Ward check

For the photon case in the corrected
[Abe source](https://arxiv.org/html/1311.4704v3), 3.8–3.16, write

\[
T^{\mu\nu}=k^\mu q^\nu-k\cdot q\,g^{\mu\nu},\quad r=q+k,
\]
\[
\Gamma_A=4[-4J_1+6J_2+(M_s^2/m_W^2)J_2],\quad
\Gamma_P=3J_1,\quad\Gamma_B=-3J_1,\quad\Gamma_C=-J_1.
\]

The common prefactor is \(\alpha\kappa_s/(2\pi v)\). Retain all four tensors:
\(\Gamma_AT\), \(3J_1 k^2 g\), \(-3J_1kk\), and
\(-J_1(r^2-M_s^2)g\). The source pinch tensor is \(-3J_1k^2g\).
P cancels that source pinch, B annihilates the exact external current, and C
cancels in the neutral sum just proved. The resulting attached source tensor
equals A and obeys the real-photon Ward identity. A is also transverse in
the virtual-photon direction. These statements are checked at nonzero
virtuality with all spin states and both complex chiralities.

This establishes an electromagnetic identity for **published xi=1 source
tensors with their published pinch term**. It is not an independent
diagram-by-diagram derivation or a demonstration of xi independence.

## Conditional signed outer reduction

In the leading external-invariant expansion the two attachment numerators
are \(X\not k\gamma_\nu-\gamma_\nu\not kX=X[\not k,\gamma_\nu]\).
An independent Weyl-matrix Wick angular average gives
\(\langle X[\not k,\gamma_\nu]T^{\mu\nu}\rangle
=i\sigma^{\mu\rho}q_\rho X\) at unit Euclidean radius.
The emitted action vertex is \(+e m_i\epsilon_\mu^*q_\nu\bar u_j\sigma^{\mu\nu}Xu_i\).
The signed propagator/vertex phases and charge \(Q_\ell=-1\) are those
already derived in frozen Module4. Consequently an inner coefficient S
would give \(-[16\pi^2m_i]^{-1}\int_0^\infty dt\,S(-t)/(t+M_s^2)\).

The *source* soft A coefficient has numerator
\(-8+6u+(M_s^2/m_W^2)u\), with \(u=x(1-x)\), and denominator
\(1+ut/m_W^2\). Its radial integral is \(-2K_A\), where

\[
K_A=3f+5g+{f-g\over2z},\qquad z=m_W^2/M_s^2.
\]

For this source A alone the conditional outer coefficients are therefore

\[
C_L^{A,\mathrm{conditional}}=
{\alpha\over16\pi^3v m_i}\sum_{s=h,H}\kappa_s C_s[j,i]K_A(z_s),
\quad
C_R^{A,\mathrm{conditional}}=
{\alpha\over16\pi^3v m_i}\sum_{s=h,H}\kappa_s C_s[i,j]^*K_A(z_s).
\]

They have units GeV^-2. This sign is a conditional consequence of the
source tensor and frozen outer action; agreement with a candidate kernel
does not validate the inner source. No physical interference or rate is
computed with it. The reverse action ordering would use
\((m_i/m_j)(C_R^*,C_L^*)\); this algebra does not replace an independent
reverse ordered two-loop calculation.

The radial check separately integrates
\(\int dx\,dy[4z-3zu-u/2]/[z(1-y)+uy]\), without calling f/g kernels.
At three mass ratios it also agrees with half the photon specialization of
the corrected B.8 in the
[2016 erratum](https://doi.org/10.1007/JHEP04(2016)161).
That erratum changes B.8 and several other printed equations, not 3.8–3.16;
it supplies no CHK/Ilisie arbitration. Its page was rendered and inspected.

For a diagonal real external scalar coupling a, source A alone would give
\(a_\ell^{A}=\alpha m_\ell\kappa_s aK_A/(8\pi^3v)\); a purely axial
external vertex gives zero magnetic moment. These are conditional action
limits, **not independently established complete W moments**.

## Exact remaining gauge identity and minimal reproducer

The native \(s\bar c^\pm c^\pm\) rule is proportional to xi; replacing only
the Goldstone mass in a xi=1 expression omits both ghost vertices and
longitudinal W changes. In particular,

\[
D_\xi^{\mu\nu}(k)=D_U^{\mu\nu}(k)
-{i k^\mu k^\nu\over m_W^2(k^2-\xi m_W^2)}.
\]

The independently known Goldstone triangle+seagull subset in this convention
is

\[
C_{L,R}^{G}(\xi)={\alpha\over16\pi^3v m_i}
\sum_s\kappa_s C_s^{L,R}
F_2(\xi m_W^2/M_s^2),\quad
F_2(z)=-{1\over2}\int_0^1dx\,{u\log(z/u)\over z-u}.
\]

This is gauge dependent by itself despite satisfying electromagnetic Ward
identities. For the fixed input `matching.example(1)`, changing xi from 1 to 3
requires the remaining projected graphs to supply, relative to xi=1,

```
Delta CL_remaining = +5.0475478422e-10 +4.8569087322e-10 i  GeV^-2
Delta CR_remaining = -1.9418997438e-09 +1.9695905279e-09 i  GeV^-2
```

These are required compensators, not computed W/pinch amplitudes.
The exact missing identity is

\[
\Delta_\xi(C_W+C_{WG}+C_{\mathrm{ghost}}+C_{\mathrm{pinch}})
=-\Delta_\xi C_G
\]

for **both physical projected chiralities**, including any necessary Zee
charged-current pinch parents. The 26 signed regulated inner integrals and
the general-xi parent reductions needed to evaluate its left side remain
unavailable. Source Ward checks alone do not fix a finite transverse addition.

Run `python3 -m research.wgamma_d16.matching --example 1 --require-pass`.
It exits **2**, returns physical `C_L,C_R=null`, records the three separated
xi values and the required compensators, and marks the mass-replacement
shortcut FAIL. It does not call the incomplete shortcut the full amplitude.
The resolution procedure is in `STATUS.md`.
