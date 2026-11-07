# LFV execution report — 2026-11-07

**LFV_FULL_COVERAGE_BLOCKED.** Completed the bounded source gate and
independent numerical rate controls. No scoped full observable passes;
zero new amplitudes are integrated. This is a precise scientific block,
not a claim that public software cannot eventually support the calculation.

Starting commit: `51f5280e1e537c32bb90492a658f007c94a4dd1c` on
`research/zee-full-constraints`. Frozen parent:
`133a34061723b6bb45b19e8ebe29852ac8b5a9c2`. Read the four task/handoff
documents, Module4 and D14 LFV source/evidence, corrected public 2HDM
source and erratum, saved generated FlavorKit code, and previous Zee pilot
research. B feasibility was not reopened. Higgs was not started.

## What is newly established

1. The **unmodified** SARAH 4.15.4 Lto3Lp observable was compiled as a
   standalone rate subroutine in a disposable directory. Its ten independent
   contact operators (4 scalar, 4 vector, 2 tensor) and three complex mixtures
   agree with a separate four-spinor-density phase-space integration to
   **1.56e-15 relative**. The latter builds the contracted action, antisymmetrizes
   identical negative leptons, averages the parent spin and divides by 2!;
   it does not call or transcribe the analytic rate polynomial.
   Scalar–vector and scalar–tensor interference are nonzero and signed.
2. Its pure-dipole normalization agrees with the independent
   [Kuno–Okada Eq.(123)](https://arxiv.org/html/hep-ph/9909265v1) at
   **4.45e-16 relative**. With the D12 lepton masses/alpha, the leading
   dipole-only mu3e/muγ ratio is **0.00612697641261**. Common-phase covariance,
   single-coefficient conjugation falsification, an incoherent-rate falsifier
   and the source's `V -> V+e² K1` shift were also checked. These last checks
   are algebraic rate properties, not independent model matching of the
   dipole/contact relative sign.
3. For all four original D12 central witnesses, the complex neutral scalar
   contact coefficients give native rates agreeing with independent traces
   within **1.12e-15 relative**. The original massive, finite-propagator tree
   BRs replay **exactly**. Complete original Module2 and Module4 output hashes
   match their saved receipts; scalar, neutrino input and witness hashes are
   retained. No Yukawa fitting or new model point was performed.
4. The existing corrected neutral-fermion/photon reference comparison replays
   **exactly**, all 12 card/channel records, with maximum relative coefficient
   residual **3.70e-11**. It remains REFERENCE_ONLY and already present in
   Module4. Complex Wilson values are retained, not replaced by unsigned BRs.
5. A new source regression executes **unmodified MuEconversion** on a scalar-only
   up-quark EFT insertion. At all six source targets, the scalar nuclear current
   uses exchanged proton/neutron weights relative to the published formula and
   direct `Z*g_p+N*g_n`. For Au the expected/source currents are **910.3/941.5**,
   and source/reference rate is **1.06972357425**. Source literal single-precision
   rounding is retained; a 1e-7 rounding tolerance tests that exchange, not a
   physics uncertainty. The vector isovector sign is different and correctly
   retains the usual proton/neutron assignment. This finding is scoped to the
   pinned source, not every later FlavorKit version.

The rate-functional controls qualify a reusable ingredient. They do not
qualify K1, Z penguin, scalar penguin or box coefficients, do not prove their
Ward/UV cancellations, and do not establish complete Zee branching ratios.
The driver is a validation harness, with no callable Zee exclusion adapter.
The conversion discrepancy is recorded without changing upstream source.

## Numerical evidence on original cards

All entries below are **subset diagnostics**. A partial rate above a bound
does not exclude a card in the presence of unbounded interfering amplitudes.
The dipole diagnostic uses existing Module4 C_L/R alone as the Lto3Lp dipole
input; no tree/dipole combination is presented as a prediction.

| Original scalar / ordering | Massive tree BR(mu3e) | Dipole-only mu3e diagnostic | Dipole-only / tree |
| --- | ---: | ---: | ---: |
| d7_NO_neutral_near_heavy_07 / NO | 1.51072561329e-23 | 8.50045578377e-13 | 5.62673705203e10 |
| d7_NO_neutral_near_heavy_07 / IO | 3.40723740686e-23 | 1.98046617061e-12 | 5.81252767013e10 |
| F13_heavy_0001330 / NO | 8.82316749903e-26 | 1.09384667130e-14 | 1.23974374444e11 |
| F13_heavy_0001330 / IO | 4.77090584636e-25 | 2.54835057278e-14 | 5.34143966543e10 |

The exact tree rates differ from the massless/contact approximation by
−0.07911%, −0.06456%, −0.07770%, −0.07551%, respectively. Those are measured
approximation shifts on these cards, not universal remainder estimates.
The enormous omitted dipole diagnostics prevent a tree-only physical claim.
The normalization is the frozen illustrative D12 snapshot:
alpha=0.0072973525692838015,
Gamma_mu=2.995983701908041e-19 GeV,
Gamma_tau=2.267350867723045e-12 GeV. Nuclear conversion instead requires a
target capture denominator and independently qualified hadronic/nuclear data.

## Source gate and previous work

[LFV_COVERAGE.md](LFV_COVERAGE.md) gives the topology/operator ledger and
source line map. [lfv/sources.json](lfv/sources.json) binds **65** artifacts,
including original cards, frozen source, public code, generated sources and
previous research receipts. The executable verifies them before **and after**
the bounded calculation. No external source is redistributed.

The separate pilot checkout at `81cd376294e223c7311fba134f643db5c02bbad0`
was clean and read-only. Its D15 scalar one-loop complex bridge is useful
but requires the isolated experimental loop-function patch. It does not
qualify the whole generated four-fermion vector. D16 has real partial
integrals and a strict-2HDM HW normalization repair, but still explicitly
blocks the full Zee gauge sum. Its prior generated/altered model cards were
**not rerun**. Archived numerical claims are distinguished in the coverage
ledger from the fresh original-D12 and rate-functional calculations here.

The selected next observable was mu→3e, because its rate and tree machinery
are available. It fails the full-observable gate at independent complex
physical-scheme K1/S/V/T matching and dipole/contact crossing, with enhanced
two-loop dipoles still incomplete. The alternate radiative route fails at
full kinetic W/Goldstone/ghost/BRST/LSZ, charged-current fermion/W, mixed
potential HW and F†F/reducible classes. These are unfinished theoretical
calculations and validation, not a missing package installation. No new
subset calculator or physical PASS/FAIL flag is justified.

## Focused verification and reproduction

```bash
python3 research/full_constraints/lfv/validate.py --output /tmp/NEW_LFV_VALIDATION.json
python3 -m unittest research.full_constraints.lfv.test_validate -v
python3 -m unittest discover -s tests -p 'test_module14_lfv.py' -v
python3 -m unittest discover -s tests -p 'test_module[34]_*.py' -v
git diff --check
```

Use a nonexistent output path: the evidence CLI refuses overwrites. Restore
optional source bytes at the manifest hints on another host, or supply a
manifest with updated **path hints only** and unchanged hashes. Missing or
changed source is an error. Python, NumPy, SciPy and gfortran are needed;
no Mathematica generation, full SPheno execution, MG5 or network is used by
the verifier. Compilation writes modules/binaries only in its temporary directory.

Fresh research suite: **5/5 PASS**; original D14 LFV suite: **2/2 PASS**.
Original Modules3/4 suite: **73/75 PASS**, with the two retained failures
asserting historical branch names `feature/zee-lfv-module3` and
`feature/zee-barrzee-module4`. They fail on this required research branch;
neither test nor branch name was changed or mocked. The new research test
separately verifies this branch, frozen-parent ancestry and byte-identical
protected LFV source. All numerical, phase, mixing-endpoint, Ward/subset,
normalization and receipt checks in those suites passed. The two old branch
assertions are not reported as a clean original-suite pass. Test outcomes
and transcript hashes are in [lfv/TEST_RESULTS.json](lfv/TEST_RESULTS.json).
The accessible frozen SPheno forensic receipt also replays **exactly** after
checking its 87 artifacts, with zero native reruns. This preserves the prior
full-loop-unavailable finding; it does not validate any new observable.

No frozen modules, production records, historical evidence or other checkout
were edited. No scans, new model cards, Condor submissions, MG5 production,
full-loop spectrum runs or author contacts occurred. The final scan remains
unauthorized; B remains blocked and global acceptance remains null.
