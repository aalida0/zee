# Source-first literature audit for Zee full physical constraints — 7 Nov 2026

**Purpose:** Correct the prior false claim that the unequal-mass charged-scalar Zgamma calculation is absent in published literature. This is a source/reference recovery index, NOT a statement that full LFV/B/Higgs exclusions are solved. Frozen original modules and scanner branch remain untouched.

## Evidence and completeness declaration

- Fresh **75 relevant-paper semantic graph search**, plus Babu et al. (2020) recovered separately through direct citations; **23 full-text focused reviews**, with directed outgoing/incoming screens for key 2001/2005/2017/2021/2022/2023/2025/2026 sources.
- Semantic citation queries are NOT exhaustive reverse-citation lists, and **not every reference of every paper has been read**. The previous October novelty audit extracted 356 numbered bibliography entries across four focal publications, with duplicates. Do not claim all 356 inspected.
- Detailed two-way graph and full-text evidence: Undermind workspace `5c874c15-c3c8-4ebd-b96f-9fcd953e4ce8`, search `/Zee model two-hop formulas software and exclusion closure November 2026`.
- Before claiming any loop, vacuum equation, theory uncertainty or acceptance is 'not available in public sources', inspect full text **and its relevant citations/citers**, record paper DOI, equations, model assumptions, and public reference implementation; don't confuse 'not directly ready to use' with 'not published'.

## HIGH-PRIORITY missed or underused formulas — verify at frozen D7/F13

1. **Florentino/Romão/Silva EPJC 81 (2021) 1148**, doi:10.1140/epjc/s10052-021-09956-2, **Appendix D.3 Eq(D.20)**: mixed unequal-mass `h→Zgamma` charged-scalar loops with off-diagonal `Z H1 H2`; Apps B/C/E charged vertices, B→Xsγ matching and scalar unitarity. It computes h (light CP-even); H needs coupling/kinematics transformation and A needs distinct CP analysis. **Apparent printed dimensional errors in Eq(D.19) tau definition and Eq(D.21) prefactor** require independent normalization, not blind copying.
2. **Hue et al. EPJC 78 (2018) 885**, doi:10.1140/epjc/s10052-018-6349-0 **Eq(16)**: general unequal-mass charged-scalar PV form factor with precise internal-mass ordering; independent check vs Flo21. Eq(4) amplitude/physical width with m_phi³, App A PV. This is a generic CP-even scalar formula, not an automatic complete A→Zgamma.
3. **Bilenky/Santamaria NPB 420 (1994) 47**, doi:10.1016/0550-3213(94)90375-1 **Eqs(4.8–4.17),(4.20–4.21),Sec6**: gauge-invariant one-loop EFT for an unmixed charged scalar singlet: `F†F` penguins, dipoles, 4l boxes, and semileptonic operators. Valuable F-sector limit, not whole mixed Zee at two loops.
4. **Mitsuda/Sasaki PLB 516 (2001) 47**, doi:10.1016/S0370-2693(01)00842-5 **Eq(16), Eqs(26–28)**: two-mixed-charged-state `F^4` box coefficient for `mu→3e`. Its restricted lepton texture and incoherent rate assumption do not transfer; operator coefficient can be independently checked.
5. **Ghosal/Koide/Fusaoka PRD 64 (2001) 053012**, doi:10.1103/PhysRevD.64.053012 **Eqs(4.1–4.7)**: summed mixed-charged-state lepton-flavor Z penguin at **q²=mZ²**, singlet `F†F` structure. Not full off-shell mu-e conversion.
6. **Khasianevich et al. CPC (2024) 109244**, doi:10.1016/j.cpc.2024.109244: **FlexibleSUSY NPointFunctions** tree+one-loop `li→3lj`, mu-e conversion (Al/Au), l→l gamma one-loop, photon/Z/scalar penguin and boxes. Public `https://github.com/FlexibleSUSY/FlexibleSUSY`. Independent potentially powerful check of FlavorKit ~6.97% gold conversion scalar-isovector source discrepancy. It does NOT offer full two-loop Zee Barr-Zee, nor validated Zee cards.
7. **Primulando/Julio/Uttayarat EPJC 82 (2022) 253**, doi:10.1140/epjc/s10052-022-10189-0 **Eqs(35–43)**: restricted family-Z2 model top two-loop LFV and `mu→e` scalar/vector/photon conversion. Use as nuclear-operator reference, not generic Zee loop result.
8. **Crivellin et al. JHEP05(2017)117**, doi:10.1007/JHEP05(2017)117 **Sec2,3,4/AppA**: all needed low-energy mu-e EFT operators, QED/QCD RG, nuclear matching after full Zee matching.
9. **Barroso/Ferreira PRD 72 (2005) 075010**, doi:10.1103/PhysRevD.72.075010 **Eq(23)**: Zee cubic permits charge-breaking minima below neutral minima (ordinary 2HDM non-CB theorem invalid).
10. **Babu/Dev/Jana/Thapa JHEP03(2020)006**, doi:10.1007/JHEP03(2020)006 **Eq(4.24–4.25)**: gauge-fixed 5-VEV Zee CB minimization; useful witness-search coordinates, not exhaustive global proof.
11. **Lopes/Milagre/Silva 2025/26**, doi:10.1142/S0217751X26501265, **BounDS** `https://github.com/andremilagre/BounDS`: generic tree unitary scattering 2-doublet+1-charged-singlet (not vacuum solver).
12. **FlexibleDecay** doi:10.1016/j.cpc.2022.108584: generic loop scalar widths and CP-odd epsilon tensor for A→VV and Zgamma, if a supported custom Zee FlexibleSUSY model generates right vertices. NO automatic offshell charged-W multibody closure.
13. **Hermann/Misiak/Steinhauser JHEP11(2012)036**, doi:10.1007/JHEP11(2012)036: NNLO charged-Higgs matching expansions and published Mathematica companion; neither historical one-state bound nor code addresses arbitrary Wilson-dependent resolved-photon covariance in two-state Zee.
14. **Schmidt/Vandeleur JHEP06(2026)006**, doi:10.1007/JHEP06(2026)006: Zee→2HDM EFT matching/RG; warns **never add full one-loop neutrino amplitude and corresponding EFT-running contribution**.

## Directed citation relationships actually screened

- `Bilenky/Santamaria 1994 → Mitsuda/Sasaki 2001; Herrero-García et al. 2017`; separate `Ghosal et al. 2001 → He/Majee 2012 → Herrero-García 2017 → Heeck/Thapa 2023`.
- `Barroso/Ferreira 2005 → Florentino/Romão/Silva 2021` and `Babu et al. 2020`.
- `Fontes/Romão/Silva 2014 2HDM hZgamma → Florentino/Romão/Silva 2021 Zee mixed hZgamma`; independent `Hue et al. 2018 general unequal-scalar hZgamma`.
- `Borzumati/Greub 1998 NLO → Hermann/Misiak/Steinhauser 2012 NNLO → Misiak/Steinhauser 2017 → Florentino et al. 2021`; `Benzke et al. 2010 → resolved photon uncertainty`.
- `FlexibleDecay → Khasianevich et al. 2024 one-loop CLFV → Kotlarski/Voigt 2026 HiggsTools interface`.
- All outgoing/incoming edges are **selected**, not full network census; many later citing papers deal with *Zee–Babu*, scotogenic-Zee, 3HDM or restricted 2HDM not our exact field content.

## Model transfer discipline

The target's quark sector is Type II but its leptonic Yukawas are **general complex**, with antisymmetric singlet F and two charged mass eigenstates. Papers assuming alignment, small F, leptophilic quark sector, one charged boson, decoupling or a family-specific texture cannot be imported as complete Zee exclusions. Validate chiral phases, signed mixing, both charged states, and interference at coefficient level before comparisons. A computed leading amplitude does not prove total width or likelihood, and any missing physical mandatory cut is `UNKNOWN`.

**Do not rerun a global parameter scan**; focused evaluations on original D7/F13 and other saved cards are allowed as validation only. This audit changes NO existing physical status: `B_FULL_RATE_BLOCKED`, `LFV_FULL_COVERAGE_BLOCKED`, `HIGGS_FULL_COVERAGE_BLOCKED`.

## Correct next source-first comparison

- Flo21 EqD20 **versus** Hue18 Eq16 (including printed typos check), at h original D7/F13, then CP-even H and separately CP-odd A.
- Bil93 singlet EFT **versus** native one-loop F sector; Mit01b box and Gho01 on-shell mixed Z form factors **versus** one-loop generated diagrams; optionally independent FlexibleSUSY NPointFunctions 3l/conversion operator response to pinned FlavorKit.
- No absent full two-loop Zee W/Goldstone/ghost gauge class was located as a ready-to-run general-model package in the inspected papers. Mark this literature finding provisional given incomplete graph coverage, not as proof nonexistence.
