# Candidate A — one decisive, comprehensive vacuum–charged-mixing study

**Approved 7 November 2026.** Research branch **research/zee-full-constraints**; baseline HEAD **a942458561100489c00518d1b062926f282f8a6b**.

## Mission, scientific question and acceptance policy

Conduct a **single comprehensive, disconfirmation-first** mathematical and numerical investigation of whether **rigorous tree-level global-electroweak-vacuum requirements produce novel and quantitatively useful bounds on the two mixed charged Higgs bosons and their off-diagonal Z interaction in the exact frozen CP-conserving Zee Type-II scalar model**. The final deliverable is a **GO/NO-GO manuscript verdict** grounded in genuinely source-checked theory, code-reproduced results, and a comparison to the published 2005 and 2021 analyses and general numerical vacuum tools.

User authorizes **bounded deterministic scalar-only continuation** of existing exact D10 potentials needed to assess this question (e.g. interpolation/bisection in the cubic coupling with all other Lagrangian coefficients fixed, and targeted test-field minimization); this does **not** authorize an unrestricted scalar scan, one final Zee parameter scan, changing Yukawa/neutrino models, Condor, expensive event generation, detector/HL-LHC/FCC-hh simulation, or a new multi-loop project. Do not silently enlarge scope. One decisive investigation; do not conclude with an automatic request for another series of pilot tasks. If mathematical certification is infeasible, stop transparently with partial/inconclusive evidence rather than inventing a theorem.

**Null hypothesis:** the known 2005 Zee charge-breaking formulas plus 2021 scalar/cascade analysis already give the underlying physics; our D10 full-field positive certificate and P2 negative witness may merely be an application of generic SOS/numerical optimization without a broadly informative mixing bound. Try to prove this null, including through public-code and literature reuse. A dramatic but contrived single-path figure does not by itself establish an EPJC/PTEP centerpiece.

## Immutable foundations — read before implementing

1. AGENTS.md and research/full_constraints/LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md.
2. module1/D10_VACUUM_GLOBAL_AUDIT.md, validation/module1/d10_vacuum_global.json, module1/d10_certificate.py, module1/d10_polynomial.py, module1/d10_search.py, module1/potential.py, module1/d10_benchmarks.json, models/SARAH/ZeeTypeII/ZeeTypeII.m, module1/README.md, tests/test_module1_d10_global.py.
3. module14/conditional_scan/PRODUCTION_MAP_REPORT.md, research/full_constraints/PAPER1_FEASIBILITY_REVIEW.md, PAPER1_CONSTRAINT_CONTRACT.json, PROGRESS_TO_FINAL_SCAN.md and the completed flavor-cascade NO-GO report.
4. Distinguish the 2017/2021 lepton/flavor-physics restrictions from the precise **scalar-sector-only** statement being investigated here. Old full-model flavor/Higgs/global-acceptance statuses remain UNKNOWN.

Record SHA-256 of every original physics input and source file, implementation commit/versions, runtime, and binary64-vs-exact-rational convention. Preserve all original Modules 0–14, SARAH model, validations, cards, receipts, and main/frozen scan branch **byte-for-byte**. All new code/evidence is isolated under research/full_constraints/candidate_a/ and a short summary in research/full_constraints/.

### Physical scope and conventions

Use ONLY the CP-conserving, softly Z2-broken, two-doublet-plus-one-complex-charged-singlet potential actually implemented in the repository. Calling the full **ten-real-field** orbit of that restricted potential "full-field" is acceptable; calling it the unrestricted most-general complex Zee potential is NOT. No loop, thermal, bounce-time or cosmological stability claims.

Source normalization (verify against frozen SARAH and independent polynomial, do not replace by remembered conventions):

- x = Phi1†Phi1, y = Phi2†Phi2, z = Phi1†Phi2 = u + i w, s = |S|²;
- d = Phi1+ Phi20 − Phi10 Phi2+; |d|² = xy − u² − w²;
- V2 = M112 x + M222 y − 2 M12Sq u + MCS2 s;
- V3 = 2 Mu4 Re(conj(S) d);
- V4 = Lambda1 x²/2 + Lambda2 y²/2 + Lambda3 xy + (Lambda4+Lambda5)u² + (Lambda4−Lambda5)w² + LambdaC s² + (K1 x + K2 y − 2 K12 u)s.

Electroweak reference must be the exactly defined neutral stationary orbit with proper tadpole/root enclosure; its potential value does not depend on Mu4 at fixed other scalar coefficients. Exact charged eigenvalues/mixing must be recomputed on any Mu4 deformation; they cannot be held fixed independently. In the D10 convention Mu4=(mH2²−mH1²) sin(2 gamma)/(sqrt(2) v) with signed branch/orientation checks. The published off-diagonal Z coupling is proportional to sin(2 gamma), not a new discovery. A tree on-shell cascade partial width is not an experimental exclusion or detector sensitivity.

## Work package 1 — priority, equations and direct literature cross-examination

**Before writing any new theorem**, retrieve/read primary full texts and exact relevant locators:

- A. Barroso and P. M. Ferreira, "Charge breaking bounds in the Zee model", Phys.Rev.D72 (2005) 075010, arXiv:hep-ph/0507128, especially Eqs. (6), (10)–(12), (14), (17)–(23), and its actual numerical/parameter restrictions;
- R. R. Florentino, J. C. Romão, J. P. Silva, EPJC81 (2021) 1148, arXiv:2106.08332, **published** model potential, signed charged mixing and Z-coupling equations, charge-breaking method and numerical benchmark conclusions (journal and arXiv-v1 numbering differ);
- Zee flavor/scalar earlier studies as needed; generic 2HDM vacuum theorems must NOT be transferred to cubic Zee without proof;
- generic public vacuum code precedent, including Vevacious (arXiv:1307.1477), its numerical homotopy/one-loop roles and actual model VEV coverage;
- relevant post-2021 literature / citing 2005 and 2021; search INSPIRE-HEP / arXiv plus exact source references for combinations of "Zee", "charge breaking", "global minimum", "sum of squares", "semidefinite", "cubic scalar", "charged mixing", "certified bound", "vacuum", through current date.

For each candidate novelty claim record the closest literature equation, model identity, domain, proof strength, and material difference. Explicitly distinguish a generic SOS optimization method from a new Zee physics bound. Provide search queries, dates, paginated counts/coverage and incomplete citation edges; do not assert exhaustive absence.

**Non-negotiable falsifier:** independently rederive/evaluate the exact 2005 Eq. (23) in compatible conventions on a suitable physical charge-breaking stationary witness. Note its domain/parametrization; if its assumed nonzero coordinates do not cover a witness, do not force a correspondence. Check the published 2021 original vacuum search against our own full-field results, and whether a proposed new inequality is merely 2005 Eq. (23) rearranged.

## Work package 2 — audit and independently reproduce D10

Repeat foundational D10 tests and reconstruct the saved certificate independently:

- compare exact scalar polynomial from independent real-component expansion versus frozen potential at generic complex charged configurations, incl. signs of Mu4, K12, LambdaC; gauge invariance, first and second derivatives, null Goldstones;
- verify the identity for V−VEW, square completion and strict conditions using exact coefficients, not copied printed algebra:
  
  q=(x,y,u,w,s), q0=(a²/2,b²/2,ab/2,0,0), D=xy−u²−w²=|d|²;
  
  V−VEW = (q−q0)^T(C−epsilon J)(q−q0)
  + epsilon |d+(Mu4/epsilon)S|²
  + [mD²−epsilon (a²+b²)/2] B
  + [mS²−Mu4²/epsilon] s,
  
  where B=|b Phi1−a Phi2|²/(a²+b²), J implements D.
- reproduce exact rational LDL/PSD, exact EW-root interval enclosure, and stored positives D7, F13_heavy_0001330, aligned control; locate all seven original D10 representatives/controls and their vacuum statuses;
- independently revalidate saved negative witnesses: pure singlet and **P2_Mu4_scale_1.5**, including actual lowered energy, field configuration, local Hessian and gauge-zero modes;
- check archived 33/225 certificate provenance, and avoid reclassifying 192 UNKNOWN as FAIL.

A numerical solver status, BFGS success, same-code replay, negative Gram pivot, or inability to find a deeper minimum is not proof of globality/non-globality. Positive certificate must be an exact identity plus exact/interval PSD proof; negative certificate can be an exact/interval verified **field configuration** with V(field)<VEW and correct fixed model, whether or not stationary. The scalar model has gauge-related non-isolated stationary manifolds: witness search and homotopy root certification on one chart DO NOT prove exhaustion.

## Work package 3 — independent necessary cubic-coupling bound from field witnesses

This is the **first important numerical kill test**: reproduce OR REFUTE the previously discussed P2 necessary bound near **Mu4 <= 1346.14 GeV**. It was previously given as a rough inference, not a certified theorem; do not accept by repetition.

For a full-field *fixed* trial phi with nonzero Re(conj(S)d), at fixed non-Mu4 Lagrangian coefficients:

DeltaV(phi;Mu4) = DeltaV0(phi) + 2 Mu4 Re(conj(S)d).

Verify this affine relation symbolically from frozen potential and independently in real components, with correct field normalization, sign, and unit dimensions. Choose physical singlet phase/orientation that lowers V for the chosen sign of Mu4. Derive the **necessary condition on Mu4** from the exact trial configuration; interval/rational-evaluate the threshold against the exact certified EW root. Reconstruct P2 witness with the binary64 saved inputs interpreted exactly as the native implementation and correct stationary reference. Check at Mu4=943.400148, 1179.250..., 1415.100223 GeV and on both sides of the inferred threshold; verify original EWSB charged eigenmasses and local Hessian at each.

Be explicit: a single trial field yields a **one-sided necessary** bound on global stability for the fixed parameter slice; it does NOT prove stability below the bound or universally across parameter space. If the 1346.14 GeV estimate is false, state why and retire it; do not silently shift constants. For a collection of verified fixed test fields phi_j, take the strongest of the individual necessary inequalities with transparent sign handling; do not call this a globally optimized bound without proof.

Derive an independent **positive sufficient stability lower interval** from the existing exact D10 square completion, treating epsilon as an auxiliary variable under C−epsilon J PSD, mD²−epsilon n/2>=0, mS²−Mu4²/epsilon>=0. Explore whether the positive-certificate range and the negative-witness range can be narrowed enough to be physically useful. FAILURE of this sufficient ansatz is UNKNOWN. Report the gap between certified sufficient and certified necessary regions.

## Work package 4 — exact orbit-space reduction / stronger global methods

Try to improve the certificate without losing any charged/CP/gauge direction. Important orbit constraints:

x>=0, y>=0, s>=0, and u²+w²<=xy; D=xy−u²−w²>=0.

The independent complex singlet phase can minimize V3 at fixed orbit invariants, so for |Mu4|>=0 use the **exact** phase-minimized potential:

V_orbit,min = V2+V4−2|Mu4| sqrt[s (xy−u²−w²)].

Prove the orbit representation is complete and construct full complex fields for random feasible orbit points and all boundaries. If using polynomial auxiliaries, impose all necessary nonnegative/equality constraints and prove the two directions of equivalence; avoid dropping an inequality or minimizing over an unphysical superset. An independent second formulation should use full 10 real fields or an explicitly proven gauge-fixed Gram coordinate system. Treat u,w boundaries, s=0, D=0, Phi1=0/Phi2=0, vanishing Mu4 and complex phases.

Investigate at least TWO independent stronger approaches if practical and accessible, selected using the software audit below:

(A) sparse or structured SOS/Positivstellensatz optimization on the physical semialgebraic set with rational/interval certificate extraction, exploiting symmetry and degrees; use bounding ball ONLY if the existing D10 coercivity/radial exclusion is independently verified and sufficient to prove the exterior cannot beat the EW orbit;

(B) a gauge-reduced polynomial stationary-system search using homotopy/Groebner basis and interval root verification, explicitly stratifying singular cases, residual gauge directions, non-isolated components and chart boundaries.

If (B) does not exhaust all real solutions, report only **located/certified local extrema**, not complete global classification. If (A) obtains a merely numerical SDP dual/Gram matrix, label it NUMERICAL_SOS_CANDIDATE until an exact rational/interval verified identity, PSD and domain certificate exist. No inferences from infeasible SOS relaxations to instability. A single infeasible relaxation is NOT a counterexample.

Useful alternative: field-configuration witness optimization plus interval subdivision of the compact gauge orbit, if a full SOS/stationary solution is not computationally affordable. An approximate global optimizer alone cannot certify absence of lower minima.

**Investigate completeness cost before a high-degree full ten-field SOS.** Prefer the orbit-space five-invariant formulation and low-degree/sparse certificates. No false absolute proof from merely increasing starts/orders.

## Work package 5 — maximize actual reusable public code, with a source/reuse ledger

Public code and documentation *starting points* below have been located. Inspect live license, tags/commits, dependencies and supported solver features; pin versions/SHAs. Prefer EXISTING packages over writing a new SDP, homotopy or polynomial engine. Do not assume packages are installed or that a successful build validates this Zee model.

- **Our frozen D10** — first-class reference: exact SymPy/Fraction certificate, Krawczyk enclosure, polynomial/equations, gauge-aware numerical search. Read-only.
- **SumOfSquares.jl** (https://github.com/jump-dev/SumOfSquares.jl), **JuMP**, **DynamicPolynomials.jl**, plus **Clarabel.jl** or another actually available open-source PSD-capable solver: numerical SOS/weighted semialgebraic certificates. Read https://jump.dev/SumOfSquares.jl/dev/generated/Extension/certificate/ before choosing the exact domain API. A solver result is not an exact proof.
- **TSSOS** (https://github.com/wangjie212/TSSOS): alternative sparse SOS/Putinar workflow; validate current API, solution quality and domain mapping independently. Try it if it gives a real computational advantage, not merely for a package-count checklist.
- **HomotopyContinuation.jl** (https://github.com/JuliaHomotopyContinuation/HomotopyContinuation.jl) for complex-root continuation and certified nonsingular isolated roots. Its Krawczyk local root certificates do not certify *all* solutions or positive-dimensional varieties. Use only after gauge elimination, valid chart/stratum accounting and testing a small control.
- **OSCAR.jl / Singular** (https://github.com/oscar-system/Oscar.jl), or SymPy/SageMath if available, for exact polynomial ideals, elimination and rational checks; use only on a manageable system with a clear mathematical objective.
- **Vevacious / Vevacious++** (https://github.com/benoleary/Vevacious) and SARAH model export as an **independent, documented numerical vacuum cross-check** only if realistically runnable with the *correct charged/complex VEV set*. Its search and potential one-loop stages must NOT be relabelled exact global certificates. Existing SARAH/SPheno full-loop numerical issues make unvalidated automatic loop output unacceptable.
- Optional SOSTOOLS (https://github.com/oxfordcontrol/SOSTOOLS), via MATLAB plus a compatible installed SDP solver, **only if** licensed software/runtime is already available and an open Julia route is unsuitable; not necessary to use every stack.
- CVXPY/SymPy/MPMath/interval arithmetic, scipy for bounded witness search, and precise rational/interval PSD verification are useful complementary backends; benchmark solver statuses against an independent identity and test cases.

Execution policy: audit installed binaries, OS, versions and current source pins. Create at most ONE dedicated isolated Julia environment when useful. Place package trees/cache/build intermediates in ignored scratch, not the tracked repo. No systemwide pip upgrades, no destructive environment changes, no use of proprietary solvers requiring new licenses. Keep command + actual exit code + time/CPU/memory and diagnostic reason for every attempted package. Prefer two successful *independent* algorithms over six installed but unvalidated packages. If a software stack fails due to a source/API issue, document it and move to a viable alternative instead of spending the whole task repairing installers. Do not claim a package independently reproduces physics if it merely solves the same mis-specified polynomial.

**Scope/resource cap:** no Condor or broad distributed compute; cap any single solver attempt at 45 minutes and approximately 16 GiB resident memory, and aggregate new numerical solver runs at ~12 CPU-hours unless an existing already-running computation was user-authorized separately. Record wall/CPU and whether the environment supports this. If the cap is reached, report remaining bound gaps as UNKNOWN; do not request endless background work.

## Work package 6 — targeted exact potentials and physically consistent continuation

Primary test set:

1. Exact D10 P2_beta_shift and its existing Mu4 multipliers (0, 0.5, 1, 1.25, 1.5), including its verified deeper charge-breaking configuration at 1.5;
2. Exact D7 certified scalar card;
3. Exact F13_heavy_0001330 certified card;
4. historical F13_0000981 and F13_0001003 UNKNOWN certificate cards;
5. aligned-decoupling certified positive control and singlet-only deeper-vacuum negative control.

Read the archived 33/225 sufficient certificate result and at most revalidate it from source records; do not launch another 225/20k production scan. If needed for *a sharply defined P2 threshold*, allow a deterministic scalar-only Mu4 bracket refinement with at most 32 evaluation points total on the P2 path (not 32 per solver), recording every evaluated point, parent source hash and held-fixed coefficients. Additional exact card cases at most 2 smaller deterministic 1D Mu4 slices, only if the first P2 proof and physical link warrant a robustness check; at most 12 points per extra path. No random / adaptive full potential scan and no Yukawa or neutrino refitting. A locally unstable or charge-breaking path is not globally Zee-disallowed under uncomputed full model experimental gates; explain tree statement only.

For each actual path sample, independently verify:
- no unannounced change of neutral EW tadpoles or quartics; BFB and tree unitarity whose parameters remain fixed, without silently promoting EWPO on changed masses;
- local EW transverse Hessian and charged masses positive, gauge/Goldstone modes correct;
- Mu4–mass–gamma signed consistency and the resulting off-diagonal Z gauge coupling;
- certified POSITIVE sufficient vacuum, certified NEGATIVE deeper field, or UNKNOWN; show every status, never infer FAIL from unavailable SOS;
- threshold continuity/precision and effect of field-witness refinement and numerical tolerances.

The *necessary* global-stability upper threshold found from field witnesses may be higher than the *sufficient* guaranteed-stability lower threshold; graph and tabulate the unknown gap. If local charged-mass positivity or another fixed theoretical requirement excludes an interval earlier, say so: the vacuum argument must add nontrivial information beyond tachyonic masses/local BFB/perturbative unitarity.

## Work package 7 — propagate to observables, but do not claim LHC reach

Using exact same-path scalar cards and frozen signed vertices, compare:

- |g(Z H1 H2)| in the verified source convention, including zero-mixing and maximal-mixing controls;
- scalar mixing gamma, sin(2gamma), charged masses and threshold mH2−mH1 compared to mZ;
- tree on-shell Gamma(H2→H1 Z) from independent analytic D2/D4 validated formula and second signed-vertex calculation where feasible;
- ratio of this **partial** width across certified stable, certified unstable and unknown regions; do not silently call it a BR when the rest of H2 width is not recomputed from a complete consistent card;
- if BR is needed, recompute the complete *stated tree two-body* width ledger under the same potential/other couplings, label its missing off-shell/QCD/EW effects, and do not claim physical global acceptance.

Prove that an alleged upper bound on |g| or Gamma is truly necessary for the stated slice (or only sufficient-domain), taking mass-dependence/phase space into account. Do not infer an upper bound on Gamma simply from an upper bound on Mu4: phase-space/mass dependence can be non-monotonic. Avoid a universal Mu4 max or sin2gamma bound from one P2 path. Compare bound strength to the known 2021 mixing dependence; a formula rewritten in observable notation is not new physics.

NO MG5 event generation, Pythia, shower, Delphes, backgrounds, pyhf, 14/100 TeV cross-section production or HL-LHC/FCC-hh sensitivity. Collider relevance may be **kinematic/theoretical coupling and partial-width** only.

## Work package 8 — hostile-review novelty and decisive outcome

Produce a proper independent comparison:

- The 2005 Zee charge-breaking potential-depth formula and observed deeper-vacuum phenomenon;
- the 2021 boundedness/CB numerical analysis and already published Z-mixing/cascade;
- generic SOS positivity and Vevacious/homotopy methods (method novelty versus model-specific quantitative outcome);
- your rigorous new positive/negative bounds, exact model scope, actual additional parameter exclusion beyond local scalar checks and numerical materiality;
- whether an example is simply selected to make a figure, rather than a robust reusable constraint;
- validity of statements for *the restricted CP-conserving scalar sector*, not general complex Zee/lepton model.

Classify each candidate contribution as ALREADY_DONE, INCREMENTAL, NEW_THEOREM_OR_REUSABLE_BOUND, CONDITIONAL_NUMERICAL_DEMONSTRATION, or UNSUPPORTED, with exact literature locators.

Deliver **one** release verdict:
- GO_SCALAR_THEORY_PAPER_CANDIDATE: at least one independently verified, source-differentiated reusable theorem/bound and quantitatively consequential scalar/charged-mixing impact beyond 2005/2021; include explicit counterexample and actual range of applicability.
- NO_GO_CANDIDATE_A: existing work replicated/rewritten, certificates too conservative to affect observables, only a contrived 1D slice, or bound dominated by already-known local conditions.
- INCONCLUSIVE_METHOD_BLOCKED: originality/rigorous bound cannot be established within the recorded resource/runtime/input limits; NOT a positive verdict.

A successful 2005 reproduction, 3 passing unit tests, a positive Julia solver report or a single nice plot **never suffices**. Include a hostile-referee paragraph that could still reject a GO verdict. Do not promise journal acceptance. If NO-GO, explicitly retire Candidate A as an independent paper center, preserve all reusable code, and stop without proposing another big build automatically.

## Deliverables — evidence-backed, reproducible, one commit or a compact commit series

Write new material **only** under research/full_constraints/candidate_a/ and one summary report:

- research/full_constraints/CANDIDATE_A_DECISIVE_REPORT.md — executive decision, explicit theorem statements/scope or failed attempts, exact numbers, claim–evidence matrix, comparison against 2005/2021, code reuse and compute costs, real physics significance, reviewers' objections, final GO/NO-GO.
- candidate_a/PUBLIC_CODE_AND_SOURCE_REUSE.md — tools/literature links, pinned versions/commit/LICENSE, commands actually run, numerical/equation scope and why alternatives were or were not used.
- candidate_a/LITERATURE_NOVELTY_MATRIX.md — search ledger, 2005 Eq.23 and 2021 equations/figures, compared theory statements, relevant citing papers, coverage gaps.
- candidate_a/VACUUM_MIXING_BOUNDS.json — exact card hashes, fixed-coefficient slices, analytic inequalities, lower/upper *certified* ranges vs UNKNOWN, P2 1346 claim reproduced/refuted, local-mass/EW controls, units, observed test output, null semantics.
- candidate_a/CERTIFICATES/ — small machine-checkable exact SOS/LDL/interval witness data, polynomial coefficient/signature inputs, exact rational negative field witnesses where possible; distinguish experimental solver candidates from verified certificates.
- candidate_a/REPRODUCE.md — environment/version matrix, self-contained commands to reconstruct exact source checks, bound, non-global witness and physical partial-width mapping; optional numerical solver instructions.
- Small stand-alone source-read-only adapters/tests if needed; at most 3 informative figures: (1) Mu4/charged-mixing vs rigorous stability classification and unknown band; (2) certified bound vs partial width/coupling; (3) method/certificate comparison only if a substantial new result exists. Figures must not claim global accepted Zee parameter space.
- Full run receipts and large solver matrices/logs remain in ignored scratch; only compact proof objects and summary artifacts committed.

At minimum rerun original D10 tests, independent full-polynomial/sign gauge controls, 2005 Eq.23 source validation if its domain is applicable, exact positive controls, exact negative witnesses, threshold sign/energy bracket, and physical charged-mass/vertex relations. Tests must distinguish source replay from independent mathematics. Save real stdout/exit codes, number of executions and actual values, git diff --check and final git status; no fake PASS. A compact negative result with exact failure reasons is a valid outcome.

Follow existing repo style: source first, tight isolated research changes, English report/commits, no secrets or large binaries, **do not change AGENTS.md beyond the task pointer already supplied by the user**, do not merge to main/frozen branch. Commit and push validated outputs only on research/zee-full-constraints. In the final Codex response give (1) definitive verdict; (2) highest-impact verified theorem/bound and numbers, or reason for failure; (3) exact 2005/2021 originality difference; (4) public tools actually executed and fallbacks; (5) scope and remaining UNKNOWN; (6) tests, changed paths, pushed SHA. Do not ask the user to launch follow-up pilots to finish this assignment.
