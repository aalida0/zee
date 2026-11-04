# D15 diagnostic: four committed D12 inputs

**Final validation status: NOT_EVALUATED.** Four reduced SPheno executions
completed, but the complex operator map is not analytically established,
the input schemes are unmatched, vertex arrays have not been checked
numerically, and individual charged/neutral contributions and null limits
have not been measured. FlavorKit is not yet a validated one-loop LFV
reference. Nothing here establishes complete Zee LFV constraints.

Run `python3 research/spheno_flavorkit/compare_dipoles.py` after generating,
building and instrumenting the reduced backend as in [README](README.md).
The script requires exactly one instrumented output per chirality, errors on
missing results, uses four central committed D12 witnesses, and records
SHA-256 for input dataset, executable, template, each card, log and spectrum.
The committed [JSON](d15_diagnostic.json) contains all complex coefficients,
residuals and provenance. Generated files remain ignored. Group 0 reproduces
the original card and instrumented log hashes; the printed spectrum may
contain run-dependent metadata. Groups 0/1 and 2/3 use NO/IO respectively,
with two scalar spectra and independently supplied complex Yukawas.

| Group | candidate relative residual L | R | SPheno BR / D12 scalar BR |
|---|---:|---:|---:|
| 0 | 2.018959e-5 | 2.453408e-5 | 1.000020983 |
| 1 | 4.153292e-5 | 2.593449e-5 | 1.000022829 |
| 2 | 2.593179e-6 | 1.362634e-5 | 1.000097054 |
| 3 | 6.949487e-6 | 1.100781e-5 | 1.000075694 |

Residual is `abs(K2+conj(C))/abs(C)` and is **only a candidate diagnostic**.
The four rates include the common scalar one-loop subset only on the D12
side, not its partial two-loop terms. No acceptance tolerance can be
scientifically justified until conventions, actual vertices and matching
uncertainties are resolved; in particular the original 2e-5 is not a
universal tolerance. Neither residuals nor rates certify the sign.

## Input and perturbative scheme audit

D12 records `v=246.21965`, `mZ=91.1876`, `mW=80.379` and an on-shell
`g2=2mW/v` scheme. Its charged-lepton masses are pole snapshots
`(0.00051099895,0.1056583755,1.77686)` GeV; see
`validation/module12/d12_benchmarks.json` `SM_decay_card`. The card exporter
sets GF from v and sets mZ and tau, but leaves SPheno electron and muon
inputs at its defaults (0.00051099893 and 0.1056583715 GeV in
`src/StandardModel.f90:684-686`). SPheno uses `mf_l_mz` in K2 normalization
and running SM Yukawas (`RunSM_ZeeTypeII.f90:134-153`), whereas the
observable uses pole `mf_l` and alpha(0). D12 uses the frozen scalar-one-loop
inputs and includes the nonzero daughter phase-space factor. The ~7e-5 rate
change from this factor helps explain the different amplitude and rate
residuals; lifetime, running and mixing differences must still be quantified.

SPheno reports `mW=80.348464`, a -0.030536 GeV difference from D12. It is
not inserted as an MW input by the exporter. Generated `RunSM_ZeeTypeII.f90`
uses a fixed `sinW2=0.22290` at MZ in constructing running SM inputs, and
SPheno performs matching/running; D12 directly fixes MW/MZ. The generated
calculation reports Q=160 GeV and tree scalar mass output (loop masses off).
These source facts establish different input paths, but do not isolate every
term producing the MW number; the exact final MW derivation is NOT_EVALUATED.
Forcing MW would not establish matched couplings. The input has alpha_s(MZ)
0.1187 versus D12 0.118; quark masses are default SPheno inputs (e.g.
mb(mb)=4.18, mt pole 172.89 GeV) versus D12's separately recorded
threshold/running choices. Quarks do not enter the compared direct scalar
lepton one-loop diagrams, but may affect matching. D12 F/Ye2 complex inputs
are written verbatim; SPheno derives Ye through its matching and rotates
fields. Eigenstate row signs were observed in the pilot. Full F, Ye, Ye2,
ZEL/ZER and scalar-mixing readback for every point remains NOT_EVALUATED.
No claim is made that selecting identical numerical mass values removes
running-versus-pole or perturbative-order differences.

## Next required work

Trace the PreSARAH tensor projector through the actual all-incoming amplitude
and photon conventions to prove the complex map; numerically export both
charged vertices including ZEL/ZER for all indices and scalar rows; instrument
charged and neutral contributions independently, quantify each input-scheme
change, and run phase, sign, null and rephasing tests. Then define a tolerance
from those measured mismatches and truncations and compare each coefficient
and rate. Treat all those gates as NOT_EVALUATED until demonstrated.

## Continuation: numerical root cause and component readback

The ignored generated backend was instrumented to export both complex charged
vertex orientations, actual rotation/Yukawa arrays, scalar-by-scalar raw
`OA2lS` increments, and neutral vertices and masses. The reproducible helpers
are `instrument_components.py`, `check_components.py`, and
`test_backend_transformations.py`; compact hashes and results are in
[d15_component_evidence.json](d15_component_evidence.json). The generated
vertex values agree with the generated analytic rotation expressions to
at most 5.7e-26 absolute over all 27 index triples and four witnesses. Against
the frozen expressions with one measured sign per scalar row, the maximum
absolute discrepancy is 1.1e-10, coincident with the generated Ye matching
difference up to 1.3e-10; F and Ye2 agree at the printed precision. These are
observations, not a general vertex-validation tolerance or a proof of an
operator convention. Both charged scalar row signs were measured and applied
to both ends; raw arrays and logs are in ignored `local/`.

A controlled same-input comparison of the neutral `h,H,A` contributions
initially differed from the candidate mapped Module3 amplitudes by up to
1.66e-4. The discrepancy was traced to the generated loop functions `C1g`
and `C0C1C2`: for equal internal lepton masses much smaller than the scalar
mass, the `r < 1e-10` branch substitutes `large=0` for logarithmically
singular expressions even when `r` is nonzero. The electron-to-125-GeV
squared-mass ratio is approximately 1.67e-11. The minimal experimental patch
`patch_small_ratio.py` changes only these two positive-ratio branches to use
the existing analytic expression, retaining the original zero-ratio branch.
With actual generated neutral vertices and masses in Module3, the candidate
complex residuals after the patch are at most 6.9e-11 (L) and 1.6e-15 (R)
over those contributions and four witnesses. This establishes the specific
source of the prior discrepancy; it does not prove the global operator map.
The patched coherent candidate residual against the original D12 snapshots is
at most 2.2e-7 in this sample, with different input schemes still present.
The patch is confined to ignored generated code and is not integrated into
Modules 0–14 or D14.

At the first witness, conjugating the input F and Ye2 phases conjugates both
complex generated coefficients exactly to printed precision. Setting F=0
makes both F-dependent charged-vertex orientations zero while the D and
neutral terms remain. These two checks are narrow; reverse ordering, other nulls, independent new fixtures,
matched BR reconstruction and a derivation from an explicit spinor matrix
element remain open. **Overall operator mapping and backend validation remain
NOT_EVALUATED.** Do not infer the required completion from the good residuals.

To reproduce after the reduced build and the existing K2 instrumentation:

```sh
python3 research/spheno_flavorkit/instrument_components.py research/spheno_flavorkit/local/SPheno-4.0.5/ZeeTypeII
python3 research/spheno_flavorkit/patch_small_ratio.py research/spheno_flavorkit/local/SPheno-4.0.5/ZeeTypeII/Observables/FlavorKit_LFV_ZeeTypeII.f90
(cd research/spheno_flavorkit/local/SPheno-4.0.5 && make Model=ZeeTypeII F90=gfortran)
python3 research/spheno_flavorkit/compare_dipoles.py
python3 research/spheno_flavorkit/check_components.py
python3 research/spheno_flavorkit/test_backend_transformations.py
python3 research/spheno_flavorkit/tests/test_small_ratio.py
```

The first two commands require a fresh unmodified generated copy (and refuse
reapplication); run the comparison before patching as well to retain the
failure trace. The installed `pytest` is an incompatible 2.6.0 on Python
3.10; the focused regression file can be run directly as shown.

A charged-lepton rephasing with phases `(0.31,-0.47,0.82)` was also
tested at the first witness, transforming the complete complex `F` and
`Ye2` matrices and comparing both generated coefficients to the predicted
phase. The L/R relative residuals are 9.77e-11 and 4.56e-11. The first
attempt failed with residuals 0.1891 and 0.1894 because the experimental
test script mistakenly transformed only the imaginary Ye2 block; after
fixing the test to transform both real and imaginary entries, the check
above passed. This is a test implementation error, not an adjustment to
physics inputs to force agreement. The 1e-10 assertion is a regression
check at this point, not a universal physics uncertainty.

Both charged eigenstate row signs were flipped in separate instrumented
executables with all corresponding Gamma2l vertices transformed; both
complex coefficients were unchanged to printed precision at all four
witnesses. Reconstructing the SPheno rate from its complex coefficients and
exported alpha, pole muon mass and `GammaMu` agrees with the printed rate to
2.6e-9 relative, within its nine-significant-digit output rounding. The
SPheno observable uses `width/(width+GammaMu)` and omits the nonzero
daughter-mass phase-space factor. `check_rate.py` reproduces this check.
The row-flip helper requires a disposable instrumented source and a rebuild;
restore the generated source after each run.

## Additional independent matrix-element and loop stress checks

See [OPERATOR_MATRIX_ELEMENT.md](OPERATOR_MATRIX_ELEMENT.md) for the tested
Dirac and crossed-chain identities and their limitation. These tests do not
fix the generated overall crossing sign, so the operator gate remains open.
The FormCalc 8 manual identifies 6 as PR and 7 as PL; do not infer the matrix
projector from the generated SL/SR name.

`python3 research/spheno_flavorkit/tests/test_loop_precision.py` compiles the
actual two experimental functions and original variants, and compares against
80-digit mpmath values. For the affected `m1=m2` branch the tested positive
ratios from `1e-30` through `1e-8`, including both sides of `1e-10`, agree
within 3e-16 relative; exact zero retains the original zero regulator
placeholder despite the logarithmic positive-mass divergence. Close to the
existing `r=0.999` Taylor switch, subtraction in the original closed form
loses precision: at 0.999 the relative error is 4.32e-8, and at 0.9989 it
is 2.95e-8. These are measured samples, not a bound for all masses.

A distinct untouched branch has the same positive-ratio issue:
`C1g(1,1e-11,1e-11)` returns zero versus `11.9142180118347` at 80 digits.
It occurs in the `m2=m3`, `m1>m2` guard in generated
`FlavorKit_LFV_ZeeTypeII.f90:38120-38123` (line numbers may change after
instrumentation). A disposable one-guard correction returns the reference
with relative error 1.0e-16 and retains the exact-zero placeholder. It has not
been promoted to the experimental backend patch or tested over all regimes.
The current experimental patch SHA256 is
`ef6e6ecbbdfee9247a1c04a6ce41682527108c12a9aa30ff0255469364b54b41`;
the local generated executable SHA256 is
`59b7145cdd9c309af4ee34e81bcabc218c6abc6ccae3d1564f1fa99970ac372c`.
No universal amplitude tolerance is justified by these local measurements.
