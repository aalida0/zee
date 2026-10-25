# Module 2 validation status

Overall: **PARTIAL**. The neutrino physics, inverse families, observables,
interface, and regression gates pass. The data comparator supports explicit
Gaussian approximations; the official profiled NuFIT projections are not yet
ingested. The runner is
`bash scripts/run_module2_validation.sh`; detailed test output is retained at
`validation/module2/local/validation.log` and ignored by Git.

| Gate | Status | Evidence / limitation |
|---|---|---|
| Full finite one-loop mass | PASS | 80-digit quadrature; archived complex E3 matrices and phases; independent chiral-product check. No native rerun. |
| Inverse complex Yukawa families | PASS | Analytic bilinear null cone; rank 5 and four complex homogeneous directions; NO/IO reconstructions. |
| Takagi observables | PASS | NO/IO, zero and degenerate masses; signed Dirac invariant checks and Majorana undefined cases. |
| Oscillation data | PARTIAL | Source-versioned NuFIT 6.0 IC19 central values and pinned diagonal Gaussian covariances; not an official likelihood, no acceptance classifier. |
| JSON/JSONL and Module 1 | PASS | Strict versioned records, scalar hashes, Module 1 v1 input/output checks, fail-closed errors. |
| Regression and evidence | PASS | Reproducible runner; raw log ignored locally, concise results and hashes tracked. |

NO and IO synthetic physical witnesses close the requested target matrices; this
is algebraic closure, not a claim of experimental acceptance. The fit inputs are
the explicitly selected NuFIT 6.0 (2024), IC19 without SK atmospheric data
parameter table; asymmetric one-sigma errors were symmetrized and correlations
were not supplied, so the stored covariance is explicitly diagonal. The official
NuFIT parameter table is at
[NuFIT 6.0 (2024)](https://www.nu-fit.org/sites/default/files/v60.tbl-parameters.pdf).

The official release also provides machine-readable one-, two-, and
three-dimensional profiled Δχ² projections, but not one joint six-observable
likelihood in the dataset used here. The projections are not combined because
that would invent cross-observable correlations. This comparator pins v6.0 as
an archived source-versioned dataset; NuFIT now lists v6.1 based on November
2025 data as its latest release ([results page](https://www.nu-fit.org/?q=node%2F12)).

The frozen Module 0 SARAH self-energy closure report is a separately labeled
archived reference; native Mathematica/SARAH was not rerun. LFV/Barr-Zee,
SPheno, RG closure, collider/flavor, and global vacuum proof remain outside this
module. See `results.json` and `source_manifest.json` for numerical evidence and
code/source hashes.
