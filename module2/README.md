# Module 2: general Zee neutrino sector

Python API: `from module2 import evaluate` (or `from module2.interface import evaluate`).
The CLI reads one JSON document by default and JSONL with `--jsonl`; `--input` and
`--output` select files. See `input.schema.json`, `output.schema.json`, and
`dataset.schema.json` for the versioned contracts. Complex matrices use paired
`real`/`imag` arrays.

Inputs require an explicit `ordering` (`NO` or `IO`) and scalar record. A scalar
record can be an explicit, versioned Module 0 physical record, a Module 1 v1.0.0
input, or a Module 1 v1.0.0 output. The scalar record is bound by a canonical
SHA256. Module 1 outputs additionally require matching frozen provenance. No
oscillation data are selected implicitly. Optional source-versioned datasets are
tagged `GAUSSIAN_APPROXIMATION`; their chi-square is not an official NuFIT
likelihood and never yields experimental or global Zee acceptance.

The production kernel is the full finite charged-lepton integral, in GeV at the
loop interface and eV in the returned neutrino matrix. `F` is SARAH's physical
antisymmetric coupling; `D=-sin(beta) Ye+cos(beta) Ye2`. Inverse mode returns a
rank diagnostic and the full complex homogeneous Yukawa family. The returned
`Ye2` is unrestricted; LFV is not evaluated.

Run `bash scripts/run_module2_validation.sh` from the repository root. NumPy and
mpmath are required; the validator uses only Python's standard library beyond
those numerical packages and works offline. The runner writes concise tracked
evidence under `validation/module2/` and the detailed local log under the ignored
`validation/module2/local/` directory.
