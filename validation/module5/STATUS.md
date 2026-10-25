# Module 5 — Gate A

`LO_MATCHING_ONLY`; `MATCHING_CONVENTION_UNKNOWN` for downstream use.

Completed on branch `feature/zee-bsgamma-module5`, descended from validated
`22d249fb57d55a88b266b69d1575be66ec7209b3`. Frozen model and Modules 0–4
were read only. This delivery covers Gate A, not Gates B/C.

## Actual validation

- Required unittest discovery: **16 passed**, zero failures/errors (11 in
  the original candidate). mpmath 1.3.0 at 90 decimal working digits;
  Python 3.10.12, NumPy 2.2.6.
- Independent parameter-integral oracle: 80 kernel comparisons, maximum
  relative residual **2.651212582804874e-13**, at the upper series switch.
- Additional 4,001-point rational-oracle grid from 0.7 to 1.3: 16,004
  comparisons, maximum relative residual **4.4497738826976274e-13**.
- Candidate falsified at x=1.0442: F8_1 relative error
  **5.823064253007715e-11**, beyond the original 2e-11 target.
  Extended the stable Taylor evaluation through degree 20 over
  `|x-1|<0.25`; regression tests include old failure and switch neighbors.
- Frozen rotation projections reproduce both signed Type-II couplings.
  Tests cover independent state coefficients, degeneracy, interchange,
  decoupling and beta dependence. Complex production inputs are rejected.
- Required example CLI completed, producing ignored
  `local/bsgamma_LO_example.json`:
  `DeltaC7=-0.03708502841033828`, `DeltaC8=-0.04201213114029559`.
  Absolute residuals against independent 90-digit two-state quadrature are
  **6.595838218997492e-19**, **5.3582341466053335e-18**, respectively.
- CLI round-trip and duplicate/nonfinite/extra-field rejection passed.
  `git diff --check` passed. No frozen-module tests were invoked or reclassified.

Reproduce:

```sh
python -m unittest discover -s tests -p 'test_module5_bsgamma_lo.py' -v
python module5/bsgamma_lo.py --input module5/example_bsgamma_input.json --output validation/module5/local/bsgamma_LO_example.json
```

## Source and physics limits

HyperIso v1.0.3 annotated tag
`5a93aca5e28011df3a348954cdc7c7c330ea2169`, peeled commit
`09d26ac6e71d1528922097a896d15693589f636b`: raw release manifest and
relevant matching/kernel/helper/manuscript files were inspected and hashed.
LO algebra agrees under real `lu=Y, ld=-X`. This is source inspection;
there was no checkout/build, runtime version check or R1/R3/R6 execution.
Neither `HYPERISO_REFERENCE_VERIFIED` nor a runtime failure is asserted.

The 2026 unprimed operator structures were read, but full Hamiltonian,
sigma/CKM normalization and native charged-quark amplitude closure remain
uncertified. HyperIso's pinned manuscript itself retains a `Check sign`
editorial marker. The frozen model/rotation check supplies partial evidence;
the existing SARAH audit does not supply charged-quark vertices.

Output explicitly blocks downstream use. **No coefficients were fed into
2026 Eq. (4) or HyperIso.** No `2026_LINEARIZED_SCREEN`, BR, exclusion,
uncertainty combination, or per-state 670 GeV bound was calculated.
The example running top mass is a user assertion, not a mass-scheme fit.
Historical SuperIso NLO context bugs/NNLO differences remain unresolved;
its old baseline is not used as the 2026 SM prediction.

## Next action

Close the charged-quark native vertex-to-dipole normalization and exact
2026/HyperIso convention mapping. Then undertake Gate B's pinned runtime
references and supported two-state/complex injection audit; only after
that mapping undertake Gate C. Details, versions, hashes, residuals and
limitations: `results.json` and `module5/CONVENTIONS.md`.
