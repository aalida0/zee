# D14G — Final SPheno physical-consistency triage and physics freeze

**Branch:** `feature/zee-d14-conditional-cascade-scan`.
**Baseline:** `5865e8d5f4f18f35cd72f5f43249640c92b4e890`.
**USER DECISION:** The project must finish and freeze the workflow code. **No more parameter-space scans or broader calculations. The next and only large scan will be the user-authorized final scan.**

## Purpose: one forensic diagnosis, not another research program

The full SARAH/SPheno 4.15.4/4.0.5 Zee build **compiles**, but its loop-level
physical predictions catastrophically disagree with the original physical
model inputs. We must decide whether a **simple, genuine model/scheme/SLHA
mapping error** explains this, or whether the full-loop backend remains
unusable in our paper's scheme. We **must not** use absurd loop spectra and
widths as HiggsTools/LFV exclusions.

Existing evidence: `module14/PHYSICS_ADAPTER_READINESS.md`,
`module14/physics_adapters/spheno_build_evidence.json`,
`module14/physics_adapters/SPheno.m`,
`module14/public_spheno_evidence.json`. Fixed four original D12 cards:
- loop neutrino masses up to 5.54 eV, rather than radiative one-loop
  target singular values ~0.01–0.051 eV;
- 'light Higgs' pole masses ~302/358 GeV instead of tree input 125 GeV;
- total one-loop widths 0.75–1.13 **million** GeV, far above masses;
- scalar tree card/mixing closure remains accurate to ~1e-9; original
  scalar-one-loop LFV card matching had separate good component-level
  results but is NOT a complete LFV validation.

These are **observations**, not a diagnosis. Avoid premature labels
such as gauge failure, double counting, numerical bug or perturbative
breakdown until source and card evidence establish which.

## Phase A — Forensic analysis of SAVED outputs only

1. Inspect source-pinned original `full.spc`, `tree.spc`, original
   inputs, logs and generated Fortran in ignored local storage. Verify
   exact hashes before reading; if not mounted, report the exact missing
   artifact and provide commands for an operator to run locally.
2. For each saved point, identify the *specific* decay channel(s) and
   particle(s) responsible for enormous summed one-loop total widths,
   including phase space, tree vs loop contribution, sign, multiplicity,
   renormalization scale, external masses and complex couplings.
   Cross-check whether the total equals the actual channel sum.
   An enormous total without a channel-level explanation is
   `FULL_LOOP_WIDTH_CAUSE_UNRESOLVED`.
3. Investigate pole-mass shifts by comparing tadpole/renormalization
   scheme, chosen SM/EW input definitions, tree vs loop mass matrices,
   mixing, subtraction/convergence, `SPheno.m` matching conditions
   and generated boundaries. Verify whether the supposed 125 GeV
   Higgs is truly the same eigenstate at tree and loop level.
   Require a source-located explanation rather than changing inputs
   to make 125 GeV appear by construction.
4. Investigate neutrino masses carefully: **Zee neutrinos are
   radiative at leading order**. Verify whether the 1-loop neutrino
   self-energy from the *full* model includes the intended leading
   mass once, rather than tree vs one-loop contributions in
   inconsistent conventions or repeated contributions. Check
   flavor basis, neutrino rotation, complex-conjugation conventions,
   neutrino momentum/renormalization schemes and suppression factors.
   Do not enforce the target singular values by overwriting output.
5. Differentiate genuine physics/scheme mismatch from a generated
   source bug. Where possible, test analytic power counting, gauge
   identities and decoupling on the **same existing input**. No new
   mass scan or variable-fitting study.

## Phase B — Single bounded correction only if root cause is demonstrated

- If A yields an **unambiguous localized, model-correct fix** (e.g.
  malformed LHA conversion or one missing physical rotation), make
  a minimal change in a separate pinned research model/adapter,
  save source diff and rerun **at most two of the four exact original
  cards**. Validate that neutrino masses, scalar masses, tree cascade,
  full loop BRs and appropriate loop predictions now agree with
  independent sources within defined tolerances, with proper
  perturbative width/mass behavior. No blanket truncation or
  artificially suppressing channels. Check physics constraints and
  gauge completeness before enabling any new operative observable.
- If no unambiguous correct fix is found from the saved evidence,
  STOP. Keep full-loop SPheno **DIAGNOSTIC_ONLY / UNAVAILABLE** and
  existing frozen D4/Module4 predictions. This is a successful
  bounded triage, not permission for another month of generator
  patches.

## Phase C — Freeze the final workflow's physics scope

1. Confirm the corrected **streaming exporter** and frozen 225-point
   source replay remain byte-identical and memory-safe. Do not
   re-implement what passed at commit `5865e8d`.
2. Enumerate **exactly which constraints the single final scan may
   apply as actual hard vetoes** versus conditional/partial diagnostics:
   reconstruction, BFB, tree unitarity, EWPO, sufficient D10 vacuum
   PASS (UNKNOWN not FAIL), neutrino reconstruction; LFV by validated
   subset only with its clear coverage; published 2026 linear B→Xsγ
   only diagnostic, no single-state 670-GeV substitute;
   h125/HiggsTools only with original declared incompleteness;
   full SPheno pole/loop widths NOT operative unless corrected and
   source-validated here.
3. Audit actual `final_config_template.json`, relevant stage flags
   and `final_workflow.py`: no optional unvalidated external code
   may be enabled as a hard veto by a misleading flag. Add a
   **fail-closed preflight check or warning** for any unsupported
   full-loop SPheno/Higgs/rare-decay override. No new physics kernels.
4. Produce a short model-aware **paper claims matrix**:
   (a) what the final scan can establish as reproducible conditional
   Zee phenomenology;
   (b) statements not supported (`fully constrained Zee`,
   `complete two-loop LFV`, `certified all global vacua`,
   `full-NNLO Zee B→Xsγ limit`, `HL-LHC 95% CL expected limit`).
   The user's paper can still report a transparent conditional
   constraint-and-cascade analysis if framed accurately.
5. Do NOT initiate Vevacious or HomotopyContinuation gauge
   reduction from scratch, or open another two-loop calculation.
   Their already established gaps must remain documented.
6. Deliver `module14/FINAL_PHYSICS_FREEZE.md` with
   `SPHENO_FULL_LOOP_OPERATIVE=YES/NO`, exact cause/evidence,
   all remaining missing physical pieces, code/physics status,
   one manual final-run preflight checklist and freeze recommendation.
   Make any needed updates to `FINAL_WORKFLOW_READINESS.md`,
   `EXTERNAL_CAPABILITY_MATRIX.md` and runbook only on actual evidence.

## Final acceptance and stop

Run source/physics adapter tests, final workflow tests, original
225-point replay and `git diff --check`. Preserve all original
Modules0–13, existing D14 scan and production evidence, pinned
external source and saved generated cards. Changes only under
`module14/`, `scripts/zee_d14_*`, `tests/test_module14_*`
and docs. No MG5, no new proposals, no HTCondor, no new
external author contact.

Report:
- `FINAL_PHYSICS_SCOPE_FROZEN_CONDITIONAL` when no additional
  unvalidated physical claims are enabled and one final manual
  conditional scan is technically ready, with any remaining
  issue named.
- `FINAL_PHYSICS_FREEZE_BLOCKED` if code/preflight or source
  inconsistencies prevent freezing even this **conditional**
  workflow.

**Do not claim `PHYSICS_VALIDATED` when B→Xsγ, full Zee LFV,
global vacuum or HiggsTools remain incomplete.** Commit/push audited
work only. **Do not launch the final scan.**
