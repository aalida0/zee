# Zee Higgs constraints: public-code reuse results (11 November 2026)

**Branch:** `research/zee-full-constraints`  
**Model:** Zee scalar singlet + CP-conserving 2HDM, Type-II **quark** Yukawas with general lepton Yukawas.  
**Result:** real public-code execution, all 16 original certified scalar witnesses / 64 newly constructed lepton families. **No globally allowed Zee point certified.**

## 1. HiggsTools 1.1.3 HiggsSignals: successful h125-only effective-coupling input

Original failed `Higgs.tools.Input.predictionsFromDict` because it required a `w_h` total width. The native `HiggsPredictions.effectiveCouplingInput` instead supplies its **SM-reference effective-coupling inferred width**. We add the actual source-computed h125 `e mu`, `e tau`, `mu tau` partial widths once; the reference SM width is *not* promoted into a certified exact Zee physical total. Both physical mixed charged-state photon loops and complex diagonal lepton couplings are retained.

**Successful CI with same pinned experimental dataset:** https://github.com/aalida0/zee/actions/runs/43117782437. Source: `pheno_paper_2026/h125_higgssignals_probe.py`. 4 explicit width accounting/falsification tests passed. The dataset's same-source SM χ² is **153.714285**. Representative **NO seed 20261111** `Delta chi2 = chi2_Zee - chi2_SM`:

| Original scalar ID | Δχ² |
|---:|---:|
| 15673 | 0.1211173 |
| 15591 | 1.9228411 |
| 2264 | 1.5275601 |
| 14074 | 0.5967910 |
| 14555 | 74.38398 |

Across each scalar's four NO/IO/seeds, source Δχ² ranges include **14555: 74.32–75.67**, **8850: 10.92–37.25**, **16385: 9.40–37.51**, **3693: 10.16–10.25**. These represent notable relative h125 fit tension; they are not automatically 95% CL failures without a declared effective likelihood statistic. Do **not** take a threshold on a raw Δχ² without specifying the comparison hypothesis, correlations and degrees of freedom.

## 2. HiggsTools h125-only HiggsBounds

Source `pheno_paper_2026/h125_higgsbounds_probe.py`, same successful CI. Evaluated all 64 h125 effective-coupling model points against the pinned source HiggsBounds observed dataset (HB commit `3539f9adf3724f8752701208bf059d1658824cd2`). Within **this explicitly h125-only** model input all 64 returned selected-limit `allowed=True`. For 15673 NO 20261111, the HiggsBounds **selected** ID 12045 (CMS-PAS-HIG-12-045) observed ratio was ~0.77943, not an exclusion. Some **unselected applied** limits had ratio >1, which is **not the selected-limit HiggsBounds exclusion decision**. The h125-only screen is an incomplete/full-model-independent diagnostic; charged and heavy Higgs searches are absent.

## 3. AnyHdecay 1.1.0 / HDECAY 6.60: successful source-locked heavy H/A channel transfer

Public code pinned to AnyHdecay commit `137b6991cafcd32770e64b2b5979de80db1e44af`. Complete source, 16 auxiliary-R2HDM reference runs, 64 native Zee H/A partial-channel mergers and focused crosschecks **passed**:

https://github.com/aalida0/zee/actions/runs/43119479264

No ordinary 2HDM charged scalar, Type-II lepton width, single-charged photon amplitude or HDECAY total width is transferred. The auxiliary charged-doublet curvature is `mD² = cos²(gamma)*mH1² + sin²(gamma)*mH2²`; native mixed charged states are retained separately. The HDECAY QCD quark widths and gluonic and neutral-doublet channels replace their native tree counterparts **once**; exact Zee H/A→H1W,H2W, charged-pair and general-lepton channels are kept disjoint. The sums remain `partial_widths_only=True`, **not physical total widths**.

These are the *ranges of positive known mixed-order channel sums*, not measured or complete physical widths:

| ID | H sum GeV | A sum GeV | H sum/mass | A sum/mass |
|---:|---:|---:|---:|---:|
| 2264 | 56.373 | 50.696 | 6.07% | 5.66% |
| 2616 | 34.474–34.475 | 37.208–37.209 | 3.03% | 3.27% |
| 3693 | 29.314 | 40.090 | 3.28% | 4.06% |
| 4611 | 22.053 | 29.569 | 2.29% | 2.90% |
| 8294 | 50.338 | 44.679 | 4.49% | 4.22% |
| 8850 | 56.812–56.814 | 54.450–54.452 | 5.65% | 5.64% |
| 9454 | 14.518–14.519 | 15.664–15.665 | 1.65% | 1.88% |
| 11016 | 26.745–26.746 | 30.137–30.138 | 2.15% | 2.27% |
| 13345 | 39.515 | 29.593 | 3.78% | 3.08% |
| 14074 | 51.284–51.290 | 63.513–63.520 | 3.83–3.84% | 4.46% |
| 14187 | 33.581–33.588 | 44.323–44.330 | 3.13–3.14% | 3.98% |
| 14555 | 3.179–3.187 | 3.405–3.413 | 0.34% | 0.35% |
| 14984 | 63.807 | 56.908 | 5.52% | 5.10% |
| 15591 | 49.446–49.449 | 55.887–55.891 | 5.14% | 5.60% |
| **15673** | **72.411–72.412** | **56.234** | **5.69%** | **4.75%** |
| 16385 | 29.663–29.669 | 25.674–25.680 | 2.85% | 2.58% |

For 15673 NO seed 20261111: `H→H1W both charges =40.77269 GeV`, `A→H1W both charges=25.95049 GeV`, with `H→tt=31.26961 GeV` and `A→tt=30.15089 GeV`. Source H/A on-shell two-body tree channel inventory has no declared missing on-shell channels at this benchmark; genuine omitted virtual/off-shell, Zγ/gg-loop-matching, QCD/EW higher orders, widths/interference and heavy search rate/acceptance materiality are still **unknown**.

### Important HDECAY output anomaly

HDECAY's **unused auxiliary SM reference** `SM_b_H_gg` was **negative** in four of the 16 control runs:
`11016=-4.11646e-4`, `14074=-1.16914e-3`, `14984=-3.17220e-5`, `15673=-5.93609e-4`. This auxiliary output is not a Zee channel and is not transferred. All physically transferred partial widths must remain nonnegative and pass independent Hhh/AhZ/HVV identity checks. The parser exposes these anomalies, rejects any negative transferred rates, and does not clip/correct them. This limits the role of the auxiliary SM reference; it is not an excuse to treat HDECAY model totals as physical Zee totals.

## 4. Current Higgs phenomenology scope

**Validated and actually executed:** h125-only HiggsSignals and HiggsBounds effective-coupling screening at 64/64; charged mixed-state leading h125 photon loops; H/A all-64 transferable HDECAY quark/neutral and native Zee tree decay channels; original real 13/14 TeV `tbH2` hard production at 16/3 source scalar cards; original D7/F13 13 TeV SusHi H/A production.

**Not completed:** source-matched H/A production for *these* 16 original scalar spectra (the old D7/F13 SusHi results are not transferable); qualified total heavy widths and BR uncertainties; actual applicable heavy H/A observed HiggsBounds constraints and full charged search coverage, including H1 production; statistical h125 fit acceptance threshold; nontrivial line-shape effects near 5–6% width and interference; all-parameter-space scan. Absence of a dedicated public `H2→H1Z` search is not experimental permission to accept the benchmark.

**Scientific status:** `H125_EFFECTIVE_HS_HB_SCOPED_EVALUATED`, `H_A_HDECAY_16x4_DISJOINT_PARTIALS_COMPLETED`, `HEAVY_HIGGS_EXPERIMENTAL_SEARCH_NOT_DONE`, `FULL_PHYSICAL_HIGGS_UNKNOWN`, `GLOBAL_ACCEPTANCE=null`.

Artifacts in the two linked Actions runs have finite retention; the numerical results here are permanently summarized, while raw 64-card source files can be regenerated with the same pinned Python/NumPy/flavio environment.

## Source links

- Florentino et al. 2021 charged Zee cascade, arXiv:2106.08332.
- AnyHdecay/HDECAY interface https://jonaswittbrodt.gitlab.io/anyhdecay/
- Original 2HDMC reference, arXiv:0902.0851.
- HiggsTools API https://higgsbounds.gitlab.io/higgstools/
