# Coy–Frigerio 2022 EFT control for the mixed Zee Type-II project

**9 Nov 2026 — SOURCE-LIMIT CONTROL COMPLETE; PHYSICAL LFV UNKNOWN.**

Source: Rupert Coy and Michele Frigerio, *Effective comparison of neutrino-mass models*, Phys. Rev. D **105**, 115041 (2022), [arXiv:2110.09126v2](https://arxiv.org/pdf/2110.09126). The relevant published equations are (1), (9), (11), (23), (70), (71) and Tables 3 and 5.

The paper assumes parametrically heavy new states, neglects Yukawa couplings of the second doublet to quarks, and illustrates the decoupled singlet-only and doublet-only limits. Its published full Zee-model exclusions **do not apply** directly to the strongly mixed Type-II benchmarks in this repository.

## Newly computed F-only left-current contact, four actual cards

In the frozen native convention, the antisymmetric source Yukawa is $Y_\delta=F/2$. For the exact broken-phase zero-external-momentum charged exchange, define

$$
w_F=\frac{\sin^2\gamma}{m_{H_1^\pm}^2}
+\frac{\cos^2\gamma}{m_{H_2^\pm}^2}.
$$

The restricted F-only dimensionful left-current seed and the source's dimensionless normalization are

$$
C_{ll}^{e\mu\tau\tau}=\frac{w_F}{4}(F^\dagger F)_{e\mu},
\qquad
c_{ll}^{e\mu\tau\tau}=\frac{v^2}{2}C_{ll}^{e\mu\tau\tau}
=\frac{v^2w_F}{8}(F^\dagger F)_{e\mu}.
$$

This is a **broken-phase F-only tree contact**, not a claim of complete gauge-invariant mixed-state SMEFT matching at a high scale. Other native D/F interactions remain unknown. For $v=246.22$ GeV, saved exact low-joint textures give:

| Card | Re $c_{ll}$ | Im $c_{ll}$ | $w_F^{-1/2}$ [GeV] |
| --- | ---: | ---: | ---: |
| D7 NO | -2.4697262e-10 | -3.1592701e-10 | 305.43 |
| D7 IO | -3.1380459e-10 | -6.2217216e-10 | 305.43 |
| F13 NO | -6.1737863e-9 | -7.8974983e-9 | 610.88 |
| F13 IO | -7.8444424e-9 | -1.5552971e-8 | 610.88 |

If one hypothetically took an **unmixed** scalar singlet at the physical H2 mass with the same F, the contact would be smaller by **3.0446** (D7) or **2.0433** (F13). Therefore the actual charged-scalar mixing cannot be dropped from these benchmarks.

## Independent analytic source limit for g4 and g6

In the source's strictly unmixed $\epsilon_\delta$-only limit, the leading-log SMEFT entries of Table 3 satisfy

$$
c_{Hl}^{(1)}+c_{Hl}^{(3)}
=\frac{2(g_1^2+g_2^2)}{3}
c_{ll}^{e\mu\tau\tau}\frac{\log(M/v)}{16\pi^2}.
$$

Inserting these into the paper's Eqs. (70)–(71), the weak-scale gauge-logarithmic pieces cancel, using $e^2=g_1^2(1-s_W^2)=g_2^2 s_W^2$. The resulting restricted-limit identity is

$$
g_4=g_6=\frac{e^2}{3\pi^2}
\log\left(\frac{v}{m_\tau}\right)c_{ll}^{e\mu\tau\tau}.
$$

Both published equations were numerically evaluated on each of the four frozen complex F matrices, *only in the synthetic limit* $D=0,\gamma=0$ with the singlet at $m_{H_2^\pm}$. Explicit-vs-simplified relative residuals are below $3\times10^{-16}$. Source-limit $g_4,g_6$ values are saved in the accompanying JSON. They are **not** mixed-model Wilson coefficients.

**Double-counting warning:** This leading-log source contains photon-induced operator mixing; it must not be summed with the current finite off-shell charged-photon form factor $A_1$ or the restricted F box before the common LEFT basis and subtraction/overlap are independently matched. No complete $\mu\to3e$ branching ratio, Al conversion rate, LFV pass/fail, or collider accept/reject decision is inferred.

## Numerical receipt and next scientific decision

Computed directly from the committed \`lfv_2hdm_photon_2026/CHARGED_RESULT.json\` source. Four reconstructions of the prior $A_{1L}^F=-(F^\dagger F)_{e\mu}w_F/(288\pi^2)$ pass with maximum relative discrepancy $1.91\times10^{-16}$. The $g_4=g_6$ control and its analytical simplification pass with maximum relative discrepancy $2.13\times10^{-16}$ in independent Python and JavaScript arithmetic.

Machine-readable result: [COY_FRIGERIO_EFT_SOURCE_LIMIT_2026-11-09.json](COY_FRIGERIO_EFT_SOURCE_LIMIT_2026-11-09.json).

**Verdict:** The paper is a successful restricted analytic control for the frozen Type-II setup, not a substitute for complete finite mixed-Zee $\gamma^*$, $Z$, and box matching. B physics, Higgs and full LFV remain globally UNKNOWN; no new parameter scan was run.
