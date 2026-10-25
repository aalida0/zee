# F24 — Correct F23 two-state HyperIso SM subtraction (same original LHA)

**Motivation, 2026-10-25:** The actual 157 F23 two-state legacy higher-order observable outputs and F23b real 193-trace + 18 unmodified Type-II native comparisons ALL passed. Crucially, however, the printed R3 SM reference 0.00032967 comes from upstream `sm_reference.flha` whereas every F23 Zee spectrum uses the 2HDMC `thdm_reference.lha` SM inputs, rewritten ONLY in charged mass and Type-II quark parameters.

The two original SLHA reference inputs **are not the same**:

| Input | tagged SM reference | tagged THDM reference |
|---|---|---|
| `SMINPUTS[1]`, inverse electromagnetic coupling | 127.930 | 137.036 |
| `SMINPUTS[3]`, αs(MZ) | 0.1180 | 0.1179 |
| `SMINPUTS[5]`, mb(mb) | 4.183 | 3.88454248 |
| `SMINPUTS[6]`, mt pole | 172.57 | 173.34 |

Therefore the superficially tempting subtraction
`BR_Zee(F23) - 3.2967e-4` is **not a same-input NP-only ΔBR** and must not appear as a physical constraint or confidence interval. The old-HyperIso R3 value remains a tagged regression only.

## Single large F24 native re-evaluation, not a scan

F24 takes the intact on-disk real F22/F23/F23b outputs, authenticates their exact SHA provenance, verifies 193 physical native calls and prior 18 unmodified Type-II endpoint comparisons, and invokes the previously compiled **unmodified HyperIso v1.0.3** CLI in explicit `--model SM --spectrum true --order NNLO` mode on the **same 157 original F23 generated THDM LHA input files** used in the Zee 157 native runs. The model is explicitly SM so no Type-II charged contribution enters, while nuisance masses, couplings, photon cut and inputs are preserved.

It computes:
\[
\Delta\mathrm{BR}^{\text{historical scheme}}_{Zee,i}
 = \mathrm{BR}^{\text{HyperIso THDM+Zee}}_i
 - \mathrm{BR}^{\text{HyperIso SM, SAME exact LHA}}_i,
\]
then checks that the calculated SM observable is invariant (numerical tolerance) under all 157 changes to BSM mass, tanβ and YU/YD. Any significant sensitivity to BSM parameters is a **hard STOP** indicating SM-model-selection/source contamination. The 157 source spectra (and their SHA-256) remain unchanged.

One diagnostic comparison per benchmark uses the *existing* independently computed F19d+Misiak 2026 Eq.4 LO-linearized NP response, but **the two contributions are not asserted to be perturbatively/schematically equivalent**. The report records signs/ratios solely to prioritize future matching-scheme work; no 2026 correlated uncertainty, experimental exclusion, or model allowed label is produced.

The current Misiak et al. (arXiv:2608.29863) reports
`BR_SM=(3.54+-0.14)e-4` and `BR_exp=(3.49+-0.19)e-4`
for `Egamma>1.6 GeV`. We deliberately **DO NOT** add the F24 historical-scheme ΔBR to the Misiak 2026 central prediction and call it NNLO. A validated cross-scheme operator/observable response is still required.

## Run once on Ubuntu (no recompile, no new F22/F23/Condor jobs)

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only

python3 scripts/zee_paper1_F24_157_matching_SM_same_LHA_HyperIso_2026_LO_audit.py \
  --f22 "$HOME/zee_F22_frozen_benchmarks_20261025" \
  --f23 "$HOME/zee_F23_hyperiso_157_20261025" \
  --f23b "$HOME/zee_F23b_157_validated_summary_20261025" \
  --output "$HOME/zee_F24_matched_SM_157_20261025"
```

The F24 output directory must not exist before execution, to protect
source integrity. This is a **single integrated native 157-case computation**, not 157 manual commands.

Results:
- `F24_157_same_LHA_matched_SM_and_Zee_legacy_NP_NOT_2026_CL.csv`
- `F24_9_priorities_same_LHA_flavor_comparison_NOT_ALLOWED.csv`
- `F24_157_unmodified_SM_CLI_source_trace.jsonl`
- `F24_157_source_matched_SM_subtracted_HyperIso_NP_report_NOT_2026_CL.json`
- Two marked `NOT_2026_CL` exploratory PDF plots, if matplotlib is available.

Expected final marker only **if** all native 157 exact-source calculations and SM invariance pass:

```text
F24_COMPLETE_NATIVE_SM_MATCHED_157_SOURCE_AND_PHYSICS_PASS ORIGINAL_F22 157 EXACT_SHARED_LHA_NATIVE_SM 157 ...
```

Interpretation: the actual nine large-cascade priorities can then be ranked by
**source-matched historical-scheme NP response**, rather than total BR relative
to an unrelated reference file. This supports proper upcoming SuperIso/F3
perturbative convention comparison; it does NOT establish final flavor
compatibility, complete general-Zee LFV, HiggsTools, or physical LHC rates.
