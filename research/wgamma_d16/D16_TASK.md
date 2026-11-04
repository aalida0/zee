# D16 — Gauge-complete Wγ two-loop dipole matching: Codex execution specification

**New branch:** `research/zee-d16-wgamma-gauge-matching`  
**Starting immutable code:** D15 `ONE_LOOP_COMPLEX_DIPOLE_PASS` at `f6676356a95517f2820dea79298a938cc8786968`.

## Objective

Derive, independently validate and—**only after complete gauge checks**—implement the two-loop neutral-scalar/Wγ contribution to the off-diagonal `l_i -> l_j gamma` dipoles in the frozen CP-conserving ZeeTypeII model. Preserve the D15 one-loop and Module4 signed convention. In the *same isolated research branch*, investigate the gauge/Goldstone/ghost/pinch completion until there is either a reproducible gauge-independent LFV result or a precise minimal technical blocker.

**Do not** claim `COMPLETE_ZEE_LFV_PASS`: this work addresses one previously missing electroweak class. Additional Zγ, WZ, mixed charged/W, non-dipole three-body, mu-e conversion, and other two-loop contributions remain outside scope unless explicitly validated.

## Read first

- `module4/MATCHING_AUDIT.md`: W discrepancy; sections 5–6 are central.
- `module4/CONVENTIONS.md`: frozen `C_L,C_R`, native scalar/Yukawa conventions and deliberately excluded W candidates.
- `module4/CHARGED_SCALAR_AUDIT.md`: examples of complete scalar-QED Ward/seagull tests; **do not** confuse those loops with Wγ.
- `research/spheno_flavorkit/CROSSING_BRIDGE.md`: D15 proved `K2L/R=-conj(C_L/R)` in matched normalization; do not reopen it.
- `module3/CONVENTIONS.md` and `validation/module0/CONVENTIONS.md`: h/H/A LFV vertices, gauge and Goldstone rules.
- The pinned primary sources in `module4/MATCHING_AUDIT.md`, especially Abe–Hisano–Kitahara–Tobioka, arXiv:1311.4704 **with its 2016 erratum**; Chang–Hou–Keung hep-ph/9302267; Ilisie arXiv:1502.04199; Davidson arXiv:1601.01949.
- The general Zee 2017 analysis arXiv:1701.05345 as a coverage cross-check, not a substitute for our full LFV calculation.

## Why current formulas cannot be chosen by fit

The existing audit records three distinct candidate W effective kernels:

```
K_CHK    = 3 f + 23 g/4 + 3 h/4 + (f-g)/(2z)
K_Ilisie = 15 f/2 + 2 g + (f-g)/(2z)
K_Abe    = 3 f + 5 g + (f-g)/(2z)
```

The differences are mass-dependent and trace to missing or differently treated off-shell structures, not arbitrary normalization constants. Existing audit verifies the P-pinch cancellation, but **B, C tensor reductions, all R_xi diagrams and their external-line projection are NOT established**. Do not choose a kernel by numerical agreement, a preferred reference, or assuming all other tensor terms vanish.

## Deliverables and execution gates

### Gate A — exhaustive diagram/assumption inventory

1. State the precise amplitude class and working approximation: neutral h/H/A to WW (where applicable), LFV external leptonic vertex, external-mass treatment, and all diagrams required for a gauge-invariant observable. Include W, charged Goldstone, ghosts where applicable, mixed vertices, seagulls and pinch/non-Barr–Zee attachments.
2. Derive a table of diagrams with charge, field, source vertex, gauge parameter dependence, symmetry factors, relative signs, Goldstone mixing/neutral scalar sum rules and included/omitted status. Distinguish genuine physical zero and not implemented. Use SARAH native vertices, not copied 2HDM couplings.
3. Identify which terms are specific to Zee charged-singlet/doublet mixing or general LFV Yukawas and which reduce to ordinary 2HDM formulae. Prove any cancellation or reduction needed to reuse a 2HDM expression.

### Gate B — independent source tensor and full Ward identity

4. Build independent signed off-shell hγγ, hγZ or specifically hγγ* W-loop tensor contributions *as needed for the targeted LFV Wγ class*. Retain transverse and non-transverse tensor structures (A,P,B,C of Abe audit) before projection. Show actual W+Goldstone+ghost+pinch contributions to each component rather than using published final kernels alone.
5. Verify electromagnetic Ward identities at arbitrary relevant off-shell virtual photon momentum and both photon directions where applicable; evaluate before/after pinch terms. Demonstrate R_xi parameter cancellation (for ≥3 separated ξ values, including ξ=1 and a nontrivial ξ) in the **complete projected physical LFV amplitude** within numerically justified tolerances. A check solely on the inner vertex or a R_xi=1 number is insufficient.
6. Derive explicitly how the B and C off-shell structures reduce or cancel when attached to both outer lepton-line photon orderings and neutral-scalar propagators. Include external spinors, q momentum, mass insertions and neutral sum rules. If the cancellation requires diagrams absent from the stated class, include them or mark a precise blocked scope; do not set terms to zero without derivation.

### Gate C — physical dipole matching and reference arbitration

7. Project complete amplitude to the **frozen D12/Module4 operator** `L=e*m_i/2 * bar(l_j) sigma(C_L PL+C_R PR) l_i F + h.c.`. Use the D15 crossing conventions; compute both complex chiralities, CP-even/odd couplings, reverse ordered amplitudes, and coherent sign relative to validated one-loop + fermion/photon + physical charged-scalar/photon components.
8. Independently reproduce diagonal limiting magnetic moments using correctly signed external scalar/pseudoscalar couplings. Compare kernel values and analytic differences to CHK/Ilisie/Abe as **conditional reference checks**, explaining which assumptions/terms each formula contains. Include Abe 2016 erratum. Do not fit constants or phase.
9. Test Ward, gauge parameter, rephasing, neutral-scalar alignment/sum rules, decoupling and physical nulls. Include generic complex LFV Yukawas with nonzero L and R, not only a simplified 2HDM flavor texture. Use nonzero, nondegenerate scalar masses and independent numerical points.

### Gate D — implementation/integration boundary

10. Implement only within `research/wgamma_d16/`; place bulky symbolic notebooks, generated code and logs in ignored local scratch. Do **not** modify Modules 0–14 or frozen SARAH files. Use existing pinned Mathematica/SARAH/FeynArts/FormCalc user-space infrastructure where it demonstrably helps; otherwise independent Python/Fortran is fine.
11. Produce a minimal reproducible numeric interface returning `C_L, C_R`, contributing tensors, gauge residuals, reference/kernel differences, approximation and provenance, **but only label VALIDATION_PASS if Gates A–C close**.
12. Tests must explicitly fail if an omitted nonzero topology is silently treated as zero, an R_xi dependence remains above tolerance, or a required gauge/pinch graph is unavailable. Distinguish `PASS`, `FAIL`, `BLOCKED_GAUGE_MATCHING`, `NOT_EVALUATED`, and `NOT_APPLICABLE`.
13. Commit the complete diagram inventory, signed derivation and independent benchmark tests under `research/wgamma_d16/`. Supply a top-level scoped status report with evidence; do not add this amplitude to the global coherent LFV ledger or D14 until validated.

## Efficient approach / avoid busywork

- **Start with Gate A** and a tiny symbolic test of P/B/C projected contributions and the neutral-scalar sum rule already in `module4/MATCHING_AUDIT.md`. Then determine the minimal necessary gauge/pinch set. Avoid regenerating 44 PreSARAH photon coefficients; D15 already closed that.
- Once a gauge-independent W subset is demonstrated at one nontrivial complex point, expand to multiple points and independent source comparisons. Do not run a large scan.
- If a tensor identity fails, inspect actual graph/vertex signs, orientation, missing diagrams and source errata; do not hide it by picking `K_CHK`, `K_Ilisie`, or `K_Abe` arbitrarily.
- If a genuine blocker remains, report **the specific missing diagram or source identity and a runnable minimal failing case**; prioritize its technical resolution, not another general status overview.
- Only a fully gauge-invariant and signed calculation can establish `WGAMMA_GAUGE_MATCHING_PASS`; otherwise preserve explicit UNKNOWN status and explain what physical constraints still cannot be claimed.

## Commit/branch

Continue exclusively on `research/zee-d16-wgamma-gauge-matching`. Freeze `research/zee-spheno-dipole-conventions` at the D15 validated milestone. Never merge to D14 or main before independent acceptance.
