# Capability and compatibility report

Source baseline: `b1ec52c` on `research/zee-spheno-flavorkit-pilot`.
This is a feasibility investigation, not a complete Zee constraints package.
Status `PASS` below applies only to the specific step described.

## Model and convention audit

**PASS (source audit; not SPheno validation).** The committed ZeeTypeII model
implements the real CP-conserving potential shown in `ZeeTypeII.m`, including
real M12Sq, Mu4, Lambda1–5, LambdaC, K1, K2, K12 and MCS2. Module1's
`scalar_constraints.reconstruct` converts the physical masses and signed
angles into these parameters, and verifies tadpoles and Hessian rotations.
The negative charged basis uses rows `(cb,sb,0)`, `(-sb*cg,cb*cg,sg)`,
`(sb*sg,-cb*sg,cg)`; the Goldstone is first. Rows and physical mass order
must be matched up to allowed eigenstate phases, not assumed equal bytewise.
`D=-sin(beta) Ye+cos(beta) Ye2`, while Fzee is complex antisymmetric.
Both Ye and Ye2 are general complex matrices; quarks have Type-II structure.
The Majorana neutrino uses `Fv -> {vL,conj[vL]}` with no new right-handed
field or tree-level mass operator. For physical vertex signs, fermion order,
conjugations and the one-loop Majorana factor see
[the frozen convention audit](../../validation/module0/CONVENTIONS.md).

**NOT_EVALUATED (complete SPheno matching).** The low-energy prototype solves M112 and
M222 tadpoles and uses `Ye = YeSM vSM/v1 - Ye2 v2/v1`, matching the SARAH
THDM-III pattern. It assumes the charged-lepton mass basis and an SM Yukawa
input with the same orientation and convention as the frozen benchmark. The
actual complex input blocks, antisymmetry, parameter boundary ordering,
running/threshold scheme, and the loop-generated Majorana masses require
checking in generated Fortran and at a physical point. A mismatch must be
investigated rather than silently changing the Lagrangian. No new claim is
made about those assumptions.

## Observable coverage

FlavorKit's published framework provides generic tree and one-loop form
factors and implementations of radiative lepton decay, three-lepton decay,
conversion and several quark-flavor observables ([Porod, Staub, Vicente,
arXiv:1405.1434](https://arxiv.org/abs/1405.1434)). These are generic framework
capabilities, not demonstrated capabilities of this Zee build.

| Target | Status | What remains |
|---|---|---|
| Zee one-loop mu to e gamma | NOT_EVALUATED | Exploratory complex comparison below; derive convention mapping and validate all diagrams. |
| mu to 3e | NOT_EVALUATED | Check tree, photon/Z penguins, boxes and their interference in generated code; compare with the existing tree subset. |
| mu-e conversion | NOT_EVALUATED | Audit photon, scalar, vector and nuclear inputs; match quark conventions and operator normalizations. |
| Quark flavor, including b to s gamma | NOT_EVALUATED | Inspect actual generated operator coverage and perturbative/QCD accuracy; validate against matched calculations. |
| Higgs partial/total widths | NOT_EVALUATED | Check actual channels, thresholds and loop accuracy; no assumption of complete widths. |
| Full two-loop Zee Barr–Zee, including W-gamma | NOT_EVALUATED | Not established by generic FlavorKit's one-loop framework; the existing Module4 itself is incomplete. |

None of these statuses asserts that a contribution is physically zero. A
complete one-loop calculation, if eventually generated, would still not
establish complete Zee phenomenology or the full two-loop dipoles.

## Benchmark and comparison protocol

Candidate: `validation/module12/d12_benchmarks.json`, group 0, central witness
`d7_NO_neutral_near_heavy_07/NO/scale_0.001` (file SHA-256
`f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8`).
It contains the input scalar record, F, D, Ye and Ye2, and individually
stored signed complex contributions. Existing results are partial LFV
quantities and are not evidence of full-model acceptance. The scalar one-loop
dipole group must be compared to the same generated diagrams; its reference
must not be confused with the coherent total, which also contains partial
two-loop terms. Map operator prefactors, chirality, dimensions, external
fermion order, phases and Majorana factors before comparing complex `C_L` and
`C_R`. Compare tree masses/rotations, then charged vertices, then individual
amplitudes and coherent one-loop sums, and only then branching ratios.
Match electroweak inputs, renormalization scale and pole/tree masses; otherwise
numerical differences cannot be interpreted. A Les Houches exporter preserving
both real and imaginary entries and checks of model-generated input readback
are still required.

**Recommendation:** further investigation is justified as a model-specific
one-loop cross-check. Do not integrate into D14 until the convention mapping
is derived, matched amplitudes and coverage are independently validated, and
missing higher orders and scheme dependence are explicitly represented.

## Environment and local execution evidence

- **PASS:** SARAH 4.15.4 loaded and `Start["ZeeTypeII"]` returned with
  `ModelLoaded` true and `AbortStart` false, using the copied frozen model.
  This is initialization only, not a new CheckModel validation.
- **PASS:** GNU Fortran 11.4.0, GNU make and BLAS/LAPACK shared libraries were
  found. The official SPheno 4.0.5 archive compiled its stock executable with
  `make F90=gfortran` (exit 0). Build transcript SHA-256
  `8f1d2fc2fab0f2bb6e0aea36a655e96bb4c98d5c5c29cf912487131f6d7859f6`;
  executable SHA-256 `f238963ee440a24c7541193d65b9684559c60d911c9031976a5709b5391e6cd9`.
  This is not the Zee-specific executable.
- Model file SHA-256: `ZeeTypeII.m`
  `78d6b48232f9a75a21b058301d9233dba3ed067e21f534d27c0d6f415484aa4d`,
  `parameters.m` `499dbcc555dedf5f2cb45a69664812d4e919513500cf6bd91332b9e61b4aba6b`,
  `particles.m` `91b550b69fdcdd3dc409979f6621f1654d57881e36e125e786c2e9ad54c9c6a7`.
- **PASS (generation and reduced build only):** SARAH generated FlavorKit-enabled
  source; generation transcript SHA-256
  `f9dbc64abfed71484dd33d06c9deb4f37d8c48ae159df7c635bb243619c6c4ee`.
  The first full build **FAIL**: generated `Wrapper_LoopDecay_Fe_ZeeTypeII.f90`
  references undeclared `ZRUNoMatrix` and `ZRUNoMatrixc` for Fv final states
  (gfortran `no IMPLICIT type`, build exit 2, transcript SHA-256
  `22551978feab5457d658043592f4aa40569b6f9a7f54cbd8dc7f1298087ec4e8`).
  The generated wrapper assumes a neutrino rotation object not provided in
  this tree-level-massless neutrino packaging; this is an inference from the
  identifiers and model, not a proven SARAH root-cause diagnosis.
  No model field was changed. `IncludeLoopDecays->False` and
  `Include2loopMasses->False`, with FlavorKit enabled and `ReadLists->True`,
  generated again (log SHA-256
  `81cbb397e88e93457613597bed25dc6a8e721ce51351728bdd2f074f38d1ed3d`)
  and **PASS** compiled (log SHA-256
  `6a1a18e71cf3fce014a3e3d519d979bfcb975dbe344fb132dabefd4d692a27f0`).
  This excludes general one-loop decay widths, not the separate FlavorKit
  one-loop flavor routines.
- The `local/` directory contains complete transcripts and generated files
  and is ignored by Git.

The actual preliminary numerical checks, complex coefficients, candidate
convention map and file hashes are in [BENCHMARK.md](BENCHMARK.md).

## Generated-source inspection

**PASS (presence only):** `CalculateGamma2l` contains neutral scalar/lepton
and charged-scalar/neutrino couplings. `Calculate_Lto3Lp` and
`Calculate_MuEconversion` consume K1/K2 and four-fermion coefficients; the
generated LFV file contains tree, scalar/vector penguin and box routines for
four-lepton and lepton-quark operators. The generated spectrum includes LFV
and QFV observable blocks. These observations do not certify all diagrams,
gauge cancellation, nuclear inputs, QCD accuracy or matching. In particular,
no full Zee two-loop Barr–Zee or W-gamma contribution is established. The
reduced build omits SARAH's separate one-loop decay-width package.
