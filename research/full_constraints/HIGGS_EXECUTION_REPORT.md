# Bounded Higgs execution — 2026-11-07

**Result: HIGGS_FULL_COVERAGE_BLOCKED**, with
**HIGGS_SCOPED_CHANNEL_VALIDATED** for the complete leading one-loop
h125 diphoton amplitude. No newly validated experimental exclusion and
no globally allowed point are established. `exclusion=null`,
`global_acceptance=null`, `final_scan_authorized=false`.

Read `AGENTS.md`, `HIGGS_NEXT_STAGE.md`, `HIGGS_TASK.md`, the research
`PLAN.md`, and the frozen physics, decay and production evidence before
execution. The root `PLAN.md` does not exist; the handoff explicitly points
to `research/full_constraints/PLAN.md`, which was read. B/LFV conclusions
are retained; neither investigation nor its tests are rerun.

## Work executed

1. Verified the native HiggsTools 1.1.3 library and every HB/HS dataset
   JSON byte against frozen D13 evidence, then enumerated all loaded APIs:
   310 limits, 22 measurements, 159 observables. Produced the conservative,
   exact-ID applicability/input matrix **before** executing benchmark rates.
2. Bound the two original D12 NO/low_joint witnesses and all 16 existing
   D14 scalar production cards / 64 original families. The saved D14 dataset
   SHA256 is `2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9`.
   Added explicit per-card heavy-neutral threshold and missing-width ledgers.
3. Calculated h125→γγ using common tree v/MW/MZ gauge inputs and signed
   restricted-model scalar trilinears, W, all charged fermions, complex
   diagonal leptons, both charged scalars and coherent interference.
   No SPheno full-loop input was consumed. Independent numerical controls
   include source formulas, parameter integrals, scalar QED and the
   expanded potential. Source receipts include published versioned HTML
   hashes and historical native SARAH evidence.
4. Investigated Zγ: extracted complete physical charged G, Q, Z and AZ
   seagull matrices. Nonzero G12 Z21 proves that diagonal charged-loop
   duplication is insufficient. Complete mixed-state gauge matching is
   unavailable; no Zγ model width is assigned.
5. Exercised the supported HiggsTools partial-width replacement interface:
   the validated complete LO γγ ratio rescales the SMHiggsEW reference.
   Replacing the width preserves the full partial-width sum without double
   counting. Conditional Zγ=0/1/2 times SM controls expose missing-width
   sensitivity; no model χ² exclusion or p-value is inferred.
6. Replayed only existing charge-inclusive 13-TeV H2 production with the
   exact full-family D4 two-body widths in isolated H2-only predictions.
   No absent cross section was interpreted as coverage. Checked all 64
   bindings and independently interpolated the actual observed/expected
   charged limit tables. Raw MG directories are absent: native hashes in
   committed manifests are preserved, not claimed freshly revalidated.
7. Updated the coverage, validation matrix and readiness decision. No hard
   physics adapter was installed because its full prediction/uncertainty
   gate is closed. The new code is a research-only calculator and replay.

## Numerical results and independent controls

| Quantity | Result |
| --- | ---: |
| Complete D7 Γγγ/ΓSM | 0.9317959556087543 |
| Complete F13 Γγγ/ΓSM | 0.9750252263683726 |
| Loop functions vs independent logarithmic Feynman integral, max relative | 7.951e−15 |
| Scalar/fermion simplex parameters, max absolute | 9.104e−15 |
| Complete complex D12 amplitudes vs independent parameters, max absolute | 6.217e−15 |
| D12 trilinears vs independent expanded potential, max absolute [GeV] | 1.428e−10 |
| Normalized CP-even rate vs compiled HiggsTools, max absolute | 6.661e−15 |
| Scalar-QED Ward residual, max absolute | 4.730e−16 |
| Independent polarization/identical-photon width residual | 0 |
| Charged observed/expected table interpolation, max relative | 3.258e−16 |
| Largest selected observed ratio, isolated D14 H2 subset | 0.16360744200457877 |
| D14 H2 Γ/M range | 0.023225–0.089697 |

**16/16 tests pass, no failures, errors or skips.** The
[complete test log](higgs/TEST_LOG.txt) includes heavy-mass decoupling,
SM/one-state/mixing-endpoint/degenerate-mass limits, electric-charge and
trilinear-sign falsifiers, CP-odd tau input, seagull/Bose identities,
width normalization, inclusive-invisible double-counting rejection,
nonfinite/non-Hermitian/missing inputs, and energy/PDF/charge/Yukawa/source
binding error injection. An injected conflicting source digest exposed an
overlapping-manifest check in the new replay; both source manifests are now
checked independently and the falsifier passes. Numerical residuals are not
theoretical errors.
The exact controls and every numerical application are in
[HIGGS_VALIDATION.json](HIGGS_VALIDATION.json).

| Conditional HS control | D7 χ² | F13 χ² |
| --- | ---: | ---: |
| Assumed ΓZγ/ΓZγSM=0 | 170.764804 | 154.488233 |
| Assumed ΓZγ/ΓZγSM=1 | 171.012258 | 154.449879 |
| Assumed ΓZγ/ΓZγSM=2 | 171.262236 | 154.415789 |

These conditional values use the SM reference rescaled by LO γγ and are
not a uniformly NLO Zee fit. All 159 data points are retained with the
pinned correlations. The physically matched total width, theory covariance
and complete model interpretation remain UNKNOWN. In particular a χ²
shift is not labelled a 95% CL failure.

## Scope and stopping gate

The exact ID/process/energy/domain gaps are in
[HIGGS_COVERAGE.md](HIGGS_COVERAGE.md) and
[higgs/COVERAGE.json](higgs/COVERAGE.json). Every potentially applicable
unqualified rate is `MISSING_PREDICTION`; absent public cascade topologies
are `MISSING_EXPERIMENTAL_COVERAGE`. Axis-envelope rejection and absent
charge sectors are the only automatic `NOT_APPLICABLE` proofs used.
No positive `APPLICABLE_INPUT_COMPLETE` physics gate is invented.

Unresolved Higgs inputs include complete mixed-state Zγ and total-width
qualification; 8-TeV/H1/other charged production; complete H/A production and
competing widths; relevant off-shell and finite-width/interference treatment;
SM-reference/STXS signal-shape transfer; production/decay scale/PDF/QCD/EW
uncertainty and covariance; and experimental signal-model applicability.
The source-backed path is feasible in parts, but full coverage is not
established by the existing calculations within this bounded task.

The [ATLAS tb source](https://arxiv.org/html/2102.10076) uses NLO 4FS,
a narrow-width signal and neglected background interference. Saved LO 5FS
central inputs are insufficient to certify that transfer or robust uncertainty.
The old D7 central LO excess is not upgraded. Missing rates are not zeros;
16 central H2 rates cannot become full HiggsTools coverage. Full-loop
SPheno remains UNAVAILABLE.

## Reproduction and immutable outputs

Use the existing pinned runtime and saved dataset; no generators, fitting of
new Yukawa families, scan, Condor or production job is called:

```bash
python -m research.full_constraints.higgs.coverage \
  --dataset /tmp/zee-d14c-dataset.json --out /tmp/zee-higgs-inventory-REPLAY
python -m research.full_constraints.higgs.study \
  --dataset /tmp/zee-d14c-dataset.json \
  --coverage research/full_constraints/higgs/COVERAGE.json \
  --out /tmp/zee-higgs-study-REPLAY
python -m unittest research.full_constraints.higgs.test_higgs -v
git diff --check
```

Each executable refuses an existing output directory. Failed attempts were
retained separately; final successful evidence is from
`/tmp/zee-higgs-study-20261107-verified/`. The matrix was exported from
`/tmp/zee-higgs-inventory-20261107-r2/`. Committed copies preserve the results.
Published-source replay paths and byte hashes are in
[higgs/SOURCE_MANIFEST.json](higgs/SOURCE_MANIFEST.json); calculation/model/
library and dataset hashes are in the validation artifact and matrix.
The private saved dataset and raw native production artifacts are not
redistributed. Missing raw artifacts prevent a fresh native-run audit, not
an honest replay of source-controlled central numbers.

Only files under `research/full_constraints/` are changed. Modules0–13,
D14 source/collections/receipts and the frozen conditional branch are untouched.
No final-scan merge or execution is authorized.
