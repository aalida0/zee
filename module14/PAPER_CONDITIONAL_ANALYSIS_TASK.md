# D14E — Paper-oriented conditional scan and cascade phenomenology

**Branch:** `feature/zee-d14-conditional-cascade-scan`.
**Starting physics/evidence commit:** `26bdcf33db91c4f1f2ffc3868841d7cb947c3c96`.
**Scope:** turn existing validated scan + real production evidence into a scientifically defensible paper-oriented *conditional* phenomenology analysis and a final manual AF scan plan. No new precision-flavor framework or detector study.

## Why this is the next task

D14D already completed:
- Fully validated 16-point **13 TeV** LO 5FS associated-H2 production map.
- Three **actual 14 TeV** runs for IDs 15591, 2264, 15673.
- SHA-pinned, independent MG/native/ALOHA/decay validation.
- Preserved unresolved constraints: modern physical B→Xsγ UNKNOWN, partial LFV, incomplete HiggsTools, 192 vacuum UNKNOWN, missing scale/PDF/decay theory uncertainty.

**Do not rerun or 'improve' those 19 integrations merely to add more tests.**
Read `module14/conditional_scan/PRODUCTION_MAP_REPORT.md` and
`production_map_13_14.json`, the complete 225-point summary and
`module14/D14A_INTEGRATED_SCAN_AUDIT.md`. Existing 20k and 225 AF
collections are COMPLETE, so do not recollect them again.

## A — Scientific audit and paper skeleton (first)

1. State the precise restricted Zee Type-II parameterization, scanned ranges,
   scalar, EWPO, neutrino, vacuum certificate, *partial* LFV, HiggsTools
   and linearized B→Xsγ coverage. Do not use "fully constrained" or
   "globally viable" if any required observable is UNKNOWN.
2. Make a table of what the prior 2017 **general Zee constraints** and
   2021 **H2±→H1±Z cascade** papers already establish. Pin actual
   references/claims and identify **which of our results are additional**,
   e.g. a reproducible multi-constraint conditional scan + model-matched
   13/14 TeV production for explicit spectra. Do not claim novelty without
   source-qualified comparison. Avoid a deep unrelated literature search.
3. Explain the actual proposal-dependent 20k→225→33 vacuum-certificate PASS
   and 77 nominal flavor-compatible, with **16 in the intersection**;
   none of the 16 has mH2<1 TeV in this finite sample. All statuses must
   be named accurately. A 95%-style *reference pull* is NOT a
   95% CL exclusion or a valid global likelihood.
4. Provide a paper-ready outline and *exact list of figures/tables*
   supported by existing evidence, explicitly distinguishing actual
   findings from needed validation. Suggested figures:
   - original sample's 2D charged mass scatter with vacuum and
     approximate B diagnostics (both legend and caption conditional);
   - branching fraction vs mixing/mass for selected spectra;
   - source-validated 13 TeV sigma×tree BR vs mH2;
   - 13/14 TeV comparison for the three actual benchmarks;
   - candidate table with explicit 16 source IDs, masses, gamma, tanbeta,
     flavor reference pull and unresolved constraints;
   - proposal-arm cutflow / robustness commentary without claiming
     model-space probability.
5. Produce a draft **limitations/approximation** section with the
   exact B→Xsγ citation and Eq.(4) LO-only convention, 2017/2021
   comparison, tree-level-only widths, absent luminosity/cuts/background,
   scale/PDF uncertainties and model input assumptions. Never call
   the paper EPJC-ready solely on software PASS.

## B — Complete the actual signal-chain rates (no detector assumptions)

The 13 TeV ranking is
15591, 8850, 2264, 14984, 4611, 15673, ...
At these top points existing D4 tables show
BR(H1→t b)≈0.993–0.998. Associated H2 production followed by
H2→H1 Z→t b Z creates a `t tbar b Z` partonic signal
(inclusive charge conjugates; a 5FS incoming b has no resolved final-state
spectator b at matrix-element level).

1. Read the existing D4 family decay tables. Compute, **for each
   energy where real sigma exists**, per family:
   `sigma*BR(H2→H1Z)*BR(H1→tb)`.
   Do not assume BR(H1→tb)=1. Include other H1 modes if visible.
2. To illustrate Z→e+e− and μ+μ− only, obtain the actual
   source/version for its branching fractions, state any SM vs PDG
   convention, then calculate `sigma*BR(H2→H1Z)*
   BR(H1→tb)*BR(Z→ee or mumu)`.
   Label whether top decays are left inclusive; never silently
   include top/W BRs or acceptance.
3. If a specific 14 TeV raw yield example is shown, explicitly
   declare a hypothetical luminosity (e.g. 3 ab⁻¹), perform exact
   pb×fb⁻¹ conversion and state `before selection, detector
   efficiency, background, higher-order theory and complete decay
   chains`. The raw count is **not an HL-LHC expected limit**.
4. No signal significance, 95% CLs limit or claim of exclusion
   without an explicitly matched background and efficiency model.
   If such a projection is desired, describe the minimum experiment-
   level/simulation inputs needed for a separate study; do not
   fabricate them.

## C — Source-controlled uncertainty and 14 TeV completeness

1. Perform an **a priori finite** real 14 TeV production pilot for
   point **8850**, presently ranked second at 13 TeV, with strict
   mapped-card, PDF/source/receipt validation used by D14D.
   This tests whether the top two 13 TeV benchmarks preserve their
   ordering under actual 14 TeV production. If the pinned runtime is
   unavailable, leave this as a manual run with production UNKNOWN.
2. If resources permit, perform the standard **seven-point LO
   muR/muF scale variation** for ID 15591 at 14 TeV with the
   Yukawa masses frozen at the central reference scale and all
   PDF/model inputs held fixed. Reuse the validated real MG framework.
   Report only scale sensitivity; it is not NLO correction or full
   uncertainty. Do not label integration-only error as a theory error.
3. For PDF uncertainty, use an authentic PDF ensemble only if
   available and correctly matched to a defined alpha_s/PDF
   prescription. Otherwise PDF uncertainty UNKNOWN, rather than
   invented member variations. No generic K-factor.
4. Never substitute 13→14 reweighting for uncomputed spectra.
   Do not overwrite original D14D artifacts.
5. Use a small test that reconstructs channel BR arithmetic from
   16 validated source cards; negative, missing or mismatched
   family/energy records must fail closed.

## D — Next high-statistics conditional scan: plan and pilot, not auto-submit

The 20k proposal has only 16 positive-vacuum/nominal-flavor intersections,
too sparse for a robust multidimensional publication plot. The existing
`module14/conditional_scan/next20k_proposal.json` was only a proposal
and has **not** been run.

1. Design a **manual 100k-point conditional follow-up proposal**
   with documented sampling arms around the promising
   mH2=1.0–1.35 TeV window, an independent sub-TeV arm and a broad
   control arm. Retain non-endpoint gamma and the open Z channel.
   Do NOT fit to the 2026 flavor pull to manufacture survivors.
   Pin an independent seed, config hash and generator version;
   proposal weights are NOT physical prior/volume fractions.
   Include the full neutral spectrum/quartics and Yukawa-family
   sampling, as in validated D14.
2. Validate only a **small local pilot** (e.g. 100-500 proposals)
   for correct deterministic sharding, collection, conditional
   status mapping, vacuum UNKNOWN and source hashes. Provide
   a real output cutflow, not an expected-survivor prediction.
3. Output exact `/home` Condor packaging and `/data` immutable
   run collection commands, resource estimates based on **actual**
   receipts, a staged manual execution plan (pilot batch first).
   No automated Condor submission or large scan in Codex.
4. Decide what a high-statistics scan can establish under current
   limitations: distributions of **conditional** candidate classes
   and comparative cascade trends, but **not** a globally
   exclusion-approved parameter-space fraction or complete
   flavor/low-energy/Higgs likelihood.

## Deliverables and scientific stop criteria

- New files only under `module14/conditional_scan/` and
  `tests/test_module14_conditional_*.py`:
  `PAPER_READINESS.md`, `paper_channel_rates.json`, a
  `paper_figure_manifest.json`, `final_conditional_scan_config.json`,
  and focused scripts/tests as needed.
- A figure should be based on source-verified inputs and include
  "conditional LO" and relevant omitted-constraint disclosures.
- Original Modules 0–13, D14 original worker, original 20k/225
  evidence and production receipts remain read-only. No new
  precision B→Xsγ or vacuum theorem work. No contact with authors.
- Run focused tests and `git diff --check`; commit and push
  reproducible evidence only.

Final result:
`PAPER_CONDITIONAL_ANALYSIS_READY` means actual validated
conditional figures/channels plus staged 100k manual scan package.
It does **not** mean full B→Xsγ/LFV/HiggsTools acceptance or an
experimental sensitivity projection. If critical input is missing,
report `PAPER_CONDITIONAL_ANALYSIS_PARTIAL` and its exact blocker.

**One important boundary:** The ultimate intended paper may require
realistic detector or background acceptance for 95% CL projections;
provide the inputs necessary rather than making unjustified claims.
