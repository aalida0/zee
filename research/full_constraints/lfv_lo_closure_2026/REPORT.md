# Four-card leading LFV closure: incomplete

**Verdict: LFV_LEADING_SCOPE_INCOMPLETE.** The leading scalar-loop plus selected photon Barr–Zee prescription is defensible as a *declared approximation for radiative LFV*, not as a complete LFV constraint prescription for these cards. No benchmark is established to pass or fail the complete physical LFV constraints. A fully constrained cascade scan is not justified. A conditional phenomenology study remains possible with this limitation stated and without labeling points physically allowed; unrelated B, Higgs and vacuum constraints also remain open.

## Executed work

`run.py` checks the frozen D12 archive SHA-256 and each scalar/Yukawa hash and evaluates the four **low_joint** texture cards, not the older central scale cards. It evaluates the h/H/A tree scalar contacts and the mixed-state massless-neutrino F-only charged box using the existing validated source relation, records the stored tree-only rate, and exports the signed complex coefficients. It copies the saved Module3/4 radiative amplitudes without recalculating photon Barr–Zee and includes the previously validated neutral-fermion Zγ coefficient separately for muon decay. No hZ term is promoted: the integrated report explicitly marks it preliminary. The JSON contains baseline plus Zγ partial rates; the matrix consistently compares the baseline-only partial rates with the source-pinned 90% limits. Tau Zγ and other missing groups are not silently set to zero. Radiative numbers are subset diagnostics, not full rates or physical passes.

The tree contacts reuse `module3.tree.wilsons` and `vertices`, whose action/rate normalization was checked in `LFV_SOURCE_TO_CODE_REPORT.md`; those checks do not independently validate this entire new calculation. The F-only coefficient uses Mitsuda–Sasaki, [hep-ph/0103202](https://arxiv.org/abs/hep-ph/0103202), Eqs. 16, 26 and 27, with the native F=2f convention; the prior extraction of the independent generated charged-box block established 28 complex controls with maximum relative discrepancy 3.90e-16 on the old cards and analytic limits. The present calculation applies that checked relation to the four requested cards. The paper Lagrangian PL×PL coefficient is minus the raw generated VLL; the ordered-action bridge to other generated penguins is unvalidated. The F-only box is not the full charged or neutral box.

`current` in `run.py` implements the isolated correction to the FlavorKit equal-density scalar current: `(Z+N)g0 + (Z-N)g1 = Z gp + N gn`, with `g1=(gp-gn)/2`. It accepts complex coefficients. The nonzero scalar/vector interference tests check it against direct proton/neutron contraction and expose the old sign; the isovector and equal-mass/charged-state interchange checks also pass. This is a current-level adapter, **not** a corrected complete FlavorKit conversion program, a KKO overlap/rate implementation, or an independent validation of ultraviolet Zee Wilson coefficients. KKO's general formalism uses separately weighted proton and neutron overlap integrals ([hep-ph/0203110](https://arxiv.org/abs/hep-ph/0203110)); the equal-density contraction cannot replace those overlaps. Existing independent FlexibleSUSY/source-current comparisons and their target-input caveats are documented in `LFV_SOURCE_TO_CODE_REPORT.md`.

## Numerical scope and experimental sources

`NUMERICAL.json` provides complex radiative, scalar-tree and F-box components and hashes; `CONSTRAINT_MATRIX.csv` has all 20 card/process rows. For D7 NO/IO and F13 NO/IO, respectively, the saved μ→eγ partial branching fractions are 1.5613e-19, 1.0857e-18, 4.0313e-20 and 1.3379e-19. All saved radiative subsets are below the selected limits; uncomputed amplitudes can interfere and have not been bounded, so this is not an exclusion or a physical pass.

Observed source-specific comparisons, not an exhaustive current-limit combination: MEG II 2021–22 [μ→eγ < 1.5e-13](https://arxiv.org/abs/2504.15711v2); SINDRUM [μ→3e < 1e-12](https://doi.org/10.1016/0550-3213(88)90462-2); Belle [τ→eγ < 5.6e-8 and τ→μγ < 4.2e-8](https://arxiv.org/abs/2103.12994v2), all 90% CL. SINDRUM-II's [7e-13 conversion bound](https://doi.org/10.1140/epjc/s2006-02582-x) is on **gold**, not aluminium, so it is not applied to an Al rate. Projected Al sensitivity is not an observed bound. Mu3e's reported denominator is the ordinary muon-decay width; radiative stored rates use the frozen total-lepton-width normalization.

## What prevents closure

- μ→3e: source-matched complex off-shell photon monopole K1L/R, low-q² Z penguins, neutral and mixed D/F box vectors, their common ordered-action phases with K2 and scalar terms, and the full identical-particle rate remain unvalidated. The stored tree-only rate and F-box are not total-rate bounds because interference can be destructive.
- Conversion: matched complex K1L/R, low-q² Z and semileptonic scalar/vector box coefficients for the Type-II quark sector, heavy-quark/gluon threshold matching, QCD/QED evolution, and the common signed convention for dipole and nucleon currents are absent. Therefore no KKO aluminium nuclear rate, uncertainty, or gold-limit comparison is defensible. Current tests establish only the stated algebraic sign correction.
- Radiative channels: charged-current and bosonic electroweak gauge aggregates and potentially enhanced new mixed-F structures remain unmatched; standard extra-loop dressing of the existing F†F invariant is beyond the declared leading prescription, but that observation is not a numerical bound on other missing invariants. Tau rates lack the separately checked muon Zγ group.
- No numerical theory, running, nuclear, or missing-amplitude uncertainty is asserted. Partial-rate comparisons cannot establish that any unknown coherent total lies below an experimental bound.

## Reproduction

From the repository root:

```
python3 research/full_constraints/lfv_lo_closure_2026/run.py
PYTHONPATH=.:research/full_constraints/lfv_lo_closure_2026 python3 -m unittest research/full_constraints/lfv_lo_closure_2026/test_closure.py -v
```

Three tests passed. These are algebraic and invariance checks, not independent full operator validations. Prior reported external/source comparisons are identified above and were not rerun. Frozen modules and evidence were read only; no new points, scans, Git operations or two-loop tensor calculations were performed.
