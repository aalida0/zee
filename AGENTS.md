# Zee Project — D0 coherent scalar–neutrino–LFV–flavor pilot (NOT an accepted scan)

## Target / repository / local directory
Work only on branch `feature/zee-coherent-scan-pilot` in `aalida0/zee`, parent SHA `6cafa9c37baea9ba3228e1d7fd58fd048cc3e10a`. Follow the user's convention: **new task directories must live inside `~/zee/`**, preferably `~/zee/workspaces/zee-coherent-scan-d0`. If `~/zee` itself is a Git checkout, avoid altering its tracked files and keep the nested clone ignored in the parent `.git/info/exclude`. Never overwrite any prior working branch.

**Scientific objective:** Prove that one *identical*, provenance-bound frozen Module 1 scalar input can feed Module 2 inverse neutrinos, Module 3 scoped LFV and Module 5 2026 *exploratory* B->Xs gamma, without independently inventing a second set of masses/beta/gamma. This is a minimal end-to-end **candidate architecture**, not an allowed/excluded scan or complete LFV/flavor test. A future *true* scan needs physically selected scalar/neutrino fit points, controlled W-gauge LFV, constraints, and collider processes. Do not enlarge scope into physical exclusion or detector simulation.

Read first only:
- `module6/coherent_pilot.py`, `tests/test_module6_coherent_pilot.py` — prewritten **unexecuted** scaffolding.
- `module3/example.json`, `module3/interface.py`, `module3/input.schema.json`.
- `module2/interface.py` for scalar-provenance hashing.
- `module1/scalar_constraints.py`, `module1/README.md` (scalar gate assessments).
- `module5/bsgamma_2026_linear_diagnostic.py`, `module5/hyperiso_patch_contract.py`, `module5/BSGAMMA_SCAN_TRIAGE.md`.
- `validation/module1/STATUS.md`, `validation/module2/STATUS.md`, `validation/module3/STATUS.md`, `validation/module4/STATUS.md`.

Everything preexisting (frozen SARAH, Modules 0–5, tests, previous evidence and original branches) is READ ONLY. Create/change only the new Module6 pilot, its new tests/audit, `validation/module6/`, and AGENTS.md if necessary. No edits to upstream HyperIso. Avoid global repository exploration, old full test suites, full R1–R7, SARAH regeneration or the C0 broken patch.

## Known independently established physics and limitations
- Module 1: reconstruction/BFB sufficient certificates, unitarity and scalar EWPO validate the declared computations. A numerical vacuum search is **not a global proof**. Its pipeline never declares global allowed.
- Module 2: full finite one-loop neutrino reconstruction/inverse family supported; authentic official NuFIT 6.1 profile source still missing. An inverse target match is not an experimental NuFIT likelihood.
- Module 3: scalar one-loop LFV, tree subsets and charged-lepton Higgs widths computed, but **COMPLETE_LFV=false**, no experimental acceptance. Exact one-loop completion and missing terms persist.
- Module 4: fermion/photon and charged-scalar/photon Barr–Zee parts validated; **Wgamma gauge completion unresolved** and no complete physical LFV prediction. This pilot does **NOT** silently include Module4 two-loop parts; it labels them NOT_EVALUATED. A later pass can bind a complete Module4 input/output explicitly.
- Module 5: LO+NLO signed C7/C8(+C4 NLO) matching against native/independent BMU PASS within retained top/ms=0 scope. Source-locked 2026 Misiak Eq.(4) linear diagnostic `mu0=160` available, **NOT a validated physical BR, statistical exclusion or full model-acceptance**; C3 quadratic response not available. Illustrative flavor pulls cannot authorize any CL.
- Single Type-II 2HDM charged Higgs 670 GeV lower bound from Misiak 2026 must NEVER be imposed on either Zee mass separately. Do not call exploratory points viable. Unknown gates remain UNKNOWN.

## D0 task: one real coherent point, with tests and evidence
1. Independently review `module6/coherent_pilot.py` and `tests/test_module6_coherent_pilot.py`. Fix actual bugs. Production pilot must take only a **full Module3 input** (Module2 input inside, canonical SHA-bound Module1 scalar input) plus explicitly sourced `mt_MSbar(160)` from reference LHA SHA256 `984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374`; reference mass `163.96892236746697 GeV`. Do not automatically assume top mass or remap quark schemes. Derive `mH1,mH2,beta,gamma` exclusively from the SAME validated bound scalar record.
2. Run REAL code for the committed `module3/example.json` NO witness: scalar `module1.scalar_constraints.evaluate`, the frozen `module3.interface.evaluate` (which runs Module2 inverse), and `module5.bsgamma_2026_linear_diagnostic.run_contract` using the derived scalar variables. Inspect every status: a Module1 gate FAIL is a scalar-gate FAIL, NOT overall global exclusion; UNKNOWN remains UNKNOWN. Module3 radiative rates are scalar-one-loop approximations, not full LFV rates. Flavor is a linear conditional result; do not assign an experiment classification. Module4 is not computed in this pilot. The result must always set `global_zee_acceptance=null` and `constraints_complete=false`.
3. Run `python -m unittest discover -s tests -p 'test_module6_coherent_pilot.py' -v`. Mock-only tests are structural, NOT sufficient: run the actual end-to-end CLI and add at least one independent integration test or cross-check of physical mass/beta/gamma and per-sector hashes. Use this command (replace only validated paths if needed):
```bash
mkdir -p validation/module6/local
python -m module6.coherent_pilot \
  --module3-input module3/example.json \
  --mt-MSbar-160 163.96892236746697 \
  --reference-lha-sha256 984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374 \
  --output validation/module6/local/coherent_NO.json
```
4. Falsifying controls: scalar input modified without hash update is rejected; matching-scale mismatches or unsupported data types fail; scalar/LFV benchmark IDs mismatch rejects; changing scalar source shifts the flavor masses **only if** its canonical input SHA is recomputed correctly; demonstrate the absence of global viability and experimental comparisons. A heavy scalar numerical vacuum run may be slow; no shortcut may silently skip evaluation and still declare gate PASS. If resource unavailable, `D0_END_TO_END_BLOCKED` with exact command/error; mock tests do not rescue it.
5. Optional second IO witness **only if** an existing complete frozen IO Module3 input is readily available and hashes reproduce. Do not invent a second neutrino fit or mutate its scalar record. One genuine NO end-to-end execution suffices for this pilot.

## What to deliver
- `module6/COHERENT_PILOT_AUDIT.md`: actual supported gates, status table, signed flavor output and intermediate scalar/LFV values, hashes, explicitly missing Wgamma/other LFV, vacuum/global fit/statistics, reproducible command. Explain why all statuses are NOT an accepted point.
- `validation/module6/pilot.json`: compact actual numeric result, source hashes, tests, the real run's output digest, code versions, and `global_zee_acceptance=null`.
- Optional brief `module6/README.md` for API usage. Local full outputs/logs remain ignored under `validation/module6/local/`.
- Suggest future **actual scan design**: an explicit scalar sampler, NO/IO neutrino inverse-family exploration with complex Yukawas, consistent per-point constraints and benchmarks, prompt collider observables, with a three-valued `PASS/FAIL/UNKNOWN` gate. Distinguish a documented exploratory channel correlation from an actual discovery/exclusion prospect. Do not implement broad scan or claim EPJC novelty now.
- Separately recommend asking the 2026 (B\to X_s\gamma) authors for released coefficient-to-rate numerical response and input card. No additional 2026 nonlinear-rate code without data; do not repeat C3's no-go search.
- Run `git diff --check`; commit only scoped Module6/tests/evidence and optionally AGENTS; `git push origin feature/zee-coherent-scan-pilot`; verify `git rev-parse HEAD` exactly equals `git ls-remote origin refs/heads/feature/zee-coherent-scan-pilot`. Report SHA, URL, tests, real output and blockers in minimal chat text. Push failures `PUSH_BLOCKED`.
