# D15 — Resolve the off-diagonal crossing bridge (after 95a2e1a)

## Objective and current evidence

**Single open proof:** independently derive the **ordered off-diagonal external-state/Wick-crossing** relation from D12's LFV dipole Lagrangian to the actual PreSARAH/FeynArts projector and installed SPheno `K2L/K2R`. Do **not** finish by postulating the coefficient map and testing its numerical agreement. One-loop backend and D14 integration remain unvalidated until this proof and the outstanding full-card checks pass.

Already completed at commit `95a2e1a401179c71ab89f57bcb0c43a0fa269838`:
- Recovered PreSARAH 1.0.3 + FeynArts 3.9 + FormCalc 7.5 reproduce **44/44** installed `Gamma2l.m` coefficient expressions and **15/15** integral assignments (see `PROJECTOR_REPRODUCTION.md`).
- `projector_toy.m` sends an explicit tensor vertex through the real `CalcAnalyticPenguins2Fermion` coefficient-extraction routine. With arbitrary independent complex chiral coefficients `cl,cr`, the raw wrapped projector gives `{cr,cl}`.
- An additional substitution **`cl -> -Conjugate[cr], cr -> -Conjugate[cl]`** then gives the numerically inferred `K=-conj(C)` relation. That substitution is *not* yet a derivation.
- Independent scalar/pseudoscalar diagonal signed `g-2` confirms `a=-m² Re(K2L+K2R)` in this generated source; diagonal sign alone is not off-diagonal complex crossing proof.
- 492 loop precision cases, 102 direct complex amplitude cases, 36 transformation checks and four original D12 matched-input comparisons have good scoped results. Preserve them; **do not rerun unrelated scans**.

## Minimal reproducible experiment — complete the missing logical step

1. Derive the explicit 3-point vertex from the **original ordered D12 effective action**:
   `L = e*m_i/2 * bar(l_j) sigma^{mu nu}(C_L PL+C_R PR) l_i F_{mu nu} + h.c.`,
   with `sigma=i[gamma,gamma]/2`, `e>0`, metric `+---`. Use two different labeled charged Dirac fields (`i != j`), independent **complex** `C_L,C_R`, and an outgoing photon. Derive the Feynman rule using the functional derivative/Wick contractions, showing all factors of `i`, Fourier signs and fermion ordering. Do this symbolically before substituting any benchmark numbers.
2. Construct the corresponding **disposable FeynArts toy** (or a demonstrably equivalent direct FormCalc amplitude generated from that derived vertex) for the *same* explicit ordered process and its Hermitian conjugate. Distinguish `bar(l_i), l_j` in the projector's external fields from the physical amplitude `l_i^- -> l_j^- gamma`. Keep their masses distinct when extracting chirality/mass-normalization mappings; temporary equal-mass kinematics may be used only for a clearly labeled intermediate test. Do not change the frozen Zee model.
3. Run the toy through the **recovered, already verified** `PreSARAH-1.0.3` coefficient projector with the **same** FeynArts/FORM crossing and polarization conventions used by `Gamma2l.m`. Capture the pre-projection `DiracChain` amplitude, the projected `Op[6]` (`PR`) and `Op[7]` (`PL`) coefficients, and the final wrapper normalization `-1/(2 e m_i)`. The essential new assertion must compare the projected output directly to the coefficient expressions derived in step 1, *without* any manual HC/negative-phase substitution inserted afterward.
4. Run **an independent on-shell explicit-spinor test** for both complex chiral coefficients, noncollinear photon momentum/polarization and both spin choices, comparing the physical ordered amplitude against the exact crossed pre-projection spinor chain. Show the effect of crossing and HC separately. If an external spinor phase remains convention-dependent, fix it from the **same** FeynArts external-state convention using an independently signed QED vector vertex for the same states, not by choosing signs to fit Zee `K2` values. Explain which overall phase is pure convention and which relative sign impacts coherent interference.
5. Test forward and reversed **ordered amplitudes** and their mass-normalization relation. Never claim an on-shell physical `e -> mu gamma` decay. Test conjugation, both chiralities, external field rephasings and negative Fourier sign. Explicitly decide **same-label vs exchanged-label** relation and whether `K=-conj(C)` follows.
6. If direct local FormCalc toy generation requires extra files, work in ignored `local/` using `reproduce_projector.py`'s pinned dependencies. The toolchain has been proven to run; no version-recovery work is needed. On failure, keep the exact failing minimal case and investigate instead of immediately marking blocked.

## After a proven bridge

- Replace the previously hypothesized `K=-conj(C)` assertion with a **source-derived** relation; if a different map emerges, update the *isolated diagnostic tests* and investigate physical disagreement instead of silently changing the frozen Module3 coefficients.
- Re-run source-mapped h/H/A/H1/H2 chiral contributions and coherent one-loop sums, plus the already established physical null/rephasing tests, using their explicitly matched inputs. Confirm the coefficient/rate normalization independent of positive BR matching.
- Validate on at least one **new physical card** beyond the original D12 quartet. Distinguish same-input computational tolerance from actual full-card input/scheme differences.
- Only then give a scoped `ONE_LOOP_COMPLEX_DIPOLE_PASS` with its explicit approximations (massless-neutrino, external-mass-expansion treatment, loop patch, D12 mass scheme), not `COMPLETE_ZEE_LFV_PASS`: missing two-loop contributions remain.

## Deliverables and acceptance gate

- `research/spheno_flavorkit/CROSSING_BRIDGE.md`: complete ordered Wick/LSZ / FeynArts/FormCalc source-to-amplitude derivation with exact file/line anchors and no fitted `-conj` substitution.
- An executable independent toy and spinor regression test; compact recorded source hashes/results.
- Updated `OPERATOR_MATRIX_ELEMENT.md`, `PROJECTOR_REPRODUCTION.md`, and `D15_VALIDATION.md` with corrected non-stale top-level status.
- Commit/push on the **same** branch `research/zee-spheno-dipole-conventions`. No changes to frozen Modules 0–14, no D14 integration, no mass scans.

**Decision rule:** if all direct ordered-amplitude and projector assertions pass, prove the map and proceed to final scoped closure. If a concrete test fails, find the mathematical/source reason, amend only the isolated experiment, and rerun. If still genuinely blocked, show the precise missing step and its minimal reproducer. More unlabelled close rates or repeated overview documents do not satisfy the proof.
