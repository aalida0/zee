# Codex AGENTS — Zee Type-II full physical-constraint research

**Research branch:** `research/zee-full-constraints`.
**Frozen working parent:** `feature/zee-d14-conditional-cascade-scan`
at `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

## CURRENT TASK — fixed-card neutral H/A widths and usable Higgs search

Read **`research/full_constraints/HIGGS_NEUTRAL_WIDTH_SEARCH_TASK.md`**
first, including its references to the SusHi/HDECAY execution report,
HiggsTools analysis coverage and frozen D12 D7/F13 cards.

**B→Xsγ fixed-card NLO validation / uncertainty work is completed
within the known scientific scope** at commit `59e919f`.
The central two-scalar HEPfit/SuperIso rate, a seven-input correlated
block and 69 nuisance/scale computations are archived and tested.
The historical Type-II confidence control gave 473.1 GeV vs published
480 GeV. Wilson-dependent nonlocal/resolved-photon covariance,
charm-scale physical variation and omitted-effect materiality remain
unqualified. **STOP solo B-code work now**. Use
`research/full_constraints/bsgamma_hepfit/specialist_question.md`
to obtain outside theory guidance if/when user authorizes.
No more rate reimplementation or ungrounded `theory_sigma`.
B `B_FULL_RATE_BLOCKED`; no physical exclusions.

**Focus Higgs:** native source-validated SusHi 1.7.0 LO 13-TeV
H/A ggF/bbH production is available for ORIGINAL D7/F13 cards,
including tested PDF/scale response. HDECAY 6.60 partial widths and
native Zee charged-W/general-lepton additions are incomplete but
reusable. Execute fixed-card F13 HDECAY transfer and independently
validate model-matched H/A→γγ and all relevant competing widths.
Attempt at least one genuinely applicable HiggsBounds observed
search only with complete BR, production/acceptance assumptions
and justified uncertainty. Missing contributions remain
`MISSING_PREDICTION`, not zero. A scoped result does not imply
globally allowed physics or full Higgs coverage. Full-loop
SPheno is **UNAVAILABLE**.

LFV remains `LFV_FULL_COVERAGE_BLOCKED` pending substantive
gauge-invariant theory work.

Never edit frozen Modules0–13 or the final scan branch
`feature/zee-d14-conditional-cascade-scan` at `133a340`.
No new scalar points or pilot/large scans, no Condor, no broad
MadGraph production, no global pass or final-scan launch.
Only source-pinned exact D7/F13 and original D14 saved cards
for bounded independent validation. Work on
`research/zee-full-constraints`; commit/push real evidence.
All reports and communications in English.

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

A source-verified B→Xsγ feasibility and full-rate path
(`FEASIBILITY_GATE.md`, `BSGAMMA_COVERAGE.md`), with executable
bounded controls only if scientifically supported. Commit and push
to this research branch. Retain unvalidated results explicitly
research-only and the original conditional pipeline unchanged.
