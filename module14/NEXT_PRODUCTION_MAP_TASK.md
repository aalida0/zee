# D14D — Complete the 16-point collider-rate map and 14 TeV projection pilot

**Branch:** `feature/zee-d14-conditional-cascade-scan`.
**Baseline:** commit `111b54423bce0ba820b7efad7000348ca9bd9f6e`.
**Scope:** bounded per-point production + conditional collider rates. DO NOT reopen completed D14C audits, the 20k/225 collector, vacuum searches, or precision B→Xsγ work.

## Current verified physics facts

- The 225-point AF dataset is COMPLETE. Among the 33 D10 sufficient-vacuum PASS scalar points, **16** are also nominally compatible with the published 2026 **LO-NP linear** B→Xsγ screening. This is NOT full physical B acceptance. Incomplete LFV/HiggsTools and missing correlated NP uncertainty prevent a globally allowed label.
- The 16 original point IDs, in ascending H2 mass, are:
  `15591, 8850, 4611, 2264, 14984, 9454, 3693, 15673, 14555, 14074, 13345, 8294, 16385, 14187, 2616, 11016`.
- At 13 TeV the first real, SHA-bound MG5 3.6.7 LO 5FS
  `pp→tH2⁻ + tbar H2⁺` integrations are:
  `15591: 0.011868 pb`, `2264: 0.0050014 pb`,
  `15673: 0.0029876 pb`.
  Their `sigma*BR(H2→H1 Z)` ranges are
  `0.003869369–0.003869743 pb`,
  `0.001843759–0.001843805 pb`,
  `0.001176377–0.001176477 pb`.
  See `module14/conditional_scan/CANDIDATE_FOLLOWUP.md`
  and `candidate_followup.json`.
- Three of the six nominally flavor-compatible **sub-TeV H2** points had bounded vacuum searches with no conclusive witness and **remain UNKNOWN**. No more generic multi-start attempts unless a new mathematically sufficient certificate exists.

## A — Preserve existing source and full cards

1. Reuse original immutable 225 scalar/Yukawa records, recorded source hashes,
   exact real SARAH Zee UFO and D5/D6 production machinery. Obtain full source
   data from the existing on-host assets/AF SHA-pinned archive, not invented
   partial scalar cards.
2. Preserve the three D14C 13 TeV integrations as fixed provenance data.
   Only use actual real data and reconstruct/verify the exact signed tbH2
   couplings and independent amplitude normalization for any *new*
   scalar family; their external quark coupling is shared among the four
   neutrino families but the output contract must bind each family.
3. Preserve 13 TeV LO 5FS, both charges and both beam orders, PDF
   NNPDF30_lo_as_0130, fixed `muR=muF=mH2`, stable hard external
   H2/top, and D4 frozen Yukawa-running conventions for direct comparison.
   The above D14C cards are the definitive reference for mapping/defaults,
   not a template to edit only H2 mass.
4. All generator/native results, integration statistics, cards, logs,
   compiled code manifests and SHA receipts remain in ignored `local/`.
   Do NOT vendor external binaries. Capture and validate all native
   artifacts independently before calling a rate verified.

## B — Run only a *finite* 13 TeV production completion

1. Run real one-scalar-level LO 5FS MG5 integrations for the **remaining 13**
   among the 16 (or a smaller clearly reported subset if computation/runtime
   blocks completion). Use a fixed production recipe that is reproducible
   and parameter-card/map tested. No arbitrary mass interpolation to fill holes.
2. For each, calculate `sigma*BR(H2→H1Z)` **per family** from existing
   verified complete D4 tree two-body totals. Preserve H1 decay BRs
   separately; do not treat the cascade partial width as a BR.
3. Report generator integration error, relevant decay-card provenance,
   total H2 width, energy, PDF, perturbative order, and a separate null
   field for unmeasured scale/PDF/decay theory uncertainty. Order the
   16 rates by actual `sigma*BR`, NOT by BR alone, and retain the
   13 TeV energy label.
4. On resource failure, stop with executable *manual* AF commands for
   remaining IDs and show `NOT_EVALUATED`, not fake cross sections.

## C — HL-LHC-relevant 14 TeV **actual** pilot

The previous 13 TeV computation cannot be relabelled 14 TeV. For a
14 TeV projection, rerun actual partonic production with 7000+7000 GeV
beams and an explicit PDF/alpha_s/scale scheme.

1. Execute 14 TeV versions for **15591, 2264, 15673** only,
   with all other model, order, charge definition and PDF choices
   identical to their corresponding 13 TeV cards. If one or more
   cannot run, do not infer missing 14 TeV rates using a guessed
   energy factor.
2. Verify process/card consistency and report the three
   `sigma(14)/sigma(13)` **measured** ratios, with numerical
   integration uncertainties. A 14 TeV ratio is **process and
   spectrum specific**, not automatically a universal reweighting
   of all other candidates.
3. Optional bounded seven-point LO scale-sensitivity pilot for
   `15591` at **14 TeV** if resources allow; retain frozen Yukawas
   when varying scales (state any scheme alternative separately).
   The scale envelope is NOT a fully calibrated perturbative or PDF
   confidence interval.
4. Source and label a specific PDG Z branching fraction only if a
   genuinely needed illustrative leptonic final-state yield is
   calculated; do not silently pick (Z→\ell\ell) branching fractions.

## D — Paper-oriented conditional tables and plots

1. Produce auditable tables and a few useful labeled plots: `mH2`
   versus validated `sigma*BR` for the 16 at 13 TeV;
   `sigma` versus `mH2` (with tanbeta and gamma indicated);
   a `(mH1,mH2)` conditional scatter showing vacuum PASS versus
   UNKNOWN, *nominal* B status, and no globally allowed claims;
   the actual three 13-vs-14 TeV production comparisons.
2. For **14 TeV only**, optional truth-level raw `sigma*BR*L`
   at a clearly specified scenario luminosity (e.g. 3 ab⁻¹),
   without acceptance, decay-chain BR or background. Never
   call this an experimental sensitivity, exclusion or discovery
   projection. Later detector/parton-level cuts and backgrounds
   are a separate analysis.
3. Include the six sub-TeV vacuum UNKNOWN points as clearly
   annotated *unresolved opportunities*; they are not approved
   benchmark selections. No arbitrary vacuum score promotion.
4. Distinguish in every output: scalar vacuum-sufficient PASS,
   approximate published LO B diagnostic, partial LFV,
   HiggsTools incompleteness, theory-error limitations,
   truth-level tree decays and missing full detector constraints.
   `global_acceptance` must remain `null`.

## E — Deliverables, audit and stop

- Commit new code/results only under
  `module14/conditional_scan/` and focused tests under
  `tests/test_module14_conditional_*.py`. Do not modify
  Modules 0–13, original Module14 workers, the historical
  dataset or the existing production receipts.
- Create `module14/conditional_scan/PRODUCTION_MAP_REPORT.md`
  and `production_map_13_14.json`, with separate per-family
  tables and hashes. Include plotting scripts and static
  plot outputs only if genuine data was produced.
- Evaluate technical completion gates:
  `PRODUCTION_MAP_13TEV_COMPLETE` only if actual 13 TeV
  results for all 16 have been executed and validated;
  `PRODUCTION_MAP_PARTIAL` if any is unavailable;
  `PRODUCTION_14TEV_PILOT_COMPLETE` separately if all three
  real 14 TeV checks pass.
- Check source/input binding, independent amplitudes, closure,
  duplicate charges/beam orders, generator output origin,
  missing-data handling, deterministic data export, and
  `git diff --check`. Commit and push clean tests.
- Do not launch any broad scan or Condor batch automatically.
  Do not fabricate rate systematics, a full flavor 95% CL,
  globally viable benchmarks or experimental sensitivity.

**Important:** The user's objective remains a **publishable
constraint+charged-cascade phenomenology study**. This task supplies
collider-rate evidence; it does not certify missing full LFV,
modern B→Xsγ NP theory errors, or global vacuum status for the other
192 points.
