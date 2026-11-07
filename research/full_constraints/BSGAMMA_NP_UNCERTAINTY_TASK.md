# B→Xsγ final physics gate — NLO uncertainty, one-state confidence and two-state coverage

**Working branch:** `research/zee-full-constraints`.
**Starting result:** `e2202f1466ce35c83d64e42cffff09847486c19d`.
**Prior achievement:** HEPfit built/executed 37 fixed-card/control runs, coherent eight-operator real top-only NLO matching passed; D7/F13 HEPfit and frozen SuperIso central rates differ by 1.12/1.29% in different physical prescriptions. The original one-state NNLO table can be interpolated but its nuisance/prescription are NOT directly the NLO Zee likelihood.

**Your task is to attempt the NEXT MISSING PHYSICS GATE, not revisit matching and not create another literature-only audit.**

## Target, explicit outcome and timebox

Can the executed HEPfit NLO two-charged-state branching ratio be given a **scientifically source-justified NP-dependent uncertainty and physical experimental comparison**, at a clearly stated *NLO NP matching* accuracy?

The user wants complete LFV/B/Higgs constraints before one final big scan. Do not run any Zee parameter scan or even pilot random points. Use only **D7, F13**, the two exact existing scalar spectra/families, source-validated **published SM / one-charged Type-II reference controls** and analytic matching endpoints. Focused numerical HEPfit runs needed to evaluate actual nuisance/scale responses on these fixed cards are permitted; **no new Zee physics points**.

Read `research/full_constraints/bsgamma_hepfit/HEPFIT_RATE_REPORT.md`,
`execution/HEPFIT_EXECUTION.json`,
`FEASIBILITY_GATE.md`, `BSGAMMA_COVERAGE.md`, `SOURCE_MANIFEST.json` and
`PROGRESS_TO_FINAL_SCAN.md`. Use the **already compiled pinned HEPfit**
driver/client and pinned SuperIso only for controlled independent checks.
Do not rebuild unless the executable is genuinely absent; if absent,
use the committed exact REPRODUCE.md recipe, not new source installations.

## Gate 1 — Real nuisance/scale propagation (not a guessed sigma)

1. Inventory HEPfit's *actual source-implemented* correlated semileptonic,
   heavy-quark kinetic/mass/CKM inputs and `BLNPcorr`, with the
   historical fit covariance and Eγ cut source. Distinguish:
   (a) input/parametric priors; (b) scale/truncation variations;
   (c) resolved photons/HQE/nonperturbative; (d) model-specific
   missing terms (primed, light-quark, EW and possible additional
   charged-scalar operators). Some HEPfit parameters are correlated;
   do NOT sample them independently if covariance is known.
2. Vary `μ0`, `μb`, `μc` according to an explicitly cited
   prescription, and run at least SM + D7 + F13 for each
   scientifically meaningful control (a finite, predeclared variation
   matrix; **no parameter-space scan**). Independently vary the
   documented nuclear/semileptonic/HQE correlated inputs if an
   actual covariance is available. Log each execution stdout and
   full input and digest. Do not infer statistical sigma from
   the 120/200 GeV matching-scale envelope.
3. Decompose `ΔBR = BR(SM+two-state NP)-BR(SM)` **within the same
   HEPfit normalization** for each systematic variation. This
   separates nuisance effects on SM baseline from NP response
   without fitting intercepts or changing the calculation.
4. For source-backed resolved photon uncertainties, inspect the
   explicit Wilson/power dependence in the HEPfit N(E0) path and
   relevant literature. A single `BLNPcorr*P0` may be a defined
   nuisance, but it does not prove the full C4/C7/C8 covariance.
   Document which NP-dependent nonlocal effects remain outside it.
5. Provide parameter/nuisance sensitivity matrices and separate
   signed shifts for fixed cards. **No quadrature combination
   without justified correlations and scale prescription.**

## Gate 2 — Independently qualify the one-state likelihood

1. Reproduce an explicit published **Type-II one-charged-state**
   95% CL exclusion under its own complete theory+experimental
   setup. Available anchors:
   - Misiak et al. 2015: `arXiv:1503.01789`, SM (3.36±0.23)×10^-4,
     published Type-II limit 480 GeV within its prescription.
   - Misiak–Steinhauser 2017: `arXiv:1702.04571`, explicitly
     disaggregated NNLO nonperturbative/parametric/HO/charm-interpolation
     errors; compare confidence prescriptions, don't copy sigma.
   - Misiak et al. 2026: `arXiv:2608.29863`, SM (3.54±0.14)×10^-4,
     Type-II 670 GeV bound with *new* perturbative inputs and 2026
     linear NP Eq.(4) in its stated domain.
2. The **HEPfit one-state NNLO lookup table** has a separate 7%
   uncertainty, and the NLO direct kernel differs by ~3.9% at
   the prior one-state anchors. A likelihood using the NNLO
   table is NOT a validation of the NLO two-state uncertainty.
   Explicitly reproduce a historical reference if possible and
   explain what can/cannot transfer by perturbative order.
3. Use the actual observed B→Xsγ limit/measurement dataset,
   Eγ=1.6 GeV and confidence construction. Do not label a
   Gaussian pull automatically as a one-sided physical
   95% CL exclusion without its prescription.
4. If one-state reproduction only works in the published NNLO
   table prescription, record that honestly and stop promotion
   of NLO two-state constraints.

## Gate 3 — Accuracy/materiality and pass/fail status

1. Quantify which missing operator contributions could be
   competitive in the **two existing points** (u/c, finite strange
   mass, primed, down-Yukawa, additional Zee EW/charged-lepton
   effects and threshold logs). Use justified source power
   counting, analytic bounds or controlled existing-card
   evaluations; don't assert they vanish just from a model name.
2. Determine whether total theoretical+experimental confidence
   treatment is supportable across a **declared domain** in
   (mH1,mH2,gamma,tanβ). Two cards validate only their
   neighborhood; no generic all-parameter exclusions without
   certified domain and uncertainty.
3. If **all** the matched-rate, NP-dependent uncertainties,
   missing-operator materiality, and statistical one-state
   checks pass, implement **opt-in** explicit model-aware
   physical `B_PHYSICAL_VALIDATED_PASS/FAIL` on existing
   cards with exact validation source IDs and no global
   acceptance yet (LFV/Higgs still blocked). A fail-closed
   adapter must reject unsupported spectra.
4. Otherwise return `B_FULL_RATE_BLOCKED`,
   `physical_bsgamma=UNKNOWN`, `exclusion=null`,
   `theory_sigma=null` unless individual partial nuisance
   components genuinely measured; those can be reported
   separately **without** a fabricated total.
5. If the remaining nonperturbative/Wilson-response covariance
   cannot be obtained from published sources or existing public
   source, end this line of solo code work and produce an **exact
   specialist question**: which Wilson-dependent covariance/
   remainder/precision response at Eγ>1.6 GeV is needed,
   with order, operator basis, scale and two-state matching.
   Do not start a two-loop/NNLO derivation or another month-long
   C++ backend reimplementation.

## Deliverables

- `research/full_constraints/bsgamma_hepfit/UNCERTAINTY_REPORT.md`
- `.../UNCERTAINTY_RUNS.json`, raw hashed execution receipts;
  `.../UNCERTAINTY_COMPONENTS.json` (component status and source,
  **no invented full sigma**)
- `.../ONE_STATE_CONFIDENCE.md` with explicit calculation and
  reproduced or not-reproduced reference
- `.../specialist_question.md` only if unavoidable; a concise
  reproducible request, not a vague appeal for help.
- Focused unit/physics tests, hash/source checks,
  `git diff --check`. Keep previously pinned source immutable.
- Update `research/full_constraints/BSGAMMA_COVERAGE.md`,
  `VALIDATION_MATRIX.json`, `PROGRESS_TO_FINAL_SCAN.md` and
  readiness only for **actually passed** milestones.

**No new random model points, mass scans, HTCondor, MG5 production,
LFV/Higgs source re-audits or final large scan.** The frozen
`feature/zee-d14-conditional-cascade-scan` and Modules0–13
must not change. Commit/push only validated research results.

**Stop successfully even if `B_FULL_RATE_BLOCKED` remains**, when
the exact irreducible physics uncertainty and the needed expert
input have been established. Do not claim a fully constrained scan
from a central BR and a borrowed SM sigma.
