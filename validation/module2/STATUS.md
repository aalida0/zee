# Module 2 independent audit

Overall **PARTIAL**: all achievable physics and software regressions pass;
authentic NuFIT 6.1 archive validation remains blocked by network access.
Audited baseline: `b88b13c792f10d0b3a713a43d1362e66bc586a67`.
Complete audit run: 96 tests passed, with zero failures, errors, or skips.

| Gate | Status | Independent evidence |
|---|---|---|
| Full finite Majorana mass | PASS / CONFIRMED | Frozen SARAH pole conversion, both charge orientations, absolute sparse chiral check, full complex archived E3 matrices. |
| Inverse Yukawas | PASS / CONFIRMED | Rank five; analytic D=W^-1(cI+n r.T) spans all four complex homogeneous directions, including isotropic n. |
| Null cone | PASS / CORRECTED | Uses n.T M n; all six charts and extreme overall scales tested; free_x completes identically zero chart polynomials. |
| Takagi and observables | PASS / CORRECTED | Scale-stable congruence and finite diagnostics; independent CP invariant; theta13=0 Majorana phases; NO/IO and massless limits. |
| Experimental data | PARTIAL | Verified NuFIT 6.0 Gaussian snapshots retained; NuFIT 6.1 native profile reader tested on synthetic grids, authentic archive unavailable. |
| Interface / regressions | PASS | Module 1 v1 input/output interoperability, JSON/JSONL, explicit hashes; complete repository suite, no skipped tests. |

**CONFIRMED.** Module 0 defines the pole conversion
`delta M=-(conj(S_SL)+S_SR)/(32 pi²)`; its charged vertices and B0 difference
derive the implemented `sin(2 gamma)/(32 pi²)` coefficient, with SARAH
`F=2 f_Chen`, `D=sqrt(2) Y_Chen`. No factor or sign was fitted. Maximum archived
E3 mass difference is 7.69e-15 eV; the new sparse chiral normalization error is
3.41e-16 relative. The analytic homogeneous-space span residual is 3.74e-15;
the independent mass-matrix J_CP identity differs by less than 3e-16.
The kernel differs from unrounded 85-digit quadrature by at most 5.55e-17
relative; scaled Takagi congruence differs by at most 1.58e-15.

**CORRECTED.** The previous unscaled Frobenius norm could turn finite matrices
of scale 1e-200 into zero masses, or give nonfinite diagnostics at scale 1e200.
Takagi now normalizes first and rejects unrepresentable results. Tests cover
1e-200 through 1e200. The previous electron-row-only Majorana extractor omitted
physical phases at theta13=0; mu/tau row invariants now recover them while
excluding massless-column phases. The zero-target null cone now exposes its
free coordinate. Correlated Gaussian phase comparisons now minimize over 2pi
lifts and reject nonfinite observations. The runner discovers all new tests;
the source manifest also hashes schemas, tests, and the runner.

**Shared-error audit.** Forward/inverse closure and spectrum-only checks can
pass with shared normalization or convention errors. The archived native
complex matrices, sparse source-derived chiral calculation, independent
component inverse equations, analytic kernel span, and mass-matrix CP invariant
provide separate checks. Sign, conjugation, and factor-two mutations are
explicitly rejected. The archived native fixture is a reference, not a new
Mathematica/SARAH execution.

**UNRESOLVED.** The official NuFIT 6.1 release notes describe 22 one-, two-, and
three-dimensional profiled delta-chi-square sections, for IC23 without SK and
IC24 with SK. The new reader verifies caller-supplied archive hashes, native
coordinate transforms, IO signs, complete grids, interpolation and domain
bounds, while preserving offsets. These are single profiled projections;
they are never summed into a manufactured joint likelihood. Source authenticity
is declared by the caller and is not established by a checksum alone. Direct
official-host retrieval timed out (curl exit 28 after 30 seconds, zero bytes);
the hostname without www failed DNS (exit 6). No authentic NuFIT 6.1 archive or
new central-value snapshot was numerically validated.

NuFIT 6.0 IC19 NO/IO means and symmetrized one-sigma errors were checked against
the [official table](https://www.nu-fit.org/sites/default/files/v60.tbl-parameters.pdf).
Their diagonal covariance remains explicitly `GAUSSIAN_APPROXIMATION`, with no
measured correlations, ordering preference, cosmology, or experimental acceptance.
NuFIT 6.1 format provenance is the
[official release notes](https://www.nu-fit.org/sites/default/files/v61.release-notes.pdf)
and [release page](https://www.nu-fit.org/?q=node%2F309).

Reproduce: `bash scripts/run_module2_validation.sh --all-tests`.
Numerics, NO/IO witnesses, exact test count, and code/source hashes are in
`results.json` and `source_manifest.json`; detailed output is ignored locally
at `validation/module2/local/validation.log`. Frozen Modules 0/1 remain unchanged;
both pinned ancestries are verified. LFV/Barr-Zee, SPheno, RG closure,
collider/flavor, and global vacuum proof remain unestablished.
