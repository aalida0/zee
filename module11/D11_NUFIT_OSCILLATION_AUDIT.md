# D11 NuFIT 6.1: blocked at authentic source acquisition

Executed locally on 2026-11-03 on `feature/zee-d11-nufit-oscillation`.
Starting HEAD `a2266ab5ae0a09346f9918b6d804a15d4e64c7ca` has the requested
D10 `4fc4bd32a72432dc915f411d32f3381e96d989c3` as its immediate parent;
the intervening commit changes only AGENTS.md. No history was rewritten.

## Result and mandatory bounded stop

**No authentic NuFIT 6.1 archive could be acquired.** The required
[official release page](https://www.nu-fit.org/?q=node%2F12) and
[release notes](https://www.nu-fit.org/sites/default/files/v61.release-notes.pdf)
timed out through web retrieval. Direct curl, including outside the sandbox,
timed out after 20 seconds for the page and 15 seconds for the notes.
The official hostname without `www` failed DNS resolution (curl exit 6).
Browser retrieval was unavailable because its access host was unavailable.
The legacy release-page URL recorded in frozen Module2 also timed out.

The official page could not be read, so its four download links could not be
followed. No archive URLs were invented. All four expected variant/ordering
entries have null download URLs, sizes and SHA256s in [sources.json](sources.json).
No raw table or PDF was obtained. Normalizations, 22 section metadata, grid
minima and published best-fit comparisons consequently remain **unverified**.

AGENTS.md requires: “If actual official 6.1 grids can't be acquired/interpreted,
STOP rather than creating fake or overconfident fit results.” This stop takes
precedence over proceeding to inverse attempts or creating data-based tests.
No NuFIT 6.0/5.2 substitute, rounded parameter table reconstruction or synthetic
NuFIT result was used. **D11 has no numerical physics result in this run.**

| D10 benchmark (tree vacuum globally certified) | charged masses GeV | NO targets attempted | IO targets attempted | perturbativity fraction |
|---|---:|---:|---:|---|
| d7_NO_neutral_near_heavy_07 | 298.726655, 532.932913 | 0 | 0 | unevaluated |
| F13_heavy_0001330 | 572.231624, 873.207683 | 0 | 0 | unevaluated |

These masses are display values only. All seven D10 canonical input hashes
were recomputed and match the benchmark snapshot and vacuum evidence.
The exact scalar input and reconstructed-Lagrangian hashes, original D10
status categories and per-ordering blocker records are retained in
[d11_nufit.json](../validation/module11/d11_nufit.json).
P2_beta_shift, F13_heavy_0000981 and F13_heavy_0001003 remain vacuum UNKNOWN.
Neither certified representative is asserted to be fully Zee allowed.

## Frozen solver and scope verified by reading

Mandatory Module2/3 interfaces, schemas, validator, witnesses and conventions,
and D10 audit and benchmark snapshot were read. Module2 already supplies the
exact inverse, complete four-complex-parameter homogeneous family, null-cone
construction and finite charged-lepton kernel; no replacement was written.
Its target convention is `M = U.conj() @ diag(m) @ U.conj().T`, with eV
targets and GeV loop inputs. Its forward kernel explicitly multiplies by
`1e9` for GeV to eV. Its full-family relative closure tolerance is `2e-9`.
The frozen Yukawa rotation is `Ye=cos(beta) S-sin(beta) D`,
`Ye2=sin(beta) S+cos(beta) D`, `S=diag(sqrt(2)*ml/v)`; physical F is
antisymmetric with the frozen SARAH normalization.

For future real targets, dm3l means positive dm31 for NO and negative dm32
for IO; native DMA is in units of 1e-3 eV², DMS is log10(dm21/eV²), and
DCP is degrees. The lightest mass and two real Majorana phases must remain
explicit unconstrained nuisance inputs. These are the required conventions,
not an assertion that the unavailable grids were numerically checked.

The supplied release specification describes marginalized 1D/2D projections
and `T23/DMA/DCP`, not an official full six-dimensional likelihood. No
projections were added or reconstructed into a joint likelihood. No ordering
significance, global acceptance, conditional perturbative fraction or LFV
exclusion can be inferred from this blocked run. Wγ remains blocked; missing
two-loop, gauge and non-dipole contributions are not silently included.

## Validation and resume condition

`python3 -m unittest discover -s tests -p 'test_module2_*.py' -v`:
**25 tests PASS**, including frozen exact inverse, NO/IO observables and
archived finite-kernel checks. Existing projection-reader tests use synthetic
grids; their success is not authentic NuFIT validation. No prior snapshot or
module was overwritten. New scientifically falsifying real-data tests and
100–500 bounded target/nuisance proposals are deferred by the mandatory stop.
`git diff --check` passed.

Statuses: `D11_NUFIT_PROJECTIONS_AUTHENTICATED_BLOCKED`,
`D11_INVERSE_NO_BLOCKED`, `D11_INVERSE_IO_BLOCKED`,
`D11_FULL_6D_JOINT_LIKELIHOOD_NOT_AVAILABLE`.
`global_zee_acceptance=null`, `COMPLETE_LFV=false`.
The full-likelihood status records that none was obtained; the inaccessible
site was not independently surveyed for additional unpublished resources.

Resume when the official release page and its four original 6.1 archives are
accessible. Resolve links from that page, archive bytes under ignored
`validation/module11/local/`, and pin URLs/sizes/hashes before any claimed
experimental target or inverse result. This delivery records a source-access
blocker, not completion of the intended D11 physics analysis.
