# Original D7/F13 h125 rates: width ledger and physical ratios

**H125_SIGNAL_STRENGTH_BLOCKED for absolute μ; three width-independent ratios calculated.**
The ordinary-channel sums are **4.280495766 MeV (D7)** and
**4.005236276 MeV (F13)** after correcting the HDECAY charm input scheme.
They are not certified total widths. No incomplete sum is normalized into BRs.
Absolute signal strengths, a HiggsSignals model χ² and physical exclusion remain
`null`. The specific remaining width gate is a numerical bound on virtual
exotic contributions and radiative invisible decay, together with a qualified
uncertainty/reference transfer. This is an implementation/validation gap, not
an assertion that the relevant physics is absent from the literature.

Read AGENTS, the task, completed Zγ, execution/coverage, SusHi and neutral-width
reports, original cards, source rescue audit and pinned experimental dataset.
The validated photon amplitudes are consumed unchanged. No photon loop,
heavy-H/A calculation, parameter point, scan, Condor or MG5 run was performed.
All changes are research-only. B, LFV, vacuum and global status are unchanged.

## Predictions that do not need Γtotal

For the same h125 resonance, narrow-width factorization gives

`μ(p,d)/μ(q,e) = [Rσ(p) RΓ(d)]/[Rσ(q) RΓ(e)]`.

The total width cancels, including LFV and invisible contributions. These are
physical, declared-order **ratios of signal strengths**, not absolute μ or
experimentally measured categories. SM denominators use the same input/order
as the corresponding model amplitudes. No tree-α Zγ width is divided by an
unmatched α(0) reference.

| Ratio, 13 TeV where production differs | D7 | F13 |
|---|---:|---:|
| μ(VBF,γγ) / μ(VBF,WW*) | **0.933958096** | **0.975031103** |
| μ(VBF,Zγ) / μ(VBF,WW*) | **0.981041588** | **0.989596141** |
| μ(ggF,γγ) / μ(VBF,WW*) | **0.846127486** | **0.977310053** |

The first two also cancel production and its QCD/PDF errors. They use the
complete leading one-loop photon widths and tree-EW WW* scaling. The third
uses the independently checked **LO QCD** production ratio below. These are
central finite-order predictions; no numerical physics σ or physical CL is
assigned. Remaining EW/scalar, higher-QCD and parametric uncertainties do not
become integration errors. Decay-channel acceptance and experimental covariance
are needed before comparing any ratio to data. No ratio likelihood was run.

## Exact original cards and partial-width ledger

D7 scalar SHA256:
`ff0c551534e5051f223c00435293403e3b553f52e0cbec4344287da8b3dce862`.
F13 scalar SHA256:
`9117e7af53f9ad5c21f964a7c216de7af5824e903856fed54b9b237c922f4a1d`.
Both use the saved D12 **NO/low_joint** witness. All four Yukawa hashes,
physical parameters, native lepton κ values and source/output hashes are in
[the evidence](higgs/H125_SIGNAL_STRENGTH_EVIDENCE.json). No fitted Yukawa is changed.

| Partial width, GeV | D7 | F13 |
|---|---:|---:|
| bb | 2.667519074e−3 | 2.347690584e−3 |
| cc, corrected scheme | 1.090639622e−4 | 1.195146271e−4 |
| gg | 2.839523020e−4 | 3.151253698e−4 |
| WW* | 8.394650870e−4 | 8.414079115e−4 |
| ZZ* | 1.046163970e−4 | 1.048585170e−4 |
| ττ | 2.581200859e−4 | 2.587031386e−4 |
| μμ | 1.121823269e−6 | 9.150394851e−7 |
| ee | 1.700583892e−11 | 2.144126167e−11 |
| ss | 9.723559417e−7 | 8.576236919e−7 |
| uu, tree | 1.048848438e−9 | 1.149350596e−9 |
| dd, tree | 6.022909282e−9 | 5.295983667e−9 |
| γγ, retained validated result | 9.316109546e−6 | 9.748316425e−6 |
| Zγ, retained validated result | 6.338611988e−6 | 6.408681595e−6 |
| eμ, both charges | 5.415181492e−40 | 1.406759238e−45 |
| eτ, both charges | 7.113979622e−12 | 1.220792177e−16 |
| μτ, both charges | 2.861460246e−9 | 4.911688495e−14 |
| **Known-channel sum, not Γtotal** | **4.280495766e−3** | **4.005236276e−3** |

Native leptons use `C = cos(β−α) diag(ml/v) − sin(β−α) D/√2`,
including all complex entries and exact unequal-mass phase space. Six unordered
channels cover nine charge orientations: three diagonal, six LFV orientations.
The total LFV sums are 2.868574226e−9 and 4.923896417e−14 GeV. Diagonal
scalar/pseudoscalar interference and off-diagonal chiral interference are
retained. Generic independent chiral trace kernels reproduce every entry.
QED corrections to these lepton widths are outside the declared tree order.

HDECAY transfer is per partial width, never its Type-II lepton/photon channels
or R2HDM total. The pinned anyHdecay 1.1.0/HDECAY 6.60 library matches the old
execution hash. Quark channels retain running-mass, channel-specific higher
QCD corrections; gg retains massive coherent quarks with finite-mass NLO and
the source's heavy-quark higher-order terms. These are not a uniformly exact
NNNLO general-model result. WW*/ZZ* retain its off-shell approximation at
LO EW, verified against κV². `IOELW=0` disables EW corrections; `IONSH=0`
and `IONWZ=0` permit off-shell treatment. See
[HDECAY 1801.09506, §2.5](https://arxiv.org/html/1801.09506v1#S2.SS5)
and the pinned wrapper/Fortran hashes in [execution evidence](higgs/h125_receipts/EXECUTION.json).

**New input-scheme correction:** the linked `hdecay_core.f::RUNM_HDEC`
uses `QQC=3 GeV` and `AMCB` as m_c(3), while the old driver passed 1.273.
Executing that function at 1.273 returns 1.632236691 GeV. Its linear MSbar
mass evolution gives **m_c(3)=0.9928272100 GeV** for m_c(m_c)=1.273,
with this pinned αs/threshold prescription. A fresh SM-only HDECAY execution
checks the corrected charm channel. The exact native Type-II up-quark factor
then supplies Γcc; the old Γcc/SM ratio is independently checked to equal κu².
The correction to the saved model sums is −6.994024670e−5 and
−7.664202124e−5 GeV: **1.63% and 1.91%** of the corrected sums. Old receipts
remain unchanged. This finite-order conversion has no assigned parametric σ.

The matching SM ledger replaces HDECAY photons and leptons with the same
orders/schemes used for Zee, and includes u,d,e. Its known sum is
4.070980542 MeV. It is not substituted for the HiggsTools SMHiggsEW reference.

## Competing decays and the precise remaining width gate

- All non-SM scalar masses exceed 125 GeV: D7 (H,A,H1±,H2±) =
  (492.431,493.161,298.727,532.933) GeV; F13 =
  (707.082,792.259,572.232,873.208) GeV. Thus scalar pairs, h→AZ,
  h→H±W∓ and every cascade containing an on-shell extra scalar are closed.
  tt and any final state containing an on-shell top are also closed.
- Closing on-shell thresholds does **not** remove virtual exchange:
  h→Z(*)A*, W(*)H±*, scalar-pair exchange and scalar radiation from fermions
  can contribute to four-fermion final states. The two charged propagators,
  native F/D/quark daughter currents and interference with retained SM
  amplitudes need a coherent bound. Ordinary HDECAY doublet charged tails
  cannot supply that bound in Zee. The retained WW*/ZZ* sum is itself a
  pseudo-channel approximation, not a full model four-fermion matrix element.
- There is no neutral renormalizable hνν Yukawa without right-handed neutrinos;
  its width is zero at the **massless-neutrino tree order**. The actual radiative
  Majorana hνν coupling is not set to zero. Its leading loop/materiality bound
  is `null`. Small native F/D make suppression plausible, not certified here.
  SM h→ZZ*→4ν is already inside ZZ* and must not be added as a second channel.
- No extra dark particle is present. Radiative/Dalitz channels, real/virtual
  QED radiation and corrections to the retained standard channels belong in
  a consistently inclusive higher-order definition, not new duplicated widths.

For an *additional positive disjoint* width to suppress a denominator-based
rate by 1%, it must equal the retained sum/99: **43.2373 keV (D7)** or
**40.4569 keV (F13)**. A signed interference correction needs control at
approximately 42.8050/40.0524 keV for 1% linear precision. These are numerical
**required tolerances**, not upper bounds on unknown channels. The sums are
not advertised as rigorous upper/lower bounds when interference is missing.
Consequently a sub-percent-complete Γtotal has not been demonstrated.

For uncertainty materiality, a correlated 5% shift in the dominant bb channel
alone shifts the sum by about **3.12%/2.93%**. HDECAY's §2.5 discusses
non-factorizing EW effects at the several-percent level in doublet models;
that discussion is **not a certified Zee error band**. No ad hoc common K
factor, Gaussian 5–10% nuisance or SM precision error is assigned to these
cards. Missing corrections at the declared higher order are uncertainties;
missing potentially competing leading channels additionally block normalization.

## Source-matched production and absolute-μ numerators

Only three new native SusHi 1.7.0 runs were made: original h125 at D7/F13,
and a unit-quark-Yukawa SM reference at the same 125 GeV/13 TeV. Raw cards,
outputs, logs, exact executable/PDF lineage and environment are retained.

| Production | D7 σ/SM | F13 σ/SM | Accuracy/scope |
|---|---:|---:|---|
| ggF | 0.9038614042 | 1.0023312694 | LO QCD, coherent massive t,b,c |
| bbH | 1.1078083176 | 0.9741031250 | LO 5FS; κb² checked |
| VBF | 0.9976849708 | 0.9999939731 | Tree EW; common κW=κZ, factorizing QCD ratio |
| WH Drell–Yan | 0.9976849708 | 0.9999939731 | Tree EW, factorizing QCD ratio |
| ZH Drell–Yan | 0.9976849708 | 0.9999939731 | Only quark-initiated component |
| ttH | 0.9133962942 | 1.0009192344 | Tree EW, factorizing QCD ratio |
| Inclusive ZH | null | null | gg→ZH/interference contribution unqualified |

SusHi uses MMHT2014lo68cl, OS mb=4.78, μR=μF=M/2 (ggF),
μR=M and μF=M/4 (bbH). Absolute LO (ggF,bbH) pb are
D7 (17.9323833,0.399140040), F13 (19.8860007,0.350966457),
SM (19.8397489,0.360297024). These are not precision LHC-HXSWG cross sections.
The LO PDF uses αs(MZ)=0.135, unlike decay αs=0.118; each ratio has its own
matched denominator. Their combination is explicitly mixed-order, not one
uniform higher-order scheme. Production–decay uncertainty correlation is missing.

SusHi converts its charm input to an internal pole mass **3.20168553 GeV**
in this LO prescription. An analytic coherent amplitude must use that mass;
using the frozen photon mass 1.273 does not reproduce the production ratio.
With the printed internal mass, the independent coherent t,b,c expression
agrees within 3e−7 relative; dropping interference fails. This scheme artifact
and untested mass/PDF/scale dependence preclude a precision ggF claim. No
colorless scalar ggF graphs are inserted. No STXS shapes are supplied.

For `μ = N/(Γtotal/ΓSM)` the supported **numerators**, not signal strengths, are:

| N | D7 | F13 |
|---|---:|---:|
| ggF, γγ | 0.842214401 | 0.977298273 |
| VBF, WW* | 0.995375301 | 0.999987946 |
| VBF, bb | 1.104373249 | 0.974211283 |

Missing normalization remains explicit; the code rejects both incomplete totals
and missing production, including an attempt to replace missing widths by zero.

## Scoped experimental comparison gate

Selected **HiggsSignals ID 201108280**, pinned dataset commit
`3c6c2538d9ba0549ea0559cf9b38c18eb80c3af1`,
`h125/bb_vbfH_LHC13_ATLAS_126.json`, 126 fb−1, 13 TeV.
[ATLAS 2011.08280v2, Table 6/results](https://arxiv.org/html/2011.08280v2)
reports combined μVBF,bb=0.99 with total +0.36/−0.34 and
σVBF×BR=2.16 pb. The JSON encodes the latter with lower/upper endpoints
1.412939092/2.940320447 pb. These are **absolute-rate units**, not a bad
μ entry: `JsonSupport.cpp::readRateMeasurement` defaults a missing `ref`
to the reference particle's process rate. Its native SMHiggsEW reference
is **2.20257783862 pb** at 125 GeV (3.782 pb × 0.58238441).
The slightly different reference must be retained, not replaced silently.

The single pinned submeasurement has only `vbfH,bb`; it is simpler than a
STXS mixture but still comes from a fit with assumptions about other production
modes and a VBF+photon combination. D7's altered ggF component and model signal
uncertainty/acceptance need qualification. A complete model BRbb with errors
is the first missing input. **Zero model HiggsSignals calls** were made.
No χ², Δχ², p-value, observed exclusion or physical 95% CL is claimed.
Historical conditional 159-observable χ² outputs remain unchanged.

## Verification and release

Six focused checks pass: independent chiral phase space/all charges; incomplete
and missing→zero rejection; SM normalization and exact total cancellation;
charm-scheme/coherent-production controls; all on-shell exotic thresholds;
and native absolute-rate experimental convention. Native library, source,
card and output hashes accompany the receipts. Numerical residuals are not
physics uncertainties. The prior SM/signed-one-scalar photon controls are reused,
not rerun. There is deliberately no BR-sum PASS for incomplete widths.

```
python -m unittest research.full_constraints.higgs.test_h125_signal_strength -v
python -m research.full_constraints.higgs.h125_signal_strength
git diff --check
```

**Release:** partial-width ledger, declared-order production ratios and the
three width-independent observable ratios. **Do not release:** absolute μ,
normalized Zee BRs, a Higgs constraint, global PASS or a final scan. The next
decisive input is the h125-only competing-channel bound at the stated keV
precision, followed by model/reference uncertainty and selected-category
acceptance qualification. No heavy-H/A detour is needed.
