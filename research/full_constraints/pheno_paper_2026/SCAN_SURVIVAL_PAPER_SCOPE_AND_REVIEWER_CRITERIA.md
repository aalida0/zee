# Paper objective and sampling protocol — corrected after reviewer audit
**Date:** 11 November 2026  
**Branch:** `research/zee-full-constraints`  
**Working aim:** *Does the previously proposed charged-Higgs cascade in the Zee model survive updated scalar, neutrino, lepton-flavor, B-physics and Higgs-sector constraints, and where can it remain observable at the LHC?*

## Exact question and precedence

The scientific target is **the constrained parameter space**, NOT a claim to discover the (H_2^pm	o H_1^pm Z) cascade. The benchmark/production map is only a supporting second-stage observable.

We must distinguish:
- **Scalar proposals (independent sampling units)** versus **neutrino-family realizations** (conditional Yukawa solutions per scalar), so counts are never confused.
- **APPROX_COMPATIBLE** at a declared leading order versus experimental **full physical PASS**.
- **FAIL** from a validated veto versus **UNKNOWN** from a sufficient-but-incomplete vacuum certificate, absent LFV amplitudes, missing Higgs widths, or incomplete observed-search coverage.
- **A known surviving point** versus **an allowed region and its boundary**. Both the proposal prior and the scan selection efficiency must be published.
- **Predicted truth-level rate** versus **detector-level discovery/exclusion reach**.

An uncomputed observable remains `null`, not zero. A benchmark with all implemented theoretical checks and approximate flavor screens cannot be labeled globally viable unless all material experimental constraints have actually been evaluated.

## Three independent literature precedents

1. **Cascade and scalar constraints:** Florentino, Romão and Silva, arXiv:2106.08332 (2021) already established (H_2^pm	o H_1^pm Z), analyzed scalar/quark constraints, the 2HDM-II (B	o X_s\gamma) analogy, and collider benchmarks. They explicitly **did not** include a full neutrino/lepton-flavor fit. The paper must compare the *same observable* under the additional constraints. Repeating the cascade alone is not novelty.
2. **General Zee complete flavor scan:** Herrero-García, Ohlsson, Riad, Wirén, JHEP 04 (2017) 130, arXiv:1701.05345 already performed general Zee neutrino/LFV/Higgs scans. Our work must not claim first complete general Zee analysis. It is complementary **Type-II-quark/specific potential + cascade-region survival**.
3. **Constructed LFV-safe textures:** arXiv:2303.13383 (2023) provides algebraic Yukawa textures and discusses hard-to-find fine-tuned LFV-safe regions; our construction of (D_{e\mu}=D_{\mu e}=0) is not itself original. The test is whether the **same textures coexist with the cascade and other scalar/precision bounds** without reliance on excluded amplitudes.

## Existing data are stage-0 and stage-1, not the final scan

### Genuine preliminary scan, 400 unique scalar proposals (10 Nov)

Source: `research/full_constraints/scan_pilot_2026/receipt_400_20261110.json`, CI `42842354835`.

| Distinct scalar proposal gate | Count |
|---|---:|
| Original independent scalar proposals | 400 |
| Reconstruction | 400 PASS |
| BFB alone | 61 PASS; 317 FAIL; 22 UNKNOWN |
| Perturbative unitarity alone | 101 PASS |
| EWPO alone | 214 PASS |
| **Joint reconstruction+BFB+unitarity+EWPO** | **5/400** |
| D10 sufficient tree-vacuum certificate among those five | **1 PASS / 4 UNKNOWN** |
| Four neutrino families per five scalar-eligible points | **20/20** neutrino closures |
| Nominal 2026 Gaussian (B	o X_s\gamma) compatible class across all proposals | 174/400 (not an exclusion pass) |
| **Joint sufficient vacuum PASS and approximate B compatibility** | **0 / 400** |

This is a *negative finding about the sparse pilot*, not a proof the cascade is excluded. Zero joint witnesses is a reason to improve the sampling strategy and validate boundaries, **not** to promote four vacuum-UNKNOWN points to pass. Sampling fractions are conditional on these three nonuniform proposal arms; no prior-independent model-space probabilities may be quoted.

### Separate benchmark feasibility sample

**16 pre-selected sufficient tree-vacuum** scalar points from a separate 225-point campaign; **64 deliberately algebraic LFV-suppressed neutrino families**; source B leading-NP 10/16 under a one-sided Gaussian screen and three more demanding nonprobabilistic-stress survivors. These are **not independent random proposals** from the 400-point pilot. Under the known-approximation B screen, scalar 15673 is attractive, but it is not globally allowed.

Already source-verified actual LO five-flavor MG5:
- **16/16** scalar production rates at 13 TeV.
- **3/16** true native 14 TeV production rates, IDs 15591, 2264, 15673; NO mass-only interpolation for others.
- **15673** at 14 TeV: (\sigma_{tbH_2}=4.2345\) fb, new four-family (\sigma_{tbH_2}\times \mathrm{BR}(H_2\to H_1Z\to tbZ)\simeq1.6634\) fb. Before Z/top daughters/selection, `~4990` events at 3000 fb⁻¹; after just (Z\to e^+e^-,\mu^+\mu^-) (PDG 6.7294%), `~336` raw events before top decays, detector efficiencies and backgrounds. **Not HL-LHC sensitivity.**

Source-locked paper input builder: `research/full_constraints/pheno_paper_2026/paper_gate.py`, five passing CI checks and complete 64-family workflow:
https://github.com/aalida0/zee/actions/runs/43103815814
The updated PDG branching-ratio run also passed:
https://github.com/aalida0/zee/actions/runs/43104370522

## Final paper scan design and minimum required stages

**1. Unbiased, traceable baseline proposals.** Retain a reproducible multi-arm sample:
- `sub_TeV`: (m_{H_2}\in[500,1000]) GeV, original declared priors.
- `production_window_1000_1350`: (m_{H_2}\in[1000,1350]) GeV, original declared priors.
- `broad_control`: (m_{H_2}\in[500,2200]) GeV, broad parameter ranges.
The pre-existing `module14/conditional_scan/next20k_proposal.json` specifies **3:5:2 proposal weights**, not a model prior. Record arm labels and separate, denominator-correct cutflows per arm. The runner `run_conditional_pilot.py` already executes the exact module14 generate, gate, neutrino, receipt-checked collector pipeline.

**2. Sequential physically interpretable cutflow for each unique scalar candidate.**
- Correct scalar spectrum, BFB, perturbative tree unitarity.
- One-loop scalar EW precision with the documented covariance.
- Tree vacuum: `PASS` if rigorously certified, otherwise `UNKNOWN` unless a deeper state establishes a **FAIL**.
- Type-II coherent (B\to X_s\gamma) using Misiak et al. 2026 leading-NP Eq(4), **one-sided and two-sided tests separately**, with model NP uncertainty caveat.
- 125 GeV coupling/signal strengths plus all materially relevant heavy/charged Higgs observed search constraints. **Do not approximate missing heavy widths as zero**.
- Neutrino mass target at one loop with both NO/IO and deliberately **diverse** (unconstrained and algebraically LFV-suppressed) Yukawa families, retaining perturbativity.
- LFV \(\mu\to e\gamma\), \(\tau\to \ell\gamma\), \(\mu\to3e\), \(\mu-e\) conversion and (h\to \ell\tau) at a consistent declared leading order. Any missing physically relevant operator sets `UNKNOWN`.
- Preserve a three-state `PASS/FAIL/UNKNOWN` label for *each* screening observable, plus source and approximation labels. Report intersection and missing-coverage counts per scan arm; **never convert UNKNOWN into PASS**.

**3. Cascade survival map after constraints.** For the subset with a positive theory/neutrino/leading flavor screen, compute tree on-shell (\Gamma(H_2\to H_1Z)\), charged-scalar competing modes and (\mathrm{BR}(H_1\to tb,\tau\nu,\ldots)), with proper family variations. Plot survival versus (m_{H_1},m_{H_2},\tan\beta,\gamma\), and before-versus-after cuts for the **same** proposal sample. Quantify how many formerly high-BR points are eliminated, unresolved or remain viable **at each declared approximation**.

**4. Production only after flavor/scalar screening.** Compute actual LO associated (tbH_2^\pm) at 13/14 TeV for the most relevant surviving or conditional benchmark representatives, with labeled PDF/scale variation or an explicit uncalibrated theory caveat. Avoid spending MG5 resources on points already vetoed by robust checks. Compare the cascade rate against the **2021 benchmark range and equivalent final state**.

**5. Independent controls and paper claims.** Validate representative accepted/near-boundary/rejected points with a second backend or analytic limit; check source-relative efficiency and width consistency. Distinguish rare hand-engineered LFV textures from broad untuned priors. Clearly state when the constrained-survival question is **not yet scientifically answered**.

## Reviewer acceptance criteria

An EPJC-level **scan-and-survival paper**, without detector simulation or all-orders loop matching, could be defensible if:
- it contains a credible new multi-arm scan (not only the 16 selected benchmarks);
- cuts are physically justified, source-matched and reported at a declared order;
- the intersection of constraints is nonempty at that order **with adequate Higgs/LFV coverage** or an honest claim that those constraints are still conditional;
- it quantifies how a constrained region compares to 2021's cascade scenario and provides concrete collider rates or robust upper-rate bounds;
- it explicitly reports all approximation sensitivity, exclusions, unclassified regions, and scan nonrepresentativeness.

**A paper titled a 'full constraints' or 'allowed parameter space' study would currently be rejected**: complete heavy-Higgs observed-search inputs and new-family \(\mu\to3e\)/conversion and Zee two-loop LFV coverage are missing. De-scoping to leading-order constraints is reasonable **only if all leading operators that can materially dominate are included or transparently excluded from the claim**. More numerical scan points cannot repair missing physics.

## Proposed physics cutflow columns

`proposal_id,arm,scalar_hash,mH1,mH2,tanbeta,gamma,reconstruction,bfb,unitarity,ewpo,vacuum,nu_NO,nu_IO,B2026_LO_NP_1s,B2026_LO_NP_2s,h125_signals,heavy_higgs_search,LFV_muegamma,LFV_mu3e,LFV_conversion,LFV_tau,h125_LFV,dominant_cascade_BR,sigma13_or_null,sigma14_or_null,global_acceptance_or_null`

**Final question answered by the *future executed full scan*, not the benchmark snapshot:** *After imposing the specified theory, neutrino, flavor and Higgs constraints, is there a demonstrably surviving portion of the 2021 charged-Higgs cascade parameter region, and what rate could experiments target?*
