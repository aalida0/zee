# D16 continuation — outer two-loop projection, crossed parents, BRST/LSZ

**Starting evidence:** commit `43d8992da30f599b0ffcfea974c14475586938ac`, same branch `research/zee-d16-wgamma-gauge-matching`. D15 and Modules0–14 must remain frozen.

## Current valid work — DO NOT redo it

- Native 26-diagram inner W/G/ghost/mixed sum constructed from SARAH vertices, dimensionally integrated, with symbolic **arbitrary-ξ inner 1/ε cancellation**.
- ξ=1 finite five-tensor basis independently reproduces Abe's A/P/B/C at multiple spacelike kinematics.
- 8 W/G fixed-`r` open-lepton parent subloops integrated at ξ=1 for **one scalar placement**; independent WWW neutrino-propagator pinch proves `N=2 n² γ^μ P_L + N_rem`.
- General-ξ WWW fixed-`r` RQMC was checked against ξ=1; its errors are too large for precise gauge-cancellation claims.
- Native `sGH` couplings are nonzero and mass-dependent; full charged parents must NOT be dropped on the basis of an unweighted scalar sum.
- `parent_integrals.exact_parent_integrand()` is an explicit full two-loop integrand witness, **not yet a valid regulated outer integral**.
- `STATUS.md` correctly declares `BLOCKED_GAUGE_MATCHING`; `matching.py` returns `C_L=C_R=null` and `coherent_inclusion=false`. Preserve this until all physical requirements pass.

Read `D16_GAUGE_DERIVATION.md`, `STATUS.md`, `parent_integrals.py`, `native_integrands.py`, `tensor_reduction.py`, `longitudinal_identities.py`, `st_sources.json`, `gauge_ledger.json` and `module4/MATCHING_AUDIT.md` first.

## Objective 1 — ONE actual regulated two-loop parent at ξ=1

1. Start with the **existing** scalar-first `WWW` `exact_parent_integrand()`. Establish all loop-momentum routing and charge/current ordering. Preserve native prefactors including relative `i`, masses, weak and electromagnetic charges, chiral projectors, photon orientation, and inner vs outer loop normalizations. Use the separately calculated neutrino-pinch triangle as a cross-check, not as an inferred gauge compensator.
2. Construct a dimensionally regulated outer `r` integration and **on-shell dipole projection** in an independent Dirac basis, including the full charged lepton and scalar propagators. The output must include `1/ε`, `ε^0` and an honest audit of which subloop `O(ε)` terms multiply any outer pole. If the subloop/outer convolution is overall convergent, **prove** the required falloff before evaluating it directly in four dimensions. Never silently set `d=4` in a potentially divergent outer structure.
3. To simplify, choose valid off-shell Euclidean/spacelike kinematic points for intermediate tensor checks, but the eventual physical dipole needs an on-shell emitted photon with (q^2=0) and unequal charged-lepton masses. Define a justified analytic-continuation/threshold prescription; a naive Wick contour across poles is not acceptable. Validate against an independent parameter-space or sector-decomposition calculation at a nontrivial point.
4. Emit a **nonzero calculated one-topology `C_L,C_R` contribution** with exact normalization, signed complex values, integration error, UV structure and provenance. Label it `TOPOLOGY_ONLY_NOT_GAUGE_INVARIANT`; do not expose it as the physical W coefficient. The existing `--require-completion` exit 2 must remain while other required classes are missing.

## Objective 2 — crossed placement and charged Higgs parents

5. Obtain the opposite LFV scalar placement on the outgoing lepton line from the **native source** and implement its full propagator ordering and chiral structure; do NOT replace it with an assumed conjugate or mass swap. Compare both placements under a derived on-shell external-state crossing identity, using the D15 proven operator map as a fixed convention. Keep m_i, m_j distinct.
6. Complete the `WWW,WWG,WGW,WGG,GWW,GWG,GGW,GGG` open-lepton parent families **for both placements**, including the correct Goldstone currents and charged-lepton masses for each placement. Preserve individual diagrams and potential 1/ε poles; combine only after signed projection.
7. Use `st_sources.json` and the native charged H1/H2–G–s vertices to construct the actual charged-parent graphs (not zero by assumption). Establish the necessary mixing/mass-weighted sums; account for the charged-H doublet/singlet components. Any neutral-scalar inverse-propagator cancellation must be derived for the specific term before applying an h/H sum rule.

## Objective 3 — complete BRST / Slavnov–Taylor / LSZ terms

8. Build the missing general-ξ BRST insertion/contact terms from the **actual SARAH linear gauge-fixing and ghost transformations**. The existing `-b_μ b_ν/ξ` kernel in `longitudinal_identities.py` is nonzero; do not discard it as electromagnetic transversality. No fictitious ghost-to-lepton tree vertex should be added.
9. Enumerate and evaluate required reducible/external charged-lepton self-energies, photon attachments, field renormalization, LSZ and counterterms consistently with the chosen renormalization scheme. Distinguish physical one-loop QED corrections from pieces required by the targeted two-loop BRST reduction; avoid double counting.
10. Derive ST identities at the **complete projected two-loop amplitude** level and verify UV/local cancellations before allowing any 4D limit. An inner 1/ε cancellation alone is insufficient.

## Objective 4 — independent general-ξ gauge closure and physical release gate

11. Compute `C_L,C_R` from the **actual independent calculated graphs**, initially at ξ=1, then ξ=0.5,1,3 and at least one more nontrivial ξ. Include two independent mass/complex-coupling spectra, both scalar placements and their charged-parent/LSZ completion; quantify numerical error on cancellation.
12. Check `Δξ(C_W + C_mixed + C_ghost + C_pinch + C_charged + C_LSZ)` cancels the full independently defined Goldstone-sector variation. The existing `goldstone_projection()` was diagnostic: verify its scope and native potential/gauge vertices before equating it to the entire `C_G`. **Never** set any missing term to `-Δξ C_G` or fit a kernel to enforce cancellation.
13. Enforce electromagnetic Ward, ST, full UV, rephasing, reverse ordered amplitudes, physical nulls and nondegenerate h/H checks. Compare to Abe (with 2016 erratum), CHK and Ilisie only after identifying what actual complete diagrams each expression includes.
14. Only when every physical gate closes, update `matching.py` to return finite source-derived `C_L,C_R` with explicit input/provenance, uncertainty and applicability. Otherwise leave nulls and `BLOCKED_GAUGE_MATCHING`. No D14 integration, no complete LFV/global acceptance claim.

## Implementation detail

- Keep new work in `research/wgamma_d16/` and large source expressions/artifacts in ignored `local/`.
- The first stage should create a minimal `outer_projection.py` or Mathematica/FORM equivalent with: `evaluate_topology()` returning signed `pole,finite,C_L,C_R,precision,scope`. Use `TOPOLOGY_ONLY_NOT_GAUGE_INVARIANT` status.
- Implement a reusable check that the integrand reconstructed from the subloop and outer kernel agrees numerically with the original unsplit `exact_parent_integrand` at generic loop momenta; this checks factorization before integration. Use pointwise tests in a nonexceptional domain only.
- Keep d-dependent gamma algebra before extracting any finite term if UV poles arise. Cross-check a reduced toy scalar/tensor integral analytically and against an independent numerical method.
- A numerical `ξ` test must include propagated inner and outer uncertainties, not only pointwise differences.
- Maintain a topology ledger with explicit `COMPUTED`, `MISSING`, `NOT_APPLICABLE_PROVED` entries; missing never silently means zero.
- Run only focused tests; no restart of D15, 20k scan, or massive workflow.

## Execution plan and stop criteria

Start by closing **one actual scalar-first WWW outer integral**. If its UV/kinematic continuation is unresolved, give the exact unresolved integral, failed analytic/numerical attempt, and a minimal executable reproducer, and keep working on that concrete blocker. Do **not** spend the next session writing another broad inventory without calculating anything.

Then implement the crossed parent, other W/G parent families, charged H parents and ST/LSZ terms; finish with physical gauge checks. Commit/push incremental reproducible results to the existing branch. **Only** `WGAMMA_GAUGE_MATCHING_PASS` with complete independent ξ-invariant complex physical dipoles permits release; until then `C_L,C_R=null` is the correct output.
