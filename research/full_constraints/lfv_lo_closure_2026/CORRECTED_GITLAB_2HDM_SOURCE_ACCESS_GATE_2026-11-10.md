# Current general-2hdm-pheno source verification gate — 10 November 2026

**Status: UPSTREAM_CORRECTED_CODE_IDENTIFIED; EXACT_SOURCE_NOT_FETCHABLE_IN_ASSISTANT_RUNTIME; PHYSICAL_ZEE_LFV_UNKNOWN.**

The requested [jbrod/general-2hdm-pheno GitLab](https://gitlab.com/jbrod/general-2hdm-pheno/) site is live and advertises **master latest commit b5035cd5**, title **Corrected further errors in l -> l' gamma Wilson coefficients**. The published [erratum JHEP07(2026)184](https://doi.org/10.1007/JHEP07(2026)184) appeared 21 July 2026. This GitLab commit is the correct priority for source-level validation, NOT older PDF-derived expressions assumed to be identical.

The repository README confirms thdm.py exposes general 2HDM one-/two-loop radiative decay prediction Gamma_l_to_lp_gamma and inputs theta12/13/23, rhou/rhod/rhol 3x3 complex matrices (absolute values/phases), neutral Mh1/2/3, charged MHp, and charged scalar potential Z3/Z7. **GitLab raw thdm.py was not retrievable** from the available assistant runtime (web cache failures and container DNS denied). No thdm.py API was imported, and it is not true that the existing v4 scripts were checked against author b5035cd5. Do not promote them to source-locked corrected-code status.

Independently executed an eight-test frozen-card Zee-to-2HDM *neutral input* bridge. All eight tests pass. The valid mapping is rho_l = D/sqrt(2) in the original RH-row LH-column convention; theta12=beta-alpha, theta13=theta23=0; neutral h/H/A masses identical to frozen Zee; Type-II rho_u=(m_u/v)cot beta, rho_d=-(m_d/v)tan beta (illustrative quark masses only). Tests cover neutral h/H/A native vertex complex equality, Type-II quark sign and diagonality, CP mixing and explicit no-fake-charged-Higgs guards.

**Fundamental limit:** full 2HDM authors' code has one doublet charged Higgs MHp and couplings Z3/Z7. Zee has two mixed charged masses, singlet F Yukawas, non-diagonal ZH1H2 vertex and singlet-gauge completion. No unique physical map of MHp/Z3/Z7 exists. Source tests explicitly reject treating a synthetic MHp as a Zee full two-loop calculation.

The user-facing reproducibility archive **zee_gitlab_corrected_source_reconciliation_2026-11-10.zip** (attached in chat) contains:
- four frozen cards and matched source input dictionaries, with MHp/Z3/Z7 omitted;
- independently executed eight-test suite;
- a GitLab API downloader pinned to the visible correction commit b5035cd5, saves SHA-256 receipt (NOT executed here);
- documented version/physics limits.

The prior arXiv-v4 two-loop scripts' own **17 regression tests PASS locally**, which is independent from and does not replace a comparison with GitLab corrected b5035cd5. All previously published v4-based two-loop numbers are **provisional pending source revision check**.

Next exact dependency: obtain b5035cd5 thdm.py bytes on a network-connected machine and run precise source-level comparison against the frozen data; then separately assess genuine Zee mixed charged/gauge two-loop flavor structures. Physical_lfv=UNKNOWN, global_acceptance=null; no new scans or exclusions.