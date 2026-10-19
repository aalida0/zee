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
