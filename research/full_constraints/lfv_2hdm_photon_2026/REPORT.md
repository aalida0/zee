# One-loop off-shell photon transfer to the Type-II Zee cascade model
**9 November 2026 | source-backed analytic implementations and independent four-card arithmetic**
**Status: TWO_RESTRICTED_SUBSETS_CALCULATED; FULL_PHYSICAL_LFV=UNKNOWN.**

## Implemented physics (not another audit)

1. **Neutral-scalar internal-tau photon monopole**: `tau_monopole.py`. Direct implementation of the **published restricted** neutral h/H/A tau-loop vector amplitude from Herrero-García, Ohlsson, Riad, Wirén, *JHEP 04 (2017) 130*, [doi:10.1007/JHEP04(2017)130](https://doi.org/10.1007/JHEP04(2017)130), Sec. 3.3.4 **Eq. (3.25)**. Fully preserves the two complex flavor orderings. The published \(g_{LV}\) and \(g_{RV}\) are stored in **that paper's convention**, not yet transferred into the common native K1 EFT basis. Internal e/mu loops, external invariant corrections and generic Zee charged loops are NOT in that equation. It is not the complete photon monopole.
2. **Charged scalar, massless active neutrino, off-shell photon \(A_1\)**: `charged_k1.py`. Transfers the **universal charged scalar/neutral fermion topology** from Raghavendra Srikanth Hundi, *Eur. Phys. J. C 85 (2025) 805*, [doi:10.1140/epjc/s10052-025-14505-2](https://doi.org/10.1140/epjc/s10052-025-14505-2), **Eq. (23)**. It implements **both** physical Zee charged masses, doublet fractions \((c_\gamma,-s_\gamma)\), singlet fractions \((s_\gamma,c_\gamma)\), native \(D D^\dagger\) and \(F^\dagger F\) complex flavor invariants, and both external lepton chiralities. A classic reference for this non-dipole topology is Toma and Vicente, *JHEP 01 (2014) 160*, [doi:10.1007/JHEP01(2014)160](https://doi.org/10.1007/JHEP01(2014)160). This is the *same QED scalar/neutral fermion topology*, not a transfer of the scotogenic mass model.
3. Neutral and charged source terms are intentionally **not added in one signed low-energy Wilson** until their different published conventions and the complete neutral-photon form factors have been matched. `full_common_K1=null`; no physical \(\mu\to3e\) or Al rate claimed.

## Exact charged source and operator

Hundi Eq. (23), charged scalar \(S^+\) and neutral fermion of mass \(m_N\), defines the off-shell source vertex
\[
ie\,\bar u_e\left\{
 A_1\left[q^2\gamma^\mu P_L-(m_\mu P_R-m_eP_L)q^\mu\right]
 + A_2(m_\mu P_R+m_eP_L)i\sigma^{\mu\nu}q_\nu
\right\}u_\mu,
\]
plus the \(L\leftrightarrow R\) mirror. The paper defines
\[
A_1=-\frac{y_\mu y_e^*}{16\pi^2\,6m_S^2}G_1(x),\quad
A_2=-\frac{y_\mu y_e^*}{16\pi^2\,2m_S^2}G_2(x),
\quad x=m_N^2/m_S^2,
\]
\[
G_1(x)=\frac{2-9x+18x^2-11x^3+6x^3\ln x}{6(1-x)^4},
\quad G_2(x)=\frac{1-6x+3x^2+2x^3-6x^2\ln x}{6(1-x)^4}.
\]
At \(x=0\), \(G_1(0)=1/3\), \(G_2(0)=1/6\), and therefore \(A_1/A_2=2/3\) **within each single charged scalar and fixed Yukawa chirality**. For the Zee two-state massless-neutrino approximation,
\[
A_{1L}^{F}=-\frac{(F^\dagger F)_{e\mu}}{288\pi^2}
\left(\frac{s_\gamma^2}{m_{H_1^\pm}^2}+\frac{c_\gamma^2}{m_{H_2^\pm}^2}\right),
\qquad
A_{1R}^{D}=-\frac{(D D^\dagger)_{e\mu}}{288\pi^2}
\left(\frac{c_\gamma^2}{m_{H_1^\pm}^2}+\frac{s_\gamma^2}{m_{H_2^\pm}^2}\right).
\]
These two chiralities do **not** interfere at the one-loop vertex level for massless active neutrinos; a mixed \(F D\) flip requires a neutrino mass insertion. The **source** dipole coefficients for the same loop are \(A_{2R}^{F}=3A_{1L}^{F}/2\) and \(A_{2L}^{D}=3A_{1R}^{D}/2\), where \(A_2\) carries the explicit \(m_\mu P_{R/L}+m_eP_{L/R}\) daughter-mass flips.

**Physical and normalization checks:** The charged source dipoles \(A_{2R}^{F}\) and \(A_{2L}^{D}\) match the frozen `module3.core.dipole_ledger` chiral coefficients, including its \(m_e/m_\mu\) suppressed mirror coefficients. This source-to-native on-shell agreement is necessary, but **does not independently establish** the full off-shell Zee vertex renormalization, cancellation of all model-specific diagrams, or the relative sign to other \(K_1\), Z and box operators. Eq. (23) is transverse between on-shell spinors: \(q_\mu\sigma^{\mu\nu}q_\nu=0\), and \(\bar u_e\slashed qP_Lu_\mu=\bar u_e(m_\mu P_R-m_eP_L)u_\mu\). The algebraic Ward check is not presented as an independent gauge-dependent loop-level check.

## Neutral tau-only published Eq. (3.25)

JHEP04(2017)130 gives, in its own \(\mu N\to e N\) vector-action convention,
\[
g_{LV}^{\mathrm{neutral},\tau}=
-\frac{\alpha}{18\pi}\sum_{\phi=h,H,A}
\frac{4+3\ln(m_\tau^2/m_\phi^2)}{m_\phi^2}
 C_{\phi,\tau\mu}\,C_{\phi,\tau e}^*,
\quad
g_{RV}^{\mathrm{neutral},\tau}=
-\frac{\alpha}{18\pi}\sum_\phi\frac{4+3\ln(m_\tau^2/m_\phi^2)}{m_\phi^2}
 C_{\phi,\mu\tau}^* C_{\phi,e\tau}.
\]
Here each \(C_\phi\) is the **off-diagonal** native neutral lepton Yukawa vertex. This maps the source's \(Y_{2,\tau\mu}Y_{2,\tau e}^*\) with the corrected \(\rho_\ell=D/\sqrt2\). In the generic-basis mass-diagonal off-diagonals \(Y_2^{\tau\mu}=c_\beta D_{\tau\mu}\); the native-\(h,H\) version of source \(g_{h0}^{(2)}\) is \((-s_{\beta-\alpha}, c_{\beta-\alpha},-i)/(\sqrt2 c_\beta)\). Using native \(\alpha,\beta\) directly in the source paper without accounting for the two angle conventions would lead to a wrong physical-h admixture.

**The Eq. (3.25) source's normalization to the fully signed \(A_1\) one-loop vertex or nuclear-response \(g_{p,n}\) is not yet independently verified**, so the separate tau-only \(g_{LV/RV}\) must NOT be summed with \(A_{1L/R}^{D,F}\) until that map is established.

## Actual four-card results (complex, GeV^-2)

| Exact card | \(A_{1L}^{F}\) from charged singlet | \(A_{1R}^{D}\) from charged doublet | \(g_{LV}^{\tau,hHA}\) (2017 convention) |
|---|---|---|---|
| D7 NO texture_0.0001 | \((1.14657+1.46669i)10^{-17}\) | \((1.02590+1.31328i)10^{-18}\) | \((1.66469+1.45389i)10^{-17}\) |
| D7 IO texture_0.0001 | \((1.45684+2.88843i)10^{-17}\) | \((1.49886+2.97653i)10^{-18}\) | \((0.459132+4.14401i)10^{-17}\) |
| F13 NO texture_0.001 | \((2.86617+3.66641i)10^{-16}\) | \((2.84547+3.64253i)10^{-21}\) | \((5.12462+4.47567i)10^{-20}\) |
| F13 IO texture_0.001 | \((3.64178+7.22045i)10^{-16}\) | \((4.15727+8.25577i)10^{-21}\) | \((1.41340+12.75697i)10^{-20}\) |

**Material physics takeaway:** F13 \(F^\dagger F\) off-shell charged photon monopole is much larger than the source's neutral-tau term. The known tiny direct \(D_{e\mu}\) does NOT suppress the \(F^\dagger F\) one-loop monopole. This is why the off-shell photon had to be explicitly included rather than using a dipole-only conversion approximation.

These are **coefficients**, not physical \(\mu\to3e\) branching ratios, full converted \(g_{p,n}\), benchmark LFV PASS, or experimental exclusions.

## Independent checks actually performed

The original source-hashed four frozen D12 witnesses were independently processed through a separate arithmetic implementation:
- Tau-only neutral: native full \(D\) Yukawa vertices versus generic-basis \(Y_{e2}\) source ordering, **both complex chiralities**, all \(h,H,A\); maximum relative residual **2.305e-16**.
- Charged: direct complex \(F^\dagger F\) and \(D D^\dagger\) evaluation from original matrices versus the prior independently audited source invariants; published \(G_1(0)/G_2(0)\) loop factors and on-shell native charged-dipole normalization; maximum numerical relative discrepancy **2.514e-16** in these controls.
- New reproducible Python tests cover complex lepton-field rephasings, \(D=0\), \(F=0\), charged scalar mass/state exchange, one-sided chirality tests, decoupling, and the Ward-identity algebra. **Python tests were not run on the user's local checkout in this assistant session**; the independent checks above did run.

The artifacts `RESULT.json`, `CHARGED_RESULT.json`, `VALIDATION_RECEIPT.json`, `CHARGED_VALIDATION_RECEIPT.json` capture numerical coefficients and validation metadata. All other research/frozen source trees remain unchanged.

## Run tests now in user's checkout

```bash
cd ~/zee
git switch research/zee-full-constraints
git status --short
git pull --ff-only origin research/zee-full-constraints
python3 -m unittest discover -s research/full_constraints/lfv_2hdm_photon_2026 -p 'test_*.py' -v
python3 -m research.full_constraints.lfv_2hdm_photon_2026.tau_monopole
python3 -m research.full_constraints.lfv_2hdm_photon_2026.charged_k1
git status --short
```

The two executables write their own `RESULT.json` and `CHARGED_RESULT.json` only. They do not modify archived modules.

## Exact remaining task after the partial calculation

1. **Complete and independently match all neutral internal e,mu,tau one-loop photon \(\gamma^*\) form factors**, with external invariant effects where material; source Eq. (3.25) only includes a dominant tau term.
2. Establish **one** common signed off-shell-photon operator basis: relate the 2017 \(g_{LV/RV}\) tau-only vector coefficient, Hundi \(A_{1L/R}\), and native \(K_{1L/R}\), including charge factors and off-shell Ward amplitude, using an independent common 2HDM limit/source comparison.
3. **Z penguin and boxes**: import source-complete 2HDM neutral and charged gauge-invariant groups, plus 2-state Zee F terms; match relative ordered-operator signs against `lfv_lo_closure_2026` restricted F box and tree scalar.
4. **Al conversion matching**: only after signed full vector, QED/QCD evolution and nuclear uncertainties, invoke the existing `lfv_lo_closure_2026.adapter.al_kernel` in its own source convention, correcting prior generated FlavorKit p/n scalar mismatch.

**Verdict remains `physical_lfv=UNKNOWN,global_acceptance=null`.** This is an increase in explicitly calculated one-loop source terms, not a declaration that all leading LFV is complete.
