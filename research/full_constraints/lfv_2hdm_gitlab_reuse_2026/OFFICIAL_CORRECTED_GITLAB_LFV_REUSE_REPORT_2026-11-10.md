# Corrected official general-2HDM LFV source: reproducible Zee input audit

**10 November 2026 — Actual corrected public GitLab code executed. FULL PHYSICAL ZEE LFV UNKNOWN.**

## Pinned sources, exact execution

- GitLab https://gitlab.com/jbrod/general-2hdm-pheno; pinned commit **b5035cd58d2a7e4a91e9790d045df062b97adffe**.
- Upstream thdm.py SHA-256: **9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193**.
- Paper Altmannshofer et al JHEP 06 (2025) 156, arXiv:2410.17313 and July 2026 erratum JHEP 07 (2026) 184.
- Verified GitHub CI run https://github.com/aalida0/zee/actions/runs/42787820408 (actual full corrected upstream, exact four original D7/F13 cards).
- All four original source input witnesses from validation/module12/d12_benchmarks.json (SHA-256 f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8).

## Exact neutral and Yukawa mapping, strictly pure-2HDM

The native Zee D matrix has right-handed row and left-handed column indices; the source-basis mapping is rho_l = D/sqrt(2), rho_u = diag(m_u,m_c,m_t)*cot(beta)/v, rho_d = -diag(m_d,m_s,m_b)*tan(beta)/v, theta12=beta-alpha, theta13=theta23=0. The neutral h/H/A couplings are identical in the mapped CP-conserving neutral 2HDM sector.

The official program has **one physical charged Higgs** and no F charged singlet. Consequently we compare three pure-2HDM **proxy** masses: bare charged doublet mass sqrt(mH1²cos²gamma+mH2²sin²gamma), physical mH1, physical mH2. None is the full mixed Zee charged scalar sector and these runs are NOT complete Zee branching ratios.

The first GitLab attempt failed because the corrected constructor requires ms_at_2GeV, md_at_2GeV and mu_at_2GeV. The corrected workflow supplies them and now passes.

## Corrected complete 2HDM source results (bare charged doublet proxy)

| Frozen card | Total corrected pure 2HDM BR(mu->e gamma) | 2loop / 1loop complex Wilson norm | Corrected neutral fermion Barr-Zee K2 norm GeV^-2 |
| --- | ---: | ---: | ---: |
| D7 NO | 1.6490056762278941e-19 | 3.0633344252513026e-10 | 2.67333021797623e-25 |
| D7 IO | 1.1345340136323594e-18 | 9.775188996936673e-11 | 2.2375926915338525e-25 |
| F13 NO | 9.852361237326081e-23 | 4.909469569063358e-11 | 1.2184380311032559e-27 |
| F13 IO | 6.759884350426034e-22 | 4.837871204104953e-11 | 3.145014462671516e-27 |

The one-loop, neutral-fermion, charged-fermion, neutral-bosonic, and charged-bosonic COMPLEX coefficient groups were extracted from the original upstream cR_llpg / cL_llpg source **in memory only**. Their coherent sum matches the unchanged public methods to <1e-12 relative for all four cards. Complex results and original source SHA are preserved at OFFICIAL_CORRECTED_GITLAB_COMPLEX_WILSON_GROUPS_2026-11-10.json. The official program's complete dipole rate for a single 2HDM charged state agrees with native Zee D-only one-loop calculations to about 0.13% for D7 and 0.008% for F13; input schemes and one-loop approximations differ, so those differences are NOT pure two-loop effects.

**Correction:** prior v4 hand-transcribed neutral-fermion Barr-Zee values (D7 NO 1.018e-25 and IO 8.520e-26, F13 NO 2.538e-28 and IO 6.551e-28) are superseded by the directly executed pinned corrected code for pure 2HDM. Do not retain or combine the obsolete coefficients.

## Exact corrected upstream texture selection check

Set only the direct neutral flavor-changing rhol(1,2)=rhol(2,1)=0 while retaining all other Yukawas and masses. **Every one of the four published 2HDM two-loop source groups is exactly zero, for cR and cL on all four cards.** The one-loop tau-mediated two-Yukawa transitions survive. This is a verified selection rule specific to the published pure-2HDM topology, not a bound on unseen Zee charged-singlet/gauge two-loop diagrams or a proof that exact texture zeros are RGE stable.

## Processwise conditional, not physical, headroom

With native Zee one-loop rate diagnostics, the triangle inequality gives BR_full <= (1+kappa)^2 BR_source **IF AND ONLY IF** the omitted complete process-amplitude norm has separately been demonstrated <= kappa times its source norm in the same scheme. The strict-source rates and current 90% CL limits imply maximum assumed missing amplitude ratios:

| Card | mu->e gamma | mu->3e | Au conversion |
| --- | ---: | ---: | ---: |
| D7 NO | 948.2 | 30312 | 31646 |
| D7 IO | 358.9 | 11524 | 12403 |
| F13 NO | 1867 | 46900 | 10501 |
| F13 IO | 1024.4 | 26196 | 6034 |

The conditional demonstration with kappa=300 passes all 12 one-loop-source limits. **No calculation has established kappa<=300 for the omitted Zee diagrams**; therefore this is a sensitivity result only, not physical global LFV acceptance or a source-backed precision uncertainty. The conditional script and seven fail-closed tests are in this directory.

## Unresolved physical work

Genuinely Zee-specific charged singlet F / mixed charged-gauge two-loop LFV, finite-q² three-body photon corrections, scalar-penguin scheme, modern heavy-quark/gluon/QED-QCD and nuclear conversion matching. Complete full-model B/Higgs/vacuum constraints are likewise beyond the scope of this audit.

**Verdict: corrected public 2HDM results VALIDATED for the mapped pure-2HDM control; full Zee physical LFV=UNKNOWN and global_acceptance=null.**
