# Decision: LFV perturbative accuracy for the Type-II Zee charged-cascade phenomenology paper
**8 November 2026 | literature-checked theoretical scope decision; NOT a new LFV exclusion**

**Executive verdict: ADOPT a leading scalar one-loop + leading enhanced photon-Barr–Zee LFV prescription, with selected additionally validated gauge-invariant neutral groups; DO NOT require a complete Zee two-loop gauge-renormalization calculation as a default prerequisite for a scoped phenomenology paper.** This is an **accuracy definition**, not a proof that all omitted two-loop terms are small or that four witnesses are physically allowed. It does **not** authorize a "fully constrained general Zee scan" or solve currently incomplete B, Higgs, vacuum sectors.

**Non-negotiable distinction:** Omitted *two-loop radiative corrections to the same F†F one-loop dipole invariant* are beyond this declared dipole order **unless** they introduce numerically enhanced or new leading structures. But **one-loop four-lepton and semileptonic LFV operators are genuinely leading at that order for mu->3e and mu-e conversion**; they are not made complete by a good mu->eγ dipole. If these observables will be used as hard experimental vetoes or to claim a complete allowed region, their **full relevant leading UV Wilson vectors** and complex interference must be validated separately. There is no source-backed general argument to mark missing conversion or trilepton Wilsons zero.

## A. Primary source evidence, with exact scope

1. **Altmannshofer et al., JHEP 06 (2025) 156 with erratum JHEP 07 (2026) 184**, [arXiv:2410.17313v4](https://arxiv.org/html/2410.17313v4), immediately preceding Eqs. (20) and (53). The authors explicitly include leading two-loop diagrams with Yukawa combinations not already present at one loop and *omit two-loop corrections to Yukawa combinations that already enter one-loop matching*. This establishes a **published leading-enhanced philosophy**, not full fixed-order NLO/NNLO or general-Zee correctness. The model contains **one doublet charged scalar, no antisymmetric Zee singlet F**. Transfer of its one-charged-state EW kinetic group or potential group to the two-eigenstate Zee theory requires genuine gauge-aggregate matching; isolated f8e or HZ/HW substitutions are unjustified. Note the published erratum corrected fermion dipole formulae.
2. **Herrero-García, Ohlsson, Riad, Wirén, JHEP 04 (2017) 130**, [arXiv:1701.05345v2](https://arxiv.org/pdf/1701.05345), Sec. 3.3.2 **Eqs. (3.16)–(3.19)**: two physical mixed charged scalars produce the **one-loop singlet F** mu->eγ dipole; their Eq. (3.19) is explicitly F-bilinear. Their scan includes approximate leading neutral loops and photonic Barr–Zee. Crucially, Sec. 3.3.4 **Eqs. (3.24)–(3.25)** also retains the **off-shell photonic monopole** in mu-e conversion, not just the on-shell dipole. Their quark model in Sec. 2.5 imposes **Y_u2=Y_d2=0**, NOT the project's Type-II quark assignment; some direct mu-e Yukawas are set zero in their scan. The 2017 scan is precedent for scope, not a universal rate backend for our exact cards. PDF source pages and equation labels were independently inspected through web text; screenshots attempted but remote cache returned errors.
3. **Heeck–Thapa, Phys. Lett. B 841 (2023) 137910**, [arXiv:2303.13383v2](https://arxiv.org/pdf/2303.13383), Secs. II–III: assumes **neutral alignment** and **neglects extra-doublet H2 quark Yukawas**. Its Sec. III explicitly neglects Z-exchange, charged-scalar and specified W/charged-scalar bosonic two-loop terms on *those assumptions*, including certain zeroes in alignment. Its Eq. (5), `CR(mu Al->e Al) ≃ 0.0027 BR(mu->e gamma)`, applies to the paper's dipole-dominant approximation and **must not be transferred as an exact Type-II Zee prediction**. It demonstrates that source-qualified *leading LFV phenomenology* is publishable, not that all F-dependent electroweak corrections vanish in the general mixed model.
4. **Bilenky–Santamaria, Nucl. Phys. B 420 (1994) 47**, [arXiv:hep-ph/9310302](https://arxiv.org/abs/hep-ph/9310302), integrates out a **heavy unmixed charged singlet** at one loop and constructs dimension-6 LFV effective operators. This independently motivates operator-level matching rather than only an on-shell dipole. It does **not** supply a mass-unrestricted two-mixed-state Zee result or a bound on its missing two-loop gauge sector.
5. Existing native `module3/core.py::dipole_ledger`, `module4/amplitudes.py` and `research/full_constraints/LFV_COVERAGE.md` implement **one-loop scalar dipoles** (including F†F) and validated selected photon Barr–Zee components; frozen `module14/physics_adapters/lfv_reference_evidence.json` compares the complex photon terms. New `lfv_transfer_2026/zgamma/CONTINUATION_RESULT.json` includes a signed neutral-fermion Zγ subset with 2 author-code controls (maximum residual 3.03e-14) and tiny relative partial-rate shifts 1e-12–1e-14. Corrected `hZ` remains preliminary (author comparison about 3.4e-6 with unmatched numerical inputs and missing limit/chirality falsifiers) and **must not be called independently validated**.
6. Native `research/full_constraints/LFV_SOURCE_TO_CODE_REPORT.md` has independent restricted F-only mixed scalar box and generated rate checks. **Neither proves a complete mu->3e one-loop Wilson vector.** Native FlavorKit conversion's scalar **proton/neutron interchange** is independently documented. No sourced complete semileptonic vector exists for these four cards; keep conversion UNKNOWN.

## B. Precise perturbative-order matrix

| Process/term | Order/structure | Can omit in explicit scoped leading-LFV prescription? | Status and caveats |
|---|---|---|---|
| \(\ell_i\to\ell_j\gamma\): neutral h/H/A one loop, charged H1/H2 D/F one loop | Leading one loop; \(D D^\dagger, F^\dagger F\), and complex neutral Yukawa products, with external mass/chirality terms | **NO**, required at declared leading order | Native Module3 source-validated within massless-neutrino and external-invariant approximations. |
| Neutral top,bottom,charm,tau/photon Barr–Zee, charged-scalar/photon | Potentially chirality- or Yukawa-enhanced leading two-loop terms absent from the LO structures | **NO by default** if potentially competitive; include validated source-matched groups | Native Module4 already includes; avoid double counting. |
| Neutral-fermion Zγ | Additional source-matched two-loop neutral term | **YES if source-quantified negligible on a specified card**; retaining it is easiest | Already numerically validated for four low-texture cards: <1.1e-12 relative change of partial BR. |
| Standalone neutral hZ | Two-loop neutral kinetic source term linear in tiny direct \(D_{e\mu},D_{\mu e}\) | **Potentially**, with verified source/phenomenological suppression | Preliminary corrected hZ partial-rate change ~1e-13 or less, but source-code validation not finalized. |
| Full 2HDM kinetic W/G/ghost and charged-fermion W-H groups | Leading *within 2HDM Yukawa counting*; neutral direct Yukawa appears, charged sector has gauge partners | **Not automatically:** preserve source-defined whole gauge-invariant aggregates; if omitted, state approximation | Small native direct D_eμ can suppress specific neutral-source structures, but Zee charged mixing and F interactions require a separate classification. |
| Mixed physical charged scalar HZ/HW | 2-loop gauge/potential effects with two distinct charged eigenstates and off-diagonal ZH1H2 | **Not automatically; cannot transfer one-state formula naively** | Native unmatched; source HW normalization issue. Quarantine unless coherent validated complete aggregate available. |
| Gauge dressing of existing \(F^\dagger F\) charged scalar/neutrino dipole | Additional EW loop on already-present 1-loop \(F^\dagger F\) dipole, schematically \(C^{(2)}_{FF}\sim C^{(1)}_{FF}g^2/(16\pi^2)\,{\cal K}\) | **YES at explicitly declared leading loop order**, *subject to checking chirality/log/coupling enhancement* | \({\cal K}\) is an **unknown complex model-dependent kernel**; a guessed \({\cal K}=1\) is NOT a physics bound. Original Rξ W/GWW partial UV subgraphs are not a finite coefficient. |
| New \(F D\), mixed charged-current, changed chirality or top-enhanced structures at two loops | Different flavor invariant or chirality suppression possibly bypassed | **NO blanket statement**; must identify whether actual diagram exists and is leading/enhanced at chosen accuracy | Detailed complete source matching not available. Report unresolved, not an assumed \(g^2\) correction to F†F. Do not restart full Rξ tensor calculation unless expert/source audit establishes material leading term. |
| \(\mu\to3e\) neutral tree contact | Tree \(D_{e\mu}\times D_{ee}\) and crossed terms | **NO if claiming complete \(\mu\to3e\)** | Native tree is tested; chosen low textures suppress direct entries. |
| \(\mu\to3e\) one-loop off-shell photon \(K_1\), dipole \(K_2\), Z penguins and boxes | **Leading one-loop** 4-lepton Wilson coefficients, including \(F^\dagger F\) photon anapole and restricted F-only box | **NO if using the whole process for an exclusion/acceptance**; can leave observable unassessed if claiming scoped dipole-only LFV | Rate trace is validated, **source-matched full signed vector is not**. Box F-only source is not the whole Zee box. |
| \(\mu N\to eN\): dipole, off-shell photon monopole, Z penguin, semileptonic scalar and quark operators | Tree + leading one-loop UV matching with Type-II quarks, QCD/nuclear matching | **NO if using conversion as physical veto/allowed-region constraint** | Heeck–Thapa Eq.(5) is restricted; 2017 Eq.(3.25) shows monopole already appears in a Zee study. FlavorKit scalar p/n bug mandates isolated cross-code match. |
| Electroweak/QED higher-order radiative corrections | Loops beyond declared leading accuracy; QED evolution possibly logarithmically enhanced | Can omit with explicit scheme and perturbative uncertainty statement | An unmeasured numerical residual cannot be reported as e.g. 1% or 10% without a calculation. |

**Reviewer-level point:** It is consistent to have a *leading-loop plus selectively enhanced Barr–Zee* result that is not a complete strict two-loop computation. It is **not** consistent to claim a complete \(\mu\to3e\) or conversion limit from an on-shell dipole alone unless separate operator-level suppression has been demonstrated for the specific Zee+Type-II texture.

## C. Numeric evidence from four frozen low-texture Zee cards

Using source-hashed `validation/module12/d12_benchmarks.json` and `research/full_constraints/lfv/TEXTURE_COUPLING_AUDIT.json`, the native **already-included** charged-singlet \(F^\dagger F\) one-loop coefficient is

\[
|C_R^{F,1\ell}| = \frac{|(F^\dagger F)_{e\mu}|}{192\pi^2}
\left[\frac{\sin^2\gamma}{m_{H_1^\pm}^2}+\frac{\cos^2\gamma}{m_{H_2^\pm}^2}\right],
\qquad |C_L^{F,1\ell}|=(m_e/m_\mu)|C_R^{F,1\ell}|.
\]

This follows *exactly at the frozen Module3 approximation* from `H1_F + H2_F`; both heavy states are included. The numerical benchmark limits use the previously pinned MEG-II snapshot \(\mathrm{BR}(\mu\to e\gamma)<1.5\times10^{-13}\), corresponding to the paper's native norm limit \(n_\mathrm{lim}=1.367785824084\times10^{-12}\,\mathrm{GeV}^{-2}\). **The table does not compute any missing amplitude.**

| Exact saved card | \(|(F^\dagger F)_{e\mu}|\) | \(|C_R^{F,1\ell}|\) [GeV⁻²] | \(n_\mathrm{lim}/|C_R^{F,1\ell}|\) | Saved retained total dipole norm [GeV⁻²] |
|---|---:|---:|---:|---:|
| D7 NO, texture_0.0001 | 4.936365e-9 | 2.79250e-17 | **48,981** | 1.39544e-15 |
| D7 IO, texture_0.0001 | 8.577953e-9 | 4.85254e-17 | **28,187** | 3.67986e-15 |
| F13 NO, texture_0.001 | 4.936365e-7 | 6.98064e-16 | **1,959** | 7.09078e-16 |
| F13 IO, texture_0.001 | 8.577953e-7 | 1.21303e-15 | **1,128** | 1.29175e-15 |

**Interpretation:** A correction *only to the existing \(F^\dagger F\) dipole* would need to be **enormously** larger than its one-loop reference contribution to independently reach the coefficient norm corresponding to the current MEG-II limit. A conventional EW loop factor \(g^2/(16\pi^2)\) would point in the opposite direction **if the finite dimensionless kernel is not enhanced**. This is a **naturalness/power-counting screening observation, not a quantitative upper bound**. A distinct leading invariant, hard chirality enhancement or nontrivial cancellation can invalidate naive expectations. The pre-existing sufficient missing-norm budgets \(\sim1.364-1.367\times10^{-12}\) GeV⁻² are geometry, **not** a bound on uncomputed physics.

See `SCOPE_DIAGNOSTICS.json` and `reproduce_scope.py` (read-only source-hashed executable; created as part of this audit and *not run against the user's live checkout in this chat*). The arithmetic was independently evaluated from the saved coupling products and scalar masses in the verified GitHub repository; the reproducer is supplied for local source-replay.

## D. Decision for paper claims, not just calculations

**Supported now:**
- A methods subsection *declaring* scalar one-loop \(\ell\to\ell'\gamma\) amplitudes plus source-matched selected leading photon Barr–Zee and neutral Zγ terms, with the exact scalar mixing, complex phases, source hashes, and known unmatched bosonic groups.
- Conditional/illustrative fixed-card rates with clear labels "within the stated approximation" and **NOT** "allowed by all LFV constraints".
- A scientifically reasonable argument for **not commissioning all two-loop F-gauge corrections**, provided the paper does not promise strict complete two-loop Zee matching or falsely claim their remainders are bounded.

**Not supported now:**
- "Complete LFV constraints imposed" or "LFV PASS" on the four cards; the LO \(\mu\to3e\) and Type-II \(\mu-e\) conversion operators and relative signed matching remain incomplete. Potential new mixed-F enhanced two-loop structures have not been exhaustively classified, although the standard F†F dressing is a beyond-LO correction.
- A "fully constrained allowed parameter-space scan" from those rates. There are independent previously documented B→Xsγ physical-rate uncertainty, Higgs direct-width/search and scalar-vacuum limitations as well.
- Strict experimental 95% CL pass/fail from unknown source/operator components. Incomplete coefficients cannot be set to zero. No new physics benchmark may be called allowed.

**Two viable publication paths:**
1. **Scoped phenomenology paper:** advertise "leading-order leptonic flavor diagnostics and selected enhanced Barr–Zee effects", not "complete all relevant constraints"; show cascade production/widths and *conditional* benchmark scenarios. Do not depict gray "experimentally allowed" regions unless every claimed applicable veto is justified. This is a scientific scope choice, not a prediction of journal acceptance. Peer reviewers might still insist on direct muon-channel coverage for the exact benchmark textures.
2. **Full-constraints scan paper:** before labeling an allowed region, finish at least the leading \(\mu\to3e\) and Type-II conversion operator vectors (or establish source-backed bounds on their rates), and independently close applicable B, Higgs and vacuum constraints. The missing strict F-gauge two-loop calculation is **not the top priority**.

**Prioritized remaining practical work:** (i) one-loop \(\mu\to3e\) full signed vector, including off-shell photon, Z and F/D boxes, with interference; (ii) Type-II semileptonic matching and independently corrected conversion nuclear response; (iii) documented exceptional two-loop mixed-F chirality enhancement test (no full Rξ calculation unless genuinely needed); (iv) B/Higgs/vacuum physics. Existing preliminary hZ can be finalized opportunistically, but the ~1e-13 relative scoped rate effect does not justify holding up the paper.

## E. Final machine-readable/reviewer gate

- `decision=LEADING_SCOPED_LFV_PRESCRIPTION_ACCEPTABLE_AS_AN_EXPLICIT_APPROXIMATION`
- `strict_complete_two_loop_F_gauge_required_by_default=false`
- `physical_LFV_pass_4cards=false / actual_status=UNKNOWN`
- `full_leading_mu3e=false; full_TypeII_conversion=false`
- `global_physical_benchmark_pass=0 established; global_acceptance=null`
- `new_scans_authorized=false`
- `new_missing_amplitude_computed=false`
- `scientific_novelty_or_journal_acceptance_not_assessed=true`

## Primary links and document restrictions

- [Altmannshofer et al. 2025/2026](https://arxiv.org/html/2410.17313v4), discussion immediately before Eqs. (20) and (53), and JHEP07(2026)184 erratum.
- [Herrero-García et al. 2017](https://arxiv.org/abs/1701.05345), Secs. 2.5, 3.3.1–3.3.4, Eqs. (3.16)–(3.19), (3.24)–(3.25).
- [Heeck–Thapa 2023](https://arxiv.org/abs/2303.13383), Sec. II–III, Eq. (5), alignment and quark Yukawa assumptions.
- [Bilenky–Santamaria 1994](https://arxiv.org/abs/hep-ph/9310302), heavy charged-singlet one-loop EFT; **not** general mixed Zee matching.
- Repo evidence: `LFV_COVERAGE.md`, `LFV_TEXTURE_MATERIALITY_RESULT.md`, `lfv_transfer_2026/zgamma/CONTINUATION_REPORT.md`, `lfv_transfer_2026/HZ_EQ59_PRELIMINARY_NUMERICAL_2026-11-08.md`, `module3/core.py`, and `lfv/TEXTURE_COUPLING_AUDIT.json`.

No existing completed physics source files, four-card signed amplitude ledgers, global constraint statuses, Zγ tests, original frozen modules or user-local uncommitted integrated work were changed. This decision is **a theoretical scope assessment**, not a physical LFV result or paper author approval.
