# Source-transferred neutral-fermion two-loop LFV in Zee Type II

**10 November 2026. Verdict: neutral h/H/A fermion-loop gamma/Z Barr–Zee subset evaluated and negligible for four frozen D7/F13 textures. Complete physical LFV remains UNKNOWN.**

## Source and strict validity

The independently implemented calculation follows Altmannshofer *et al.*, arXiv:2410.17313 **v4** (2026-05-01), Eqs. (22)–(23) and (54)–(55), using neutral internal fermions t,c,b,tau and both photon and Z gauge exchange. The source article's JHEP 07 (2026) 184 erratum and later corrected GitLab code have **not** been independently source-by-source checked here, so this is a **v4 source-formula implementation**, not a certified exact copy of latest code. Heeck–Thapa 2023, arXiv:2303.13383, neglects Type-II extra-doublet quark couplings and some bosonic two-loop diagrams in the alignment limit; its approximations cannot establish full Zee charged/gauge LFV.

Exact input four cards: validation/module12/d12_benchmarks.json (D7 NO/IO, F13 NO/IO). Zee native D uses RH-row/LH-column; 2HDM rho_l=D/sqrt(2); Type-II rho_u=(m_u/v)cot beta, rho_d=-(m_d/v)tan beta. Mixing h=(cos(delta),-sin(delta)), H=(sin(delta),cos(delta)), A=(0,i), delta=beta-alpha. Charged singlet does not enter this *separately gauge-invariant* neutral-fermion Barr–Zee subset.

The published two-loop functions are integrated via exact Feynman-parameter representations:

f1(z)=integral_0^1 dx log[x(1-x)/z]/[x(1-x)-z],
f2(z)=(1-2z)f1(z)+2(2+log z),
f3(z,y)=y[f1(z)-f1(y)]/(z-y),
f4(z,y)=y[f2(z)-f2(y)]/(z-y).

The source c_R maps to the original SARAH K2L, source c_L to original K2R, each K2=-c/(8 pi^2 v^2). **This was checked independently** by implementing the source Eq. (51)–(52) one-loop leading 2HDM dipoles and comparing with the native Zee D-only K2: dominant complex relative mismatch D7 NO/IO 6.57e-4/6.52e-4 and F13 NO/IO 3.83e-5/3.78e-5; subleading chirality <0.007 (source approximation neglects small external-mass terms).

## Quantitative result

| Card | ||K2^(neutral fermion BZ)|| [GeV^-2] | Ratio to original native full one-loop ||K2|| | max |Delta Mnu| on projecting D_e_mu=D_mu_e=0 [eV] |
|---|---:|---:|---:|
| D7 NO | 2.5068074e-25 | 1.7964291e-10 | 5.783e-18 |
| D7 IO | 2.0982122e-25 | 5.7018838e-11 | 3.067e-18 |
| F13 NO | 1.1520187e-27 | 1.6246711e-12 | 2.226e-18 |
| F13 IO | 2.9735740e-27 | 2.3019763e-12 | 5.674e-18 |

Top-quark contribution dominates; c,b,tau photon/Z loops were included. Coherent one-loop plus this one specific two-loop subset modifies the source radiative branching ratio by <4e-10 **relative** in each card. These extremely small numbers originate from direct e-mu Yukawa entries at floating-point near-zero level (roughly 1e-19 to 1e-20). Projecting just those two entries to exact zero leaves the original Zee neutrino mass matrix unchanged to <6e-18 eV and makes every calculated 2HDM single-direct-LFV-insertion neutral fermion term vanish. **The projection is a numerical test, not proof that exact zeros are RGE-stable or that these are globally allowed points.**

A fixed-background direct-Yukawa sensitivity study finds sufficient 2loop-only amplitude stress scales of ~8.1e-7 (D7) and ~5.6e-6 (F13) for equal direct e-mu entries; these are **not** scan exclusions because the perturbation changes the neutrino solution and the one-loop amplitude. They show the negligible two-loop conclusion is **texture-specific**.

## Reproducibility and fail-closed scope

Original independently executed Python integrals and complex coefficient calculation, the exact native one-loop source benchmarks, one-loop chiral convention verification, data receipt, source-rephase/texture controls, sensitivity test, and 9 passing Python unittest checks are in conversation archive **zee_lfv_neutral_barr_zee_two_loop_2026-11-10.zip**. The archive intentionally does not redistribute original generated private Fortran. No large scan was run.

**Still missing for full physical LFV:** mixed Zee charged H1/H2–W/gauge two-loop sets and gauge completion, potentially relevant two-loop dressing of tau-chain DD^dagger/F^dagger F tensors, full correction/erratum cross-check, finite-q2 mu3e photon, scalar penguin renormalization, and complete heavy-quark/gluon matching plus RG/nuclear conversion. No numerical upper bound on those missing amplitudes was demonstrated.

**Gate:** NEUTRAL_2HDM_FERMION_BZ_SOURCE_V4_RESTRICTED=EVALUATED; FULL_ZEE_TWOLOOP=UNKNOWN; PHYSICAL_LFV=UNKNOWN; GLOBAL_ACCEPTANCE=null.
