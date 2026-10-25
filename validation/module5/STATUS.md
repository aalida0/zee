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

## Gate A2 — appended native/amplitude audit (2026-10-25)

Branch `feature/zee-bsgamma-native-convention`, exact validated Gate A
ancestor `09e0e6788f2206e767742730a9fe4c9427f1c097`. The evidence above
is retained unchanged. New outcome: **PARTIAL**, with production
`MATCHING_CONVENTION_UNKNOWN` unchanged.

- **A2.1 PASS**: genuine Mathematica 15.0.1 / SARAH 4.15.4 extraction,
  58 original vertices plus three scalar photon vertices. Eight complex
  flavor witnesses compare 952 coefficients, maximum absolute residual
  **8.909917792212513e-16**. Both h.c. channels, CKM phase, Goldstone,
  physical admixtures, quark mass suppression and gauge charges tested.
- **A2.2 PARTIAL**: independent diagram numerator/Gordon reduction and
  signed dipole projection pass under explicit Hamiltonian/sigma/Fourier
  conventions. Twenty on-shell matrix comparisons: maximum norm residual
  **3.08396340716532e-14**. Thirty-two 70-digit diagram/kernel comparisons:
  maximum relative residual **7.49600253313853e-14**. Independent 550/900
  GeV two-state residuals C7/C8: **8.920822600063753e-18** and
  **9.727881400400765e-19**. These are numerical checks, not theory errors.
- **Exact external convention BLOCKED**: the inspected 2026 Letter
  specifies Q7/Q8 but not explicit Hamiltonian/sigma/Fourier conventions;
  the pinned HyperIso files print the Hamiltonian and scalar matching,
  without establishing the executable dipole operator insertion. Its
  editorial marker determines no correction factor. Full external
  normalization is consequently not certified despite conditional LO
  agreement. Required next evidence is an explicit pinned convention
  definition or trusted executable operator/amplitude insertion comparison.
- **A2.3 BLOCKED**: no linear diagnostic, BR, exclusion or per-state bound.
  HyperIso R1/R3/R6 remain **NOT_RUN**, deferred to separate Gate B.
  Source hashes match Gate A; this is not a runtime validation. R1/R6
  use 81 GeV; no conversion into the 160 GeV 2026 formula was attempted.
- Actual tests: **37 passed**, zero failures/errors/skips: structural 3,
  existing LO 16, native/local-operator amplitude 11, independent loop
  projection 7. Frozen model, Modules 0–4 and production LO code unchanged.

Derivation, assumptions, falsifiers and reproduction commands:
`module5/NATIVE_OPERATOR_MATCHING.md`. Small machine-readable evidence,
actual residuals and hashes: `validation/module5/native_matching.json`.
Detailed Mathematica output, source downloads and witness data remain ignored.
No uncertainty covariance, mass-running calibration or NP NLO was computed.

## Gate B — pinned external runtime audit (2026-10-25)

- **B1 `HYPERISO_REFERENCE_PASS`**: clean HyperIso v1.0.3 checkout at
  `09d26ac6e71d1528922097a896d15693589f636b`, freshly built CLI version
  1.0.3. R1/R3/R6 normalized outputs are byte-identical to upstream frozen
  references; official full R1–R7 suite also passes. R1/R6 matching scale
  is 81 GeV. Archived R3 BR(B→Xsγ)=3.2967e−4 is not the 2026 SM baseline.
- **B2 PARTIAL, `MATCHING_CONVENTION_UNKNOWN`**: 18 separate LO executions
  at 160 GeV compare signed one-scalar C7/C8 against frozen γ=0 Zee and
  independent 70-digit diagram integrals. Maximum absolute/relative
  residuals: 9.71445146547012e−17 / 8.814469452255025e−16. Source tracing
  fixes the LO alpha_s factor and plain/effective shift; the external
  sigma/Fourier and full complex CKM/chirality insertion remains unexecuted.
- Generic documented C++ complex matching patches pass an executable API
  test. Dedicated Zee wrapper: `ZEE_TWO_STATE_INJECTION_NOT_AVAILABLE`;
  use a separate minimal adapter after closing the operator gate.
- **33 tests passed**, zero failures/errors; one native tree class skipped
  because historical local numerical evidence is absent. No regeneration
  or branch-guard relabeling. Historical Gate A2 hashed files are unchanged.
- No `EXTERNAL_CONVENTION_PASS`, Zee BR, Eq.(4) screen, exclusion or mass cut.
  Next: trusted pinned O7/O8 operator-insertion audit and restoration of
  hash-verified native evidence. Details/hashes: `module5/HYPERISO_BRIDGE.md`
  and `validation/module5/hyperiso_bridge.json`; detailed logs stay ignored.
