# Result — bounded independent rate pilot

**Executable nonlinear restricted-sector prediction obtained. Full ordinary
C4/C7/C8 Zee rate accuracy NOT_EVALUATED. DIAGNOSTIC_ONLY. Publishability and
2026 exclusion readiness UNKNOWN; global acceptance null.**

flavio 2.7.1 + wilson 2.5.2 was selected for a high-scale dipole pilot. Existing
BMU ordinary LO/NLO matching is imported unchanged. EOS 1.0.21 independently
executes a low-scale C1–C8 rate and reproduces its upstream numerical references.
HEPfit's inspected public matching route lacks the required C8/C4 injection;
no HEPfit build or rate was attempted. EOS v1.1 is newer than the available
PyPI wheel and was inspected but not executed. See [BACKENDS.md](BACKENDS.md).

At Eγ>1.6 GeV, mu0=160 GeV, matching mt_MSbar=163.09480225405557 GeV and
alpha_s=0.10911534140168211 (flavio defaults):

| Executed quantity | BR |
| --- | ---: |
| flavio zero NP | 3.30969227017549e-4 |
| 550 GeV, tanβ=5.3, LO+NLO matching **dipoles only** | 3.91980888976674e-4 |
| 900 GeV, tanβ=5.3, LO+NLO matching **dipoles only** | 3.61337263630917e-4 |
| 100 TeV decoupling diagnostic, tanβ=5.3 | 3.30972881680358e-4 |
| 550 GeV opposite-coupling sign diagnostic | 2.75937680391265e-4 |
| Two-state 550/900 GeV, tanβ=5.3, γ=1.09, **dipoles only** | 3.67779290337027e-4 |
| EOS default SM NLO prescription | 3.36534333645447e-4 |
| EOS WET default total-coefficient NLO prescription | 3.36532497863266e-4 |

LO and LO+NLO matching, both masses, tanβ=2/5.3/50, decoupling and the opposite
sign are retained in [results.json](results.json). LO+NLO means
`Delta C = Delta C^(0) + alpha_s(mu0)/(4 pi) Delta C^(1)` exactly once.
It is not a full NLO NP rate: wilson's NP evolution is leading-log and flavio's
fixed numeric rate kernel has its own higher-order prescription.

C4 is computed and recorded but explicitly **excluded from the flavio pilot**:
its public WCxf basis rejects `C4_bs`. No C4 sensitivity bound is inferred.
No NLO ordinary-to-effective correction is applied manually; the backend
constructs effective dipoles once after running and adding the SM vector.
The coherent two-state supported dipoles are injected once, with cos²γ/sin²γ
weights. Endpoint, equal-mass and interchange rate residuals are zero in the
recorded run. Its BR minus the weighted average of one-state BRs is
−1.12421503476140e-7, demonstrating that averaging rates loses nonlinear terms.

Independent high-scale ±0.01 probes give nonzero even responses:
C7: 7.06515669449473e-8; C8: 5.10620960819013e-9, defined as
`[BR(+h)+BR(-h)]/2−BR(0)`. Doubling h quadruples each even response in live
tests. Odd responses also remain nonzero. EOS separately responds to signed
**low-scale total** C4/C7/C8 shifts; those are not high-scale NP coefficients.

EOS reproduces its source regression card at cuts 1.6/1.8/2.0 GeV:
3.13699360919809e-4, 3.09211051284121e-4, 3.00017787152860e-4,
respectively, within 1e-9 absolute of upstream rounded references. This checks
the installed kernel against its own documented implementation. The flavio
SM regression reproduces its upstream 2015-framework target within that test's
0.2e-4 tolerance. Neither check is an independent full Zee one-state precision
benchmark or a matched flavio/EOS comparison. No physical-accuracy PASS is issued.

**Validation:** nine focused tests and one unchanged upstream flavio SM test
pass, with no failures/errors/skips. Tests additionally check archived D9B
ordinary matching numbers, invalid inputs/scales, unsupported C4 rejection,
cut rejection, decoupling, opposite sign and nonlinear mixing identities.
`git diff --check` passes. Existing physics modules and historical evidence
are unchanged; external source/binary/environment files are ignored locally.

The separately archived legacy SuperIso example 3.88229911548e-4 is **not**
compared as an accuracy oracle: matching inputs, RG order, normalization,
nonperturbative terms and retained operators are not genuinely matched.
The flavio baseline represents its 2015 calculation framework with its current
pinned inputs, not the historical audit's 2026 3.54e-4 prediction. No central
value rescaling, mass exclusion, likelihood or global scan was performed.

## Remaining work and separate D14 adapter design

1. Implement and independently test a **separate research adapter** for the
   full ordinary high-scale C4/C7/C8 vector. EOS is promising because its
   low-scale rate accepts C4. The installed wilson registry has JMS→EOS but
   no EOS→JMS translator: a direct high-scale EOS call actually fails. Obtain
   an existing validated NDR ordinary→JMS/Bern bridge and order-consistent
   evolution, or a documented backend native matching extension. Certify
   normalization/CKM, all induced Q1–Q8 entries, effective maps and basis
   round trips before using it. Do not reuse SuperIso evolution as independent
   validation or silently drop C4. Execute current EOS v1.1 if selected.
2. Reproduce an external one-state numerical rate benchmark with **matched**
   inputs, cut and perturbative prescription. Kernel regressions and qualitative
   Type-II trends do not establish the desired physical accuracy. Repeat the
   full-vector nonlinear/sign/identity controls through that validated bridge.
3. Quantify NP matching/evolution/kernel truncation, cutoff dependence,
   nonperturbative and normalization uncertainties against the current SM
   prediction. The executed flavio 64-draw SM uncertainty interface returns
   2.12269407873182e-5, a finite-sample API probe, not a Zee uncertainty model.
   Primed/finite-ms/light-quark effects, enhanced down Yukawas, other operators
   and their covariance remain **NOT_EVALUATED**. No full NNLO NP claim.
4. Only then define the adapter contract: explicit NP-only ordinary coefficient
   object with mu0, scheme, perturbative components, input/source hashes and
   cut; one backend evolution/addition/rate call; output BR, supported-operator
   coverage, uncertainties/covariance provenance and `DIAGNOSTIC_ONLY` status.
   Cache must bind all those fields and executable/kernel versions. D14 should
   receive a separate optional diagnostic result, never an accepted-point flag.
   Missing or unvalidated coverage returns `NOT_EVALUATED`. Changing D14
   acceptance requires a separately validated accuracy domain and statistical
   prescription; no D14 integration code or accepted-point logic was changed.
