# D2 scoped scalar and independent inverse-family audit — 2026-10-27

**D2_EXECUTED_EXPLORATORY.** The declared source-centered neighborhood contains 35 spectra: 29 pass the scoped tree/EWPO gates, 6 fail, 0 computations are blocked. Three physically distinct scoped-passing spectra and four independent coefficient choices per spectrum produced **12/12 completed real coherent points**. Execution success is not physical acceptance. All twelve full vacuum searches remain **UNKNOWN**; `constraints_complete=false`, `global_zee_acceptance=null`, `COMPLETE_LFV=false`, `2026_LINEARIZED_FLAVOR_FILTER_READY=false`.

## Scope and independent prefilter audit

This separate checkout is on `feature/zee-d2-scalar-prefilter-yukawa`, descended from validated D1 `e486d8e8aefac0248bc664b0cf5eb2a251994b65`. The parent checkout already ignores `/workspaces/` in its local `.git/info/exclude`; no other checkout was modified. Modules0–5, SARAH, D0/D1 code/tests/audits/hashes remain unchanged. No historical suite, external HyperIso runtime, LO/NLO loop-matching audit, SARAH generation or 2026 nonlinear search was repeated.

The prewritten screen had a wrong EWPO result-field lookup, silently returning null chi2. D2 now reads the selected fit from `alternative_fits_not_combined`, validates the nested Module2 schema, checks all three IDs and explicit vacuum configuration, rejects embedded stale Module2 output, and retains earlier gate evidence if a later evaluation errors. Structural controls cover immutability, stale hashes, invalid models/types/IDs, nonfinite offsets, UNKNOWN and computation errors. Every spectrum binds the full Module1 input, including its ID, to a recomputed canonical SHA.

The unchanged declared support is SOURCE + 26 signed one-coordinate perturbations + 8 correlated perturbations; it is a deterministic development neighborhood, not a sampling prior or confidence region. All 35 screen records, offsets, scalar SHAs, masses, STU values and gate assessments are retained in the tracked evidence. Vacuum, neutrino, LFV and quark flavor are NOT_EVALUATED during screening.

| Screen gate | PASS | FAIL | UNKNOWN |
|---|---:|---:|---:|
| reconstruction | 35 | 0 | 0 |
| bfb | 32 | 3 | 0 |
| unitarity | 31 | 4 | 0 |
| ewpo | 35 | 0 | 0 |

Cumulative cutflow: 35 reconstruction → 32 sufficient-BFB → 29 tree-unitarity → 29 selected scalar-EWPO. The six rejected spectra are:
- `mh2_m15p0`: bfb FAIL.
- `mh2_p15p0`: unitarity FAIL.
- `mh2_m35p0`: bfb FAIL, unitarity FAIL.
- `mh2_p35p0`: unitarity FAIL.
- `correlated_04`: unitarity FAIL.
- `correlated_05`: bfb FAIL.

## Selection and scalar physics

Source then greedy maximin squared distance in (mH1/10,mH2/15,gamma/.02); ties use all five STEP-normalized fields then ascending name; physical duplicates removed. No flavor value or experimental flavor cut used.

No conditional flavor prediction was used in selection. Maximin picks the two ±50 GeV charged-mass changes; neutral-only records with identical charged masses/mixing were not counted as additional flavor diversity. All other scalar, electroweak and search inputs retain their exact source values. Each selected record was independently reconstructed and checked with the frozen Module1 interfaces; its STU vector and chi2 exactly equal the screen values. SOURCE reproduces pinned D0 chi2 **0.8726172333959237**.

| Spectrum | mH1/mH2 GeV | gamma | S | T | U | chi2 | max unitarity eigenvalue |
|---|---|---:|---:|---:|---:|---:|---:|
| source | 300/700 | 1.089 | 0.00444043302066 | -0.00490217831758 | 5.73370811303e-05 | 0.872617233395924 | 18.1367790857304 |
| mH1_m50p0 | 250/700 | 1.089 | 0.00755828686658 | -0.00196597112951 | 0.000190964613331 | 0.805159084975881 | 18.1345583632225 |
| mH1_p50p0 | 350/700 | 1.089 | 0.00192682152932 | -0.00277524647011 | -2.22415780604e-07 | 0.573373941802206 | 18.1395969686551 |

All three selected spectra have reconstruction PASS, sufficient BFB PASS, 55-state tree unitarity PASS (<8π), and selected Gfitter scalar-only STU PASS (chi2 <7.814727903251179). mh1=125, mh2=580.7, ma=633.7 GeV, alpha=1.398, beta=1.394, gamma=1.089 rad. The EWPO-failing D1 450/850 GeV control is absent.

Each of the twelve points ran the frozen full vacuum search afresh, without memoization or skipped evaluations: 300 attempts per point, two original seeds 123/104852, starts=64, charts 66+66+18 per seed, field bound 12v. Total: 3,600 attempts, 3,528 credible stationary minima, 72 rejected/nonconverged, 0 boundary hits, no deeper witness. Every point has `all_attempts_converged=false`, `global_stability_proven=false`, vacuum UNKNOWN and scalar pipeline UNKNOWN. Scoped passing does not establish vacuum or global scalar acceptance.

## Independent complex inverse directions

The exact source four-complex vector is (1e-7+2e-7i, -2e-7+0i, 3e-7-1e-7i, 1e-7+3e-7i). The zero imaginary component is inherited from the source. Every spectrum uses:

- `baseline`: unchanged vector.
- `index0`: only c0 multiplied by 12 exp(0.7i).
- `index2`: only c2 multiplied by 18 exp(-1.1i).
- `mixed13`: only c1 multiplied by 9 exp(0.4i), and c3 independently by 15 exp(1.3i).

These fixed development directions are not common rescalings or a probability prior. Component bounds are checked before multiplication (1e-3/36), followed by a finite complex-vector bound |ck|≤1e-3; this is an overflow guard, not a perturbative-validity certificate. All coefficient vectors, changed indices, polar/Cartesian multipliers, physical inputs and canonical hashes are recorded per point. All three benchmark IDs and the full nested scalar SHA are rebuilt, and both nested schemas validated before execution. Equal physical spectra have different full scalar hashes because their benchmark IDs differ.

Each point called the real frozen `coherent_pilot.pilot` (Module1 scalar, Module2 inverse, Module3 scalar-LFV subset, Module5 conditional flavor) and a separate real `module2.interface.evaluate`. Complete independent neutrino output hashes must agree. Tests additionally execute Module2 afresh on all twelve generated inputs and recompute their complex target residuals, D hashes and coupling maxima. No fake conjugations or substituted matrices were used.

The exact illustrative NO target is unchanged: canonical target SHA `4f9a9e2fe7cadcfb44052bf919568f1929488e3e9eafd903264daddf49c5e7d1`. It is not an official NuFIT joint likelihood. The closure tolerance is the independently inspected frozen Module2 forward gate 2e-9 (`module2/interface.py:148`), chosen before D2 results, not the largest observed D1 residual. Actual relative errors range from 1.0685014e-15 to 3.7258778e-15; maximum absolute complex entry error is 1.7149213e-16 eV. The maximum slightly exceeds D1’s observed 3.50e-15 but is far inside the unchanged frozen tolerance.

| Spectrum/family | relative target residual | mu→eγ subset BR | Γ(h→eτ) GeV | Γ(H→muτ) GeV |
|---|---:|---:|---:|---:|
| source/baseline | 3.029e-15 | 5.11705975942e-19 | 7.50525358974e-18 | 1.60218951394e-09 |
| source/index0 | 2.837264e-15 | 5.11738235638e-19 | 5.63987381123e-18 | 1.60215917728e-09 |
| source/index2 | 2.836173e-15 | 5.11315281267e-19 | 5.74910390728e-16 | 1.60152899487e-09 |
| source/mixed13 | 3.725878e-15 | 5.12842049258e-19 | 2.84745121976e-16 | 1.60255386057e-09 |
| mH1_m50p0/baseline | 1.295278e-15 | 1.04692312515e-18 | 7.05046604969e-18 | 1.08502082754e-09 |
| mH1_m50p0/index0 | 1.392735e-15 | 1.04688606917e-18 | 1.8066759824e-17 | 1.08491798525e-09 |
| mH1_m50p0/index2 | 1.068501e-15 | 1.04862410209e-18 | 4.84778757203e-16 | 1.08457896605e-09 |
| mH1_m50p0/mixed13 | 1.67312e-15 | 1.0487054295e-18 | 4.67231058129e-16 | 1.08544771373e-09 |
| mH1_p50p0/baseline | 2.124922e-15 | 2.78834162904e-19 | 9.25228573654e-18 | 2.3940568574e-09 |
| mH1_p50p0/index0 | 2.241083e-15 | 2.78820148493e-19 | 2.09493990368e-17 | 2.39398831715e-09 |
| mH1_p50p0/index2 | 2.080164e-15 | 2.78876419416e-19 | 6.22460520397e-16 | 2.39325286189e-09 |
| mH1_p50p0/mixed13 | 2.082167e-15 | 2.78887292768e-19 | 3.2024233381e-16 | 2.39452799512e-09 |

All three radiative subset BRs, nine neutral-Higgs LFV partial widths, complex inverse residuals, Frobenius norms of F/D/Ye/Ye2/Mnu, maximum entries of F/D/Ye/Ye2, gate statuses and source/output hashes are in the compact evidence. Full paired real/imaginary matrices and scalar search details remain ignored locally. Norms and maxima are diagnostics only.

| Spectrum | mu→eγ max/min | Γ(h→eτ) max/min | Γ(H→muτ) max/min | distinct D matrices |
|---|---:|---:|---:|---:|
| mH1_m50p0 | 1.00173787806 | 68.7583989181 | 1.00080099994 | 4 |
| mH1_p50p0 | 1.00024081572 | 67.2764047849 | 1.00053280339 | 4 |
| source | 1.00298596198 | 101.936747163 | 1.00063992954 | 4 |

F is unchanged within each spectrum (indeed across these spectra because its inverse null-cone choice is fixed); D and Ye2 change across the four directions. The mu→eγ subset responds only weakly (0.299%, 0.174%, 0.0241% for source/250/350 GeV), as does Γ(H→muτ). Γ(h→eτ) responds strongly in relative terms but remains extremely small in absolute units. At source, index0 lowers Γ(h→eτ), while index2 raises it; no monotonic or general physical correlation follows. All zero conditional-flavor changes and nonzero LFV variations are retained rather than presupposed.

## Signed conditional flavor falsifiers

| Spectrum (all four families) | DeltaC7 | DeltaC8 | conditional value in 10^-4 |
|---|---:|---:|---:|
| source | -0.059553544443998449 | -0.062999183819590174 | 4.1828789002687419 |
| mH1_m50p0 | -0.06428360601034018 | -0.066543364243477759 | 4.2307871539139068 |
| mH1_p50p0 | -0.055903518399357255 | -0.060084672982689061 | 4.1455218352211389 |

Within each physical spectrum all three flavor quantities have **exactly 0.0 max-minus-min**, with strict equality checked. Tests deliberately change C7 by 1e-12 and require rejection. The baseline matches all four signed/numeric D0/D1 references exactly (difference 0.0): C7=-0.05955354444399845, C8=-0.06299918381959017, conditional value=4.182878900268742, mu→eγ subset BR=5.117059759419609e-19.

Relative to source, the 250 GeV charged state changes (C7,C8,value) by (-0.004730061566341731, -0.0035441804238875857, +0.04790825364516493); the 350 GeV state changes them by (+0.003650026044641194, +0.002914510836901113, -0.037357065047602944). These genuine scalar contrasts support the development hypothesis, without any experimental flavor selection.

Every flavor mass and angle is derived from the identical SHA-bound scalar used by neutrino/LFV. Matching scale=160 GeV and mt_MSbar(160)=163.96892236746697 GeV are pinned to the versioned D0/Module5 QCDHelper source, not guessed or evolved again. Original read-only reference LHA bytes were rehashed to `984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374`. Wrong scale/top/LHA, stale hashes, invalid types/IDs, invented complete-LFV and allowed/excluded claims are rejected. Full LFV, physical flavor rates and experimental likelihoods are not inferred from this conditional LO-linear diagnostic.

## Provenance, validation and reproducibility

[Tracked evidence](../validation/module6/d2_scoped_scan.json) includes the complete neighborhood and cutflow, selected scalar physics/SHAs, twelve input/output byte and canonical hashes, complete frozen D0 source map, D1 and execution-code hashes, final validation-code hashes, source-versioned top provenance, per-point runtimes and contrasts. Source canonical input SHA: `8e6d0ac27c439176f89f36c4b5ab55054ef3faf3f36abb4a4d0929675a137981`; original seed byte SHA: `6a55f774041a9d5e06bd6ea30a628bfcf5c840af0ddff30bce5f692a551c2915`. Detailed records are ignored at `validation/module6/local/d2_points/`.

Actual coherent wall time: 56.983874 s; individual times 3.1682, 2.9616, 2.9644, 3.0308, 5.4608, 5.6249, 5.4881, 5.9455, 5.7236, 5.4761, 5.4915, 5.6471 s. Exactly twelve full coherent points were attempted once; no runtime blocker occurred. After adding stricter Boolean scope guards, all twelve saved full outputs were independently replayed against input/byte hashes, summary regeneration and those guards; zero vacuum searches were repeated. Execution-time and final-validation source hashes are distinguished explicitly.

**15 scoped tests PASS**, no errors/failures/skips. Tests run from tracked evidence and do not require ignored point outputs. The final independent checks include fresh Module2 evaluations, direct frozen changed-spectrum STU, all independent coefficient directions, exact target preservation, bounds, immutability, stale scalar SHA/types/IDs/scale/top/LHA, UNKNOWN handling, exact flavor invariance and falsification, four D0/D1 pinned regressions, and rejection of invented LFV completeness/global acceptance. `git diff --check` PASS. The unchanged D0/D1 historical test suites were not rerun.

```bash
python -m unittest discover -s tests -p 'test_module6_d2_scalar_prefilter.py' -v
python -m module6.d2_scalar_prefilter --seed module3/example.json --output validation/module6/local/d2_scalar_prefilter.json
python -m module6.d2_family_runner --seed module3/example.json --screen validation/module6/local/d2_scalar_prefilter.json --output-dir validation/module6/local/d2_points --summary validation/module6/d2_scoped_scan.json --mu-GeV 160 --mt-MSbar-160 163.96892236746697 --reference-lha-sha256 984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374
python -m unittest discover -s tests -p 'test_module6_d2_*.py' -v
git diff --check
```

Rerunning the runner performs twelve fresh full vacuum searches and overwrites execution evidence; do so only for a new justified calculation. Tests perform no vacuum searches. CLI writes are restricted to the scoped D2 summary and ignored local directory.

## D3 decision and unresolved physics

**CONSIDER_DECLARED_PRIOR_IO_AND_DECAYS:** three distinct scoped-tree/EWPO-passing scalar spectra and four independent inverse solutions per spectrum have been demonstrated. The h→eτ partial-width response is nontrivial; the radiative subset and H→muτ response is small. This satisfies only the stated development gate for considering a genuine declared-prior sampler, IO and collider decay observables. It does not justify a global prior, a population correlation, a paper novelty claim or a discovery prospect.

All scalar vacuum gates remain UNKNOWN. Full LFV and Wgamma/other dipole completion can qualitatively alter radiative rates. Authentic NuFIT joint likelihood/data comparison, RG closure, collider acceptance, full calibrated 2026 quark-flavor rate, uncertainties and statistics remain unresolved. There are no experimental LFV cuts, per-state mass cuts, allowed/excluded points or global viability flags. Any first-paper plot remains explicitly exploratory until missing LFV/Wgamma and precision flavor calibration are resolved or excluded from the claimed constraints. The 2017 general-Zee / 2021 cascade prior-art audit is required before novelty claims and was intentionally outside this task. No publication plot or expanded scan was produced.
