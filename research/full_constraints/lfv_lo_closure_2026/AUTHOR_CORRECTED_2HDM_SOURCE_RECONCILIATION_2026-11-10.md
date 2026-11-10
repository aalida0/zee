# Exact uploaded general-2HDM corrected-source reconciliation — 10 November 2026

**SOURCE EXECUTED, PRIOR PDF-v4 NEUTRAL BARR-ZEE NUMBERS SUPERSEDED; FULL PHYSICAL ZEE LFV UNKNOWN.**

The user uploaded the authors' actual general-2hdm-pheno files. The source-locked thdm.py has SHA256 **9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193**. This hash identifies the uploaded bytes, **not a verifiable upstream Git commit**: the files did not include Git metadata, so equivalence to GitLab commit b5035cd5 has not been proved.

The unmodified source cR_llpg, cL_llpg and Gamma_l_to_lp_gamma(2,1) have been executed on all four exact frozen Zee lepton-Yukawa cards. Type-II neutral mapping: rho_l = D/sqrt(2) (RH-row/LH-column), theta12=beta-alpha, theta13=theta23=0, CP-odd q2(A)=i. Quark input was corrected to the author's internally running MSbar masses evaluated at mt: diagonal rho_u=m_u(mt)/v*cot(beta), rho_d=-m_d(mt)/v*tan(beta). The 2HDM control uses alphaQED=1/129, sw2=0.23129, and an explicitly artificial MHp=650 GeV, Z3=Z7=0. The artificial 2HDM charged mass is NOT a physical Zee charged spectrum. The original source gamma rate agrees with independent assembly from original cR,cL for each card.

| Card | Pure 2HDM reference BR(mu->e gamma), synthetic MHp 650 | Corrected-author neutral-fermion BZ norm K2 [GeV^-2] | Charged-fermion doublet-weighted diagnostic norm K2 [GeV^-2] |
|---|---:|---:|---:|
| D7 NO | 1.635588261e-19 | 2.498861516e-25 | 1.277457915e-25 |
| D7 IO | 1.125301901e-18 | 2.091561381e-25 | 1.069239642e-25 |
| F13 NO | 9.772163274e-23 | 1.143077485e-27 | 5.672273437e-28 |
| F13 IO | 6.704858588e-22 | 2.950494923e-27 | 1.464118924e-27 |

The **neutral** terms are extracted from the exact corrected author's original th/ch/bh/tauh terms, not hand-copied PDF equations. These norm values exceed the previously reported v4-source approximations by factors **2.45483, 2.45485, 4.50402, 4.50404**, respectively. Mark the older PDF-v4 report and JSON as SUPERSEDED. The charged column evaluates the authors' charged t/charm/tau expressions at the two actual Zee charged masses weighted by doublet fraction squared. It omits singlet F, mixed gauge/seagulls and off-diagonal ZH1H2, and is **not a validated complete or independently gauge-invariant Zee two-loop amplitude**.

The sum of these two restricted subset norms divided by the **full native F+D Zee one-loop dipole norm** is **2.706e-10, 8.589e-11, 2.412e-12, 3.418e-12**. Their suppression is demonstrated. **No upper bound on omitted Zee-specific two-loop contributions** follows.

**Important signed matching correction:** in the dominant complex dipole, the proper original native SARAH doublet-only K2L agrees with **+cR_author/(8 pi^2 v^2)**, NOT with the previously used overall minus. Relative residuals are 6.569e-4, 6.517e-4, 3.826e-5 and 3.780e-5; wrong sign gives ~200%. This affects coherent amplitude addition, not standalone BZ norms. The subleading chirality is less accurately matched because of external-mass approximations.

Setting rho_l12=rho_l21=0 exactly makes every two-loop term in the **modelled pure 2HDM single-direct-external-LFV class** zero, as tested using the original authors' methods. It does not suppress Zee charged-singlet F/neutrino/W diagrams and multi-flavor tau-chain corrections.

**Source-input warnings:** uploaded example.py incorrectly assigns electron mass 511e-5 = 0.00511 GeV (10 times actual); the bridge uses 0.00051099895 GeV. The uploaded rge.py/adm.py implement CP-odd EDM operator evolution, not the full LFV mu-e conversion LEFT.

Reproducibility: 18 focused source-locked tests PASS in a clean archive replay. Complete independently executable scripts, four card inputs, old numeric snapshots, native SARAH OA2 references, original method coefficients and SHA receipt are in the conversation ZIP **zee_corrected_general2hdm_vs_zee_lfv_2026-11-10.zip**, excluding original uploaded author code.

**Final physics gate:** FULL_ZEE_TWOLOOP=UNKNOWN; PHYSICAL_LFV=UNKNOWN; global_acceptance=null. No physical four-card acceptance or large scan authorized solely by these restricted source results. Finite-q2 mu3e, scalar renormalization and complete heavy/gluon/nuclear conversion still await a physical error budget.
