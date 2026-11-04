# D16 continuation — calculate the missing general-ξ Wγ amplitudes

**Start:** `4221e39d76a3a1886e7aa7ecefdb06fd54e365ae`, branch `research/zee-d16-wgamma-gauge-matching`. D15 `f667635` and Modules 0–14 are frozen.

**Primary goal:** Derive and calculate the missing *actual*, not reconstructed/fitted, W/mixed/ghost/pinch contributions and demonstrate that their gauge variation cancels the known Goldstone-sector variation at the projected complex LFV dipole level. Only then implement validated physical `C_L,C_R`.

## Current facts — do not repeat old work

- 26 labeled inner diagrams were counted and the native source has 58 vertex queries / 444 coefficient checks. Their complete regulated integrals **have not** been evaluated.
- Outer current's B term cancels between both photon attachments at unequal external masses. The C term cancels **for the corrected ξ=1 source coefficient** after the complete off-diagonal h/H sum. These facts alone do not establish general-ξ gauge completion.
- Abe's ξ=1 source A/P/B/C + published P pinch satisfies scoped Ward checks. Its source-A radial integration matches the corrected B.8 transcription. That **does not** independently establish a gauge-invariant physical W contribution.
- `matching.gauge_falsifier()` computes an **incomplete** Goldstone-only mass-shift prescription and its required, not yet derived, compensator. `missing_compensator_relative_to_xi1` is a diagnostic target; **it must not be inserted as the answer**.
- The deliberate `python3 -m research.wgamma_d16.matching --example 1 --require-pass` exit 2 and `C_L,C_R=null` are correct while the contributions are not computed.

## Execution milestone 1: real signed integrands and ξ=1 independent reduction

1. Inspect `STATUS.md`, `inventory.py`, `native_vertices.json`, `evidence.json`, `module4/MATCHING_AUDIT.md`, `symbolic_reductions.py` and `algebra.py`. Associate every enumerated triangle/contact/ghost with an **actual FeynArts diagram**, its native vertex order, charge orientation, relative signs, ghost minus, gauge propagator numerator, seagull and symmetry factor. Do not count generic field combinations as physical without verifying their nonzero native couplings. Keep explicit additional required parent/LSZ/pinch classes.
2. Construct **one common momentum routing** for both external photons (one on-shell, one off-shell) and neutral-scalar momentum, and derive dimensionally regulated `d=4-2ε` one-loop *integrands* directly from native vertices at general ξ. Label momentum, Lorentz indices, charges, gauge factors, and denominators. Include W, charged Goldstone and ghosts and mixed W–Goldstone vertices/contact terms; do not drop longitudinal numerators or divergences before the sum.
3. Before doing the full ξ scan, set ξ=1 **in this independently constructed integrand** and reduce the relevant nonvanishing topology classes to Passarino–Veltman scalar/tensor integrals or equivalent regulated parameter integrals. Report the `1/ε` pole and finite coefficient of each topology or cancellable group, plus the complete A/P/B/C coefficients **before** imposing published relations. Confirm the published Abe ξ=1 expression where the diagram/parent scope matches. This is the first objective experimental milestone and must involve an actual numerical/symbolic integral, not reusing `source_tensors()`.
4. Use spacelike off-shell virtual-photon test points first to avoid threshold/branch ambiguities, with at least two independent scalar masses and complex LFV L/R vertices. Record integration uncertainty and do not use unregulated pointwise quadrature for UV-divergent terms.

## Execution milestone 2: longitudinal/Goldstone/ghost/pinch identity at integrand level

5. Exploit the verified `R_ξ` W propagator identity `D_W^(ξ) = D_W^unitary - i k_μ k_ν/[m_W²(k²-ξm_W²)]`. Derive **native** W–Goldstone/ghost Slavnov–Taylor contractions for the triple, mixed and quartic vertices used. Use the full gauge-fixing/BRST rules appropriate to the SARAH model; an electromagnetic Ward identity alone is insufficient. Treat charged physical H1/H2 mixing parents and on-shell LSZ/irreducible external contributions explicitly, not as presumed zeros.
6. Show which longitudinal terms convert into scalar propagators and which pinch inverse internal/external propagators. Label every resulting parent/contact term and keep source-to-integrand traceability. Contract remaining terms with the **sum of both external photon attachments**, maintaining unequal external masses. Use the native h/H scalar sum rule only after its relevant scalar propagator has actually canceled; do not reuse the ξ=1 C cancellation without proving the general-ξ coefficient condition.
7. Derive and regulate the parent W–lepton, G–lepton, mixed, ghost and pinch contributions as required by these identities. Explicitly show `1/ε` and ξ-pole cancellations in the **full projected amplitude**, not merely separately finite inner subsets. If any required contribution cannot be constructed, preserve the exact missing term and minimal counterexample.

## Execution milestone 3: physical two-loop matching and acceptance

8. Project the complete amplitude (including parents) onto the frozen complex operator of `module4/CONVENTIONS.md`, using D15 crossing proof. Compute independent `C_L^W,C_R^W` at ξ=.5,1,3 at `matching.example(1)` and at least one further independent example with both nonzero complex chiralities. Record per-topology contributions, sum, uncertainty, residuals.
9. Verify, for both chiralities, independently calculated `Delta_ξ(C_W+C_mixed+C_ghost+C_pinch) = -Delta_ξ C_G`, without sourcing the left side from the computed right side or subtracting by construction. Cross-check UV cancellation, photon Ward identities, neutral-scalar mixing/decoupling, scalar rephasing and reverse ordered amplitudes.
10. Compare the *complete* ξ-independent result (where the reference definitions match) to CHK/Ilisie/Abe, including Abe's 2016 erratum; explain *which concrete diagrams/terms* generate their differences. If gauge-independence is not met, do not choose a preferred kernel, modify couplings to force closure or mark `WGAMMA_GAUGE_MATCHING_PASS`.
11. Maintain `physical.C_L=C_R=null` and `coherent_inclusion=false` until all signed diagram and general-ξ gates pass. Once passed, update the interface with explicit provenance and mixed absolute-relative numerical error appropriate for cancellations/zero crossings. Do not add this contribution to D14 in this task.

## Suggested structure and diagnostics

Keep new work within `research/wgamma_d16/` and bulky generated code/logs in ignored `local/`.

- `native_integrands.py` and/or Mathematica/FORM scripts: indexed, source-derived regulated integrands; no hard-coded final physical kernel.
- `tensor_reduction.py` or Mathematica/Package-X/LoopTools equivalent: UV pole + finite PV functions with reproducible prescriptions. If no external package is available, implement/verify a minimal independent regulated reduction; do not substitute the literature final kernel.
- `longitudinal_identities.py`: actual contracted vertex/source and parent term ledger with tests.
- `gauge_ledger.json` compact evidence for each ξ, scalar, chirality, topology: UV pole, finite, integration error, Ward/BRST residual, source hash.
- `D16_GAUGE_DERIVATION.md`: explicit tensor algebra, how pinch parents arise, formula for physical projection, reference comparison. Give exact source files/lines.
- `STATUS.md`: separate `INNER_XI1`, `LONGITUDINAL_ST`, `PARENT_COMPLETION`, `PHYSICAL_GAUGE_INDEPENDENCE` states. Historical B/C and source-A PASS must not be promoted to physical W PASS.

## Specific safeguards

- The computed Goldstone `C_G(ξ)` may itself rely on a defined scalar-loop subset and on model/potential assumptions: verify its trilinears, mixing, ξ mass and charges with the native vertices, instead of assuming the diagnostic defines the entire gauge-dependent G sector.
- A numerical ξ cancellation at a single mass point is necessary but insufficient. Test another scalar spectrum and a different nontrivial complex Yukawa configuration, with ξ both below and above one.
- Finite numerical outputs and 1/ε poles must be consistent; apparent gauge cancellation after dropping UV terms is invalid.
- **Do not** replace a missing graph by zero or by `-Delta C_G`; that would make the acceptance test circular.
- Small new computations first. No new 20k scan, no full regeneration of the already validated D15 one-loop code.
- If blocked, preserve a minimal executable test of the **first nonzero missing topology**, not only the high-level acceptance exit 2. Document exact integrand and why the calculation fails. Continue attempts to resolve it, but never fabricate `PASS`.

## Codex completion contract

Proceed from first actual regulated ξ=1 W/ghost/mixed diagrams → general-ξ longitudinal cancellation → actual two-loop parents → full signed matching. Do not stop merely after rewriting the same status or counting graphs. Commit/push incremental reproducible progress on this same branch. The only valid final physical PASS is independently computed ξ-independent left/right dipoles with proved diagram and renormalization completeness. Otherwise retain `BLOCKED_GAUGE_MATCHING` with a **more specific, executable** blocker.
