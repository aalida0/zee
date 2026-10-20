# F5: 309 original Zee spectra, source-matched two-charged C7eff projector (NOT a branching ratio)

## Completed E7 inputs
User's E7 AF run finished 309/309; general Zee f/Y charged lepton width replacement lowered all 309 included-channel cascade proxies. The median changed 0.291223 -> 0.274934, a reduction of 5.59%. Six corrected HiggsSignals–cascade Pareto candidates:

| ID | E6 Delta chi2 (NOT a CL) | E7 included cascade proxy | H2->H1Z included fraction | H1->tb included fraction |
|---|---:|---:|---:|---:|
| B4_0017640 | -0.9041 | 0.366096 | 0.60844 | 0.99985 |
| B4_0003854 | 0.2868 | 0.522630 | 0.64235 | 0.97823 |
| B4_0003582 | 0.2967 | 0.530008 | 0.64295 | 0.99112 |
| B4_0004143 | 0.7709 | 0.591985 | 0.71423 | 0.99653 |
| B4_0004380 | 12.3113 | 0.604982 | 0.75171 | 0.99806 |
| B4_0002315 | 15.3385 | 0.621959 | 0.79058 | 0.99871 |

The values are partial-width/production proxies, NOT physical branching fractions or acceptance tests.

## Exact F5 calculation

F5 extends the existing rigorously source-pinned F4b Type-II matching and running audit to all 309 actual E7 spectra. It uses the SAME compiled SuperIso three-mode Wilson RG probe, its saved source/executable fingerprints and alpha_s(mu_b). **Before** the new 309 calculations it recomputes all eight historical Type-II single-charged controls at masses 300/580/670/1000 GeV and tanbeta 5.6/50 and checks six previously saved dipole projectors each.

F5 reads the original mH1, mH2, gamma and tanbeta for each original B4 Zee potential (quark doublet fraction weights cos^2(gamma) and sin^2(gamma)). It computes NP-minus-SM squared C7eff at LO and strictly first order in alpha_s, separating NLO high dipole and four-quark operator matching. The high-scale C4 contribution is kept, not discarded. Both exact coefficient order separation and source control closures are tested.

**Interpretation:** This is a *squared-dipole-only projector*, not a complete observable. The full inclusive B->Xs gamma branching ratio needs scheme-matched NLO/NNLO matrix elements, bremsstrahlung, power/EW corrections and a calibrated uncertainty likelihood. F5 NEVER declares any Zee point allowed/excluded, and the auxiliary delta chi2 is NOT a calibrated confidence level. The historical F3/F4b/F4c/EOS source audits do not solve this outstanding issue.

## One AF invocation

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
bash scripts/zee_gateF5_one_shot.sh
```

The runner checks E7 and F4b source files, runs seven F5 regression tests, closes eight historic Type-II source controls, computes original 309 Zee points and reports six corrected Pareto cases' signed strict C7eff dipole projectors.

Saved under `work/zee_F5_309_two_charged_C7eff_projector_20261020_v1/`:

- `F5_309_Zee_strict_dipole_projector_NO_BR.jsonl`
- `F5_309_HS_cascade_C7_dipole_NO_EXCLUSION.csv`
- `F5_E7_Pareto_C7_source_audit_NO_EXCLUSION.csv`
- `summary.json`, `manifest.json`

Existing E2–E7 source/output files remain read-only. F5 synthetic CI passed, but the actual full AF calculation has NOT been run as of this documentation commit.

## What would change the paper verdict

Need independent complete B->Xs gamma branching-ratio matching and likelihood; five-state HiggsBounds predictions with validated production cross sections and all charged/neutral widths; full LFV and neutrino likelihood; and global vacuum/threshold scheme. Until then, **no point can be certified experimentally allowed**. B4_0004143 remains the most attractive existing collider candidate for further verification, not a confirmed allowed benchmark.
