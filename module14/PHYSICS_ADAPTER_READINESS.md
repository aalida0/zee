# Physics adapter readiness — 2026-11-06

**WORKFLOW_CODE_READY_PHYSICS_CONDITIONAL**. No new physical exclusion is
validated by this work. The compiler blocker and exporter scaling are
resolved; the remaining scientific limitations below are explicit.
Modules0–13, original model files, historical results and production were
read-only. No parameter proposals, scans, Condor jobs or MG5 runs occurred.

| Stage | Executed outcome |
|---|---|
| `SPHENO_FULL_BUILD_VALIDATED` | Full generated model compiles and all four original D12 cards finish with loop masses/decays enabled. This status validates build/runtime, **not** observable completeness or a production physics adapter. |
| `LFV_SCOPED_ONLY` | Independent complex neutral-fermion/photon subset comparison passes; already present in Module4. No new LFV exclusion. |
| `VACUUM_SCOPED_UNKNOWN` | Ten-field potential/gradient/Hessian checks pass at one saved PASS and one UNKNOWN potential; actual SARAH export has only two neutral fields. No global solver certificate. |
| `HIGGS_PARTIAL` | Both charged eigenstates occur in SPheno's effective diphoton source; numerical predictions fail the same-point/scheme gate for replacement. Existing D13 diagnostics retained. |
| `EXPORT_STREAMING_VALIDATED` | SQLite join/export, original 900-row byte replay, atomic failure/retry checks and bounded-RSS synthetic test pass. |

## A. Actual SARAH/SPheno failure and correction

The original minimal compile was reproduced (exit 1):

```sh
gfortran -c -g -ffree-line-length-none -J. -I ORIGINAL_SPHENO/include Wrapper_LoopDecay_Fe_ZeeTypeII.f90
```

Errors: `Function zrunomatrix / zrunomatrixc has no IMPLICIT type`.
The compiler log is `validation/module14/local/original-minimal-compile.log`;
its exact hash and original wrapper hash are committed in
`physics_adapters/spheno_build_evidence.json`.

This is an absent neutrino rotation in the model combined with an inadequate
SARAH generator guard, **not** declaration ordering or a stale interface.
An original-model Mathematica query returned
`getMixingMatrix[Fv]={NoMatrix,NoMatrix}`, `getMixingMatrixHead[vL]=NoMatrix`.
The generator tests `getMixingMatrix[p]=!={NoMatrix}` (e.g.
SPhenoLoopDecays.m:1009,4017), which returns True for this pair. It therefore
emits nonexistent external-state rotation names.

The isolated correction adds `{{vL},{VL,UV}}` to MatterSector, the neutrino
mixing parameter metadata and VL metadata, and uses `Fv->{VL,conj[VL]}`.
The Lagrangian, physical modes and Majorana nature are unchanged. There is
no manual identity matrix, dummy declaration or removed decay. Regeneration
returns `{UV,UV}` and consistently generates the mass matrix, radiative
self-energies, couplings, UV/ZRUUV declarations and wrapper interfaces.

`zee_d14_prepare_sarah.py` recreates the **exact model bytes used** after
checking pinned SARAH source. Only one corrected model generation and one
actual native compilation were needed; a shell copy-path setup error was
corrected before that build. The original-model query did not regenerate
Fortran. The pristine pinned SPheno archive was extracted in ignored scratch;
no prior research precision patches or compiled libraries were reused.

Validation was eight bounded evaluations of **four existing cards**: each
original physical card once with flags 11/16/55=1/1/1 (full runtime), and once
with 1/0/0 (tree comparison). Appended evaluation flags are the only card
changes; original and effective card hashes are recorded. Each native run
finished in under one second. Full spectra contain finite output values;
the initial iteration's `Infinity` convergence diagnostic is not a final
spectrum value. Model generation and compilation took minutes on this host.

Measured checks and limitations:

- Tree scalar masses agree with the original card within 1.16e-9 relative;
  charged-mixing magnitudes within 4.57e-10. UV unitarity residuals are below
  1.0e-9 at SLHA printing precision. These do not validate neutrino phases.
- D4 H2→H1Z kernel agrees within 2.4e-9 after matching the **native gauge
  coupling**. The unmatched frozen-EW result differs by 3.13%; this is a
  scheme difference, not an uncertainty. Complete D4 totals are not replaced.
- Tree-scheme mu→eγ rates differ from the Module4 scalar-one-loop references
  by 2.1e-5–9.7e-5; tau→eγ by about 0.103%, tau→muγ by about 0.964%.
  Stock kernels, lepton inputs and gauge contributions are not the matched,
  precision-patched complex-component validation in the earlier research
  evidence. No new chirality/phase or gauge/Goldstone completeness claim.
- Full loop masses yield neutrinos up to 5.54 eV versus the original
  approximately 0.01–0.051 eV references. The light scalar becomes about
  302/358 GeV, and full one-loop total widths are enormous
  (about 0.75–1.13 million GeV). These unmatched outputs fail the production
  scheme/perturbative gate. They cannot be interpreted as h125 corrections.
- Mu→3e, tau three-body and conversion outputs are nonzero, but there is no
  independently validated complete scalar/box/penguin interference reference.
  Every such observable remains **UNVALIDATED**. Generated operator presence
  is not a completeness proof.

**Operative SPheno observables: none.** There is no enabled adapter that can
promote these raw numbers to PASS/FAIL, and Module4 remains unchanged.

## B. Corrected public LFV source

The byte-pinned Apache-2.0 source is
[general-2hdm-pheno b5035cd58d2a7e4a91e9790d045df062b97adffe](https://gitlab.com/jbrod/general-2hdm-pheno/-/tree/b5035cd58d2a7e4a91e9790d045df062b97adffe).
The [paper's Eqs.11 and 48](https://arxiv.org/html/2410.17313v3) fix the map:
`rho_l=D/sqrt(2)`, `theta12=beta-alpha`, `theta13=theta23=0`,
`rho_u=(m_u/v)cot(beta)`, `rho_d=-(m_d/v)tan(beta)`, and
`C_L,R=-c_L,R/(8*pi²*v²)`. Neutral vertices have
`q1=(cos(delta),sin(delta),0)`, `q2=(-sin(delta),cos(delta),i)`.
This fixes sign, complex conjugation and chirality, rather than matching BRs
alone. The photon projection of the neutral fermion terms is separately
transverse and contains no charged-scalar or singlet vertices.

`lfv_reference.py` reads only the source-hashed upstream assignments for
neutral top/charm/bottom/tau loops. Setting their external vector-Z coupling
to zero projects photon exchange; no bosonic gauge group is split. At all
four saved D12 cards and all three radiative channels, complex coefficients
agree with independently integrated Module4 kernels within **3.70e-11**
relative, with explicitly matched internal masses. The neutral subset is
unchanged in singlet decoupling; no altered scalar spectrum or parameter
proposal was generated. Inputs are restricted to the four original witnesses.

This is an independent check of an **existing** amplitude subset. Adding it
to Module4 would double-count it. The source's entire 2HDM rate is never
imported. Missing singlet-F, mixed charged, charged-current and complete
bosonic/gauge classes keep `two_loop_full_Zee=UNKNOWN`. No operative exclusion.
Exact inputs, coefficients and residuals: `lfv_reference_evidence.json`.

## C. Vacuum backend

`zee_d14_vacuum_contract.py` checks the full ten canonical real fields,
including charged, CP and singlet components, against the independent
expanded polynomial and tensor Module1 implementations. It uses only saved
`d7_NO_neutral_near_heavy_07` (PASS) and `P2_beta_shift` (UNKNOWN).
Potential/gradient/Hessian scaled residuals are below 3.85e-15; EW gradients
below 1.25e-16 in units of v³. Signed Mu4/K12 terms and all parameters are
retained. Field probes check the same two potentials, not new model points.

The actual `MakeVevacious[Version->"++"]` export succeeds, but its
`FieldVariables` are **phi1,phi2 only**. Its tree potential lacks charged/CP/
singlet directions, Mu4 and singlet portals. Its scalar mass matrices do not
restore those missing minimization variables. This is an executed Zee export
failure of coverage, beyond the stock THDM-example limitation. Export files
and source hashes are recorded with the build evidence; none is vendored.

A ten-gradient system has gauge orbits: EW broken rank 3, generic rank 4,
with singular strata. A square polynomial representation alone is not an
isolated-root exhaustion proof. No complete gauge reduction/LHA map was
validated, so no external minimizer or polynomial solver was run.
`ZEE_VEVACIOUS_ADAPTER_UNVALIDATED`; no new global-vacuum verdict, no
metastability/thermal inference. Numerical non-discovery would remain UNKNOWN.

## D. HiggsTools

HiggsTools 1.1.3 and original experimental datasets are unchanged. Inspection
of generated LoopCouplings confirms the diphoton charged sum runs over
`Hm(2:3)` with each mass and scalar coupling. Tree-spectrum raw h125 diphoton
widths are recorded, but no independent nonzero full-channel/normalization
comparison validates replacing D13. Full-loop runtime changes the spectrum
and produces unusable large widths, as above. No generic 2HDM charged state
is substituted. `HIGGS_REMAINING_UNKNOWN`: validated h125 gamma-gamma/Z-gamma
inputs, complete normalized channels, neutral/H1 production and same-scheme
provenance remain absent. Historical H2 production is retained; no MG5 rerun.

## E. Export and reproducibility

The final CLI uses `join(...,streaming=True)`; legacy join remains available.
Manifest lookup, joined rows, export sorting, duplicate checks and ranks are
SQLite backed. Cache is 2 MiB per connection, temporary sorts stay on disk.
Canonical dataset hashing and JSONL/CSV/benchmark output stream row by row.
Saved-input hashes are checked before and after interpretation. Explicit
production contracts, rank tie ordering and all physics/null labels persist.
No schema bump: `d14-final-family-1` / `d14-final-export-1` are unchanged.

The saved 225-point/900-family export matches **every original file hash and
its audit exactly**, including the original input digest. Frozen join replay
also matches legacy join and reversed shard order. Tests cover missing data,
wrong source, duplicate families, interrupted publication and retry. A sibling
exclusive lock and same-filesystem rename publish only a complete directory.
After SIGKILL, verify no exporter owns the lock before manually removing its
stale `.export-lock` and scratch directory; normal exceptions clean both.

Synthetic repetitions of one saved family (mock IDs only, zero kernel calls):
1,000 rows peak **94,028 KiB**, 6,000 rows **93,872 KiB**, each below **256 MiB**.
This bounds memory in measured cases, not arbitrary single-record sizes.
Disk remains proportional to input/output; set TMPDIR/SQLITE_TMPDIR and allow scratch for manifest/join/
export SQLite stores and the complete output. Plotting and legacy join are
separate memory consumers. `export_streaming_evidence.json` records metrics.

Reproduction commands (existing pinned source/local artifacts only):

```sh
python3 scripts/zee_d14_prepare_sarah.py --sarah PINNED_SARAH --output NEW_SCRATCH
math -script NEW_SCRATCH/generate.m
# Extract SHA-checked SPheno 4.0.5 archive into scratch, copy generated
# EWSB/SPheno to its ZeeTypeII directory, then:
make F90=gfortran Model=ZeeTypeII
# Evaluate only the four original group0..3.in cards, appending the
# evaluation flags recorded above. Keep separate working directories.
python3 scripts/zee_d14_spheno_evidence.py --local SAVED_LOCAL --original-spheno-archive PINNED_ARCHIVE --output NEW_EVIDENCE.json
python3 scripts/zee_d14_lfv_reference.py --source PINNED_2HDM_SOURCE --output NEW_LFV.json
python3 scripts/zee_d14_vacuum_contract.py --output NEW_VACUUM.json
python3 scripts/zee_d14_export_stress.py --rows 6000 --limit-mib 256
python3 scripts/zee_d14_workflow_tests.py
```

Upstream pins/licenses remain in `public_source_lock.json`: SARAH 4.15.4
archive 4ab8f01e… (redistribution license unverified, no copied upstream
source); SPheno 4.0.5 archive 3f84a6c3… (redistribution license unverified in
the inspected archive; no copied upstream source); Vevacious++ 657cf31… GPL-3.0-or-later;
HomotopyContinuation 0cbf1e2… MIT; HiggsTools 1.1.3 GPL-3.0. No upstream source
or binaries are committed. Runtime: Mathematica 15.0.1 Linux x86-64,
gfortran 11.4.0, Python 3.10.12. Full hashes, runtime logs and generated-source
hashes are in the three adapter evidence files; large logs/builds stay ignored.

**Validation:** 74 focused tests passed (five optional historical-artifact
skips); frozen 225-point export replay passed; compile checks and
`git diff --check` passed.

Still missing: calibrated 2026 B→Xsγ NP uncertainty, complete Zee two-loop
LFV and additional validated LFV operators, certified global vacuum coverage,
and complete Higgs constraints. Physical B→Xsγ and global acceptance remain
UNKNOWN/null. The final scan still requires separate explicit approval.
