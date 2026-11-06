# Final physics freeze — 2026-11-07

**FINAL_PHYSICS_SCOPE_FROZEN_CONDITIONAL**

**CODE_READY / PHYSICS_CONDITIONAL**

**SPHENO_FULL_LOOP_OPERATIVE=NO**

Freeze the existing conditional workflow. The SPheno build is technically
successful; its pole spectra, loop widths and observables derived from them
are **UNAVAILABLE for operative constraints**. No model correction is justified
by the bounded evidence. This investigation made **zero native reruns, zero
model patches and zero new parameter points**. No scan, Condor, MadGraph,
external solver or author contact was performed.

## Saved evidence and reproducibility

The read-only `scripts/zee_d14_spheno_forensics.py` verifies **87 artifacts
before interpretation**: the four original/effective input cards, eight
spectra/log pairs, corrected model, generated source/export files, build and
generation logs, and original D12 benchmark JSON. The first 86 match
`physics_adapters/spheno_build_evidence.json`; the 87th is its pinned D12 input.
All were mounted. Exact hashes, channel inventories, phase space, scalar
overlaps and numerical scheme diagnostics are in
[spheno_forensic_evidence.json](physics_adapters/spheno_forensic_evidence.json).
The reader and existing forward kernel are also hashed there. Original
artifacts were unchanged, under `validation/module14/local/`.

Replay (no backend execution; choose a nonexistent output):

```sh
python3 scripts/zee_d14_spheno_forensics.py --local validation/module14/local --output /tmp/NEW_FORENSICS.json
```

Missing/changed pinned artifacts fail before parsing; use the report's exact
relative artifact names and hashes to restore them on another host. No
third-party source or executable is vendored.

## Width discrepancy: channels located; underlying cause unresolved

Groups 0/1 are saved `d7_NO_neutral_near_heavy_07` NO/IO; groups 2/3 are
`F13_heavy_0001330` NO/IO, all original `scale_0.001` witnesses.
Widths below are **positive printed partial widths**, obtained from total × BR.
`DECAY` and `DECAY1L` in the **same full.spc** share the full spectrum; this
avoids comparing a closed 125-GeV tree channel with an open 302-GeV channel.

| Group | h1 mass (GeV) | Total DECAY1L (GeV) | h1→W−W+ (GeV) | Same-spectrum DECAY h1→W−W+ (GeV) |
|---|---:|---:|---:|---:|
| 0 | 301.939102 | 1127716.740 | 1127708.088 | 6.501314 |
| 1 | 301.939102 | 1127718.350 | 1127709.698 | 6.501314 |
| 2 | 357.958593 | 754293.994 | 754279.414 | 12.170722 |
| 3 | 357.958594 | 754290.068 | 754275.488 | 12.170722 |

The culprit channel is **PDG 25→−24,24**, BR 0.999992328 (0/1) or
0.999980670 (2/3). Width/mass is 3735 or 2107. The two-body dimensionless
phase factor is 0.846809 or 0.893715: these are open channels, far from
threshold. W masses are recorded per channel in the evidence. The tree
polynomial coupling at the printed full parameters is real, approximately
−53.0692 or −52.9034 GeV; changing an eigenvector's overall sign is unphysical.
This coupling alone does not explain the enhancement.

Other anomalous channels (NO/IO differences are retained in JSON):

| Parent/channel | Groups 0/1 partial width (GeV) | Groups 2/3 partial width (GeV) |
|---|---:|---:|
| top→bW+ | 70782.787 | 25382.181 |
| h2→H1−W+ and conjugate, **each** | 19921.585 | Closed/not printed |
| h2→W−W+ | 6170.95 | 39852.84 |
| A→H1−W+ and conjugate, **each** | 20016.50 | 29563.285 |
| H1−→h1W− | Not dominant | 496.5565 |
| H2−→h1W− | 886.1809 | 11399.717 |
| H2−→h2W− | Closed/not printed | 191181.10 |
| H2−→AW− | Closed/not printed | 20800.27 |

Source locations refer to the hash-verified generated directory
`output/ZeeTypeII/EWSB/SPheno/`:

- `LoopDecays/Wrapper_LoopDecay_hh_ZeeTypeII.f90:2567–2665` builds
  tree × (tree + 2 wave + 2 vertex), then adds real photon emission.
  The W−W+ width has generator multiplicity 2 and `helfactor=1`; the
  GammaTPS phase-space denominator is 16πm³ (`Kinematics.f90:15–30`).
  This establishes the implemented expression, not its correctness.
- `LoopDecays/LoopDecayhh_ZeeTypeII.f90:6531–6564` passes the complex
  scalar-vector coupling to `hardphotonSVV`. Complex F/Ye2 real and imaginary
  inputs are retained in the saved spectra; no real-only replacement was made.
- `Settings.f90:29,37–62`: default interference-only widths, on-shell external
  kinematics, external Z factors, MS switch `rMS=1`, IR shifting, regulator
  1e-10 GeV. Saved cards set decay running off and Q=160 GeV. The routine
  separately uses internal running masses and on-shell external masses.
- `BranchingRatios_ZeeTypeII.f90:136–139` defines the total as the **signed
  sum** of the actual channel array. `InputOutput_ZeeTypeII.f90:5089–5300`
  prints only BR > 1e-4. Negative/small channels are therefore not recoverable
  from SLHA. Printed h1 partial sums miss 8.652 or 14.581 GeV of net total.

The source sums channels, but the saved output cannot independently verify
the **complete signed numerical sum**. Wave, vertex, counterterm, real-radiation
and runtime complex amplitudes were not saved. Consequently the precise
enhancement mechanism is **FULL_LOOP_WIDTH_CAUSE_UNRESOLVED**. There is no
demonstrated gauge/IR cancellation failure, factor error or isolated generator
bug. No truncation, regulator change or channel suppression is justified.

## Scalar and radiative-neutrino schemes

**Scalars.** Squared tree/full CP-even overlaps are 0.999935 (0/1) and
0.993013 (2/3) on the diagonal: the light state has not swapped with the heavy
state. Original tree scalar/mixing closure remains at approximately 1e-9.
The full calculation keeps the card quartics as running inputs rather than
performing physical on-shell mass matching. V changes from 246.219650 to
242.813563/242.842709 GeV. `LoopMasses_ZeeTypeII.f90:132–174,212–305`
recomputes EW matching and tadpoles, solving M112/M222; `1204–1386` uses
the tadpole-adjusted matrix minus the self-energy with effective-potential
two-loop terms and iterative pole momenta. This is a different mass scheme
from the tree inversion used to construct the original card.

There is an additional **executed effective-SM overwrite**:
`Boundaries_ZeeTypeII.f90:1606–1624` calls `Get_mh_pole_SM` and replaces
Mhh(1), without a corresponding new ZH. Input flag 67=1 enables this when
Mhh(2)>300 GeV; every full log confirms this path. Thus the reported light
mass is not simply the unmodified full-model one-loop eigenvalue. The saved
files do not contain pre-overwrite masses, individual tadpoles/self-energies
or iteration matrices. The numerical division of the 125→302/358 GeV shift
among these effects remains unresolved. Turning off a flag would not establish
physical matching and is not an independently justified fix.

**Neutrinos.** Both tree source (`TreeLevelMasses_ZeeTypeII.f90:234–397`)
and `OneLoopFv` start with a zero Majorana mass matrix. The leading mass is
radiative, **not a correction to a tree target mass**. `LoopMasses:586–614`
uses −(conj(SigmaSL)+SigmaSR)/2 at p²=0; mass-proportional wave terms vanish
at this order. `854–1024` includes both charged scalar/lepton orientations
with explicit 1/2 factors and the final 1/(16π²) suppression. W/Z terms have
no independent chirality-flipping mass source at zero tree neutrino mass.
No explicit insertion of Module2's target followed by a second addition was
found. The arbitrary massless flavor rotation does not supply such a mass.

The demonstrated major discrepancy is **mixed input schemes**.
`SPheno.m` and `Model_Data_ZeeTypeII.f90:2074–2106` hold complex Ye2 fixed
while replacing Ye with vSM YeSM/vd − vu Ye2/vd. Module2 constructed both
Yukawas using pole charged-lepton masses and its original v. Native running
mass combinations become approximately (0.0004933,0.1020,1.7153) GeV in
groups 0/1, rather than (0.0005110,0.1056584,1.77686).
The small residual D=−sinβ Ye+cosβ Ye2 is sensitive to that subtraction.

Using **only the native complex D and F at the same original scalar/lepton
inputs** in the existing forward formula gives:

| Group | Native-D forward singular values (eV) | Saved full SPheno masses (eV) |
|---|---|---|
| 0 | 0.005225, 0.852281, 0.883066 | 0.005147, 0.839487, 0.869810 |
| 1 | 0.009277, 0.988875, 1.040096 | 0.009138, 0.974031, 1.024483 |
| 2 | 0.002354, 4.709312, 4.739442 | 0.002326, 4.653498, 4.683271 |
| 3 | 0.007073, 5.546711, 5.601706 | 0.006989, 5.480972, 5.535316 |

This accounts for the eV enhancement within 1.53%; it is not a full native
self-energy reconstruction or phase validation. Original targets remain
0.01–0.0511 eV. Saved tree UVMIX is zero, while full UVMIX is unitary at
printing accuracy; tree rotation-dependent predictions need separate care.
Finite-momentum, internal-mass, flavor-basis/conjugation and scheme residuals
have not been completely separated. Restoring a matched radiative input
scheme would require additional validated matching, not overwriting masses
or adjusting Ye2 to fit a target. **Stop: no single demonstrated fix covers
the width, scalar and neutrino failures.**

## Frozen filters and unavailable observables

| Item | Exact operative scope |
|---|---|
| Reconstruction | Positive/ordered physical inputs; tree tadpole/Hessian/mixing closure (relative spectrum ≤1e-7, gradient/v³ ≤1e-9, scaled mixing ≤1e-10). Failure/error prevents evaluation. |
| BFB | Existing sufficient strict-quartic PASS or independently checked negative witness FAIL. No witness/certificate is UNKNOWN, never physical FAIL; current worker requires PASS for family evaluation, so this is a **certificate-selected sample**, not exhaustive BFB coverage. |
| Unitarity | 55-state tree high-energy contact eigenvalues, strict max absolute eigenvalue <8π. No loop/finite-energy unitarity claim. |
| EWPO | Converged scalar one-loop STU inside the selected correlated 95% 3D Gaussian ellipsoid; template selects Gfitter_2026_U_floating. No full electroweak likelihood. |
| Vacuum | D10 sufficient tree certificate PASS only. Certificate miss UNKNOWN **continues** to families. No global solver, tunneling or thermal constraint. Numerical ERROR prevents completion and needs repair. |
| Neutrinos/Yukawas | Module2 radiative forward/inverse closure for sampled NO/IO families, declared NuFIT secondary coordinates and phases; max implemented Yukawa magnitude strictly below configured perturbativity limit (template √4π). No joint oscillation likelihood. |
| LFV | Existing coherent Module4 subset and optional tree μ→3e, PARTIAL/DIAGNOSTIC_ONLY. **No full-model hard LFV veto**: omitted amplitudes may interfere. Independent subset checks do not validate the complete rate. |
| B→Xsγ | Published 2026 linear Eq.(4) LO-NP and optional legacy D9B are separate diagnostics. Physical UNKNOWN, NP theory sigma null, exclusion null. No individual-state 670-GeV bound. |
| h125/HiggsTools | Original approximate D13 diagnostics only. Incomplete normalized channels, charged-loop inputs and neutral/H1 production remain missing. No hard Higgs veto. |
| Full-loop SPheno | UNAVAILABLE for operative pole masses, loop widths, LFV, Higgs or rare-decay vetoes. |
| Cascade/production | Original complete on-shell tree two-body BR inventory; optional source-bound per-family rates with exact energy/process/charge/PDF/order/scale contract. Missing production null, never zero. No loop/off-shell or detector-sensitivity claim. |

`final_config_template.json` was audited and remains unchanged: lfv and
conditional_flavor enabled, optional lfv_tree/bsgamma/higgs disabled;
count/seed/shard size/weights/source commit remain deliberate placeholders.
Stage booleans enable **calculation only**. Exact config/stage/runtime keys
reject unsupported SPheno and hard-veto overrides. Preflight now records a
fixed `PHYSICS_SCOPE`, explicit warnings and immutable diagnostic-only policy;
workers reject a rehashed report that changes this scope. Adverse LFV/Higgs/
flavor diagnostics demonstrably leave conditional cascade ranks unchanged.
Historical export labels/bytes and kernels remain unchanged.

## Paper claims matrix

| Supported | Unsupported |
|---|---|
| Reproducible conditional Zee constraint-and-cascade study with specified inputs and certificate selection | Fully constrained/globally allowed Zee points |
| Coherent implemented partial LFV and independently checked amplitude subset | Complete Zee two-loop LFV or complete rare-decay exclusions |
| D10 sufficient tree vacuum certificates and explicitly unresolved points | Certified exhaustion of all global vacua; metastability/thermal conclusions |
| Conditional published linear B-rate diagnostic | Full-NNLO Zee B→Xsγ 95% CL limit |
| Source-bound LO rate × tree BR benchmarks, energies kept separate | HL-LHC 95% CL expected limit, calibrated detector yield or sensitivity |

## Verification and manual final-run checklist

Focused no-scan suite: **76 tests, zero failures, five optional historical
artifact skips**. It covers source/adapter contracts, frozen forensic replay,
missing evidence, forbidden overrides, preflight tampering, mock orchestration,
failures/retry and deterministic streaming exports. Original 225-point replay:
**225 scalars, 900 families, 16 existing 13-TeV and three 14-TeV rates, 76
production-family bindings**; all five output file hashes and the entire export
audit equal `fixtures/saved_225_export_audit.json`. Raw remote 225-shard
recollection remains NOT_EVALUATED because original triples are unavailable.

Streaming exporter/join/disk-store/stress-script source hashes still equal
the prior memory-tested evidence: 1,000/6,000 synthetic saved-family repetitions
used 94,028/93,872 KiB RSS (<256 MiB), zero physics evaluations. No exporter
rewrite or new stress campaign was needed. Memory bounds apply to these
record sizes; disk remains proportional to input/output. `git diff --check`
and Python compile checks pass. Modules0–13, original cards, model, historical
scan/production files and independent flavor branch are unchanged.

Before a separately authorized final run, an operator must:

1. Obtain the user's separate execution authorization and explicit count,
   seed, shard size and arm weights; pin a clean frozen commit and template.
2. Review this fixed scope, especially certificate-selected BFB, vacuum UNKNOWN,
   partial LFV and unavailable SPheno. Reject unsupported hard-veto flags.
3. Provision exact runtime/package pins and any enabled diagnostic binary/data
   hashes at the actual site; optional stages do not acquire veto authority.
4. Run the no-physics preflight from FINAL_WORKFLOW_RUNBOOK.md on the actual
   filesystem; inspect `physics_scope`, warnings, source/resources and hashes.
5. Reserve SQLite/join/export scratch and complete-output disk space. Follow
   atomic publication and stale-lock recovery rules; never assume a partial
   directory is a valid export.
6. Require complete source-bound receipts and export audits, retain UNKNOWN/null
   labels and separate 13/14-TeV production contracts. No global acceptance claim.

**Recommendation: freeze this conditional scope now.** Remaining scientific
gaps are full-loop width cause and scalar/scheme decomposition, fully matched
radiative-neutrino/backend conventions, complete Zee LFV/rare decays,
calibrated B-rate NP uncertainty, complete Higgs inputs and certified global
vacuum coverage. None blocks the explicitly conditional workflow. No further
backend research or scan is authorized by this freeze.
