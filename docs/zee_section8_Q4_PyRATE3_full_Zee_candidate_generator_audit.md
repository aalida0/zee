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


## Q4v4 actual generator result — successful beta generation, optional post-export failure

The AF `work/zee_section8_Q4_pyrate_v4` execution passed 22 source/input unit tests. The pinned PyR@TE 3 upstream log confirms:

- Lagrangian expansion and mapping completed;
- gauge-invariance check **All OK**;
- **one-loop RGEs generated** for gauge, Yukawa, quartic, scalar mass, and trilinear sectors;
- RGE recombination completed;
- substitutions applied;
- `Exporting to Python... Done.`

Upstream then attempted its unrelated default `EndCommands: pdflatex [name].tex`, even though the runner disabled the LaTeX output option, and raised `FileNotFoundError: 'pdflatex'`. The runner therefore correctly failed on subprocess exit 1, **but the generated Python output may already be complete**. Do NOT interpret this as a model RGE failure and do NOT rerun solely to satisfy pdflatex. Inspect files under `work/zee_section8_Q4_pyrate_v4/generator_output/GeneralZee_CANDIDATE_NOT_VALIDATED/PythonOutput/`.

A new non-executing static audit `scripts/zee_section8_Q4_audit_existing_pyrate_exports.py` inventories the already generated `RGEs.py`, model solver module, and `run.py`. It uses AST parsing without importing or running the generated scripts, hashes each export, lists beta functions, and enforces presence of gauge 3, Yukawa 7 (including f, Ye1, Ye2), quartic 11 (including l6, l7, l10), scalar mass 4, and trilinear 1. It does not establish that coefficients, normalization or complex tensor symmetries are correct. Companion synthetic regression tests intentionally omit f / complex scalar couplings and verify fail-closed behavior.

**One AF command, no repeat RGE generation:**

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \\
    -p 'test_zee_section8_Q4_audit_existing_pyrate_exports.py' -v &&
python3 scripts/zee_section8_Q4_audit_existing_pyrate_exports.py \\
    --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \\
    --report work/zee_section8_Q4_pyrate_v4/export_inventory.json
```

The audit result may be `INCOMPLETE` for several physically interesting reasons (e.g. no valid f beta was exported). That must be investigated from raw RGEs rather than relaxed by renaming/masking couplings.

**Current physics classification**: full one-loop general Zee equations **symbolically generated by PyR@TE 3 under our input conventions**, export file completeness **awaiting audit**, Kanemura restricted-real f and FLS f→0 normalization/coupled Yukawa checks **not performed**, independent RGBeta **not performed**, phenomenological acceptance **not established**.


## Q4v5 — 26 exported equations present; begin source-limit comparisons

AF user verified Q4v4 generated export inventory:

```text
Q4_EXPORTED_BETA_FUNCTION_COUNT 26
Q4_STATIC_EXPECTED_BETA_INVENTORY PASS
Q4_FULL_COMPLEX_ZEE_PHYSICS_VALIDATION False
```

Function list includes beta_gp, beta_g2, beta_g3; beta_Yu1/Yu2, beta_Yd1/Yd2, beta_Ye1/Ye2, beta_f; beta_l1..l7, beta_l8..l10, beta_lh; beta_m1/m2/m12/mchi, beta_muZee. This proves AST parseability and function-name coverage **only**. In particular, scalar complex conjugation/coefficients, operator f conventions and flavor tensor maps are not certified.

New first physics-source probe `scripts/zee_section8_Q4_generated_source_limit_probe.py` loads *only* the previously generated `RGEs.py`, never its `run.py`. It calls one-loop beta functions at deterministic points and compares:

1. Gauge: beta_gp=(22/3) gp^3, beta_g2=−3 g2^3, beta_g3=−7 g3^3, SM non-GUT hypercharge.
2. Kanemura 2001 Appendix A (A13): source-reduced **real antisymmetric** 3×3 f, zero ordinary Yukawas. This comparison is strictly conditional on the generator input's f normalization matching the historical convention. A mismatch is NOT automatically an incorrect beta—it requires a physical operator-normalization audit. No silent rescaling.
3. Gauge/real-f/complex-f antisymmetry, f=0 fixed subspace.
4. Ferreira–Lavoura–Silva 2010 multi-doublet quark Yukawa beta equations, with complex general Yu1/Yu2, Yd1/Yd2, Ye1/Ye2, f=0. Compares all four matrices directly at a fixed deterministic seed. Discrepancies demand tensor orientation, conjugation and convention audits.

It emits each residual, signature mapping, export SHA-256 and statuses in JSON; returns nonzero for mismatches or errors, and **never** marks complete Zee UV RGEs or allowed benchmarks as established. Nine synthetic tests validate positive reference functions and rejection of wrong gauge/f factors, unknown parameters, missing functions and wrong shapes. The nine new tests and this numerical comparison have **not yet run against the AF generator export**.

**AF command, no generation rerun:**

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests -p 'test_zee_section8_Q4_generated_source_limit_probe.py' -v &&
python3 scripts/zee_section8_Q4_generated_source_limit_probe.py \
  --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
  --report work/zee_section8_Q4_pyrate_v4/source_limit_probe_v1.json
```

Even all source-limit checks passing **does not** prove the general complex beta_f, general beta_Ye1/Ye2, beta_l6/l7/l10, muZee mass sector or RGBeta agreement. The next rigorous stage must inspect the explicit symbolic tensors and independently derive/compare these components.


## Q4v6 — lepton Yukawa and full-complex covariance gate

AF Q4v5: 9/9 synthetic tests and 11/11 source-limit comparisons PASS. Gauge exact; historical real-f beta reproduces Kanemura A13 (normalized residual 2.76e-16); complex f antisymmetry residual about 1e-18 absolute; four general quark Yukawas reproduce FLS 2010 at f=0 with normalized residuals below 8e-16. Existing NumPy matrix subclass warnings are cosmetic; the generated source uses matrix-specific multiplication and .H and must not be blindly converted to ndarray.

New script: scripts/zee_section8_Q4_complex_lepton_scalar_covariance_gate.py
New tests: tests/test_zee_section8_Q4_complex_lepton_scalar_covariance_gate.py (11 synthetic unit cases). AF validation remains pending.

- Implement independently FLS 2010 Eq(5a-c) for both lepton Yukawa matrices Pi1/Pi2 with all six generic complex doublet Yukawas at f=0; a_Pi = -9/4 g2² - 15/4 gp².
- Evaluate all 26 beta functions under Phi2_new=e^{i theta} Phi2_old and chi_new=e^{i psi} chi_old. Coupling weights: Yu2:+theta, Yd2/Ye2:-theta, f:-psi, l5:-2theta, l6/l7/l10/m12:-theta, muZee:-theta+psi, others invariant. Check H2 only, chi only and combined rephasings.
- Check complex-conjugation covariance for all 26 and numerical reality of 13 beta functions for manifestly real couplings.
- Test generic one-loop f-feedback in both charged-lepton Yukawas: nonzero with generic f, invariant under f phase and quadratic under f→2f. Quark beta functions must not have direct f dependence at one loop. Check the only dimension-one scalar coupling muZee=0 remains zero under RGEs.
- Fail closed on any discrepancy; preserve raw source hashes and residuals. This is a model symmetry and FLS limiting-equation check, NOT an independent complete beta-function derivation or RGBeta validation.

AF invocation (reuses existing generated RGEs; does NOT rerun PyR@TE or Q3):

    cd /home/aalida/zee
    git pull --ff-only
    python3 -m unittest discover -s tests -p 'test_zee_section8_Q4_complex_lepton_scalar_covariance_gate.py' -v &&
    python3 scripts/zee_section8_Q4_complex_lepton_scalar_covariance_gate.py --generator-output work/zee_section8_Q4_pyrate_v4/generator_output --report work/zee_section8_Q4_pyrate_v4/complex_covariance_v1.json

Full complex Zee RGEs and physical point acceptance remain unverified.


## Q4v7 — independent pure-scalar one-loop quartic beta calculation (19 October 2026)

User-run Q4v6 reported **156/156 PASS**: rephasing covariance in the complete complex Zee scalar-Yukawa system, conjugation covariance, reality of real beta functions, both independent FLS 2010 lepton Yukawa f=0 limits, nonzero f-induced lepton Yukawa feedback obeying phase and quadratic scaling, zero direct quark f feedback, and muZee=0 multiplicative protection. Together with the Q4v5 11/11 published source-limit comparisons, **167 numerical source/symmetry checks passed**. None independently compared the genuine Zee scalar quartic coefficients.

**New genuinely independent calculation** (not RGBeta): `scripts/zee_section8_Q4_independent_scalar_hessian_gate.py`. The general Zee quartic potential is reconstructed as `V4 = q^T C q` with five gauge-invariant real bilinears `q=(Phi1†Phi1, Phi2†Phi2, chi†chi, Re(Phi1†Phi2), Im(Phi1†Phi2))` and ten canonically normalized real scalar components. The one-loop **pure-scalar** (all gauge and fermion Yukawa couplings switched off) effective-potential divergence gives

```text
16*pi^2 beta(V4)|_scalar = 1/2 * Tr[(d^2 V4/d r_i d r_j)^2].
```

This is the standard one-loop quartic scalar contribution, related to general scalar RGE calculations such as Machacek–Vaughn NPB249 (1985) 70–92, DOI 10.1016/0550-3213(85)90040-9. The Hessian and real-orbit sampling are written independently of the PyR@TE tensor/diagram rules. An overconstrained, full-rank real-field projection recovers **all 15 real components** of `l1,l2,l3,l4,l5,l6,l7,lh,l8,l9,l10` (four complex parameters l5/l6/l7/l10). The field design uses 96 seeded configurations and checks rank, conditioning and polynomial closure. Two analytic checks are reproduced locally, with all other interactions zero: `beta_l1 = 12*l1^2` for O(4) Higgs-doublet quartic and `beta_lh = 20*lh^2` for O(2) complex-singlet quartic. The analytic Hessian code's projection residual was <1e−15 for the synthetic full-complex test point; **this does not claim AF PyR@TE agreement yet**.

The new comparison evaluates the existing generated PyR@TE quartic functions with gauge=all Yukawa=f=all dimensionful terms=0 at six coupling sets: two full-complex examples, one pure-doublet, one pure-singlet, one pure Zee-portal complex example, and one general mixed-doublet complex example. Expected **66 independent beta comparisons** (6 x 11 physical quartic couplings), with all complex components compared, a fail-closed tolerance and per-case JSON residuals. Twelve companion unit tests validate bilinear definitions, independent potential reconstruction, Hessian finite-differences, rank/closure, O(4)/O(2) coefficients, full-complex projections, and mutated portal-beta rejection.

**AF command; NO RGE regeneration and NO Q3 rerun:**

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_section8_Q4_independent_scalar_hessian_gate.py' -v &&
python3 scripts/zee_section8_Q4_independent_scalar_hessian_gate.py \
  --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
  --report work/zee_section8_Q4_pyrate_v4/scalar_hessian_v1.json
```

**Acceptance:** Even 66/66 PASS validates **only** the pure-scalar contributions to all 11 one-loop quartic beta functions and their complex components. Gauge/Yukawa-f-mediated scalar terms, beta_f complex nontrivial Yukawa structures, dimensionful masses/muZee, and the independent full RGBeta cross-check remain unverified; no fully allowed Zee point has been found.


## Q4v8 — independent electroweak gauge contributions to 11 Zee quartic RGEs

User-run Q4v7 results: **66/66 PASS** of the independent one-loop pure-scalar quartic Hessian comparison across six quartic configurations. The max values in the previous normalized-difference field (as high as 1.8e-3 on isolated benchmarks) are driven by the 1e-12 numerical normalization floor for analytically vanishing coefficients; the actual pass criterion uses absolute differences and a max(1,|beta|) scale. Do not describe those as 0.18%-level disagreements in physical nonzero beta coefficients. Independent pure-scalar part is validated only at the six tested configurations; it is not a proof of every full-complex parameter combination.

**New independent gauge calculation:** scripts/zee_section8_Q4_independent_gauge_quartic_gate.py. Start from two canonically normalized SU(2) doublets with Y=1/2 and one canonically normalized electrically charged singlet with Y=1. In arbitrary ten-real-field backgrounds, construct the 4x4 gauge-boson mass-squared matrix M_V² in basis (W1,W2,W3,B) by expanding the covariant kinetic terms. The one-loop gauge contribution to the scalar quartic polynomial is the vector Coleman-Weinberg UV divergence (3/2) Tr[(M_V²)^2] plus universal external-scalar gauge anomalous dimension terms. Coupling-level gauge-linear terms are: l1..l7: -(9 g2²+3 gp²) lambda; lh: -12 gp² lh; l8,l9,l10: -(9/2 g2²+15/2 gp²) lambda. The gauge quartic polynomial is projected onto all 15 real components of the 11 quartic couplings with the independently verified scalar-bilinear design matrix.

**Analytic limits verified in the construction:** with quartics=0,
beta_l1(beta_l2) = 3/4(3g2^4+2g2² gp²+gp^4),
beta_l3 = 3/4(3g2^4-2g2² gp²+gp^4),
beta_l4=3g2² gp²,
beta_lh=6 gp^4,
beta_l8=beta_l9=3 gp^4.
No pure gauge constant term seeds complex l5,l6,l7,l10.
These follow independently from the gauge kinetic representation, and are checked by dedicated regression tests.

**AF comparison:** With all Yukawa, f and dimensional scalar terms zero, compare
 beta_l^generated(gp,g2,quartics) - beta_l^generated(0,0,quartics)
against the independent gauge expression. This isolates g^4 and lambda*g² without counting the scalar Hessian contribution twice. Six gauge/quartic cases yield **66 comparisons**, with tolerance absdiff <= 2e-9*max(1,|got|,|expected|). Fourteen synthetic/analytic tests validate gauge boson masses, electroweak/charged-singlet limits, projections, covariance of portal coefficients, and rejection of a deliberately modified gauge beta. The new 14 tests and actual 66 AF comparisons have **not yet been executed on AF**.

**Single AF command (reuse prior generated RGEs, do not rerun Q3 or PyR@TE):**

    cd /home/aalida/zee
    git pull --ff-only
    python3 -m unittest discover -s tests -p 'test_zee_section8_Q4_independent_gauge_quartic_gate.py' -v &&
    python3 scripts/zee_section8_Q4_independent_gauge_quartic_gate.py --generator-output work/zee_section8_Q4_pyrate_v4/generator_output --report work/zee_section8_Q4_pyrate_v4/gauge_quartic_v1.json

Even 66/66 PASS would establish only the gauge-dependent quartic contributions in addition to the previous pure-scalar limits. The complete Yukawa-dependent quartic beta terms, full complex f/charged-lepton mixing betas, trilinear/mass betas and independent RGBeta full-theory agreement remain unvalidated. No physical Zee point has been established.


## Q4v9 — Independent f=0 fermion-box and mixed quartic-Yukawa RGE stage

User-run AF Q4v8 **66/66 PASS** for independent electroweak-gauge contributions to all eleven Zee quartic beta functions at six parameter configurations. Maximum absolute difference among reported cases ~1.61e-15. This validates tested scalar-gauge g^4 and lambda*g² contributions on top of Q4v7's 66/66 independent scalar-only checks. Overall previously reported numeric gauge/FLS/Kanemura source limits 11/11, complex covariance 156/156, scalar Hessian 66/66, and gauge quartic 66/66 have passed: **299 numeric checks** across complementary tests. This is NOT an independent verification of the entire 26-function beta system.

The new independent Q4v9 script `scripts/zee_section8_Q4_independent_yukawa_quartic_gate.py` calculates **fermionic Yukawa effects in the f=0 limit**, without reusing PyR@TE loop formulas. With arbitrary complex Yukawa matrices Yu1/Yu2, Yd1/Yd2, Ye1/Ye2 and arbitrary charged + neutral Higgs backgrounds, build the quark (uL,dL) × (uR,dR) 6×6 Dirac mass matrix and lepton (nuL,eL) × eR 6×3 mass matrix from the Higgs/Yukawa Lagrangian. The one-loop fermionic Coleman–Weinberg quartic divergence is

```text
(16*pi²) beta(V4)|ferm_box = -2 [3 Tr((Mq†Mq)^2) + Tr((Me†Me)^2)].
```

The independent Higgs wavefunction mixing matrix `T_kl = 3Tr(Yd_k Yd_l† + Yu_k† Yu_l) + Tr(Ye_k Ye_l†)` comes from the FLS 2010 multi-doublet Yukawa formalism; apply `delta(Phi_l) = sum_k T_kl Phi_k` to the general Zee quartic potential and add `delta V4` for its one-loop lambda*Y² contributions. No additional f wavefunction contribution is included because **f is explicitly zero**.

Project the total fermionic quartic polynomial onto the **15 real quartic components** using the independently verified 10-real-field design. Compare against `beta_l[PyR@TE](Y) - beta_l[PyR@TE](Y=0)` with gauge=0, f=0 and dimensions=0; pure-scalar terms cancel. Seven configurations (isolated top, lepton, full-complex quark/lepton, nonzero general scalar quartics and complex portals) yield **77 comparisons** covering all eleven quartic functions. Seventeen synthetic/analytic tests verify standard top-only beta_l2=-12yt^4 and +12lambda2 yt², lepton beta_l1=-4ye^4 and +4lambda1 ye², charged portal l8 contribution +6 yt² l8, complex projection, quartic scaling, full-doublet-rephasing invariance, charged-singlet decoupling at f=0, and mutated lambda10 comparator rejection.

**This is NOT the nonzero-f full Zee Yukawa/portal validation**. Do not claim full model RGEs accepted if Q4v9 passes. Next source-independent physics step is the f-dependent quartic contributions and full complex lepton/f beta coefficients, then dimensionful scalar beta terms and RGBeta.

One AF command, reusing existing PyR@TE export:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
 -p 'test_zee_section8_Q4_independent_yukawa_quartic_gate.py' -v &&
python3 scripts/zee_section8_Q4_independent_yukawa_quartic_gate.py \
 --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
 --report work/zee_section8_Q4_pyrate_v4/yukawa_quartic_f_zero_v1.json
```

Pending AF evaluation. The generator is NOT rerun. Complete Zee beta validation remains FALSE, and physical point acceptance UNKNOWN/NOT EVALUATED.


## Q4v10 — 77/77 Yukawa quartics PASS, independent Zee f-dependent quartics

User-run Q4v9 on AF yielded **77/77 PASS** for all eleven scalar quartic beta functions, including two generic-complex Yukawa/full-quartic random seeds, charged-singlet portals, a top-only sector, and a charged-lepton-only sector. Maximum absolute residual across the seven cases was approximately 9.38e-14. Combined Q4v5...v9 report: 11 + 156 + 66 + 66 + 77 = **376 numerical validations PASS**. This is evidence for all 11 quartic coefficients in pure scalar, gauge, and general f=0 Yukawa limits at tested points. It does not test f-dependent quartic terms.

New Q4v10 scripts:

- scripts/zee_section8_Q4_independent_f_quartic_gate.py
- tests/test_zee_section8_Q4_independent_f_quartic_gate.py (17 synthetic and analytic regression tests).

**Physics derivation.** In an arbitrary ten-real-scalar background, construct the complex symmetric 9x9 mass matrix for the nine left Weyl leptons (nu_L,e_L,e_R^c), three flavors each. Write the 6x6 LL mass subblock from the antisymmetric Zee interaction as M_{nu,eL}=2 f chi; the coefficient 2 is fixed by Kanemura's reduced real-f normalization in Appendix A, Eqs A9–A11. The L−eR^c mass block equals complex-conjugated Pi_k Phi_k in the 2-component convention, with generic complex Pi1/Pi2. The resulting f-dependent fermionic one-loop quartic counterterm is computed independently from the field-dependent mass spectrum as

```text
(16 pi²) beta(V4)|f-fermion-box
 = -Tr[(M†M)^2 - (M0†M0)^2],
M0=M(f=0) with every other coupling unchanged.
```

The charged-singlet wavefunction contribution is

```text
(16 pi²) beta(V4)|f-chi-wave
  = 8 Tr(f†f) s dV4/ds,
s=|chi|².
```

This wavefunction coefficient is independently **source-normalized** (but not independently diagram-derived) against Kanemura A9-A11. At Ye=0 the method reproduces:
 beta_lh|f = 16 lh Tr(f†f) −32 Tr[(f†f)^2],
 beta_l8|f = 8 l8 Tr(f†f),
 beta_l9|f = 8 l9 Tr(f†f),
 beta_l10|f = 8 l10 Tr(f†f).
The raw box is fully independent of PyR@TE's loop expressions. Generic complex Ye1,Ye2 and complex f produce both box-interference quartic terms and wavefunction contributions.

Project onto 15 real quartic components using the independent real-field scalar-orbit basis (96-128 samples, overconstrained rank checked). Eight configurations include historical real f with/without singlet quartic, pure complex f, complex f with portals, generic complex f and nonzero lepton Yukawas, two complex quartic seeds, and a mixed-portal case. Compare beta_l(f)−beta_l(f=0) from existing generated RGEs against the independent construction, with all gauge and dimensional parameters zero. Expected **88 comparisons** (eight x eleven). Zero effect on the seven pure-doublet quartic beta functions is a falsifiable consequence at one loop. The 17 regression tests check source-normalized f quartic coefficients, f flavor antisymmetry, 9x9 Weyl mass symmetry, correct phase covariance, f^4 and f² scaling, mixed complex projection closure, and synthetic mutated-coefficient rejection.

**One AF run, NO new PyR@TE generation and no Q3 rerun:**

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests -p 'test_zee_section8_Q4_independent_f_quartic_gate.py' -v &&
python3 scripts/zee_section8_Q4_independent_f_quartic_gate.py \
    --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
    --report work/zee_section8_Q4_pyrate_v4/f_dependent_quartic_v1.json
```

Q4v10 script and regression tests are committed but **AF tests and real comparison remain pending**. Any mismatch is to be investigated at the Weyl flavor ordering/complex-conjugation/operator-normalization level, not silently repaired with a factor. Even 88/88 PASS does not certify full complex beta_f, f-dependent beta_Pi1/Pi2, dimensionful scalar RGEs, threshold matching, independent RGBeta or physically allowed model points.


## Q4v11 — 88/88 nonzero-f quartic agreement; new scalar-only dimensionful beta comparison

AF Q4v10 outcome: **88/88 PASS** across eight f and complex lepton-Yukawa scenarios, max reported absolute difference ~5.63e-16. Combining all previously recorded v5...v10 11+156+66+66+77+88 gives **464 numerical source/metamorphic/reference comparisons PASS**. This does not guarantee full UV RGEs, threshold implementation, or physical model viability.

New independent scalar-only dimensionful RGE code:
  scripts/zee_section8_Q4_independent_dimensional_scalar_gate.py
Companion tests:
  tests/test_zee_section8_Q4_independent_dimensional_scalar_gate.py (13).

With ten canonically normalized real scalar fields r and bilinears q=(Phi1†Phi1,Phi2†Phi2,chi†chi,Re Phi1†Phi2,Im Phi1†Phi2), reconstruct
  V2=m1*q1 + m2*q2 + mchi*q3 - 2 Re[m12*(q4+i q5)],
  V3=2 Re[muZee*epsilon_ij Phi1_i Phi2_j chi*],
  V4=all 11 general quartic couplings (previously tested).

The independently derived Hessian H(V) splits as H2+H3+H4, homogeneous in background fields with degrees 0, 1, 2. One-loop pure-scalar counterterms of degrees 2 and 3 from (1/2) Tr(H(V)^2) are:
  degree2: Tr(H2 H4) + (1/2) Tr(H3^2);
  degree3: Tr(H3 H4).

Project onto the **five real quadratic coefficients** (m1,m2,mchi,Re m12,Im m12) and **two real cubic coefficients** (Re muZee,Im muZee), using 128 overconstraining real-field backgrounds, full-rank verification, and separate polynomial closure tests. Independently test analytic single-field limits:
  beta_m1(scalar) = 6*l1*m1 (all other couplings zero);
  beta_mchi(scalar) = 8*lh*mchi (all others zero);
  pure muZee cubic induces additive scalar masses even with all quadratic terms zero, with beta_mchi=2 beta_m1=2 beta_m2;
  trilinear beta is proportional to muZee and zero at muZee=0.
Note: these analytic limits are conditional on the model potential normalization and do NOT cover gauge, f or ordinary Yukawa contributions.

Seven scalar coupling/spectrum cases compare each generated PyR@TE scalar mass/trilinear beta (with gauge/Yukawas/f=0) to this independent Hessian prediction. Expected **35 comparisons** against existing RGEs, without rerunning PyR@TE, including complex offdiagonal mass m12 and trilinear muZee. Synthetic tests verify finite-difference quadratic/cubic Hessians, 7-real-component projection, complex rephasing of full potential, isolated O(4)/O(2) mass limits, pure Zee-cubic additive mass effects, projection closure, and deliberate beta mismatch. These 13 tests have NOT YET BEEN RUN on AF.

**Single AF command:**

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_section8_Q4_independent_dimensional_scalar_gate.py' -v &&
python3 scripts/zee_section8_Q4_independent_dimensional_scalar_gate.py \
  --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
  --report work/zee_section8_Q4_pyrate_v4/scalar_dimensional_v1.json
```

This is an independent scalar-loop coefficient cross-check, **not** a complete calculation of dimensionful Zee RGEs. Priority after Q4v11: full complex beta_f and f-dependent beta_Pi1/Pi2 using a independently derived or separate-engine one-loop general Weyl-Yukawa tensor, then gauge/Yukawa/f contributions to dimensionful scalar running and independent RGBeta full-source matching. Do not run scale evolution on physical benchmark candidates until all essential sectors are certified.
