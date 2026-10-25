# Module 0 validation — 2026-10-25

Mathematica **15.0.1**, SARAH **4.15.4**; branch `isolate/sarah-module0-only`.
The original Zee scalar potential, Type-II quark sector and general complex
Fzee/Ye2 are retained. The sole model correction packages the existing Weyl
neutrino as a self-conjugate Majorana spinor; it adds no field or operator.

| Gate | Status | Evidence / remaining issue |
|---|---|---|
| 1. Load / CheckModel | **PASS** | One diagnostic lists nine missing-term candidates, all explicitly reviewed in [CONVENTIONS.md](CONVENTIONS.md). Complete diagnostics retained; none silenced by adding operators. |
| 2. Scalars | **PASS** | Six independent Hessian comparisons, Goldstones and mixing; 217 cubic/quartic vertices at each of two unrelated points. Maximum vertex residual 1.14e-13. |
| 3. Gauge / Yukawa | **PASS** | Z/photon, 32 W-current comparisons including conjugate momentum orientation, 144 complex Type-II quark chiral comparisons, general complex lepton couplings and rotations. |
| 4. E3 Majorana loop | **PASS** | Actual SARAH full loop generation; independently fixed chiral mass conversion; finite-integral, CP-product, rephasing, Takagi, scale/scheme and eight native null checks. Maximum complex mass residual **2.51e-15 eV**; phase covariance residual 1.52e-14 eV. |
| 5. SPheno / FlavorKit | **BLOCKED** | Model-specific `SPheno.m` absent; no executable or valid source installation identified. Generation, compilation and FlavorKit execution were not attempted. |
| 6. Regression suites | **PASS** | 28 unit tests, 31 independent numerical checks, runnable A1b–f / Gate6 reports and 32-start vacuum search. Failed width-reference and W-ordering comparisons were corrected, derived and rerun. |

Reproduce from the checkout root:

```sh
python3 scripts/zee_sarah_module0.py
```

The runner creates a new UTC evidence directory, routes SARAH output into
this checkout, and records commands, exit codes, source/dependency SHA256,
inputs, residuals and tolerances. [FINAL.json](FINAL.json) maps every final
gate to its immutable trace and records verification of 1,051 artifact hashes.
The full corrected run is `20261025T020907.037566Z`; its two failed audit/test
comparisons are superseded only by `20261025T021551.971703Z`. All other source
hashes agree. Earlier runs are retained, including the original spinor A/B.

Scalar/current tolerances are 1e-7 / 1e-12; physical Majorana closure requires
5e-11 eV absolute and 1e-8 relative. Full benchmark inputs are in archived
`gate6_fixture.m`, `e3_charged_loop_fixture.m`, `module0_native_inputs.m`,
`module0_quark_inputs.m` and `module0_numerics.json`. The two E3 spectra are
(300,700) GeV at gamma=1.089 and (375,925) GeV at gamma=0.71.

These passes concern the stated identities and representative fixtures,
including physical limits. They do not establish a global vacuum, RG closure,
a 309-point archive, complete phenomenological viability, or “full model allowed.”
The old A/B `...PHASE_SIGN_DERIVATION_PENDING` marker describes that diagnostic
alone; the separately executed physical closure resolves it as derived in
[CONVENTIONS.md](CONVENTIONS.md). No work was performed in `~/zee`.
