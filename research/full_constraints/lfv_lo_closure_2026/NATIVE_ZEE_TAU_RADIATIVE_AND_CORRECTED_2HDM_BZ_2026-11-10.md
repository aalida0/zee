# Native Zee tau radiative LFV + corrected 2HDM Barr-Zee audit (10 November 2026)

**NEW IMPORTANT PHYSICS RESULT: TAU LFV TWO-LOOP NEUTRAL BARR-ZEE CAN DOMINATE ONE-LOOP. FULL ZEE LFV STILL UNKNOWN.**

## Original generated source

Compiled the original SHA256-locked SARAH 4.15.4 generated.f90, couplings.f90, loops.f90, preserving the original CalculateGamma2l source and PV-integral functions. For all four exact D7/F13 NO/IO cards ran **mu->e gamma, tau->e gamma, tau->mu gamma** in full/F-only/D-only/zero Yukawa modes. Correct native flavor argument order: **CalculateGamma2l(gt1=final,gt2=initial,gt3=final)**, hence (1,2,1), (1,3,1), (2,3,2). All complex source full = F-only + D-only and zero-mode checks PASS. The F-only coefficient for **all 12 channels** independently matches (F-dagger F)[final,initial] times (sin(gamma)^2/mH1^2+cos(gamma)^2/mH2^2)/(192 pi^2).

| Card | Zee one-loop Br(mu->e gamma) | Zee one-loop Br(tau->e gamma) | Zee one-loop Br(tau->mu gamma) |
|---|---:|---:|---:|
| D7 NO | 1.6722518e-19 | 7.9599381e-18 | 3.2561793e-15 |
| D7 IO | 1.1628990e-18 | 4.7490062e-17 | 3.7326202e-15 |
| F13 NO | 4.3178556e-20 | 3.4837938e-21 | 6.2154815e-20 |
| F13 IO | 1.4329654e-19 | 5.9122984e-21 | 7.3465839e-20 |

These are native *one-loop approximation* diagnostics with alphaMZ=1/127.95 and physical parent lifetimes, neutrino masses zero. The earlier mu-only source rates differ around 0.44% due to the muon total width/input convention. Do not interpret differences as a physical discrepancy.

## Current authors' corrected 2HDM two-loop original source

The uploaded source-lock thdm.py SHA256 **9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193** was executed via its own Gamma_l_to_lp_gamma(3,1) and (3,2), with Type-II quarks matched to the source running masses and the exact neutral Yukawa bridge rho_l=D/sqrt(2). For the **pure 2HDM reference only** we used a synthetic charged MHp=650 GeV and Z3=Z7=0.

| Card | Full pure-2HDM reference Br(tau->e gamma) | Full pure-2HDM reference Br(tau->mu gamma) |
|---|---:|---:|
| D7 NO | 1.0316e-13 | 4.1495e-11 |
| D7 IO | 6.1510e-13 | 4.7613e-11 |
| F13 NO | 1.4584e-17 | 5.8678e-15 |
| F13 IO | 8.6959e-17 | 6.7331e-15 |

The **neutral-fermion-only** Barr-Zee amplitude norm extracted from the corrected authors' original th/ch/bh/tauh source terms is **~75 times** the pure-2HDM tau one-loop amplitude norm for D7 and **~202 times** for F13. The complete pure-2HDM two-loop correction norm is ~113× (D7), ~315× (F13). This is why the earlier finding of negligible neutral BZ in mu->e gamma **MUST NOT BE GENERALIZED TO TAU**: the exact direct tau-flavor neutral Yukawas are not numerical texture zeros.

## Coherent partial Zee one-loop + gauge-invariant neutral-fermion Barr-Zee

The original native Zee **full F+D one-loop dipole** is combined coherently with just the corrected 2HDM **neutral-fermion** BZ term using the doublet-only signed dipole bridge (+c/(8 pi² v²)). Results are **partial source diagnostics, not complete Zee two-loop rates**:

| Card | Partial Zee Br(tau->e gamma) | Partial Zee Br(tau->mu gamma) |
|---|---:|---:|
| D7 NO | 4.5486e-14 | 1.8300e-11 |
| D7 IO | 2.7122e-13 | 2.0998e-11 |
| F13 NO | 5.8386e-18 | 2.4385e-15 |
| F13 IO | 3.5582e-17 | 2.7979e-15 |

The native D-only dipole agrees with the author's leading doublet-only dominant-chirality K2 to ~0.06% for tau->e and **5-7% for tau->mu**, reflecting neglected external muon mass terms in the 2HDM formula; thus the coherent addition is **NOT precision physical acceptance**.

Comparison bounds for scale only: Belle 2021 90% CL Br(tau->mu gamma)<4.2e-8 and Br(tau->e gamma)<5.6e-8; BABAR 2010 Br(tau->e gamma)<3.3e-8. Belle II arXiv:2608.23009 reports 9.5e-8 for tau->mu gamma, weaker than Belle. The partial results are below these bounds but **no physical LFV pass follows because mixed Zee two-loop terms are missing**.

## Reproduction and gate

Attached ZIP **zee_tau_radiative_zee_vs_corrected_2hdm_2026-11-10.zip** provides source compile/replay code, matched four-card inputs, 48 original source output channels, 4×3 corrected authors' source references, partial coherent results, 14 passing focused tests and SHA-256 manifest. It excludes original generated Fortran and downloaded author thdm.py; user has supplied them separately. All 14 tests PASS in clean archive.

**Gate:** ORIGINAL_SARAH_MU_TAU_ONELOOP_COMPLETE; CORRECTED_NEUTRAL_FERMION_BZ_TAU_MATERIAL; PURE_2HDM_FULL_TAU_NOT_FULL_ZEE; PHYSICAL_LFV=UNKNOWN; GLOBAL_ACCEPTANCE=null. Missing gauge-complete F/W/Z/H1/H2 two loops, finite-q2 mu3e, tau->3l, and heavy/gluon coherent conversion.
