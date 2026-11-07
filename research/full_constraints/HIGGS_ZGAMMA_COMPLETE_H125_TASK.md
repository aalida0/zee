# Next calculation — release source-independent complete h125→Zγ one-loop width on D7/F13

**Research branch:** `research/zee-full-constraints`
**Starting commit:** `45a9d11e89d0ba2f796a1d7fd3dd545e344f3644`.
**Aim:** Turn the independently Ward-validated unequal-mass CP-even charged scalar `h→Zγ` kernel into a **complete physical leading-one-loop h125 partial width** with correct interference against SM W and native complex diagonal fermions. Stop after the fixed-card h125 observable is validated or an exact incompatibility is shown. **Do NOT extend to H or A in this task**: heavy absorptive thresholds and A's CP tensors require a separately scoped calculation.

## Why now, and what is already known

Read `research/full_constraints/HIGGS_ZGAMMA_2021_RESCUE.md`,
`HIGGS_TAUTAU_MATERIALITY.md`,
`LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md`,
`higgs/ZGAMMA_SOURCE_EVIDENCE.json`, `higgs/ZGAMMA_SOURCE_MANIFEST.json`,
`higgs/diphoton.py`, `higgs/neutral_widths.py`,
`HIGGS_COVERAGE.md`, original native SARAH physical D7/F13 cards and saved h→γγ amplitude.

- Frozen model `Z=(e/(s_wc_w))(P/2-s_w² I)`, `G_ij` native.
- Hue18 Eq16/Appendix A and independently executed LoopTools 2.13, integrals and scalar Ward test identify unique **photon-adjacent equal-mass propagator routing** in common PV convention:
  `C0(t,0,s,b,a,a)` and `C0(t,0,s,a,b,b)` for the two orientations, not literal `C0(t,0,s,a,a,b)` etc in Flo21 D.20.
- Literal Flo21 routing yields mixed-scalar disagreements 0.232% D7 and 0.0388% F13; corrected candidate yields UV and scalar Ward residuals at ~1e-14, independent native tensor checks. This is a **validated scalar sector within its real subthreshold domain**, not yet a physical total width.
- 2019 Thành et al. has prior Zee off-diagonal mixed loop but does not specify all PV arguments. Do not demand verbatim equality to an ambiguous printed D.20 once independent direct Feynman integral, Ward identity, regulator cancellation and proper limits have established the physical scalar-loop routing. Acknowledge source discrepancy prominently and, if useful, prepare a concise author clarification request without delaying independent calculation.
- In Flo21 D.19 and D.21 printed dimensions of `tau` / width prefactor appear inconsistent; derive physical normalization from the transverse tensor, not a typo.

## Only required actual calculation

1. **Promote only the scalar `hZγ` kernel** from `zgamma_source_audit.py` into a separate research calculator **with source/physics provenance and strict mass domain**. Preserve triangle + AZ seagull current, both unequal-mass orientations, exact native h trilinear signs, stable real-subthreshold integration and photon Ward tensor identity. No silent fitting.
2. Independently implement/execute **h125 W and charged fermion loops**, with native Type-II quark couplings and **general complex diagonal** lepton Yukawas. Include properly normalized CP-even and CP-odd loop form factors; off-diagonal flavor lepton single-insertion loop vanishes for flavor-diagonal gauge currents, but document that. Bind native signed couplings and identical `alpha, e, v, MW, MZ, m_f` prescriptions. Test both left- and right-chiral `Zff` factors, charges, color, `g_V`, (\gamma_5) signs, and physical thresholds.
3. Fix **relative complex phase and sign between W, fermion and scalar contributions**, not only independent scalar kernel. Verify complete SM width with standard published SM `h→Zγ` reference or an independently executed reference code under **identical electroweak inputs and perturbative order**, then one charged-scalar 2HDM/decoupling control. Prove CP-even/odd non-interference for unpolarized width. Compare any alternate expression only after mapping its tensor convention.
4. Execute D7/F13 physical `Γ(h→Zγ)` and common-input SM `Γ_SM(h→Zγ)`; report `Γ/Γ_SM`, absolute GeV, normalized complex W/fermion/scalar components, CP-odd part if any, per-source hash and numerical error. **No claim of HiggsSignals physical likelihood** until other h125 widths, total BR and measurement inputs are qualified.
5. Explicit domain check: h125 is below charged scalar and W thresholds on these cards; the scalar subthreshold PV calculation is applicable. If a sector is above threshold (e.g. internal light fermions) use its complete physical absorptive result or a justified suppression/error bound, never discard `Im` by taking real parts. Use correct alpha scheme and cross-check sensitivity to alpha(0) as a *scheme comparison*, not a guessed sigma.

## Validation/stop

- Independent SM check plus public 2HDM limit, photon Ward + UV cancellation, conjugate orientation, equal-mass, zero mixing, source hash, CP-chirality and signed interference tests. Include a falsification test that shows swapping the PV mass routing breaks the scalar Ward tensor relation; don't make this a source authority contest.
- Deliver `research/full_constraints/HIGGS_ZGAMMA_COMPLETE_H125.md` with actual source/SM benchmark and fixed D7/F13 results, `higgs/zgamma.py` and tests plus source-hashed `higgs/ZGAMMA_H125_EVIDENCE.json` only if genuinely calculated.
- If the independent SM benchmark or W/fermion relative tensor normalization cannot be established, return `H125_ZGAMMA_BLOCKED` with exact mismatch, **not** a partial width.
- Preserve B `B_FULL_RATE_BLOCKED`, LFV `LFV_FULL_COVERAGE_BLOCKED`, Higgs global `HIGGS_FULL_COVERAGE_BLOCKED`, vacuum UNKNOWN. Update existing progress/readiness only if a declared milestone actually passes. Do not restart neutral `H/A→γγ`, SusHi, HDECAY, Flo21 literal audit or 2019 survey.
- The ATLAS ττ study remains `HIGGS_SCOPED_SEARCH_BLOCKED`; its central tree-level tau numerator is tiny, but no physically certified bound exists. Do not attempt that likelihood in this task or normalize partial widths as totals.
- No new model points, pilot/full scans, HTCondor, MG5 campaigns, modification to frozen Modules0–13, old D14 scanner or acceptance statuses. Commit/push research-only valid evidence.

**Success is one verified physical h125 `Zγ` partial width at two existing cards.** Not another 100 tests without numerical SM model normalization, and not a global full Higgs exclusion.
