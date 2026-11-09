
# Compiled native Zee FlavorKit one-loop groups — 9 November 2026

**Verdict: RAW ONE-LOOP SOURCE GROUPS EXECUTED; PHYSICAL LFV UNKNOWN.**

Exact user-uploaded generated Fortran verified SHA-256:
- generated: 2d30006d8d4759b2b7bfe76e2e4795bd2cf2f19ef5cb5772390ed3155b1bc41d
- couplings: a0de851498f3e68e7421538098b3979381a3ecf5245021fce9d1c2df46a42e8c
- loops: 8142a813fcc00283d1de2865266be04ff1de25c09422b24b04d57523a6595a24

The original SARAH-generated source groups were compiled and executed on all four **exact, full F/D, D7/F13 NO/IO low-joint cards**. The executable scripts, original source-derived drivers, complex Wilson-group results and 9 passing regression tests are supplied in the separately attached user ZIP, **zee_lfv_full_source_operator_progress_2026-11-09.zip**. No new scan, new cards, collider work or physical exclusions were performed.

## Source group results and controls

- Photon monopole: original CalculateGamma2l (17 generic structures), full gauge/scalar OA1 projection at q²=0, matches separately computed full scalar-only K1 to max 2.5e-16 relative. The on-shell dipole OA2 group was not extracted or re-run in this specific audit; earlier Module 3/4 results remain a separate subset.
- Neutral h/H/A photon: original MonopoleSFF for internal e/mu/tau; tau-only reproduces the published 2017 Zee limit; electron/muon source contributions negligible at q²=0 for THESE textures, **not a bound on finite virtual-photon q²**.
- Z-penguin direct CalculatePengV4L (46 structures) and crossed CalculatePengV4Lcross (92 structures): both executed with correct original SPheno B1 finite mass ordering; coefficients stable when renormalization Q varies mZ to 1 TeV to max 1.03e-11 relative. Cross/direct relation: source VLL/VRR cross = 2x direct, VLR/VRL cross = direct, all four complex cards. Do not naively sum: ordered-action and Fierz map is not established.
- Four-lepton boxes CalculateBox4L and CalculateBox4Lcross: all original 31+52 generic structures run with physical charged/neutral scalar, F/D, W/Goldstone native vertices, original loop kernels. Source-level outputs are NOT a proof of a fully matched physical 3e action.
- Scalar-penguin direct and crossed CalculatePengS4L groups: original 84+168 generic diagrams executed with original native scalar trilinears reconstructed from frozen potential parameters (the Gate6 physical inversion). Their raw coefficients have **20% to 194% Q-scale sensitivity for some chiral structures**, so they are NOT certified physical Wilsons.
- The native electron, up-quark and down-quark Z gauge couplings were compiled, and direct electron spectator factorization verified at ~1e-12 across four complex cards. That provides a semileptonic Z-current **subset**, NOT all Type-II quark operators.

**Crucial basis correction:** The original charged rotation includes beta:
G=(cos beta,sin beta,0),
H1=(-sin beta cos gamma, cos beta cos gamma, sin gamma),
H2=(sin beta sin gamma, -cos beta sin gamma, cos gamma).
Using a Higgs-basis ZP together with the original Ye/Ye2 changes D/F mixing and is invalid. After correction the original native charged photon F/D source agrees with independent amplitudes to <7e-16.

## Numerical source hierarchy — coefficients GeV^-2

| Card | abs(e² K1L), q²=0 | abs(direct Z VLL) | Z / e² K1L | abs(direct box VLL) |
| --- | ---: | ---: | ---: | ---: |
| D7 NO | 1.27322e-17 | 1.89047e-18 | 0.1485 | 2.49401e-25 |
| D7 IO | 2.36501e-17 | 3.28767e-18 | 0.1390 | 1.04046e-24 |
| F13 NO | 4.27090e-17 | 2.83441e-16 | 6.637 | 6.42154e-22 |
| F13 IO | 7.42177e-17 | 4.92537e-16 | 6.636 | 2.85276e-21 |

These are separate **source-coefficient magnitude diagnostics**, not coherent amplitudes or rates. In particular the non-negligible Z group means the previous charged-photon-only rate cannot be used to claim F13 passes LFV.

## Remaining physical blockers — must not fabricate zeros

1. Common signed ordered amplitude and complete identical-electron crossing/Fierz/interference, including neutral scalar tree, photon monopole at finite q² and dipoles. q²=0 is not a full physical 3e virtual photon prediction for internal e/mu.
2. Scalar source group Q dependence: check counterterms and scheme, or establish a defensible quantitative error/omission condition.
3. Aluminium: full Type-II semileptonic scalar/vector up/down source groups, quark boxes, heavy-quark/gluon thresholds, running and source-matched photon/Z/dipole signs. Original FlavorKit nuclear scalar proton/neutron contraction has a known swap and must use the corrected nuclear adapter.
4. Complete radiative LFV has separate potentially material gauge/mixed electroweak two-loop groups; no missing-amplitude error envelope yet.

The user-uploaded original source files remain private; only this report is pushed. The separate ZIP holds scripts and result data for independent reproduction, not a public GitHub copy of generated Fortran.

**Final: LFV_LEADING_SCOPE_INCOMPLETE, physical_lfv=UNKNOWN, physical_mu3e_BR=null, physical_Al_conversion=null, global_acceptance=null.**


## Additional conversion numerical subset

Using only the original four-lepton-source-factorized LFV Z current, the original generated up/down Z spectator vertices, and separately validated Al-27 p/n vector overlaps (Vp=0.0159, Vn=0.0169, capture 4.64079e-19 GeV), the *Z-only* vector quadratic diagnostics are: D7 NO 3.18900e-25, D7 IO 9.78301e-25, F13 NO 6.84994e-21, F13 IO 2.06842e-20. They are **not physical conversion rates, upper bounds, lower bounds or exclusions**. The direct original generated semileptonic 2L2q and box groups, source-matched photon/Z/dipole interference, scale evolution and nuclear uncertainty are absent. The executable Python and per-card complex p/n current results are provided with the private audit ZIP.
