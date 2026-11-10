# Full-source Zee Type-II LFV continuation — 10 November 2026

**Scientific verdict: SOURCE_GROUP_EXECUTED__PHYSICAL_LFV_UNKNOWN.**

This bounded execution uses the three original SHA-locked user-provided generated Fortran files. It does **not** modify the source, run a scan, or assert physical exclusions. Four exact D7/F13 low-joint lepton Yukawa matrices and scalar inputs are used; quark masses and complex unitary CKM are *illustrative* rather than matched precision inputs.

## Original generated routines now compiled and run

**Semileptonic (10):** CalculateTreeS2L2u/d, CalculateTreeV2L2u/d, CalculatePengV2L2u/d, CalculatePengS2L2u/d, CalculateBox2L2u/d. Every group evaluated for all four cards. The tree and boxes are source-scale independent. The vector penguins pass a 32-component complex comparison to independently computed native up/down quark Z gauge-current factorization at <3e-11 relative and are stable under Q: mZ to 1 TeV. The scalar penguins exhibit a **large relative** Q dependence, therefore are **not** certified renormalized observables.

**Direct/cross tree four-lepton (4):** CalculateTreeS4L, CalculateTreeS4Lcross, CalculateTreeV4L, CalculateTreeV4Lcross. All four cards evaluated. Direct and crossed vector-tree coefficients vanish. Original crossed scalar-tree source **is not equal** to the direct group; the Fierz mapping was explicitly validated in all complex cards:
- SLL and SRR crossed = 0.5 times their direct source;
- SLR and SRL crossed = their direct source;
- crossed VRL = -0.5 * direct SRL; crossed VLR = -0.5 * direct SLR;
- crossed TLL and TRR = 0.125 times their corresponding direct SLL and SRR.

These relations are source-level crossing/fierz **checks**, not a complete gauge-invariant identical-electron mu3e amplitude proof.

## Numerical materiality, four frozen cards

| Card | Illustrative light-quark scalar norm / Z-only Al amplitude (Gs=100 stress) | Max absolute scalar source Q shift / largest direct four-lepton Z coefficient | Heuristic contact-only mu3e norm-to-BR stress |
| --- | ---: | ---: | ---: |
| D7 NO | 5.212e-3 | 2.662e-6 | 1.073e-18 |
| D7 IO | 7.836e-3 | 4.939e-6 | 3.888e-18 |
| F13 NO | 5.308e-6 | 7.227e-9 | 2.408e-16 |
| F13 IO | 7.772e-6 | 8.853e-9 | 7.270e-16 |

The scalar-nucleon assumption |Gs|<=100 is an **illustrative input, not a sourced uncertainty bound**. The contact-only amplitude-norm stress uses a large arbitrary phase-space/spin prefactor 15000/GF² and *does not include the nonlocal dipole, finite-q2 photon, missing higher-order diagrams or source-convention uncertainty*. **It is not a physical branching ratio or a rigorous bound on physical mu3e**. No experimental allowed/excluded decision follows.

The scalar penguin scale instability is small in absolute size compared with the generated Z coefficient **in these saved cards**. This is a materiality observation, *not a renormalization proof*. Large cancellations in the full amplitude, mismatched chiral normalization and heavy-quark/gluon contributions can invalidate a bound inferred from this comparison.

## Reproducible tests and delivery

- New 10 semileptonic-group and four tree-group sources compile and execute in temporary original-Fortran drivers.
- New independent source package: **9/9 tests PASS** (complex unitary CKM mass diagonalization, 32 direct Z gauge-current matches, all operator groups, scalar scheme guards, tree Fierz, source scale behavior, missing-is-null, local normalization stress arithmetic, B0/B1 controls).
- The previous source package's **9/9 tests PASS**.
- Clean unpack/replay in an independent temporary directory: **PASS**, including new gfortran compilation/execution of original Type-II TreeS2L2u/d and all four Tree4L groups.
- The user-facing ZIP is `zee_lfv_typeii_semileptonic_closure_update_2026-11-10.zip`, containing portable Python source extractors, all per-card complex source Wilson results, tests, SHA manifest, prior source-group dependencies and README. The user's original generated Fortran is **not** redistributed or pushed to Github.
- Machine-readable small summary committed in `NATIVE_TYPEII_SEMILEPTONIC_AND_TREE4L_SOURCE_GATE_2026-11-10.json`.

## Physical requirements still preventing closure

1. **mu3e:** source K1 at q²=0, dipole K2, 4L S/V/T operators and direct/crossed Fierz terms must be assembled into a *single independently validated signed on-shell mu3e amplitude*, with finite-invariant error and identical-electron antisymmetrization. The generated original operator groups do not themselves certify this.
2. **Scalar-penguin source scheme:** counterterm/renormalization verification or a documented, independently justified perturbative omission/error prescription remains necessary for physical rates.
3. **mu-e conversion:** original Type-II u/d one-loop operator groups run, but complete heavy quark/gluon matching, running, precision CKM/quark masses, proton/neutron scalar response, and signed interference with dipole/photon/Z are NOT validated.
4. **Radiative LFV:** previously identified potentially relevant mixed-F/D electroweak and gauge two-loop contributions are not bounded by this one-loop study.

**Accordingly:** physical_mu3e_BR = null, physical_Al_rate = null, global_acceptance = null, physical_lfv = UNKNOWN. No parameter scan filtering and no physical pass/fail.

**Practical scientific recommendation:** For an honest publishable cascade scan, either obtain specialist validation of the common LFV LEFT action and required higher-order amplitudes, or explicitly present LFV as unassessed/conditional and avoid claiming the benchmarks satisfy *all* constraints. More source-code execution alone cannot resolve a missing operator-convention proof.
