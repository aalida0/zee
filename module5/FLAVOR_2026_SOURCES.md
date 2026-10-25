# Module 5 source hierarchy: HyperIso and 2026 Bbar -> Xs gamma

Scope: source-pinned context for an independent two-charged-scalar Zee-model flavour interface; this is **not** a computed physical BR, exclusion, or globally allowed point.

## Primary flavour framework (not SuperIso)

- T. Reymermier, N. Fardeau, F. Mahmoudi, *HyperIso: A general BSM calculator for flavour observables*, arXiv:2607.18222 (July 2026): https://arxiv.org/abs/2607.18222
- Official repository: https://github.com/Hyperiso/Hyperiso ; inspect/tag **v1.0.3** (17 July 2026); archived software DOI: 10.5281/zenodo.21447072.
- At v1.0.3, `reproducibility/manifest.json` specifies: **R1** C7/C8 matching and low-scale Wilson coefficients; **R3** BR(B->Xs gamma); **R6** THDM NNLO B-sector Wilson coefficient benchmark. The archived R1 and R6 commands default to `--qmatch 81` GeV; **the Misiak Eq.(4) convention requires mu0=160 GeV**, so reconcile explicitly, never transfer coefficients blindly.
- The software provides C++/Python/CLI, SM, THDM, SUSY, and MARTY-based generic-LO Wilson workflows. **No supported public Zee two-physical-charged-scalar injection interface has yet been demonstrated.** An archived THDM model does not automatically implement this Zee model.

## Primary 2026 precision theory/experimental baseline

M. Misiak et al., *The Inclusive Bbar -> X_s gamma Decay Rate with Higher Precision*, arXiv:2608.29863v1, submitted 30 August 2026. Source: https://arxiv.org/html/2608.29863v1, Section IV, Eqs. (3),(4), LEFT basis Eq. (2).

For CP/isospin averaged inclusive BR with E_gamma >1.6 GeV:

`BR_SM = (3.54 +/- 0.14) * 10^-4`.

`BR_experiment = (3.49 +/- 0.19) * 10^-4`.

At `mu0=160 GeV` and **neglecting terms quadratic in NP shifts**:

`10^4 * BR = (3.54 +/- 0.14) - 8.51*DeltaC7(mu0) - 2.16*DeltaC8(mu0)`.

The coefficients and sign require the paper's Q7/Q8 definitions; do not feed an arbitrary alternative basis or a low-scale coefficient into the formula. Other operator effects and higher-order NP corrections can be relevant; the paper explicitly discusses limitations. The nominal ±0.14 pertains to the updated SM calculation, not a derivation of NP Wilson-coefficient uncertainties or the experimental covariance.

The paper's `m_H+ >670 GeV` (95% CL) applies to the **ordinary one-charged-state Type-II 2HDM**, computed with its known higher-order matching. It is NOT a bound `m_H1 >670` or `m_H2 >670` in the Zee model.

## Relation to older work

- F. Florentino et al., arXiv:2106.08332 (2021), charged mixing and two-state weighted Type-II quark couplings: existing prior art, not a novelty claim.
- Old SuperIso v5.0 / historical A1V two-state studies had sign/scheme and source-code matching issues, including sensitivity to input contexts. They cannot be treated as precision-grade evidence for Zee exclusion.
- The prewritten `module5/bsgamma_lo.py` is a deliberately restricted high-scale LO mathematical cross-check based on historic SuperIso loop functions. It must pass independent sign, normalized basis, and HyperIso source comparisons before use in the 2026 Eq.(4). No inherited 580 GeV/670 GeV hard mass cut is valid for the two-state model.

## Implementation acceptance gates

1. `LO_MATCHING_C7C8_PASS`: actual source/basis and mixing, 90-digit loop-kernel checks, independent signed two-state limit.
2. `HYPERISO_REFERENCE_PASS`: installed version pinned, official R1/R3/R6 actual tests reproducible; if unavailable, status BLOCKED.
3. `ZEE_HYPERISO_BR`: do not assert until two-state Wilson injection, operator/scale matching, consistent normalization and uncertainties are demonstrated.
4. `MISIak_2026_LINEAR_SCREEN`: treat as conditional **linearized** NP assessment only with correctly mapped `DeltaC7,DeltaC8(160)`, no nonlinear/exclusion claims beyond documented validity.
5. `GLOBAL_ZEE_ALLOWED`: expressly out of scope until scalar, neutrino/LFV, flavor, vacuum and collider constraints are combined.
