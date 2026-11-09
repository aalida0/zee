# External source reuse: Zee neutral-photon loop and complete one-loop route

**9 November 2026. Verdict: neutral tau SOURCE KERNEL matched; full physical LFV remains UNKNOWN.**

## Source checks and new numerical computation

- Herrero-García, Ohlsson, Riad, Wirén, JHEP 04 (2017) 130, [arXiv:1701.05345v2](https://arxiv.org/pdf/1701.05345), Eq. (3.25): restricted tau-only neutral-photon monopole.
- Chowdhury and Nasri, JHEP 12 (2015) 040, [arXiv:1506.00261v2](https://arxiv.org/pdf/1506.00261), Eqs. (3.11), (B.4): charged-fermion/neutral-scalar non-dipole loop. Different particle charges and representations require a native Zee operator match before using complete amplitudes.
- Porod, Staub, Vicente, EPJC 74 (2014) 2992, [DOI](https://doi.org/10.1140/epjc/s10052-014-2992-2), Secs. 5.3–5.4: generic off-shell photon monopole and four-fermion assembly machinery in FlavorKit, with special off-shell loop functions. This is a candidate for a complete one-loop coefficient backend, not automatic Zee validation.
- Kitano, Koike, Okada, PRD 66 (2002) 096002 and 2007 erratum: common nuclear overlap and complex interference conventions, needed before combining source coefficients.

The 2015 kernel is

$$
G_c(x)=\frac{16-45x+36x^2-7x^3+6(2-3x)\log x}{6(1-x)^4},
\quad x=m_\tau^2/m_\phi^2.
$$

At small x, $G_c(x)=(2/3)(4+3\log x)+O(x\log x)$. Thus

$$
-\frac{e^2}{48\pi^2m_\phi^2}G_{c,\mathrm{asym}}(x)
=-\frac{\alpha}{18\pi m_\phi^2}(4+3\log x),
$$

matching **the complete constant and logarithmic prefactor** of 2017 Eq. (3.25). Four-card numerical residual is below $4.2\times10^{-16}$.

Applying the **candidate** finite-x loop-kernel ratio to each existing 2017 tau-only scalar term changes its total $g_{LV/RV}$ by $4.14827\times10^{-5}$ relative for D7 NO/IO and $1.53212\times10^{-5}$ for F13 NO/IO. The 2017 approximation was already sufficiently accurate for this tau-only subset. This is a topology/loop-kernel check, *not* a new full neutral photon calculation or a proof of the relative native operator signs. The native electron/muon loops remain missing: their external momentum is not uniformly small compared with internal masses, so naïvely replacing $m_\tau$ in the source log formula is invalid.

Artifacts: NEUTRAL_TAU_GC_SOURCE_LIMIT_RESULT_2026-11-09.json, neutral_tau_Gc_source_limit.py, test_neutral_tau_Gc_source_limit.py. The numbers were independently evaluated directly against source-locked GitHub data in JavaScript. Python unit tests are committed but **not run on the user's checkout**.

## Highest-value existing numerical code to reuse next

The 2017 source alone does not give full one-loop mu3e/Al amplitudes, but **Zee FlavorKit output already exists on the user's machine**. The precise source paths and SHA-256 hashes are in research/full_constraints/lfv/SOURCE_TO_CODE_SOURCES.json:

- generated: /home/amine/zee-conditional-cascade-scan/validation/module14/local/output/ZeeTypeII/EWSB/SPheno/Observables/FlavorKit_LFV_ZeeTypeII.f90 ; SHA256 2d30006d8d4759b2b7bfe76e2e4795bd2cf2f19ef5cb5772390ed3155b1bc41d.
- couplings: same model output, EWSB/SPheno/Couplings_ZeeTypeII.f90 ; SHA256 a0de851498f3e68e7421538098b3979381a3ecf5245021fce9d1c2df46a42e8c.
- loops: SPheno-4.0.5 source LoopFunctions.f90 ; SHA256 8142a813fcc00283d1de2865266be04ff1de25c09422b24b04d57523a6595a24.

The generated full code has not been validated for the four physical cards. Prior source work extracted/verified only a restricted F-only charged box. The old generated program also has an **independently identified scalar proton/neutron exchange** in its conversion rate routine; it must not be adopted without correction.

**Precise next execution:** From these source-locked local Fortran files, extract and separately validate the existing photon K1L/R, low-q2 Z and the complete four-lepton box Wilson groups. Test (1) pure singlet (Crivellin 2021), (2) pure general 2HDM neutral tau (2017 with 2015 asymptotic check), (3) H1/H2 exchange and complex flavor rephasing, (4) UV/scale cancellation and the full common signed basis. For the conversion kernel, keep explicit distinct proton/neutron currents. If a generated block fails, record the concrete numerical incompatibility rather than forcing it into a physical BR. **No new FeynArts installation or general two-loop gauge derivation is justified until this source-driven route has been tried.**

**Gate unchanged:** physical_lfv=UNKNOWN, global_acceptance=null. No new scan, no physical exclusions, no full rates from the present tau-kernel check.
