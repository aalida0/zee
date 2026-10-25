# Zee charged-scalar paper: final implementation critical path (2026-10-24)

## Publication objective / freeze rule

**Target:** A defensible EPJC *phenomenology* paper on the type-II-quark
ansatz of the general Zee model, emphasizing genuine neutrino/flavor–
collider correlations and the charged cascade
`H2+ -> H1+ Z -> t b Z`. A detector-level reinterpretation is NOT
part of this paper: leave that to a dedicated follow-up.

**Literature baseline:** Herrero-García et al., JHEP04(2017)130
already scanned general Zee neutrino/LFV parameter space; Florentino,
Romão, Silva, EPJC81(2021)1148 already studied off-diagonal charged
Z couplings and cascades. Thus neither a three-benchmark scan nor
"large cascade branching ratios" is novel alone. New deliverable must
be a source-reproducible joint **flavor-neutrino–cascade relationship**
or a demonstrably new constrained collider-parameter corner.

**Existing actual CERN anchor results, 24 Oct 2026:**
- F18 physical complete MadWidth 2+3-body **three point** charged
  cascade BR = (0.44634835, 0.46387734, 0.42032289).
- F19 sufficient scalar quartic BFB, tree 8pi unitarity and scalar STU
  correlated Gfitter/PDG 3/3 pass; `0001330` is within ~1.7% of
  8pi scalar unitarity boundary, so not robust to stricter cuts.
- F19b 3/3 original full-complex f/Y fixed **central NO** reconstruction
  residual O(1e-14) eV, coherent subset partial mu->e gamma 6.9e-18
  to 5.8e-17, not the full general Zee LFV prediction.
- F19c six-real-field nonconvex tree potential 66 successful starts
  each, no deeper EW/charge/CP-breaking witness; **not** global proof.
- F19d independently reconstructed *analytic LO* two-state C7,C8
  with mtop(mu0)=163 GeV illustrative gives
  `1e4 BR(B->Xs gamma)` = (3.95137,3.94942,3.94703).
  Modern 2026 SM=3.54±0.14, experiment=3.49±0.19 (all 1e-4).
  These new-scheme approximations have uncalibrated NP matching
  uncertainties. This closeness to a naive 2-sigma comparison is
  a HIGH-RISK publication bottleneck, not a 95% exclusion.
  The 670 GeV single-Type-II charged bound does NOT directly map
  onto a mixed two-charged Zee spectrum.
- UChicago AF unavailable. CERN LXPLUS/EOS/HTCondor workflow
  operational; F20 four-shard 20k-proposal integrated SCREENING
  campaign submitted by user. F20 does NOT solve items below.

## Budgeted physics implementations (ordered by manuscript risk)

### MUST-HAVE A — mathematically consistent two-charged B->Xs gamma

**One substantial solver, not ad hoc extra microgates.**

1. Define the exact quark-Yukawa ansatz and mixing conventions;
   compute matching `C7,C8` for BOTH charged states coherently at
   LO and the available higher-order (preferably NLO) in one
   renormalization scheme with common quark masses and Wilson basis.
2. Validate original single-Type-II limit and large-mass decoupling;
   use two independent implementations or same-scheme literature
   benchmarks for Wilson signs/normalization and scale dependence.
3. Evaluate inclusive B->Xs gamma at the highest *honestly validated*
   perturbative accuracy, with consistent SM baseline, hadronic
   normalization, photon cut, interpolation/NP nonlinear terms and
   theoretical uncertainty. 2026 Misiak et al. improved SM and
   Type-II result cannot be reconstructed by replacing a legacy
   SuperIso baseline with 3.54e-4.
4. Build calibrated exclusion/sensitivity treatment with experimental
   correlations; use measured bound only under matched assumptions.
5. Test exact three benchmark viability FIRST with full solver; if
   disfavored, rescan before spending time on collider simulation.

**Acceptance artifact:** source-locked real backend producing
`C7,C8(mu0)`, scales, rates and uncertainty budgets for all F20
selected points; Type-II reference validation. A consistent NLO BSM
analysis with explicit conservative perturbative uncertainty may be
sufficient for a *scoped* paper if it robustly resolves the borderline
points; an exact 2026 NNLO extension is not a hard implementation
deadline. No acceptance flag if only F19d linearized LO inputs exist.

### MUST-HAVE B — full coherent general Zee LFV and neutrino likelihood

- For an expedited defensible paper, **scope the main claim to normal
  ordering (NO)** rather than delaying release to cover IO. Use exact
  complex physical `f` and `Y^ℓ` shared with scalar and collider
  input, vary PMNS Dirac/Majorana phases and NO oscillation uncertainties
  using current fit inputs, and state the cosmological mass-sum assumption.
  Investigating IO is an extension, not a prerequisite to a NO-only claim.
- Coherently sum **all phenomenologically important** one-/two-loop
  radiative LFV amplitudes, including remaining charged-scalar/bosonic
  terms. Missing terms may be omitted only with independently tested
  quantitative upper bounds that show they cannot change viability
  in the claimed region; a low partial rate by itself is not enough.
- Calculate `mu->3e`, tau 3-body with tree, dipole, non-dipole,
  Z, box interference and coherent `mu-e` nuclear conversion;
  LFV Higgs decays, lepton universality, CP-sensitive EDM checks
  where relevant. Validate against the 2017 and independent
  Zee LFV references in parameter limits.
- Do not use 2017 historical experimental limits when better
  2026 measurements are available.
- Fully evaluate a **controlled representative subset** of F20
  solutions first, then apply surrogate / optimization to broad scan
  ONLY after bounded approximation error has been demonstrated.

**Acceptance artifact:** complete amplitude inventory, independent
unit-normalization/complex conjugation control, 2026 experimental data
sources, coherent per-channel rates and an auditable likelihood.

### MUST-HAVE C — collider/Higgs constraints with real model rates

- Obtain five-state `h,H,A,H1,H2` model widths and branching ratios,
  with neutral Higgs and charged QCD-corrected fermionic channels,
  open cascade/off-shell modes and specified completeness tolerances.
  F18 MadWidth charged 3-point result is an anchor, NOT a width
  surrogate valid over F20 scalar population.
- Source real `pp->t(b)H2^±` production at LHC energy
  (13/13.6/14 TeV as appropriate), with unambiguous Type-II quark
  Yukawa mixing fraction, scheme, scale/PDF uncertainty and
  validation. `sin^2 gamma` alone is NOT a cross section in pb.
- Complete HiggsTools predictions for neutral states and review
  *explicit coverage limitations* for the exotic charged cascade.
  Add independently relevant direct charged-Higgs search and
  SM-like Higgs signal-strength constraints. Do NOT infer exotic
  exclusion where no dedicated result is applicable.
- A limited number of accurate production-normalized benchmark
  rates and an explicitly labeled parton-level fiducial
  signal study are enough for **paper 1**. No detector/Delphes
  sensitivity forecast required; reserve that for paper 2.

**Acceptance artifact:** complete five-particle rates accepted by
HiggsTools and `sigma(pp->t(b)H2) x BR(H2->H1Z) x BR(H1->tb)`
with propagated uncertainties and citations.

### RECOMMENDED D — scalar vacuum/RGE robustness

- For best posterior-independent candidate families, strengthen
  C5 multistart 66 -> 256/512; nonfind is not a global proof.
- Check eigenvalue margins under stricter perturbativity criteria,
  vacuum lifetime or certified minimization if necessary.
- Define perturbativity/RGE cutoff instead of inferring absolute
  high-scale validity from electroweak tree unitarity.
- Optional if a small and honest electroweak-scale pheno scope is
  used, but claims must acknowledge each limitation.

## F20 handling while these modules are built

User has already submitted F20 four parallel CERN HTCondor jobs.
Per-job workload 5000 scalar B4 proposals, up to 30 complex
fixed-NO partial LFV fits and up to 12 x 64-start C5 vacuum
searches. `+MaxRuntime=86400` is a **24h runtime cap**, not ETA:
jobs may queue; unprofiled runtime ranges from hours to possible
timeout. Four jobs run simultaneously when CERN allocates slots;
total wall time is the slowest successful shard plus queue time,
not four times per-shard time.

Observe: `condor_q -nobatch $USER` and
`condor_q $USER -af ClusterId ProcId JobStatus RemoteWallClockTime`.
States: 1 Idle, 2 Running, 5 Held.
After completion, preserve all four EOS result archives. The worker
transfers a diagnostic tarball even when the Python job fails, and the
F20 merger rejects nonzero `F20_SHARD_*.exit` status. A job disappearing
from `condor_q` is NOT sufficient evidence of success.

**F20 scientific interpretation**: 20k proposals are biased correlated
B4 random walks, **not** uniform sampling, volume fractions or
posterior credible regions. LO B->Xs gamma is diagnostic only.
Optimized complex-Y LFV has omitted diagrams, and selected spectra
use included-channel charged-cascade proxies. No F20 point is fully
excluded/allowed without A/B/C.

## Final EPJC deliverables — freeze when sufficiently validated

1. Model/conventions, numerical input, independent validation and
   uncertainty-method sections.
2. Model-constrained mass/mixing plane, with *only actually evaluated*
   constraints and uncertainty categories clearly differentiated.
3. At least one genuinely new joint correlation:
   e.g. `BR(H2->H1Z)` vs coherent `mu->e gamma` or conversion;
   physical production-normalized `t(b)H2 -> t(b)tbZ`
   vs neutrino phases/orderings, under identical scalar/quark data.
4. Two or three fully evaluated, traceable benchmark cards plus
   realistic range of rates and dominant experimental/theory limits.
5. Exact comparison against 2017 JHEP Zee general scan and
   2021 EPJC off-diagonal Z cascade results. State **what is genuinely
   different**, not simply upgraded code or number of points.

**No-go condition:** if A/B/C cannot be validated sufficiently within
available project time, do not submit a "full constraints" Zee paper
based on F18-F20. Consider a strictly limited model-validation
methodology/LO phenomenology publication only after independent
novelty/referee audit; the claim will be weaker and EPJC acceptance
less certain.

**Operating rule:** stop creating one-file-per-gate microcampaigns.
Focus on the three substantial backends A/B/C and one final integrated
physics scan + manuscript. Do not add detector-level scope to paper 1.
