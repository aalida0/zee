# Public-code reuse audit for finishing the Zee scan workflow
**Date:** 2026-11-06. **Task:** Audit/adapt public tools BEFORE implementing additional flavor, vacuum or Higgs calculations.
**Status:** SOURCE_IDENTIFIED / MODEL_ADAPTER_NOT_VALIDATED. None of these packages is already a validated complete Zee Type-II implementation or a waiver of a missing theory uncertainty.
**One final scan policy:** No new physics proposals, benchmark production campaigns, Condor submissions, or pilot scans. Only read-only inspection, bounded existing-point comparisons, tests and code integration until the user separately authorizes the final scan.

## Highest-value direct source discovery: two-loop general-2HDM LFV

**Altmannshofer, Assi, Brod, Hamer, Julio, Uttayarat & Volkov**
- *Electron EDM and Gamma(mu -> e gamma) in the 2HDM*, JHEP 06 (2025) 156, arXiv:2410.17313.
- **2026 erratum**: JHEP 07 (2026) 184, https://doi.org/10.1007/JHEP07(2026)184. INSPIRE documents corrections affecting mu->e gamma and tau->(e/mu) gamma; earlier equations 5.7 and 5.8 needed correction.
- Source: https://gitlab.com/jbrod/general-2hdm-pheno ; `thdm.py`, `example.py`, `README.md`; observed repository latest short commit `b5035cd5` ("Corrected further errors in l -> l' gamma Wilson coefficients"), Apache License 2.0 as linked by GitLab. **Pin full SHA locally, verify repo/erratum alignment**, and run its original self-test/examples.
- Supports up-to-two-loop radiative LFV and electron EDM for a general *two-Higgs-doublet model* with generic Yukawa matrices. **Not a complete Zee calculator**: its model has one charged scalar, not the Zee charged-singlet + two mixed charged eigenstates and antisymmetric Zee singlet-lepton Yukawa F.
- **Action**: inventory individual gauge-invariant diagram classes; identify any rigorously portable neutral-fermion Barr-Zee and other subsets, including corrections. The 2HDM result has gauge-dependent subsets if charged loops are arbitrarily omitted; do NOT splice cherry-picked terms. Require identical potential/couplings/conventions, proper charged-scalar modifications and gauge consistency. Validated 2HDM restriction and Zee decoupling limit first. If impossible, use only as reference/control and mark missing Zee amplitudes UNKNOWN.
- Do not cite "complete two-loop Zee mu->e gamma" or "solved full LFV" based on this package.

## High-value LFV automation: current SARAH model + SPheno/FlavorKit

- SARAH https://sarah.hepforge.org/ ; official MakeSPheno source workflow. Read FlavorKit paper W. Porod, F. Staub, A. Vicente EPJC (2014) https://doi.org/10.1140/epjc/s10052-014-2992-2
- FlavorKit package provides generic LFV Wilson coefficients and observables through 1 loop, including mu->e gamma, tau radiative decays, mu->3e, mu-e conversion. PreSARAH + FeynArts/FormCalc can customize operators/observables.
- Standard model generation: `Needs["SARAH\`"]; Start["ZeeTypeII"]; MakeSPheno[]` within an isolated installed source checkout. Exact generated SPheno/SLHA conventions and supported SARAH 4.15.4 model features **must be checked**. No successful Zee SPheno run is assumed.
- **Action**: run an isolated non-scan smoke test on a prior frozen Zee point (from existing validated cards). Verify spectrum/charged mixing/neutral scalar masses, complex lepton Yukawas, neutrino one-loop mechanism, and lepton dipole amplitude/W and Goldstone completeness. Compare rate/coefficients against existing Module4 on one frozen card, including gauge and chirality checks. Broader LFV coverage requires dedicated checks of each operator and decay scheme.
- FlavorKit SPheno quark B->Xs gamma uses its own rate prescription and cannot certify the 2026 Misiak Eq.(4) omitted curvature/NLO error.

## High-value vacuum tools: Vevacious++ + certified polynomial roots

- Vevacious++ development repo: https://github.com/jwittbrodt/VevaciousPlusPlus_Development or https://github.com/JoseEliel/VevaciousPlusPlus_Development . Source README specifies SARAH model export `MakeVevacious[Version->"++"]`, which generates the model-specific `.vin` potential and `ScaleAndBlock.xml`, with input LHA model parameters. Its included THDM example is *not* Zee. License GPLv3.
- Code uses homotopy continuation (PHC/HOM4PS2) for stationarity candidates, numerical minimization and tunneling methods. A numerical search can find deeper vacua and estimate metastability **but non-discovery is not a sufficient proof of the global minimum**.
- HomotopyContinuation.jl https://github.com/JuliaHomotopyContinuation/HomotopyContinuation.jl ; https://www.juliahomotopycontinuation.org/HomotopyContinuation.jl/stable/certification/ . Its `certify` uses interval/Krawczyk checks for given nonsingular polynomial roots; license MIT. **Certification of found roots != certification of exhaustion of all stationary solutions**, especially singular/positive-dimensional cases and gauge-orbit zero modes.
- **Action**: export correct full real-field Zee potential including charged and CP-violating directions, gauge-reduce where justified. Compare P(x) and derivatives against frozen Module1/D10 at existing points. Test independently first on one D10 PASS and one D10 UNKNOWN, with sign, gauge-orbit and energy/witness polish. A successful discovery of a truly deeper vacuum is meaningful FAIL evidence; a missed discovery alone remains UNKNOWN. Keep a robust hash-addressed optional backend; do not replace the sufficiency gate silently.
- BSMPT https://github.com/BSMPT/BSMPT supports custom models with generator scripts, temperature-dependent one-loop minima and phase transitions. **No built-in Zee model**. More model implementation effort; lower priority for the current tree-vacuum gate.

## Higgs and decays: exploit existing HiggsTools and SPheno

- HiggsTools docs https://higgsbounds.gitlab.io/higgstools/ , notably https://higgsbounds.gitlab.io/higgstools/alternative_input.html . `Higgs.tools.Input.predictionsFromDict` can receive explicitly calculated masses, BR, cross sections and effective couplings. HiggsPredictions/HiggsBounds/HiggsSignals are already in D14; **do not replace them**.
- SARAH/SPheno automated 1-loop two-body widths: Goodsell, Liebler, Staub, arXiv:1703.09237 (full one-loop decays in many supported models). Possible improved `h125 -> gamma gamma` charged-loop input and additional neutral/charged widths; **must validate full Zee content and conventions** against existing tree D4, SARAH UFO, Ward relations and scheme.
- Existing 16 exact real H2 13-TeV and 3 exact 14-TeV LO production runs are validated; do NOT rerun them. Charged HiggsTools limits need H1/H2 production and complete width inputs. Unsupported production modes remain NOT_EVALUATED.
- SusHi or other 2HDM neutral production software would need actual matched Zee doublet-sector couplings and neutral spectrum; do not treat complete-model correspondence as automatic.

## Independent one-loop cross-check: MARTY

- MARTY https://github.com/docbrown1955/marty-public GPLv3; computes generic 1-loop amplitudes and Wilson coefficients and generates independent C++ numerical libraries; its own 2HDM sample provides a technical precedent.
- Potentially useful for one-loop LFV or dipole cross-checks when FlavorKit generated calculations fail, **but requires a separate correctly defined Zee model** and cannot solve 2026 B->Xs gamma higher-order rate uncertainty or two-loop Zee Barr-Zee by itself. Avoid maintaining two full symbolic models unless an actual physics discrepancy justifies it.

## Existing b->s gamma tools: do NOT restart a failed search

- Already used EOS 1.0.21, flavio/wilson, HyperIso 1.0.3, SuperIso 5.0 and inspected HEPfit. Technical LO/NLO Zee matching/RG and partially matched diagnostics are frozen. The 2026 Misiak et al. formula arXiv:2608.29863 Eq.(4) is **linear** in LO `DeltaC7, DeltaC8`; its public material does NOT provide a justified generic joint nonlinear Zee rate/error domain. Do not transfer 2HDM Type-II's 670-GeV one-Higgs result.
- No newly source-verified public turnkey executable supplying the **exact 2026 full joint high-scale `DeltaC4/7/8` nonlinear response and NP theory uncertainty** was found in this audit. Legacy backend spread is NOT a theory sigma. Keep `bsg_physical_status=UNKNOWN` and its clearly labelled published LO-NP *conditional* reference diagnostic in the final workflow.

## Orchestration and collider statistics (secondary)

- BSMArt v2 https://goodsell.pages.in2p3.fr/bsmart/ provides glue for SARAH, SPheno, HiggsTools and Vevacious++, among others. Our D14 Condor/manifest/receipt orchestration is already validated; borrow *backend adapter conventions* only. DO NOT replace the scanner or run BSMArt scans.
- MadAnalysis 5 https://github.com/MadAnalysis/madanalysis5 , CheckMATE2 https://github.com/CheckMATE2/checkmate2 , and pyhf https://github.com/scikit-hep/pyhf support a **later separate** detector-level reinterpretation/statistical sensitivity study. None generates a signal/background acceptance merely from the 16 cross sections. No detector analysis now.

## Zero-scan code-only plan for Codex

1. Make an `EXTERNAL_CAPABILITY_MATRIX` with exact backend output, Zee-specific completeness, source version/license, dependencies, input basis, precision and uncertainties.
2. Implement a **research-only** `tools_available` / `probe` interface or version-pinned backend templates where helpful. No package is mandatory to run the existing conditional D14 workflow.
3. Prioritize *one* isolated integration spike: **general-2HDM two-loop Python LFV, corrected 2026 revision**, **or** **SARAH/SPheno/FlavorKit**. Test with a preexisting benchmark and literature limiting case; report `COMPATIBLE_SUBSET_ONLY` or `UNVALIDATED` if model-specific missing amplitudes remain. Do not silently change current LFV status.
4. A parallel independent bounded vacuum-method check may use SARAH `MakeVevacious[Version->"++"]` or HomotopyContinuation, **without running a new scan**. Require full field-space scope and source/control validation; unknown remains unknown.
5. For the remaining Higgs h125 loops, prefer to calculate and feed **explicit** correctly normalized Zee predictions to the existing HiggsTools adapter rather than alter its interpretation.
6. External tool binaries/sources and large artifacts stay in ignored local/ and are version/SHA pinned; respect GPL/Apache/MIT licenses, no copying GPL code into user project.
7. After source and smoke tests, integrate only independently verified observable components with exact per-operator coverage status; preserve original frozen Modules0–13, D14 evidence, old tests and `global_acceptance=null`. Document missing calculations before the final **single** scan.

**Do NOT call a package available merely because it is named.** A correct external model implementation, benchmark/sign/normalization comparison and coverage assessment are prerequisites to an operative constraint.
