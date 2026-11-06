# 2026 published-NP route: finish the B→X_sγ constraint without rebuilding a precision flavor code

**Branch:** `research/zee-bsgamma-rate-validation`.
**Start commit:** `1c8860ae0e44156d9ba00e238c3706ea32c3b639`.
**Execution:** Ubuntu Codex. Read root `AGENTS.md` and this file before doing any work.

## Decision and scope

The previous independent physical-rate task finished **BSG_PHYSICAL_ACCURACY_BLOCKED**, with 20 actual EOS/SuperIso diagnostic cases and 22 tests. Do **not** repeat that unsuccessful published-single-Higgs benchmark search or attempt a third large rate reconstruction.

Use the **2026 published linear new-physics formula** as the primary, rigorously labelled **LO-NP diagnostic**. Determine whether a source-supported *quantitative remainder/validity domain* exists that could elevate a subset of Zee points to a defensible B→Xsγ scan constraint. If the requisite source information is unavailable, prepare a specific brief request to the paper's authors and stop cleanly. This is **not** permission to promote a heuristic old-code envelope to a 2026 confidence interval.

Target: **CP- and isospin-averaged inclusive** B→Xsγ with `E_gamma>1.6 GeV`, for **real** Type-II Zee quark couplings with coherent two-charged-scalar matching. Do not apply the one-charged-scalar 670 GeV bound separately to each Zee charged mass.

## Published starting point (checked against arXiv:2608.29863v1, p.4, Eq.4)

At the **high matching scale** `mu0=160 GeV`, the paper states

```
10^4 * BR(B→Xsγ) = (3.54 ± 0.14) - 8.51 * DeltaC7 - 2.16 * DeltaC8
```

Here `DeltaC7` and `DeltaC8` are **LO (alpha_s^0) new-physics matching coefficients** of the ordinary, unprimed electromagnetic/chromomagnetic operators in the paper's Eq.(2), with the sign convention fixed by its weak Hamiltonian. **Quadratic terms are explicitly omitted**. The formula does **not** provide a numerical finite coefficient-validity range, a quadratic-response tensor, a model-dependent NP theory uncertainty, or an NLO/NNLO NP prediction. The one-Higgs Type-II 670 GeV mass limit in the *same* letter uses a **more refined higher-order calculation**, not this linear expression by itself. The 2026 paper quotes `BR_exp=(3.49±0.19)e-4` and `BR_SM=(3.54±0.14)e-4`; the latter's uncertainty describes its SM calculation, not all Zee NP uncertainties. Cite exact versions, source locations and relevant words precisely; check for newer revisions before running.

**Critical reuse**: `module5/BSGAMMA_2026_ACCURACY.md`, `module5/BSGAMMA_SCAN_TRIAGE.md` and existing C1 scripts already implemented/audited Eq.(4), its ordinary/effective convention, a 27-point diagnostic and alternative pull definitions. Read that evidence and **reuse**, not independently regenerate an allegedly new result. Frozen BMU high-scale matching lives in `scripts/zee_module5_bmu_nlo.py`. The standalone EOS native full vector, original SuperIso and partially matched comparison evidence are `research/bsgamma_rate_validation/{RESULT.md,BRIDGE.md,FINAL_VALIDATION.md,final_results.json,bridge_results.json}`. All of this is read-only.

## Stage A — freeze Eq.(4), signs and controlled model inputs

1. Verify paper Eq.(2), Eq.(4), the `160 GeV` matching scale, `10^-4` units and photon cut using authoritative source text (not a web snippet). Record page, equation, version/date and exact coefficients. Cross-check the existing C1 tests/fixtures. Ensure `DeltaC7/8` enter **without** a factor `alpha_s/(4pi)`; NLO `DeltaC7^(1), DeltaC8^(1)` and `C4^(1)` must **not** be silently added into Eq.(4).
2. For each scalar, reuse the frozen LO ordinary matching at a consistent `mu0=160 GeV`; combine `DeltaC_i = cos²γ DeltaC_i(H1) + sin²γ DeltaC_i(H2)` **at the Wilson-coefficient level**, then evaluate the published linear equation once. Check all endpoints, equal-mass, interchange and decoupling.
3. Build one small strictly read-only **audit adapter** in `research/bsgamma_rate_validation/`, not in D14/Module5. Return `BR_linear_2026`, the actual `DeltaC7,DeltaC8` and their signed separate contributions, source and input hashes, `status=DIAGNOSTIC_ONLY`, `exclusion=None` by default. Preserve existing Module5 outputs; no new global scan.
4. Include a finite frozen grid with at least `mH1={300,550,900} GeV`, `mH2={700,900,1400} GeV` (only physically ordered pairs), `tanbeta={2,5.3,50}`, `gamma={0,1.09,pi/2}`, plus a few preexisting D14 points if fully specified. Do not change model conventions or fit input masses to preferred results.

## Stage B — the one missing piece: **credible 2026 remainder/accuracy domain**

1. Look for an *existing* author-maintained numeric response or explicitly documented approximation error for generic NP `DeltaC7, DeltaC8` (including signed, joint quadratic contributions) at `mu0=160`, plus NLO `DeltaC4^(1), DeltaC7/8^(1)` contributions and their truncation/parameter/resolved-photon uncertainty. Prior literature audit in `module5/BSGAMMA_SCAN_TRIAGE.md` found no ready-to-run 2026 tensor; do not repeat the same web review without new evidence. Check journal updates, revised arXiv versions, ancillary data, authors' linked code and official follow-up only. Log source-qualified positive and negative findings and exact numerical definitions.
2. Use EOS 1.0.21 and SuperIso v5.0 strictly as **legacy diagnostic** cross-checks. At matched high-scale `DeltaC7, DeltaC8`, measure their *separate* local linear slopes by a symmetric finite difference and their `C7²,C7*C8,C8²` response on a small sign-symmetric probe grid. Keep both coefficients' **joint** response. Distinguish an ordinary coefficient at `160 GeV` from a low-scale total coefficient. Ensure a consistent NP matching order for each comparison; explicitly record differences in SM normalization, photon cut, QED, RG, matrix elements, quadratic truncation and hadronic prescription. Do **not** subtract or rescale their SM baselines to force the 2026 Eq.(4) intercept. Do **not** treat EOS–SuperIso disagreement or a fit to their curvature as a validated 2026 uncertainty, and do not call code agreement a published-rate benchmark.
3. For any proposed finite accuracy domain or error envelope, require **source-supported and independently tested bounds** for the *complete omitted contribution* over that domain (quadratic NP, NLO matching / C4, additional operators, coefficient-dependent nonperturbative effects). An envelope from one or several legacy codes alone does NOT certify the 2026 prediction. State why each omission can be neglected or how it is bounded and carry correlations appropriately. Hold out separate points not used to set boundaries.
4. As a qualitative consistency check only, compare the trend in Type-II `tanbeta=50` with the paper's refined single-Higgs results. **Never** demand that the LO linear equation reproduce the paper's `670 GeV at 95% CL` NNLO mass limit. If available, reproduce an independent author-supplied *linear-formula* test point instead.
5. If the public source lacks enough input to justify a remainder, mark `VALIDITY_DOMAIN_UNKNOWN`. In that case write `AUTHOR_QUESTION_DRAFT.md`: a **short, polite, technically detailed unsent draft** to the authors asking about coefficient range of validity, unprimed high-scale normalization, a full quadratic response/table or executable for `DeltaC7/8`, treatment of NLO `C4/7/8`, and a conservative error prescription for two coherent Type-II charged Higgs contributions. Explain this is for a Zee charged-Higgs phenomenology scan. Do not invent an email address or contact/send anything.

## Stage C — statistics and safe interface

Only **if** Stage B provides a supported finite validity domain and defensible NP uncertainty, implement a research-only two-sided confidence test with sources, correlations, and 95% CL convention; use distinct labels `PASS`, `FAIL`, `UNKNOWN`, not an unjustified `1.96 sigma` from `sqrt(0.14²+0.19²)` alone. Confirm it against known limits, including zero NP. State whether confidence is conditional on the linearized approximation. Do not make a global scan.

If Stage B remains **UNKNOWN**, still save the diagnostic rates and the exact experimental/theory measurements, but return `classification=UNKNOWN` and `exclusion=None` for *every* point; do not implement an operative scan filter, and do not alter D14 accepted-point logic. A point's linear central prediction appearing inside an experimental interval does **not** validate the approximation or make it allowed.

## Outputs and stop rule

Work only under `research/bsgamma_rate_validation/`. Create:
- `M2026_ROUTE_RESULT.md`: exact source eq/conventions, what C1 already established, new diagnostics, finite-grid summary, coverage/uncertainty status, and a clear paper-safe statement.
- `m2026_route_results.json`: reproducible inputs, source hashes, Wilson vectors, linear prediction, optional legacy response diagnostic, source version and explicit `UNKNOWN` where applicable.
- A small adapter and targeted tests for signs, units, gamma identities, no-NLO-injection, zero-NP, and `UNKNOWN` handling. Reuse rather than edit historical inputs/tests.
- `AUTHOR_QUESTION_DRAFT.md` only if the remainder cannot be independently certified.

Final classification must be exactly one of:
- `M2026_RESTRICTED_FILTER_VALIDATED`: only if supported numerical coefficient-range and complete remainder/error bounds were actually obtained and independently validated. Specify the **finite** supported domain, otherwise do not use this label.
- `M2026_DIAGNOSTIC_ONLY_AUTHOR_INPUT_REQUIRED`: Eq.(4) implemented and tested, but no source-supported finite remainder/NP uncertainty; author draft available.

Do not claim full NNLO Zee accuracy or a universal mass bound. Do not modify Modules 0–14, other branches, prior audits, published numerical evidence or the existing D14 scan. No new two-loop integrals, ADMs, or major C++ backend projects; no costly large grid. Execute focused tests and `git diff --check`, then commit and push with a report of the exact result.

**Bounded stop condition:** after one focused source/ancillary check and a finite legacy comparison, if no quantitative author-published remainder or executable is located, write the author question and stop. No speculative repeated effort.
