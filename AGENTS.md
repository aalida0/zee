# Module 5 Gate C0 — Zee two-charged-Higgs LO patch into pinned HyperIso

## Identity / immutable baseline
Use ONLY Git branch `feature/zee-hyperiso-two-state-patch` in repo `aalida0/zee`, forked from verified Gate B commit `218fe01d893730bc2699c270d10db85a22708616`. This task makes a **minimal external adapter, not a physically validated B->Xs gamma constraint**. Current validated facts: HyperIso v1.0.3 R1-R7 PASS, matched LO C7/C8 at 160 GeV through 18 real Type-II probes, and native SARAH dipole matching within explicit conventions. Gate B still has `MATCHING_CONVENTION_UNKNOWN`. Retain this status unless genuinely new external operator evidence closes it.

Do not edit `models/SARAH/ZeeTypeII`, Modules 0–4, the frozen `module5/bsgamma_lo.py`, prior tests, results or audits. Do not modify or vendor HyperIso. Do not change main, baseline branch, prior commit history or unrelated files.

Read initially only:
- `AGENTS.md`, `module5/hyperiso_patch_contract.py` (prewritten), `tests/test_module5_two_state_patch_contract.py` (prewritten).
- `scripts/zee_module5_hyperiso_probe.cpp`, `scripts/zee_module5_hyperiso_bridge.py`, `module5/HYPERISO_BRIDGE.md`, `module5/CONVENTIONS.md`, `module5/NATIVE_OPERATOR_MATCHING.md`, `validation/module5/hyperiso_bridge.json`.
- In external HyperIso, only pinned `WilsonInterface.h`, `WilsonMatchingPatch.h`, `BWilsonTHDM.cpp`, `WilsonManager.cpp`, `BWilsonGroup.cpp`, `BXsDecay.cpp` and any direct dependencies needed to build.
- Sources: HyperIso `v1.0.3` **peeled commit `09d26ac6e71d1528922097a896d15693589f636b`**; Misiak et al. arXiv:2608.29863v1 Eqs. (2),(4) at mu0=160 GeV; Florentino et al. arXiv:2106.08332v1 charged mixing Eq. (62)-(63); no broader literature hunt.

## 0. Prewritten test contract / build
The Python contract produces explicitly signed C7/C8 BSM LO contributions, each with two state components, from the frozen validated `module5.bsgamma_lo.compute`; inputs include TWO charged masses, beta ANGLE, gamma ANGLE, matching-scale-renormalized MSbar top mass and mu_match. It is a conditional coefficient payload, **not a physical prediction**. Fix actual scaffold bugs only after independent checks; do not claim prewritten tests pass until actually run.
Run:
```bash
python -m unittest discover -s tests -p 'test_module5_two_state_patch_contract.py' -v
mkdir -p validation/module5/local
python -m module5.hyperiso_patch_contract --input module5/example_bsgamma_input.json --output validation/module5/local/zee_patch_contract.json
```
Build/reference pinned HyperIso only in ignored local cache, preferably reuse the already built v1.0.3 binary if actually present. Check actual `git rev-parse HEAD`, release hash, and `hyperiso-ui --version`. An unavailable existing binary is not a failed physics test. **Do not rerun the expensive R1–R7 full reference suite** unless upstream content changed or a directly relevant regression occurs; Gate B already validated it.

## 1. Implement a minimal external C++ adapter (principal task)
Create a small self-contained `scripts/zee_module5_two_state_patch.cpp` and a narrow Python launcher (if useful) using **public existing** `WilsonInterface::addMatchingPatch` (or equivalent verified v1.0.3 public API) without editing HyperIso.
- Use **SM baseline plus BSM patches**, NOT built-in THDM BSM plus the same shifts. Add EXACTLY one additive patch for **C7 LO** and one for **C8 LO** (or independently justified per-state patches that sum exactly once). `contribution=BSM`, `order=LO`, `group=B`, explicit `q_match=160` for 2026 tests, and explicit `q_hadronic` for running tests. Input signed coefficients from the vetted contract. No arbitrary (\alpha_s/4\pi\) rescaling at LO. No C1-C6 additions.
- Verify the actual contribution semantics: at the matching scale `C_BSM^{patch} = Delta C^{Zee,LO}`, `C_TOTAL = C_SM + C_BSM` exactly once. Ensure model setup doesn't discard a BSM patch in SM mode; if it does, stop and document the supported alternative instead of forcing a silent THDM double count. Verify full complex `scalar_t` through a synthetic complex test, but **the physical frozen Type-II quark-sector C7/C8 are real up to CKM factoring**; do not invent Zee complex phases.
- At one-state `gamma=0`, compare signed C7/C8 patch vs the **native, separately executed Type-II THDM LO BSM calculation**, using identical `mt_MSbar(mu_match)`, `tanbeta`, scalar mass and matching scale. Test gamma=pi/2 with swapped physical masses. For nontrivial gamma/mH1/mH2, compare the patch's signed C7/C8 with direct independent summation of **two separate native THDM LO BSM results**, weighted by `cos²gamma, sin²gamma` (no direct Zee backend assumed). Test degeneracy, interchange, zero-doublet, heavy decoupling and sign-flipped ld controls.
- Test LO running via public `getFR` / requested basis: `TOTAL = SM + BSM` at low scale, confirm patch contributes (no silent drop); compare a synthetic linearity/additivity run with two separate scalar patches. Do not interpret low-scale running or order LO as a complete NLO/NNLO observable. Suppress unrelated SM-vs-2026 absolute-BR comparisons.
- Demonstrate a hard **double-counting trap** by proving native THDM BSM + patch produces two copies at gamma=0 and reject that configuration. Fail closed if matching scale differs, top mass definitions differ, or `CONTRIBUTION` is wrongly SM/TOTAL. Never infer the top running mass just from the user's illustrative `163 GeV`; preferably retrieve `mt_MSbar(160)` with the exact v1.0.3 QCDHelper used by its THDM matching, as Gate B did.

## 2. Distinguish the three claims
1. `HYPERISO_PATCH_INTEGRATION_PASS`: executable injection, same-source signed coefficient trace, and no double count, plus running/additivity tests.
2. `EXTERNAL_OPERATOR_CONVENTION_PASS`: requires independent pinned Misiak 2026 Hamiltonian/sigma/Fourier/operator insertion alignment or trusted external operator-level amplitude result; numerical THDM LO matching agreement, source editorial text, or trend sign alone **do not** establish this. It can remain `MATCHING_CONVENTION_UNKNOWN`.
3. `ZEE_B_TO_XS_GAMMA_PHYSICAL_PASS`: NOT part of this task. Do not calculate a full Zee BR, exclusion/allowed labels or a mass cut; HyperIso's R3 legacy SM baseline is not the Misiak 2026 SM baseline.

Only if a **new external operator-level proof is genuinely achieved** may a separately labeled 2026 `LINEARIZED_BSM_SCREEN_CONDITIONAL` be added with:
`10^4 BR = (3.54 +/- 0.14) - 8.51*DeltaC7(160) - 2.16*DeltaC8(160)`,
`BRexp=(3.49 +/- 0.19)*1e-4`, `Egamma>1.6 GeV`. Linear expansion omits quadratic NP and uncomputed NLO, and is NOT an exclusion/likelihood. Otherwise leave it `NOT_EVALUATED`. Do **not** apply single-Higgs Type-II 670 GeV exclusion to either Zee mass.

## 3. Validation evidence and completion contract
- Add narrow C++/Python regression tests for matching/running/double count and real two-state inputs. If compile impossible mark `HYPERISO_ADAPTER_RUNTIME_BLOCKED` with actual error; do not fabricate passed tests.
- Preserve original actual Gate B tests and evidence, ideally rerun just `test_module5_bsgamma_lo.py` and newly written scoped tests. Historical native-tree file `native_numerical.json` was local-only; its absent data is not a physics failure. If useful, **regenerate with genuine SARAH** on this checkout and validate source hashes against historical evidence; do not misreport regenerated data as restored byte-identical, and do not require that regeneration to run adapter tests.
- Write `module5/TWO_STATE_PATCH_AUDIT.md` plus `validation/module5/two_state_patch.json` with actual executable output, source SHA256, reference release, tests, quantitative residuals, status hierarchy, and explicit remaining physics barriers. Append new section to `validation/module5/STATUS.md`, preserving prior results and numeric evidence.
- Only commit scoped `module5/`, `scripts/zee_module5_two_state_*`, `tests/test_module5_two_state_*`, `validation/module5/` and `AGENTS.md`; keep logs, external clones/binaries, other local outputs ignored.
- Commit, `git push origin feature/zee-hyperiso-two-state-patch`; verify `git rev-parse HEAD` equals `git ls-remote origin refs/heads/feature/zee-hyperiso-two-state-patch`. Report commit SHA, URL, test totals, injection signs/sums, scopes and blockers, concise chat. `PUSH_BLOCKED` if push fails.

### Cost discipline
No whole-repository exploration, no source download when already pinned/local, no repetition of full native SARAH+LO kernel derivation, no new phenomenology scan. Avoid long Codex narrative.
