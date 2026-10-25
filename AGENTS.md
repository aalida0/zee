# Zee Module 5 — Type-II quark flavor: B -> X_s gamma, Gate A only

## Identity, branch, and scientific scope
Work only on `feature/zee-bsgamma-module5` of `aalida0/zee`, branched from `22d249fb57d55a88b266b69d1575be66ec7209b3`. The preceding Module 4 amplitudes remain PARTIAL and the Wgamma matching remains BLOCKED. This task **does not fix Module4**; it starts the **quark-flavor validation** essential for the first Zee phenomenology paper.

Implement and independently validate the **charged-scalar leading-order matching-scale shifts Delta C7 and Delta C8 for the TWO physical charged Higgs bosons**. Do NOT compute B->Xs gamma branching ratios, exclusions, full NLO/NNLO, multiscale QCD evolution, or global viability in this task. The existing historical `reference/` calculations are unvalidated inspiration only, not physical acceptance evidence.

## Read only these first
- `module5/bsgamma_lo.py` (prewritten production implementation).
- `tests/test_module5_bsgamma_lo.py` (prewritten independent 90-digit mathematical tests).
- `module5/example_bsgamma_input.json` (illustrative input).
- `module4/couplings.py` (charged-scalar rotation and frozen Type-II Yukawa context).
- Relevant frozen model in `models/SARAH/ZeeTypeII/` only as necessary.
- Historical `reference/` only for a specific cross-code comparison, not as a source of truth.

Do not scan the entire repository unnecessarily. No changes to frozen Modules 0–4, `models/SARAH/ZeeTypeII/`, their established tests, or previous validation. Do not touch another working directory or main. Old branch-bound test runners are not valid on this isolated branch; run focused Gate A tests.

## Pinned physics definitions and primary literature
**Use the following exact conventions, and independently verify them.**
- SuperIso 3.4 paper, Mahmoudi, arXiv:0808.3144, Appendix C.1.2, Eqs. (47)–(49):
  https://superiso.in2p3.fr/superiso3.4.pdf
- Florentino, Romão and Silva, EPJC 81 (2021) 1148, DOI 10.1140/epjc/s10052-021-09956-2, Appendices B.3 and C:
  https://link.springer.com/article/10.1140/epjc/s10052-021-09956-2
- The Zee model has Type-II QUARK couplings. The doublet charged component mixes with the charged singlet. Florentino B.9 gives
  `X=(tan(beta)*cos(gamma),-tan(beta)*sin(gamma))`;
  `Y=(cot(beta)*cos(gamma),-cot(beta)*sin(gamma))`.
  Therefore `|Y_a|^2=(cot(beta))^2*w_a`, `X_a*conj(Y_a)=w_a`, with `w=(cos(gamma)^2,sin(gamma)^2)`.
- In the SuperIso convention (lambda_tt=cot(beta), lambda_bb=-tan(beta)), at LO the charged-scalar matching contribution is
  `Delta C7,8 = sum_a [(|Y_a|^2/3) F7,8^(1)(x_a) + (X_a Y_a*) F7,8^(2)(x_a)]`,
  `x_a = [m_t_MSbar(mu_match)/m_Ha]^2`. **Check the sign and operator normalization** against BOTH sources; do not conflate with the 2017/2021 branching ratio or an effective low-scale coefficient.
- The four F functions are explicitly programmed from SuperIso Eq.49. The near-x=1 Taylor expansions were derived independently and should be checked against 90-digit evaluation. Do not infer new charged Higgs lower mass bounds or experimental likelihoods from LO matching.
- This task requires **explicit** top MSbar mass at the user-supplied matching scale, no pole-mass substitutions or guessed running. A single matching scale for both mass eigenstates is an LO fixed-order approximation; flag this limitation.

## Work required
1. Independently audit the prewritten code and tests for algebra, source signs, convention, floating stability, complex/chirality issues, basis/mixing, and fail-closed input. Fix actual errors. Independently compare frozen SARAH quark charged vertices or frozen model quark/charged-scalar rotations to the X,Y mapping before declaring full Gate A verification. If native Mathematica/SARAH calculation is not feasible locally, use the explicit frozen model and source as a scoped check; clearly identify what was NOT freshly validated.
2. Run `python -m unittest discover -s tests -p 'test_module5_bsgamma_lo.py' -v`. Confirm 90-digit source evaluations across small, near-degenerate, large x; x=1 analytic limits; gamma=0 single-2HDM case; gamma=pi/2 singlet/doublet assignment; swapped spectra; equal charged masses; tanbeta dependence; heavy decoupling; missing/NaN/invalid scheme inputs. Expand tests only if a real gap is identified.
3. Run a real CLI smoke test:
   ```bash
   mkdir -p validation/module5/local
   python module5/bsgamma_lo.py --input module5/example_bsgamma_input.json --output validation/module5/local/bsgamma_LO_example.json
   ```
   Do not claim that 550/900 GeV illustrative fixture is an accepted benchmark.
4. Create `validation/module5/STATUS.md`, concise `validation/module5/results.json`, and `module5/CONVENTIONS.md` with inputs, equations, residuals, source links, known limitations, source/provenance SHA256, and next milestone. Reproducible numerical results MUST come from actual runs; keep raw logs/cache ignored locally. Reference model cross-checks and exact version/commit.
5. Specifically compare to Florentino 2021: the mixing-weighted C7, C8 treatment **already exists**, so do not claim it as new. The novelty later requires *full general Zee lepton/neutrino constraints plus collider correlations*, and that cannot be inferred from Gate A.
6. Evaluate which subsequent **well-scoped** Gate B is necessary for a physically defensible B->Xs gamma observable: consistent scale/mass/Yukawa treatment, NLO/NNLO SM+NP matching, QCD running and experimental covariance. Distinguish math-matched coefficients from physical prediction. If this exceeds available tools, flag the blocker rather than applying an approximate 'type-II 580 GeV' mass cut.

## Completion contract
- Do not change physical coefficients in Modules 0–4. No silent historical changes.
- Tests and actual independent source/mathematical comparisons must pass for `VALIDATION_PASS_LO_MATCHING`; otherwise mark `PARTIAL/BLOCKED`.
- Always output `LO_MATCHING_ONLY_NOT_BR_OR_EXCLUSION`, no unsupported exclusion/allowed claims.
- Commit only scoped `module5/`, `tests/test_module5_bsgamma_lo.py`, `validation/module5/`, and this AGENTS.md if amended.
- `git push origin feature/zee-bsgamma-module5`.
- Verify `git rev-parse HEAD` = `git ls-remote origin refs/heads/feature/zee-bsgamma-module5`.
- Report commit SHA and canonical GitHub URL, tests, numerical residuals and scope limitations. If push fails report PUSH_BLOCKED.
- Keep Codex chatter brief; place detail in audit files. Preserve exact code and source hashes. Never claim delivery without a verified remote commit.
