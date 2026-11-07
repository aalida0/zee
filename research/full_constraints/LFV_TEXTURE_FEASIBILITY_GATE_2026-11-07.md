# Zee charged-cascade paper: neutrino-compatible LFV texture feasibility and a **quantitative approximation gate**

**Date:** 2026-11-07. **Status:** SOURCE-BACKED REANALYSIS OF EXISTING RESULTS; **NO NEW MODEL POINTS, NO NEW AMPLITUDES, NO SCAN**.
**Research branch:** `research/zee-full-constraints`. We analyzed saved D12 neutrino-family and Module4/2026-11-07 dipole evidence. Companion results: [TEXTURE_MATERIALITY_DIAGNOSTIC.json](lfv/TEXTURE_MATERIALITY_DIAGNOSTIC.json); reproducible local calculation [texture_materiality_gate.py](lfv/texture_materiality_gate.py). Primary original evidence: [D12_FLAVOR_COLLIDER_AUDIT.md](../../module12/D12_FLAVOR_COLLIDER_AUDIT.md), [D12 JSON](../../validation/module12/d12_benchmarks.json), and [PRACTICAL_SENSITIVITY.json](lfv/PRACTICAL_SENSITIVITY.json).

## Executive result

**The most important texture/physics study had ALREADY been done in D12.** The D12 dataset contains **112 constructed neutrino-inverse-family solutions** plus **24 actual ±1% homogeneous-coefficient perturbations** (136 evaluated solutions), at two separately tree-vacuum-certified scalar spectra, for NO and IO. The homogeneous freedom was used to solve the **four real conditions** `D_eμ=D_μe=0` at fixed reconstructed neutrino masses. This is algebraic texture choice, not a statistically representative scan, naturalness proof, all-loop symmetry, or full LFV viability.

The selected low-LFV textures keep both the one-loop neutrino reconstruction and the **charged cascade tree branching ratios** essentially intact, despite huge differences in the *calculated subset* of `μ→eγ`. The earlier central F13 and D7 dipoles exceed the measured limit, but the family itself demonstrably contains low-subset-rate witnesses. **Thus do not discard the charged cascade because the arbitrary central Yukawa solutions look bad.**

### Exact quoted original D12 measurements (rounded source table)

| scalar/ordering | BR(μ→eγ) retained: central | BR retained: low_joint | suppression | BR(H₂→H₁Z) low | BR(H₁→tb) low | selected family |
|:--|--:|--:|--:|--:|--:|:--|
| D7 NO | 1.387e−10 | 1.561e−19 | 8.89e8 | 0.045477 | 0.996718 | texture_0.0001 |
| D7 IO | 3.232e−10 | 1.086e−18 | 2.98e8 | 0.045477 | 0.996717 | texture_0.0001 |
| F13 NO | 1.785e−12 | 4.031e−20 | 4.43e7 | 0.485020 | 0.997594 | texture_0.001 |
| F13 IO | 4.159e−12 | 1.338e−19 | 3.11e7 | 0.485020 | 0.997551 | texture_0.001 |

These quoted BRs are **7 one-loop terms plus 27 fermion/photon and 6 physical charged-scalar/photon two-loop terms**, coherently summed in Module4. The actual Wγ and other gauge/charged-current groups are not included; the numbers are **neither upper nor lower bounds** on the full model's physical decay rates.

**F13 fixed scalar spectrum** `mH1=572.2316244 GeV, mH2=873.2076828 GeV`, `tanβ≈5.308`, `γ≈1.08895`. Its low-texture BR(H2→H1Z) is 48.502%, BR(H1→tb) is ~99.759%, hence the cascade-to-tb product ~48.385%. Both neutrino orderings have closure residuals ~1e−15 on the saved low witnesses. The D7 scalar, by contrast, has only 4.548% cascade BR and is less attractive for a collider reach study.

The source D12 report already identified the 2021-cascade versus 2017-Zee-flavor gap but **did not establish a paper novelty**. The correct question is now whether realistic LFV filters leave observable-cascade spectra/textures, not whether neutrinos can be reconstructed.

## New quantitative gate: what must omitted LFV terms be smaller than?

Use the common complex dipole convention
`L_D=(e mμ/2) (bar e σμν (C_L PL+C_R PR) μ) Fμν + h.c.`, with `[C]=GeV⁻²`.
Let `n=√(|C_L|²+|C_R|²)`. On the fixed muon and α input, `BR∝n²`.
For MEG II's version-pinned **90% CL** measured limit `BR_lim=1.5e−13`,
the limit norm obtained from the *exact stored central complex coefficients*
is **`n_lim=1.367785824084e−12 GeV⁻²`** for all four groups.

The low-texture norm is reconstructed from the same coefficient/BR normalization: `n_low = n_lim √(BR_low/BR_lim)`. For any *combined* omitted complex amplitude vector `Δ=(ΔC_L,ΔC_R)`, the triangle inequality gives a useful **sufficient** (not necessary) condition for passing the limit:

`||Δ|| <= n_lim − n_low`.

| spectrum/order | central norm GeV⁻² | selected low norm GeV⁻² | **maximum omitted norm sufficient for a pass** GeV⁻² | central cancellation fraction required if excluded? |
|:--|--:|--:|--:|--:|
| D7 NO | 4.160e−11 | 1.395e−15 | **1.36639e−12** | 96.71% |
| D7 IO | 6.349e−11 | 3.680e−15 | **1.36411e−12** | 97.85% |
| F13 NO | 4.719e−12 | 7.091e−16 | **1.36708e−12** | 71.01% |
| F13 IO | 7.202e−12 | 1.292e−15 | **1.36649e−12** | 81.01% |

**These are NOT estimates or upper bounds of the actual gauge/charged-current/renormalization contributions**. They are *numerical targets* for a future source-based bound. If an independently justified bound on their **combined coherent norm** falls below ~`1.36e−12 GeV⁻²`, the selected NO and IO textures pass the `μ→eγ` limit *at that declared accuracy*. If not, keep `UNKNOWN`. No generic `O(α/4π)` assertion without model-specific chiral/Yukawa evidence is acceptable.

### What the saved ±1% perturbations actually say

D12's original 24 runs perturb the **native homogeneous coefficients** by factors 0.99 and 1.01, preserving exact neutrino closure through the inverse solver. They are a **single coefficient direction test**, *not* full eight-real-dimensional tuning robustness or RG stability.

At the common `texture_0.001` design (not necessarily the D7 discrete minimum), the retained BR ranges are:
- D7 NO: **1.369–1.406e−14** (below 1.5e−13); D7 IO: **3.203–3.261e−14** (below).
- F13 NO: **1.732–1.838e−16** (below by >800 times); F13 IO: **4.077–4.242e−16** (below by >350 times).

**Important nuance:** D7's `low_joint = texture_0.0001` becomes **~1.387e−12 (NO)** / **~3.232e−12 (IO)** under the same ±1% deformation, *above* the limit in the retained subset. Thus the most tiny nominal BR is **not automatically the most robust texture**. The `texture_0.001` family is the more defensible example for assessing practical LFV suppression, including on D7. We still lack full neighborhood/loop stability.

### `μ→3e` does not currently overrule the texture argument

D12's `mu→3e` *neutral-scalar tree* vanishes numerically at the targeted direct-eμ-zero textures (the report calls this “numerical zero,” below its reporting threshold). However photon monopoles, Z/scalar penguins and the coherent four-lepton boxes are not evaluated as a validated complete signed vector. The 2026-11-07 independent pure-dipole flavio rate control agrees with the frozen dipole-only scaling at the ~1.65% parameter/running-level difference. **Do not report BR(μ→3e)=0, or a physical μ→3e PASS**. The 2017 general Zee paper includes these observables in its restricted scan; a defensible reevaluation is required for any comparative statement.

## Remaining physics gaps & release priorities (stop endless toolchain work)

1. **Immediately freeze FlexibleSUSY attempts.** FormCalc alone works; SARAH+FeynArts+FormCalc same-kernel is blocked. Our frozen native SARAH/FlavorKit and published analytical/reference models are sufficient for the present limited objective.
2. **Evaluate missing `μ→eγ` terms only at four existing **low_joint** D12 cards and, if nearly free, the D7 `texture_0.001` ±1% cards already evaluated.** For missing gauge/Wγ, Zγ, charged-current and F†F dressing, use actual published two-loop 2HDM expressions (post-2026 erratum) *only in valid model limits*; estimate untransferable Zee contributions with a transparent per-topology power-counting envelope if the relevant chiral structures are known. Never treat a loop factor alone as an unconditional upper bound. Do not import validated Module4 fermion/photon or charged-scalar/photon twice. No new analytic two-loop research projects.
3. **Decisive numeric criterion:** derive an actual model-specific upper bound on the **combined** missing two-component dipole vector and compare with `1.364e−12 GeV⁻²` (conservative common four-card sufficient target). If no defensible bound can be given from sources/couplings, keep LFV `UNKNOWN` and explicitly scope the paper as conditional rather than claiming measured exclusions.
4. **Next: `μ→3e` at selected F13 textures.** Reuse published full tree+penguin+box operator machinery and independent flavio rate matching; do *not* mistake tree-zero for full.
5. **Paper-level downstream:** One parameter scan requires separate user authorization and a frozen constraint prescription. Production at the **exact D7/F13 spectra** remains `NOT_EXECUTED`; do not substitute a mass-matched but otherwise different F14 MG5 cross section. F13's historical B→Xsγ legacy value ~3.887e−4 vs measured central ~3.49e−4 still needs defensible theoretical uncertainty; Higgs signal-rate coverage and quantum vacuum/RG remain unknown. The verified tree-level global-vacuum witness is not quantum stability.

## Honest publication verdict

**Promising, but conditional.** An interesting, interpretable physical possibility is already demonstrated **at the retained-calculation level**: low-LFV neutrino textures with an undiluted ~48.5% cascade. This is not yet a global physically allowed point, an HL-LHC reach, or established novelty relative to the combined 2017 Zee+2021 charged-Higgs literature.

The paper's sensible emphasis should be a **matched neutrino/LFV-constrained scalar-cascade study**, with collider prospects only after an actual production and background feasibility assessment. A modest publication does not require brand-new general two-loop formulae, but it cannot suppress unknown interfering amplitudes by fiat.

## Reproduction and immutable evidence

The companion `lfv/texture_materiality_gate.py` reads saved original D12 results, source-locked central amplitudes and experimental limits, applies the geometric identity and writes JSON to stdout/scratch. No new physics packages, minimizations or neutrino reconstructions.
```bash
python3 research/full_constraints/lfv/texture_materiality_gate.py --output /tmp/zee-texture-gate.json
```
The committed `lfv/TEXTURE_MATERIALITY_DIAGNOSTIC.json` uses the **rounded D12 audit table** for low-texture BR and cascade products, while the script uses complete D12 JSON precision. Tiny numeric differences at the table's significant-digit level are expected. Treat the script's recomputation as independent arithmetic **only**; neither result supplies a physical omitted-amplitude estimate or exclusion. The original D12 dataset is ~1.75 MB and is never rewritten. `physical_lfv=UNKNOWN`, `global_acceptance=null`, `new_parameter_points=0` remain mandatory.
