# Gate C3 — bounded scan triage (2026-10-27)

**C3_EXPLORATORY_SCAN_DIAGNOSTIC_PASS; C3_QUADRATIC_SOURCE_NOT_READY.**
**2026_LINEARIZED_FLAVOR_FILTER_READY=false; FULL_ZEE_ALLOWED=NOT_EVALUATED.**
NO-GO for a complete validated nonlinear calculation from the inspected inputs. Curvature and its validity domain remain unknown. No physical BR, exclusion, or charged-mass cut is produced. [Machine-readable evidence](../validation/module5/scan_triage.json) contains actual outputs and byte hashes.

## Bounded source feasibility

Inspected the pinned publications, their abstract/source-access listings, the actual companion data link (reference 64), and the immediately cited rate frameworks below. All listed HTML/data downloads succeeded through curl; the browser reader could not access the KIT page and some older HTML. No broad software search or rate reconstruction was undertaken. Exact revisions, downloaded-byte SHA256, access and license records are in the evidence JSON; the two 2026 HTML hashes match C2. No ready complete high-scale response was found in this bounded inspection.

Basis throughout the retained C1 calculation: ordinary Q7=e mb/(16 pi²) (bar s_L sigma b_R) F and Q8=gs mb/(16 pi²) (bar s_L sigma T^a b_R) G, positive weak interaction Lagrangian / negative Hamiltonian. The ordinary Q1–Q6 basis and NDR scheme are fixed by companion Eq.(13)–(14) and its reference 65 Eq.(4); effective dipoles are a different finite basis at NLO. C2 certifies ordinary P4/P7/P8 matching, not the rate.

| Candidate / revision | Basis, scales, cut, baseline | Numerical input, order, scheme, access/license | C7/C8 curvature **and** C4? |
| --- | --- | --- | --- |
| [Letter 2608.29863v1](https://arxiv.org/html/2608.29863v1), Sec. IV Eq.(4) | Eq.(2) ordinary dipoles; mu0=160 GeV; Eγ>1.6 GeV; SM 3.54e-4 | Slopes −8.51, −2.16 only; generic LO NP on updated SM QCD calculation; no numeric quadratic tensor or C4 response. Open HTML, CC BY 4.0. | No; quadratic NP terms explicitly omitted. |
| [Companion 2608.29864v1](https://arxiv.org/html/2608.29864v1), Eqs.(3),(10),(13)–(17), Apps. A–C | Ordinary Q basis / NDR coefficients; high mu0 to low mu_b running required; cut 1.6 GeV, except stated uncut non-BLM G17/G27 approximation; SM 3.54e-4 | Low-scale bilinear framework; F1/F2 fits, HQE inputs/correlation matrix, kinetic normalization. Updated NNLO treatment with stated incomplete channels; not a ready high-scale response array. Open HTML, CC BY 4.0. | No complete portable numeric tensor/executable located. |
| [Actual KIT data page](https://www.ttp.kit.edu/preprints/2026/ttp26-034) and [archive](https://www.ttp.kit.edu/_media/progdata/2026/ttp26-034.tar.gz), unversioned, byte-pinned 2026-10-27 | O2–O7 interference notation tied to 1702.07674; z=mc²/mb², w=(1−sqrt(1−4z))/(1+sqrt(1−4z)); no mu0=160 rate interface, cut configuration or SM baseline | Archive **2793 bytes**, only `README` (1542) and `G27_3P.m` (10310); analytic three-particle-cut two-loop charm functions with HPL continuation conventions. Scheme requires cited definitions; not a standalone scheme specification. No LICENSE or independent code reuse grant established. Inspected, not executed. | No C7²/C7C8/C8² response, evolution or C4. |
| [1503.01791v1](https://arxiv.org/html/1503.01791v1) and [1503.01789v1](https://arxiv.org/html/1503.01789v1), companion refs. 34/35 | Ordinary Q1–8 NDR framework (definitions cited therein); mu0=160 for generic NP formula; Eγ>1.6 GeV; SM 3.36e-4 | Historical NNLO/interpolated charm framework, low-scale kernels and linearized NP formula; old semileptonic normalization. No complete 2026 tensor. Open HTML; arXiv publication license, no standalone software license established. | No validated 2026 joint response. |
| [2002.01548v2](https://arxiv.org/html/2002.01548v2), companion ref. 69 | Ordinary Q1–8, weak Lagrangian Eq.(4), NDR framework; EW-to-bottom evolution; Eγ>1.6 GeV; SM 3.40e-4 | Partial NNLO G27 update and historical P+N normalization, not a 160-GeV 2026 executable. Open HTML, arXiv publication license. | No complete 2026 joint response. |
| [1702.04571v1](https://arxiv.org/html/1702.04571v1), Letter ref. 41 | Ordinary Q basis Eqs.(2)–(4); common EW matching, low-scale evolution; 1.6-GeV default; historical Rγ SM 3.31e-3 | One-state higher-order 2HDM and statistical prescriptions using 2015 inputs; not 2026 response data. Open HTML, arXiv publication license. | No reusable validated 2026 tensor including generic C4. |

The SM–NP interference requires the full SM coefficient vector and evolution, even when NP C1/C2 vanish at matching. The low-scale bilinear alone does not numerically determine the high-scale curvature. To reproduce the published precision one must retain its approximations, scheme conversions, cut prescription and normalization. Reassembling all of this would require rebuilding and independently validating the updated rate pipeline, which triggers this gate’s stop condition. Older rates cannot be rescaled to 3.54e-4. No guessed curvature, plot digitization, C4-negligibility assumption, or new multi-loop calculation is used.

Missing: (1) versioned high-scale interference vector and quadratic C7/C8 tensor with perturbative truncation specified; (2) consistent NLO C4 evolution, ordinary/effective conversions and rate interference with all relevant SM operators; (3) the 2026 kernel/evolution/input configuration, kinetic normalization and Wilson-dependent HQE/resolved-photon terms; (4) independent numeric zero-NP and one-state benchmarks plus source/reuse provenance. A publication’s HQE parameter covariance is not the model-NP or SM/experiment covariance.

## Executed exploratory diagnostic

The unchanged C1 `run_contract` is called for every point. The wrapper now retains its status and source URL, hashes the frozen implementation/convention files, validates explicit finite inputs, rejects duplicate physics points as well as duplicate labels/JSON keys, and fails closed on overflow. Coefficient/source/basis tampering is tested through C1. No C0 patch or C2 NLO matching enters Eq.(4).

**8 scan tests + 11 frozen C1 tests = 19 PASS**, zero failures/errors/skips. The independent 60-digit Decimal oracle uses literal published numbers and checks five points across ten assumptions (50 pulls, rho=−1,−0.5,0,0.5,1; NP sigma=0,0.2). Tests also check original CLI input bytes SHA256, implementation hashes, no physical classification, unknown fields, missing top, wrong scale, booleans, nonfinite/overflow inputs, duplicates and unchanged output on invalid input. These are formula/integrity checks, not physical-rate validation.

All five points use tanβ=5.3, mt_MSbar(160)=163.96892236746697 GeV and matching scale 160 GeV. The reference top is inherited from C1’s specified input, not recalibrated to 2026. Points are illustrative and have **not** been checked for scalar stability, neutrino/LFV, other flavor, collider or full Zee constraints. Rates/shifts/differences below are conditional linear quantities in units 10⁻⁴.

| mH1,mH2 [GeV]; γ | ΔC7 | ΔC8 | NP shift | Eq.(4) central | central−experiment | pull A | pull B | pull C | pull D |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 550,900; 1.09 | -0.03737804303 | -0.04231149396 | 0.4094799732 | 3.949479973 | 0.4594799732 | 1.946879 | 1.485288 | 1.601647 | 2.693519 |
| 550,900; 0 | -0.05960262467 | -0.06447194325 | 0.6464777334 | 4.186477733 | 0.6964777334 | 2.951071 | 2.251393 | 2.427769 | 4.082825 |
| 550,900; 1.5707963 | -0.03133093447 | -0.03628183524 | 0.3449950165 | 3.884995016 | 0.3949950165 | 1.673648 | 1.276838 | 1.376866 | 2.315502 |
| 800,1300; 0.3 | -0.03519325886 | -0.04026360669 | 0.3864640234 | 3.926464023 | 0.4364640234 | 1.849357 | 1.410888 | 1.521418 | 2.558597 |
| 2000,3000; 1.09 | -0.006057503544 | -0.007707077904 | 0.06819664343 | 3.608196643 | 0.1181966434 | 0.500815 | 0.382075 | 0.412008 | 0.692881 |

Every pull is **HYPOTHETICAL**. A: rho=0, NP sigma=0; B: rho=0, NP sigma=0.2; C: rho=−0.5, NP sigma=0; D: rho=+0.5, NP sigma=0. All NP sigmas are in 10⁻⁴, independently chosen for illustration. Scenario sigmas are respectively 0.2360084744, 0.3093541660, 0.2868797658, 0.1705872211.

`pull = (linearized central − 3.49) / sqrt(0.14² + 0.19² − 2 rho 0.14 0.19 + assumed_NP_sigma²)`

At the reference point, A→B changes 1.946879→1.485288 (about 24% lower); C→D changes 1.601647→2.693519. This is substantial sensitivity to assumptions. A pull around two does not justify a 95%-CL exclusion. The scenario choices are not a calibrated NP error budget, and C2’s −0.0721940895e-4 dipole-only increment is neither a corrected BR nor a one-sigma error. There is no universal 10% applicability threshold.

Separately unresolved: the SM/experiment error correlation; independent versus shared/correlated model-NP nuisances (including correlations among scan points and with SM inputs); Gaussian versus other nuisance distributions; profiling versus marginalization; one-/two-sided CL and ordering/coverage prescription; and the physical quadratic validity domain. The tool evaluates a stated Gaussian variance for each point; it supplies no likelihood or cross-point covariance. Quoting 0.14 and 0.19 separately resolves none of these.

## Most efficient next physical task

Obtain an author-maintained 2026 coefficient-to-rate executable or numerical response tables and a reproducible input card covering ordinary C4/C7/C8, with versions, scheme, cut, normalization, perturbative truncation and access/reuse terms. This is source acquisition, not permission to reconstruct a massive rate pipeline here. If supplied, a separate bounded validation task must reproduce zero-NP 3.54e-4 and numeric one-Higgs higher-order references, probe high-scale C7 and C8 separately and jointly with both signs, check odd interference/even curvature by sign reversal, test gamma endpoints and scalar exchange, and inject C4 with consistent basis/evolution. It must also verify cut/scheme changes before bounding omitted operators, mass/scale/missing-order uncertainties and calibrating a controlled two-state validity domain. Statistical treatment follows that physical error budget.

## Reproduction

```sh
python -m unittest discover -s tests -p 'test_module5_scan_triage.py' -v
python -m unittest discover -s tests -p 'test_module5_bsgamma_2026_linear.py' -v
mkdir -p validation/module5/local
python -m module5.bsgamma_scan_triage --input module5/example_scan_triage.json --output validation/module5/local/c3_scan_example.json
```

The five-point input and compact embedded output are committed; downloaded HTML/archive and CLI scratch output remain ignored. Modules 0–4, SARAH, frozen C1/C2 physics/reports and external HyperIso are unchanged. Previous statuses are preserved.
