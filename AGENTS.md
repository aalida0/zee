# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## Mandatory source-first literature gate (new: 7 Nov 2026)

Before claiming any Zee-specific loop calculation, scalar/vacuum constraint,
flavor uncertainty, or numerical implementation is absent from the literature,
**read** `research/full_constraints/LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md`
and the actual paper full text, then check relevant **references AND citing works**.
Document DOI/arXiv, exact equation, physical particle content, Yukawa
restrictions, source/code version, and a tested limiting case. A previous
false absence claim overlooked Florentino–Romão–Silva 2021 App. D.3 Eq(D.20)
for mixed charged-scalar h→Zγ, Hue 2018 unequal-mass PV formulas,
Bilenky–Santamaria 1994 singlet EFT, and old Zee LFV box/Z-penguin formulas.
Do **not** call an unimplemented published expression nonexistent; do not call
a restricted formula complete general Zee physics. Citation-search indexing is
not exhaustive; report limitations. Always preserve original frozen modules.

## CURRENT TASK — decisive LFV texture materiality for a simple paper

**User direction:** continue actual physics using justified published
approximations, with no more endless generalized two-loop projects.
READ `research/full_constraints/LFV_TEXTURE_FEASIBILITY_GATE_2026-11-07.md`
FIRST and `research/full_constraints/LFV_PUBLIC_CODE_REUSE_AUDIT_2026-11-07.md`,
then the original D12 study
`module12/D12_FLAVOR_COLLIDER_AUDIT.md` and
`research/full_constraints/LFV_COVERAGE.md`.

**Major existing source-backed result:**
D12 has already produced 112 neutrino-family designs and 24 actual
coefficient perturbations (136 full inversions) at original D7/F13
NO/IO spectra. Targeted direct-eμ texture cancellation gives
F13 NO and IO **partial** BR(μ→eγ)=4.031e-20 and 1.338e-19,
respectively, while BR(H2→H1 Z)≈0.485 and BR(H1→tb)≈0.9976.
These are *not complete LFV rates*, but show the standard F13
central diagnostic excess is not a model-level impossibility.

The saved central complex Wilson coefficients calibrate the
MEG II 90% CL limit at `||C_lim||=1.36778582408e−12 GeV−2`.
On all four saved low_joint texture witnesses, **if**
the total as-yet-omitted complex dipole vector has norm
`||ΔC_missing|| < 1.364e−12 GeV−2`,
then the limit is satisfied for these witnesses by the triangle
inequality. This is a **sufficient conditional target, not
a physics estimate/bound on ΔC_missing**. See
`lfv/TEXTURE_MATERIALITY_DIAGNOSTIC.json`.
F13 `texture_0.001` ±1% saved variants remain below the
measured bound in the retained subset; D7 `texture_0.0001`
nominal low_joint variants are not robust to ±1% in the
tested homogeneous direction, but D7 `texture_0.001` is.

**NEXT BOUNDED EXECUTION — do actual physics work, not another
preparatory paper search/toolchain audit.**
1. Run and independently check
`python3 research/full_constraints/lfv/texture_materiality_gate.py`
on existing D12 full-precision JSON; compare the reported budget
and source source-hashes with the rounded committed table.
If the script has an error, fix it in this research branch,
never change the original D12 source.
2. Investigate the **actual** potentially leading omitted
`μ→eγ` amplitudes only on the original F13 NO/IO low_joint
and D7 low_joint cards. Rank the missing non-overlapping
2HDM `Zγ/Wγ/kinetic` and Zee mixed-F charged-current
sectors using the *source-validated* post-2026-erratum
2HDM code, published Zee limits, stored Yukawa tensors,
and genuine chiral/loop-mass power counting. Preserve
both complex chiralities. Reuse existing Module3/4 code,
do not double-count neutral-fermion/photon or
charged-scalar/photon terms. A **quantitatively justified
combined-norm bound** and its derivation are the goal.
If such a bound cannot be established without
a multi-week general calculation, stop and label
physical LFV UNKNOWN: do not infer it from
small partial rates, Yukawa textures, or loop factors alone.
3. If a sound `μ→eγ` approximation is obtained, test
complete leading `μ→3e` operator interference at
same F13 low textures using native generated
SARAH/FlavorKit and independent flavio EFT rates;
separate diagnostic tree and full result.
4. Produce `research/full_constraints/LFV_TEXTURE_MATERIALITY_RESULT.md`
with source/version/formula, per-topology numeric evidence,
the ±1% perturbation caveat, exclusion/UNKNOWN and
B/Higgs/vacuum caveats. Goal is a modest neutrino+LFV-
informed charged-cascade paper, not sophisticated precision.
No new point, full parameter scan, Condor, MG5 or additional
unrestricted custom loop project. No formula absent claims
without looking at original full text and cited work.

**Environment decision:** SARAH/FeynArts/FormCalc combined kernel
is blocked, despite fixed scratch `ReadForm`; FlexibleSUSY
is an OPTIONAL independent check, not a precondition.
STOP debugging/reinstalling that toolchain for now;
use current validated SARAH/FlavorKit pieces and
public code/analytical results.

**Scientific release:** all previous `B→Xsγ` theory
uncertainties, Higgs signal strengths and quantum vacuum
limitations remain. `physical_lfv=UNKNOWN` and
`global_acceptance=null` until independently validated
per-observable full amplitudes/physical exclusions.
D12 targeted family isn't statistically representative or
a global-flavor-allowed population.

Research branch `research/zee-full-constraints` only.
Frozen Modules0–13 / old D14 pipeline/scanners/read-only
data and `feature/zee-d14-conditional-cascade-scan` at
`133a340` remain protected.
Commit and push the verified report/code on this branch.

## Mandatory physics safeguards

- "Complete" means all materially relevant contributions at the
  **explicitly declared perturbative order** with justified numerical
  and theoretical uncertainties, correct interference and physical
  confidence interpretation. Not literally all perturbative orders.
- Two mixed Zee charged states are NOT separately subject to the
  single Type-II 670 GeV bound. Use coherent Wilson coefficients.
- The corrected general 2HDM two-loop LFV backend is NOT complete Zee;
  the neutral fermion/photon subset is already in Module4 and must
  not be double-counted.
- SARAH/SPheno **full-loop observables are unavailable** (unphysical
  ~10^6 GeV WW loop widths and eV neutrino input-scheme mismatches).
  Compiling the backend did not validate its physics.
- HiggsTools requires source-bound rates for every applicable
  channel and collision energy; missing predictions are NOT zeros.
- A validated single failing observable can yield PHYSICAL_FAIL.
  `global_acceptance=PASS` requires all mandatory observables
  independently covered. Any uncomputed mandatory observable -> UNKNOWN.
- Original Modules0–13, D14 scanners/reports, 20k/225 collections,
  16-point MG5 map, all frozen source/receipts and separate B research
  branch are **read-only**. Work in `research/full_constraints/` and
  isolated optional adapters, retaining complete provenance and tests.
- No new parameter-space proposals (even a pilot), no exploratory
  scans, no Condor submission, no production campaign, no unauthorized
  merge into the frozen final-scan branch. Existing saved cards and
  analytic model-limit controls may be evaluated for validation only.
- Timebox/source-gate every area. A blocked full-physics result must
  remain UNKNOWN, not become a soft/conditional claim mislabeled 95% CL.
- Use English for all Codex sessions, notes, code review and commits.

## Current deliverable

`research/full_constraints/LFV_TEXTURE_MATERIALITY_RESULT.md`,
with the precise source-matched missing-amplitude bound
(or a documented reason it cannot be justified at
phenomenology accuracy), before any future scan. Cite
`LFV_TEXTURE_FEASIBILITY_GATE_2026-11-07.md`
and never mislabel missing terms as zero.