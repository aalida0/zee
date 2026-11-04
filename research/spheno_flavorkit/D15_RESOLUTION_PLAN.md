# D15 dipole resolution — executable continuation plan

**Branch:** `research/zee-spheno-dipole-conventions`. **Baseline evidence:** commit `23fa5df7126e532dbb68b2fcd433517f6c92183b`.

This task is **not complete** when four BRs agree, an exploratory log is produced, or a Markdown summary says `NOT_EVALUATED`. Keep investigating and testing in the same working session until every gate below either passes or is demonstrably blocked by an irreducible external dependency. If a gate fails, investigate the cause, make the smallest justified experimental change, rerun, and document both the failed and successful experiments. Never manufacture PASS; record the exact blocker and needed remedy if further work is genuinely impossible.

## Fixed facts — do not reinvent

- The reduced SARAH 4.15.4 + SPheno 4.0.5 FlavorKit backend **builds and runs**; its independent model and conventions are frozen. Avoid the unrelated `ZRUNoMatrix` one-loop-decay wrapper issue.
- D12 uses `L_eff = e*m_i/2 * bar(l_j)*sigma_mu_nu*(C_L P_L + C_R P_R)*l_i F_mu_nu + h.c.`, with metric `+---`, `sigma = i[gamma,gamma]/2`, `e>0`.
- The generated `K2L/R(2,1)` approximately follows `-conj(C_L/R)` at four D12 points. Relative complex residuals range `2.6e-6..4.2e-5`, but **this is a hypothesis, not a convention proof**.
- SPheno uses running masses in the dipole normalization; D12 uses benchmark masses and includes a nonzero daughter-mass phase-space factor. Baseline SPheno `mW=80.348464` vs D12 `80.379` GeV.
- D12's scalar one-loop-only BR is approximately `3.47e-18` at its first witness; its partial two-loop-inclusive LFV BR is approximately `1.39e-10`. These are different calculations and must never be compared as equivalent.
- Inspect `DIPOLE_CONVENTIONS.md`, `D15_VALIDATION.md`, `d15_diagnostic.json`, `compare_dipoles.py`, `module3/CONVENTIONS.md`, and `module4/CONVENTIONS.md` first.

## P0 — source-to-operator trace (the primary blocker)

1. Locate the actual installed `SARAH-4.15.4/FlavorKit/LFV/Operators/Photon*.m`, the `Photon_wrapper.m`, the installed PreSARAH photon operator generation, the generated `LowEnergy_ZeeTypeII.f90`, `FlavorKit_Observables_ZeeTypeII.f90`, and generated `Gamma2l` coefficient source. Record **absolute paths, SARAH source SHA256, and exact line ranges**.
2. Follow `ExternalFields`, `FermionOrderExternal`, `CombinationGenerations`, `Op[6]` / `Op[7]`, and `Pair[ec[3],k[1]]` through FormCalc `DiracChain` and momentum assignment. Establish which flavor is incoming/outgoing for the `(2,1)` array and which operator each projector denotes.
3. Starting with both **all-incoming** generated amplitude and D12's (i \mathcal{L}_{\mathrm{eff}}) vertex, derive the sigma/F tensor replacement including `F_mu_nu` Fourier signs, `i` factors, photon momentum, external spinor crossing, and hermitian conjugation. The derivation must state whether L/R are exchanged, whether the result is conjugated, any (m_i/m_j) factor, and any common sign/phase. There must be **no benchmark-fitted phase**.
4. Implement a tiny independent explicit Dirac-spinor or symbolic test for two *nonzero complex* chirality amplitudes and both incoming/outgoing photon conventions, evaluating the projected matrix element and the D12 operator for the same on-shell kinematics. Include chirality exchange and orientation tests. This must verify the source-derived mapping independently of SPheno BR.

**Useful literature starting point:** FlavorKit/PreSARAH reference Porod–Staub–Vicente (EPJC 74 (2014) 2992) section 5.3 and Appendix B; SARAH FlavorKit advanced-usage wiki. Documentation explicitly describes the `Op[6/7] Pair[ec[3],k[1]]` dipole projector, external fermion ordering, and specialized mass handling. Literature is a guide; only the *installed source version* and actual generated code establish the executable convention.

## P1 — real numerical vertex and input readback

5. Instrument **only ignored generated code** to export all nonzero complex H1/H2–lepton–neutrino chiral vertices for both charge orientations and selected generations, including actual ZEL/ZER and charged ZP rotations. Assert against the frozen Module0/3 complex expressions with a single documented scalar-eigenstate rephasing applied to both vertices. Do not change model couplings to force an identity.
6. Export SPheno's effective `e`, `m_e,m_mu,m_tau` (pole and running), `mW,mZ,v`, scalar mixing, EW scheme and scale. Compare each D12 input, identify which specific input/threshold controls the residual. Check actual complex F/Ye2/Ye at every test point. Report scheme differences explicitly, not just that they exist.
7. Test a same-input/bare-form-factor comparison that bypasses the branching ratio and a parameter-by-parameter sensitivity study (masses, `Alpha_MZ`, `mf_l_mz`, Q, thresholds), without changing the frozen D12 convention. If exact scheme matching is infeasible, derive a justified residual uncertainty envelope from controlled variations.

## P2 — isolate topologies and test physical transformations

8. Instrument charged H1/H2 and neutral h/H/A contributions **separately before the coherent sum** (ideally by generated diagram identifiers/internal-state summands). Check each contribution in the source-derived mapped basis against corresponding Module3 one-loop pieces, with interference and both chiralities. Do not infer per-topology agreement from the final rate.
9. Implement independent null limits (vanishing F, vanishing D, vanishing neutral LFV, zero gamma / singlet mix, decoupling and relevant charged mass degeneracy; note which terms must vanish in each case). Ensure the selected null logically applies to the chosen term, not the full amplitude by assumption.
10. Use complex phase conjugation, nontrivial charged-lepton rephasing, H1/H2 eigenstate row sign flips, and explicitly reverse `mu -> e` and `e -> mu` amplitude labels where supported (do not claim a physical reverse decay for forbidden kinematics). Check the *predicted transformation* of complex coefficients and BR invariance.

## P3 — independent multi-point closure

11. Re-run the four committed D12 witnesses; add genuinely independent phases, masses and gamma values using existing **validated** scalar/Yukawa fixtures. No fitted sign or point-by-point phase. Require both L/R complex coefficients, contribution-by-contribution and coherent one-loop sums to agree to a tolerance derived from numerical precision and measured scheme mismatch, not an arbitrary target.
12. Recompute the BR **from the matched complex coefficients and the same masses/alpha/phase-space factors**, then compare to SPheno's reported rate, separating physics mismatch from normalization/phase-space mismatch.
13. Preserve all source and executable SHA256, cards, provenance, numerical results, null/transformation tests and failure traces under ignored `local/`; commit only compact JSON summaries and focused tests.

## Required end state and decision rules

- `PASS` for operator mapping requires an explicit derivation **and** independent amplitude test; near-perfect rates cannot substitute.
- `PASS` for vertex comparisons requires actual complex numerical generated-vertex readback, not only algebra with assumed identity rotations.
- `PASS` for topology agreement requires per-diagram-group complex comparisons and explained residuals.
- `PASS` for one-loop backend requires all above plus multi-point transformations/null tests, consistent BR reconstruction and justified errors.
- If any gate still fails, continue debugging the failing gate rather than changing it to `NOT_EVALUATED` after one unsuccessful pass. If truly blocked, document an exact reproducer, diagnostic hypothesis, source line and next remedy; **do not claim validation**.
- Leave Modules 0–14 and the frozen Zee SARAH model untouched. No full Zee LFV claims; missing two-loop Barr–Zee/Wgamma remains a separate task.
- Commit and push focused changes on the **same branch** `research/zee-spheno-dipole-conventions`; update `DIPOLE_CONVENTIONS.md` and `D15_VALIDATION.md` with clear gate-level evidence. Do not merge to the D14 production branch.

## Start here

```bash
git status --short
git log -1 --oneline
grep -R -n -E 'OA2lSL|OA2lSR|K2L|K2R|FermionOrderExternal|Pair\[ec' \
  "$HOME/.Mathematica/Applications/SARAH-4.15.4/FlavorKit/LFV" \
  research/spheno_flavorkit/local/SPheno-4.0.5/ZeeTypeII/Observables \
  | head -100
```

If the SARAH installation is in a different path (e.g. `~/.Mathematica/Applications/SARAH`), find it first. Prefer a reproducible output of actual source snippets to reliance on informal assumptions.
