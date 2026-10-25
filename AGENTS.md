# Zee Module 4 — omission sensitivity triage

## Branch and scope
Work exclusively on `feature/zee-module4-omission-triage`, forked from verified Module4 commit `231e58fc35a7ea26d6f04f4735f8e9a197f1b6d3` in `aalida0/zee`. This is a small, standalone Module4 diagnostic, NOT a new LFV physics calculation or a complete two-loop prediction.

Read first only: `scripts/zee_omission_triage.py`, `tests/test_zee_omission_triage.py`, `module4/interface.py`, `module4/amplitudes.py`, `module4/example.json`, `module4/MATCHING_AUDIT.md`, `validation/module4/STATUS.md`. Inspect other files only for specific blockers.

## Frozen foundations
Do not change `models/SARAH/ZeeTypeII/`, Modules 0–3, any existing Module4 physics, kernels, schemas, tests, or their validation records. Keep the fixed dimension-GeV^-2 dipole `C_L,C_R` convention. The Wgamma candidates remain excluded: their signed matching is not physically validated. Do not insert guessed W, Zgamma, or arbitrary other amplitudes into coherent rates. Do not infer LFV allowance, exclusion, or global benchmark viability.

## Required task
The code and independent mathematical tests are ALREADY written. Audit them for correctness, fix bugs only when justified, and execute:
```bash
python -m unittest discover -s tests -p 'test_zee_omission_triage.py' -v
mkdir -p validation/module4/local
python -m module4.interface --input module4/example.json --output validation/module4/local/triage_input.json
python scripts/zee_omission_triage.py --input validation/module4/local/triage_input.json --output validation/module4/local/triage_output.json
```
For each of the three channels verify reproduction of signed complex included amplitudes, norm `||C||`, cancellation index `sum||C_i||/||sum C_i||`, and triangle-inequality sharp conditional ranges for `||Delta_missing|| <= b`. The diagnostic fractions 0.05/0.1/0.25/0.5/1 times the largest included component are **purely hypothetical budgets**, NOT upper bounds, numerical uncertainty estimates, or physical estimates of Wgamma. Test phase rotations, anti-alignment, large cancellation, zero included amplitude, invalid JSON, provenance, and fail-closed preservation of the excluded-W ledger. The result cannot by itself establish whether physical omitted Wgamma is small.

Write `validation/module4/OMISSION_TRIAGE.md` with brief mathematics, actual outputs, interpretation, provenance and a prioritized recommendation for the next *physics* milestone. Write concise `validation/module4/omission_triage.json` with verified summary results, source SHA256 and an explicit `DIAGNOSTIC_ONLY` status. Prefer real baseline run; optionally add NO/IO witness results if straightforward without rerunning the neutrino fit. Keep huge logs/raw inputs ignored locally. No speculative gauge matching or literature expedition.

## Delivery
Only commit scoped triage files and the task-specific AGENTS.md. Run genuine tests; include failure details if blocked. Commit, `git push origin feature/zee-module4-omission-triage`, and verify local `git rev-parse HEAD` equals remote `git ls-remote origin refs/heads/feature/zee-module4-omission-triage`. Report exact commit SHA, URL, tests, diagnostic findings, and unresolved physics. No local-only completion claims. Minimize token use; report concisely.
