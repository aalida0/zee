# Zee Type-II charged-cascade LFV: genuine mixed two-loop obstacle — physics decision

**10 November 2026. Completed exact tree-current/spurion algebra, source-locked materiality tests. No complete gauge-invariant two-loop LFV coefficient has been computed.**

## Executive decision

**The full mixed charged-Higgs/W/Goldstone two-loop amplitude is NOT a necessary prerequisite for an explicitly scoped leading-LFV phenomenology paper.** This is an order-definition decision and published-practice precedent, **not** a mathematical demonstration that every omitted coefficient is negligible or a valid full-constraints acceptance test.

The paper can consistently declare:
1. all source-verified **leading one-loop charged and neutral Zee scalar** dipoles, including both charged states, `F†F`, `DD†` and their complex phases;
2. **selected leading/enhanced two-loop neutral Barr–Zee** terms from the corrected general-2HDM code and separately checked scalar/photon terms, avoiding double counting;
3. leading-order coherent 3-lepton and conversion Wilsons **only to the extent their full process amplitudes and scheme are matched**. Otherwise these observables must be explicitly labeled diagnostics/unassessed and **not used as hard allowed-region cuts**;
4. all uncomputed genuine finite two-loop W/Goldstone F-sector dressing as beyond the declared precision, **unless a specific newly enhanced independent invariant is identified**.

There is **no** claim of all-orders LFV, of a gauge-complete next-to-leading-order Zee model, or of a globally allowed benchmark.

## Exact mixing and spurion identities (new executable checks)

Let the physical charged eigenstates have doublet and singlet fractions

```
u=(cos gamma,-sin gamma),  v=(sin gamma,cos gamma).
P_D = u u^T,  P_S = v v^T, P_D+P_S=I.
Q_gamma/e = I.
Q_Z/(g/cW) = P_D/2 - sW² I.
Q_Z(1,2)/(g/cW) = -sin(gamma)cos(gamma)/2.
```

The photon charge is identical for the singlet and doublet. Thus no tree-level off-diagonal photon charged-scalar vertex arises from any charged mixing; `[Q_gamma,Q_Z]=0` and `Q_gamma^{12}=0` **exactly**.

For *any* scalar-only diagonal mass kernel `f`, the mixed overlap is

```
u^T diag(f(mH1²),f(mH2²)) v
  = cos(gamma)sin(gamma) [f(mH1²)-f(mH2²)].
```

The overlap vanishes at equal masses or at constant `f`. That cancellation is an exact charged-state identity, **not a proof of full finite W/Goldstone gauge cancellation**. The mixed mass matrix entry and charged potential parameter satisfy

```
M^2_DS=cos(gamma)sin(gamma)*(mH1²-mH2²),
mu4 = -sqrt(2)/v_EW * M^2_DS.
```

With the gauge-invariant lepton number convention `L(L)=L(eR)=1`, `L(chi+)=-2`, `L(H1,H2)=0`, the antisymmetric `F LL chi+` vertex preserves assigned lepton number, whereas the scalar mixing `mu4 H1 H2 chi-` carries a two-unit breaking spurion. The *L-conserving* charged dipole cannot have an unmatched *single* `mu4` spurion. This rules out particular one-mixing-insertion `F D` structures in the massless-neutrino limit; it **does not** rule out two-spurion contributions, `F†F` gauge dressing, all `DD†` corrections or contributions requiring explicit neutrino-mass insertions.

Neutral scalar Barr–Zee contributions with exactly one external neutral-scalar LFV Yukawa necessarily factor `D_e_mu` or `D_mu_e`. Their magnitudes in these saved cards are at a numerical floor and must not be treated as symmetry-protected zeroes; a future scan must reevaluate the textures.

## Source-matched numerical dressing sensitivity

The calculation reads the exact SHA-256-locked four D12 witnesses; checks their complex `F†F` invariants and both charged-state propagator weights against the **existing** source-gated `lfv_precision_scope_2026/SCOPE_DIAGNOSTICS.json`; and uses the **later native-generated** four one-loop `mu->e gamma` rates from `NATIVE_COMPLETE_ONELOOP_LFV_FOUR_CARD_GATE_2026-11-10.json`.

The normalization is internally consistent: `alpha(MZ)=1/127.95`, `m_mu=0.1056583755 GeV`, `Gamma_mu=hbar/(2.1969811 us)`, `BR_90CL=1.5e-13` (MEG II, EPJC85 1177, 2025).

For a strictly hypothetical correction parallel to the full two-chirality `F†F` dipole vector,

```
delta C_F = [g²/(16*pi²)] K C_F^(one loop),
epsilon_g = g²/(16*pi²) = alpha(MZ)/(4*pi*sin²thetaW),
||C_F|| = |C_R^F| sqrt(1+(m_e/m_mu)²).
```

Define `K_critical = (sqrt(BR_limit/N)-sqrt(BR_one_loop/N))/(epsilon_g||C_F||)` where `N=alpha*m_mu^5/(4 Gamma_mu)`. The triangle inequality guarantees the **one-loop plus this specific assumed correction** stays below the radiative limit whenever `|K|<K_critical`.

| Card | native BR(mu->e gamma) one-loop | |F†F| | charged mixed Z12/(g/cW) | mu4 [GeV] | conditional K_critical |
|---|---:|---:|---:|---:|---:|
| D7 NO | 1.554528844e-19 | 4.936365228e-9 | -0.12172496356 | 272.3613 | **1.758218e7** |
| D7 IO | 1.081033349e-18 | 8.577952583e-9 | -0.12172496356 | 272.3613 | **1.010116e7** |
| F13 NO | 4.013887756e-20 | 4.936365228e-7 | -0.20532592083 | 1026.1179 | **7.036999e5** |
| F13 IO | 1.332087711e-19 | 8.577952583e-7 | -0.20532592083 | 1026.1179 | **4.047868e5** |

**K is uncalculated and has no rigorous bound.** These unusually large thresholds make ordinary perturbative gauge dressing of the known F dipole an implausible source of these benchmark exclusions, but that inference is a power-counting screening argument, not a bound, exclusion, or proof of all-Zee two-loop completeness. The result does NOT cover a new leading operator, a different flavor tensor, chirality enhancements, large new dimensionful couplings, or cancellation-driven sensitive points. The maximum direct `D_e_mu/D_mu_e` among four cards is `3.067e-19` and the Yukawa norms are small, but those facts do not prove RGE-stable zeros or global constraints.

## Literature matching and limits

- Altmannshofer *et al.*, **JHEP 06 (2025) 156**, arXiv:2410.17313v4, plus **JHEP 07 (2026) 184 erratum**: explicit leading-enhanced two-loop 2HDM organization. Their single doublet charged scalar and external Yukawa structures are **not** the general Zee mixed singlet/doublet.
- Heeck & Thapa, **Phys. Lett. B 841 (2023) 137910**, arXiv:2303.13383, Sec. III: a Zee phenomenology calculation omitting identified suppressed Z/charged/W bosonic Barr–Zee groups. It assumes **alignment and vanishing extra-doublet quark Yukawas**; these assumptions do **not** hold automatically for Type-II cascade points.
- Herrero-García *et al.*, **JHEP 04 (2017) 130**, arXiv:1701.05345: general Zee scan with explicitly limited perturbative precision and non-Type-II quark Yukawa choices.
- MEG II, **EPJC 85 (2025) 1177**, arXiv:2504.15711: observed 90% CL `BR(mu->e gamma)<1.5e-13`.

This source-backed perturbative-order choice was already identified in the repository's **8 November** `lfv_precision_scope_2026/LFV_PERTURBATIVE_SCOPE_DECISION_2026-11-08.md`. The **new** contribution here is the executable physical charged gauge current/spurion algebra and later **source-replayed** radiative one-loop benchmark threshold test including both F chiralities.

## Paper scope versus full-theory claim

**Resolved as a scoped phenomenology prerequisite:** It is scientifically consistent to proceed without a complete fixed-order Zee mixed gauge two-loop amplitude, **provided** this truncation is documented, all selected leading enhanced pieces are included without duplication, and omitted processes do not become hard experimental filters.

**NOT resolved:** the original user's literal request for a **gauge-complete two-loop Zee LFV amplitude**, whose `R_xi` cancellation and finite Wilson coefficients are still uncalculated. The available SARAH generated one-loop FlavorKit source, the published 2HDM code and these exact gauge-current identities are **not** a substitute for a full independent two-loop computation.

For a paper claiming **all applicable constraints**, more urgent independent gates remain in one-loop `mu->3e` finite-`q²` and counterterms, Type-II conversion hadronic scheme, `B->Xs gamma` physical uncertainties, Higgs direct searches/total widths and vacuum globality. Do not promote the four low-texture witnesses to globally allowed while these remain unresolved.

## Reproduce

```sh
python3 -m unittest research.full_constraints.lfv_two_loop_scope_2026.test_gauge_spurion_screen -v
python3 -m research.full_constraints.lfv_two_loop_scope_2026.gauge_spurion_screen --output zee_two_loop_scope_conditional.json
```

CI run: https://github.com/aalida0/zee/actions/runs/42839081528 (five focused tests plus four-card machine JSON; PASSED). Neither this report nor CI claims a computed missing complex K.

**Gate: `SCOPED_LEADING_LFV_TWOLOOP_PREREQUISITE_RESOLVED`; `FULL_ZEE_TWOLOOP_MIXED_GAUGE=UNKNOWN`; `PHYSICAL_LFV=UNKNOWN`; `GLOBAL_ACCEPTANCE=null`.**
