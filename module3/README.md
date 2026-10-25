# General Zee charged-lepton LFV ledger, v1.0.0

```bash
bash scripts/run_module3_validation.sh
bash scripts/run_module3_validation.sh --all-tests
python -m module3.interface --input module3/example.json --output /tmp/lfv.json
python -m module3.interface --jsonl --input /tmp/points.jsonl --output /tmp/lfv.jsonl
```

Python: `from module3 import evaluate; result = evaluate(input_record)`.
Requires Python, NumPy and mpmath. SciPy is additionally required by independent
tests and by the frozen Module 1 scalar evaluator. No network is needed for
the numerical validator once the audited Git history and tag are present.

Supply a complete Module 2 v1 input, binding a full Module 1 scalar input or
output by canonical SHA256. Minimal Module 2 explicit scalar records lack
neutral masses/alpha and are rejected. An optional full Module 2 output must
exactly reproduce its input under the pinned frozen code, including complex
mass reconstruction and Ye/Ye2 rotation; mismatched outputs fail closed.
Every mass, phase, scalar parameter, electromagnetic/Fermi normalization,
lepton total width, and integration setting is explicit. JSON complex arrays
use paired real/imag arrays; scalar complex coefficients use numeric
`{"real": ..., "imag": ...}`. JSONL errors are isolated per line; CLI exits 2
if any line fails. Python raises on invalid input. Duplicate keys, nonfinite
numbers, unsupported fields, versions and conventions are rejected.

The ledger separates every neutral and charged-scalar dipole, retaining CL/CR
and exact operator/basis/approximation metadata. The combiner rejects
incompatible contributions. Neutral tree records contain all four chiral
contact Wilson coefficients for both contractions; rates use full scalar
propagators. See [CONVENTIONS.md](CONVENTIONS.md) for derivations, sign
discrepancies against legacy baselines, and the precise validation boundaries.

`PASS` validates a declared calculation. Three-body rates remain
`TREE_SUBSET_ONLY`, radiative rates `SCALAR_ONE_LOOP_APPROXIMATION`, neutral
two-body results partial widths, and universality `SUBSET_DIAGNOSTIC`.
Exact one-loop completeness is UNKNOWN. No experimental LFV limit or global
exclusion is evaluated; `COMPLETE_LFV` is false. Failed quadrature convergence
returns UNKNOWN with the last numerical estimate and its convergence change.
Two-order quadrature comparison is a numerical diagnostic, not a rigorous
interval bound.

The six NO/IO witnesses span three explicit positive-mass spectra with four
arbitrary complex homogeneous-family coefficients, using the current audited
Module 2 solver. They are synthetic physical-mass witnesses, not fits or
scalar-allowed benchmarks. Module 1 gates are retained when an actual scalar
output is supplied. Authentic NuFIT 6.1 archive validation remains pending.

Frozen-file hashes are checked at every evaluation. The validation manifest
also hashes implementation, schemas, constants, test sources, and primary
paper downloads. Downloaded PDFs and detailed logs stay under ignored
`validation/module3/local/`. The primary paper hashes are pinned in
`sources.json`; the runner checks cached PDFs if available. The source
identities and E3 fixtures are available, while the raw SARAH vertex archive
is absent. The overall delivery is scientifically PARTIAL for that missing
cross-check and the explicitly omitted physics.
