# Executable backend inventory (2026-11-06)

Actual versions, source SHA256 values, errors and commands are recorded in
[inventory.json](inventory.json). PyPI queries returned flavio 2.7.1, wilson
2.5.2 and eoshep 1.0.21. GitHub's latest EOS release is v1.1 (2026-09-25);
its rate and WET interface were inspected, but only 1.0.21 was executed.

| Candidate | Executed support and coefficient interface | Decision |
| --- | --- | --- |
| flavio 2.7.1 + wilson 2.5.2 | `BR(B->Xsgamma)`, CP average, fixed Eγ>1.6 GeV. NP-only ordinary `C7_bs`, `C8_bs` at 160 GeV in WET/flavio; backend runs them once, adds SM once, constructs effective dipoles once. Both signs and curvature work. `C4_bs` initialization actually raises AssertionError. | Selected for restricted **dipole** pilot. Full ordinary C4/C7/C8 NLO input unsupported by this public route. |
| EOS 1.0.21 wheel | `B->X_sgamma::BR(E_min)@NLO`, `model=WET`; total ordinary C1–C8, C7'/C8' at `sb::mu`, no NP subtraction/addition. C4/C7/C8 ±0.01 tests and three upstream numeric rate references executed. `model=SM` separately evaluated. | Viable independent low-scale kernel. High-scale ordinary-vector evolution/injection bridge **NOT_EVALUATED**. |
| EOS upstream v1.1 | Same rate observable/NLO implementation family and WET coefficient function with ignored `mu` argument in inspected source. No PyPI v1.1 or GitHub binary asset in queried listings. | Source-only inventory; v1.1 execution **NOT_EVALUATED**. |
| HEPfit commit `322bd73a2dadd94ce94a6d71cb79d616e569120a` | `Bsgamma` implements nonlinear rate and E0 bin minimum. Inspected `FlavourWilsonCoefficientMatching::CMbsg()` copies SM matching, sets `WCscale`, injects only `DC7g` at LO; C8/C4 are not passed by that method despite getters elsewhere. | No build: `root-config` absent. Public route inspected is insufficient for the required vector. Other model/custom C++ routes **NOT_EVALUATED**, not ruled out. |

## Physics/normalization and input coverage

**flavio:** the installed `bxgamma.py` cites Misiak et al.
[1503.01789](https://arxiv.org/abs/1503.01789) and
[hep-ph/0609241](https://arxiv.org/abs/hep-ph/0609241).
It uses numeric K1/K2 matrices, attributed in source to M. Misiak, with
Q1–Q8 bilinears and primed terms; several K2 four-quark entries are zero.
This is the 2015 prediction framework with backend defaults, not the archived
2026 3.54e-4 prediction. Normalization is experimental semileptonic BR times
`|Vts*Vtb/Vcb|² 6 alpha_e(0)/(pi C_BXlnu)` and perturbative + constant
nonperturbative + nuisance terms. Low scale is 2 GeV. Public uncertainty
interfaces sample parameter distributions (`sm_uncertainty`, `np_uncertainty`,
`sm_covariance`); only the SM interface was numerically probed here.

Masses, alpha_s, CKM, `C_BXlnu`, `BR(B->Xcenu)_exp` and nuisance distributions
are supplied by the pinned parameter defaults. The SM Wilson vector is an
interpolated **fixed table**, and K matrices and the central nonperturbative
correction are numeric constants. Arbitrary changes to all SM masses do not
recompute a complete SM NNLO matching/kernel calculation. In particular, do
not describe this as a fully variable-input NNLO solver. The rate retains
squares of the supplied total coefficients and the numeric NNLO matrix; the
NP evolution in wilson is leading-log QCD/QED, not certified NLO evolution.
Injecting NLO matching into that path does not establish full NLO NP accuracy.
Cut changes are explicitly rejected and tested.

**EOS:** the NLO source cites BCMU:2002A and CMM:1996A, with leading HQE and
EGN:2010A power corrections. It evaluates virtual amplitudes, bremsstrahlung,
C7/C8 squares and interference, including C4 in the virtual amplitude and
ordinary-to-effective conversion. Its amplitude square and exponential
bremsstrahlung term retain some higher-order contributions: it is the backend
prescription, not our newly uniformly truncated NLO calculation. Normalization
is a decay width using GF², alpha_e(mb), CKM, mb and lifetime/hbar, unlike
flavio's semileptonic normalization. Parameters include masses/QCD running,
CKM, GF, alpha_e, lifetime and mu_pi²/mu_G². Both executable default SM and
WET-total baselines are retained; their small difference is not a NP shift.
WET reads total coefficients at the low scale and does **not** evolve the
input vector from 160 GeV. Public c7/c8 are ordinary coefficients; the internal
inverse-gs convention is handled inside EOS. Do not multiply public inputs by
an extra alpha_s factor.

EOS allows a cut only where `0.03 <= z <= 0.12` and
`1/36 <= delta <= 1/3` in this implementation. The tests reproduce upstream
1.6, 1.8 and 2.0 GeV reference rates with its full regression card. EOS
sampling/parameter/analysis interfaces do not supply a calibrated Zee theory
covariance by themselves; uncertainty sampling was **NOT_EVALUATED** here.

The installed wilson registry provides **JMS→EOS only**. Attempting to run
`Wilson({'b->s::c4':1e-5},160,'WET','EOS').match_run(4.2,'WET','EOS')`
actually fails: `No translator from basis EOS to JMS found.` This is a
specific interface blocker, not a claim that a validated adapter is impossible.
A C7/C8-only flavio→EOS translation was also probed: its output contained
complex values in EOS real coefficient slots, so it was not promoted to a
physical bridge or used in results. No manual projection or guessed C4 map
was substituted. A bridge needs normalization, CKM, ordinary-basis and RG tests.

**HEPfit:** inspected `bsgamma.cpp` reads SM+NP coefficients at mu_b through
`ComputeCoeffsgamma`, contains LO/NLO/NNLO pieces, electroweak/power terms and
semileptonic normalization `BRsem * CKMratio * 6 alpha/(pi C)`.
E0 is obtained from the observable bin; no cut validation was executed.
`BRsem`, masses, mu_b/mu_c and `BLNPcorr` are among its inputs. General model
matching is C++/NDR with order-tagged arrays, not a demonstrated arbitrary
C4/C7/C8 Python input API. ROOT, GSL, Boost and the documented BAT/RGESolver
build requirements exceed the selected numerical pilot. BAT/statistical
interfaces exist; no HEPfit result, uncertainty or model covariance was run.
No framework rewrite was attempted.

## Source references

- [flavio v2.7.1 rate source](https://github.com/flav-io/flavio/blob/v2.7.1/flavio/physics/bdecays/bxgamma.py), [upstream SM regression](https://github.com/flav-io/flavio/blob/v2.7.1/flavio/physics/bdecays/test_bxgamma.py).
- [wilson v2.5.2 WET evolution](https://github.com/wilson-eft/wilson/tree/v2.5.2/wilson/run/wet), [basis translations](https://github.com/wilson-eft/wilson/blob/v2.5.2/wilson/translate/wet.py).
- [EOS v1.0.21 rate](https://github.com/eos/eos/blob/v1.0.21/eos/rare-b-decays/inclusive-b-to-s-gamma.cc), [regression card and references](https://github.com/eos/eos/blob/v1.0.21/eos/rare-b-decays/inclusive-b-to-s-gamma_TEST.cc), [WET implementation](https://github.com/eos/eos/blob/v1.0.21/eos/models/wet.cc).
- [EOS v1.1 release](https://github.com/eos/eos/releases/tag/v1.1), [current documented observables](https://eoshep.org/doc/reference/observables.html).
- [HEPfit pinned matching](https://github.com/silvest/HEPfit/blob/322bd73a2dadd94ce94a6d71cb79d616e569120a/FlavourWilsonCoefficient/src/FlavourWilsonCoefficientMatching.cpp), [rate](https://github.com/silvest/HEPfit/blob/322bd73a2dadd94ce94a6d71cb79d616e569120a/Flavour/src/bsgamma.cpp), [installation](https://github.com/silvest/HEPfit/blob/322bd73a2dadd94ce94a6d71cb79d616e569120a/README.md).
