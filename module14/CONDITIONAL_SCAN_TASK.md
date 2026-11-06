# D14B — Conditional Zee cascade scan without waiting for B→Xsγ authors

**Branch:** `feature/zee-d14-conditional-cascade-scan`.
**Starting base:** `feature/zee-d14-integrated-scan` at `b1ec52c4656186532ca17f559fc40aca49fd2730`.
**Owner workflow:** Codex on Ubuntu for code/test development; user submits HTCondor jobs on the UChicago AF separately.

## Physical goal and scientific integrity

Produce a reproducible **conditional** parameter-space and collider-priority
dataset for the Type-II Zee model with the on-shell
`H2± → H1± Z` cascade. This is the continuation of the research project,
not a new precision B→Xsγ backend effort.

There is no author-provided joint nonlinear 2026 B→Xsγ response/NP error.
We may legitimately use Eq.(4) of Misiak et al. arXiv:2608.29863v1
for **published-leading-NP approximate phenomenology**, but must not call
its conditional comparisons definitive exclusions or globally allowed points.
The 2026 single-Higgs Type-II `670 GeV` bound does NOT apply separately
to two mixed Zee charged scalar masses.

**Hard rule:** report each constraint's *actual* coverage separately.
Only a demonstrated, validated physics hard gate may eliminate a point as
`FAIL`. Theory-unvalidated areas remain `UNKNOWN`; passing a diagnostic
must never change `globally_allowed=None`.

## Existing resources — read before implementing

Read selective files:
- `module14/D14A_INTEGRATED_SCAN_AUDIT.md`,
  `module14/AF_RUNBOOK.md`, `module14/COLLECTION.md`,
  `module14/heavy_scan_config.json`, `module14/scan.py`,
  `module14/collect.py` and relevant worker interfaces.
- `module1/d10_certificate.py` for sufficient vacuum certificate;
  `module7/cascade_z.py`, `module7/d4_decay_table.py` for
  charged scalar rates; `module13/` and `module14/external.py` for
  production/HiggsTools contracts.
- `module5/BSGAMMA_2026_ACCURACY.md`,
  `module5/BSGAMMA_SCAN_TRIAGE.md`,
  `module5/bsgamma_2026_linear_diagnostic.py`,
  `validation/module5/linear_2026.json`. Existing validated
  leading-order matching is available locally in this D14 base.
- **Separate research branch**, `research/zee-bsgamma-rate-validation`
  at `4c7998579e0dacd87fb1d73fa328de8c026a9c0c`, especially
  `research/bsgamma_rate_validation/M2026_ROUTE_RESULT.md` and
  `m2026_route_results.json`. Read with `git fetch` / `git show`
  when available. Do **not** merge that branch wholesale or copy binaries.
  The same source branch now contains `OUTREACH_AND_TRIAGE_HANDOFF.md`
  explaining why gamma endpoints are collider-irrelevant.
- Existing `module14/AF_RUNBOOK.md` specifies 20,000 heavy proposals
  (80 shards) and a 225-ID follow-up (9 shards). **Neither 20k proposed
  nor 225 follow-up IDs are globally allowed points.**
  Do not make up completion status for remote AF data.

## Phase 0 — Audit the actual scan results BEFORE a new run

1. On Ubuntu, inspect tracked D14 pilot and runbook only. On UChicago AF,
   **if accessible**, locate the existing 20k and 225-run files and
   execute the original `module14.collect` receipt/hash checks using the
   command patterns in `AF_RUNBOOK.md` with new immutable output files.
   Require `COMPLETE`, all expected shards, `missing_points=0`,
   exact source commit, input manifest/hashes and matching source settings.
   Do not submit, overwrite, merge partial shards or claim completion
   without actual receipts. If AF files are unavailable locally, produce
   minimal read-only export/collection commands for the user, then
   continue local tests using the committed pilot; clearly mark real scan
   collection `PENDING_REMOTE_EVIDENCE`.
2. Inventory stage-by-stage outcomes: BFB, unitarity, EWPO, sufficient
   D10 vacuum certificate, NO/IO fit provenance, perturbativity, tree
   decay table, LFV (coverage), D9B legacy, HiggsTools, production.
   Explicitly distinguish `PASS`, `FAIL`, `UNKNOWN`,
   `NOT_EVALUATED` and `ERROR`. Do not silently convert unknown
   vacuum or LFV into PASS.

## Phase 1 — Lightweight 2026 B→Xsγ sidecar (conditional, not exclusion)

The letter's Eq.(4), CP/isospin averaged and `Eγ>1.6 GeV`,
specifies at `μ0=160 GeV`:

```
10^4 * BR_linear = (3.54 ± 0.14) - 8.51*DeltaC7_LO - 2.16*DeltaC8_LO
BR_exp=(3.49 ± 0.19)*10^-4
```

DeltaC7/8 are **ordinary unprimed alpha_s^0 NP matching coefficients**.
Compute them for two charged eigenstates coherently with the correct
doublet projection weights `cos²gamma, sin²gamma`, then evaluate Eq.(4)
ONCE. Do NOT inject NLO C4/7/8, add arbitrary alpha_s factors, rescale
old EOS/SuperIso SM baselines to 3.54, or apply a one-state mass bound.

Use existing module5/C1 implementation as the source of truth, or
copy a tiny **audited** read-only adapter into a new sidecar; do not
alter frozen Module5, D9B or D14 worker acceptance. All input cards,
top-running mass, scales, quark scheme and source hashes must be
recorded. Reject missing or incomplete point input rather than
reconstructing from candidate IDs or partial summaries.

Return:
- `BR_linear_2026`, `DeltaC7_LO`, `DeltaC8_LO`, contribution splits;
- `conditional_pull` using the explicitly labelled symmetric
  experimental and SM quoted errors **only as a reference sensitivity**
  (with assumptions), not a complete Zee NP likelihood;
- `bsg_nominal_classification` as
  `APPROX_COMPATIBLE / APPROX_DISFAVORED / APPROX_BOUNDARY / UNKNOWN`.
  The threshold for the first two is an explicitly predeclared
  **conditional-only** 95%-style *reference*; never report as a
  validated 95% CL constraint.
- `bsg_physical_classification=UNKNOWN`,
  `np_theory_sigma=None`, `bsg_exclusion=None`,
  `globally_allowed=None` in **every** row unless an independent
  future validated prescription is supplied.

Predeclare numerical boundary sensitivity. One useful comparison is
a **separate**, clearly non-probabilistic robustness flag:
`APPROX_STABLE / METHOD_SENSITIVE / NOT_EVALUATED` after testing
existing, source-specified EOS/SuperIso/NLO-matching variants on a
small *fixed* sample. Method spread is NOT a 1-sigma NP uncertainty.
Never fit a tolerance to obtain a desired lighter-mass survivor.

## Phase 2 — Cascade-aware conditional benchmark shortlist

1. Require ordered `mH2>mH1` and on-shell
   `mH2>mH1+mZ`. Use `module7/cascade_z.py` and full
   `module7/d4_decay_table.py` where validated.
2. The off-diagonal Z coupling obeys
   `g_ZH2H1 ∝ -sin(2gamma)/2`. Thus gamma=0 or ±π/2 gives
   **zero cascade** even if B physics looks favorable.
   Do not rank on B alone or treat `Gamma(H2→H1Z)` as a branching
   fraction if total competing widths are missing.
3. Rank points only with clearly labeled, physically comparable
   `BR(H2→H1Z)`, production cross sections (energy/model match),
   and cascade yield proxy `sigma * BR` where supplied; flag
   absent production or widths as `NOT_EVALUATED`. Include neutral
   spectrum and scalar/LFV/neutrino/HiggsTools gate status and
   uncertainty. No cross-energy 13 versus 13.6 versus 14 TeV
   substitution without documented factors.
4. Do not optimize for approval of `B` gate or declare the shortlist
   globally viable. A candidate can be listed as
   `conditional benchmark requiring further flavor/vacuum/LFV validation`.

## Phase 3 — Prepare the *next* scan, do not launch it

- Audit scalar, neutrino and B-screening cutflows by proposal arm,
  using **actual** complete run outputs when accessible; proposal
  survival is NOT a volume fraction or model-wide exclusion rate.
- Create a reproducible configuration for a follow-up scan
  emphasizing **nonzero cascade mixing** and both sub-TeV and
  higher mass charged spectra. Preserve a broad sampling arm to
  avoid selection bias and publish separate arm counts.
- Demonstrate one small local generation+worker+collector pilot,
  sharding/seed reproducibility, sidecar source hashing and
  fail-closed status handling. Then output exact UChicago AF
  manual submission commands and resources. Do **not**
  auto-submit HTCondor jobs or run a 1e6-point scan in Codex.
- Freeze complete structured output with stage-by-stage statuses,
  uncertainties and conditional assumptions. **No final fully
  constrained Zee acceptance claim** until relevant independent
  uncertainties/coverage are resolved.

## Deliverables

Make new code/files under `module14/conditional_scan/` (or
`scripts/zee_d14_conditional_*`) and tests under
`tests/test_module14_conditional_*.py`. Do not alter existing
Module0–13 or D14 generated evidence. Add
`module14/CONDITIONAL_SCAN_READINESS.md` and JSON pilot outputs,
plus human-executable AF collection/submit commands.
Protect all prior hashes, use focused tests and `git diff --check`;
commit and push validated work only to this branch.

Report precisely one:
- `CONDITIONAL_SCAN_READY_LOCAL`: local reproducible end-to-end pilot
  and valid conditional statuses; remote AF evidence may still be pending.
- `CONDITIONAL_SCAN_READY_REMOTE`: in addition, original 20k and
  225 follow-up fully collected with exact receipt/manifest evidence.
- `CONDITIONAL_SCAN_BLOCKED`: concrete reproducible blocker preventing
  even a conditional, local physics sidecar.

**No publication-level final acceptance is implied by these labels.**
