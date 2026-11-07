# Higgs coverage gate — 2026-11-07

**h125 rate-ledger update:** [current report](HIGGS_H125_SIGNAL_STRENGTH_REPORT.md) supplies corrected-charm ordinary-channel sums 4.280495766/4.005236276 MeV, full native LFV and independently checked h125-only LO production. Three width-independent signal-strength ratios are released. Absolute μ/BR normalization and the scoped VBF→bb comparison remain BLOCKED pending a competing-channel bound and uncertainty/acceptance qualification. No new exclusion or milestone increment. The selected HS absolute-rate convention is source-checked; missing `ref` does not mean μ=1 normalization.

**h125 Zγ update:** the [complete leading one-loop h125 calculation](HIGGS_ZGAMMA_COMPLETE_H125.md)
now passes independent matched-input SM and signed one-charged-scalar controls,
including both mixed charged scalars and complex diagonal leptons. D7/F13
ΓZγ=(6.338611988312, 6.408681594999)e−6 GeV and Γ/ΓSM=
(0.978770448547, 0.989590176981). This supersedes the h125 Zγ missing-input
statements in the historical inventory below, only at the declared leading
order. H/A Zγ, total-width/likelihood qualification and all global blockers
remain unchanged; no new exclusion or scan authorization follows.

**HIGGS_FULL_COVERAGE_BLOCKED.** The complete leading one-loop
h125→γγ amplitude is independently validated on the two original D12
NO/low_joint witnesses, including W, all nine charged fermions and **both**
mixed charged scalars. This establishes **HIGGS_SCOPED_CHANNEL_VALIDATED**
for the amplitude, not a validated experimental exclusion.
`physical_higgs=UNKNOWN`, `exclusion=null`, `global_acceptance=null`.
No Higgs hard veto or global PASS is supplied.

The [neutral-width execution](HIGGS_NEUTRAL_WIDTH_SEARCH_REPORT.md) adds
the original F13 HDECAY transfer and independently checked leading H/A
diphoton widths on both cards, with 16 fresh signed SARAH trilinear checks.
Known disjoint sums are D7 H/A = 11.9585831695/18.5677788929 GeV and F13
H/A = 2.25626947016/7.78229418104 GeV; none is a physical total or BR
normalization. The exact ATLAS tau-tau analysis ID 200212223 is loaded and
source checked, but all four signal inputs fail the complete-width gate.
Mixed H Zgamma, off-shell/finite-daughter effects, loop A WW/ZZ and
uncertainty/acceptance remain unbounded. `HIGGS_SCOPED_SEARCH_BLOCKED`;
zero new usable exclusions. The historical inventories/receipts below are
preserved; [OBSERVED_SEARCH_COVERAGE.json](higgs/OBSERVED_SEARCH_COVERAGE.json)
records this selected-analysis stopping decision. Higgs milestones stay 2/6.

The subsequent [executed SusHi/HDECAY stage](HIGGS_SUSHI_EXECUTION.md)
adds independently validated **13-TeV LO ggF and 5FS bbH for H and A on
both original D7/F13 cards**, with signed native-SARAH matching, seven-point
scale envelopes and MMHT2014lo68cl Hessian PDF estimates. It also executes
HDECAY 6.60 through rebuilt anyHdecay on D7 and validates transferable
neutral partial widths plus native charged-W/general-lepton additions.
Complete Zee widths and physical analysis qualification remain missing:
zero new usable exclusions, zero complete signals connected to HiggsTools.
Machine evidence and the D7/F13 per-ID consumer gate are in
[SUSHI_EVIDENCE.json](higgs/SUSHI_EVIDENCE.json). The historical
`COVERAGE.json` inventory below is preserved; the new evidence overlays its
prediction availability without changing its qualified exclusion statuses.

## Dataset and exact analysis inventory

[The machine-readable matrix](higgs/COVERAGE.json) enumerates **all 310
loaded limit IDs**, their actual process definitions, original source URLs,
collision energy, grid-axis envelopes, explicit width grids, constraints,
normalizations, acceptances, suppression rules and byte hashes. It also
enumerates all **22 loaded HS measurements / 159 observables**, preserving
all submeasurement processes and the hashed sources of their correlations.
It is the authoritative per-ID gap list; searches omitted by the library
are not silently declared passed.

| Retained source | Pinned identity | Scope |
| --- | --- | --- |
| HiggsTools | 1.1.3, source `71a93a82f34fb120e3095460e52cb15b7bffcea0` | Native library hash checked against frozen D13 evidence |
| HB dataset | `3539f9adf3724f8752701208bf059d1658824cd2` | 274 neutral, 24 singly charged, 11 doubly charged, 1 charged→W-neutral |
| HS dataset | `3c6c2538d9ba0549ea0559cf9b38c18eb80c3af1` | Frozen h125 dataset; not complete November 2026 experimental coverage |

There are 178 ChannelLimits, 17 ChannelWidthLimits, 63 PairDecayLimits,
24 ChainDecayLimits, 23 PairProductionLimits and 5 LikelihoodLimits.
All current dataset JSON bytes match the historical manifests. Per-file
SHA256 and aggregate manifest hashes are retained in the matrix; library,
model, input and calculation hashes are in [HIGGS_VALIDATION.json](HIGGS_VALIDATION.json).

The scope is D7 and F13 D12 witnesses plus **only** the 16 historical D14
production-map scalar IDs (four original NO/IO families each). The original
64-MB saved dataset is read-only and SHA-bound to the production map.
No proposals or new inverse families are generated. Each D14 scalar coverage
row explicitly binds all four original Yukawa witnesses; prediction availability
is common to the four, but numerical widths and charged results retain each
family separately.

`NOT_APPLICABLE` is proved only by an absent doubly charged particle or by
all model mass assignments lying outside at least one published mass-axis
envelope, with zero mass-uncertainty/extrapolation assumed for this inventory.
Bounding-box inclusion is **not** proof of interpolation-hull, selection,
constraint or width validity. Such cases remain `MISSING_PREDICTION`, with
candidate mass assignments retained. This conservative inventory can overcount
potentially applicable channels; it cannot certify a PASS. No claim is made
that all 148–179 potential missing limits per scalar are ultimately applicable.

Even central-input charged searches retain `MISSING_PREDICTION` at the
physics gate while theory/signal-model qualification is absent. Their separate
`central_LO_two_body_inputs_available` field identifies the calculable subset.
There are zero `APPLICABLE_INPUT_COMPLETE` entries at the qualified exclusion
level. Numerical evaluation alone does not fill that status.

## h125: what is now calculated

The native restricted-model potential is `models/SARAH/ZeeTypeII/ZeeTypeII.m`.
The signed trilinear is G=d³V/(dh dH− dH+), in GeV, with L_int=−h H− G H+.
Both charged legs are rotated with the frozen signed ZP matrix. Historical
SARAH evidence covers the diagonal/off-diagonal rules, photon identity charge,
seagull and W/Goldstone normalization; it is reused, not re-extracted.
A fresh independent derivative of the expanded invariant potential checks
G on both actual D12 cards.

The finite leading one-loop amplitude uses

    S = kV A1(tW) + sum_f Nc Qf² Re(kf) Ahalf(tf)
        + sum_i Q_i² G_ii v/(2 m_i²) A0(ti)
    P = sum_f Nc Qf² Im(kf) Ahalf_odd(tf)
    Gamma = alpha_tree² mh³/(256 pi³ v²) (|S|²+|P|²)
    t = mh²/(4 m²)

The common tree scheme fixes v, MW, MZ, g2=2MW/v, cw=MW/MZ,
e=g2 sqrt(1−cw²), hence alpha_tree=0.007565201924913188. Each fermion
uses the same declared mass in its Yukawa normalization and propagator;
D4 kinematic quark and lepton inputs are retained. No running Yukawa is
silently combined with a different propagator mass. An explicitly labelled
alpha(0) convention control is also recorded; its difference is not a sigma.
Scalar masses and trilinears come entirely from the same physical tree card.
No SPheno loop width, pole mass or neutrino result enters.

[2HDMC Eqs.24–28](https://arxiv.org/html/0902.0851v2#S2.SS4.SSS5)
fix the loop and width normalization; its signed scalar vertex maps to
C=−G. An independent inverse-tau convention and sign test uses
[Bhattacharyya–Das Eqs.3–5](https://arxiv.org/html/1408.6133v2), with
kappa_i=−G_ii v/(2mi²) and the opposite overall amplitude sign.
Published HTML byte receipts are in [SOURCE_MANIFEST.json](higgs/SOURCE_MANIFEST.json).

Photon charge is the identity, so a single off-diagonal G insertion cannot
close the γγ loop. Neutral LFV insertions likewise cannot close a one-insertion
flavour-diagonal photon loop. Physical tree H±–W–photon vertices vanish in this
doublet/singlet model; the standard W function includes its gauge completion.
There is no tree hγγ amplitude requiring an independent one-loop parameter
counterterm. Scalar triangles and seagull satisfy the electromagnetic Ward
and Bose controls without a transverse projector. The odd CP tensor is
retained for the complex diagonal lepton Yukawas and does not interfere
with the even tensor in the unpolarized rate.

| Original witness | G11 [GeV] | G22 [GeV] | charged contributions to S (H1, H2) | Γγγ/ΓSM | Without charged loops |
| --- | ---: | ---: | --- | ---: | ---: |
| D7 NO low_joint | 128.393251 | 1645.362706 | +0.060461, +0.239492 | 0.931795956 | 1.022147723 |
| F13 NO low_joint | −153.472961 | 1863.660779 | −0.019357, +0.100575 | 0.975025226 | 0.999625401 |

These are **width ratios**, not inclusive signal strengths. Absolute common-tree
widths are 9.316109546e−6 and 9.748316425e−6 GeV; the common-tree SM control is
9.998014576e−6 GeV. Their alpha(0) convention equivalents are 8.668105670e−6,
9.070249385e−6 and 9.302579194e−6 GeV, respectively.

## h125 still missing for a full likelihood

The physical charged Z generator is

    Z_ij = (g2/cw) [ 1/2 (ZP_i1 ZP_j1 + ZP_i2 ZP_j2) − sw² delta_ij ].

The matrix stores full G, eQ, Z and 2eZ seagull currents. Z12 is −0.09016183
for D7 and −0.15208516 for F13. The G12 Z21 products are **18.2645** and
**27.3960 GeV**, not zero. Thus hZγ needs mixed-mass loops and their seagull /
electroweak gauge completion; a sum of two diagonal 2HDM terms is incomplete.
That complete source-matched group has not been established: `hZgamma=UNKNOWN`.

Source inspection also finds two old input defects: `NeutralEffectiveCouplings.Zgam`
defaults to zero, and `CalcHgamgam.cpp:64–71` repeats the CP-odd muon term and
omits the tau. The new γγ calculator bypasses that implementation; no protected
source is edited. Other effective-coupling channels remain approximations.

A diagnostic HS study replaces **one** γγ partial width by the SMHiggsEW
reference times the complete LO ratio, retaining tree LFV widths. This
reference rescaling is a stated approximation, not uniformly NLO Zee physics.
For assumed Zγ width ratios 0, 1 and 2, it verifies total-width replacement and
BR sums and records all measurement χ² contributions at ratio 1. These are
missing-width sensitivity controls, not three model predictions, a nuisance
profile, a p-value or an exclusion. The physical total width remains UNKNOWN.
`Decay.inv` is a derived inclusive channel and is excluded from the independent
partial-width sum to avoid counting ZZ→4ν twice.

The remaining h125 gate needs complete Zγ, physical mass/total-width accuracy,
SM-reference-to-Zee production/decay and STXS shape qualification, a justified
QCD/EW/parametric covariance, and the declared likelihood confidence prescription.
No arbitrary Δχ² cutoff is used.

## Charged searches and existing production

Five single-charged 13-TeV process implementations accept the saved Hpmtb
central inputs where their mass grids cover H2:

| Limit ID | Reference / process | Required input |
| --- | --- | --- |
| 210210076 | ATLAS 2102.10076, tb | charge-inclusive σ13(Hpmtb) BR(tb) |
| 190809206 | CMS 1908.09206, tb leptonic | same process with its selection |
| 2001077631 | CMS 2001.07763, tb | same process with its selection |
| 1807079152 | ATLAS 1807.07915, τν | σ13(Hpmtb) BR(τν), plus declared constraints |
| 1903045601 | CMS 1903.04560, τν | σ13(Hpmtb) BR(τν) |

The H2-only replay has 37 families with five applications and 27 with three
(the latter exceed the 2-TeV grids). All 64 expected-selected observed ratios
are below one; the maximum is **0.163607442**, ID 15591 NO family 1. This is
`CENTRAL_LO_SUBSET_DIAGNOSTIC`, not a full Higgs PASS. The 3 existing 14-TeV
rates are retained in the original manifest and are not relabelled or used.
D14 has no H1 rate. D12's four existing H1/H2 rates remain frozen historical
D13 evidence; D7's old central ratio 1.072383 still lacks robust qualification
and is not promoted to a new validated physical FAIL.

Inputs are actual LO 5FS gb-associated H2 production, both charges / beam
orders once, NNPDF30_lo_as_0130 member 0 ID263000, fixed μR=μF=mH2, D4
running quark Yukawas at mH2, with numerical integration errors separately
retained. Each row binds full scalar, gamma, tanbeta, all F/D/Ye/Ye2 hashes,
original card, PDF/order/energy/process, source, decay and receipt identity.
The committed manifests are checked; **raw native MG receipt directories
are unavailable in this checkout**. This is documentary replay, not a fresh
validation of raw runs. No integrations are executed.

The reused complete D4 on-shell tree two-body BRs include scalar/vector
competition, including H2→H1Z and H2→H1h. They do not include finite daughter
widths, consequential off-shell channels or NLO corrections. ΓH2/mH2 spans
**0.023225–0.089697**. [ATLAS 2102.10076, Sec.2](https://arxiv.org/html/2102.10076#S2)
uses NLO 4FS signal simulation with a narrow-width approximation and neglects
signal/background interference. Transfer from the LO 5FS Zee rate, its
chiral mixture and finite width needs qualification, not a universal K factor.
The experiment's observed 95% CL curve is retained; the model's confidence
interpretation remains unqualified. Integration errors are not theory bands.

Remaining charged production/qualification gaps are, per in-range state:
8-TeV Hpmtb tb/τν searches; 8/13-TeV qqHpm tb searches; D14 H1 Hpmtb13;
pair/associated channels where applicable; loop-induced VBF H±→WZ if relevant.
A zero **tree** H±WZ vertex does not prove the full loop process absent, so
those analyses conservatively remain missing rather than globally inapplicable.
LEP charged pair and top-decay mass grids are outside these saved cards.
The exact 24 IDs, domains and state assignments are in the matrix.

There is no loaded Hpmtb search for H2→H1Z, H2→H1h or H±→W(h/H/A).
These are explicitly `MISSING_EXPERIMENTAL_COVERAGE` in this dataset. The lone
WH top-decay analysis is a distinct process, not cascade coverage.

## Heavy-neutral gate and source-feasible path

No complete H/A model prediction is present. The matrix gives every loaded
neutral production/decay topology and energy, every potential scalar assignment,
and a per-card heavy-neutral threshold ledger. In particular H→hh is open on
both D12 cards; H/A→H1±W∓ is open too. SM-scaled total widths would therefore
omit physical competition. The threshold ledger is deliberately not a BR table:
CP/gauge zeros and coupling validation must be established separately.

The exact missing inputs include ggH/bbH with scalar/pseudoscalar quark
interference and source-prescribed QCD/PDF uncertainty at 8 and 13 TeV;
VBF, VH, ttH and pair/cascade modes when specified; complete fermion/LFV,
vector, hh/other-scalar, charged-scalar W and loop partial widths; and relevant
off-shell/finite-width, continuum interference and acceptance qualification.
ChannelWidthLimits retain their actual relative/absolute width convention;
unknown neutral widths cannot be tested against that grid.

[SusHi](https://arxiv.org/abs/1212.3249) 1.7.0 now **executes** this gg/bb
path at scoped LO CTB-QCD accuracy. D7 (H,A) ggF=(2.32581373,4.06750239) pb,
bbH=(0.00284816445,0.00309843975) pb; F13 ggF=(0.0159280599,0.0146694072)
pb, bbH=(0.0138685780,0.00802913282) pb. All are pp at exactly 13 TeV.
Source- and scheme-matched independent convolutions agree within 1.56e−6
relative. The transferred colour-singlet quark sector does not transfer
2HDM total widths, electroweak loops or experimental acceptances. Executed
HDECAY partial widths plus native Zee additions give known disjoint D7 sums
11.9584845277 GeV (H) and 18.5675702523 GeV (A), **not** physical totals.
In particular H/A→H1±W∓ contributes 0.926020/0.939357 GeV on D7 and
1.053424/6.154915 GeV on F13. Complete photon/off-shell/uncertainty channels
remain missing. Other energies/processes and the full signal gates above
remain unfilled. Full provenance, omitted terms and uncertainties are in
the execution report; installed/built packages alone do not establish coverage.

## Uncertainty and stop decision

Independent numerical residuals are recorded, not interpreted as theoretical
uncertainties. Missing terms include two-loop QCD/EW effects and tree-input
parameter/covariance qualification for γγ, full Zγ/total widths, production
scale/PDF/mass-scheme uncertainty, decay corrections/off-shell effects and
production-decay/acceptance correlations. No numerical NP sigma is invented.
Large trilinears are retained coherently; higher-order scalar effects are not
bounded by the numerical agreement of leading-order formulas.

The source gate therefore stops the **full-coverage claim**, while preserving
the useful validated γγ calculation. B and LFV remain blocked with their
previous precise findings; no B/LFV calculation is repeated. Full-loop SPheno
remains UNAVAILABLE. The frozen pipeline and all Modules0–13 are unchanged.
