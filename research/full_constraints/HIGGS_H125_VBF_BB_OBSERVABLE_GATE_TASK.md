# Next decisive Higgs gate — observable-specific h125 Γtotal materiality and one ATLAS VBF→bb rate

**Branch:** `research/zee-full-constraints`
**Starting result:** `654794f1ba887765985d8ffda491c901dc34d1c4`
**Priority:** qualify **one experimentally interpretable h125 observable**, not calculate more unrelated loops.
**No new random Zee points, pilot/full scans, Condor, large MG5 or heavy H/A amplitude work.**

## Starting evidence and sources

Read `research/full_constraints/HIGGS_H125_SIGNAL_STRENGTH_REPORT.md`,
`HIGGS_ZGAMMA_COMPLETE_H125.md`, `HIGGS_EXECUTION_REPORT.md`,
`HIGGS_COVERAGE.md`, `higgs/H125_SIGNAL_STRENGTH_EVIDENCE.json`,
and the actual ATLAS paper `2011.08280` and pinned HiggsSignals 1.1.3
`h125/bb_vbfH_LHC13_ATLAS_126.json` (ID 201108280, 13 TeV).

Already independently executed on original NO/low_joint cards:
- Known disjoint h125 Γ sums: D7 **4.280495766 MeV**, F13 **4.005236276 MeV**; common-accuracy known-channel SM **4.070980542 MeV**. NOT certified physical totals.
- Γγγ/ΓγγSM D7 **0.9317959556**, F13 **0.9750252264**.
- ΓZγ/ΓZγSM D7 **0.978770448547**, F13 **0.989590176981**.
- Rσ(VBF) D7 **0.9976849708**, F13 **0.9999939731**; RΓ(bb) native consistent. Supported μ numerator VBF→bb D7 **1.104373249**, F13 **0.974211283**.
- The ratios of μ(VBF,γγ)/μ(VBF,WW*) and μ(VBF,Zγ)/μ(VBF,WW*) are already *validated theory-only ratios*, not absolute signal strengths.
- ATLAS VBF bb μ ≈0.99^{+0.36}_{−0.34}. Native pinned SMHiggsEW reference σ×BR is **2.20257783862 pb**, different from ATLAS's published nominal reference; respect the JSON's implicit ref convention.
- The previous 40–43 keV '1% denominator impact' figures are **sensitivity thresholds, NOT physics upper bounds**. 1% is not automatically necessary to use this ~35% experimental measurement.

## Phase 1: predeclare experimental sensitivity requirement FIRST

1. Read *actual* ATLAS paper and pinned JSON. Verify process identity, VBF purity, possible ggF admixtures/fixed assumptions, h125 mass, widths, SM reference, confidence/profile construction and experimental error. Do not transpose nominal 2.16 pb as μ=2.16.
2. Before new source calculations, derive `μ_VBF,bb=RσVBF RΓbb × ΓSM/ΓZee` and an **observable-specific uncertainty/materiality tolerance**: how large a signed total-width shift, ggF admixture, or source scheme deviation would be necessary to change a decision at 68% and 95% (when data truly supplies such confidence). Do not reverse-engineer a tolerance to force PASS. A predicted μ≈1 may be merely uninformative as a *constraint*, even if its rate is calculable.
3. Derive and show `μ` versus ΔΓ and perturbative uncertainties as a **conditional diagnostic curve** over a bounded documented domain. The curve is NOT an accepted physical scan or a prior on ΔΓ.
4. If the experiment cannot be model-matched without a detector recast or additional significant process mixtures, mark the exact acceptance blocker, and do not consume the JSON as a physical constraint.

## Phase 2: establish a defensible bounded missing h125 width contribution

1. Analyze original D7/F13 h125 **only**. On-shell extra scalar/invisible two-body states are kinematically absent. Explicitly enumerate the physical virtual exotic `h→W* H_i*, Z*H*/A*, H_i*H_j*, lepton 4-body, loop hνν`, and **interference or double-counting with existing HDECAY WW*,ZZ***. Do not assume an offshell contribution zero just because its parent is heavy or closed.
2. Before implementing, search *targeted source calculations only* (the citation audit is already done) for a genuinely applicable effective four-fermion/semileptonic bound and h→νν Majorana loop. A published form factor for a restricted Zee texture is a **check**, not automatic general-model answer.
3. Where meaningful, compute rigorous analytical conservative bounds or a directly executed **fixed-card only** matrix-element phase-space integral with SM–BSM interference and correct gauge/Goldstone/combinatorics. Use independent cross-check (e.g. tight propagator bound and numerical fixed-card quadrature). Do not construct a new fully general 1→4 phase-space generator, full 2-loop vertex calculation, FeynArts/FlexibleSUSY rebuild, new mass scan, or MG5 campaign.
4. Quantify with correct units the max disjoint additional width and max signed interference change, comparing to the *predeclared ATLAS decision sensitivity*, not a made-up global percent. For hνν distinguish absence of a **tree massless-neutrino vertex** from loop-induced Majorana couplings: if using mν-derivative power counting establish the correct vev/spectrum derivative and coupling domain; no bare guess `g_hνν≈mν/v` without proof.
5. Bound uncertainty in the existing large Γbb/gg and experimental SM reference, including HDECAY charm conversion and native κb matching. No arbitrary common 5–10% nuisance or treating a raw numerical integration precision as theory σ.

## Phase 3: qualify one actually useful experimental result or stop

1. If Γtotal plus production/acceptance uncertainties are source-qualified to the stated accuracy, compute **D7 and F13 absolute μ(VBF,bb)** with numerator and complete Γtotal, plot/record confidence inputs, run the pinned HiggsSignals single native measurement using its **absolute rate reference** and preserve full stdout/inputs/dataset hashes.
2. Explicitly distinguish `RATE_THEORY_VALIDATED`, `MEASUREMENT_SCOPED_EVALUATED`, `MODEL_NOT_EXCLUDED_BY_THIS_MEASUREMENT`, `EXCLUDED_BY_THIS_MEASUREMENT` and global Higgs coverage. A single agreement with μ≈1 is not a global PASS; a single measurement's Gaussian chi² is not automatically an independent 95% CL exclusion.
3. If no honest certified bound can be obtained with existing source and fixed-card methods, stop at **`H125_ABSOLUTE_MU_BLOCKED`** with a concise missing physics input. Do not turn the same study into another open-ended loop calculation. Preserve existing source-validated ratios and numerical data.
4. Report whether the prospective experimental conclusion is robust to a wide physically motivated uncertainty envelope. If this measurement simply cannot constrain these cards, state that and recommend a more informative h→γγ / LFV h / charged H2 search for paper scope.

## Deliverables

- `research/full_constraints/HIGGS_H125_VBF_BB_OBSERVABLE_GATE.md`
- `research/full_constraints/higgs/H125_VBF_BB_MATERIALITY.json` (actual quantified bounds only; otherwise null+reason)
- optional isolated calculation/tests in research subtree only if actual independent physics input generated.
- Update Higgs milestone only if genuinely new physically qualified signal/experimental result. B and LFV remain blocked; no full-model globally-allowed claim.
- Run actual tests/hash replay and `git diff --check`; commit/push.
- Frozen Modules0–13, original D14 scan/data and `feature/zee-d14-conditional-cascade-scan` remain immutable.

**Strict stop:** one exact experimentally matched VBF→bb observable or a demonstrated narrow uncertainty/acceptance obstruction. Not another broad search and not more tests without calculated physics.
