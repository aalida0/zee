# D14C — Targeted production and vacuum follow-up on verified 225 points

**Current branch:** `feature/zee-d14-conditional-cascade-scan`
**Starting commit:** `8eaaac6a835eb739dbf66ebbb16bd8b103fd0ec6`.
**Work in English.** Follow updated `AGENTS.md`.

## Scientific decision

The completed 20k+225 AF batch has been receipt/hash verified; this is not
a new collection task. The existing conditional B→Xsγ screen is an
**approximate diagnostic**, not a certified exclusion or global model fit.
No author response is expected as a prerequisite.

**Do NOT launch another 20,000-point scan yet.** We need model-matched
production rates for meaningful on-shell cascade yields, and a targeted
evaluation of promising low-mass points with an unresolved sufficient
vacuum certificate. Scope this task to at most a small finite set of
production integrations/probes. Avoid reopening B-physics matching,
EOS/SuperIso precision comparisons or literature searches.

## Already verified data

`module14/conditional_scan/remote_conditional_summary.json` is derived from
the *actual complete 225-point AF result*, hash-addressed to the full
remote data; the original immutable full dataset is at
`/data/aalida/zee/d14_heavy_physics_225/conditional_dataset_20261106.json`.
Read `module14/CONDITIONAL_SCAN_READINESS.md` first.

A fresh intersection audit of the committed JSON gives:
- 225 scalar-screen follow-up records.
- 33 D10 sufficient vacuum `PASS`; 192 vacuum `UNKNOWN`.
- 77 approximate B→Xsγ `APPROX_COMPATIBLE`, 148 `APPROX_DISFAVORED`.
- **16** intersections of `vacuum=PASS` and
  `bsg_nominal_classification=APPROX_COMPATIBLE`; **zero** with
  `mH2<1000 GeV`.
- **Six** sub-TeV points with `vacuum=UNKNOWN` and
  `APPROX_COMPATIBLE`, original IDs:
  **3582, 3821, 6850, 11920, 13512, 17671**.
- D10 `UNKNOWN` is not a physical vacuum failure.
- All physical B statuses remain UNKNOWN; incomplete LFV/HiggsTools and
  missing production prevent full-model acceptance.

Preliminary conditional-production targets from the 16 (original
point IDs; on-shell tree-level decay BR across the four neutrino families):
- **15591**: `mH1=442.5934`, `mH2=1035.7037 GeV`,
  `gamma=1.296914`, `BR(H2→H1 Z)≈0.326`.
- **2264**: `mH1=674.2744`, `mH2=1165.9748 GeV`,
  `gamma=0.854499`, `BR≈0.369`.
- **15673**: `mH1=714.5076`, `mH2=1277.3633 GeV`,
  `gamma=1.253410`, `BR≈0.394`.

Sub-TeV vacuum-UNKNOWN cases for follow-up:
- **3582**: `mH2=919.21 GeV`, `BR≈0.650`,
  conditional pull ≈1.91.
- **6850**: `mH2=981.55 GeV`, `BR≈0.753`,
  conditional pull ≈1.87.
- **13512**: `mH2=952.35 GeV`, `BR≈0.805`,
  conditional pull ≈1.89.
The other three are 3821, 11920 and 17671. All six are only nominally
compatible; none has proved global scalar vacuum stability.

## Phase 1 — Exact candidate export and coverage audit (no physics rerun)

1. From the immutable `remote_conditional_summary.json`, rederive
   these counts rather than hardcoding them into output. Verify record IDs,
   scalar cards, all four Yukawa family source hashes and provenance,
   NO/IO statuses, decay table binding and each gate.
2. Produce two auditable JSON/CSV tables:
   `CERTIFIED_VACUUM_APPROX_BSG_16` and
   `SUBTEV_UNKNOWN_VACUUM_APPROX_BSG_6`, containing full scalar point
   identity/hashes, masses, tanβ/gamma, cascade BR *per family*,
   conditional B pull, vacuum certificate status, LFV and HiggsTools
   coverage, and production availability. Distinguish the tree two-body
   BR from a physical higher-order branching ratio.
3. Do not call the former `globally allowed`. Retain
   `global_acceptance=None` and `physical_bsgamma=UNKNOWN`.
   No automatic exclusion of the 148 nominally disfavored points.

## Phase 2 — Production pilot: only one to three actual points

1. Reuse the **real model-matched** machinery and physics conventions in
   `module8/D5_PRODUCTION_AUDIT.md`,
   `module8/D6_PRODUCTION_ROBUSTNESS.md`,
   `module8/d6_production.py`,
   `module8/ufo_audit.py`, `module8/mg_matrix_checks.py`,
   `module8/real_run_validation.py`.
   D5/D6 verified MG5 v3.6.7, SARAH-Zee UFO, LO 5FS
   `gb→t H2−` (and charge-conjugate, both beam orders), NNPDF30 LO
   and a 13.6 TeV benchmark at 700 GeV. The existing fixed-mass D6
   runners are NOT a production-ready *arbitrary 225-point* interface.
   Use validated source mapping to construct the new full per-point
   card; do not simply edit the mass while leaving old couplings/scales.
2. Prefer **13 TeV** for direct interface to existing D14 HiggsTools
   production contract. If targeting HL-LHC 14 TeV, perform a
   **separate actual 14-TeV calculation**, never silently rescale a
   13/13.6 TeV rate. Pin PDF, factorization/renormalization scales,
   quark mass/Yukawa running, alpha_s, charge sum, order, top widths
   and 5FS definition. Do not add 4FS on top of 5FS.
3. One small real MG5 LO pilot first, point **15591** if feasible;
   then, resources allowing, **2264 and 15673**. If actual MG5 or
   LHA PDF environment is absent on Ubuntu, document this concrete
   blocker and prepare **manual** commands (e.g. for an AF job or
   a vetted local installation). Do not invent a physical cross section.
   Integration error and 7-point LO scale sensitivity are distinct;
   a measured scale spread is not a complete theory sigma.
4. A uniform `sin²gamma` rescaling of Type-II
   `tbH2` production is plausible only where both chiral quark
   Yukawas share the same charged-doublet projection; confirm
   against the *actual* frozen Zee UFO vertices and independent
   amplitude tests, including gamma endpoints and signs.
   Only use a cached or externally supplied Type-II production table
   after physically validating its PDF/energy/scale/order/charge
   conventions. Do not assume mixed-pair Z-only production is full.
5. Bind any real matched scalar-level generator result to each
   relevant family using the existing strict
   `MODULE2_INPUT_SHA256.json` schema described in
   `module14/conditional_scan/AF_COMMANDS.md`. Supply full artifact
   hashes and the actual generated result, not a synthetic proof.
   Preserve the distinction between one scalar-level production
   amplitude and per-family SHA-bound result cards.
   **Never backfill missing rates with zero.**
6. Recalculate `sigma(pp→tbH2) × BR(H2→H1 Z)` only where
   real production and complete tree two-body BR are both
   present. Rank within exactly matched energy, process, QCD
   order, PDF and scale prescription; show per-family results and
   integration/scale uncertainties separately. No detector
   acceptance or HL-LHC exclusion yet.

## Phase 3 — Focused vacuum diagnostics for six sub-TeV candidates

1. Read D10's actual sufficient-global-certificate method and scope.
   Inspect original witness/search statuses and hashes for the six
   points in the immutable AF output. Do not rerun the full scan.
2. Attempt a **bounded** higher-resolution physical vacuum check for
   at most the three predeclared points 3582, 6850, 13512; other three
   get a triage record. An explicitly verified lower-energy stationary
   vacuum witnesses instability; absence of a witness, repeated
   multi-start minimization convergence or an insufficient D10
   certificate is **NOT** a proof of global stability. Promote a
   point to PASS only if a previously established *sufficient*
   mathematical certificate applies without new unvalidated
   assumptions. No new scalar-potential theorem or multi-month
   minimizer research.
3. Preserve all original scalar datasets, statuses and hashes. Output
   a separate vacuum diagnostic record with `PASS/FAIL/UNKNOWN`,
   source and method coverage; no silent mutation of D14 gates.

## Phase 4 — Make a decision, not a new giant scan

- Produce `module14/conditional_scan/CANDIDATE_FOLLOWUP.md`,
  `candidate_followup.json`, a reproducible export script and
  focused tests in `tests/test_module14_conditional_*.py`.
- If actual 13-TeV production was feasible, include real artifact-bound
  rates, yield rankings and source hashes. Otherwise explicitly
  mark `PRODUCTION_PENDING` and give actionable, manual commands.
- Summarize what the first three production probes imply for the
  cascade signal *conditional* on present flavor/vacuum/LFV data,
  and whether there is a meaningful mass window worth resampling.
- Only then recommend a new 20k proposal configuration, clearly
  separated from the original; do **not** submit or run it here.
- Run focused tests and `git diff --check`, commit/push only this branch.
  Preserve Modules 0–13, D14 original worker, the original 20k/225
  evidence and the separate B-physics research branch.
- No new precision flavor framework, no global accepted-point flag,
  no claim of final HiggsBounds or LFV completeness.

**Final labels**:
- `TARGETED_PRODUCTION_EVIDENCE_AVAILABLE` only if independent real
  production artifacts were executed and verified for ≥1 point;
- `TARGETED_PRODUCTION_PENDING` if only card validation/plans exist;
- `TARGETED_FOLLOWUP_BLOCKED` only for a reproducible source/data
  blocker to even generating a shortlist or audit.

These are workflow statuses, not physics acceptance.
