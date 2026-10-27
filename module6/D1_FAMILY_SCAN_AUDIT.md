# D1 illustrative coherent family grid audit — 2026-10-27

**D1_REAL_GRID_EXECUTED_NOT_PHYSICAL_ACCEPTANCE.** Six independent NO inputs completed the actual frozen scalar → inverse-neutrino → Module3 LFV subset → Module5 conditional flavor workflow. Every point has execution status `PASS_SCOPED`, which means the computations ran. The second spectrum has a real scalar EWPO **FAIL**; both spectra retain vacuum **UNKNOWN**. These six hand-picked development probes define no sampling distribution, physics prior, viable population or confidence exclusion.

## Independent audit and implementation

The scaffold omitted nested Module2 schema validation, accepting malformed nested ordering/types/extra fields until evaluation. The generator now validates Module2 before generation and every generated row; rejects embedded outputs that would become stale; requires explicit vacuum starts/seeds; and prevents output paths overwriting the seed. Existing deep-copy mutation safety, four complex coefficients, finite-number checks, full scalar canonical SHA and all three benchmark IDs were independently checked. Overflow under the complex ×10 transformations fails closed. No physics defaults were introduced.

The runner regenerates the exact six expected records from SHA-pinned D0 source bytes, compares the manifest and all rows, and independently repeats Module3/2 schema, full Module1 scalar SHA and identity checks before calling actual `module6.coherent_pilot.pilot` for each row. It checks all 45 inherited D0 source-file hashes, rehashes the original read-only reference LHA bytes, and rejects matching scales other than 160 GeV or any different top mass/reference hash. It performs an additional real Module2 evaluation, compares its complete output hash with the pilot, and computes the matrix difference against the original target directly. Every numerical JSON write uses `allow_nan=false`; complex matrices remain paired real/imag arrays in ignored full outputs. Errors retain exception type/message/traceback, input and source hashes and `BLOCKED_ERROR`; none occurred.

No frozen Modules0–5, D0 code/tests/evidence, SARAH or external HyperIso code was modified. The branch descends from D0 `bb3834c5b3679dbfd9cb4cf4a530eecb460fc32e`; its nested workspace is already ignored by the parent checkout. No external mass evolution, NLO/BMU/HyperIso re-evaluation or literature search was performed.

## Actual grid and scalar results

All other scalar inputs, EW inputs, source constants, numerics and original target matrix are retained from `module3/example.json`. beta=1.394 rad; tanbeta is derived inside the frozen flavor contract. Each of four complex homogeneous coefficients receives the same multiplier 1, 10 or 10i. Every row gets a unique ID and a new full Module1 canonical SHA including that ID; equal spectra therefore need not have identical full-record hashes.

| Spectrum | charged masses GeV | gamma rad | reconstruction | BFB | unitarity | scalar EWPO | vacuum |
|---|---|---:|---|---|---|---|---|
| source_spectrum | 300 / 700 | 1.089 | PASS | sufficient PASS | PASS | PASS | UNKNOWN |
| illustrative_second_spectrum | 450 / 850 | 0.95 | PASS | sufficient PASS | PASS | FAIL | UNKNOWN |

For source/second spectra respectively, max tree-unitarity eigenvalues are 18.136779085730428 / 18.266901729253323 (<8π), and selected inherited Gfitter scalar-oblique χ² values are 0.8726172333959237 / 102.55669830921558. The latter exceeds its 7.814727903251179 threshold; the runner preserves `SCALAR_PIPELINE_FAIL`. This scoped Gaussian scalar-oblique gate is not a global experimental classification.

Each point actually ran 300 vacuum attempts (two original seeds, 66+66+18 per seed), giving 294 credible stationary minima, six nonconverged/rejected attempts and no deeper witness or boundary hit, within 12v. `all_attempts_converged=false`, `global_stability_proven=false`. No memoization, skipped vacuum, certified global stability or substitution was used. The final six-point execution therefore used 1,800 attempts. An initial six-point development execution also completed before compacting evidence; a fresh final six-point rerun supplied the committed evidence. The D0 baseline integration also executes its full scalar search.

## Neutrino, Yukawa and LFV results

Every row preserves exactly the original complex Majorana target and NO ordering. Its target SHA is `4f9a9e2fe7cadcfb44052bf919568f1929488e3e9eafd903264daddf49c5e7d1`. Relative target-vs-reconstructed matrix errors range from 9.82034788e-16 to 3.50201083e-15. Maximum entrywise absolute errors and all F/D/Ye/Ye2/Mnu norms are in the compact evidence. This is inverse-equation closure, with neutrino data comparison `NOT_EVALUATED`.

| Actual benchmark ID | relative Mnu error | ||D||F | mu→eγ subset BR | Γ(h→eτ), GeV |
|---|---:|---:|---:|---:|
| d1_NO_source_spectrum_source_family | 3.0290001e-15 | 1.491905747e-05 | 5.11705975942e-19 | 7.50525358974e-18 |
| d1_NO_source_spectrum_homogeneous_x10 | 2.6562166e-15 | 1.585207481e-05 | 5.12278228975e-19 | 4.60694575147e-16 |
| d1_NO_source_spectrum_homogeneous_i10 | 3.5020108e-15 | 1.585207481e-05 | 5.12692223587e-19 | 4.57722858195e-16 |
| d1_NO_illustrative_second_spectrum_source_family | 9.8203479e-16 | 1.724649772e-05 | 7.91826525153e-20 | 8.48021536806e-18 |
| d1_NO_illustrative_second_spectrum_homogeneous_x10 | 1.3391753e-15 | 1.805967008e-05 | 7.91570218329e-20 | 4.70610194313e-16 |
| d1_NO_illustrative_second_spectrum_homogeneous_i10 | 1.183516e-15 | 1.805967008e-05 | 7.93065234886e-20 | 4.6885481895e-16 |

Within source/second spectra, the mu→eγ subset BR max/min ratios are 1.0019273717554702 / 1.0018886720629747 (about 0.193% / 0.189%). The source-spectrum x10 and i10 directions have equal ||D|| but different subset BRs: magnitude alone does not determine these channels. The second-spectrum real x10 direction slightly lowers mu→eγ, while i10 raises it. Thus the observed variation is small and phase-sensitive; there is no universal monotonic family-factor/rate relation. Γ(h→eτ) increases substantially along these directions (about 61.4× / 55.5× maximum relative to the respective source-family value). All three radiative tau/muon subset BRs and all nine Higgs LFV partial widths are retained per point; none is compared with an experimental LFV limit.

## Flavor invariance, spectrum contrast and D0 regression

| Spectrum (all three families) | signed DeltaC7 | signed DeltaC8 | conditional LO-linear value, 10^-4 |
|---|---:|---:|---:|
| source | -0.05955354444399845 | -0.06299918381959017 | 4.182878900268742 |
| second | -0.04800734416336548 | -0.05256754326927448 | 4.062088392291873 |

For each spectrum, max-minus-min residuals across all three lepton families are exactly 0.0 for C7, C8 and the conditional value (tested tolerance 1e-13). This supports the expected conditional flavor independence of these homogeneous lepton directions. Flavor masses/mixing come solely from each row’s validated scalar record, and top input is identical.

At changed spectrum and fixed homogeneous family, DeltaC7 changes by +0.011546200280632968, DeltaC8 by +0.010431640550315695, and the conditional value by -0.12079050797686897 in 10^-4 units. The mu→eγ second/source subset ratios are 0.1547424814993398, 0.1545195898552329 and 0.15468641777667158 for 1, 10, 10i. Both lepton and flavor sectors respond to the changed spectrum; these controlled contrasts are not population correlation estimates.

The NO source-spectrum/source-family point agrees exactly (absolute difference 0.0) with the D0 references for signed C7/C8, conditional 4.182878900268742 and mu→eγ subset BR 5.117059759419609e-19. The other five points were real independent pilot executions; D0 reuse is limited to pinned provenance and regression targets.

## Provenance, runtime and validation

Full SHA256 values for every input, complete scalar record, per-sector output, local output bytes, source file and test log are in [d1_family_scan.json](../validation/module6/d1_family_scan.json). Large outputs and JSONL/manifest remain ignored under `validation/module6/local/`. The per-point `physical_status=NOT_EVALUATED` is retained generator metadata; actual computed scalar assessments appear under `scalar_gates`, and no physical acceptance is assigned.

- JSONL: 13798 bytes; SHA256 `e92ea8c5b5fa50d0643dea218e6a9a2fe7be770825482c5e148fdcc6e3614534`.
- Manifest bytes SHA256: `731ef7e3f683168052bc3f8b60493b8e622a25fa420f9e62f8f9e73ce093eaaa`.
- D0 source seed bytes SHA256: `6a55f774041a9d5e06bd6ea30a628bfcf5c840af0ddff30bce5f692a551c2915`.
- Compact evidence bytes SHA256: `4ee11239d688a106c8fea964e35e70e7b3a3f6b55db7ddbe437293bbf88234e2`.
- Fixed reference LHA SHA256: `984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374`.
- Fixed `mt_MSbar(160)=163.96892236746697 GeV`, inherited `QCDHelper::msbar_mass(6,160.,MassType::MSBAR)` provenance from frozen D0/Module5; reference LHA bytes independently rehashed, no mass evolution guessed.
- Final six-point wall time: 20.293104 s; individual times 3.2159, 2.9367, 2.9338, 2.9470, 2.9905, 5.2690 s.
- **29 tests PASS**, zero failures/errors/skips: nine generator controls, nine runner/evidence controls, eleven unchanged D0 regressions including a real scalar/neutrino/LFV/flavor integration and independent 60-digit signed flavor oracle.

Controls reject stale charged-mass scalar hashes, swapped identities even with valid hashes, invalid nested schemas/types, nonfinite/overflow coefficients, wrong scale/top/LHA provenance, missing sectors and experimental/global acceptance promotion. They check all six real inverse closures against the unchanged target, actual fixed-spectrum flavor invariance and deliberately falsified invariance, complete-LFV/likelihood claims, and D0 numeric regression. Test log hashes, commands and counts are in the evidence. `git diff --check` is required before commit.

```bash
python -m unittest discover -s tests -p 'test_module6_d1_family_grid.py' -v
python -m module6.d1_family_grid --seed module3/example.json --output-jsonl validation/module6/local/d1_inputs.jsonl --manifest validation/module6/local/d1_manifest.json
python -m module6.d1_run_grid --seed module3/example.json --inputs validation/module6/local/d1_inputs.jsonl --manifest validation/module6/local/d1_manifest.json --output-dir validation/module6/local/d1_points --summary validation/module6/d1_family_scan.json --mu-GeV 160 --mt-MSbar-160 163.96892236746697 --reference-lha-sha256 984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374
python -m unittest discover -s tests -p 'test_module6_d1_run_grid.py' -v
python -m unittest discover -s tests -p 'test_module6_coherent_pilot.py' -v
git diff --check
```

Running the CLI regenerates execution evidence; test-log metadata is added after running the suites. Raw output hashes can change with runtime environment/numerical libraries; input hashes are deterministic.

## Unresolved physics and next actionable paper path

No computational D1 blocker occurred. `constraints_complete=false`, `global_zee_acceptance=null`, `COMPLETE_LFV=false`; all flavor/LFV experimental comparisons remain `NOT_EVALUATED`. Exact one-loop LFV remains UNKNOWN; full LFV, Module4 Barr–Zee and Wgamma completion, authentic NuFIT 6.1 joint likelihood, global vacuum proof, RG closure, physical 2026 B→Xsγ rate/uncertainties/statistics, other required flavor constraints and collider likelihood are absent. No per-state 670-GeV cut, physical BR, global acceptance or discovery/exclusion prospect is inferred.

The next concrete paper step is a reproducible physically motivated scalar sampler with declared support/distribution and provenance, coupled to NO/IO inverse-family solution populations. Prioritize complete LFV and gauge completion, authentic neutrino likelihood inputs, consistent scalar vacuum/RG treatment and released flavor coefficient-to-rate response with uncertainty/statistical treatment; then compute collider production and decay observables for surviving scoped candidates. Preserve FAIL/UNKNOWN per gate. Compare actual observables with the 2017 general Zee and 2021 cascade results before any paper novelty claim. No large statistical scan is implemented here.
