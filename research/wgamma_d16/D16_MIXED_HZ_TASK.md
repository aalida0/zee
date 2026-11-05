# D16 next computation — mixed charged-scalar Zγ potential class

## Starting point

Branch `research/zee-d16-wgamma-gauge-matching`, commit `18b5f82a1df83208a8dd35c002c767b7693f69f1`.

Read before coding:
- `research/wgamma_d16/GENERIC_2HDM_CLOSURE.md`
- `research/wgamma_d16/HW_NORMALIZATION_AUDIT.md`
- `research/wgamma_d16/ZEE_EXTENSION_INVENTORY.md`
- `research/wgamma_d16/zee_singlet_hz.py`
- `research/wgamma_d16/STATUS.md`
- `module4/CHARGED_SCALAR_AUDIT.md`, `module4/CONVENTIONS.md`
- `research/spheno_flavorkit/CROSSING_BRIDGE.md`

**Already complete:** author-reference HW error identified and independently normalized; generic CP-conserving complex 2HDM coefficients agree on 39 channels; restricted `gamma=0,F=0` pure charged-singlet scalar-Z-photon (`HZ`) class validated with triangles, AZ contact and both outer orders. Do not repeat generic reference scans or reopen D15.

## Central physics objective

Independently calculate and validate the **full physical charged-scalar mixing-dependent, potential-mediated h/H/A–(H1,H2)–Zγ class**, including diagonal and off-diagonal charged transitions and all necessary gauge/Goldstone partners. Keep this isolated from Wγ gauge completion and from the already validated charged-scalar/photon Barr–Zee class. Produce complex `C_L,C_R` for this *specific gauge-complete class only*, not the entire Zee LFV amplitude.

### Why generic mixing is not a diagonal f10 sum

In the physical charged basis, with `d=(cosγ,-sinγ)`, photon current is `Qγ=e I`, but the positive charged-state Z current is

```
T_Z = (d d†/2 - sin²θW I)/(sinθW cosθW)
```

and `G_s` is the *full* neutral scalar/charged pair trilinear matrix from the frozen potential. The loop may contain `G_s[a,b] T_Z[b,a]` for `a≠b`, with **two different charged masses**. The seagull AZ couplings follow the *same* charge-current matrix and must be included; a photon-diagonality argument does not kill mixed trilinears when Z is off-diagonal. At unequal masses, contracting the Z current generates a term proportional to `[M_charged²,T_Z]`, so the simple unmixed (k_Zcdot J_Z=0) proof does not extend. Derive the associated neutral Goldstone `G0 H_a^+ H_b^-` and any reducible/contact ST terms from *native SARAH rules*, not by imposing a guessed mass-difference formula. Distinguish physical h/H and A cases and never assume A mixed contribution is zero just because `G_A,aa=0`.

## Computation order: produce new signed results

**Stage 1: exact mixed vertices and diagram closure**

1. Extract and pin native `Z H_a^- H_b^+`, `A H_a^- H_b^+`, `A Z H_a^- H_b^+`, `h/H/A H_a^- H_b^+`, `G0 H_a^- H_b^+` and any relevant mixed Goldstone or counterterm vertices from SARAH for two genuine nonzero mixing spectra. Determine all momentum, charge, `i`, conjugation and symmetry conventions. Check `T_Z` and `G_s` from *independent* matrix rotations of gauge-basis generators and third derivatives of the frozen potential.
2. Generate a complete set of the two scalar-current orientations, AZ contact, both outer lepton-line attachments, longitudinal-Z and Goldstone partner graphs. Include any seagulls or reducible external terms demanded by the native broken-gauge ST identities. Do not invent fake Z ghost-lepton tree couplings. Inventory real nonzero graphs separately from proved nulls, including A off-diagonal CP-odd possibilities.
3. Verify at the integrand level the real-photon Ward identity and Z/Goldstone ST relation for arbitrary charged masses and complex external L/R, retaining nonzero `[M²,T_Z]`. Use `ξ_Z=0.5,1,3` as an eventual gauge test, but do not promote a partial subset to a physical coefficient.

**Stage 2: mixed-mass master and one numeric nonzero amplitude**

4. Derive the two-distinct-mass scalar-loop tensor and its signed outer Z exchange contribution in the existing external-invariant approximation, including both scalar triangle orientations, AZ contact and both external attachment orders. Use dimensionally regulated PV/Feynman parameters, retaining UV and epsilon terms if poles enter the outer integral. Avoid taking equal masses in the derivation. Define a genuine off-diagonal mixed-mass master and compare its degenerate limit to independently integrated `zee_singlet_hz.hz_radial_kernel` and the corrected 2HDM `f10`.
5. Compute one nonzero, signed complex L/R **off-diagonal** `a≠b` contribution at a model-consistent mixing/potential witness with `F=0` (allow nonzero Mu4). Record `G_ab,T_Zba,M_a,M_b`, numerical integration uncertainty, electromagnetic Ward and longitudinal-Z residual. Keep a clear separate status `MIXED_HZ_TOPOLOGY_ONLY` if full ST cancellation is not yet demonstrated.
6. Include the diagonal pieces in the same mass-basis framework, and derive the basis-covariant trace form when possible. Test charged row sign flips and, in the exactly degenerate charged mass limit, arbitrary unitary basis rotations. Check that the sum is invariant while individual row-decomposed terms need not be.

**Stage 3: full mixed HZ class completion**

7. Supply the missing neutral-Goldstone/longitudinal Z parent and contact terms derived from the actual frozen potential. Verify `ξ_Z` cancellation for both complex chiralities at ≥2 independent, nondegenerate mixed spectra; compare analytic identities and numerical contributions separately. Do **not** infer the missing term by setting it to minus the residual. The completed class should have correct UV/pinch/LSZ accounting.
8. Recover two strict limits: (i) `γ=0,F=0`, portals off -> corrected general-2HDM `HZ` from the validated external adapter, with extra decoupled singlet contribution absent; (ii) `γ=0,F=0`, portals on -> general-2HDM `HZ` + previously validated restricted pure-singlet `HZ`, with proper prevention of double counting. A diagonal-mass degeneracy/charge-basis check is a third independent control.
9. Test (γ	o-γ) with appropriately transformed input and row phases, continuous small-mixing behavior, LFV null limits, scalar portal decoupling, (M_{H2}	o\infty) with bounded couplings, rephasing and reverse ordered dipoles. Include h/H/A individually and coherent complex sums with distinct masses.

## Acceptance, deliverables and boundaries

- Put implementation solely under `research/wgamma_d16/`, e.g. `zee_mixed_hz.py`, `test_zee_mixed_hz.py`, and `MIXED_HZ_DERIVATION.md`; large generated SARAH expressions, logs and integration data under ignored `local/`.
- Preserve pinned corrected author's 2HDM code unmodified and the previous expected-failure for original HW. Never alter frozen Modules 0–14, D15, Zee Lagrangian or D14.
- Record source hashes, exact masses/angles/complex Yukawas, mixing/trilinear matrices, pole/finite and quadrature errors, gauge residuals and complex results. An explicit failing Ward/ST test is useful and must not be hidden.
- Only call `MIXED_ZEE_HZ_CLASS_PASS` when the complete gauge-invariant class, **including** Goldstone/ST terms where required, agrees with both strict limits and passes independent complex/mass/basis tests. If not, retain `BLOCKED_MIXED_Z_HZ` with its exact missing integrand and minimal reproducer, while keeping already proved `UNMIXED_SINGLET_HZ_CLASS_PASS`.
- Even if this class passes, `WGAMMA_GAUGE_MATCHING_PASS`, complete Zee two-loop LFV and global model acceptance **remain open**. Do not set general `matching.py` physical `C_L,C_R` non-null until the full intended complete class is specified and validated; class-only coefficients may live in a separate tagged function.
- Commit/push incremental reproduced progress to existing branch; prioritize a **nonzero mixed-mass master** and full Ward/ST proof over writing another general audit. Do not run a 20k scan or redo 39 common-limit comparisons.

## Immediate success criterion

A new, independently calculated **off-diagonal H1/H2 scalar-Z-photon amplitude** for both complex chiralities, with all native vertex signs and exact diagram partners identified; then gauge-complete it rather than declaring PASS on an incomplete subset.
