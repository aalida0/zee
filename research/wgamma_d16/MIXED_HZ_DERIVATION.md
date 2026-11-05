# Physical charged-scalar Zγ radiative current

The unequal-mass **radiative scalar-current subset** is calculated, including
both triangles, AZ contact, both external lepton orders, and its neutral
Goldstone current. Its real-photon projection is gauge independent. This
does not establish the assignment/cancellation of all reducible neutral
mixing graphs, the complete potential-mediated electroweak sector, or the
full acceptance `MIXED_ZEE_HZ_CLASS_PASS`. Those larger gates remain open.
No W result is inferred from this calculation.

## Native signs and a correction to the task's premise

`mixed_hz_sources.json` retains 32 new SARAH queries, 64 numerical coefficient
checks at the two pre-existing mixed spectra, exact returned field/momentum
ordering, source hashes, and Wolfram/SARAH versions. The largest residual is
2.274e-13. The original model and authors' code were read without modification.
With negative/positive charged-field indices a,b, the rules are

\[
 V_{sH_a^-H_b^+}=-iG_{s,ab},\quad
 V_{ZH_a^-H_b^+}=-ieT_{ab}(p_+-p_-)_\nu,\quad
 V_{\gamma ZH_a^-H_b^+}=2ie^2T_{ab}g_{\mu\nu},
\]
\[
 T={dd^\dagger/2-s_w^2 I\over s_wc_w},\qquad
 d=(\cos\gamma,-\sin\gamma),\qquad Q=I.
\]
Both legs of the frozen full potential derivative are rotated. Independently
differentiating its G0 direction gives
\[
 G_{G^0}=R\,i\begin{pmatrix}0&0&-\mu s_\beta\\
 0&0&\mu c_\beta\\\mu s_\beta&-\mu c_\beta&0\end{pmatrix}R^T
 \bigg|_{\rm physical},\quad\mu=\mu_4/\sqrt2,
 \qquad G_{G^0}={ie\over M_Z}[M_\pm^2,T].
\]
The second equality is checked against the first and the native vertices;
it is not used to define/fill an unknown coupling.

The task anticipates nonzero **physical** off-diagonal A trilinears. Direct
queries and the independent full potential rotation instead give
`G_A[physical,physical]=0` for this frozen potential, including nonzero Mu4.
This is a model-specific identity, not a claim that CP alone forces it.
In the Higgs basis,
\[
 H_1^Ti\sigma_2H_2\supset {i\over\sqrt2}
                  (A G^+-G^0 H_D^+).
\]
The Mu4 term couples A to the **charged Goldstone** and the singlet, while
the doublet quartics couple A to G± and HD±. Neither produces A-HD-S or a
physical-physical A block. The additional native A-G±-Ha∓ checks are nonzero.
They remain relevant to the missing charged/reducible sector. A nonzero
physical A row must not be manufactured to satisfy the task's expectation.

## Unprojected unequal-mass integral and ST identity

Use Euclidean incoming photon p, Z momentum k and r=p+k. For a fixed ordered
charged pair, strip `e² G_ab T_ba/(16π²)`. With `D_a(l)=l²+m_a²`, the tensor is
\[
 \mathcal T_{ab}^{\mu\nu}=\int_l\left[
 { (2l+p)^\mu(2l+2p+k)^\nu\over D_a(l)D_a(l+p)D_b(l+r)}
 +{(2l+2k+p)^\mu(2l+k)^\nu\over D_a(l)D_b(l+k)D_b(l+r)}
 -{2g^{\mu\nu}\over D_a(l)D_b(l+r)}\right].
\]
It is dimensionally regulated before integration. The identity
`∫L_mu L_nu/(L²+Δ)³ = g_mu,nu/4 ∫1/(L²+Δ)²` retains the finite rational
terms from d=4−2ε. The finite triangle is
\[
 \int_{a,b\geq0}^{a+b\leq1}
 [-2g^{\mu\nu}\log(\Delta/\mu_R^2)+A^\mu B^\nu/\Delta],da,db.
\]
For triangle 1, `R=a p+b r`, `A=p−2R`, `B=2p+k−2R`,
`Δ=(1−b)m_a²+b m_b²+a p²+b r²−R²`; triangle 2 uses
`R=a k+b r`, `A=p+2k−2R`, `B=k−2R`,
`Δ=(1−a−b)m_a²+(a+b)m_b²+a k²+b r²−R²`.
The bubble contributes `+2g ∫dx log[((1−x)m_a²+x m_b²+x(1−x)r²)/μ_R²]`.
Pole residues are +1,+1,−2. Their sum and scale dependence cancel exactly.

Cancelling adjacent inverse propagators at the photon vertex proves
`p_mu T^{mu nu}=0`. Contracting the Z vertex instead gives
\[
 k_\nu\mathcal T_{ab}^{\mu\nu}
 =-(m_b^2-m_a^2)\mathcal J_{ab}^\mu,
\quad
 \mathcal J_{ab}^\mu=\int_l\left[
 {(2l+p)^\mu\over D_a(l)D_a(l+p)D_b(l+r)}+
 {(2l+2k+p)^\mu\over D_a(l)D_b(l+k)D_b(l+r)}\right].
\]
The leftover bubbles cancel the AZ contact. Multiplication by T_ba and the
native G0 identity gives the corresponding Goldstone-current identity,
including its phase. This remainder is **nonzero off shell**. Deleting the
contact breaks the photon identity and leaves a UV pole; the tests retain
that falsifier.

The independently integrated current J also obeys `p·J=0`. Lorentz covariance
gives `J=A p+B k`. For p²=0 and p·k≠0 this implies B=0, hence ε·J=0 for a
physical photon. The remaining kinematics follow by analytic continuation.
There is no scalar-loop epsilon tensor. Consequently the longitudinal Z
exchange and the G0 radiative triangle vanish **after** the physical-photon
contraction, despite the nonzero off-shell commutator. No cancellation was
imposed on the transverse tensor. Complex Euclidean null photons verify the
unprojected identities and ξZ=.5,1,3,7 current contractions independently.
These are current-tensor checks, not a new complete W dipole gauge test.

## Soft master, outer integration and signed coefficients

Extracting the `k_mu p_nu` coefficient directly from the two triangles gives
\[
 -2\int_0^1 {x(1-x)\,dx\over
 (1-x)m_a^2+x m_b^2+x(1-x)k_E^2}.
\]
Triangle 1 supplies `−2x(1−x)²`, triangle 2 `−2x²(1−x)` before their sum.
A symmetric finite derivative of the complete tensor checks this result;
it is not obtained by imposing a transverse projector. Define
\[
 \mathfrak f_{10}(x_a,x_b,y)=-\int_0^1 da\,u\int_0^\infty dt\,
 {t\over[t+(1-a)x_a+a x_b](t+yu)(t+u)},\quad u=a(1-a).
\]
Here `x_a=m_a²/M_s²`, `y=MZ²/M_s²`. The master is symmetric in a,b,
finite also at y=1, and reduces to validated f10 at equal charged masses.
An independent bounded integral uses `t=u w/(1−w)`:
\[
 \mathfrak f_{10}=-\int_0^1da\,dw\,
 {u w\over[y+(1-y)w][((1-a)x_a+a x_b)(1-w)+u w]}.
\]
The projected outer integral is UV convergent, so no discarded O(ε) inner
term can multiply an outer pole in this radiative-current subset. This
argument does not apply to the open W/reducible sector.

The native external vertices are `Y_L=C_s,ji`, `Y_R=C_s,ij*`. Both external
orders use the signed frozen Module4 operator derivation. Their axial Z
anticommutator contracts to zero; their vector factor is `−v_e^Z/2` relative
to the photon lepton current. Thus in GeV−2
\[
 C_X^{H^\pm Z\gamma,\,\mathrm{current}}=
 -{\alpha v_e^Z\over64\pi^3m_i}
 \sum_{s=h,H,A}{Y_{X,s}\over M_s^2}
 \sum_{a,b=1}^2G_{s,ab}T_{ba}\,
 \mathfrak f_{10}(x_a,x_b,y_s),\quad
 v_e^Z={-1/2+2s_w^2\over s_wc_w}.
\]
The diagonal doublet limit reproduces corrected
[2410.17313v4, Eqs.63–64](https://arxiv.org/html/2410.17313v4), with
`C=−c/(8π²v²)`. Portals at gamma=0 add exactly the previously validated
singlet HZ, with no photon overlap. Dense charged-basis rotations transform
M²,G,T together in `spectral_sum`; row phases, degenerate rotations,
gamma sign, complex lepton rephasings and mass-weighted reverse channels
are tested. Fixed-portal unmixed heavy-singlet decoupling is tested; fixed
nonzero mixing with arbitrarily heavy mass would grow Mu4 and is not that
decoupling limit.

Detailed new results and scope are in `two_loop_evidence.json`. Reproduce:

```bash
math -script research/wgamma_d16/extract_mixed_hz.m
python -m research.wgamma_d16.mixed_hz_sources
python -m unittest research.wgamma_d16.test_zee_mixed_hz -v
```
