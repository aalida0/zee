# Tau-tau materiality: bounded stop, with retained-width arithmetic only

**`HIGGS_SCOPED_SEARCH_BLOCKED`.** The h125 source comparison stopped at
the explicit Flo21/Hue18 mass-routing mismatch documented in
[HIGGS_ZGAMMA_2021_RESCUE.md](HIGGS_ZGAMMA_2021_RESCUE.md).
Consequently no H/A Zgamma width has been added and no Phase II omitted-width
calculation was attempted. The numbers below replay existing receipts;
they do not recompute SusHi, HDECAY, diphoton amplitudes or LFV.
No physical BR, certified signal bound, likelihood ratio, exclusion or
“not excluded” result is assigned.

## What the existing evidence actually quantifies

Inputs are the pinned `NEUTRAL_WIDTH_EVIDENCE.json`, `SUSHI_EVIDENCE.json`
and `COVERAGE.json`; their digests and arithmetic are retained in
[TAUTAU_MATERIALITY_REPLAY.json](higgs/TAUTAU_MATERIALITY_REPLAY.json).
Here K denotes the known disjoint mixed-accuracy sum, **not** a total width.
The tau numerator is the previously calculated tree general-Yukawa width.

| Retained quantity | D7 H | D7 A | F13 H | F13 A |
| --- | ---: | ---: | ---: | ---: |
| K / GeV | 11.9585831695 | 18.5677788929 | 2.25626947016 | 7.78229418104 |
| Gamma_tau(tree) / GeV | 2.31209154e-6 | 6.20557400e-9 | 9.22309259e-9 | 6.57164349e-11 |
| Gamma_tau(tree)/K, formal ratio | 1.93341595e-7 | 3.34211972e-10 | 4.08776199e-9 | 8.44435244e-12 |
| K/M, lower-width diagnostic | 0.0242848 | 0.0376505 | 0.00319096 | 0.00982291 |
| Central ggF times formal ratio / pb | 4.49676536e-7 | 1.35940799e-9 | 6.51101179e-11 | 1.23873645e-13 |
| Central bbH times formal ratio / pb | 5.50668657e-10 | 1.03553566e-12 | 5.66914461e-11 | 6.78008273e-14 |

These very small central diagnostics motivate examining a conservative
upper bound, but are **not** such a physical bound. The production inputs
have scoped LO scale/PDF variations, with unknown Zee EW and parametric
errors; they are not a certified sigma_upper. The tau widths have no
qualified correction/error bound. In particular a suppressed tree Yukawa
does not justify assuming a small relative correction to the tau numerator.
A numerical threshold comparison without those qualifications would create
an unsupported confidence statement.

At fixed, qualified numerator and production, positivity would give
BR_tau <= Gamma_tau/K and sigma BR_tau <= sigma_upper Gamma_tau/K.
Our K is a disjoint sum at the declared mixed accuracy; promoting it to a
rigorous lower bound on the all-corrected physical total also requires
control of signed corrections to already counted channels. New omitted
final states add nonnegative rates, whereas finite-width corrections after
subtraction and higher-order corrections need not be positive. This
distinction must survive any future “conservative” implementation.

## Exact missing contributions and requested numerical inputs

No missing contribution below has been converted into zero or an arbitrary
percentage. A closed on-shell threshold only sets that on-shell mode to zero.

| Channel or correction | Existing evidence / gap | Required bounded input |
| --- | --- | --- |
| H/A Zgamma | h scalar source comparison has a localized routing mismatch; no complete h/H/A release | Resolve the six-argument C0 definition and complete the one-loop gates in the rescue report |
| A WW/ZZ at one loop | No per-card physical width or certified bound | Model-matched CP/chiral amplitude or a controlled per-card upper bound; include general complex lepton couplings |
| H/A charged-W off-shell tails and finite charged daughters | Original H1 on-shell contributions already included; H2 tail not bounded | Inclusive model-matched calculation with explicit subtraction of already counted on-shell channels; signed correction and uncertainty |
| Virtual charged pairs and nonresonant scalar/EW multibody modes | Charged pairs closed on shell on these cards; virtual rates unbounded | Controlled per-card bound, including overlap/subtraction conventions |
| Neutral cascades and finite neutral daughters | Transferred HDECAY approximation retained; F13 A->HZ* already contributes 0.009988109 GeV | Correction to that approximation without counting HZ* twice |
| Tau numerator and existing-channel QCD/EW corrections | Existing channel-specific accuracy only, no correlated decay error budget | Bound on Gamma_tau and on changes to K, with shared parameters and possible suppressed-Yukawa sensitivity |

The original charged-W gaps M-Mcharged-MW and charged daughter tree widths
are copied in the replay JSON. Notably the closed H2-W gaps are approximately
-121/-120 GeV for D7 H/A and -246/-161 GeV for F13 H/A; that observation
alone is not a numerical tail bound. The already counted charged-W widths
are 0.926020/0.939357 GeV for D7 H/A and 1.053424/6.154915 GeV for F13 H/A.
No ordinary single-charged-state HDECAY tail is silently transferred to the
two-state Zee model.

For a genuinely additional positive missing width Delta with an unchanged
numerator, the relative reduction from Gamma_tau/K is exactly
Delta/(K+Delta). If an observable-specific allowed relative shift were
epsilon, the needed bound would be Delta <= epsilon K/(1-epsilon).
Neither epsilon nor a Delta bound is established here. Epsilon must follow
from the actual production-plane likelihood, signal uncertainty and width
response; a private choice of 1%, 5% or 10% would not answer that question.

## Selected ATLAS likelihood and overlap qualification

The [ATLAS analysis](https://arxiv.org/html/2002.12223v2) is
arXiv:2002.12223, DOI 10.1103/PhysRevLett.125.051801, 13 TeV, 139 fb^-1.
Its signal samples use ggF Powheg-Box v2 and bbH MG5_aMC@NLO; the
interpretation assumes natural width negligible relative to resolution.
No acceptance transfer from our LO SusHi inputs is established.

The actual pinned HiggsTools dataset is ID **200212223**,
`neutral/tautau/LLH_LHC13_ATLAS_139.json`, commit
`3539f9adf3724f8752701208bf059d1658824cd2`, SHA256
`626edb4f21ab3c3a77febf71b3780ce070961b29c9221289c47853916262a591`.
Its runtime class is `LikelihoodLimit`, with separate ggH->tautau and
bbH->tautau axes, and `analysis.massResolution={absolute:5,relative:0.15}`.
This was read and hash-checked, not replaced by a one-dimensional limit curve.
The prior pinned HiggsTools runtime remains unchanged; no predictions were
constructed during this task.

[HiggsBounds-5](https://arxiv.org/html/2006.06007v1),
DOI 10.1140/epjc/s10052-020-08557-9, Sec.4 documents approximate clustering
and likelihood reconstruction, including special processing of the ATLAS
excess region. Its historical 20% clustering prescription must not replace
the actual pinned dataset's 15%/5 GeV settings. Neither prescription proves
the required Zee interference or line-shape approximation.

D7 H/A are separated by only 0.730534 GeV near 493 GeV, while their retained
K/M values already reach 2.4%/3.8%. They cannot be treated as two independent
isolated observed curves. F13's separation is 85.177412 GeV near 707/792 GeV;
its handling likewise requires the pinned combination algorithm and signal
assumptions. General complex tau couplings prevent importing an unproved
pure-CP interference argument. No multi-state observed ratio is reported.

## Stopping decision

The smallest decisive specialist package is: the corrected/intended mixed
PV routing and one-loop convention check; per-card bounds on the omitted
widths and tau numerator corrections above; and a qualified two-production,
two-state acceptance/width/likelihood treatment. This is a request for a
bounded correction and observable-specific assessment, not a new scan or
a demand for all perturbative orders.

No physical width/materiality gate passed, so `HIGGS_COVERAGE.md`,
`VALIDATION_MATRIX.json` and `PROGRESS_TO_FINAL_SCAN.md` have not been
promoted. The new scalar diagnostics do not change
`HIGGS_FULL_COVERAGE_BLOCKED`, `B_FULL_RATE_BLOCKED`,
`LFV_FULL_COVERAGE_BLOCKED`, `physical_higgs=UNKNOWN` or final-scan
authorization. Existing frozen calculations and their validated bounded
claims remain intact.
