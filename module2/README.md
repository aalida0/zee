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

Use `bash scripts/run_module2_validation.sh --all-tests` for the complete
repository regression suite. The runner discovers every `test_module2_*.py`
file; new audit tests cannot be silently omitted.

The Takagi convention is `U.T @ M @ U = diag(m)` and
`M = U.conj() @ diag(m) @ U.conj().T`. NO labels masses in increasing order;
IO labels the middle, largest, and smallest singular values as m1, m2, m3.
`dm3l_eV2` is dm31 for NO and dm32 for IO. PMNS phases use
`U = V(delta) diag(1, exp(i alpha21/2), exp(i alpha31/2))` modulo charged-lepton
row phases and Majorana column signs. A massless column has no assigned
Majorana phase. Degenerate spectra give UNKNOWN mixing; a vanishing reactor
angle leaves delta undefined while mu/tau row invariants can still determine
physical Majorana phase differences. Extremely ill-conditioned phases and
unresolvable cancellation in zero-target families fail with UNKNOWN.

For fixed nonzero F with `F n=0` and nonvanishing diagonal loop weights W,
the complete homogeneous family is `D = W^-1 (c I + n r.T)`: one complex c
and three complex components of r. This establishes nullity four and rank five
even when `n.T @ n=0`. In an identically zero null-cone chart, optional complex
`free_x` specifies the extra projective coordinate; otherwise it is rejected.

NuFIT 6.0 and 6.1 native profiled tables are supported as a separate dataset
variant (`profile.schema.json`). A dataset declares `likelihood` as
`PROFILED_DELTA_CHI2`, a single `section` (for example `T23/DMA/DCP`), source
version/selection/ordering, and an `archive` containing local `path` and exact
file `sha256`. The archive may be XZ-compressed or plain text. Native DMS is
log10(dm21/eV²), DMA is dm3l/(10^-3 eV²), and DCP is in degrees. Interpolation
uses the original Cartesian axes, preserves the published chi-square offset,
and gives UNKNOWN outside the grid. No projections or Gaussian terms are
added together. A checksum binds the caller's file; source authenticity remains
declared by the caller. The Gaussian option remains `GAUSSIAN_APPROXIMATION`;
phase correlations, if supplied, are profiled over integer 2pi lifts.

NuFIT 6.1 format metadata was checked against its
[official release notes](https://www.nu-fit.org/sites/default/files/v61.release-notes.pdf).
Direct official archive retrieval timed out in the audit environment, so the
reader's numerical tests use explicitly synthetic grids. No NuFIT 6.1 central
values or authentic archive closure are fabricated; the packaged Gaussian
snapshots remain the verified NuFIT 6.0 IC19 inputs.
