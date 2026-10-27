# Zee Module 5 Gate C1 — direct 2026 B -> Xs gamma EFT diagnostic and convention decision

## Scope
Work **only** on `feature/zee-2026-bsgamma-linear-diagnostic` in `aalida0/zee`, branched from `7a0509696779998dc2de737da330404c2d8c56dd`. This is a bounded route toward the phenomenological scan, **not another HyperIso matching-patch repair**.

Known evidence: Modules 0–4 frozen. Module 5: native SARAH charged-quark vertices, independent diagram-level signed LO C7/C8 under explicit conventions, and HyperIso Type-II same-scale/scheme LO matching agree; HyperIso v1.0.3 R1–R7 PASS. Previous C0 experiment proved HyperIso **SM mode forces BSM matching to zero**, while THDM+patch double-counts. Do not retry failed C0 using SM, THDM+patch, hidden subtraction, or patched upstream binaries.

**Freeze** `models/SARAH/ZeeTypeII`, Modules 0–4, `module5/bsgamma_lo.py`, `module5/hyperiso_patch_contract.py`, previous evidence, and HyperIso itself. Scope changes to source review, this Gate C1 diagnostic/tests, and its concise evidence only. Do not edit main or unrelated checkouts.

Initially inspect only `AGENTS.md`, `module5/bsgamma_2026_linear_diagnostic.py`, `tests/test_module5_bsgamma_2026_linear.py`, `module5/FLAVOR_2026_SOURCES.md`, `module5/NATIVE_OPERATOR_MATCHING.md`, `module5/HYPERISO_BRIDGE.md`, `module5/TWO_STATE_PATCH_AUDIT.md`, `validation/module5/{native_matching,hyperiso_bridge,two_state_patch}.json`. Read other source only to resolve a concrete convention ambiguity.

## Primary 2026 reference: no claim inflation
Misiak et al., arXiv:2608.29863v1 (2026-08-30), `https://arxiv.org/html/2608.29863v1`, Eq.(2) operators and Eq.(4) formula at `mu0=160 GeV`:
`BR(Bbar->Xs gamma) * 10^4 = (3.54 +/- 0.14) - 8.51 DeltaC7 - 2.16 DeltaC8`,
inclusive CP/isospin averaged `Egamma >1.6 GeV`. Experiment `(3.49 +/- 0.19) *1e-4`. The authors explicitly recommend LO new-physics coefficients as an approximation for small shifts, neglect `O(DeltaC^2)`, and mention higher-order NP/operators for refinement. Their 670 GeV 95% bound refers to a ONE-charged-state Type-II 2HDM with higher-order matching; **never apply to either individual Zee mass**.

The earlier Florentino/Romao/Silva arXiv:2106.08332v1 independently provides the two-state mixing-weighted matching structure; the 2017 general Zee constraints and 2021 cascade paper are priority novelty comparators later, not constraints to rewrite now. Pinned HyperIso is v1.0.3 peeled `09d26ac6e71d1528922097a896d15693589f636b`; don't combine its archived R3 BR baseline with Misiak's updated SM result.

## Task A: independent source-to-operator convention determination, **bounded**
1. Inspect only the pinned 2026 and 2021 B->Xs gamma operator/Hamiltonian definitions, their cited standard EFT convention if needed, and existing independent native amplitude proof. Trace exact sign and factor(s) of `H_eff=-4GF/sqrt(2)*Vtb Vts* sum C_i Q_i`, sigma^{mu nu}, field strength, L=-H, CKM rephasing, color, ordinary/effective C7,C8 shifts, Q7/Q8 chirality and the 160-GeV matching mass definition.
2. Test the independent Type-II limit and **the sign/trend of the 2026 paper's published 2HDM calculation**. A qualitative trend match is a cross-check, NOT full operator-level proof. If possible reproduce quantitative heavy-mass small-shift points from the published formula with clearly stated higher-order differences. Do not derive a 670-GeV two-state Zee cut.
3. Write a compact `module5/BSGAMMA_2026_CONVENTION.md` with the exact verification chain (equations, reference version, basis transformations, residuals) and classification: `EXTERNAL_CONVENTION_PASS` **only with an explicit independent operator-level normalization/source bridge**; otherwise retain `MATCHING_CONVENTION_UNKNOWN`. Do not perpetually demand unobservable global sigma sign if convention changes cancel everywhere: distinguish physical relative sign from notation choices in your audit. Source ambiguity should be stated precisely, not treated as a numerical failure.
4. **No arbitrary declaration of success:** if proof is insufficient, keep `UNKNOWN`, do not create a physical exclusion/allowed label. This task is not a new SARAH run or rederivation of the four kernels.

## Task B: implement/run conditional direct EFT computation (already scaffolded)
The prewritten `module5/bsgamma_2026_linear_diagnostic.py` and `tests/test_module5_bsgamma_2026_linear.py` use Eq.(4) **directly from verified two-state LO C7/C8**; they do not inject a BSM patch into HyperIso. Independently review and fix actual bugs before execution.
- Run `python -m unittest discover -s tests -p 'test_module5_bsgamma_2026_linear.py' -v`.
- Run `python -m unittest discover -s tests -p 'test_module5_two_state_patch_contract.py' -v`; run frozen Gate A `test_module5_bsgamma_lo.py` only if needed for regressions.
- Generate an actual input contract, with explicitly sourced matching mass at mu=160 (use the validated HyperIso helper/reference LHA if already available, otherwise a declared illustrative input):
```bash
mkdir -p validation/module5/local
python -m module5.hyperiso_patch_contract --input module5/example_bsgamma_input.json --output validation/module5/local/2026_contract.json
python -m module5.bsgamma_2026_linear_diagnostic --input validation/module5/local/2026_contract.json --output validation/module5/local/2026_conditional.json
```
- Demonstrate Eq4 zero-NP limit 3.54e-4, correct signs, separate C7/C8 terms, physical-state interchange, gamma limits, and scale=160 guard; reject duplicate keys/nonfinite/tampered contract, no silent top-mass scheme assumption.
- Crucial: label output `2026_EQ4_CONDITIONAL_DIAGNOSTIC_OPERATOR_MAPPING_UNCERTIFIED` until source-to-operator mapping genuinely passes. Even when it does pass, a linearized `screen` is **not** the full Zee BR or likelihood. Do not add a 95% CL exclusion, chi2, allowed label or arbitrarily chosen validity threshold; uncertainties 0.14/0.19e-4 are documented published values, not a correlated Zee-model NP uncertainty. Track uncomputed `O(DeltaC^2)`, NP NLO, mass matching choices and LEFT operator omissions.

## Gate C1 deliverables
Produce `module5/BSGAMMA_2026_CONVENTION.md`, `validation/module5/linear_2026.json`, and a concise appended section in `validation/module5/STATUS.md`, with exact status, sources, actual numerical diagnostic, source/input hashes, tests and remaining steps to have a **scan-ready** flavor filter. Report the failure of the HyperIso SM patch honestly and **do not spend this gate fixing it**. HyperIso v1.0.3 reference remains a matching cross-check.

Review success separately:
- `GATE_C1_NUMERICAL_DIAGNOSTIC_PASS`: source-locked algebra and tests run, but not a constraint;
- `EXTERNAL_CONVENTION_PASS`: only if the independent operator bridge actually proves it;
- `2026_LINEARIZED_FLAVOR_FILTER_READY`: only if convention, scheme, validity envelope, statistical prescription and NP errors are justified. This is NOT automatic from first two gates.

If no new operator source is found, declare uncertainty accurately and give a precise next action instead of embarking on another open-ended spinor/loop calculation. Do not regenerate old local-only SARAH output merely to increase test counts.

Commit scoped files, `git push origin feature/zee-2026-bsgamma-linear-diagnostic`, then verify `git rev-parse HEAD` equals `git ls-remote origin refs/heads/feature/zee-2026-bsgamma-linear-diagnostic`. Report exact SHA/URL, numeric results, tests, classification and blockers. Minimize Codex chat tokens. If push fails: `PUSH_BLOCKED`.
