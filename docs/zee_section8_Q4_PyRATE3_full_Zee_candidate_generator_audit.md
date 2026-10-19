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


## Q4v12 — 35/35 scalar-only dimensionful PASS; new independent complex Weyl Yukawa RGE gate

AF Q4v11: **35/35 PASS** (7 cases x 5 dimensionful parameters m1,m2,m12,mchi,muZee). Max absolute difference ~1.05e-9 in the mass-squared coefficients (nominal mass-squared scale ~1e5 GeV²); all passed the explicit scale-aware tolerance. Thus Q4v5–Q4v11: 11+156+66+66+77+88+35 = **499** passed numeric source/consistency comparisons. The tested contributions to scalar mass and trilinear RGEs are PURE SCALAR, not the gauge or f/Yukawa contributions.

**New substantive independent one-loop Yukawa calculation**:
- scripts/zee_section8_Q4_independent_complex_weyl_yukawas.py
- tests/test_zee_section8_Q4_independent_complex_weyl_yukawas.py (17 synthetic/source-limit tests).

Physics source: Schienbein, Staub, Steudtner, Svirina, NPB939 (2019) 1–48, Eq.(5.11), arXiv:1809.06797. Cross-reference Chankowski, Lewandowski, Meissner, JHEP11(2016)105, Eq.(7.26). In a real-scalar + left-handed Weyl fermion representation, the general symmetric Yukawa tensors Y_a=d M_F/d phi_a satisfy the one-loop formula

```text
beta_Ya|Yuk = 1/2 (F.T @ Ya + Ya @ F)
             + 2 sum_b [ Yb @ Ya† @ Yb ]
             + sum_b [ S_ab * Yb ],
F = sum_b Yb† @ Yb;
S_ab = Re Tr(Ya† @ Yb).
```

All betas here are 16*pi² d/d ln(mu) coefficients. For two-component Weyl fermions κ=1/2, giving the scalar-wavefunction term above. Use the already independently derived 9x9 symmetric field-dependent Zee lepton mass tensor from Q4v10, with ten canonically normalized real scalars, general complex Ye1/Ye2, and complex antisymmetric f with f chi coupling 2 f chi. Construct and process ten Y_a tensors at once and project beta tensors back to beta_f, beta_Ye1 and beta_Ye2 through **four independent doublet components and two complex-singlet components**, rejecting mismatched flavor orientation/conjugation/antisymmetry. Include independent fermion Casimir gauge factors: beta_f gauge=−(3/2 gp²+9/2 g2²)f; beta_Ye gauge=−(15/4 gp²+9/4 g2²)Ye.

The generic Weyl implementation was independently prototyped locally and reproduces both published limits:
- f=0: **both** general complex FLS charged-lepton Yukawa beta matrices, for noncommuting Ye1/Ye2.
- Ye1=Ye2=0 and real antisymmetric f: historical Kanemura 2001 beta_f = [−3/2 gp²−9/2 g2²+12 sum_{i<j} f_ij²] f.

Q4v12 checks generated beta_f, beta_Ye1, beta_Ye2 at seven lepton configurations (zero and nonzero gauge, real and complex f, three complex Ye+f seeds), including direct f-dependent Ye increments relative to f=0 (7x5=35). At three more configurations with all **six** quark and lepton Yukawas generic complex, verify beta_f has no direct quark dependence and the f-induced increments of beta_Ye1 and beta_Ye2 agree after f=0 subtraction (3x3=9); total expected **44 numerical comparisons** on existing PyR@TE export. Full complex Yukawa/field conjugation projection checks and source-limit regressions accompany the code. This stage does not regenerate PyR@TE or modify generated equations. A nonzero residual is investigated, not repaired with hidden factor adjustments.

**One AF invocation (source-limit crosscheck, no regeneration):**

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_section8_Q4_independent_complex_weyl_yukawas.py' -v &&
python3 scripts/zee_section8_Q4_independent_complex_weyl_yukawas.py \
  --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
  --report work/zee_section8_Q4_pyrate_v4/complex_weyl_v1.json
```

This would independently test the remaining complex f and f-dependent lepton Yukawa coefficients, but even a full 44/44 PASS would not alone certify the **complete general Zee RGEs**: the gauge/Yukawa/f contributions to all dimensionful scalar beta functions, full multiengine RGBeta or equivalent comparison, and threshold matching are still pending. No model parameter point has been certified against full neutrino+LFV+flavor+Higgs/vacuum constraints.


## Q4v13 — LARGE integrated one-loop 26-beta and short-flow verification

AF Q4v12 outcome supplied by user: **44 / 44 PASS** for independent Schienbein symmetric-Weyl lepton/f tensor beta functions, including complex f, Ye1/Ye2, and f-induced increments with generic complex quark Yukawa matrices. The earlier 499 checks plus 44 yield **543 cumulative reported numerical matches**. One-loop full-Zee source comparison is NOT automatically certified: Q4v5...v12 mostly checked separate sectors and limits.

**Q4v13 is a single large integrated verification**, to avoid proliferating numerous narrow gates.

New files:
- \`scripts/zee_section8_Q4_large_integrated_one_loop_gate.py\`
- \`tests/test_zee_section8_Q4_large_integrated_one_loop_gate.py\`

Build a **complete independent one-loop reference for all 26 betas at the SAME complex point** using the previously source-checked independent ingredients:
1. gauge betas [22/3,−3,−7]; quarks via FLS 2010 full complex 2HDM Yukawa matrices;
2. general complex lepton/f Yukawas from symmetric 9-Weyl Schienbein tensor, supplemented with the independent FLS quark-trace contribution to beta_Ye1,Ye2;
3. all eleven quartics: independently computed scalar-field Hessian + electroweak gauge-boson mass/linear wave contribution + full complex quark/lepton mass-box and doublet Yukawa-wave contribution + complex Zee f/lepton Weyl box and charged-singlet-wave contribution;
4. **NEW dimensionful mixed contribution check**: prior pure scalar 10-real-field quadratic/cubic Hessian, plus gauge and fermionic external-scalar wavefunction effects. Gauge factors for doublet quadratic operators are −(9g2²+3gp²)/2, and for singlet mass −6gp². Zee-cubic gauge is −(9g2²+9gp²)/2. Yukawa doublet wave uses the full complex 2×2 FLS trace matrix T_kℓ and the induced bilinear variations. f singlet wave is +8 Tr(f†f) in beta_mchi and +4 Tr(f†f) in beta_muZee. In particular beta_muZee gets Tr(T) + 4 Tr(f†f) minus the gauge factor. These are one-loop **MS-bar** coefficients, source-convention-dependent and unvalidated at mixed points until the new AF run is performed.

An overconstrained 96-background scalar orbit basis independently projects the scalar potential coefficient polynomials. Comparison with PyR@TE's **unchanged generated RGEs.py** is component-wise for 26 functions, including complex matrix entries, with explicit max-abs and scale-aware tolerance per function (3e−9 +3e−9*max(1,|got|,|expected|)). Cases: **12** independently seeded full complex points, **4** independently phased equivalent full complex points, and **2 eight-step generated-RK4 trajectories**, one generic and one starting at a Type-II quark texture with generic nonzero lepton Yukawas. Compare to independent reference at **5 checkpoints each** (steps 0,2,4,6,8). Thus **(12+4+5+5)×26 = 676 full beta comparisons**, plus 2×8 RK4 source-evolution steps (64 full beta-vector source evaluations) and 11 focused sanity/negative controls. If any direct comparison fails, fail closed, skip trajectory and record which beta functions mismatch instead of hiding the discrepancy. Tracks whether wrong-doublet quark Yukawa textures are radiatively generated, without claiming any FCNC limit.

**One AF command** (runs only saved RGEs; NO new generation or Q3 rerun):

\`\`\`bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
 -p 'test_zee_section8_Q4_large_integrated_one_loop_gate.py' -v &&
python3 scripts/zee_section8_Q4_large_integrated_one_loop_gate.py \
 --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
 --report work/zee_section8_Q4_pyrate_v4/large_integrated_v1.json
\`\`\`

**Current state:** Q4v13 code committed, NOT executed on UChicago AF; 676 comparisons are pending. Even 676/676 would certify only **tested one-loop full-complex RHS numerical consistency and short integration**, NOT RG threshold matching, independent 2-loop terms, global vacuum stability, physical neutrino/LFV/flavor/Higgs constraints, or permission to call candidates 0/32 viable. Physical Zee allowed=UNKNOWN. Follow-up after success should be first a scale-running/threshold prescription and then actual flavour/viability pipeline; avoid endless Q4 check proliferation.


## Q4v13 AF PASSED: integrated 26-function one-loop numerical agreement

**Actual UChicago AF output from user:** all 26 one-loop generated beta functions agree at **12 generic complex points + 4 independently rephased complex points + 5 points on each of two short numerical RG trajectories**. This is **676/676 PASS**. Largest absolute difference across the logged points is about 1.28e-9 on dimensionful coefficients, within the explicit scale-aware tolerance. The Type-II-start Yukawa trajectory from 700 to 2000 GeV induced Frobenius norms |Yd2|_F = 5.492237841e-7, |Yu1|_F = 5.069945239e-6, even though both vanished initially. These are sources of wrong-doublet couplings and NOT neutral meson FCNC likelihoods or exclusions.

Total prior Q4v5..v12 543 checks + Q4v13 676 = **1219/1219 source/limit/metamorphic numerical comparisons PASS**. Full 26-equation one-loop RHS is now strongly cross-validated at tested complex points, including the dimensionful gauge+Yukawa+f terms, and a modest coupled one-loop integration. This is enough to stop adding serial *coefficient-only* gates. **No complete physics acceptance is established**: potential EFT thresholds, full BFB along complex RGE flows, global vacuum, collider tools, matched NNLO b->s gamma, CKM and precision quark input scheme, neutrino parameter likelihood and all LFV amplitudes remain incomplete. Continue the Paper 1 model/flavor physics program.

## Next single *physics-connected* pilot: Gate C1 joined scalar/neutrino/full-one-loop UV diagnostics

- Script: \`scripts/zee_gateC1_joined_uv_pilot.py\`
- Regression suite: \`tests/test_zee_gateC1_joined_uv_pilot.py\` (17 unittest methods).
- Output: \`work/gateC1_joined_uv_v1/summary.json\` and \`joined_uv_diagnostics_NOT_ALLOWED.csv\`.

Use the EXISTING B4 scalar/EWPO screened thirty spectra and corresponding B2 neutrino-closed (f,Y) solutions, not new random, unproven potential points. Build **one coherent renormalizable lagrangian at matching scale mu0=mH2** for each tested solution.

**SCALAR:** explicitly map restricted CP-conserving Florentino et al. (2021) Eq.16 into PyR@TE's general complex UV basis:

\`\`\`text
l1..5 = lambda1..lambda5 from Gate6 inverse spectrum
l6=l7=0; lh=lc; l8=k1; l9=k2; l10=-k12
m12=m12sq; mchi=mc2; muZee=mu4;
m1=m12sq*tan(beta)-v²/2*(lambda1*cos²(beta)+lambda345*sin²(beta))
m2=m12sq*cot(beta)-v²/2*(lambda2*sin²(beta)+lambda345*cos²(beta))
\`\`\`

Match all reconstructed neutral, pseudoscalar and charged masses and check the B4 serialized quartics; require Gate6 sufficient BFB and tree unitarity at mu0. Complex \`l6,l7\`, \`l10\` and wrong-doublet quark Yukawa couplings may be generated under coupled RG flow; DO NOT artificially project them back to the restricted subspace at each step.

**LEPTON:** B2's Chen/Herrero charged-lepton mass/Higgs-basis Y is the coefficient of \`-sqrt(2)*bar(ell_R) Y nu_L H_perp^-\`. The symmetry-basis Yukawas used by generated RGE are instead \`Ye1=cos(beta)*kappa_e-sin(beta)*rho_e\`, \`Ye2=sin(beta)*kappa_e+cos(beta)*rho_e\`, where \`kappa_e=sqrt(2)*Mell/v\`, \`rho_e=sqrt(2)*Y†\` with the Hermitian conjugation ESSENTIAL to preserve flavor orientation. Preserve the antisymmetric B2 f with the model's charged-singlet phase convention. Require neutrino mass-matrix closure against the same one fixed illustrative NO target and verify saved B2 closure roundtrips.

**QUARK and EW GAUGE input scope:** illustrative diagonal CKM=I Type-II quark Yukawa boundary, approximate dimensionless SM Yukawa eigenvalues (top .93 etc) divided by sin(beta)/cos(beta) respectively, and approximate gauge couplings. These are NOT precise running MS-bar Yukawas or a physical CKM/flavor fit and must be replaced before any quantitative UV cutoff or FCNC exclusion result. This deliberate scope limitation avoids presenting an arbitrary quark boundary as physics.

**PROVENANCE LOCK:** C1 refuses to run unless the user-produced Q4v13 report certifies exactly 676/676 passed source comparisons and its stored SHA256 matches the unmodified generated `RGEs.py`. This is a source integrity requirement, not a physical model acceptance claim.\n\n**FLOW:** RK4 over all 26 real/complex matrices and couplings, from mu0=mH2 to 10 TeV, with 24 time steps and an independently repeated 48-step run. Record the coarse/refined terminal mismatch (must be <=2e-4 on max-scaled coefficient) if both reach the endpoint; if a threshold is crossed, retain both paths as diagnostic stopping cases, not UV exclusion. Heuristic stopping diagnostics: quartic absolute value reaches 4*pi or Yukawa entry abs reaches sqrt(4*pi), or gauge input >=3. These are deliberately NOT rigorous perturbativity/unitarity/BFB conditions and not physical UV scales; no decoupling or thresholds. Output per-solution status, last mu, generated lambda6/7, wrong-doublet Yukawa norms, B2 neutrino closure, initial scalar BFB, and every incomplete physical constraint as NOT_EVALUATED.

**One AF run (NO PyR@TE regeneration):**

\`\`\`bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_gateC1_joined_uv_pilot.py' -v &&
python3 scripts/zee_gateC1_joined_uv_pilot.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --b2-json work/gateB4_zee_adaptive_pilot/B2_flavour/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
  --q4v13-report work/zee_section8_Q4_pyrate_v4/large_integrated_v1.json \
  --top-candidates 3 --solutions-per-candidate 2 --steps 24 \
  --upper-GeV 10000 \
  --output-dir work/gateC1_joined_uv_v1
\`\`\`

This is a **large physical mapping and coupled flow exercise**, not another coefficient-by-coefficient validation. Gate C1 does **not** implement full lepton flavor or meson likelihoods, HiggsTools, global vacuum or threshold matching; those are the next actual paper constraints. NO output receives an "allowed" label.


## Gate C1 v1 AF outcome — six joined RGE paths hit a heuristic scale boundary

AF logs from user confirm six successful B4/B2/full-one-loop runs, each
without unhandled errors; all six stopped by an **unclassified numerical
perturbativity diagnostic** before the chosen 10 TeV endpoint:

| B4 spectrum | neutrino ranks | last RECORDED checkpoint GeV | last checkpoint max abs quartic |
|---|---|---:|---:|
| B4_0000648 | 1,2 | 2607.6263585 | 9.3088956 |
| B4_0000318 | 1,2 | 1676.5482280 | 11.4383770 |
| B4_0001151 | 1,2 | 1684.7207798 | 8.95836135 |

**DO NOT CALL THESE LAST CHECKPOINT SCALES THE CUTOFF.**
Existing pilot records an accepted history point every four RK4 steps
and aborts after a later step that violates one of three numerical
heuristics: max_i |lambda_i| >=4pi, max_ij |Y_ij or f_ij| >=sqrt(4pi),
or an extreme gauge coupling >=3. The stdout did not identify which
criterion was violated or its crossing scale. Similar stopping between
ranks 1,2 at fixed B4 scalar point is EVIDENCE of predominantly scalar
running, but the specific driver is not known until recorded.
No global vacuum or full-LFV/meson flavor/HiggsTools exclusions
were imposed. No threshold matching; quark Yukawas and gauge
couplings were approximate CKM-identity illustrative inputs.
Thus these results are **not physical UV cutoffs or constraints**.

### C1 v2 — One larger multi-spectrum diagnostic, not more RGE tests

Expanded the existing script \`scripts/zee_gateC1_joined_uv_pilot.py\`
to report the **FIRST coupling** exceeding the heuristic cutoff at a
localized within-step boundary, not an old checkpoint. For a crossing,
bisect the full one-loop RK4 step for 12 iterations, record accepted and
rejected scale bracket and the first crossing's leading couplings,
including whether the trigger is quartic, Yukawa/f, or gauge. Reject
non-finite evolution as a separate numerical failure, not a
perturbativity exclusion. Independently evolve 24 and 48 RK4 steps;
when both reach the endpoint demand max-scaled difference <2e-4,
and when both reach a heuristic crossing demand their crossing scales
agree within 5% and driver names match. These are **solver** checks,
not theoretical uncertainties. New regressions compare the bisection
algorithm with the **analytic Riccati flow**
\`16pi² d(lambda)/dlogmu =20 lambda²\` and ensure modified output
preserves all missing-physics constraint flags.

Run the **entire 30-spectrum B4 shortlist** with the **first three
neutrino-family solutions per spectrum**, 90 joined RG trajectories
plus 90 independently refined 48-step trajectories. Aggregate
\`lambda_c(mu0)\`, \`lambda1(mu0)\`, the triggering quartic and
localized numerical crossing \`mu_heuristic\` into a per-spectrum
CSV and a diagnostic cohort summary; all plots/quantiles are
explicitly **biased B4-screened sample diagnostics**, not the
allowed fraction or a prior-independent distribution of cutoff scales.

\`\`\`bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_gateC1_joined_uv_pilot.py' -v &&
python3 scripts/zee_gateC1_joined_uv_pilot.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --b2-json work/gateB4_zee_adaptive_pilot/B2_flavour/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
  --q4v13-report work/zee_section8_Q4_pyrate_v4/large_integrated_v1.json \
  --top-candidates 30 --solutions-per-candidate 3 --steps 24 \
  --upper-GeV 10000 \
  --output-dir work/gateC1_joined_uv_v2_cohort
\`\`\`

New outputs:
- \`summary.json\`: all 90 per-solution coarse/refined diagnostic
  boundary brackets, full model-mapping provenance, and driver counts.
- \`joined_uv_diagnostics_NOT_ALLOWED.csv\`: each solution with
  first-limiting coupling, numerical boundary estimate/bracket,
  RGE solver scale-convergence, and missing physics.
- \`cohort_by_scalar_spectrum_NOT_ALLOWED.csv\`: candidate-by-candidate
  spread across three neutrino-family ranks.

The **paper-level UV program after this exploratory cohort** must
first settle the model's consistent Type-II quark alignment/symmetry,
include CKM and properly matched running quark inputs, and implement
full general-complex quartic BFB/unitarity/vacuum and thresholds along
the flow. Full neutrino likelihood, complete LFV (not just partial
amplitudes), modern two-charged b->s gamma and HiggsTools also remain
required for Paper 1. Do not extrapolate a 90-case diagnostic cohort
into model-wide exclusion, discoverability or publication-level
statistical conclusions.


## C1 v2 AF result: scalar quartic UV diagnostics fail for ALL 30 selected spectra

**Actual user-provided 2026-10-19 log:** C1 v2 ran 30 distinct B4 scalar spectra with three independent B2 neutrino-Yukawa representatives each, 90 joined full 26-one-loop-RGE trajectories and their numerical step-doubling controls. All **90/90** trajectories reached the **heuristic** \`max(|lambda_i|)=4*pi\` cutoff before the 10 TeV target. All 30 distinct scalar-spectrum cutoff estimates are in the range **1308.699–3605.650 GeV**, with median ~**1608.941 GeV**. **23/30** spectra cross below 2 TeV. First limiter: \`lh\` (the complex charged singlet self-quartic) in **18 spectra / 54 runs** and \`l1\` (the first Higgs-doublet quartic) in **12 spectra / 36 runs**. Leptonic solution ranks 1,2,3 have identical displayed limiting scales (high precision) for every spectrum. Coarse/fine boundary agreement metrics ~6.7e-6 to 2.04e-5, but **these quantify RK4 step-size sensitivity, not theoretical scale errors**.

This is a useful **negative result in the biased, large-cascade B4 local sample**; NOT a universal constraint on the Zee model, NOR a full-theory UV bound. The initial \`lc~4.5\` is large in the original 2021-inspired benchmarks, and \`lambda1\` is sensitive to the neutral-scalar soft parameter. Do not conflate an arbitrary \`4*pi\` criterion with a Landau pole, or conclude that neutrino/LFV requirements intrinsically force the early scalar divergence without a general viable flavor fit.

## Gate C2: 240-point PAIRED quartic UV-rescue experiment

New driver \`scripts/zee_gateC2_paired_uv_rescue.py\` and tests \`tests/test_zee_gateC2_paired_uv_rescue.py\`. **C2 is deliberately a large physics-controlled study, not another small source-level coefficient gate.**

For each of the same **30 B4 charged/neutral scalar spectra**, evaluate EIGHT systematically selected, mass-spectrum-preserving potentials (8×30=**240 initial spectrum-potentials**) at the **same** charged H1/H2 masses and charged mixing gamma, fixed neutral h,H,A masses, alpha,beta, tanbeta, k1,k2,k12, fixed same B2 neutrino f,Y family (rank 1).

Interventions, performed as precise counterfactuals:
1. unmodified C1 baseline, exactly reproducing its first crossing and driver;
2. cap charged-singlet self quartic \`lh=lc<=1.0\`;
3. cap \`lh<=0.4\`;
4. tune \`lambda1=1.0\`;
5. tune \`lambda1=0.5\`;
6. combine \`lh<=1\` and \`lambda1=1\`;
7. combine \`lh<=0.4\` and \`lambda1=1\`;
8. combine \`lh<=0.4\` and \`lambda1=0.5\`.

Tuning lambda1 is done exactly by inverse CP-even tree-mass reconstruction, at unchanged \`alpha,beta,mh125,mH\`:
\`\`\`text
m12sq = [mh125^2*cos(alpha)^2 + mH^2*sin(alpha)^2
         - lambda1_target * v^2*cos(beta)^2]/tan(beta)
\`\`\`
Then recompute *all* 2HDM quartics and scalar-mass terms in the same fixed renormalizable potential; the charge/neutral scalar spectrum is unchanged but scalar interactions and all potential-sensitive bosonic decay widths can change. Simply replacing lambda1 in the RGE boundary without changing this underlying potential is NOT allowed.

Lowering positive lh independently of the mass spectrum is possible because the charged singlet has no VEV. Recheck **exact scalar eigenmasses, Gate6 sufficient BFB, tree unitarity**. Original scalar S,T,U predictions depend on masses and mixing rather than lh or m12sq directly, so these on-shell oblique inputs stay unchanged under the paired intervention; other collider and precision observables can change and are explicitly NOT inherited.

Use the saved B2 rank1 neutrino f,Y pair and recalculate neutrino matrix closure (it depends on mH1,mH2,gamma, unchanged); convert Higgs-basis Y into symmetry-basis Ye1/Ye2 exactly; evaluate provisional B3 included-channel charged branching fractions for the new potential; evolve *all 26 one-loop Zee couplings* using Q4v13 source-provenance lock with twice-refined RK4 to **10 TeV**. Numerically bracket any first |quartic|=4pi (or Yukawa/gauge heuristic) crossing and test numerical stability. Comparison baseline (unmodified) is also provenance-locked against saved **C1 v2 90-solution report**, with identical SHA hashes of B4/B2/RGEs and first crossing scales/drivers.

**One AF command (do not reuse an old output directory):**
\`\`\`bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_gateC2_paired_uv_rescue.py' -v &&
python3 -u scripts/zee_gateC2_paired_uv_rescue.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --b2-json work/gateB4_zee_adaptive_pilot/B2_flavour/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
  --q4v13-report work/zee_section8_Q4_pyrate_v4/large_integrated_v1.json \
  --c1-cohort-summary work/gateC1_joined_uv_v2_cohort/summary.json \
  --max-spectra 30 --steps 24 --upper-GeV 10000 \
  --output-dir work/gateC2_paired_uv_rescue_v1
\`\`\`
Outputs \`summary.json\` and \`paired_uv_rescue_diagnostics_NOT_ALLOWED.csv\`; summary shows per-variant tree acceptance, numerically stable UV trajectories, heuristic 10 TeV survival, limiting couplings, and per-spectrum paired rescue outcomes. If none survives, that is valuable evidence that simply decreasing lh/l1 is insufficient *in this particular high-cascade sample*. If some survive, advance these specifically to **full running BFB and tree unitarity, complete flavor/neutrino constraints and non-toy CKM matching**, before any allowed benchmark or high-scale bound. Recompute any altered cascade branching fractions and do not claim original phenomenological fit remains unchanged.

**Crucial:** these 240 are **constructed modifications of a biased 30-spectrum shortlist**, not a random prior or exclusion limit for the general Zee theory. Physical allowed remains UNKNOWN; all full-LFV/HiggsTools/modern b->s gamma/global vacuum/CKM/threshold conditions NOT_EVALUATED.



## C2 AF result — near-total rescue of heuristic 10 TeV perturbativity by paired quartic tuning (2026-10-19)

Actual AF \`Pasted text(7).txt\` logs: C2 completed **240/240 paired potential configurations**, 30 B4 scalar spectra × 8 scalar counterfactuals, each with tree-level BFB sufficient and tree unitarity at matching and numerically stable full 26 one-loop diagnostic flow. All 30 unmodified baselines violate the chosen \`|lambda_i|<4*pi\` bound below 10 TeV (C1 reproduced). Among counterfactuals:

\`\`\`text
baseline                    0/30 reach 10 TeV
cap_lh_1                    7/30
cap_lh_0p4                  7/30
target_l1_1                 0/30
target_l1_0p5               0/30
both_lh1_l1_1              29/30
both_lh0p4_l1_1            29/30
both_lh0p4_l1_0p5          29/30
\`\`\`

The only exception among joint changes: \`B4_0000827\`, which first crosses \`l3\` at ~6.376, 6.379 or 7.235 TeV, depending on the intervention. For all other paired targets the one-loop heuristic 10 TeV goal is met. **This shows the original low crossing scale is NOT intrinsic to the fixed charged-Higgs mass+mixing spectrum under the existing approximate quark boundary.** It does NOT prove UV consistency, global vacuum stability, full multiscalar unitarity, threshold/CKM matching, LFV or experimental viability. Percentages are conditional on an intentionally selected local B4 cohort and should never be read as an allowed fraction of the general Zee model. B3 included-channel cascade proxies are recalculated by C2 but the stdout contains no summary of their values; do not assume unchanged signal rates.

## C3 — One larger running-BFB test of complete complex Zee scalar quartics

Script \`scripts/zee_gateC3_running_complex_bfb.py\`; tests \`tests/test_zee_gateC3_running_complex_bfb.py\` (16). Probe **60 full complex Zee RGE paths**: 30 scalar spectra × two combined C2 counterfactuals, \`both_lh1_l1_1\` and \`both_lh0p4_l1_0p5\`, each toward 10 TeV, evaluating full complex quartic BFB at **25** logarithmically spaced scales per trajectory (for 24 steps). This is NOT another 26-beta numerical coefficient gate; Q4v13 already completed 676/676.

For x=Φ1†Φ1, y=Φ2†Φ2, s=|χ|², z=Φ1†Φ2 with |z|≤sqrt(xy), use the EXACT general complex 11-quartic polynomial in the previously validated PyR@TE field convention:

\`\`\`text
V4=.5*l1*x²+.5*l2*y²+l3*xy+l4*|z|²
   +Re(l5*z²)+2Re[(l6*x+l7*y+l10*s)*z]
   +lh*s²+l8*x*s+l9*y*s.
\`\`\`

A rigorous but possibly too conservative lower bound via complex modulus, triangle inequality and AM-GM \`2x sqrt(xy)<=x²+xy\` reads \`V4 >= (x,y,s)·M·(x,y,s)^T\` with

\`\`\`text
M11 = .5*l1-|l6|
M22 = .5*l2-|l7|
M33 = lh
2*M12 = l3 + min(0,l4-|l5|) - |l6|-|l7|
2*M13 = l8-|l10|
2*M23 = l9-|l10|
\`\`\`

If the real symmetric 3×3 M is strictly copositive (using the well-known Hadeler criteria), **BFB of the full 10-real-scalar complex quartic is rigorously certified at that scale**. Failure of this conservative sufficient test is NOT instability. Independently sample ≥2048 reproducibly chosen PHYSICAL gauge-invariant field-space orbits, \`x+y+s=1, |z|²<=xy\`, including pure fields, mixed boundaries, generic complex phases. A sampled \`V4<0\` is a **genuine quartic unbounded-from-below witness**; no negative orbit detected is NOT BFB certification. Each scale gets precisely one of \`BFB_SUFFICIENT_CERTIFIED\`, \`BFB_NEGATIVE_WITNESS\`, \`BFB_INCONCLUSIVE\`. Paths that encounter an actual negative direction stop early; inconclusive do not become passes.

Accept only saved Q4v13 complete source hash and a saved C2 summary containing 240 interventions with identical B4/B2/RGE inputs and stable RK4 solver. This is a scale-sampled one-loop quartic BFB test, NOT a full global vacuum or general-complex coupled-channel tree unitarity certification, and it still lacks full LFV/mesons/HiggsTools, threshold matching, CKM and a physical UV cutoff.

**Single AF command:**

\`\`\`bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_gateC3_running_complex_bfb.py' -v &&
python3 -u scripts/zee_gateC3_running_complex_bfb.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --b2-json work/gateB4_zee_adaptive_pilot/B2_flavour/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
  --q4v13-report work/zee_section8_Q4_pyrate_v4/large_integrated_v1.json \
  --c2-summary work/gateC2_paired_uv_rescue_v1/summary.json \
  --max-spectra 30 --steps 24 --orbit-samples 2048 \
  --upper-GeV 10000 \
  --output-dir work/gateC3_running_complex_bfb_v1
\`\`\`

Pending AF result. File outputs:
  \`summary.json\` with per-variant rigorous-sufficient and negative-witness counts, plus \`running_BFB_diagnostics_NOT_ALLOWED.csv\`. Most important distinctions: which of the 29/30 RGE-perturbative paths are also rigorously sufficiently BFB throughout the sampled scales, explicitly unstable, or mathematically INCONCLUSIVE. At sampling time only; stability between steps and dimensionful charge-breaking global vacuum not certified.



## C3 AF outcome — 58/60 rescued coupled trajectories sufficiently BFB, 0 negative witnesses

Actual AF log supplied 2026-10-19 (Pasted text (8)): all 60 paths (30 B4 scalar spectra, 2 paired C2 counterfactuals) were executed against the unchanged 26 one-loop RGEs. C3 reports **29/30 COMPLETE_TO_TARGET with sufficient copositivity BFB at EVERY sampled scale for each intervention**, hence 58/60 successful running-BFB diagnostic paths (24 steps + matching scale per case = **1450 certified field-independent sufficient checks**). No negative quartic gauge-invariant orbit witness was found. Only B4_0000827 stopped at the preexisting C2 perturbativity threshold, so its lack of a full 10 TeV BFB certificate is **not a demonstrated unstable vacuum**. These checks are strong enough to establish mathematically sufficient lower bounds on V4 at sampled scales, but do not prove scale-continuous BFB, global charge-breaking vacuum stability including dimensionful terms, or physically viable spectra. Neutrino f,Y closure was checked against one illustrative target, not a full fit.

## Gate C4 — full 55-channel general complex scalar tree unitarity + running-BFB joint test

Reason: **C3 alone cannot establish theoretical UV consistency**, because scattering-matrix unitarity can fail even when the individual |quartic|<4π and a BFB lower bound are satisfied.

New \`scripts/zee_gateC4_running_55channel_unitarity.py\` and
\`tests/test_zee_gateC4_running_55channel_unitarity.py\` (18 regression tests).
Instead of relying on the original 2021 Appendix C restricted Q,Y blocks,
compute the exact high-energy 55×55 symmetric two-real-scalar scattering
matrix from all TEN real scalar components of \`Phi1, Phi2, chi\`, including
radiatively induced complex l5,l6,l7,l10. There are 10×11/2=55 normalized
symmetric two-particle states |ij>/sqrt(1+δ_ij). For V4=q^T C q and
q_a=.5 phi_i A^a_ij phi_j, derive contact vertex tensor:

\`\`\`text
T_ijkl = 2 C_ab [A^a_ij A^b_kl + A^a_ik A^b_jl + A^a_il A^b_jk]
M_(ij),(kl) = T_ijkl / sqrt[(1+δ_ij)(1+δ_kl)]
a0_eigen = - M_eigen / (16π)
tree-unitarity requirement: max |M_eigen| < 8π.
\`\`\`

**Independent normalization validation**: the restricted Gate6 benchmark
from Florentino et al 2021 Appendix C predicts max
|M_eigen| = **18.13677908573045**; the independent full 55-real-channel
construction returns the same maximum to machine precision, confirmed
by a standalone NumPy calculation. Additional exact analytic limits:
lambda1-only max eigen=3 λ1, lambda2-only=3 λ2, singlet lh-only=4 lh.
The matrix/eigenspectrum remains invariant under general complex
Higgs-doublet rephasing.

Trace the **same 60** paired C2/C3 counterfactuals under the full
complex 26-one-loop Zee flow, using 24 and 48 logarithmic RK4 steps
toward 10 TeV. Evaluate all 55 eigenvalues and the full C3 conservative
BFB sufficient proof at EVERY sampled step on both grids. RK4
step-bisect any first |eigen|=8π crossing, check its stability against
a 48-step calculation (<=5% crossing-scale difference), and report
the first theoretical numerical warning (tree unitarity vs the
earlier |quartic|=4π heuristic). Require *exact* Q4v13/C2/C3
source and B4/B2 provenance. Fail closed if C4 contradicts
C2's 10 TeV heuristic or C3's original 24-step BFB outcomes.
The reported number of 10 TeV survivors must meet ALL tested
heuristic perturbativity, sufficient BFB and complete 55-channel
tree unitarity on both grids.

**One AF command:**

\`\`\`bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_gateC4_running_55channel_unitarity.py' -v &&
python3 -u scripts/zee_gateC4_running_55channel_unitarity.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --b2-json work/gateB4_zee_adaptive_pilot/B2_flavour/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --generator-output work/zee_section8_Q4_pyrate_v4/generator_output \
  --q4v13-report work/zee_section8_Q4_pyrate_v4/large_integrated_v1.json \
  --c2-summary work/gateC2_paired_uv_rescue_v1/summary.json \
  --c3-summary work/gateC3_running_complex_bfb_v1/summary.json \
  --max-spectra 30 --steps 24 --orbit-samples 2048 \
  --upper-GeV 10000 \
  --output-dir work/gateC4_55channel_running_unitarity_v1
\`\`\`

The user-supplied C3 AF run is complete and did not run C4 yet.
C4 reports \`summary.json\` and \`running_55channel_unitarity_NOT_ALLOWED.csv\`.
This remains an approximate, tree/one-loop, no-threshold theory screen,
not a global vacuum or full RG-consistent allowed-parameter fit. In
particular no full modern two-charged-state b→sγ, Barr–Zee LFV, CKM
meson FCNC, HiggsTools or charge-breaking global extrema constraints
have been applied to these 60 counterfactuals. Never label
“full Zee point allowed” based on C4 alone.



## C4 AF outcome (2026-10-19): complete running 55-channel scalar unitarity

The user-provided C4 stdout \`Pasted text (9)\` confirms **all 60 trajectories analyzed** with complete 55×55 high-energy scalar contact scattering, both 24- and 48-step integration, and previously certified C3 sampled-scale BFB.

\`\`\`text
Intervention                           tree BFB to 10 TeV   55ch unitarity to 10 TeV   combined
both_lh1_l1_1                          29/30                28/30                     28/30
both_lh0p4_l1_0p5                      29/30                29/30                     29/30
\`\`\`

**All 60 match-scale initial conditions pass tree unitarity**; all C4 outputs explicitly \`physical_allowed_UNKNOWN\`. With \`both_lh1_l1_1\`, B4_0000755 first crosses the *8π full scattering eigenvalue criterion* around **9338.5709 GeV**, despite its |lambda|<4π and BFB tests passing up to 10 TeV. With B4_0000827, the full scattering eigenvalue crossing occurs around **4622.6779 GeV** in \`both_lh1_l1_1\` or **5532.3859 GeV** in \`both_lh0p4_l1_0p5\`; these are earlier than C2's already-known ~6.38/7.23 TeV quartic heuristic crossings. Other candidates satisfy all three one-loop/high-energy tree screening criteria at sampled scales to 10 TeV.

**Scientific interpretation:** Most of the original cascade-spectrum shortlist can be scalar-rescued, AND the complete scalar scattering matrix removes additional cases missed by the single-coupling heuristic. Neither this success nor its percentages are evidence of complete physical viability, because Type-II quark boundary CKM is toy, threshold matching is missing, and LFV, meson flavor, HiggsTools and the global vacuum have not been integrated.

## Gate C5: LARGE full tree Zee charge-breaking/CP/alternative-neutral vacuum search

A major remaining theoretical gap: running **quartic** BFB ensures V4 does not trend negative at large fields, but it does not ensure the **dimensionful** Zee scalar potential's physical electroweak stationary point is the deepest minimum. The Zee trilinear \`muZee Phi1^T epsilon Phi2 chi†\` can favor a charge-breaking vacuum even if V4 is BFB and all scalar scattering eigenvalues satisfy the 8π tree bound.

New driver: \`scripts/zee_gateC5_charge_breaking_vacuum_search.py\`; 16 regressions \`tests/test_zee_gateC5_charge_breaking_vacuum_search.py\`. Explore **30 B4 scalar mass spectra × 2 C2-rescued quartic potentials = 60** full 10-real-field renormalizable potentials at the *matching scale*. Each run uses **128 multistart seeds** + the EW reference and its signed partner (130 optimizations each, **7800 minimizations**), spanning neutral, charged-doublet, charged-singlet and mixed directions. Exact six-real-component gauge fixing \`Phi1=(0,v1)/sqrt(2)\`, \`Phi2=(u,v2+i v3)/sqrt(2)\` with real u using remaining QED phase, \`chi=(sR+i sI)/sqrt(2)\`, covers generic charge/CP-breaking orbits. The exact potential is evaluated using the independent ten-real scalar invariant/tensor representation with analytical gradients, and physical EW Hessian eigenvalues are compared to the expected three Goldstones plus seven real physical modes (125², heavy neutral², pseudoscalar², doubly degenerate charged H1/H2²). Scalar C2 reconstructed masses and B2 neutrino closure are rechecked. C4 report of all 60 scanned cases is required, with unchanged B4/B2/C2/C3 hashes.

**Crucial logical outputs:**
- \`EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS\`: a reproducible physical scalar field configuration has V(field) < V(EW) − 1e−6 v⁴, which unambiguously disproves the EW vacuum being the **global tree-level** minimum (though whether the EW state can be long-lived metastable is a separate question).
- \`NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE\`: large multistart search found nothing deeper; **not** a global-minimum mathematical proof, and not a label of physical acceptance.
- \`EW stationary or physical mass-squared Hessian closure failure\`: fail closed; do not search an incorrectly matched potential.

**ONE AF run, fresh output directory, no RGE regeneration:**

\`\`\`bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_gateC5_charge_breaking_vacuum_search.py' -v &&
python3 -u scripts/zee_gateC5_charge_breaking_vacuum_search.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --b2-json work/gateB4_zee_adaptive_pilot/B2_flavour/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --c2-summary work/gateC2_paired_uv_rescue_v1/summary.json \
  --c3-summary work/gateC3_running_complex_bfb_v1/summary.json \
  --c4-summary work/gateC4_55channel_running_unitarity_v1/summary.json \
  --max-spectra 30 --multistart 128 --maxiter 1000 \
  --seed 20261019 \
  --output-dir work/gateC5_charge_breaking_vacuum_v1
\`\`\`

Report: \`summary.json\`, \`charge_breaking_vacuum_screen_NOT_ALLOWED.csv\`. Interpretation: if explicit deeper potential witnesses appear, they are robust objections to **global EW vacuum** for those points (not lifetime/metastability exclusions). If none are found, next upgrade is a complete set of all polynomial stationary points or independently certified global optimization. Quantitative Paper 1 physics still depends on full neutrino/LFV, CKM matched b→s gamma, HiggsTools and consistent threshold schemes; no allowed Zee point established.



## C5 AF result: 4 explicit deeper charge-breaking vacuum witnesses in 60 model potentials

User ran all **60 C5 multistart scalar minimizations**, using **130 minimizations per potential** (128 generated + 2 EW reference orientations = **7800 total**). All report \`C5_PHYSICAL_ZEE_ALLOWED UNKNOWN\`. Four **explicit deeper charge-breaking** configurations were identified, affecting two distinct B4 spectra and BOTH paired scalar-quartic counterfactuals:

\`\`\`text
B4_0000822 both_lh1_l1_1       ΔV/v^4 = -1.3508153892822872
B4_0000822 both_lh0p4_l1_0p5   ΔV/v^4 = -5.365828674616401
B4_0001150 both_lh1_l1_1       ΔV/v^4 = -0.2056624990629435
B4_0001150 both_lh0p4_l1_0p5   ΔV/v^4 = -3.253198537566649
\`\`\`

These are **far beyond numerical noise** (the numerical-optimization acceptance/witness threshold is 1e-6 v^4), so they are robust counterexamples to GLOBAL EW tree-potential minimality (though no metastable lifetime is computed). The other 56 cases found no lower potential within finite multistart search, which is NOT rigorous global-vacuum certification. In addition, first C4 variant fails the full running unitarity for B4_0000755, and BOTH variants fail for B4_0000827. Therefore \`C4_pass && no_C5_deeper_witness_found\` is **26/30** first variant and **27/30** second, but **neither count measures physically allowed points**. These 53 potential realizations correspond to 27 unique scalar spectra; shared spectra across variants and shared B2 Yukawa families should not be double-counted. Note that C5 is matching-scale *tree-level* vacuum only, not a loop-corrected or running vacuum analysis. The reported minimum energy differences are physical scalar potential comparisons within the fixed model convention; no off-shell gauge loop-correction claims.

**Scientific takeaway:** Previously unexamined dimensionful Zee interactions make charged-breaking minima an independently relevant restriction: quartic positivity and complete 55-channel unitarity alone did NOT identify B4_0000822 or B4_0001150.

## Gate D1 — one large neutrino/LFV partial-amplitude audit over all 300 B2 solutions

Next shift to FLAVOR physics (rather than serial additional scalar checks).

Files:
- \`scripts/zee_gateD1_joint_300_neutrino_lfv_inventory.py\`
- \`tests/test_zee_gateD1_joint_300_neutrino_lfv_inventory.py\` (15 regression methods).

Use ALL TEN complex neutrino-family matrices (f,Y) for EACH of the same 30 B4 spectra = **300 independent saved f/Y configurations**, not 600 points because paired C2 potential interventions leave physical masses, alpha/beta/gamma and *current implemented* LFV amplitudes unchanged. The C2-based scalar potentials are reconstructed, C5 60-point outcomes and C4 55-channel theory flags imported with exact B4/B2/C2/C3/C4/C5 source hashes. Scalar-theory preselection remains a **screen**: the union has 27 unique spectra with both/one potential having successful running theory and NO OBSERVED deeper C5 witness; two spectra have definite C5 tree charge-breaking witness, one has C4 10 TeV failure in both variants.

For EVERY neutrino-family solution, re-evaluate mass-matrix closure, coherently sum full currently implemented **one-loop** scalar dipoles (\`h,H,A + physical charged-doublet Y + charged-singlet f\`), add validated-but-incomplete **fermion-photon Barr-Zee** top/bottom/tau subset in the same external chirality and phase convention, and compute neutral tree-only \`mu->3e\`, \`tau->3e\`, \`tau->3mu\`, \`tau->mu ee\`, \`tau->e mumu\` and f-only charged current lepton-universality shifts. Individual one-loop scalar BR must numerically reproduce source B2 saved values; fail closed on numerical/provenance/normalization mismatches. Re-rank ten solutions per spectrum by the largest of the three partial radiative (one-loop + fermion-photon BZ coherently combined) ratio-to-reference-experiment bound and the five tree-only 3-body ratios. This is a **cohort priority score and NOT an experimental exclusion/pass**. Re-rank even if the B2 partial-only initial ranks are different; compare the influence of fermion-photon BZ amplitudes. All physical LFV, modern B->Xs gamma, CKM and running quark masses, HiggsTools, global vacuum and physical viable state stay NOT COMPUTED/UNKNOWN.

**One AF command** (output dir MUST be new):

\`\`\`bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_gateD1_joint_300_neutrino_lfv_inventory.py' -v &&
python3 -u scripts/zee_gateD1_joint_300_neutrino_lfv_inventory.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --b2-json work/gateB4_zee_adaptive_pilot/B2_flavour/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --c2-summary work/gateC2_paired_uv_rescue_v1/summary.json \
  --c3-summary work/gateC3_running_complex_bfb_v1/summary.json \
  --c4-summary work/gateC4_55channel_running_unitarity_v1/summary.json \
  --c5-summary work/gateC5_charge_breaking_vacuum_v1/summary.json \
  --solution-limit 10 \
  --output-dir work/gateD1_joint_300_neutrino_lfv_v1
\`\`\`

Outputs:
\`summary.json\` complete 300 per-solution partial LFV diagnostics, with explicit missing-physics flags; \`incomplete_flavor_diagnostics_300_NOT_ALLOWED.csv\` 300 flat rows; \`spectrum_flavor_shortlist_NOT_ALLOWED.csv\` 30 independently re-ranked spectra. No updated experimental limits are claimed, all experimental reference 90% limits are pinned to existing source code and must be checked before publication.

The ultimate Paper 1 viability problem remains open. If all sampled B2 families have severe partial flavor tension, do not conclude general Zee excluded: these were only 300 PRE-RANKED restricted B2 samples with fixed central NO neutrino target, not globally fitted Yukawas. Next substantive work would be completing *missing dipole/3-body/conversion amplitudes*, then a proper global fit optimized over neutrino flavor while simultaneously imposing quark precision and Higgs constraints. Stop adding new RGE source checks unless new physics identifies a bug.
