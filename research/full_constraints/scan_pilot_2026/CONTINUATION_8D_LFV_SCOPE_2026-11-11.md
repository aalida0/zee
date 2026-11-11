# Zee charged-cascade phenomenology — LFV rescue and independent flavor geometry
**11 November 2026; scope: numerical diagnostic, not full-physics acceptance**

## Executive verdict
The source-retained LFV amplitudes **can be suppressed** on the previously D10 vacuum-certified
Zee scalar 2264, while keeping exact algebraic neutrino closure and a substantial
tree-level \(H_2^\pm\to H_1^\pm Z\to tbZ\) cascade. The new benchmark is a
**fresh, explicitly frozen neutrino family**, NOT the historical IO family-1
from the original 20k scan. Physical LFV/B/Higgs/collider acceptance remains
UNKNOWN. This is an independently replayed **numerical witness**, not a fully
allowed point.

## Provenance and numerical validation
- Original charged spectrum and scalar SHA: `2264`,
  `49d468ccfd1262ea2900ac41479071e821475f854c3b13441130c6a289417c8e`,
  \(m_{H_1^\pm}=674.274427\) GeV, \(m_{H_2^\pm}=1165.974815\) GeV.
- Fixed original D10 sufficient vacuum certificate **PASS**.
- Nominal original B->Xs gamma approximate compatibility **only**;
  no full physical rate/NP uncertainty certificate.
- Original historical IO-family-1 hash replay fails under fresh CI despite
  same seed and scalar; target and Yukawa SHA hashes differ. **Do not suppress
  this mismatch, label that original family source-replay BLOCKED.**
- New independent family seed `20261111`, IO family-1, with a **new** neutrino
  target and four complex homogeneous coefficients. All scalar and flavor
  source inputs are serialized in `2264_fresh_8d_reference.json`.
- Frozen new optimized neutrino-input SHA:
  `fc8ffa5998645aac9ea24571235eb1e869e064167b744abc3a600c476d286fec`.
- CI optimization and closure PASS:
  https://github.com/aalida0/zee/actions/runs/43071227052
  (4 tests PASS; 306 distinct source evaluations; two optimizer starts).
- Independent-from-optimizer *numerical* replay of the complete saved input
  PASS on Python 3.10.12 and Python 3.11.11:
  https://github.com/aalida0/zee/actions/runs/43071955206
  (same Module2/4/D4 implementation; **not** independent Feynman-diagram
  validation).
- Frozen 4x8 real Jacobian differential-rank CI PASS:
  https://github.com/aalida0/zee/actions/runs/43072400936

## One source-pinned fresh-family numerical witness
- Ordering IO; \(\tan\beta=1.05357945\), \(\gamma=0.85449927\) rad.
- Source h125 `kappa_V=cos(alpha-beta)` gives \(\kappa_V=0.999862856\)
  (model's specific convention), \(\kappa_u\simeq0.984144\),
  \(\kappa_d\simeq1.017311\). **Not** a full Higgs pass.
- \(\max|Y|=0.00740076\);
  neutrino forward closure \(7.35964\times10^{-16}\).
- INCLUDED coherent Module4 terms only:
  \(\mathrm{BR}_{\rm partial}(\mu\to e\gamma)=4.74683298035\times10^{-23}\)
  versus the *snapshot* MEG II upper limit \(1.5\times10^{-13}\) (90% CL).
- Other INCLUDED radiative BRs:
  \(\mathrm{BR}_{\rm partial}(\tau\to e\gamma)=6.18031\times10^{-16}\);
  \(\mathrm{BR}_{\rm partial}(\tau\to\mu\gamma)=7.49231\times10^{-13}\).
- Neutral tree subset \(\mathrm{BR}_{\rm tree}(\mu\to3e)=2.63138\times10^{-36}\).
  Missing photon monopoles, non-tree operators/interference and conversion
  are **NOT** implicitly zero.
- Full D4 **on-shell tree two-body**:
  \(\mathrm{BR}(H_2\to H_1Z)=0.368670816\),
  \(\mathrm{BR}(H_1\to tb)=0.997185603\),
  cascade product \(0.367633230\).
- 13 TeV LO scalar quark-hard-process **conditional proxy only**:
  historical source \(\sigma(pp\to tbH_2)=0.0050014\) pb
  times new tree cascade product gives \(1.838680836\) fb, or
  \(5.516\times10^3\) **pre-detector** cascade events at 3000 fb^-1
  if the original 13 TeV quark-only production rate applies unchanged.
  This is neither 14 TeV reweighting nor an ATLAS sensitivity forecast,
  and the old full-input source binding has not been revalidated for the
  new lepton family. Parton/PDF/scale theory uncertainties not assigned.

## Local geometry, not statistical model-space acceptance
The real Jacobian of \(\Re C_L,\Im C_L,\Re C_R,\Im C_R\) with respect to
8 real homogeneous coefficients has rank 4 in the retained Module4
prescription, singular values (normalized to the retained MEG-II amplitude
threshold) `34.293852, 34.293852, 33.813904, 33.813904`.
Thus four locally null tangent directions, which is **consistent with
ordinary parameter counting** and is **not itself a paper novelty claim**.

At absolute coefficient displacement \(3\times10^{-6}\), the signed
four sensitive singular directions exceed the partial LFV limit
(~\(1.54-1.59\times10^{-13}\)); signed four null directions leave the
retained rate ~\(4.74683\times10^{-23}\). The auxiliary 40-direction
random/Cartesian diagnostic at displacements \(10^{-7},10^{-6},3\times10^{-6}\)
reports 40/40, 40/40 and 35/40 below the **retained** limit. These are
seeded directional tests, **not** eight-dimensional permitted volume fractions.

## External published calculation / public code assessment
1. Florentino–Romão–Silva, *Off diagonal charged scalar couplings with the Z
   boson: Zee-type models as an example*, EPJC 81 (2021) 1148,
   https://arxiv.org/abs/2106.08332 — cascade precedent. New cascade
   branching fractions alone cannot establish novelty.
2. Herrero-García et al., JHEP 04 (2017) 130,
   https://arxiv.org/abs/1701.05345 — full general Zee model scans;
   benchmark flavor+collider correlations require direct comparison.
3. Heeck–Thapa, PLB 841 (2023) 137910,
   https://arxiv.org/abs/2303.13383 — Zee LFV with dominant diagrams
   and explicitly stated omissions (some bosonic/charged two-loop terms
   suppressed under specific alignment/interaction assumptions).
   Their approximation is **not** a proof all those terms are small in
   every 2264 coupling configuration.
4. Altmannshofer et al., JHEP 06 (2025) 156, 2026 erratum JHEP07(2026)184,
   public corrected `general-2hdm-pheno` code at
   https://gitlab.com/jbrod/general-2hdm-pheno — complete general-2HDM
   two-loop observables **without** the extra Zee charged singlet/mixed
   electroweak structures; prior source-locked reuse already includes the
   matching neutral-fermion/photon terms, so no double counting.
5. Schmidt–Vandeleur, JHEP 06 (2026) 006,
   https://doi.org/10.1007/JHEP06(2026)006 — Zee EFT/RG corrections to
   neutrino parameters, relevant to stability of tuned flavors across
   running. Article declares no deposited associated code.
No newer public implementation was identified that establishes a
full, source-matched Zee gauge/mixed two-loop amplitude here.

## Minimum next decisive work
**Priority 1 — justify a scoped LFV prescription.** Quantify the omitted
gauge/mixed charged-scalar terms with a coupling-aware upper envelope
against the **absolute**, not retained-relative, remaining amplitude
budget. Repeat the other independent channels: complete mu->3e
coherent non-tree and mu-e conversion, or explicitly label their absence.
If no certified omission bound exists, all LFV claims remain conditional.

**Priority 2 — B gamma rate/uncertainty and Higgs direct searches.**
Test this exact new scalar/lepton card under the currently incomplete
B->Xs gamma physical theory uncertainty, and complete heavy-neutral
width/production/limits. A favorable B diagnostic and near-SM h125
couplings do not clear these gates.

**Priority 3 — conditional collider study.** Only after scope is frozen,
produce a same-scalar-card 13/14 TeV charged-Higgs rate and
transparent parton-level reach/proxy; no detector simulation required for
a carefully scoped phenomenology paper, but do not claim an ATLAS
exclusion/discovery or statistical acceptance without efficiencies and
uncertainties.

**Global physics verdict: UNKNOWN. Full-constraints scan: BLOCKED.
Retained-LFV texture feasibility: NUMERICALLY DEMONSTRATED.**
