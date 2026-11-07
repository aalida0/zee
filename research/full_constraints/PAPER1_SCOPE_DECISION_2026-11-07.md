# Paper 1: publication-scope decision after fixed-card validation barriers

**Date:** 7 Nov 2026. **Branch:** `research/zee-full-constraints`.
**Starting experimental audit:** `1986edfe4165a19e72923a856316933acde25db4`.
**Decision type:** scientific scope and go/no-go plan, NOT scan authorization, physical exclusion or completed paper.

## Bottom line

The existing research cannot be described as a **fully constrained allowed Zee parameter space**. B→Xsγ uncertainty, LFV complete interferences/operators, broad Higgs likelihood, and global vacuum classification have not reached their declared hard gates. The old 225 scalar-qualified points, 33 sufficient positive vacuum witnesses and 16 H2 production-map points are **conditional historical exploratory data**; none becomes globally allowed by this report.

The next useful work is NOT another individual loop or forcing a total-width fit.
Decide explicitly whether Paper 1 is:
- **A. Full model, fully constrained scan**: keep hard gates, require flavor-specialist B theory, independent full LFV, HiggsTools signals, and vacuum handling; do not launch until these actually pass. This is scientifically strongest but unbounded in effort and **not presently executable as an allowed-space scan**.
- **B. Explicitly scoped Zee charged-cascade phenomenology** (preferred **feasibility direction**, contingent on novelty review): retain exact model, full tree-level scalar and neutrino reconstruction, scoped scalar EWPO, positively certified vacuum points, and independently validated *partial* observable predictions. Label missing flavor/Higgs exclusions as **UNAPPLIED/UNKNOWN**, not “passed.” Present conditional correlations and matched predictions, with quantitative collider reach only under stated external analysis assumptions and background model. Never advertise “all existing constraints satisfied,” “full parameter scan,” a current LHC 95% exclusion or global allowed benchmarks.
- **C. Postpone/change the paper** if reviewer-level differentiation from 2017 full-Zee constraints + 2021 H2→H1 Z cascade and external constraints cannot be established. A small rate table plus unvalidated collider reach is not a stand-alone EPJC result.

**User approval is required to change from A to B.** Merely writing Option B here does not authorize a scan. Prior explicit user rule remains: **one final sizeable parameter-space campaign only after agreed physics gates, never exploratory new points without permission**.

## What is unambiguously validated and publishable in isolation, with order/scope

| Sector | Actual evidence | May state | May NOT state |
|---|---|---|---|
| Scalar/perturbativity | scalar reconstruction, BFB, tree-level unitarity tests | bounded/stable and perturbative under declared tree criteria | quantum/metastability or all-field global minimum for UNKNOWN points |
| EWPO | model-scalar STU computation at scoped 1-loop | EWPO within implemented reference | all oblique/higher-loop effects certified |
| Neutrino | explicit Zee 1-loop NO/IO reconstruction, original fits | consistent exact model mass reconstruction at fixed fit inputs | full lepton flavor exclusion |
| Global vacuum | 33/225 **sufficient positive witnesses** in historical qualified set | those 33 satisfy the particular sufficient certificate | 192 UNKNOWN are safe or forbidden |
| B→Xsγ | pinned HEPfit coherent two-state NLO fixed card, 69 nuisance/scale runs, 473.1 vs 480 GeV one-state confidence | model-dependent central prediction and explicit uncertainty issue | full physical 95% CL verdict or single Type-II 670 GeV veto applied eigenstate by eigenstate |
| LFV | one-loop dipoles, photon two-loop subsets, F-only mixed-box vs published, complete 3-body rate functional, conversion source bug | validated subset complex amplitudes and source-level normalization checks | complete mu→eγ, mu→3e, conversion exclusion; uncorrected FlavorKit conversion |
| h125 | γγ and Zγ full leading-one-loop partial widths, h standard/LFV known partial channels, three total-width-free μ ratios | actual partial predictions/ratio correlations with scheme labels | absolute μ, globally allowed from HiggsSignals, uncertified Γtot |
| H/A | SusHi 13 TeV ggF/bbH LO on D7/F13 and partial widths incl H/A→γγ, H_i W | conditional production/partial-rate physics | full neutral branching fractions, observed tau tau exclusion |
| Charged cascade | native 2-body widths and signed vertices, saved LO tbH2 production at 16 old spectra | source-bound tree/LO cascade rate estimates with caveats | NLO model precision, detector-sensitive exclusion/reach without validated recast |

Numerical status evidence:
- `HIGGS_H125_VBF_BB_OBSERVABLE_GATE.md`: known h125 partial sums D7/F13 4.280495766/4.005236276 MeV, signed Δ width one-error endpoint crossings at (-0.8573,+2.8431)/(-0.9855,+2.2788) MeV, not uncertainty bounds. ATLAS VBF bb ≈0.99±0.35 only source-matched conditional.
- `bsgamma_hepfit/UNCERTAINTY_REPORT.md` and `specialist_question.md`.
- `LFV_SOURCE_TO_CODE_REPORT.md` and `LFV_COVERAGE.md`.
- `HIGGS_COVERAGE.md`, `HIGGS_ZGAMMA_COMPLETE_H125.md`, `HIGGS_H125_SIGNAL_STRENGTH_REPORT.md`.
- `PROGRESS_TO_FINAL_SCAN.md` (original milestone counts remain unchanged).

## Publication credibility requirements (evaluate before deciding to scan)

The scope is scientifically publishable *only if* the following explicit claims can be supported with numerical evidence **without conflating conditional with allowed**:

1. **Distinct contribution vs both prior papers**: source-verified side-by-side with Herrero-García, Ohlsson, Riad, Wirén JHEP 2017 **general Zee full scan** (doi:10.1007/JHEP04(2017)130) and Florentino, Romão, Silva EPJC 2021 **Zee off-diagonal charged-scalar cascade** (doi:10.1140/epjc/s10052-021-09956-2). Compare Lagrangian restrictions, neutrino/complex LFV textures, exact loop constraints, mass windows, production mechanisms, scan method, collider channels/energies, and actual plots/benchmark reach. Do not assume model interpolation alone is novelty. Also check later citing studies of cascade and ATLAS charged Higgs searches.
2. **Scientific center, not software story**: demonstrate a nontrivial *conditional* neutrino/scalar/EWPO versus charged mixing/cascade branching/cross-section correlation (e.g. on existing qualified cards), with uncertainty or sensitivity to unconstrained flavor inputs shown honestly. Do not claim a constraint-induced correlation from an unvalidated module.
3. **Collider utility**: if Paper 1 promises HL-LHC reach, the assumed sensitivity needs an explicit signal/background/acceptance/systematics model (a transparent optimistic benchmark or documented fast-simulation transfer). A cross-section × BR curve alone is a rate forecast, **not exclusion/discovery sensitivity**. Do not improvise S/sqrt(B) as a 95%-CLs limit or claim a data recast. Detector-level phenomenology may instead become Paper 2.
4. **Conditional constraints vs genuine exclusions**: clearly distinguish (i) hard model/tree constraints independently verified, (ii) experimental exclusions with validated likelihood and uncertainties, (iii) bounded diagnostic calculations, (iv) unimplemented/unqualified processes. Flavor/Higgs UNKNOWN may not be silently accepted during generation or postprocessing. A scoped publication might show “candidate viable under *applied subset of constraints*; pending B/LFV/Higgs,” not “viable point.”
5. **Vacuum policy**: a future scoped study can restrict reporting to the subset with positive witness certificates and track other points as UNKNOWN; no accidental inclusion as global vacuum PASS. Existing 33/225 do not prove meaningful collider rate/novelty retention until their rates are cross-matched by existing IDs.
6. **Physics feasibility/no-go**: check with *existing* old D12/D14 saved cards only whether there are **any** positively certified-vacuum points with genuinely interesting charged cascade rates and nontrivial neutrino/LFV mixings. Summarize actual intersected IDs, benchmark masses, H2→H1 Z BR, σ×BR and potential obstacles **only if every value can be traced to an existing saved source**. No new parameter proposal.

## Exactly what to do next (one bounded analysis, no new calculations)

Produce a reviewer-oriented, **maximum ~5-page** `PAPER1_FEASIBILITY_REVIEW.md` using existing saved evidence. It must answer:
- **Novelty**: explicit side-by-side 2017 vs 2021 vs proposal; classify NEW / previously done / unsupported for each manuscript figure. Source cite precise sections/figures not just title.
- **Existing benchmark survival**: cross-intersect original D14 saved IDs and 33 vacuum-witness certificates **if source artifacts are available without new point generation**; disclose missing joins, and whether data can already support >=2 meaningful cascade benchmark comparisons.
- **Honest candidate figure list**: at most 4 paper figures and 2 tables, with provenance and actual source status. Avoid including pretty but unvalidated 95% exclusion curves.
- **Two publication routes** (A full or B scoped) and minimum remaining external dependencies; identify exactly where a specialist opinion is required before the user authorizes anything.
- **Recommendation**: one go/no-go verdict (publishable scoped subject to criteria, no-go, or cannot yet decide) with explicit peer-review objections. Do not promise EPJC acceptance, fit fictional data or paper number.
- **Stop** without changing `global_acceptance`, hard-veto status, source production, or running a scan.

After the feasibility review, **ask the user to choose publication scope A/B or revise it** before writing a new full-scan production card. No generation/scan authorization is implied.

## Guardrails
No source or physics program edits; no new Zee points, even exploratory/pilot; no Condor, MG5 production or standalone multi-loop derivation; no 'source unavailable' assertions without citation-network check. Preserve Modules 0–13, D14 historical data and frozen feature scan branch at 133a340. Use research branch only, source hash every quantitative result and commit/push only evidence-backed reports.
