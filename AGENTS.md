# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## Mandatory source-first literature gate (new: 7 Nov 2026)

Before claiming any Zee-specific loop calculation, scalar/vacuum constraint,
flavor uncertainty, or numerical implementation is absent from the literature,
**read** `research/full_constraints/LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md`
and the actual paper full text, then check relevant **references AND citing works**.
Document DOI/arXiv, exact equation, physical particle content, Yukawa
restrictions, source/code version, and a tested limiting case. A previous
false absence claim overlooked Florentino–Romão–Silva 2021 App. D.3 Eq(D.20)
for mixed charged-scalar h→Zγ, Hue 2018 unequal-mass PV formulas,
Bilenky–Santamaria 1994 singlet EFT, and old Zee LFV box/Z-penguin formulas.
Do **not** call an unimplemented published expression nonexistent; do not call
a restricted formula complete general Zee physics. Citation-search indexing is
not exhaustive; report limitations. Always preserve original frozen modules.

## CURRENT TASK — bounded four-witness leading LFV transfer (8 Nov 2026)

**Active user-authorized task:** `research/full_constraints/lfv_transfer_2026/TASK.md`. Implement and independently check only genuinely non-overlapping **neutral heavy-fermion Zγ** and **neutral hZ** leading general-2HDM amplitudes (if their gauge-invariant groups and source-to-Zee coupling map are established), on exact source-hashed D7/F13 NO/IO `texture` cards. This is **not** the earlier `physical_closure_2026` umbrella campaign, which was completed and pushed with 66/66 UNKNOWN. The previous `Candidate A` vacuum/cascade studies also ended NO-GO and must not be rerun.

**Card ambiguity requires an explicit gate:** Archived `LFV_PRACTICAL_IMPLEMENTATION_REPORT.md` uses `scale_0.001` D12 Yukawa witnesses, whereas `LFV_TEXTURE_MATERIALITY_RESULT.md` uses different `texture_0.0001` or `texture_0.001` witnesses. Their LFV partial rates cannot be equated. Inspect original complex matrices, scalar and witness hashes and signed baseline before adding ANY source-transferred amplitude. If original texture cards cannot be reconstructed with verified inputs, record a truthful `CARD_PROVENANCE_BLOCKED`; do not substitute old scale cards.

**Scope/permissions:** New source, tests and result files only under `research/full_constraints/lfv_transfer_2026/`. Public **verified** source downloads only under ignored `work/lfv_transfer_2026/` using a workspace-write sandbox and narrow outbound host allowlist. No full-access, `--yolo`, sudo, secrets, new mass/scan points, frozen Module0–14 changes, generated physics models, Condor or collider simulation. Never directly commit/push inside Codex; trusted user-launched `research/full_constraints/lfv_transfer_2026/run_once.sh` stages, commits and pushes **only** narrowly allowlisted LFV results after checks. Just ONE Codex execution per invocation, with no autonomous follow-up loops.

**Accuracy:** The corrected 2025 general-2HDM (2026 erratum) does not include singlet `F` and its leading two-loop prescription explicitly drops certain corrections to already-present one-loop flavor structures. Do not misrepresent it as complete general Zee. Do not double count already validated Module4 photon groups. Source-match (C_L,C_R), erratum, complex phases and mixing; do not extract (f_{8e}) from full gauge kinetic aggregate, copy mixed Zee `HZ/HW` one-state formulas or silently fix reported public `HW` normalization issue. Missing (F)-gauge/mixed-current contributions remain UNKNOWN until separately addressed.

**Deliverables:** exact input SHA manifest, replay of frozen complex baseline for 4 cards, two independent nonzero source controls where feasible, executed signed neutral-group contributions or a documented scientific/software stop, focused falsifier tests, `EXECUTION_REPORT.md`, `RESULT.json`, and clear `LFV_UNKNOWN` if unassessed sectors remain. A partial/blocked result is an honest terminal outcome and **not authorization for another mass scan or open-ended two-loop calculation**.

## Mandatory physics safeguards

- "Complete" means all materially relevant contributions at the
  **explicitly declared perturbative order** with justified numerical
  and theoretical uncertainties, correct interference and physical
  confidence interpretation. Not literally all perturbative orders.
- Two mixed Zee charged states are NOT separately subject to the
  single Type-II 670 GeV bound. Use coherent Wilson coefficients.
- The corrected general 2HDM two-loop LFV backend is NOT complete Zee;
  the neutral fermion/photon subset is already in Module4 and must
  not be double-counted.
- SARAH/SPheno **full-loop observables are unavailable** (unphysical
  ~10^6 GeV WW loop widths and eV neutrino input-scheme mismatches).
  Compiling the backend did not validate its physics.
- HiggsTools requires source-bound rates for every applicable
  channel and collision energy; missing predictions are NOT zeros.
- A validated single failing observable can yield PHYSICAL_FAIL.
  `global_acceptance=PASS` requires all mandatory observables
  independently covered. Any uncomputed mandatory observable -> UNKNOWN.
- Original Modules0–13, D14 scanners/reports, 20k/225 collections,
  16-point MG5 map, all frozen source/receipts and separate B research
  branch are **read-only**. Work in `research/full_constraints/` and
  isolated optional adapters, retaining complete provenance and tests.
- No new parameter-space proposals (even a pilot), no exploratory
  scans, no Condor submission, no production campaign, no unauthorized
  merge into the frozen final-scan branch. Existing saved cards and
  analytic model-limit controls may be evaluated for validation only.
- Timebox/source-gate every area. A blocked full-physics result must
  remain UNKNOWN, not become a soft/conditional claim mislabeled 95% CL.
- Use English for all Codex sessions, notes, code review and commits.

## Current deliverable

Execute the single focused task `research/full_constraints/lfv_transfer_2026/TASK.md` on four frozen D7/F13 NO/IO `texture` witnesses, preserve existing production/constraint/vacuum results, and stop after reporting validated new groups and exact remaining coverage. No broad revalidation or repeated prior pilots.
