# F6: Full legacy inclusive B->Xs gamma branching ratios for all 309 Zee spectra

## Completed F5 interpretation (AF, 20 October 2026)

The F5 user execution log confirms 309/309 original Zee two-charged source spectra evaluated and all 8 F4b Type-II source controls reproduced. The strictly truncated squared-C7eff NP-minus-SM source projector is POSITIVE for all 309:
min 0.015360264347, median 0.021398021453, max 0.032132139802.
The median untruncated LO projector is 0.031226477 (from parsing all 309 stdout rows). Median fractional LO->strict LO+NLO reduction per point ~31.40%.
Primary B4_0004143: Q7_LO=0.027271887, Q7_LO+NLO_TRUNC=0.018545002, high-scale NLO C4 coefficient 0.00099835159. The six corrected E7 Pareto candidates have positive projector responses. These dimensionless squared-dipole combinations are NOT BR(B->Xs gamma) and cannot support any 95% CL acceptance.

## What F6 actually computes

The repo already contains a historically AF-validated **A1U original SuperIso v5 full LEGACY inclusive two-charged state observable** for (mH1,mH2,gamma,tanbeta)=(300,700,1.089,5.597170833164245):
BR=0.0003931195407821, gamma=0 0.0004511530310543,
gamma=pi/2 and degenerate masses 0.0003779342973212. SM baseline original A1R 0.0003382457724.

A1U is more than a C7-only approximation. It combines source-pinned LO/NLO/NNLO high-scale Wilson vectors for H1 and H2, includes the primed coefficients, evolves one coherent total low-scale vector, then computes the full **old vendor** bsgamma(Egamma>1.6GeV) inclusive matrix-element/bremsstrahlung/EW/power kernel. Crucially the vendor bsgamma_Ecut helper itself reloads C7/C8 high-scale matching in its nonperturbative and EM terms. The audited unchanged A1U C driver wraps this nested helper and supplies the exact same mixed high-scale matching, verifies one wrap per call, and requires three observable contexts to agree to 2e-12, plus high-scale RG context independence.

F6 reruns the historical A1U original input and all 3 endpoint/degenerate controls BEFORE the 309-model campaign and refuses a changed source, compiled vendor static library, prior A1U/A1R result, or mismatched E7/F5 source rows. F6 compiles the SAME historical C driver/library into a new work output; it never modifies SuperIso source or previous work. The doublet-quark weights are cos^2(gamma) and sin^2(gamma) as required by the original Type-II quark Yukawa assumption.

Every one of the 309 model C evaluations is parsed with the original strict A1U parser, which checks exact input values, high-scale matching coefficients, charged mixing unitarity, low-scale RG closure and the internal helper model-context test. It saves the actual full legacy inclusive BR and corresponding SAME-kernel SM reference, and separately reports the 2026-unvalidated status. If any coefficient/context/source or source-result closure fails, the run exits nonzero and writes an error JSON.

**This is not a modern 2026 NNLO observable**: the historical SuperIso SM baseline 3.382e-4 differs from 2026 updated Misiak et al. arXiv:2608.29863 SM central 3.54e-4 by ~4.45%. Differences in perturbative order, scale, electroweak inputs, power corrections, and theory covariance preclude simply adding a legacy NP BR shift to a newer SM central value and calling it a fully matched modern model prediction. No 95% CL likelihood, ALLOWED or EXCLUDED model point is produced.

## One AF invocation

After pulling the existing feature branch, run:

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
bash scripts/zee_gateF6_one_shot.sh
```

This single shell script checks E7/F5/legacy A1U/A1R/A1M paths, runs A1U and F5 regression suites plus 7 synthetic F6 tests, recompiles historical SHA-matched C driver, re-evaluates all four A1U historical controls, then runs 309 original Zee spectra.

Output: `work/zee_F6_309_two_charged_full_legacy_bsgamma_20261020_v1/`.
- `F6_309_legacy_two_state_BtoXsgamma_NOT_2026_EXCLUSION.jsonl` - complete per-point A1U physical legacy source diagnostics
- `F6_309_legacy_BR_HS_cascade_NO_CL.csv` - original 309 rows joined to HiggsSignals, E7 included cascade and F5 dipole
- `F6_E7_Pareto_legacy_BR_NO_CL.csv` - original six E7 Pareto priority cases
- `summary.json`, `manifest.json` - complete source provenance including compiled driver SHA.

Tests are source-safe via `.github/workflows/f6-legacy-br-source-tests.yml`; the actual AF physics data and SuperIso source binary are NOT available to GitHub CI.

## Scientific decision after F6

If legacy inclusive BR shifts turn out large at all six high-cascade Pareto points, **this severely challenges** an allowed high-cascade interpretation, even if not a calibrated exclusion. If some points remain close to the SM baseline, prioritize them for up-to-date independent Wilson matching, complete 2026 NNLO inclusive rate treatment, profiled SM+experiment errors, and heavy scalar direct searches. Do not conflate signed squared C7 projector with the inclusive BR and do not infer 2026 exclusion from a legacy 2012/5.0 normalization. The full model still requires HiggsBounds production and neutral/charged widths, LFV Barr-Zee and mu-e conversion, neutrino likelihood and rigorous global vacuum.

**At implementation time the 309 AF F6 numerical run is not executed. No numerical F6 predictions are invented.**
