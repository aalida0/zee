# Q4 generator-input gate — general complex Zee UV model

**19 October 2026. Status: SOURCE-DERIVED PyR@TE 3 MODEL CANDIDATE; GENERATOR NOT RUN; NO FULL BETA COEFFICIENTS VALIDATED.**

## Validation handoff

User-run Q3 integrated validation completed successfully: **135/135 required** + **16/16 SciPy-dependent** tests and 20/20 old B2 cases; the report is `work/zee_section8_Q3_integrated_v1/summary.json` on AF, not committed/uploaded. Q2e restricted Kanemura real-f ratio 0.965917428; Q3 exact singlet quartic minimization and synthetic counterexample checks pass. This report is numerical software consistency only, not an allowed physics point.

## Source-audited generator route

- **Primary:** PyR@TE 3 by Sartore–Schienbein, [arXiv:2007.12700](https://arxiv.org/abs/2007.12700), [official code](https://github.com/LSartore/pyrate). In `models/THDM.model`, the provided 2HDM already contains both doublet Yukawa tensors and lambda1..lambda7 operators. **Its illustrative `Substitutions` set lambda6=lambda7=0, impose Type-II textures and GUT-normalize g1; none of these substitutions can be copied into the general Zee UV model.**
- Specifically, `src/Core/Lagrangian.py` lines 552–555 and 594–644 use `handleSymmetricYukawa` to infer **antisymmetric** flavor Yukawa matrices from repeated identical fermions with antisymmetric contractions. This is a critical *source-observed PyR@TE 3 capability*, unlike warnings in historical PyR@TE 1 documentation. It does NOT prove the Zee f normalization works correctly until tested against the explicit source equation.
- In `src/Core/Lagrangian.py` lines 651–715, candidate complex scalar terms may generate conjugate terms automatically; inspect the resulting mapped Lagrangian to ensure lambda5,lambda6,lambda7,lambda10, m12, muZee and their h.c. are neither absent nor double-counted.
- **Independent generator:** RGBeta by Thomsen, [arXiv:2101.08265](https://arxiv.org/abs/2101.08265), [official package](https://github.com/aethomsen/RGBeta). A complete separate RGBeta model file and independent one-loop outputs still have to be built. Package capability alone is not an independent validation.

## Staged source-derived candidate

File: `rge_models/GeneralZee_PyRATE3_CANDIDATE_NOT_VALIDATED.model`.

Field content: SM quarks/leptons with three generations, two complex SU(2) doublets with Y=+1/2 and one complex SU(2) singlet `chi` with Y=+1. Includes general complex Yu1/Yu2, Yd1/Yd2, Ye1/Ye2; `f LL LL chi`; lambda1..lambda7, lambda_h, lambda8/9/10; m1, m2, m12, mchi and the Zee trilinear muZee. Conventions follow [Schmidt–Vandeleur arXiv:2512.17235v2](https://arxiv.org/html/2512.17235v2), Eqs. (3) and (4), except that the candidate is written in the standard unbroken symmetry basis rather than imposing physical alignment.

Independent hypercharge checks: `LL LL chi`: (-1/2) + (-1/2) +1=0; `Phi1 Phi2 chibar`: +1/2 +1/2 -1=0; `chibar chi Phi1bar Phi2`: (-1+1) + (-1/2+1/2)=0. The Weyl contractions and f flavor index antisymmetry are NOT certified merely by hypercharge invariance.

**Open normalization check:** in literature the f interaction may be defined with or without a 1/2 when summing over antisymmetric generation pairs. Match the physical matrix beta and interaction normalization to Kanemura et al., PRD64 (2001) 053007, Appendix A (A13), in the restricted real-f/top-only limit before interpreting an f beta from PyR@TE. Verify the full complex f antisymmetry under running.

**Open source-to-source comparison:** exactly reproduce Ferreira–Lavoura–Silva [arXiv:1001.2561](https://arxiv.org/abs/1001.2561), Eqs. (3)–(5), by setting f=0 and removing singlet interactions, in the SAME normalization and Yukawa tensor orientation. Verify gauge coefficients in the full Zee field content b=(22/3,-3,-7), g1=gprime not GUT normalized. Validate scalar quartic (all complex couplings) and trilinear dimensions separately.

## Acceptance requirements for Q4 (not yet met)

1. Execute PyR@TE 3 on the candidate with its supported version and record exact generator HEAD, Python dependencies, machine/environment, input SHA256, expanded interaction tensors, independent gauge-invariance checks, and raw one-loop outputs. Any parser failure, duplicate coupling, missing f, nonantisymmetric f, or unexpected complex/h.c. assumption is a hard stop.
2. Check the THREE source limits independently: full gauge b, f->0 FLS lepton/quark matrices, restricted real-f Kanemura A13. In addition verify lambda6/lambda7/10 and scalar self/portal source limits, dimensionful muZee and masses.
3. Independently generate the same model in RGBeta (or a documented independent equivalent). Compare beta components numerically at randomly seeded **complex** Yukawa and quartic points, subject to consistent field and coupling conventions, and report discrepancy values; never silently rescale f to force agreement.
4. Only then add the accepted beta functions to the repository's full UV coupled integrator, run on a single complete physical parameter set with documented threshold scheme, and only after fitting full neutrino+LFV compute physical quark FCNCs. Existing B2 matrices remain unfitted inputs.
5. At the end of this Q4 stage, use **one integrated new AF run** for all necessary source checks, independent comparator and model-aware numerics. Do not rerun Q3 merely to accumulate more tests.

## Decision

The model candidate is an actionable **generator input**, not generated beta functions. Full Zee RGEs and physically allowed Zee benchmarks are **UNKNOWN / NOT ESTABLISHED**. An untested PyR@TE file must not be promoted to a physical result.


## Q4 executable source-input gate (19 October 2026)

New code:
- `scripts/zee_section8_Q4_pyrate_generator_gate.py` — pinned official PyR@TE 3 checkout and CLI runner; exact field inventory and hypercharge/gauge b check; output SHA256; fail-closed JSON; does **not** claim full beta validation.
- `tests/test_zee_section8_Q4_pyrate_generator_gate.py` — 13 unit checks for field/operator inventory, source hypercharge, gauge coefficients, missing f/portal, noninvariant f, absent epsilon, unwanted lambda6/7 or GUT substitutions, output hygiene, and absence of false physics claims.

Local reproduction of the static input gate: **13/13 tests PASS** using Python 3.13 with PyYAML; generator execution and exported beta consistency **NOT RUN HERE** because the local shell has no network access to clone PyR@TE, and no AF session or Mathematica kernel is connected.

Verified official PyR@TE 3 source on GitHub:
- `LSartore/pyrate` pinned master HEAD `04b219c2016f3fc4f2371d72607edc26a7e06364` (2024-05-02).
- Entrypoint `pyR@TE.py` with CLI flags `--Model`, `--Loops`, `--Results`, `--CheckGaugeInvariance`, `--PythonOutput`, `--no-LatexOutput`, `--no-MathematicaOutput`, from `src/IO/Inputs.py` lines 127–183.
- Model parser accepts `ComplexScalars`; `src/IO/Inputs.py` aliases the example-file spelling `CplxScalars`.
- `src/Core/Lagrangian.py` lines 594–644 detects symmetric/antisymmetric same-field Yukawa tensors. The Zee-specific `f` input **has not been parsed by PyR@TE itself**.

One command for a new substantive AF stage (after `git pull --ff-only`; keep all output in `work/`):

```bash
python3 scripts/zee_section8_Q4_pyrate_generator_gate.py \
    --output-dir work/zee_section8_Q4_pyrate_v1
```

This runner performs the 13 Q4 contract tests first, executes the static source gate, shallow-fetches exactly the pinned upstream revision, then requests one-loop generation with gauge-invariance check and Python output. It writes `summary.json`, unit-test logs and generator logs. A nonzero return code is a hard blocker, not a passed result. **Even if the generator finishes, statuses remain `GENERATOR_EXECUTED_BUT_COMPLEX_BETAS_UNVALIDATED` and `full_Zee_RGE_calculation_accepted: false`.** No Q3 rerun is included.

Full Q4 acceptance is deferred until the generator's emitted f, Pi, lambda6/7/10, other quartics and muZee/mass equations are inspected; Kanemura A13 and FLS Eqs. (3)–(5) are exactly reproduced in explicitly normalized limits; and the independent RGBeta implementation agrees at general complex points. Important: simple hypercharge/operator checks do not prove the PyR@TE Weyl spinor normalization, flavor-index orientation, SU(2) epsilon/sign or automatic Hermitian-conjugate treatment.


## Q4v2 — confirmed Key4hep/PyR@TE import collision and isolation repair

User-run Q4v1 AF status: static source/input tests **13/13 PASS**, gauge coefficients **(22/3,-3,-7) PASS**, but upstream PyR@TE exited 1 before model expansion. The exact traceback was:

```text
from ModelsClass import Model
from Particles import Particle, ComplexScalar
ImportError: cannot import name 'ComplexScalar' from 'Particles'
(/cvmfs/sw.hsf.org/key4hep/releases/.../k4generatorsconfig/.../python/Particles.py)
```

This is **not a physics constraint or evidence the candidate Zee model was accepted by the generator**. The pinned upstream `pyR@TE.py` launcher appends its own `src/Core` path to Python's search path, allowing contaminated Key4hep `PYTHONPATH` to select an unrelated `Particles.py` first. Upstream has the expected `src/Core/Particles.py`.

Repair confined to our runner (`scripts/zee_section8_Q4_pyrate_generator_gate.py`):
1. Launch via `python -I -c ...` to ignore user Python environment search paths.
2. Explicitly prepend the *pinned* PyR@TE source directories, assert that `importlib.util.find_spec('Particles').origin` resolves to the exact `src/Core/Particles.py`, then execute the *unmodified* pinned `pyR@TE.py` via `runpy.run_path(..., run_name='__main__')`.
3. Drop `PYTHONPATH`, `PYTHONHOME` and `PYTHONSTARTUP` only for the child process; preserve necessary native-library environment settings and the user's shell.
4. Extend the Q4 unit suite from 13 to **16 tests**, including synthetic pinned-vs-Key4hep `Particles` collision, missing source module fail-closed behavior and environment-scoping checks. The equivalent import-isolation smoke experiment was independently reproduced **locally** (pinned source selected when present; hard failure when absent). Actual AF full generator completion is still **unverified**.

**One Q4 AF retry, reusing the prior pinned source instead of recloning:**

```bash
cd /home/aalida/zee
git pull --ff-only
python3 scripts/zee_section8_Q4_pyrate_generator_gate.py \
  --pyrate-root work/zee_section8_Q4_pyrate_v1/pyrate3_src \
  --output-dir work/zee_section8_Q4_pyrate_v2
```

If the isolated interpreter lacks scientific dependencies previously supplied through Key4hep PYTHONPATH, this may reveal a new **environment** failure; do not add Key4hep to PYTHONPATH again. Instead use an appropriate isolated interpreter/venv with PyR@TE's documented requirements. A successful execution remains **UNVALIDATED PHYSICS** until source limits and independent cross-checks pass.



## Q4v3 — PyYAML hidden by Python -I (user AF failure, diagnosed)

User-run Q4v2: `Q4_SOURCE_INPUT_CONTRACT_TESTS_PASS 16`, `Q4_PREFLIGHT_PASS True`, `Q4_GAUGE_1LOOP_B ['22/3', '-3', '-7']`; PyR@TE stdout only displayed its banner and stderr reported **`Error while importing PyYAML`**. The pinned generator launcher imports `yaml` before parsing the Zee model. This is a Python environment regression caused by the deliberately isolated `-I` mode hiding package roots originally provided through `PYTHONPATH`, **not** a failed Zee beta calculation.

Q4v3 repair in the local wrapper (no upstream/source physics changes):
- Resolve `yaml,sympy,numpy,scipy,h5py,matplotlib` via `importlib.util.find_spec` using the parent interpreter. All are documented requirements of the official PyR@TE 3 release.
- Pass precisely their package roots and expected absolute origins to the `python -I -c` bootstrap. Prepend pinned PyR@TE internal `src/Core`, `src/IO`, `src/PyLie`, `src/GroupTheory`, `src` first, then add only the discovered dependency roots. Drop `PYTHONPATH`, `PYTHONHOME`, `PYTHONSTARTUP` for the subprocess; retain other environment variables needed by native libraries.
- Assert PyR@TE's internal `Particles` origin and the exact source origin of each allowed dependency before running the original upstream entrypoint. Record `pyrate3_python_dependency_provenance.json` and stdout `Q4_IMPORT_PROVENANCE`.
- Q4 input suite extended to **19 regression tests**, including discovery of parent PyYAML, hidden third-party package import under isolated mode, and a mismatched dependency-origin fail-closed test. The bootstrap was independently smoke-tested locally with a synthetic Key4hep module collision and a hidden trusted PyYAML package; all three targeted trials passed, including import of the six real installed scientific packages in an isolated subprocess. **Full PyR@TE on AF remains unverified**.

One new AF invocation, reusing existing source:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 scripts/zee_section8_Q4_pyrate_generator_gate.py \
    --pyrate-root work/zee_section8_Q4_pyrate_v1/pyrate3_src \
    --output-dir work/zee_section8_Q4_pyrate_v3
```

A successful subprocess run permits inspecting generated expressions but **does not certify** full Zee RGEs. Continue checking the Kanemura A13 and FLS f=0 limits, scalar trilinear/complex conjugation, and independent RGBeta output before physics acceptance. If other dependencies are unavailable in the parent interpreter, fail closed with a precise missing-package message rather than modifying the Zee model.


## Q4v3 AF generator returned 0, but no RGE files (diagnostic pending)

AF terminal output reported `Q4_SOURCE_INPUT_CONTRACT_TESTS_PASS 19`, `Q4_PREFLIGHT_PASS True`, correct `(22/3,-3,-7)` gauge coefficients, followed by `Q4_FAIL_CLOSED RuntimeError('PyR@TE produced no output files')`. The original run's `pyrate3_stdout.log` and `pyrate3_stderr.log` have not yet been provided. **The precise reason is therefore NOT YET DETERMINED.**

Source audit of pinned upstream `LSartore/pyrate`:
- `src/IO/Dependencies.py` uses `exit()` (zero exit status) after logging missing mandatory dependencies.
- `src/Core/ModelsClass.py` and `src/IO/Inputs.py` have several other validation paths with `exit()` (again no guaranteed nonzero return code).
- `src/IO/Exports.py` would produce Python RGE files in `Results/[model name]/` if it reaches successful export, so an empty recursive results directory cannot count as a successful generator run.
- The Q4 wrapper appropriately uses a **fail-closed** artifact check. The new runner records `no_files_despite_zero_returncode`, prints the last 70 lines of both generator streams whenever no files appear, and archives PyR@TE's contemporaneous `log/PyLog*.log` files. This is DIAGNOSTIC ONLY; it changes no interaction or beta coefficient.

**Do not rerun Q4 or change the Lagrangian until reviewing these existing logs:**

```bash
cd /home/aalida/zee
echo "========== PYRATE STDOUT v3 =========="
tail -n 120 work/zee_section8_Q4_pyrate_v3/pyrate3_stdout.log
echo "========== PYRATE STDERR v3 =========="
tail -n 120 work/zee_section8_Q4_pyrate_v3/pyrate3_stderr.log
echo "========== LATEST UPSTREAM PYRATE LOG =========="
find work/zee_section8_Q4_pyrate_v1/pyrate3_src/log -maxdepth 1 -type f -name 'PyLog*.log' -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -n 3
```

Q4 full complex Zee beta functions, source limits, independent RGBeta agreement and phenomenological acceptance remain unverified.


## Q4v4 — diagnosed missing transitive dependencies (19 October 2026)

AF Q4v3 successfully resolved source provenance for pinned `Particles.py` and the six direct packages, but produced **zero** RGE files with subprocess return code 0. Its actual PyR@TE stdout revealed:

```text
Error: some dependencies are missing/outdated.
    -sympy >= 1.5 (current: None)
Warning: some optional dependencies are missing/outdated.
    -matplotlib >= 3.1 (current: None)
```

Their paths show *installed* SymPy 1.13.3 and Matplotlib 3.10.7 from Key4hep Python 3.13; PyR@TE's `src/IO/Dependencies.py` catches arbitrary import exceptions and reports a failed import as version `None`. Consequently the packages were found by `find_spec` but couldn't fully import under `python -I` when secondary package roots (e.g. SymPy's `mpmath`, Matplotlib's `packaging`, etc.) were absent. The precise first transitive module was not in PyR@TE's log; `mpmath` is a plausible, not directly observed, cause.

Repair: keep `python -I` and all pinned PyR@TE internal source paths first. Restore absolute directory entries from the parent's Python `sys.path` *after* the six explicit scientific package roots. Exclude empty/relative entries and all directories with an unrelated top-level `Particles.py` to prevent the original Key4hep collision. The child now actually imports all six declared packages and checks their `__version__` and exact `find_spec` origins **before** running upstream PyR@TE. An import failure now includes the underlying exception, avoiding PyR@TE's misleading `None`. Log restored roots to `pyrate3_transitive_import_roots.json`. This expands the admitted dependency search roots beyond the six primary packages, so the pinned package-origin checks and Key4hep collision filter remain necessary.

Three additional tests cover filtering colliding module roots, successful loading of a package requiring a separately located transitive dependency, and fail-closed reporting of a missing nested dependency. Q4 source-input suite is now **22** tests (19 previously passed on AF, three newly committed). The isolated dependency-chain behavior was independently reproduced locally, including both fail-before and succeed-after cases. The new complete AF run has not yet been executed.

**Single AF Q4v4 retry (use existing pinned source):**

```bash
cd /home/aalida/zee
git pull --ff-only
python3 scripts/zee_section8_Q4_pyrate_generator_gate.py \
  --pyrate-root work/zee_section8_Q4_pyrate_v1/pyrate3_src \
  --output-dir work/zee_section8_Q4_pyrate_v4
```

The expected preliminary checks are `Q4_SOURCE_INPUT_CONTRACT_TESTS_PASS 22`, `Q4_PREFLIGHT_PASS True`, `Q4_GAUGE_1LOOP_B ['22/3','-3','-7']` and `Q4_IMPORT_PROVENANCE`. **No equations are certified or model point accepted just because these checks pass.** A generator run that returns 0 without substantive RGE artifacts is still rejected, and a successful artifact must be compared with Kanemura, FLS and independent RGBeta.
