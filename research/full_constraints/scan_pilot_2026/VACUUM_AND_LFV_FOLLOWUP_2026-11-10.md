# Post-scan physics follow-up: 400-proposal Zee cascade pilot

**10 November 2026. New objective: re-prioritize candidates on LFV, not just cascade branching fraction.**

## 1. Source-locked independent bounded vacuum follow-up

Five original proposal IDs `31,112,284,320,394` were copied exactly from the real 400-point manifest into `selected_five_vacuum_inputs_400.json`. Exact scalar SHA256 comparisons now pass; the file preserves the distinction between Python JSON binary64 `125.0` and JSON integer `125` in original cards (first CI trial correctly rejected the type-mismatched preliminary copy).

Original executed scan:
- source commit `c194bb9018801b1a6881f22134e0650b1fdccae7`;
- original manifest SHA256 `afa92f0e5d8afa56db976ff4158cc9971319419595574ef09be3f6d0d545ed45`;
- conditional dataset SHA256 `52bfe78aecf28bc7c4dc299bc49a74c77e1cf7a0c51c54746d541ac6794b7639`.

Independent execution: [GitHub Actions 42845870480](https://github.com/aalida0/zee/actions/runs/42845870480), five source-provenance tests PASS.

Code uses exactly the original Module1 ten-real-field Zee potential, independently reconstructed tree parameters, D10 **exact rational sufficient** global-minimum certificate and the complete Gram-invariant 5D bounded SLSQP orbit search. Every potential deeper stationary minimum needs an independent 80-digit polynomial-polished full-transverse-Hessian certificate before a **FAIL** is declared. Numerical non-discovery **never implies PASS**.

| Candidate ID | Number of minimizations incl. 7 mandatory starts per seed | D10 exact certificate | Smallest credible ΔV/v⁴ | Verified deeper minimum | Final tree vacuum assessment |
|---|---:|---|---:|---|---|
| 31 | 55 | no | -1.30e-16 | none | **UNKNOWN** |
| 112 | 55 | yes | +1.62e-17 | none | **PASS** |
| **284** | **302** (199+103, two independent seeds) | no | -1.46e-16 | none | **UNKNOWN** |
| 320 | 55 | no | 0 | none | **UNKNOWN** |
| 394 | 55 | no | 0 | none | **UNKNOWN** |

All four UNKNOWN certificates fail because the full-domain residual Gram matrix cannot be proven positive-definite. This is a limitation of the **sufficient ansatz**, not a detected charge-breaking minimum. No finite number of SLSQP starts can promote UNKNOWN to PASS.

The full polynomial and minimized-run evidence is preserved in the Actions artifact named `zee-400-pilot-five-candidate-bounded-vacuum-no-globality`, not as a modified original worker gate.

## 2. Previously overlooked LFV problem in the completed pilot

The original 400-proposal **conditional_dataset.json.gz** already contains the exact Module14/Module4 partial complex `C_L,C_R` and `mu_to_e_gamma.partial_BR` for all 20 neutrino family rows. These were diagnostic-only and **not used to veto** the original scan. Comparing to the saved `MEG II 90% CL limit 1.5e-13` reveals that all five surviving scalar candidates have **very large** included LFV subsets.

| ID | min partial BR(mu→eγ) among 4 original families | max partial BR | min partial / exp limit | minimum required destructive amplitude magnitude |
|---|---:|---:|---:|---:|
| **284** | 1.442409933e-7 | 5.977836995e-7 | 9.61607e5 | 99.89802% |
| 31 | 3.359197743e-7 | 1.005090329e-6 | 2.23947e6 | 99.93318% |
| 112 | 1.102223372e-5 | 2.305135321e-5 | 7.34816e7 | 99.98833% |
| 320 | 3.943471632e-7 | 1.547422705e-6 | 2.62898e6 | 99.93833% |
| 394 | 2.220437843e-6 | 1.000295102e-5 | 1.48029e7 | 99.97401% |

The amplitude statement follows from the triangle inequality:
`||C_missing|| >= ||C_retained|| - sqrt(BR_limit/N)`, with `BR_partial=N ||C_retained||²`. This is a **necessary missing-amplitude size**, not proof that cancellations are forbidden. Full Zee LFV is still UNKNOWN because uncomputed terms can interfere. However, these specific **random** neutrino families are unconvincing as publishable allowed benchmarks without a justified texture or extreme cancellation.

In particular **ID 284 is not presently a good publication benchmark**, notwithstanding `BR(H2→H1Z)≈0.687` and an approximately compatible B-decay diagnostic.

## 3. Physics-directed correction to scan strategy

The original correlated scalar scan was working correctly. The problem is the **separate, unconditioned inverse-neutrino family sampling**, not the scalar/worker/collector infrastructure. The D14 generator draws a random null-cone parameter, logarithmic F scale, two Majorana phases, four complex homogeneous D coefficients, then solves the neutrino mass equation. Algebraic neutrino closure does not imply LFV compatibility.

Next scientifically useful test: **fixed-scalar flavor-family sampling** on the most relevant scalar points using **new, deterministic family IDs** and unchanged `module14.scan.neutrino_input` / `module14.scan.evaluate_family` and unchanged diagnostic `module14.lfv.evaluate_family`. Record the full partial-BR distribution, exclusion-materiality ratio, perturbativity and neutrino closure, but do not introduce a hard full-physics LFV veto. If unconditioned sampling remains many orders above the MEG II limit, design a texture-aware proposal algorithm explicitly constrained by LFV-amplitude geometry (with independent validation of statistical sampling bias).

Under no circumstance reinterpret the fixed 400-proposal scan as having 5 fully allowed points or multiply its conditional survivor yield into a discovery/exclusion sensitivity.

**Current gates: SCALAR_AND_NEUTRINO_PILOT_COMPLETE; BOUNDED_VACUUM_SEARCH_COMPLETE_WITH_FOUR_UNKNOWN; FIVE_CURRENT_RANDOM_FAMILIES_LFV_HIGHLY_TENSIONED; PHYSICAL_GLOBAL_ACCEPTANCE=null.**
