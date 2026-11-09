# Zee Type-II: Coy–Frigerio 2022 EFT source-limit calculation

**9 November 2026.** **Verdict: F-only broken-phase tree coefficient and the unmixed EFT leading-log limit CHECKED; physical full Zee LFV UNKNOWN.**

## Primary source and use restrictions

Rupert Coy and Michele Frigerio, *Effective comparison of neutrino-mass models*, **Phys. Rev. D 105, 115041 (2022)**, [arXiv:2110.09126v2](https://arxiv.org/pdf/2110.09126), especially Secs. 2.2, 3.1, 5.2, Eqs. (1), (9), (11), (23), (69)–(71), Tables 3 and 5. The source sets second-doublet quark Yukawas to zero, assumes heavy fields integrated out above the electroweak scale, and illustrates LFV using decoupled epsilon_delta-only and epsilon_2-only limits. **Its benchmark exclusions and leading-log g4,g6 formulas are not complete Type-II mixed-Zee results.**

### A directly calculable two-state tree contact

The native physical singlet fractions are \$s_\\gamma,c_\\gamma)\$, with masses \$m_1,m_2\$. The exact broken-phase massless-external-momentum tree matching of the F-only four-lepton left-current seed is

\$
w_F=\\frac{s_\\gamma^2}{m_1^2}+\\frac{c_\\gamma^2}{m_2^2},
\\qquad C_{ll}^{e\\mu\\tau\\tau}=\\frac14(F^\\dagger F)_{e\\mu}w_F,
\\qquad c_{ll}^{e\\mu\\tau\\tau}=\\frac{v^2}{2}C_{ll}=\\frac{v^2}{8}(F^\\dagger F)_{e\\mu}w_F.
\$

Here the source's antisymmetric \$Y_\\delta\$ corresponds to native \$F/2\$ at the component-vertex level; the factor \$v^2/2\$ converts its dimensionful dim-6 Wilson \$C_{ll}\$ into the source's dimensionless \$c_{ll}\$ (Eq. 1). This is a **tree contact/operator-seed check after electroweak symmetry breaking**, not an assertion that integrating out two strongly mixed charged states generates only this gauge-invariant SMEFT operator above the weak scale. Other doublet and mixed-vertex operators are not set to zero.

Using only the saved four low-joint textures from `CHARGED_RESULT.json`, the source-normalized dimensionless seed (`v = 246.22 GeV` for this numerical audit) is:

| Card | \$\\operatorname{Re} c_{ll}\$ | \$\\operatorname{Im} c_{ll}\$ |
|---|---:|---:|
| D7 NO | \$-2.4697262\\times10^{-10}\$ | \$-3.1592701\\times10^{-10}\$ |
| D7 IO | \$-3.1380459\\times10^{-10}\$ | \$-6.2217216\\times10^{-10}\$ |
| F13 NO | \$-6.1737863\\times10^{-9}\$ | \$-7.8974983\\times10^{-9}\$ |
| F13 IO | \$-7.8444424\\times10^{-9}\$ | \$-1.5552971\\times10^{-8}\$ |

The corresponding \$w_F^{-1/2}\$ is **305.43 GeV (D7)** or **610.88 GeV (F13)**. With singlet artificially assigned to \$H_2^\\pm\$ only (unmixed \$\\gamma=0\$ control), the tree seed would be smaller by factors **3.0446 (D7)** or **2.0433 (F13)**. Mixing is therefore material even before loops; an unmixed-singlet phenomenology bound cannot be transferred blindly.

### A source-specific leading-log limiting identity (not a physical rate)

In Coy–Frigerio's **unmixed epsilon_delta-only** limit, the source tree and one-loop leading-log coefficients yield

\$
c_{Hl}^{(1)}+c_{Hl}^{(3)}
 =\\frac{2(g_1^2+g_2^2)}{3}c_{ll}^{e\\mu\\tau\\tau}
 \\frac{\\log(M/v)}{16\\pi^2}.
\$

Substitution into the paper's Eqs. (70) and (71), using \$e^2=g_1^2(1-s_W^2)=g_2^2s_W^2\$, gives the algebraic cancellation

\$
g_4=g_6=\\frac{e^2}{3\\pi^2}\\log\\!\\frac{v}{m_\\tau}\\,
c_{ll}^{e\\mu\\tau\\tau}.
\$

The explicit Eq. (70)/(71) calculations agree with this simplification at \$\\lesssim 3\\times 10^{-16}\$ relative on all four complex textures. **This is an independent analytic/numerical control of a published restricted limit, not an operator we can add to the current mixed-Zee photon or box ledger.** The full source limit uses \$D=0,\\gamma=0\$, with the charged singlet at \$m_{H_2}\$; its \$g_4=g_6\$ coefficients are saved separately in the JSON result.

The QED photon mixing implicit in \$g_4,g_6\$ requires explicit subtraction/matching before any combination with the existing one-loop \$A_1\$ monopole; otherwise double counting is possible.

### Why the EFT paper does not close our four-card LFV predictions

1. The relevant H1 masses are **298.73 GeV for D7** and **572.23 GeV for F13**, and the actual singlet fractions in H1 are **93.67%** and **78.52%**, respectively. This is not the source's unmixed, parametrically heavy spectrum. The source's illustrative high-scale logarithms are not automatically numerically controlled at these masses.
2. Type-II quark couplings are **nonzero**; the source deliberately removes them. Its semileptonic vector formulas are useful as source structures but must be extended/matched with the actual UV quark operators.
3. The finite two-state charged off-shell monopole has been independently calculated in `lfv_2hdm_photon_2026/charged_k1.py`. The tree contact/leading logs here **do not replace** the missing complete neutral photon, low-\$q^2\$ Z penguin, D/F boxes, or common signed LEFT.
4. No physical \$\\mu\\to 3e\$ or \$\\mu N\\to e N\$ rates were calculated. `global_acceptance=null` stays untouched. The prior four charged-photon-only diagnostics remain partial.

## Validation and exact scope

The signed \$c_{ll}\$ values are obtained from the existing complex \$F^\\dagger F\$ flavor invariant and the physical two-state mass weights, with no scan. Four independent charged-loop \$A_{1L}^F=- (F^\\dagger F)_{e\\mu}w_F/(288\\pi^2)\$ reconstructions reproduce the archived coefficients to floating-point precision. Analytically independent source Eqs. (70)/(71) checks reproduce the simplified limit on four complex textures; results/receipts are in [COY_FRIGERIO_EFT_SOURCE_LIMIT_2026-11-09.json](COY_FRIGERIO_EFT_SOURCE_LIMIT_2026-11-09.json). Calculations ran in an isolated Python arithmetic control and via authenticated GitHub input with an independent JavaScript arithmetic implementation. These are analytic/numerical subset validations; no full loop-level source-to-code certification is claimed.

**Scientific decision:** use this paper as a **restricted analytic control**, not as a replacement for one-loop finite full mixed-Zee matching. Next highest-value task remains the common signed \$\\gamma^*\$/Z/box operator basis; do not start another general two-loop campaign. For the cascade pheno paper, preserve `PHYSICAL_LFV=UNKNOWN` until a complete declared-scope observable and uncertainty budget are validated.
