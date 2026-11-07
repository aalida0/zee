# Original D7/F13 neutral widths and observed-search stopping gate

**HIGGS_SCOPED_SEARCH_BLOCKED; TOTAL_WIDTH_INCOMPLETE on all four states.**
F13 HDECAY has executed. Complete leading one-loop H/A diphoton partial
widths are calculated and independently checked on the two original D12
NO/low_joint witnesses. No physical branching fractions, observed exclusion
ratios or new Higgs exclusions are assigned. `physical_higgs=UNKNOWN`,
`global_acceptance=null`, `final_scan_authorized=false`.

Work started at `88459b145291f6ff3d2b8a3c9207d0a52ae584f7` on
`research/zee-full-constraints`. B calculations and their tests were not
repeated. LFV, Modules0–13, all original D14 evidence, historical Higgs
receipts and the frozen scan branch are unchanged. No production calculation,
parameter point, scan, Condor job or broad MadGraph execution was launched.

## Actual partial-width predictions

All entries below are GeV. HDECAY quark/gg channels retain the previously
documented channel-specific QCD treatment; native leptons, charged-W and
light u,d channels are tree level; gamma gamma is leading one loop. These
are disjoint channels in a mixed-accuracy calculation, with no complete
total-width precision or theory covariance claimed.

| Channel | D7 H | D7 A | F13 H | F13 A |
| --- | ---: | ---: | ---: | ---: |
| tt | 10.87585129 | 17.49039480 | 0.918804493 | 1.306435214 |
| bb | 0.008234428 | 0.009214607 | 0.278489060 | 0.306442981 |
| cc | 0.000533507 | 0.000486132 | 0.000028050 | 0.000031948 |
| ss | 0.000002895 | 0.000003371 | 0.000099562 | 0.000109733 |
| gg | 0.035331771 | 0.062398397 | 0.001910429 | 0.003484659 |
| WW | 0.075754726 | missing loop width | 0.000634835 | missing loop width |
| ZZ | 0.036123068 | missing loop width | 0.000309955 | missing loop width |
| hh | 0.000608127 | tree CP forbidden | 0.002561114 | tree CP forbidden |
| hZ | tree CP forbidden | 0.065693040 | tree CP forbidden | 0.000873340 |
| HZ* | — | 2.23144e−13 | — | 0.009988109 |
| H1±W∓, both charges | 0.926020108 | 0.939356740 | 1.053423747 | 6.154915041 |
| gamma gamma, new | 0.0000986133451 | 0.000208610210 | 0.00000712553876 | 0.0000119395206 |
| **Known disjoint sum, not total** | **11.9585831695** | **18.5677788929** | **2.25626947016** | **7.78229418104** |

The sums also include all six diagonal/unordered LFV lepton channels and
explicit u,d tree widths. Their full numerical entries, complex amplitudes,
individual loop terms, couplings and missing-channel ledgers are in
[NEUTRAL_WIDTH_EVIDENCE.json](higgs/NEUTRAL_WIDTH_EVIDENCE.json). The largest
added u,d sum is 9.71037e−7 GeV (F13 A). Those channels are now computed,
not assumed zero; their QCD corrections remain part of the error-budget gate.
HDECAY Type-II lepton widths and single-charged-state gamma gamma/Zgamma
widths and total widths are discarded.

F13 uses exactly the original masses, tan beta, m12 squared and shifted
neutral angle, with charged-doublet curvature mass
`sqrt(cos(gamma)^2 mH1^2 + sin(gamma)^2 mH2^2)`, solely as the R2HDM
control input. No new Zee spectrum is defined. The native command, full
input, stdout/stderr, executable/library and source-lineage hashes are in
[F13_EXECUTION.json](higgs/neutral_receipts/F13_EXECUTION.json).
The driver, HDECAY library and source pins match the old D7 execution.

**Switch interpretation:** `IONSH=0` and `IONWZ=0` enable the relevant
off-shell branches in this HDECAY source; they do not disable them. See
`src/libified_hdecay/hdec_2HDM.f`, e.g. lines 1706–1720 and the
`if(ionsh.eq.0)` neutral cascade blocks. `IOELW=0` switches off the
implemented EW corrections (the vector branch replaces htww by htww0).
Thus the finite F13 A→HZ* result is retained. The source's ordinary R2HDM
charged-W tails cannot be transferred to two mixed physical charged states.
The [HDECAY description](https://arxiv.org/abs/1801.09506) supports its
channel-dependent corrections; it does not establish a complete Zee width.

## Independent amplitude and decay validation

The photon width uses
`alpha_tree^2 M^3 (|S|^2+|P|^2)/(256 pi^3 v^2)`, including the identical
photons factor. The shared v/MW/MZ tree scheme, all nine charged fermions,
and each fermion's common propagator/Yukawa mass are the same as the
previously validated h125 calculation. H has its signed W coupling,
general complex diagonal lepton couplings and both mixed charged-scalar
loops. A retains the general-lepton scalar and pseudoscalar tensors; scalar
CP conservation does not justify dropping its small CP-even lepton tensor.
All four masses exceed the tt threshold; absorptive form factors are kept.
Off-diagonal LFV insertions cannot close a one-insertion photon loop.
Normalization and spin functions follow
[2HDMC Eqs.24–28](https://arxiv.org/html/0902.0851v2#S2.SS4.SSS5).

A new native SARAH 4.15.4 extraction evaluated all four physical charged
entries for H and A on each original saved card. The signed vertex is
`-i G_ij`. H's diagonal G11/G22 values are −124.127835/−26.2403913 GeV
(D7) and −62.2908704/−243.525062 GeV (F13). All 16 extracted coefficients
agree with the analytic potential to 7.11e−14 GeV. The independent expanded
ten-real-field potential checks the H and A matrices to 1.71e−10 GeV.
The fresh native output, symbolic vertices and log are retained in
[neutral_receipts](higgs/neutral_receipts/native_vertices.json).

For A, the real scalar potential gives imaginary antisymmetric charged
trilinears, with exactly zero diagonal entries. Photon charge and the QQ
seagull are diagonal. Both triangle and seagull species traces therefore
vanish with a single off-diagonal A insertion, for arbitrary unequal charged
masses. There is also no physical charged-scalar–W–photon tree vertex.
This proves absence of the charged-scalar photon graphs at this order.
The extracted physical A off-diagonal entries are also consistent with zero
on these restricted cards; no nonzero A mixed-scalar Zgamma width is inferred
from numerical roundoff.

For H the situation differs: G12 Z21 is **+1.503388705 GeV (D7)** and
**−19.36560073 GeV (F13)**. This establishes the missing unequal-mass
charged-scalar Zgamma contribution. It cannot be reconstructed by adding
two diagonal 2HDM formulas. No Zgamma partial width is assigned.

Additional controls compare complete heavy amplitudes to independent
logarithmic Feynman-parameter integrals (maximum absolute residual
4.97e−16), charged-W widths to rest-frame physical polarizations with both
charges once, general lepton widths to scalar/pseudoscalar phase-space
formulas, and Hhh/AhZ/vector HDECAY widths to independent potential/gauge
expressions. All charged-pair thresholds lie above these parents; H2W is
closed on shell. Hhh is open; A→hh is tree CP forbidden. The transferred
neutral off-shell HZ* channels are kept separately from hZ.

The original h125 ratios remain 0.9317959556087543 and 0.9750252263683726.
Existing tests retain scalar QED Ward/seagull/Bose, photon normalization,
SM/2HDM/decoupling, CP, interference, threshold, production-scheme/source
tampering and missing-width controls. **35 tests pass, zero skips.**
[Validation residuals](higgs/neutral_receipts/VALIDATION.json) and
[full log](higgs/neutral_receipts/TEST_LOG.txt) are retained. Numerical
agreement is not a theoretical error estimate.

## Selected observed analysis and why no ratio is calculated

The selected analysis is **ATLAS 2002.12223**, HiggsBounds ID **200212223**,
139 fb−1 at 13 TeV, ggF and bbH followed by tau tau. Selection follows the
available production and actual mass domain, before calculating any observed
ratio. The pinned HiggsTools 1.1.3 runtime loads the exact historical dataset
file `neutral/tautau/LLH_LHC13_ATLAS_139.json`; its hash and HB commit are
checked. This is a two-production-channel likelihood dataset, not a single
observed cross-section curve. Mass coverage is 200–2500 GeV; the D7 masses
are bracketed by 400/500 GeV and F13 H/A by 700/800 GeV. No extrapolation
is used or authorized. There is no explicit width grid in this file.

The [experimental paper](https://arxiv.org/html/2002.12223v2) assumes a
natural width negligible compared with experimental resolution and uses
ggF Powheg and bbH MG5_aMC@NLO signal samples. The b-tag/veto category
acceptances must be matched to the model production and general complex
tau coupling. The known-sum/M diagnostics are 2.43%, 3.77%, 0.319% and
0.982% for D7 H/A and F13 H/A, respectively; they are not qualified full
widths or a finite-width/acceptance error bound. The close D7 H/A masses
also require a source-matched overlap/interference treatment.

All four exact-card inputs fail the complete-width consumer guard before
constructing any HiggsTools Predictions object. This is the bounded search
attempt: **zero complete signals connected, no sigma times BR, no observed
or expected ratio**. The rejected inputs and original SusHi central
cross sections/scale/PDF bands are bound in
[OBSERVED_SEARCH_COVERAGE.json](higgs/OBSERVED_SEARCH_COVERAGE.json).
The previously executed production is reused; none of its 52 runs is repeated.
LO scale envelopes/PDF estimates do not qualify the omitted production
corrections or their correlation with BRs. No uniform K factor, Gaussian
theory sigma, likelihood p-value or 95% physical exclusion is invented.

## Exact stopping barrier

A physical total needs numerical values or defensible error bounds for:

1. **H→Zgamma**, including unequal charged masses, off-diagonal G/Z currents
   and seagull/gauge completion. The nonzero products above prove the missing
   term on both exact cards. A→Zgamma also needs its model-matched fermion
   amplitudes with complex leptons; scalar-sector CP alone does not set the
   fermion width to zero.
2. **Charged-W finite-width and off-shell contributions** with both mixed
   charged propagators and all model daughter decays, subtracting the
   already counted on-shell cascade. F13 H is only 54.4713 GeV above H1W;
   the frozen H1 width is 0.200399 GeV and H2 width 12.1393 GeV. D7's H2
   width is 16.0234 GeV. Closed on-shell H2W/charged-pair channels do not
   bound their virtual tails or interference. No validated numerical bound
   exists here. Inserting spectral functions alone would not establish the
   complete gauge-consistent multibody rate.
3. **A→WW/ZZ loop amplitudes** and numerical materiality bounds for other
   nonresonant EW/multibody channels and off-shell scalar cascades at the
   intended total-width precision. For F13 A→HZ*, the transferred 0.009988
   GeV includes HDECAY's stable-H approximation, not the full Zee daughter
   width and coherent final-state treatment.
4. **Decay/production uncertainty and signal hypothesis**: channel-specific
   QCD/EW truncation, scalar and Yukawa parametric correlations, and a
   qualified acceptance/finite-width/interference transfer to the selected
   likelihood. No total uncertainty has been established.

The tree kernels and native vertices supply useful ingredients, but neither
the existing HDECAY R2HDM output nor unavailable full-loop SPheno supplies
these missing model predictions. This is the requested stopping gate; no
approximate normalized BR table or exclusion is produced. Higgs milestones
remain **2/6**, and the global/full-scan gate is unchanged.

## Reproduction

The committed native F13 and SARAH receipts are sufficient for the bounded
calculation replay; the pinned local HiggsTools runtime/dataset is required:

```bash
python -m research.full_constraints.higgs.neutral_study --out /tmp/zee-neutral-replay-NEW
python -m unittest research.full_constraints.higgs.test_neutral_widths \
  research.full_constraints.higgs.test_higgs \
  research.full_constraints.higgs.test_sushi -v
git diff --check
```

The replay refuses an existing output directory. To repeat the native F13
execution, use the exact command array in its receipt with the unchanged
driver/library built as in [HIGGS_SUSHI_EXECUTION.md](HIGGS_SUSHI_EXECUTION.md).
For SARAH, create a fresh scratch directory, copy the retained
`native_inputs.json` there, and execute `native_neutral_vertices.m` with
`ZEE_SUSHI_NATIVE_OUT` pointing to it. It only queries vertices and writes
scratch output. No frozen SARAH model file is modified.
