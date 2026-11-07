# B→Xsγ feasibility gate — 2026-11-07

**B_FULL_RATE_BLOCKED.** Coherent two-charged-scalar central rates are
technically executable. A publication-grade exclusion with independently
validated normalization, perturbative accuracy and NP uncertainties is **not
established**. `physical_bsgamma=UNKNOWN`, `exclusion=null`,
`theory_sigma=null`, `global_acceptance=null`.

**Subsequent actual HEPfit execution:**
[HEPFIT_RATE_REPORT.md](bsgamma_hepfit/HEPFIT_RATE_REPORT.md) supersedes the
historical "not built/executed" HEPfit statements below. Pinned HEPfit now
compiles and executes 37 fixed-card/control processes (`HEPFIT_RUNTIME_PASS`,
`INDEPENDENT_RATE_EXECUTABLE`). The coherent NLO full-vector bridge passes
18 tests; published Type-II NNLO table interpolation is reproduced.
Same-order physical matching remains unestablished (`INDEPENDENT_RATE_MISMATCH`),
and `UNCERTAINTY_CALIBRATION_BLOCKED` prevents an exclusion. D7/F13 HEPfit
research NLO BRs are 4.17955384241e-4 / 3.83711422745e-4. Fresh SuperIso
executions reproduce the preserved D12 rates. The report gives shared-input/
shared-NP controls and a source-located normalization/perturbative/power
decomposition. No intercept or theory sigma is fitted. The original audit
and reused receipts below are retained as historical evidence.

This is a bounded source/archived-evidence audit, not a proof that a suitable
calculation is impossible. No rate backend was rebuilt or rerun, no new
parameter point was generated, and no LFV/Higgs implementation was started.
Original D12 rates and earlier matching/response controls are reused below.
The frozen conditional pipeline and separate flavor branch remain unchanged.

## Actual implementation findings

Version/source hashes, URLs, local replay locations and reused evidence commit
are in [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json). Line numbers below refer
to those pinned sources, not a moving development branch.

| Backend | Verified input and rate behavior | Decision |
| --- | --- | --- |
| SuperIso 5.0 official archive, 23 Nov 2025 | `predict.c` and `scan_coeffs.c` use nuisance/Wilson readers and the observable interpreter. `src/interpreter.c:263–275` evolves native matching, then adds `deltaC` to **low-scale effective LO** arrays and `deltaCp` to the primed array. These are not ordinary high-scale order-separated inputs. `bsgamma.c:682` independently rematches high-scale coefficients for power/QED terms. | Stock prediction/error interface cannot simply accept Module 5 ordinary NLO matching. Do not run `scan_coeffs` for this task. |
| SuperIso 5.0 with frozen D9B patch | Explicit ordinary NDR C^(0,1) arrays enter both evolution and the rate's high-scale reads; NLO numerator explicitly removes P2. Supports real, top-only, unprimed Q1–Q8 domain, including C4^(1). Source-dependent EM/power/semileptonic conventions retained. | **Primary research prescription**, already executable and internally checked. Physical uncertainty/exclusion gate remains closed. |
| HEPfit `322bd73a…` | `FlavourWilsonCoefficientMatching::CMbsg` adds only DC7g at LO (and DC7gp in the primed method); getters for C4/C8 do not make that route complete. **However**, `THDMMatching.cpp:97–132,360–379` fills all eight order-tagged entries, including C4 and effective dipole finite shifts. `bsgamma.cpp:2008–2032,2046–2112,2506–2515` consumes evolved order-separated coefficients and includes nonlinear terms. | A custom coherent C++ matching adapter is feasible in principle. No build, two-state execution, uncertainty calibration or independent physical reference was established here. Generic-interface limitation is not a package-wide impossibility. |
| flavio 2.7.1 / wilson 2.5.2 | `BR(B->Xsgamma)` uses a fixed 1.6-GeV CP-averaged rate, Q1–Q8/primed bilinears, numerical K1/K2 matrices and a tabulated SM vector. Public WET/flavio C7_bs/C8_bs are NP-only; the previously executed C4_bs initialization fails. `WETrunner` documents LO QCD/QED ADMs only. | Useful independent **dipole diagnostic**, not a full NLO C4/C7/C8 bridge. NLO matching added to LO evolution does not certify NLO NP accuracy. |
| EOS 1.0.21, reused independent check | Native full-vector evolution bridge and low-scale ordinary total-coefficient rate already executed on the separate branch; induced Q3–Q6 retained. Rate has its own normalization, mass scheme, power terms and retained higher-order squares. | **Independent kernel check**, already done; matched physical agreement remains unestablished. EOS v1.1 was source-inspected previously, not executed. |

SuperIso's rate includes LO squares and interference at NLO (lines 349–410),
legacy NNLO terms and a heuristic P2 drop (674). Its original charged-Higgs
matching had the documented initialization-cap and ordinary/effective-basis
defects; the frozen [D9B audit](../../module5/D9B_SUPERISO_REPAIR_AUDIT.md)
and patch fix the tested sector. An upstream NNLO label is not a certification
of arbitrary Zee coefficients, phases or the local repaired NLO prescription.
HEPfit also contains explicit unfinished general-primed terms; no general
complex/primed completion is inferred from its class interface.

## Precision and normalization that can actually be claimed

The selected research calculation is **leading electroweak, real top-only,
ms=0 charged-scalar matching through NLO QCD**, ordinary BMU/NDR matching,
NLO evolution and NLO perturbative numerator, with the explicitly retained
legacy SuperIso EM/power/semileptonic normalization. It is not uniformly
truncated full QCD+QED/HQE, complete Zee, or 2026 NNLO.

The existing D12 prescription has Eγ>1.6 GeV, mu0=160 GeV,
mt_MSbar(mu0)=163.16587299291515 GeV, alpha_s(mu0)=0.10877484993481065,
mu_b=2.393749465308278 GeV and its archived default inputs. SM baseline:
3.5427236527176535e-4. The independent cross-kernel investigation instead
uses mu_b=4.2 GeV; its SM baselines must not be substituted into D12.
The real unprimed calculation targets the CP-even inclusive rate; no explicit
spectator/isospin-dependent resolved-photon completion has been certified.

The physical scalar card supplies mH1, mH2, beta and gamma; tanβ=tan(beta),
a=(cosγ,−sinγ). Both up/down vertices carry the same a_k. Therefore
ΔC_i=cos²γ ΔC_i^II(mH1)+sin²γ ΔC_i^II(mH2) at the tested QCD order,
**before** evaluating the rate. No incoherent rate addition or individual
670-GeV cut is permitted. CKM normalization, Hamiltonian sign, running top,
ordinary/effective maps and the single alpha_s/(4π) factor are already
independently checked in [C1](../../module5/BSGAMMA_2026_CONVENTION.md),
[C2](../../module5/BSGAMMA_2026_ACCURACY.md) and D9B; no rederivation here.

## Reused numerical evidence

The verifier binds complete original D10 scalar cards to their D12 receipts,
checks coherent sums and one-state matching controls, and checks archived
matching/rate/end-point evidence. This is an evidence replay, not a new
independent rate calculation. See [EVIDENCE_REPLAY.json](EVIDENCE_REPLAY.json).

| Original scalar card | (mH1,mH2), GeV | Archived D12 BR, diagnostic only |
| --- | --- | ---: |
| d7_NO_neutral_near_heavy_07 | (298.7266553444879,532.9329127809378) | 4.2262508129385407e-4 |
| F13_heavy_0001330 | (572.2316243593124,873.2076828282773) | 3.886651979064471e-4 |

D9B's independent BMU/native matching residual is at most 6.67e-16 and its
rate-path residual at most 5.43e-20. Zero NP, one-state endpoints, equal
masses and state exchange passed at its stated numerical tolerances. These
are implementation checks, not physical error estimates. Published one-state
normalization/confidence-bound reproduction is still **NOT_EVALUATED**.

The separate branch at `4c7998579e0dacd87fb1d73fa328de8c026a9c0c`
already measured signed/joint dipole curvature and two held-out probes.
For 10^4 BR=b0+s7 c7+s8 c8+q77 c7²+q78 c7 c8+q88 c8²:

| Prescription at mu_b=4.2 GeV | b0 | s7 | s8 | q77 | q78 | q88 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| EOS diagnostic | 3.222339 | −8.426197 | −2.010068 | 5.669027 | 2.632701 | 0.403327 |
| D9B diagnostic | 3.425772 | −9.304048 | −2.129365 | 5.913047 | 2.913880 | 0.409380 |

Held-out raw-BR residuals are below 9e-19. This is a verified response of
those legacy kernels, not a standalone fitted theory or a 2026 remainder.
The prior 72-point diagnostic collection is not rerun or extended.
The existing detailed comparison isolates different bottom/charm mass
prescriptions, QCD running, CKM defaults, QED terms, normalization, truncation
and power corrections. A shared low vector does not resolve those differences.
Their spread must not become a sigma or be removed by fitting an intercept.

## Uncertainty gate and 2026 source finding

[2026 Letter](https://arxiv.org/html/2608.29863v1), Sec.IV Eq.(4), supplies
10^4 BR_linear=3.54−8.51 ΔC7−2.16 ΔC8 for LO NP at 160 GeV, explicitly
dropping quadratic NP. Its SM ±0.14e-4 combines a 3% higher-order estimate
and about 2.7% parametric uncertainty. The
[companion](https://arxiv.org/html/2608.29864v1), Sec.3/Apps.A–C, gives the
bilinear framework, kinetic normalization and hadronic inputs. Previously
inspected official ancillary material supplies G27 interference functions,
not a complete generic-NP executable or a finite Zee remainder bound.
Neither the linear formula nor SM covariance certifies nonlinear Zee errors.

SuperIso **does** expose error machinery: `chi2.c:33` sets a 0.04-width
`bsgamma_rand` nuisance and `interpreter.c:582` multiplies the BR by
(1+bsgamma_rand). This is an existing backend prescription, not evidence
that it covers the D9B NLO truncation and two-state model. flavio instead
adds 0.1249*delta_BXsgamma inside its rate; the parameter width is 0.06557,
annotated as 5%,3%,3% in quadrature. Its public NP uncertainty routine samples
parameter priors, but this additive legacy nuisance is not automatically a
Wilson-dependent bound. HEPfit exposes scales, HQE inputs and BLNPcorr;
statistical software does not supply a calibrated Zee nuisance model.

Missing: independent matched finite-cut one-state BR/SM reference;
consistent order and normalization across the independent check; bounds on
the operator/accuracy omissions in [BSGAMMA_COVERAGE.md](BSGAMMA_COVERAGE.md);
NP-dependent perturbative and power uncertainties, parameter correlations and
a declared confidence prescription. Scale dependence alone cannot bound all
missing terms. No scale envelope or arbitrary theory percentage is supplied.

## Smallest next steps, in dependency order

1. Obtain an independently executed, source-qualified finite-cut one-state
   reference card: SM and NP BR, order-separated coefficients, scales/masses,
   semileptonic normalization, EM/HQE/resolved-photon prescription and numerical
   accuracy. Existing BG1998 uncut curves, HMS2012 NNLO curves and the 2026
   linear equation do not provide a matched oracle for this legacy NLO path.
2. Reproduce that card in the primary D9B path and an independently implemented
   compatible kernel. Alternatively qualify HEPfit's THDM path and implement
   a small order-tagged coherent matching adapter, checking its **effective**
   basis and alpha_s weighting explicitly. No package-wide rewrite is justified.
3. Only after that gate, test a finite saved-card set with signed/joint
   C4/C7/C8 probes and held-out spectra; propagate prescribed scales, masses,
   CKM, semileptonic/HQE inputs and Wilson-dependent hadronic nuisances.
   Bound omitted light-quark/chiral/EW/other-operator effects or restrict the
   documented accuracy domain. Reuse all current matching and RG evidence.
4. Define profiling/marginalization, correlations with the experimental
   extrapolation and confidence ordering. Reproduce the **chosen scheme's**
   one-state bound before any opt-in physical exclusion adapter.

An alternative is an author-maintained 2026 nonlinear response plus inputs
and covariance, or a certified remainder domain for Eq.(4). No author was
contacted. Stop here under PLAN.md's bounded gate; specialist/reference input
is needed before claiming full exclusions. No permission to scan follows.

## Verification and portability

```sh
python3 research/full_constraints/verify_evidence.py
python3 research/full_constraints/verify_evidence.py --check-external --rate-workspace /home/amine/zee-bsgamma-rate-validation
git diff --check
```

The first command needs only this checkout and verifies the frozen cards and
receipts. The second additionally hashes the 21 inspected public source
artifacts and 11 prior-evidence files at their recorded host locations; it
does not execute their code. `--output /tmp/NEW_REPORT.json` saves a fresh
receipt and refuses overwrites. On another host restore source bytes from
the pinned URLs/archive (preserving licenses), update only local path hints
in a separately reviewed manifest, and supply the pinned prior checkout.
No third-party sources, binaries or runtime environment are vendored.
The archived report records this audit's successful complete verification;
local hints are convenience paths, not source authority.
