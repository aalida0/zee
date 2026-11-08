# Four-witness LFV transfer: source-matched leading 2HDM → Zee amplitudes
**Authorized 8 November 2026; one bounded Codex execution, no automatic multi-round continuation.**

## Scientific purpose and precise stop condition

Compute and independently validate the **non-overlapping transferable neutral-sector contributions** to the complex Zee μ→eγ dipole coefficients for the **four existing, exact D7 and F13 NO/IO Yukawa cards**. Do not reopen the finished 2017/2020/2021 model literature search, Candidate A vacuum 93-point pilot, full flavor/B/Higgs scan, or prior 28 F-box source-matching controls. The **finished deliverable can be a negative/blocked outcome**, but it must contain actual executed source-matched numerical controls if possible and an exact next-physics dependency.

Reference audit: `research/full_constraints/LFV_2HDM_TO_ZEE_PRIMARY_SOURCE_REUSE_AUDIT_2026-11-08.md` and `research/full_constraints/LFV_COVERAGE.md`.

**This first stage is intentionally ONLY the genuinely missing, standalone gauge-invariant general-2HDM classes:**
1. **Neutral heavy-fermion (Zγ)** Barr–Zee contributions (the Z-exchange part of the 2025/2026 general 2HDM source, corrected where required by 2026 erratum).
2. **Neutral (hZ) kinetic group** if a source-matched, separately gauge-invariant interpretation of the full group is verified.

The existing Module4 photon fermion/photon and charged-scalar/photon terms **MUST NOT BE ADDED TWICE**. Some 2HDM terms that contain a charged scalar are not standalone transferable 2HDM classes: the (f_{8e}) kinetic term lives inside the **complete** `kin` aggregate and must not be taken in isolation; `HZ` has off-diagonal Zee Z currents; `HW` has a recorded source/code dimension discrepancy; charged-fermion-`W` terms need a future separately matched test. They are explicitly **NOT IMPLEMENTED in this first stage**, although their materiality and next steps must be recorded.

## Read prior results BEFORE code changes

Read:
- `AGENTS.md`; `research/full_constraints/LFV_2HDM_TO_ZEE_PRIMARY_SOURCE_REUSE_AUDIT_2026-11-08.md`; `LFV_COVERAGE.md`; `LFV_PRACTICAL_IMPLEMENTATION_REPORT.md`; `LFV_TEXTURE_MATERIALITY_RESULT.md`; `LFV_VALIDATION.json`.
- Frozen `module3/core.py`, `module4/amplitudes.py`, `module4/charged_scalar.py`, `module4/interface.py` and their limits; `module14/physics_adapters/lfv_reference_evidence.json`; saved `validation/module12/d12_benchmarks.json` and `research/full_constraints/lfv/{TEXTURE_COUPLING_AUDIT.json,TEXTURE_MATERIALITY_REPRODUCED.json,PRACTICAL_SENSITIVITY.json}`.
- Public 2HDM original JHEP06(2025)156, arXiv **2410.17313v4** and **erratum JHEP07(2026)184**. Pinned author GitLab `jbrod/general-2hdm-pheno` `thdm.py` at commit **b5035cd58d2a7e4a91e9790d045df062b97adffe**, source sha256 **9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193** from the saved audit, *not a moving HEAD*. Source code is downloadable only if not available in the local scratch/cache. If downloaded, pin source revision and verify checksum.

**Critical two-card-family mismatch:** `LFV_PRACTICAL_IMPLEMENTATION_REPORT.md` uses D7/F13 `NO/IO/scale_0.001` (D7 NO μ→eγ partial BR ≈1.387e-10), whereas `LFV_TEXTURE_MATERIALITY_RESULT.md` uses a different D7/F13 `NO/IO/texture_0.0001` or `texture_0.001` low-joint card (D7 NO ≈1.56e-19). They are NOT interchangeable. The baseline dataset for this task is **the actual four texture cards reported in the LFV_TEXTURE_MATERIALITY_RESULT**, only if exact original per-card scalar+neutrino+Yukawa and module outputs can be joined and verified. If the full precise card input for a texture record is not available, STOP with an explicit `CARD_PROVENANCE_BLOCKED` rather than silently substituting the `scale_0.001` cards. The scale cards may be evaluated as **separately labeled cross-checks only** if cheap, but cannot substitute in the designated 4-card matrix.

## Frozen physics conventions

- `L_dip = e*m_mu/2 * bar(e) sigma^{mu nu}(C_L P_L+C_R P_R) mu F_{mu nu}+h.c.`, `[C]=GeV^-2`.
- General-2HDM dimensionless source convention `C_X=-c_X/(8*pi^2*v^2)` **only after the source's ordered external flavor mapping is confirmed**. Do not guess complex conjugation, chirality, sign, or external lepton masses.
- `D=-sin(beta)*Ye+cos(beta)*Ye2`; native `F=2*f_Chen` and antisymmetric; charged rotation `H_D=cos(gamma)*H1-sin(gamma)*H2`, `S=sin(gamma)*H1+cos(gamma)*H2`.
- Source's published Eq. numbers and arXiv v4 numbering may differ. Quote the exact source and version in the input matrix, including 2026 erratum. No '2HDM total times cos²gamma' shortcut.

## Executable phases with hard gates

### 0. Input manifest and baseline replay (do this first)

- Identify the four actual `texture` witnesses (D7/F13 × NO/IO), exact scalar SHA256, D/F/Ye/Ye2 hashes, neutrino-ordering label, direct LFV Yukawas, and saved **complex C_L and C_R**. Recover full physical input cards from frozen source files and validate signed complex baseline components against Module4 output if possible.
- Produce `CARD_PROVENANCE.json` with two explicitly distinct datasets (`texture_low_joint` and `scale_0.001_old`), each `type,id,scalar_sha256,yukawa_sha256,available_fields,status`. A string label alone is not a hash check. Do not compare cross-family amplitudes without matching source cards.
- `BASELINE_REPLAY.json`: retained complex C_L/C_R, `BR_partial` and source hashes for exact same four cards. Reproduce saved retained norm to <=1e-10 relative or STOP `BASELINE_MISMATCH`. This is an engineering/source gate, **not** a new physics contribution.

### 1. Source-matched 2HDM numerical controls

- Read the actual corrected author source, identify complete functions and ordered `cL_llpg/cR_llpg` `hZ`, neutral fermion-`Zγ` components, source erratum, sign and chirality conventions. Preserve source SHA and source-only model limit values.
- Implement **independent evaluation** (not merely reusing the same function twice) from source formulas for at least two nonzero 2HDM controls with conjugate/complex Yukawas. Verify both chiralities and source (C_Xleftrightarrow c_X) normalization. Use arbitrary controlled 2HDM parameters only as analytic test vectors, NOT claimed new Zee model points; actual predictions only on frozen cards.
- F=0, gamma=0 should recover the original author one-charged-doublet result in the appropriate limit; pure singlet and no-LFV-Yukawa limit should remove the transferable neutral term. Rephasing, source normalization, complex conjugation and both charged-mixing endpoints must be explicitly tested at the operator level.
- If source's `hZ` group or Zγ sector is not independently gauge invariant in the required decomposition, report `NOT_TRANSFERRED_GAUGE_AGGREGATE` and **do not** assemble from fragmentary Feynman diagrams.

### 2. Only non-overlapping neutral amplitudes, same four cards

- Implement in **`research/full_constraints/lfv_transfer_2026/` only**; use frozen Module4 as read-only. Produce a complex `(C_L,C_R)` contribution per specific source group and benchmark with: source equation/version, loop order, mass inputs, state/vertex flavor factors, numerical method, independent control, uncertainty/completeness scope.
- For each card calculate `baseline`, `neutral_Zgamma`, `hZ` (only if validated), `sum_scoped`, `BR_scoped`, and `missing` as explicitly nullable. **Coherent complex sum before BR**.
- Explicitly list the 2025 `tHp/cHp/tauHp`, full `kin` W/G/ghost, mixed Zee `HZ`, `HW`, (F^†F) gauge-dressed and μ→3e/conversion pieces as NOT_EVALUATED. Do not promote selected pieces into physical `LFV_PASS` or imply the missing total is small.
- Compare added neutral contribution norms and interference against the **correct** saved retained baseline and **source-pinned MEG-II** 90% input, with the mathematical `sufficient_missing_norm_budget` displayed as a conditional budget **not actual bound**. Numerically compare with archived old scale cards only as separate optional control.

### 3. Decisive classification and bounded finish

Write:
- `RESULT.json`: `status` in `SCOPED_NEUTRAL_TRANSFER_VALIDATED`, `NO_NEW_TRANSFER_SUPPORTED`, `CARD_PROVENANCE_BLOCKED`, `SOURCE_OR_CODE_DISCREPANCY`, `EXECUTION_BLOCKED`; `four_cards_count`, `validated_new_groups`, `baseline_replay_pass`, `original_source_sha`, `test_counts`, `missing_groups`, `physical_lfv`=UNKNOWN, `global_acceptance`=null, `final_artifacts_ready`=true **only** with actual evidence+test receipts.
- `AMPLITUDE_LEDGER.json` (actual signed complex per-group by card), `CARD_PROVENANCE.json`, `BASELINE_REPLAY.json`, `EXECUTION_REPORT.md`, `REPRODUCE.md`, `SOURCE_CONVENTION_MATRIX.md`, `TEST_RECEIPT.md`, `WORK_CHECKPOINT.md`, focused tests with clear negative controls.
- Final report must explicitly state what was *really executed*, whether the source was **independently numerically** checked or merely source-inspected, whether transfer covered either group, what is next *only if needed*, and how result affects LFV benchmark classification. If no new transferable group passed, state NO_NEW_TRANSFER_SUPPORTED / discrepancy rather than inventing diagrams or a fake positive result.
- Frozen model/modules/test receipts and already completed research remain **unchanged**; no new physical scan, MG5/Condor/Delphes, arbitrary large-model generation, or fresh gauge two-loop tensor project. Work in a **single Codex execution**, do not ask launcher to repeat if incomplete. Limit heavy calculations to this 4-card task; do not allocate additional >16-point diagnostics.

## Explicit reviewer gate

**Releasing 4 physically allowed cards is NOT an expected output**. Even a complete matching of neutral contributions leaves `LFV_UNKNOWN` until the omitted leading sectors can be physically bounded. Only a validated contribution subset is eligible for PASS in this task. Existing BR values are conditional diagnostics. Do not silently interpret them as physical exclusion or acceptance.

**Git behavior:** Codex may download public paper/code into ignored `work/lfv_transfer_2026/`. Do not directly commit/push; a separate launcher outside Codex's protected `.git` will stage and push only the pilot results **if and only if the allowlisted scope and formatting checks pass**. `AGENTS.md` must be read and this task supersedes the completed all-constraints task for this pilot. Exit with a concise physics summary, input hashes, test counts and blocker status.
