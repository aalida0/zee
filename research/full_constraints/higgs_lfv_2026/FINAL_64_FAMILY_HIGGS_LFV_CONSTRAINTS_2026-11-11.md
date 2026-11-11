# Zee Type-II: final scoped Higgs + LFV checkpoint on 64 reconstructed neutrino families
**11 November 2026** · **Branch:** `research/zee-full-constraints` · **Model:** restricted Type-II Zee 2HDM with one charged singlet, two mixed charged mass eigenstates

**Status:** `HIGGS_SCOPED_H125_PASS__PHYSICAL_HIGGS_UNKNOWN` / `LFV_RETAINED_1LOOP_64_PASS__PHYSICAL_LFV_UNKNOWN`. The already validated source-defined 2026 B→Xsγ leading-NP selection favors **scalar 15673**. **No globally experimentally allowed point is established.**

## New physics calculation completed

Reconstructed all **64** constructed neutrino-consistent Yukawa families from the *exact original source* archive, uncompressed SHA-256
`e8c805dff20e7d34c5d58d07b2b47b37e033f10c97bbb744b399cedfb126359b`, using **16 original D10 sufficient-tree-vacuum scalar witnesses × NO/IO × seeds 20261111/20261112**. The original constructed-family homogeneous coefficient vector is **not portable across NumPy SVD null-basis rotations**: first reconstruct the original complex F, neutrino mass target, affine inverse `D(c)=D0+ΣcH`, then solve the two complex physical conditions `D[e,mu]=D[mu,e]=0` by minimum-norm pseudoinverse *again*. Do NOT replay saved coordinates in a new nullspace basis.

Reconstruction numerical validation:
- **64/64** fixed-target one-loop neutrino mass closures; max relative error **4.642×10⁻¹⁵**;
- max direct-neutral off-diagonal physical `D[e,mu]` or `D[mu,e]` modulus **3.476×10⁻¹⁸**;
- maximum source Yukawa-magnitude drift **2.6×10⁻¹⁷**;
- independent complete scalar one-loop `mu→eγ` Lavoura/Module3 coherent F+D+h+H+A dipoles match archived selected Module4 BR at worst **1.229×10⁻⁸ relative**;
- **64/64** selected `mu→eγ` rates are below the reference MEG II 2025 90%-CL **1.5×10⁻¹³** limit. This is a retained perturbative-order pass **only**, NOT full Zee two-loop LFV.

## Higgs h125 source-reweighted results

For each of 64 new complex Yukawa families, constructed the exact tree two-body neutral charged-lepton widths with full complex chiral interference. The existing native HDECAY corrected-charm SM h125 channel ledger (source blob SHA `d33f5f2feea355a13a09c98747dc69e9914abd0c`) supplies ordinary bb/cc/ss/WW*/ZZ* inputs; the model's `κu,κd,κV` and coherent LO massive t,b,c loop reweight its channels in their **specified mixed perturbative order**. Validated existing native h125 leading one-loop γγ and Zγ partial-width ratios are reused. This is **not** a complete NNLO 2026 Higgs calculation.

| Scalar | κV | κu | κd | Coherent LO ggF ratio | h125 **known-channel sum** [MeV] | max Γ(h→μτ)/Γbb | max retained BR(μ→eγ) |
|---|---:|---:|---:|---:|---:|---:|---:|
| **15673 (preferred)** | 0.99994709 | 0.99220371 | 1.01361250 | 0.98225627 | **4.129439–4.129467** | **3.73734×10⁻⁷** | **1.97153×10⁻¹⁹** |
| 15591 | 0.99988693 | 1.01243627 | 0.98186762 | 1.02827146 | 3.995702–3.996389 | 1.65780×10⁻⁵ | 1.56956×10⁻¹⁵ |
| 2264 (control) | 0.99986286 | 0.98414399 | 1.01731127 | 0.96514576 | 4.139757–4.139961 | 1.01939×10⁻⁶ | 5.04820×10⁻¹⁸ |

At 15673 the **conditional** `mu(ggF,h→γγ)` (if the known-channel sum were the total and using matched-channel common-order normalizations) is **0.975904–0.975911**. **This is not a physical absolute signal strength** and must never be used for a HiggsTools likelihood with missing exotic/virtual channels. Width-independent same-resonance ratios (e.g. `mu(VBF,γγ)/mu(VBF,WW*)`) cancel the unknown total width at the specified order and are valid restricted model predictions, but no qualified category likelihood is run.

Nominal **direct h125 LFV upper-envelope screen**: if total partial widths are positive and the transferred Γbb remains meaningful, BR(h→ℓτ) ≤ Γ(h→ℓτ)/Γbb. All **64/64** ratios are below ATLAS JHEP 07 (2023) 166, arXiv:2302.05225 95%-CL observed upper limits **0.0020 for eτ** and **0.0018 for μτ**. Maximum over the entire constructed ensemble Γ(h→μτ)/Γbb = **1.73384×10⁻⁴**, at scalar 16385. Maximum Γ(h→eτ)/Γbb = **3.46592×10⁻⁷**. This is not a complete ATLAS signal-production/acceptance recast.

The **known-channel** h125 sum across the ensemble spans roughly 3.10–4.33 MeV, but **none is an established full Γh**. Unknown virtual exotic interference in h→4f and other channels, off-shell finite-width treatment, leading radiative h→νν, heavy H/A full widths and production, STXS theory covariance, neutral/heavy HiggsTools search interpolation and experimental signal-model qualification remain unclosed. Thus **HIGGS_PHYSICAL = UNKNOWN**.

## LFV rates, sufficient budgets and exact missing physics

The reconstructed 15673 source model's *largest selected radiative* BR(mu→eγ) over four families is **1.971527×10⁻¹⁹**, over six orders below MEG II 90%-CL **1.5×10⁻¹³**. The one-loop and selected two-loop Module4 contributions are compared only at their stated approximation. Its smallest **sufficient coherent missing dipole amplitude budget / retained norm** is ~**871** (triangle inequality), not a bound on omitted amplitudes.

Additional source-reconstructed charged singlet tensor: using `wS=sin²γ/mH1²+cos²γ/mH2²`, `C_F∝(F†F)eμ wS/(192π²)`, for ONLY a hypothetical gauge correction parallel to this known tensor `ΔC_F=[g²/(16π²)] K C_F`, the minimum sufficient maximum `|K|` at 15673 is **1.3680×10⁶**; globally all 64 have `Kcrit≥1.7107×10⁴`. The corresponding checks are independent complex source matrix contractions. **K was not calculated**, and such a criterion **does not** bound new mixed charged `F D` / W/Goldstone/ghost two-loop flavor tensors, chirality enhancements or any other gauge-invariant missing diagram class. It is an explicit materiality screen, not theory sigma.

The **original SARAH 4.15.4 generated one-loop** μ→3e and u/d/s conversion rates had previously been run on *four older original D7/F13 cards* with observed p/n scalar nucleon swap repaired, as archived in `research/full_constraints/lfv_lo_closure_2026/`. Those four-card rates **cannot** be transplanted to these new 64 Yukawa matrices; the original generated Fortran source bundle was not available in the independent current runtime and no new-family full μ→3e or muon–electron conversion rate was run. Modern QED/QCD evolution, heavy scalar/gluon matching, coherent nuclear factors and uncertainty remain missing. Selected neutral Barr–Zee terms from the corrected general-2HDM source were already incorporated in Module4; they are **not counted twice**. Physical LFV remains UNKNOWN because full signed operator assembly, gauge/mixed Zee diagrams and a justified omitted-term envelope are incomplete.

## Exact accepted scope versus rejected claims

| Gate | Accepted on 64 families | Model-wide exclusion |
|---|---|---|
| Exact Zee neutrino inverse, constructed perturbative texture | PASS at declared 1-loop neutrino order | Not oscillation global-fit certification |
| μ→eγ scalar one-loop / retained Module4 | PASS at declared order, all 64 below MEG II | **UNKNOWN** gauge-complete mixed two-loop |
| Direct h125→μτ/eτ partial-width upper-envelope | 64/64 nominal source ratio screen below ATLAS bounds | Not full ATLAS production/acceptance likelihood |
| h125 width-independent coupling / photon ratios | Calculated in retained mixed order | Not model HiggsSignals χ² |
| h125/H/A physical total width, HiggsTools search limits | Not obtained from source channel sum | **UNKNOWN** |
| μ→3e complete new-family penguin/Z/box/coherent amplitude | Not executed on new Yukawas | **UNKNOWN** |
| μ−e conversion modern hadronic/nuclear scheme on new Yukawas | Not executed on new Yukawas | **UNKNOWN** |
| Global Zee physical acceptance | **null** | **NONE CERTIFIED** |

**Physics recommendation:** Keep scalar **15673** as the paper's best **conditional** charged-cascade benchmark. A realistically scoped phenomenology paper may apply source-defined leading B, Higgs and LFV screens and report approximation/materiality sensitivity; it may **not** claim a globally allowed scan, all-orders full constraints, a full 95%-CL HiggsTools exclusion or complete Zee LFV.

## Full numeric archive / source-replay package

In the associated conversation generated a downloadable **SHA-256 manifest-checked zip** `zee_Higgs_LFV_64_final_scoped_evidence_2026-11-11.zip` with:
- the exact original 64-family source JSON zip;
- portable physical SVD-invariant reconstruction code `zee_64_higgs_lfv_reconstruction.py` and **all 64 full complex F/D Yukawas and h125 partial-width channel data**, `zee_64_reconstructed_yukawa_higgs_lfv_2026-11-11.json`;
- charged F-only gauge dressing conditional code, results, 16-scalar summary CSV;
- **five passing fail-closed regression tests**, source manifest, independent h125 width-free ratio sanity crosscheck and a detailed standalone markdown report.

Recompute with Python3 + NumPy + mpmath:
```sh
python zee_64_higgs_lfv_reconstruction.py zee-16-scalar-64-neutrino-families.zip --output /tmp/zee-reconstructed-new.json
python zee_64_restricted_F_two_loop_materiality.py --source-zip zee-16-scalar-64-neutrino-families.zip --family-json zee_64_reconstructed_yukawa_higgs_lfv_2026-11-11.json --output /tmp/zee-F-check.json
python -m unittest zee_higgs_lfv_64_test_gate -v
```
Tests are *consistency tests*, not a complete model experimental validation.

**Frozen verdict:** `HIGGS_SCOPED_64_H125_VALIDATED__HIGGS_PHYSICAL_UNKNOWN`, `LFV_SCOPED_ONELOOP_64_VALIDATED__LFV_FULL_GAUGE_UNKNOWN`, `GLOBAL_ACCEPTANCE=null`.
