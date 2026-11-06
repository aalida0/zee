# B→Xsγ practical handoff: author outreach + cascade-aware benchmark triage

**Status:** research-only; NO B→Xsγ exclusion, likelihood, accepted-point flag or full theory uncertainty.
**Starting commit:** `4c7998579e0dacd87fb1d73fa328de8c026a9c0c`.
**Purpose:** Move the project forward without another unbounded code calculation.

## 1. External dependency

A source-backed numeric validity/error bound for the *joint* 2026 LO-NP
`(Delta C7, Delta C8)` formula is missing. The author email is drafted in
`AUTHOR_EMAIL_READY.md`; it is **UNSENT**. The proposed contact comes from the
University of Warsaw official staff directory.

Do not claim further reruns of EOS/SuperIso or another upstream software
regression will produce the missing 2026 quadratic/NLO residual by themselves.
If the author supplies a numerical table, executable, uncertainty prescription
or guidance, pin its version and test the 2026 LO equation and corrected
nonlinear results on a predeclared grid before classification.

## 2. Why cascade-aware triage matters

Frozen charged-scalar (H_2^+ \to H_1^+ Z) tree calculation:
`module7/cascade_z.py` (read-only) quotes the 2021 Zee cascade paper
and `g_{Z H_2 H_1} ∝ -sin(2 gamma)/2`.

Hence **gamma=0 and |gamma|=pi/2 imply zero on-shell two-body cascade
partial width**; points satisfying B physics because the light state is
entirely singlet can be *collider-uninteresting* for the requested cascade.
Similarly, `mH2<=mH1+mZ` closes the on-shell cascade. The archived
72-point flavor grid deliberately includes coupling/phase-space endpoints,
which must not be confused with realistic cascade benchmarks.

Some examples from `m2026_route_results.json` at `gamma=1.09`,
`tanbeta=5.3` (all **DIAGNOSTIC_ONLY**, no scalar/ν/LFV or collider
acceptance asserted):

| (mH1, mH2) [GeV] | 10^4 BR_linear(2026) | on-shell cascade? |
|---|---:|---|
| (300, 900) | 4.0764 | kinematically open |
| (550, 900) | 3.9495 | kinematically open |
| (550, 1400) | 3.8237 | kinematically open |
| (900, 1400) | 3.7592 | kinematically open |
| (900, 900) | ~3.8850 | kinematically closed |

Do not rank physical signals solely by B→Xsγ. A meaningful feasible-signal
proxy needs **full decay-table BR(H2→H1Z), cross section, scalar constraints,
neutrino/LFV and HiggsTools status**; a standalone partial width is not a BR.

## 3. Bounded next Codex work (no new final scan)

- Do not modify Modules 0–14 on the BSG validation branch.
- Prepare a read-only **data join contract** for future D14 accepted-scalar
  points and the BSG diagnostic: scalar and quark input card, beta/gamma
  convention, scheme/order/scale, source hashes, cascade BR and production,
  all individual constraints and their STATUS.
- Require complete original point cards before joining; never back-fill a
  point from its ID or summary rates. Reject mismatched parameter schemes.
- Support plotting and rank ordering **only as exploratory figures**;
  default `bsg_classification=UNKNOWN` and `globally_allowed=None`.
  Label any sample with gamma endpoints or closed Z channel explicitly.
- Upon receipt of author reply, create a bounded validation task using the
  exact data received (not assumptions) to decide between
  `RESTRICTED_FILTER_VALIDATED` and `UNKNOWN` before editing D14.
- If no author response is available, there is no reason to run more
  precision backends on the same inputs. Preserve original constraints and
  launch no claimed **final fully constrained scan**.

## 4. Do not confuse the three claims

1. The 2026 **linearized** equation is implemented and the frozen numbers
   are reproducible.
2. EOS and SuperIso measure legacy curvature and partially matched
   low-scale physical-rate differences; they are not a 2026 error budget.
3. A modern **statistically valid constraint** requires the missing
   accuracy domain/error prescription. Until then, sub-TeV charged masses
   are neither ruled in nor ruled out by this branch.

This handoff does not update D14 or create an exclusion filter.
