# Preliminary numerical hZ neutral LFV check — source Eq. (59), 8 Nov 2026

**Status: SOURCE_EQUATION_EVALUATED / AUTHOR_CODE_NOT_INDEPENDENTLY_MATCHED / PHYSICAL_LFV_UNKNOWN.** This note is new preliminary physics evidence, not a replacement for the existing `RESULT.json=EXECUTION_BLOCKED` or an accepted full LFV amplitude. No Codex session or new scan was used for this calculation; independently written Python/mpmath was run interactively, with SciPy quadrature as an independent check of the loop integral.

## Source, conventions and inputs

Primary source: Altmannshofer et al., *Electron EDM and Γ(μ→eγ) in the 2HDM*, JHEP06(2025)156, [arXiv:2410.17313v4](https://arxiv.org/html/2410.17313v4) **Eq. (59)** for `c_{R,L}^{hZ}`, **Eq. (35)** for `f_{7±}`, **Eq. (48)** for the effective dipole action. The published `hZ` is a standalone neutral gauge-invariant group in the 2HDM; this does not validate other `kin`/charged-Zee sectors. The documented 2026 erratum chiefly concerns Eqs. (54)-(55), not Eq. (59), but no independent author-code computation of `hZ` was obtained.

Algebraic matching: `NEUTRAL_YUKAWA_ORDERED_MAPPING.md`. `rho^†=D/√2`; `rho_{l,21}^*=D_{eμ}/√2` enters `c_R`, `rho_{l,12}=D_{μe}^*/√2` enters `c_L`; native `C_{L,R}=-c_{L,R}/(8π²v²)`.

For CP-conserving neutral mixing, `q_h1=cos(beta-alpha)`, `q_h2=-sin(beta-alpha)`, `q_H1=sin(beta-alpha)`, `q_H2=cos(beta-alpha)`, and `q_A1=0`. Therefore only the heavy CP-even state contributes to the Eq. (59) difference, proportional to `sin(beta-alpha)cos(beta-alpha)`.

The source-hashed D7 and F13 scalar inputs were taken from original `research/full_constraints/higgs/h125_receipts/{D7,F13}_h125.in` as `tanbeta`, `alpha_SusHi`, `mh=125`, `mH=Block MASS 35`. The frozen F13 execution `higgs/neutral_receipts/F13_EXECUTION.json` directly verifies `alpha_physical=alpha_SusHi−π/2`. D7 and F13 values:

| Input | D7 | F13 |
|---|---:|---:|
| tanβ | 1.1157268700505090 | 5.3077513190433523 |
| α_SusHi | 2.3627051010413220 | 2.9578268064201572 |
| m_h (GeV) | 125 | 125 |
| m_H (GeV) | 492.43078309962277 | 707.08193786447146 |
| β−α_physical | 0.048133334 | −0.0024549704 |

**Electroweak numerical scheme for this diagnostic only**: `v=246.21965 GeV`, `M_Z=91.1876 GeV`, `m_mu=0.1056583745 GeV`, `alpha_EM=1/137.035999084`, `sin²theta_W=0.23122`. This is *not* claimed to reproduce every running-coupling or renormalization-scheme choice of the author `thdm.py`; no theoretical-uncertainty calibration performed.

The **four** direct `D_{eμ}`, `D_{μe}` entries and signed baseline dipoles were taken **unchanged** from the hash-verified `CARD_PROVENANCE.json` and `BASELINE_REPLAY.json` saved in this same directory, **texture witnesses** (not historical `scale_0.001` cards).

## Evaluated expression

Using the original source's \(v_e^Z=(-1/2+2s_W²)/(s_W c_W)\), \(a_e^Z=(+1/2)/(s_Wc_W)\), \(x_{Zs}=M_Z²/m_s²\):

\[
c_R^{hZ}=-\frac{e\alpha}{48\pi s_W c_W}\frac{v²}{M_Z m_\mu}\,
\sin(\beta-\alpha)\cos(\beta-\alpha)\,\frac{D_{e\mu}}{\sqrt2}
\left[(v_e^Z)^2\Delta f_{7+}+(a_e^Z)^2\Delta f_{7-}\right],
\]
\[
c_L^{hZ}=\left(c_R^{hZ}\text{ with }D_{e\mu}\to D_{\mu e}^{*}\right),\quad
\Delta f_{7\pm}=f_{7\pm}(M_Z²/m_H²)-f_{7\pm}(M_Z²/m_h²).
\]

Eq. (35) `f7` was evaluated with **50 decimal digits** and with a one-dimensional representation for the source \(\Phi(1/(4x))\):
\[
\Phi(1/(4x))=\int_0^1\mathrm dt\,
\frac{\log[t(1-t)/x]}{t(1-t)-x},
\]
where the removable points at \(t(1-t)=x\) are evaluated by their limit \(1/x\). Cross-check: independent `scipy.integrate.quad` versus `mpmath.quad` integral values at \(x=0.01,\ M_Z²/m_H²\) for both D7/F13 and \(M_Z²/m_h²\); relative differences are \(3.0\times10^{-15}\), \(2.4\times10^{-16}\), \(2.0\times10^{-14}\), \(7.6\times10^{-16}\), respectively. These independently verify the integral evaluation, **not** the full author program or analytic two-loop diagram renormalization.

Numerically, \((\Delta f_{7+},\Delta f_{7-})=(-1.424737373,-0.8759489842)\) for D7, \((-1.722202669,-0.9674053207)\) for F13.

## Four-card numerical diagnostic (NOT complete physical LFV)

| Card | ΔC_L^{hZ} (GeV⁻²) | ΔC_R^{hZ} (GeV⁻²) | norm ΔC | norm ΔC / retained norm |
|---|---:|---:|---:|---:|
| D7 NO | \((4.18580+4.18580i)\times10^{-28}\) | \((-2.24823-8.99292i)\times10^{-30}\) | \(5.92034\times10^{-28}\) | \(4.24263\times10^{-13}\) |
| D7 IO | \(3.13935\times10^{-28}\) | \((8.33889+37.4228i)\times10^{-29}\) | \(4.95536\times10^{-28}\) | \(1.34662\times10^{-13}\) |
| F13 NO | \((-7.38585+7.38585i)\times10^{-31}\) | \((-4.21946-14.9304i)\times10^{-32}\) | \(1.05598\times10^{-30}\) | \(1.48923\times10^{-15}\) |
| F13 IO | \((-2.21576-1.47717i)\times10^{-30}\) | \((-3.54867+4.60173i)\times10^{-31}\) | \(2.72567\times10^{-30}\) | \(2.11007\times10^{-15}\) |

The **relative changes in the diagnostic partial dipole rate**, after coherent addition to the saved baseline, are: D7 NO \(-1.11304\times10^{-14}\), D7 IO \(+1.54429\times10^{-13}\), F13 NO \(-4.10120\times10^{-16}\), F13 IO \(+3.45795\times10^{-16}\) (high-precision evaluation, **not physical BR shifts**). No complete physical rate or exclusion has been produced.

This shows that **within the stated Eq. (59) mapping, this neutral gauge-invariant contribution is far too small to matter on these texture inputs**, because the direct \(D_{e\mu},D_{\mu e}\) entries are extraordinarily small and the chosen scalar states are close to neutral alignment. This does **not** place a numerical bound on the charged/gauge singlet-\(F\) sector or establish that other missing 2HDM/Zee terms are small.

## Safeguards and next action

- Verify the numerical `c_{L,R}^{hZ}` against the **pinned, post-erratum author implementation** with two nonzero complex source controls before marking it validated. The paper expression alone and independent \(\Phi\) integration are not a full independent amplitude calculation.
- Then evaluate the **neutral heavy-fermion \(Z\gamma\)** portion of corrected Eqs. (54)-(55) separately, retaining the appropriate Type-II-quark \(\rho_f\) and post-erratum signs/conjugations. The source says these Z pieces are generally suppressed by \(v_e^Z\), but this is not a per-card bound.
- Prioritize the residual potentially material Zee \(F^\dagger F\), mixed \(F D\), charged-current and gauge contributions **after** the two neutral sectors are completed, without restarting the complete global constraints/vacuum studies.
- Do **not** update `RESULT.json`, assign LFV PASS/FAIL, or authorize a parameter scan on the basis of this preliminary note.
