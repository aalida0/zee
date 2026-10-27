# D0 coherent pilot audit — 2026-10-27

**D0_COHERENT_EXECUTION_PASS_NOT_PHYSICAL_ACCEPTANCE.** One real committed NO
input traverses scalar evaluation, inverse neutrinos, scoped LFV, and the 2026
conditional linear flavor diagnostic. This establishes a candidate architecture,
not an accepted point or an allowed/excluded scan. `global_zee_acceptance=null`
and `constraints_complete=false` throughout the pilot output.

Actual compact evidence, source versions, every LFV observable/status, and output
digests are in [pilot.json](../validation/module6/pilot.json). Full CLI output and
logs remain ignored in `validation/module6/local/`.

## Independent review and corrections

The original scaffold checked the scalar hash, but postponed nested Module2
validation until after expensive scalar computation and discarded flavor inputs,
sector provenance, individual LFV statuses, and scalar numerical evidence.
Module6 now validates Module2 and all three benchmark IDs before evaluation,
requires inverse mode and a full `module1_input`, handles invalid/overflow top
types, preserves gate evidence, and verifies actual cross-sector input/output
hashes. Module2 is independently recomputed and its canonical output must equal
the digest of the inverse execution inside frozen Module3.

All four flavor variables are selected exclusively from `scalar_input`'s
validated, SHA-bound physical record. The Module1 evaluated input is rehashed
against that same bound SHA. Derived six-field flavor bytes are hashed and
verified by the frozen Module5 contract; these are generated from the bound
record, not supplied by a second benchmark. Historical contract metadata remains
unchanged; the external convention PASS applies only to C1's retained real,
top-only LO dipoles with ms=0. No C0 patch or HyperIso injection is executed.

The top input is explicitly 163.96892236746697 GeV at 160 GeV. Its source is
`validation/module5/linear_2026.json:matching_mass_provenance`, including the
inherited `QCDHelper::msbar_mass(6,160.,MassType::MSBAR)` record. D0 independently
read and rehashed the referenced LHA bytes at the recorded local path; SHA256 is
`984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374`.
D0 does not rerun mass evolution, remap schemes, or calibrate this reference top
to the paper's 2026 SM input card.

## Actual gates and intermediate values

The committed input is `module3/example.json`, benchmark `module3_NO_spectrum0`.
It binds mH1=300 GeV, mH2=700 GeV, beta=1.394 rad, gamma=1.089 rad;
mh1=125 GeV, mh2=580.7 GeV, ma=633.7 GeV, alpha=1.398 rad, v=246.21965 GeV.

| Calculation/gate | Actual result | Meaning |
|---|---|---|
| Scalar pipeline | SCALAR_PIPELINE_UNKNOWN | No global scalar certification |
| Reconstruction | PASS | Tadpole/v³ 2.339716667824362e-17; mixing residual 1.1641532182693481e-10 GeV² |
| BFB | PASS | STRICT_DOUBLET_AND_NONNEGATIVE_PORTAL, sufficient certificate only |
| 55-state tree unitarity | PASS | max abs eigenvalue 18.136779085730428 < 8π=25.132741228718345 |
| Numerical vacuum | UNKNOWN | VACUUM_NO_DEEPER_WITNESS_FOUND; no global proof |
| Scalar EWPO | PASS | S=0.0044404330206560625, T=-0.0049021783175765745, U=5.733708113025872e-05 |
| Inverse neutrino / forward closure | PASS | Relative residual 3.029000106635716e-15 |
| Neutrino observables | PASS | Algebraic computation; data comparison NOT_EVALUATED |
| LFV provenance, tree, scalar one-loop approximation, Higgs widths, universality subset | PASS | Declared restricted computations only |
| LFV exact one-loop | UNKNOWN | Missing finite-neutrino and external-invariant corrections |
| Full LFV | NOT_EVALUATED | COMPLETE_LFV=false |
| Module4 two-loop terms, including Wgamma completion | NOT_EVALUATED | No Module4 amplitudes included |
| Flavor external convention | PASS within retained C1 scope | Real top-only LO C7/C8, ms=0 |
| Flavor nonlinear reliability | UNKNOWN | No validated coefficient-to-rate curvature |
| LFV/flavor experimental comparisons | NOT_EVALUATED | No pulls, CL or classification |
| Global acceptance | null | constraints_complete=false |

The full vacuum search ran both input seeds (123,104852), with 66+66+18 attempts
per seed: **300 attempts, 294 credible stationary minima, six rejected or
nonconverged attempts, zero boundary hits**. No deeper witness was found;
`all_attempts_converged=false`. The search bound is 12v, not a proof outside it.
The lowest credible depth differs from the EW depth by -3.469446951953614e-17 v⁴,
below the deeper-witness criterion. No evaluation was skipped or promoted to PASS.

The selected inherited scalar-oblique Gfitter Gaussian gives chi²=0.8726172333959237
inside its 3D 95% ellipsoid. This is a scoped scalar EWPO assessment, not full
electroweak or global acceptance; the alternative fit is not combined with it.
A scalar gate FAIL would remain a scalar-gate failure, without a global
exclusion decision. The FAIL/UNKNOWN preservation control explicitly tests this.

Reconstructed Lambda1..5 are
(2.5323266017251225, 0.2523142747149227, 2.6450955022574054,
-1.2105423724307023, -1.1267818464232178); Mu4=943.4001484550731 GeV.
The NO neutrino masses are (0.000999999999999982, 0.008712060605849734,
0.050348783500696395) eV. sin²theta12/13/23=(0.30700000000000227,
0.02195000000000001,0.561), delta=4.199999999999994 rad. These reconstruct
the input target; they do not establish an experimental NuFIT likelihood.
Complex F and D matrices are retained in the evidence.

| Radiative channel | Actual scalar-one-loop subset partial BR |
|---|---:|
| mu -> e gamma | 5.117059759419609e-19 |
| tau -> e gamma | 3.86573009085753e-19 |
| tau -> mu gamma | 1.4030119451446245e-20 |

All 17 LFV observables report computational PASS in their stated scopes, and
all report experimental comparison NOT_EVALUATED. The five three-body channels
are TREE_SUBSET_ONLY; the largest quadrature relative change is
4.214815815314081e-06, below the input 2e-05 tolerance. The nine Higgs results
are partial widths, not Higgs branching fractions. For example,
Gamma(h -> mu tau)=5.516058297239828e-15 GeV and
Gamma(H -> mu tau)=1.60218951393824e-09 GeV.
The universality subset gives delta_GF_mu/GF=4.027628705159165e-08.
None of these is a full LFV rate or experimental acceptance test.

| Signed LO flavor term | H1 contribution | H2 contribution | Sum |
|---|---:|---:|---:|
| DeltaC7 | -0.025081667239615992 | -0.03447187720438246 | -0.05955354444399845 |
| DeltaC8 | -0.02435471088499075 | -0.038644472934599425 | -0.06299918381959017 |

The frozen Eq.(4) diagnostic is
`3.54 - 8.51 DeltaC7 - 2.16 DeltaC8 = 4.182878900268742`, in units 10⁻⁴.
The signed C7/C8 terms are +0.5068006632184268 and +0.13607823705031477;
the conditional shift is +0.6428789002687415. This is an LO-linear conditional
quantity, not a validated physical BR. Flavor classification is UNCLASSIFIED;
no experimental difference, likelihood, pull, CL or mass cut is calculated.
The single-state Type-II 670 GeV bound is never applied to either Zee mass.

## Provenance and tests

Hashes below use sorted compact JSON except explicitly marked byte digests.
The full source manifest contains 45 files and package/code versions.

| Object | SHA256 |
|---|---|
| Module3 input bytes | 6a55f774041a9d5e06bd6ea30a628bfcf5c840af0ddff30bce5f692a551c2915 |
| Module3 canonical input | 8e6d0ac27c439176f89f36c4b5ab55054ef3faf3f36abb4a4d0929675a137981 |
| Bound Module1 canonical input in every sector | 4ee55ddb553124a910ff4fc871a4110cb9ea2c9c24b705d52d6d3f87516e3f15 |
| Module2 canonical input | 0ea9b76e6c5e834bbc7f57bc7e8329a9df9586a1423d1e9cdb8833f235327ad8 |
| Derived flavor input bytes | ee35cec8f55df27a8248d3c9d1fc04c01ce4ce48cf039b21a98c86d63070dd80 |
| Full Module1 output | e4224c2751945a3e9f4f31c69eff8a62140688641c64e6a6f7c76591de9b6063 |
| Full Module2 output | 44c0f7bc1958661334cf12546d37691530ee48d2a4332993e3a1a549869c904d |
| Full Module3 output | 91dd22961cb4e72252e730e77887efc12b157e56af4082c8d26eddacacd62408 |
| Full frozen Module5 diagnostic output | b6fc3600b2871502e9f94c27c77c5a150df3e77a271e10c256432d7e560e4ad8 |
| Final real pilot output bytes | 0a0f21929b4d9d95732f9c38736f02d49fababecb760a162ccb55baf43266247 |

**11 tests PASS, zero failures/errors/skips**: ten structural controls and one
real integration test. The integration test uses transparent capture wrappers
that execute the actual Module1/2/3 functions, including the entire vacuum
search. It independently checks physical input literals, sector canonical input
and output hashes, and a separate 60-digit Decimal rational/log calculation of
the per-state signed C7/C8 and Eq.(4) value. Shared normalization or convention
errors beyond these inherited scopes are not ruled out by this pilot.

Controls reject stale scalar SHA, ID mismatch, invalid nested types, unknown
matching-scale fields, a 170-GeV contract, invalid/overflow top values, sector
hash tampering, and a full-LFV claim. Changing each of mH1/mH2/beta/gamma is
rejected with a stale SHA; recomputing the SHA makes the new bound values feed
the real flavor calculation and change C7. These mutation controls stub scalar
and LFV evaluation and are structural evidence, not additional physical points.
The committed input bytes were independently compared with `git show HEAD:`.

## Reproduce

```bash
mkdir -p validation/module6/local
python -m module6.coherent_pilot \
  --module3-input module3/example.json \
  --mt-MSbar-160 163.96892236746697 \
  --reference-lha-sha256 984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374 \
  --output validation/module6/local/coherent_NO.json
python -m unittest discover -s tests -p 'test_module6_coherent_pilot.py' -v
git diff --check
```

No D0 execution blocker occurred. The required parent is an ancestor of the
working branch; previous tracked Modules0–5, tests and evidence are unchanged.
The nested checkout was already ignored by the parent checkout. No optional IO
witness was added or invented.

## Missing physics and future actual scan

Vacuum global certification, an authentic official NuFIT 6.1 profile source,
complete LFV, Wgamma gauge completion, other missing two-loop and three-body
interference/conversion amplitudes, RG closure, collider processes, a global fit,
physical flavor-rate uncertainty and statistical treatment remain unestablished.
Even Module4's validated fermion/photon and charged-scalar/photon pieces are
NOT_EVALUATED here. The exact missing LFV inventory is retained in `pilot.json`.

A future actual scan should declare a scalar sampler, parameter ranges and
sampling distributions; keep canonical provenance-bound per-point records;
explore NO/IO inverse families with complex Yukawas and homogeneous directions;
apply consistent per-point scalar, neutrino, complete LFV and flavor constraints
and reproducible benchmarks; and compute prompt collider production/decay
observables. Use PASS/FAIL/UNKNOWN for each gate, preserving unresolved results.
An exploratory channel correlation can be documented, but discovery/exclusion
prospects require validated rates, uncertainties, statistical treatment and
collider sensitivity. No broad scan, detector simulation or EPJC novelty claim
is implemented here.

Separately, ask the 2026 B -> Xs gamma authors for their released numerical
coefficient-to-rate response and reproducible input card, including basis,
scheme, matching scale, photon cut, normalization and perturbative order. No
additional nonlinear-rate code should be written without those data; C3's
bounded no-go search is not repeated.
