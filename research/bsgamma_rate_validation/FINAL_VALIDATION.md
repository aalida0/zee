# Final physical-rate validation — 2026-11-06

**BSG_PHYSICAL_ACCURACY_BLOCKED. ACCURACY_DOMAIN_UNKNOWN.** No exclusion use, theory sigma, likelihood or scan filter is supplied. Masses below 1 TeV remain **UNKNOWN**; these tests neither exclude nor certify them. Modules 0–14 and prior evidence are unchanged.

## What was established

Twenty predeclared Stage A diagnostics executed with EOS 1.0.21 and a freshly built exact replay of the frozen D9B SuperIso 5.0 patch. An original, unmodified SuperIso build also executed its standalone Type-II path. These are actual physical-rate kernel calls, not a new matching calculation. The successful native EOS evolution at `3207b6d` is reused unchanged.

Published-reference reproduction: **NOT_EVALUATED / no qualified matched reference obtained**. Independent kernel implementations executed: **YES**. Matched independent physical-rate agreement: **NOT_EVALUATED**. Prior upstream self-regressions: preserved, distinct from both claims. No numerical discrepancy below is a backend failure or an uncertainty estimate.

## Source qualification (Stage A hard gate)

- [Borzumati–Greub v1](https://arxiv.org/html/hep-ph/9802391v1), Sec.3.3 Eqs.(31)–(39), Sec.4 Eq.(40), Sec.4.3 Figs.5–6, Appendix F Table 1: useful historical card, but an uncut rate, explicitly truncated amplitude square and semileptonic normalization. Its Type-II rates are curves; no exact one-state numerical oracle was extracted. The actual EOS uncut call throws its documented cut-domain exception.
- [Published addendum, hep-ph/9809438v1](https://arxiv.org/html/hep-ph/9809438v1), Eq.(1)/Fig.1: changes electromagnetic coupling and QED corrections. Its numerical SM reference and exclusion contours do not supply a matched one-state rate.
- [Hermann–Misiak–Steinhauser v2](https://arxiv.org/html/1208.2788v2), Sec.3 Eq.(42), Figs.5–6: specifies scales/cut and updated top/QCD inputs, inherits other inputs from cited works and supplies curves/approximate enhancements. Its NNLO charged-Higgs prescription differs from this EOS prototype. No digitization was used.
- [2026 Letter v1](https://arxiv.org/html/2608.29863v1), Sec.IV Eqs.(3)–(4)/Fig.3, and [companion v1](https://arxiv.org/html/2608.29864v1), Sec.3/Apps.A–C: updated SM framework and a generic LO-NP linear formula, with quadratic terms omitted. The displayed formula gives no quantitative finite generic-NP validity domain. The Type-II curve includes higher-order matching. They do not validate this nonlinear EOS prescription.

Abstract submission histories were checked on 2026-11-06 (BG/addendum v1, HMS v2, Letter/companion v1). Exact downloaded-byte hashes, source locations, historical input values and missing pieces are in [final_sources.json](final_sources.json). No claim is made that no suitable benchmark exists elsewhere. The earlier backend inventory and modern supplementary-data audit remain authoritative; no speculative HEPfit rebuild or EOS upgrade was needed to resolve a demonstrated issue.

## Comparison card: matched and different inputs

All new cross-kernel rows use mu0=160 GeV, mu_b=4.2 GeV, E_gamma>1.6 GeV. Independent frozen BMU matching uses the SuperIso running top 163.16587299291515 GeV and alpha_s(mu0)=0.10877484993481065. NP is added to the SM once. The two states are combined at coefficient level once. The comparison is deliberately **PARTIALLY_MATCHED**, not a physical-validation PASS.

| Ingredient | EOS–SuperIso comparison | Status |
| --- | --- | --- |
| Scalar masses, tanbeta, Yukawa sign, mixing weights | Same raw ordinary LO/NLO matching vector | MATCHED |
| mu0, mu_b, physical photon cut | 160, 4.2, 1.6 GeV | MATCHED |
| SM and NP low total ordinary C1–C8 | SuperIso order-separated output collapsed as C0 + alpha_s(mu_b)/(4pi) C1; effective maps inverted once before EOS input | MATCHED numerical vector |
| Primary low mass/QCD parameters | alpha_s(MZ)=0.118, MZ=91.188, mb(mb)=4.183, mc(mc)=1.273 GeV | MATCHED primary values |
| Derived alpha_s(4.2) | EOS 0.22479162785589887; SI 0.22469749369105324 | DIFFERENT running prescription |
| Pole bottom / charm in matrix elements | EOS mb_pole=4.722731906637331, mc(4.2)/mb(4.2); SI mb_pole=4.787498930616556, mc(mu_c=2)/[mb(mb)+0.37] | DIFFERENT mass prescription |
| CKM absolute normalization | EOS |Vts Vtb|^2=0.0016954211353262245; SI 0.0016861847239212709 | DIFFERENT defaults, recorded |
| Leading EM factor | Both 1/137.036 (explicit EOS parameter override) | MATCHED factor |
| Additional QED terms | SI leading QED correction retained; no corresponding identical EOS configuration established | DIFFERENT |
| Rate normalization | EOS GF^2 mb_pole^3 mb(mu_b)^2 times measured lifetime/hbar; SI measured semileptonic BR times its kinetic normalization | DIFFERENT, no fitted conversion |
| Perturbative counting | SI explicit NLO numerator P2=0; EOS total-coefficient amplitude square/exponential bremsstrahlung | DIFFERENT |
| HQE / resolved photons | Existing distinct backend power prescriptions; complete matched treatment unavailable | DIFFERENT / missing coverage |

EOS parameters not explicitly overridden keep the pinned defaults; their fingerprint and all overrides are recorded. No normalization is tuned. The separate EOS-evolved NP vector uses the same endpoint alpha_s values as SI; differences in low coefficients are recorded as diagnostics only, without reopening the solved evolution. Identical low-vector rate calls isolate the remaining kernel/prescription differences.

## Executed benchmark residuals

All rates and signed differences in this table are in units of **10^-4**. EOS below means the shared SuperIso low-vector/partial-card experiment, not the native EOS default prediction. delta residual = [BR_NP−BR_SM]_EOS − [BR_NP−BR_SM]_SI. Every row is DIAGNOSTIC_ONLY; agreement is NOT_EVALUATED.

| Case | SI BR | EOS BR | EOS−SI | delta residual |
| --- | ---: | ---: | ---: | ---: |
| zero_NP | 3.425772425 | 3.222338578 | -0.203433847 | 0.000000000 |
| M550_tb2 | 4.037209600 | 3.784142990 | -0.253066610 | -0.049632763 |
| M550_tb5.3 | 4.021701163 | 3.769848270 | -0.251852894 | -0.048419047 |
| M550_tb50 | 4.019157681 | 3.767504027 | -0.251653654 | -0.048219807 |
| M900_tb2 | 3.729518128 | 3.500476816 | -0.229041312 | -0.025607465 |
| M900_tb5.3 | 3.723128811 | 3.494606679 | -0.228522132 | -0.025088285 |
| M900_tb50 | 3.722080309 | 3.493643411 | -0.228436898 | -0.025003051 |
| decoupling_100TeV | 3.425805364 | 3.222366181 | -0.203439182 | -0.000005335 |
| opposite_coupling_control | 2.873122415 | 2.723064388 | -0.150058028 | 0.053375820 |
| gamma_zero | 4.021701163 | 3.769848270 | -0.251852894 | -0.048419047 |
| two_state | 3.786140373 | 3.552577690 | -0.233562683 | -0.030128836 |
| gamma_half_pi | 3.723128811 | 3.494606679 | -0.228522132 | -0.025088285 |
| equal_mass | 4.021701163 | 3.769848270 | -0.251852894 | -0.048419047 |
| interchange | 3.786140373 | 3.552577690 | -0.233562683 | -0.030128836 |
| C4_-1 | 3.385874929 | 3.182293883 | -0.203581046 | -0.000147199 |
| C4_+1 | 3.465669922 | 3.262696513 | -0.202973409 | 0.000460438 |
| C7_-1 | 3.519404213 | 3.307167457 | -0.212236756 | -0.008802908 |
| C7_+1 | 3.333323248 | 3.138643505 | -0.194679742 | 0.008754105 |
| C8_-1 | 3.447107014 | 3.242479547 | -0.204627467 | -0.001193620 |
| C8_+1 | 3.404519713 | 3.202278275 | -0.202241438 | 0.001192409 |

At 550 GeV, tanbeta=5.3, NP shifts are 5.47509691280983e-5 (EOS) and 5.95928737997420e-5 (SI), a signed shift difference −4.84190467164375e-6. This cannot be assigned as a missing-order sigma or used to calibrate the SM central value.

The original upstream standalone SM and Type-II legacy rates are respectively 3.34908322996573e-4 and 4.04960267817755e-4 at the same scales/cut. Their original matching defects and different retained order are already audited; they are diagnostics only. Original/patched SuperIso share a kernel and are not counted as independent implementations of one another. EOS supplies the independent implementation in the comparison above.

All twelve gamma-endpoint/equal-mass/interchange rate residuals (two EOS paths and SI) are exactly zero in this run. The 100-TeV point is a decoupling diagnostic, not a high-log precision result. Coherent coefficients and a weighted sum of rates differ, as expected.

Independent signed high-scale physical steps ±0.01 were applied to C7_LO, C8_LO and alpha_s(mu0)/(4pi) C4_NLO_raw. The latter is an artificial diagnostic, not a Zee parameter point. At this counting C4 starts at NLO: SI has zero even C4 response within roundoff, whereas EOS retains an even response 1.56619326759544e-8. This is direct evidence that supplying the same numerical total coefficients does not give the same perturbative prescription. It is not evidence that either result is a uniformly matched NLO prediction.

The archived native-EOS default benchmark 3.70865222239525e-4 is preserved unchanged. Only the two missing native default minimal cases were added: (550 GeV, tanbeta=50) 3.93173844289631e-4; (900 GeV, tanbeta=2) 3.65458874699652e-4. Together with bridge_results.json these complete the requested native one-state set.

## Tolerances and stopping decision

[final_card.json](final_card.json) was written before the numerical comparisons. Identity tolerance is 2e-15 absolute BR; identical-vector tolerance is 2e-12 per coefficient. These are numerical integrity tolerances only. A fully matched published x.xx times 10^-4 rate would allow 5e-7 rounding tolerance, before adding any independently justified theoretical tolerance. No physical-rate threshold is assigned to the incompatible prescriptions above. Upstream self-regression PASS is not promoted to physical agreement.

Ingredient status: frozen NP matching is LO+NLO QCD in the ordinary basis; EOS native evolution uses its existing gamma0/1/2 routine with the previously tested NP NLO projection and induced four-quark coefficients. EOS low-scale matrix elements are NLO-labelled, with retained higher-order square/bremsstrahlung terms and legacy SM matching/HQE normalization. This is neither uniform NLO NP nor the 2026 NNLO SM calculation. No isolated alpha_s^2 term was removed from EOS.

**Stage B/C: NOT_EVALUATED under the Stage A hard gate.** No scale envelope, mass/QCD uncertainty, finite theory domain, covariance, statistical test, sub-/super-TeV scan grid or filter was fabricated. Matching/RG/kernel truncation, cutoff, Wilson-dependent resolved photons, primed/finite-ms/light-quark effects and enhanced down Yukawas still lack jointly validated bounds. A small physical C4 effect or one measured curvature does not bound them. The published SM/experiment errors are not an NP error budget.

## Smallest missing input and two practical alternatives

The smallest next input is one independently executed, source-qualified one-charged-Higgs numerical BR card at a finite supported cut, with its SM BR, delta BR, order-separated coefficients, precise observable truncation/normalization, power/QED treatment and numerical accuracy. EOS needs an existing supported prescription that can reproduce that card. This is a physical-kernel/order issue, not a matching/RG blocker.

1. Obtain an author/maintainer reference card and an existing order-separated NLO rate interface for a legacy calculation. Reproduce zero NP and one finite charged-Higgs point before performing the planned finite scale/mass/HQE tests and withheld-point checks. A validated, conservatively bounded legacy-NLO domain could then support a restricted research filter without demanding NNLO NP everywhere.
2. Use the published 2026 LO-NP fit as a separate route after obtaining a quantitative coefficient-domain/remainder bound (or an author-maintained nonlinear response/executable) and the necessary input/nuisance covariance. Start with ordinary C7/C8 at 160 GeV and coherent Zee matching; explicitly bound omitted C4/higher-order/other-operator effects. This route is not currently a validated filter and must not be implemented by shifting EOS to 3.54e-4.

Neither route imposes the one-Higgs mass bound on each Zee charged state. D14 acceptance remains unchanged.

## Reproduction and checks

Use the pinned Python environment and native EOS wrapper already documented in README.md / BRIDGE.md. SuperIso is GPL-3.0-or-later, EOS GPL-2.0-only. Separate clients/binaries call each package; no combined binary or third-party source is committed. Complete archives, exact patch, source hashes, binary hashes, commands and local build logs are retained. Rebuilt static archive/binary hashes can vary by build metadata; source replay and numerical outputs provide the portable check.

```bash
curl -fLsS https://arxiv.org/html/hep-ph/9802391v1 -o research/bsgamma_rate_validation/local/bg9802391v1.html
curl -fLsS https://arxiv.org/html/hep-ph/9809438v1 -o research/bsgamma_rate_validation/local/bg9809438v1.html
curl -fLsS https://arxiv.org/html/1208.2788v2 -o research/bsgamma_rate_validation/local/hms12082788v2.html
curl -fLsS https://arxiv.org/html/2608.29863v1 -o research/bsgamma_rate_validation/local/misiak260829863v1.html
curl -fLsS https://arxiv.org/html/2608.29864v1 -o research/bsgamma_rate_validation/local/misiak260829864v1.html
curl -fLsS https://superiso.in2p3.fr/download/superiso_v5.0.tgz -o research/bsgamma_rate_validation/local/superiso_v5.0.tgz
research/bsgamma_rate_validation/local/venv/bin/python research/bsgamma_rate_validation/build_final_probes.py
research/bsgamma_rate_validation/local/venv/bin/python research/bsgamma_rate_validation/final_validation.py
research/bsgamma_rate_validation/local/venv/bin/python -m unittest discover -s research/bsgamma_rate_validation -p 'test_*.py' -v
git diff --check
```

The build always extracts fresh ignored directories; there is no need to delete or change historical builds. final_validation.py compiles the small EOS input inspector and checks source downloads, client/binary fingerprints and EOS defaults. It preserves all prior numerical files. New tests check signed perturbative bookkeeping, actual uncut rejection, coefficient/rate dataflow, identities, source integrity and the closed statistical gate. Actual test counts/log hash are in final_checks.json.
