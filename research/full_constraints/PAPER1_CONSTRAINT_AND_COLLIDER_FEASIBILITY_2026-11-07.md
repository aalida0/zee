# Paper 1: scoped constraints and collider-feasibility preflight

**7 November 2026 — implementation decision and quantitative preliminary result.**
**Research branch:** `research/zee-full-constraints`. This work **does not assert a globally allowed Zee parameter space or HL-LHC sensitivity**. No new Zee points, neutrino fits, event generation, Condor jobs, or collider backgrounds were executed during this report. A **small matched-energy signal/background pilot** is the next bounded task, conditioned on finding viable existing background inputs.

## A. Paper objective, uniqueness and honest scope

Target a modest Zee **Type-II quark Yukawa plus general leptonic couplings** phenomenology paper on the chain `pp -> t H2± -> t (H1± Z) -> t (tb) Z`. The novelty must come from a **joint neutrino/flavor-specified and collider-interpretable** benchmark comparison, not the cascade vertex or ordinary Type-II production, which [Florentino–Romão–Silva, EPJC81(2021)1148](https://doi.org/10.1140/epjc/s10052-021-09956-2) studied already. General Zee `nu + LFV` scans were done by [Herrero-García et al., JHEP04(2017)130](https://doi.org/10.1007/JHEP04(2017)130) under their stated restricted quark/scalar/textural domain. An overlap of the two is scientifically useful only when it yields a *quantitative distinction or prospective experimental test*. The previously committed [PAPER1_FEASIBILITY_REVIEW.md](PAPER1_FEASIBILITY_REVIEW.md) warned against a rate catalogue as an EPJC headline.

**Paper 1 contract:** show theoretically screened scalar spectra and neutrino-compatible **specified** Yukawa textures, compare *applied leading LFV* and *approximate B* diagnostics, and test collider feasibility. All full LFV/B/Higgs physical statuses remain `UNKNOWN`; use labels `conditional / applied-subset`, not `experimentally viable`. A CLs reach claim is permissible only when matched background acceptance, uncertainties, signal efficiency and a reproducible likelihood actually exist. Full generator/detector study can still form a second paper, but the first cannot imply reach from counts alone.

## B. Pre-agreed constraint classification to freeze before one future scan

| Sector | Calculable, allowed to filter? | Paper usage | Forbidden claim |
|---|---|---|---|
| **Scalar input and positivity** | **Hard applied tree tests:** bounded-from-below, tree unitarity, perturbativity, physical mass ordering and decay thresholds using existing Module1. | Define the sampled **tree-level** model domain; report exact tests, widths, assumptions and cutflow. | Absolute quantum/thermal stability. |
| **Electroweak oblique** | **Applied scoped** scalar one-loop S,T,U against the source-pinned experimental covariance/implementation. | State loop order, fit reference and covariance. | Full electroweak global fit. |
| **Neutrino masses** | **Applied exact reconstruction of the chosen Zee one-loop model**: NO and IO target closure and specified perturbative F,D; pin NuFIT6.1 available best-fit/ranges snapshot and note absence of full joint nuisance likelihood. | Qualitative texture-selection effects and one-loop neutrino consistency. | 2026 global neutrino-likelihood fit, full cosmology/ordering exclusion. |
| **Global tree vacuum** | **Applied only when a sufficient positive certificate exists**; the other 192/225 historical investigated points are **UNKNOWN**, not failed. | Main conditional benchmark set = certified positive witnesses; disclose biased 33/225 certificate success and 16 ID production intersection. | All of scanned parameter space proved to have correct global minimum. |
| **`B→X_sγ`** | **Diagnostic**, coherent H1/H2 NLO QCD in ordinary basis, source-pinned legacy or HEPfit rate. Current physical theory uncertainty/covariance not validated. | Plot the central value, experimental measurement and transparent *hypothetical NP-theory-error stress scenarios*; use `APPROX_...` only for internally specified scenario. | Physical 95% CL exclusion, single Type-II `mH±>670 GeV` applied to each Zee eigenstate. |
| **`μ→eγ`, `τ→ℓγ`, `μ→3e`** | **Diagnostic**, coherent Module3 one-loop + validated Module4 photon Barr–Zee, signed tree neutral `μ→3e`; **missing gauge/F/mixed EW dipoles and 4ℓ interference unbounded**. | Clearly labeled *retained-order/subset* ratio to measured 90% CL; D12 targeted textures at fixed scalar show structural feasibility, not a hard LFV pass. | `LFV-allowed` or `BR(mu→3e)=0` from tree-zero. |
| **`μ→e` conversion** | **NOT APPLIED**, source unpatched FlavorKit proton/neutron swap and unknown complete semileptonic Wilsons. | List experimental constraint as unassessed, no automatic PASS. | Inferred bound from dipole ratio without verified dipole dominance. |
| **Higgs h125, H/A and charged searches** | **Partially calculated**, γγ/Zγ and selected h125 ratios source checked; absolute rates and broad HiggsTools complete prediction set unknown. | Plot validated partial widths/width-independent ratios; only apply an observed search if exact full process rates and likelihood are independently certified (none as of now). | `HiggsBounds allowed`, `HiggsSignals 95% pass` from missing width/production inputs. |
| **Hadronic production/charged widths** | Actual LO 5FS 13 TeV 16 spectra, separately 14 TeV **three** spectra; validated complete **on-shell tree two-body** widths. | Label `σ_LO^{5FS}×BR^{tree}_{H2→H1Z}`, split H1 decay separately; show integration error but no scale/PDF theory bands until computed. | NLO-accurate model production, matched 4FS+5FS combined rate or exact detector signal efficiency. |

**Classifier contract:** A row can say `SCOPED_APPLIED` only for independently covered components at their declared order. `DIAGNOSTIC` predictions may be shown but may not silently reject or accept a globally physical point. Missing mandatory constraints => `physical_acceptance=UNKNOWN` or null. Preserve `global_acceptance=null` and source evidence. A reviewer should be able to reconstruct a cutflow of *applied* criteria and a separate table of unassessed criteria; no “all constraints imposed” in the abstract.

**No final scan is authorized by this report.** First decide whether the scoped paper gains a meaningful collider observable beyond 2021; then fix the constraint prescription, uncertainty scenarios and single production run.

## C. Existing collider input is stronger than previously recognized

[Actual D14D production map](../../module14/conditional_scan/PRODUCTION_MAP_REPORT.md) contains **16** native validated 13 TeV LO 5FS charged-associated rates and **three** independent 14 TeV integrations for the positively tree-vacuum-certified subset. At 14 TeV the exact charge-summed LO process is
```text
g b -> t H2-
g b~ -> t~ H2+
```
plus reversed proton ordering (actual UFO labels `d3,u3,hm3`). A **single charge-summed integration** already includes both charges and both beam orders. **Do not double it**, or add 4FS associated spectator-b as if independent. The 5FS hard process contains no explicit final-state spectator b; with H1→tb and two top→Wb decays the decayed signal has **three** decay-origin b quarks (`t tbar b Z`), before QCD radiation. The 4FS `pp→tH2 b` has an **additional spectator b** and requires separate consistent matching/comparison.

The 14 TeV family-level [original CSV](../../module14/conditional_scan/production_map_14TeV_families.csv) has 12 saved rows, four families at each of three model spectra. [Raw 14 TeV calculation](collider/RAW_14TEV_PREDICTION.json) parses the actual `sigma_times_BR_pb` and JSON `H1_decay_BR_separate['t anti-b']` per row, without interpolating or regenerating.

Use [PDG W decay listings](https://pdgprod.lbl.gov/pdgprod/pdgLive/Particle.action?home=&node=S043):
`BR(W→eν)=0.1071`, `BR(W→μν)=0.1063`, `BR(W→hadrons)=0.6741`.
Use [PDG Z decay listings](https://pdgprod.lbl.gov/pdgprod/pdgLive/Particle.action?node=S044):
`BR(Z→ee)=0.033632`, `BR(Z→μμ)=0.033662`.
Neglect `W→τ` feeddown *for this raw factorized budget*, and assume `BR(t→Wb)=1`. These approximations define the yield estimate and cannot be silently used in final detector analysis.

Define `B_Zll=0.067294`, `B_Wl=0.2134`, `B_Wh=0.6741`,
`f_3l=B_Zll×2×B_Wl×B_Wh = 0.01936087948872`.
For `L=3000 fb⁻¹`,
```text
N_raw,3l = L * [σ14^LO,5FS(H2 t) × BR_tree(H2→H1 Z)]
              × BR_tree(H1→tb) × f_3l
```
This includes both possibilities for which top is leptonic. If an analysis requires the **H1 daughter top specifically hadronic**, only one of those two contributions is kept, halving this preselection count before any efficiency (assuming equal W branching fractions).

**Numerically rechecked original 12 saved source rows:** ranges below are across the **four existing neutrino families**, *not experimental or theory uncertainties*.

| Certified ID | mH1 / mH2 GeV | σ14×BR(H2→H1Z) fb | raw Zll + 2 hadronic tops | raw **3ℓ** | raw **4ℓ** |
|---|---:|---:|---:|---:|---:|
| **15591** | 442.593 / 1035.704 | 5.29609–5.29660 | 484.61–484.75 | **306.83–306.92** | 48.57–48.58 |
| **2264** | 674.274 / 1165.975 | 2.57508–2.57515 | 235.49–235.54 | **149.10–149.13** | 23.60–23.60 |
| **15673** | 714.508 / 1277.363 | 1.66735–1.66749 | 152.33–152.56 | **96.44–96.59** | 15.27–15.29 |

Numbers are **raw decay-channel events** before lepton acceptance, b tagging, jet reconstruction, detector resolution, pileup, top/Z reconstruction, cuts, backgrounds and correlated uncertainties. No 14 TeV background rates are in the saved D14D bundle. No CLs or significance claim follows.

A purely diagnostic yield check: retaining **5% total analysis efficiency** would yield about 15.3, 7.5 and 4.8 trilepton signal events for these respective IDs, **conditional on that wholly hypothetical efficiency**. Reaching ≥10 selected events (not a statistical-significance criterion) would need efficiency ≥3.26%, 6.71%, 10.37%. These are computational targets, not detector estimates.

**Do not borrow the 14 TeV 15591/2264/15673 rates for F13**: its exact 873 GeV scalar potential is different and production is not matched. D12's F13 ~48.5% cascade result remains an independent flavor/decay-physics example. A paper cannot splice the F13 texture onto a mapped D14 production scalar card.

## D. Minimal, distinctive collider feasibility pilot

**Selected channel:** on-shell `Z→e⁺e⁻/μ⁺μ⁻` plus exactly **one** direct e/μ from a top, one hadronically decaying top, missing `E_T` and three b quarks at decay level. This uses the 3ℓ counts above. The experimental advantage is the `Z→ℓℓ` resonance, lepton triggers and a reconstructable `m(tb)` / `m(tbZ)` system. The experiment-level limitation is **large `t tbar Z+heavy-flavor` and combinatorial top assignments**.

**Background priority**, motivated by [ATLAS EPJC 85 (2025) 1434 `tt̄ℓℓ` trilepton analysis](https://doi.org/10.1140/epjc/s10052-025-14695-9): `tt̄Z+>=1b` and `tt̄Z+bb` subdivisions with heavy-flavor merging; `tWZ`, `tZq+jets`; `tt̄W`, `tt̄H`; `WZ+jets`, `ZZ+jets` and nonprompt leptons from `tt̄+jets`. The named priorities are a physics expectation, **not measured background yields** for our selection. Do not double count inclusive `tt̄Z` against separate HF samples or `tWZ` overlap.

**Start with source inventory** on the user's analysis facility before generating anything. The user previously reported some **13.6 TeV ATLAS HepMC backgrounds**, but no established names, DSIDs, generator weights, accessible files or 14 TeV matched samples are documented **for this Zee final state**. No assertion these include `tt̄Z` is permitted. If usable 13.6 TeV backgrounds exist, select a **consistent 13.6 TeV pilot**: generate at most one or two matching 13.6 TeV charged-Higgs **signals** with the existing native model on the existing certified ID cards, then run the same truth/Delphes fiducial procedure on signal and background. **Never combine a 14 TeV signal rate with 13.6 TeV background yields**. If no suitable backgrounds exist, run a **lightweight parton-level 13.6 TeV `tt̄Z` test**, recording the experimental uncertainty, and stop before any purported reach.

**First selection prototype (to be optimized only on actual events):**
- Exactly 3 isolated e/μ, with an opposite-sign same-flavor pair `|mℓℓ-mZ|<10 GeV` and a third top-decay candidate.
- `>=3` tagged b jets, `>=2` other resolved jets for a hadronic W, `E_T^miss>20 GeV`. These are **proposals**, not inherited ATLAS thresholds.
- Choose b-jet/W/top combinations using `m(jj)~mW`, `m(bjj)~mt`; a remaining b plus a top forms `m(tb)~mH1`, and adding Z forms `m(tbZ)~mH2`. For leptonic H1 daughter-top use W mass-constrained neutrino `p_z` reconstruction, accounting for ambiguous/compex solutions. Separate categories may outperform forcing a hadronic H1-top.
- Compare shape/binning of `m(tbZ)`, `m(tb)`, `H_T`, `p_T(Z)`, `N_b` and use control region `N_b=2` for `tt̄Z` normalization. Ensure no plotting of a reconstructed mass without verified parentage truth tests. Verify signal fiducial normalization, negative-weight handling and jet flavor labels in each sample.

**Minimum deliverable to call this a sensitivity study:** source-bound signal/background samples at *the same energy*, normalized with generator cross sections, filter efficiencies and `sumw/sumw2`, accounting for overlap and negative weights; cutflow; signal/background distributions; efficiency and acceptance; explicit `tt̄Z` heavy-flavor nuisance; a reproducible Poisson multi-bin likelihood with nuisance variation and expected **95% CLs** under specified assumptions. Absent such a statistical model, show only **pre-detector yields** or *conditional reach-vs-background-efficiency curves*, never an exclusion line. An unexplained `S/√B` is not a CLs limit.

With true 14 TeV samples, present `L=3000 fb⁻¹` projection under documented HL-LHC assumptions ([HL-LHC Yellow Report](https://e-publishing.cern.ch/index.php/CYRM/issue/download/94/69)). If only 13.6 TeV background samples exist, keep the actual pilot at 13.6 TeV; do not relabel HEPMC/Delphes 13.6 events to 14 TeV or use a single inclusive (K)-factor to imply changed fiducial shapes. Cross-energy reweighting would require phase-space coverage, parton kinematics, PDF/matrix element/EW mapping, generator systematics and a separately validated closure.

## E. Bounded next execution and go/no-go

**Stage 0, already done here:** freeze paper constraint-tier table; compute 14 TeV raw factorized 2ℓ/3ℓ/4ℓ count ranges from actual native 14 TeV family rows, retaining original provenance.

**Stage 1, next Codex task:** audit accessible existing 13.6/14 TeV background inputs and exact 13/14 TeV signal run cards; no source edits to frozen Modules0–13/D14 and no new scalar/neutrino points. Output generator/energy/PDF/weight/cross-section/overlap inventory. If genuine common-energy signal/background exists, proceed to a **single bounded pilot**; otherwise clearly state missing sample and show the background requirement to test.

**Stage 2, limited pilot after inventory:** user has authorized feasibility, not a full production campaign. Generate **at most 2 existing-ID signal samples × at most 2,000 events each** for the matched-energy check if the established generator is usable locally; never launch Condor jobs or expensive new background production without a separate explicit user decision. Reuse existing 13.6 TeV background files only if applicable and accessible. Save all outputs outside Git under a fresh scratch/data directory, source- and card-pinned. A pilot this small is **not** necessarily sufficient for precise background tails or limit construction.

**Go/no-go after pilot:** Decide whether a usable source-supported background model, reconstructable mass separation and non-negligible acceptance can justify further event generation. Do not gate on arbitrary universal S/√B; report which systematics and controls are still needed. If both background and kinematic differences are weak, do not market the old cascade rate curves as novel reach. Paper 1 can remain a narrower conditional methodology/results note, but EPJC publishability needs a demonstrable additional quantitative physics contribution.

This report grants **no final parameter-space scan or model-wide physical acceptance**, and no new production job has been launched.
