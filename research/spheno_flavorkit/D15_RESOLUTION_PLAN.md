# D15 dipole resolution — executable continuation plan

## Resolved crossing checkpoint (2026-11-04)

The off-diagonal action/crossing bridge is now executed and proven; see
CROSSING_BRIDGE.md and crossing_bridge_evidence.json. Both original ordered
vertices are differentiated before projection, distinct masses are retained,
source vertex-i factors are counted, and the independent Fock/spinor/QED
comparison passes. The derived forward map is same-label `K=-conj(C)`;
reverse normalization is explicit. The earlier post-projection substitution
has been removed from projector_toy.m.

The original quartet, 102 direct amplitude cases, two new full spectrum cards
and pole-matched variants have passed the scoped amplitude/rate checks.
ONE_LOOP_COMPLEX_DIPOLE_PASS is limited to the patched scalar one-loop subset;
no complete Zee LFV or D14 acceptance/integration is asserted. All earlier
missing-proof statements below are historical, not outstanding work items.

## New executable checkpoint (2026-11-04)

Completed this continuation: authoritative PreSARAH regeneration with a
compatible recovered FeynArts/FormCalc toolchain; 44 symbolic coefficient
and 15 integral-assignment matches to installed Gamma2l; actual-source
analytic tensor extraction; independent generated scalar/pseudoscalar g-2
sign anchor; full eight-ratio-branch experimental C1g/C0C1C2 patch with
stable degeneracy series; 492 positive precision cases; 102 new direct
complex amplitude cases; charged readback closure and controlled scheme
shifts. See PROJECTOR_REPRODUCTION.md and d15_continuation_evidence.json.

**Remaining precise proof obligation:** the raw tensor toy produces {cr,cl}.
Its HC/negative-phase substitution is currently a documented source/anchor
bridge, not an independently executed external-state/Wick-contraction test
of the D12 effective vertex. Do not count the last substitution assertion
as that proof. Resolve this ordering bridge explicitly; then certify the
complex map and promote the already measured amplitude diagnostics within
their scoped approximations. No current missing external dependency prevents
that calculation. Full spectrum-card scheme uncertainty and independent new
physical-card tests also remain distinct from the new vertex-level tests.
Do not repeat archive recovery or the successful precision/component checks.

## Checkpoint d06afa1: concrete next experiment (2026-11-04)

The existing explicit-spinor test verifies on-shell tensor/Gordon reduction, Ward, two Fourier signs, HC L/R exchange, and a **recovered** crossed chain; it does **not** establish the overall phase in the installed SPheno coefficient. FormCalc manual assigns DiracChain `6=P_R, 7=P_L`. Do not repeat the same identity tests and call the mapping validated.

An independent compiled Fortran/high-precision precision test validates the first experimental positive-small-r correction. The *second* unequal-mass branch `C1g(1,1e-11,1e-11)` wrongly returns 0 where the 80-digit reference is approximately 11.9142180118347. A disposable one-guard change worked at that point but has NOT been validated/merged into the scoped experimental patch. The existing near-degenerate `r≈0.999` switch also has observed relative errors 3–4e-8. Preserve the original exact-zero branches; `r→0+` can be logarithmically singular and is not physically continuous with the zero regulator placeholder.

### Task 1 — Reconstruct the projector from an authoritative execution path

**Do not accept a chronology argument alone:** a December 2015 generated `Gamma2l.m` might indeed originate from an older PreSARAH 1.0.3. To identify it, attempt a fresh **user-space** build/use of FeynArts and FormCalc with the recovered official PreSARAH 1.0.3 (pin source hashes). Recreate the PhotonLLp operator output. Compare *canonicalized symbolic coefficient expressions* against the installed `SARAH-4.15.4/FlavorKit/LFV/Operators/Gamma2l.m`; ignore formatting, whitespace, timestamps and harmless symbol names, but do NOT ignore global signs, `I` factors, external mass assignments, `Op[6/7]`, complex conjugations or diagram classes. If a source reproduction is impossible, report the exact dependency failure, not just a missing package.

**Phase fix independent of the Zee benchmark:** use the actual PreSARAH operator extraction on a small analytic test amplitude with two arbitrary nonzero complex coefficients, *known* incoming/outgoing fermion identities and photon Fourier conventions. Either (a) inject an exact known tree-level effective `FFV` dipole test vertex through a tiny disposable FeynArts/PreSARAH toy model, or (b) expose the exact projector coefficient-extraction routine and feed it a precisely normalized analytic FormCalc `DiracChain` corresponding to D12's operator with an explicit crossing. Preserve `iL` amplitude rule and photon creation/annihilation phases. The toy amplitude coefficients must be selected **independently**, not matched to the numerical Zee `K2` output. Check forward/reverse external ordering, L/R, complex phase, global sign and expected (m_i/m_j) factor where applicable.

If an algebraic projector test still leaves a global phase convention ambiguous, find an **independent physical sign anchor** (e.g. independently signed diagonal scalar-induced magnetic moment, generated by the same chain conventions) and show that the same implementation carries the sign into the dipole amplitude. Do NOT infer a complex coefficient convention from a positive BR.

Only after these tests, document a definitive derived `K2_{L/R} <-> C_{L/R}` mapping in `OPERATOR_MATRIX_ELEMENT.md`. If unresolved, preserve proof status `NOT_EVALUATED` and the exact minimal failing projector case.

### Task 2 — Complete loop-function patch correctness

- Extract **all** branch guards for `C1g` and `C0C1C2` in generated FlavorKit code, not just those matched by `patch_small_ratio.py`. Identify every place where a nonzero positive mass ratio can be erroneously classified as zero; don't assume all `eps` comparisons are invalid. Verify each proposed edit against its mathematical limit.
- Extend the experimental patch in ignored generated code to the `m2=m3` branch, *only after* high-precision tests of ratios `1e-30..1e-6`, both sides of 1e-10, and all relevant permutations / exact zero. Include near-degenerate (r\approx1) and cancellation-prone branches. Test both functions separately; distinguish exact-zero regularized behavior from positive logarithmic limit.
- Establish reference formulas (80-digit mpmath or numerical parameter integrals), reproduce before/after values, compile the actual generated Fortran and inspect unchanged regression channels. Keep model and Modules 0–14 untouched; no broad unvalidated replace-all operation.

### Task 3 — Finish one-loop physics closure

Once the projector mapping is independently derived, use source-mapped **separate charged** H1/H2 and **neutral** h/H/A L/R coefficients, with actual generated vertices. Run benchmark-independent new masses/phases and physical null limits, including reverse *amplitude* ordering, and reconcile SPheno vs D12 masses, couplings and scheme differences systematically. Use demonstrated precision and explicitly identified scheme effects to choose tolerances; zero crossings require absolute criteria. Only call the scoped one-loop backend PASS after source-level, algebraic, per-topology and numerical tests all pass.

**Completion discipline:** Keep debugging failures within the same branch, but do not promise an unbounded run, report a missing dependency as an irreducible blocker without attempts to recover it, or mark tests PASS without evidence. Commit small verified results and reproducible errors. No D14 integration or full LFV claim.


## Updated checkpoint: commit adc078a (2026-11-04)

**Do not redo completed checks.** The following are now established for their specified tested scope: genuine small-positive-mass bug isolated to generated FlavorKit `C1g` and `C0C1C2`; after scoped experimental correction, neutral component candidate residuals <=6.9e-11 for the four D12 witnesses with matched generated inputs; generated complex vertices read back, charged-lepton rephase and conjugation checked at a witness; independent H1/H2 charged eigenstate row flips checked at four witnesses; SPheno BR reconstructed to printed precision. The proof of the complex operator mapping, neutral vs charged complete topology closure, multi-point stress/physical null tests and full scheme uncertainty are *still open*. The corrected backend is an experimental generated copy; **do not call it a validated FlavorKit backend**.

### Next Codex execution order — solve, not report

**A. Prove projector-to-operator mapping independently, before further broad numerical scans.**

- Make a new isolated `research/spheno_flavorkit/operator_amplitude_test.py` using explicit gamma matrices, on-shell Dirac spinors, generic independent nonzero complex left/right coefficients and a physical non-collinear photon polarization. Compare the D12 (F_{\mu\nu}) operator matrix element to the **exact projected PreSARAH operator**, first for a declared Fourier convention (A_\mu\propto e^{-iqx}), and independently for the outgoing-created-photon (A_\mu\propto e^{+iqx}). Include momentum conservation, spinor ordering, `sigma=i[gamma,gamma]/2`, `P_L/P_R`, crossing/Hermitian conjugation. Do NOT choose the mapping by fitting any D12 or SPheno numbers. A direct (F\leftrightarrow A,q) algebra is necessary but not sufficient: compare to actual FormCalc/PreSARAH `Op[6/7]` chain, including sign and spinor order. An analytically derived same-label, swapped-label, and/or complex-conjugated mapping must be tested with *both* nonzero chiral coefficients to distinguish alternatives.
- The official PreSARAH 1.0.3 archive is a **recovered source**, not proven identical to the code used to emit the December 2015 installed `Gamma2l.m`. Identify whether source differences affect the projection and compare against the *actual generated Fortran* and installed SARAH wrappers. Exact upstream version identification is useful but not a prerequisite if the resulting projector and crossing can be independently fixed from available compiled/generated expressions. If no exact source is available, explicitly bound what it prevents proving rather than claiming a blanket blocker.
- Produce `OPERATOR_MATRIX_ELEMENT.md` with complete sign, complex conjugation, field order, chirality, and (m_i/m_j) factor (if any) justified by equations and source anchors. Run the independent spinor test against both derived forward and reversed amplitudes. Include all test code and failing derivations in ignored local output; commit only verified derivation and focused tests.

**B. Stress-test the new small-positive-ratio fix independently.**

- In disposable generated code, compare unpatched, patched and high-precision reference `C1g` and `C0C1C2` for positive ratios spanning below, around, and above `r=1e-10`, plus exact `r=0`, the relevant charged-lepton/scalar masses and mass-degeneracy limits. Verify branch continuity and relative/absolute accuracy of both functions. Check for catastrophic cancellation of the original analytic expressions near other thresholds. A function with logarithmic divergence as (r\to0^+) cannot be treated as having a continuous zero-mass value; record the physical vs regulator interpretations separately. Do not blanket-remove every epsilon guard.
- Preserve the original generator library unmodified; document patch SHA256 and generated executable SHA256. Only propose a reusable local override if the high-precision stress tests pass. No changes to frozen Modules 0–14.

**C. Complete the remaining amplitude tests.**

- Obtain complex diagram-class contributions for each of charged H1/H2 and neutral h/H/A, L and R, before summation; compare them with the independent D12 one-loop components after *source-derived* conversion. Use actual generated vertices and propagator masses; reconstruct the coherent sum. Reconcile external masses/scheme through controlled one-at-a-time variations.
- Run independent new physical points beyond the four original D12 witnesses, forward vs reverse field-order amplitude (not unphysical reverse-decay BR), zero-F, zero-D, zero-neutral LFV and applicable decoupling/charged-mixing limits; state which *specific contribution* vanishes in each limit. Test independent complex rephasings and charge-conjugation transformations. Do not derive universal tolerances from the four old points.
- Conclude `PASS` only when A/B/C all pass their scoped criteria. If a specific step is genuinely blocked, report the exact source file/line, failing minimal reproducible test, why available tools cannot resolve it, and the next concrete remedy. Continue debugging failures rather than producing another general partial status report.


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
