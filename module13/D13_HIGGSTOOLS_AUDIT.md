# D13 HiggsTools-only evaluation

Executed 2026-11-03. The broader production workflow was stopped. This task ran
HiggsBounds and HiggsSignals only, reusing existing predictions. No MadGraph,
event generation, integration, energy extrapolation, or literature survey was run.
D0–D12 files are unchanged.

## Inputs and software

- Exact D10 scalar records: `d7_NO_neutral_near_heavy_07` and
  `F13_heavy_0001330`. The D12 **NO / low_joint** witnesses are respectively
  `texture_0.0001` and `texture_0.001`. These are two fixed Yukawa choices,
  not statements about every NO/IO texture at the same scalar masses.
- D10 canonical hashes agree with D12. Original charged widths and BRs are
  reused without renormalizing the supplied modes to unity.
- Existing HiggsTools **1.1.3** reused. HB dataset:
  `3539f9adf3724f8752701208bf059d1658824cd2` (2025-09-11), 310 loaded limits.
  HS dataset: `3c6c2538d9ba0549ea0559cf9b38c18eb80c3af1` (2023-05-22),
  159 observables in 22 measurements. These pinned datasets are **not claimed
  to provide complete November 2026 coverage**. No dataset update was performed.
- Four previously validated 13 TeV charged-production results were already
  available in `validation/module13/local/validated_rates.json`. Their receipts,
  source-input hashes, and every receipt-listed artifact were checked read-only;
  saved native `results.dat` cross sections/errors agree with the inputs used here.
  The compact frozen input/provenance snapshot is
  `validation/module13/higgstools_production_inputs.json`.
- These production inputs are central **LO 5FS**, inclusive in both charges,
  NNPDF30_lo_as_0130 member 0, LHAPDF ID 263000, fixed muR=muF=mHcharged.
  No theoretical scale/PDF uncertainty is assigned. Their numerical integration
  errors are recorded separately and are not a theory band.

The runner, full dataset file hashes, library hash, exact input hashes, every
applied limit and ratio, selected analyses, and HS measurement contributions
are recorded in `validation/module13/d13_higgstools.json`.

## HiggsBounds: evaluated charged searches

The table gives the selected analysis for each charged state. All four select
ATLAS 139 fb^-1, [2102.10076](https://arxiv.org/abs/2102.10076), associated
tbH production with H→tb. `r_obs` and `r_exp` are the HiggsBounds prediction
over observed/expected limit ratios. Selection uses **expected** sensitivity;
the selected observed ratio determines exclusion at 95% CL for the supplied model
prediction. See the [HiggsTools documentation](https://higgsbounds.gitlab.io/higgstools/).

| Benchmark/state | Mass [GeV] | σ(tbH±) [pb] | σ×BR(tb) [pb] | r_exp | r_obs | Central-input result |
|---|---:|---:|---:|---:|---:|---|
| D7 H1 | 298.726655 | 0.106880 | 0.106529 | 0.097010 | 0.154271 | NOT_EXCLUDED |
| D7 H2 | 532.932913 | 0.255800 | 0.228398 | 0.865968 | 1.072383 | EXCLUDED |
| F13 H1 | 572.231624 | 0.0025042 | 0.00249818 | 0.011755 | 0.015126 | NOT_EXCLUDED |
| F13 H2 | 873.207683 | 0.0015023 | 0.000147146 | 0.001587 | 0.001731 | NOT_EXCLUDED |

Thus **D7 is excluded for the supplied central LO predictions**, while **F13
is not excluded by the evaluated charged subset**. D7 exceeds the selected
limit by only 7.24%; missing production theory uncertainties and differences
between the LO input and experimental signal modeling prevent calling this a
robust precision exclusion. Neither result certifies global Zee acceptance.

For each benchmark, five supported 13 TeV analyses were evaluated for both
charged states (ten applications): ATLAS tb above; CMS tb
[1908.09206](https://arxiv.org/abs/1908.09206) and
[2001.07763](https://arxiv.org/abs/2001.07763); ATLAS τν
[1807.07915](https://arxiv.org/abs/1807.07915); CMS τν
[1903.04560](https://arxiv.org/abs/1903.04560). All other evaluated applications
are NOT_EXCLUDED. The largest τν observed ratio is 2.57e-7 for D7 and
1.02e-5 for F13. `minExpRatio=0` retains these tiny positive rates instead of
discarding them at the default 1e-4 cutoff. No missing charged cross section
is interpreted as a physical zero or a passed search.

All 24 loaded singly-charged analysis entries have explicit coverage records.
Old 8 TeV tb-associated limits and relevant qqHpm limits are UNEVALUATED where
their production is missing. LEP/light-top-decay searches lie outside these
masses. VBF H±→WZ searches are NOT_APPLICABLE to the validated vanishing
tree H±W∓Z vertex. Charged Wh, WH/WA and H2→H1Z/H1h BRs are retained in the
input snapshot, but the loaded singly-charged dataset has no corresponding
implemented analysis; they give no exclusion here.

## h125 and heavy neutral states

HiggsSignals ran for both h125 predictions, reusing the existing exact tree
quark/lepton/gauge vertices with HiggsTools' SMHiggsEW effective-coupling
production/decay approximation and the existing neutral LFV-width kernel.
Charged-scalar contributions to h→γγ and Zγ are missing. Consequently these
are **approximate fits**, and a complete h125 excluded/not-excluded decision
is **UNEVALUATED**. No arbitrary Δχ² cutoff or p-value is assigned.

| Benchmark | HS χ² | SM χ² at the same 125 GeV mass | Δχ² | Observables |
|---|---:|---:|---:|---:|
| D7 | 162.086798 | 153.859389 | 8.227409 | 159 |
| F13 | 153.876920 | 153.859389 | 0.017531 | 159 |

For D7 the largest positive measurement-level Δχ² contributions are
2103.06956 (+4.040790), 1606.02266 (+2.453074), and 2103.04956 (+1.180938).
For F13 they are 2110.04836 (+0.299411), 2204.12957 (+0.196189), and
ATLAS-CONF-2019-045 (+0.134554). These identify fit tension, not individual
search exclusions. All 22 contributions and SM references are in the JSON.

HiggsBounds also ran on the approximate h125 prediction. Its selected limit
is CMS-PAS-HIG-12-045: D7 r_obs=0.739358, r_exp=3.795571; F13
r_obs=0.789132, r_exp=4.051089. Both are NOT_EXCLUDED **within this approximation**.
The result includes the dataset's historical SM-Higgs search treatment and
does not replace the HiggsSignals fit.

Heavy H/A searches are **UNEVALUATED**. D10 masses and tree couplings alone
do not provide complete H/A total widths and BRs: in particular H→hh and
open H/A→charged-scalar W modes must be included. SM-scaled default widths
would silently omit those channels. No heavy-neutral mass bound is inferred.

## Production/decay inputs still needed

1. Charge-inclusive σ(tbH1±), σ(tbH2±) at **8 TeV**, for older implemented
   associated-production tb/τν limits. Existing 13 TeV inputs are sufficient
   for the five 13 TeV charged analyses evaluated here.
2. Model-matched **qqHpm single charged production** for relevant tb analyses:
   at 8 TeV for in-range states (400–2000 GeV), and at 13 TeV for F13 H2
   (800–3000 GeV). This is a distinct topology from tb-associated production;
   its absence is not zero. Any use must also validate the analysis signal
   model. Charged-pair/associated-neutral rates are not supplied; none of the
   evaluated five searches requires them. The loaded charged pair limits are
   LEP limits outside the present masses.
3. Heavy H/A ggH, bbH and other analysis-required production at each dataset
   energy, or a validated effective-coupling input accepted by HiggsPredictions,
   together with the **complete neutral widths and BRs**. No new integration
   is required by this deliverable and none was attempted.
4. Complete h125 loop-induced BR inputs including charged scalars for a full
   HS decision. Its standard production modes currently use the built-in
   effective-coupling approximation, not missing zero rates.

No 13.6 or 14 TeV input is needed for these executed 13 TeV comparisons.
Results remain source- and dataset-bounded; all `global_zee_acceptance` values
are null. Reproduce with `python -m module13.higgstools` using the pinned local
HiggsTools installation/datasets and the committed frozen production snapshot.

## Validation

Six focused tests check frozen identity/BRs, missing-production handling,
rejection of mismatched scalar rates, expected-sensitivity selection, tiny τν
rates, and fit/status accounting: **6/6 passed**. The D12 regression suite ran
without modifying or rerunning its study: **8 passed, 1 skipped, 1 failed**.
The sole failure is its historical `AGENTS.md` source hash: the current D13
instructions hash to `2a7478020be18fc021647b40717a901f1e4189e1efbd958a9c5b09c9c20cac06`,
while D12 expects `4806717fbda37a9bf4aefb152915fd866e25a965437d710b7462c16bcd27102c`.
This mismatch predates this task; every other D12 recorded source hash still
matches. The skipped test needs a locally reconstructed SuperIso backend.
The system's obsolete pytest fails to import on Python 3.10; tests use the
standard-library unittest runner instead. `git diff --check` passed.
