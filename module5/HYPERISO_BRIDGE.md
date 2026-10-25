# Gate B: pinned HyperIso runtime and external convention bridge

2026-10-25. **B1 `HYPERISO_REFERENCE_PASS`; B2 PARTIAL,
`MATCHING_CONVENTION_UNKNOWN`.** No `EXTERNAL_CONVENTION_PASS`, Zee BR,
linear screen, exclusion, likelihood, per-state bound or allowed label.
Machine-readable results and source SHA256 values:
[`hyperiso_bridge.json`](../validation/module5/hyperiso_bridge.json).
Gate A2 evidence and the frozen production calculation remain unchanged.

## B1: independently executed official references

[HyperIso v1.0.3](https://github.com/Hyperiso/Hyperiso/tree/09d26ac6e71d1528922097a896d15693589f636b),
17 July 2026, actual checkout HEAD/tag peel
`09d26ac6e71d1528922097a896d15693589f636b`; actual CLI version `1.0.3`.
No matching installed binary was found. Built the unmodified checkout in
ignored `validation/module5/local/HyperIso/`, following upstream
`reproducibility/README.md`: CMake Release, Ninja, `BUILD_WITH_CLI=ON`.
GCC 11.4.0 with `gnu++20`, CMake 3.22.1, Ninja 1.10.1, GSL 2.7.1,
Eigen 3.4.0. Source, build products and logs are not vendored.

The candidate harness initially aborted because its relative LHA filenames
were resolved under `Assets/`. It now uses absolute paths to the **same**
manifest inputs, matching upstream `run_cli_suite.sh`. It additionally
rejects modified tracked upstream sources/fixtures, checks CMake source
provenance, hashes the binary, validates normalized output and saves raw logs.
The source pin, program version, official manifest/reference metadata,
normalizer and comparator are all checked; no expected outputs were updated.

R1/R3/R6 passed; their normalized outputs are **byte-identical** to the
pinned expected files. The official **full R1–R7 suite also passed**, including
200 accepted serial statistical draws with seed 123456.

| Reference | Matching C7, C8 | Low-scale C7, C8 / BR |
| --- | --- | --- |
| R1, SM NNLO, qmatch=81 GeV | −0.210135, −0.114968 | q=4.8 GeV: −0.293757, −0.160027 |
| R3, SM NNLO, native observable defaults | — | BR(B→Xsγ)=0.00032967; BR(Bs→μμ)=3.2711e−9 |
| R6, archived THDM BSM NNLO, qmatch=81 GeV | +0.000800431, +0.000870192 | q=81 GeV: +0.000795987, +0.000868799 |

All Wilson coefficients and BRs are dimensionless; displayed imaginary
parts are zero. R3 has no explicit CLI `qmatch` option in the official case;
its native observable defaults are preserved. R6's archived Yukawa couplings
are **not Type-II**; its positive coefficients are not a Type-II sign test.
Neither R1 nor R6 is inserted into a formula at 160 GeV.

Precision is the upstream comparator's actual serialized precision:
`math.isclose` with manifest absolute/relative tolerances (R1: 1e−12/1e−8;
R3: 1e−14/1e−8; R6: 1e−12/1e−7), including its half-unit last-printed-digit
allowance. Byte identity does not establish unprinted digits or theory errors.
R3 and Misiak 2026 are different versioned prediction bases, not interchangeable
NNLO implementations.

## B2: executable same-input one-scalar comparison

The separate client links the existing release libraries without changing
HyperIso source. It calls the public `WilsonInterface::getFM` at **LO,
qmatch=q=160 GeV**. The archived spectrum is copied locally, with only the
charged mass, tanβ, Yukawa-type field and real diagonal quark/lepton coupling
blocks set explicitly. This isolates the Type-II quark-sector dipole limit;
it is not a validated scalar-potential or vacuum benchmark.

`THDMParametersHelper.cpp` reads real `YU[2,2]=lu`, `YD[2,2]=ld`, one
`MASS[37]`, and `WPARAM_MATCH_SM[6]`. `BWilsonTHDM.cpp` computes
`lu² F_i^(1)/3 − lu ld F_i^(2)`. Thus `lu=Y=cotβ`, `ld=−X=−tanβ` gives
the conditional Gate A2 amplitude's positive XY weight. The exact running
top mass obtained using the upstream helper's own QCD call is
**mt_MSbar(160)=163.96892236746697 GeV**. This number is supplied unchanged
to the frozen Zee calculation with γ=0 and to the independent 70-digit
diagram integrals. No independent mass conversion or calibration is inferred.

At mH=550 GeV, tanβ=2, the native HyperIso BSM matching result is
**ΔC7=−0.061015148990460226, ΔC8=−0.06554247561193852**.
The full audit uses masses 300, 550, 900, 2000, 100000 GeV at tanβ=2;
tanβ=0.2, 1, 2, 10, 50 at 550 GeV; and opposite-ld controls: **18 executions,
36 dipoles**, with SM+BSM=TOTAL checked separately. Mass decoupling and
the beta dependence pass. The sign-reversed ld control at 550/2 gives
+0.057721017975271606, +0.06304589993111945, falsifying an unchanged XY sign.
Accepted tolerances are 2e−11 relative / 2e−14 absolute. Actual maximum
absolute/relative diagram residuals are recorded in the JSON; they are
numerical residuals, not theory uncertainties.

Normalization trace: `WilsonManager.cpp` implements
`Cfull=Σ(αs/(4π))^n C^(n)`, so LO carries **no extra αs/(4π)**.
`BWilsonGroup.cpp` converts plain matching dipoles to effective coefficients
before standard-basis running using the `y_std/z_std` four-quark shifts.
The client verifies BSM C1–C6=0 in all LO probes, hence
**ΔC7eff=ΔC7, ΔC8eff=ΔC8** in this retained approximation.
`BXsDecay.cpp` retrieves these running coefficients, forms the LO squared
dipoles and higher-order interference terms, and constructs `BR_B_Xs_gamma`.
This traces their observable use; it is not a new two-state BR calculation.

The independent diagram comparison retains photon Qt=2/3 and the gluon
generator contribution with no closed-fermion-loop color multiplicity.
It rejects the opposite sign and extra common factors through signed
agreement across both chirality-flip terms and two distinct dipoles.
Complex CKM conjugation and chirality are **not independently tested by
these real scalar coefficient executions**.

## Remaining operator gate and injection API

`docs/main.tex` prints the negative Hamiltonian and the αs expansion.
Its `Check sign` editorial marker alone determines no discrepancy.
Pinned `Assets/template/MARTY/C7.cpp` and `C8.cpp` additionally expose
`−Vts* Vtb e³ mb/(32π² sin²θW MW²)` and the corresponding `e² gs` factor,
with `DiracCoupling::R`. These agree with the expected CKM/prefactor form,
but delegate the dipole to `chromoMagneticOperator` in optional external
MARTY. That operator insertion, its sigma/Fourier definition and the full
complex amplitude are not executed by the native THDM path tested here.
Consequently the numerical agreement and source trace do not remove the
remaining external operator-convention ambiguity: **`MATCHING_CONVENTION_UNKNOWN`**.

Generic complex coefficient injection **is exposed and documented in the
public C++ headers**: `WilsonInterface::addMatchingPatch` accepts a
`WilsonMatchingPatch` returning complex `scalar_t`; the normal matching,
composition and running pipeline uses the patch. The client verifies the
nonphysical API-test sum `(0.001+0.002i)+(−0.003+0.004i)=−0.002+0.006i`.
These are test coefficients, not fictitious Zee Yukawas. The CLI has no
corresponding documented coefficient-input option, and a dedicated two-state
Zee wrapper is **`ZEE_TWO_STATE_INJECTION_NOT_AVAILABLE`**. A separate minimal
adapter can use the existing generic C++ patch facility; no HyperIso source
change is required. Frozen Zee quark couplings/mixing remain real up to CKM.

[Misiak et al. v1, Sec. IV](https://arxiv.org/html/2608.29863v1) states that
Type-II charged scalars enhance BR. Our negative shifts and the negative
Eq.(4) coefficients agree **qualitatively** in the small-NP linear region.
This is not an operator proof, numerical Zee screen or calibrated NP error.
The 670 GeV one-state higher-order bound is not a bound on either Zee state.

Next physical action: pin and audit/execute a trusted O7/O8 insertion with
explicit sigma, Fourier, CKM and chirality conventions, then build the
minimal external adapter. Restore the hash-verified historical native
artifact to rerun the skipped tree witnesses; do not regenerate old physics.

## Tests and reproduction

**33 tests passed**: runtime harness 6, existing LO 16, dipole projection 7,
local native-amplitude algebra 4. One native tree **class** skipped because
`native_numerical.json` is absent locally; its seven historical live tests
are not relabeled as passes. No branch-guard suite is counted. All files
hashed in historical Gate A2 evidence are unchanged.

```sh
UP=validation/module5/local/HyperIso
BIN=$UP/build/UserInterfaceLib/hyperiso-ui
python scripts/zee_module5_hyperiso_runtime.py --upstream "$UP" --binary "$BIN" --output validation/module5/local/hyperiso_runtime.json
HYPERISO_BIN="$PWD/$BIN" bash "$UP/reproducibility/scripts/run_cli_suite.sh"
python scripts/zee_module5_hyperiso_bridge.py --upstream "$UP" --binary "$BIN" --output validation/module5/local/hyperiso_bridge/one_scalar.json
python -m unittest discover -s tests -p 'test_module5_hyperiso_runtime.py' -v
python -m unittest discover -s tests -p 'test_module5_bsgamma_lo.py' -v
python -m unittest discover -s tests -p 'test_module5_dipole_projection.py' -v
python -m unittest discover -s tests -p 'test_module5_native_amplitudes.py' -v
```
