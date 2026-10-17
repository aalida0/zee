# Paper 2 pre-Delphes go/no-go: asymmetric charged-Higgs production at a muon collider

**Study status (2026-10-17):** analytic Z-only signal feasibility and
B4-to-Yang/Wu scalar card mapping committed. *No MG5 rates run for this
study, no detector sensitivities calculated, and no fully allowed Zee
benchmarks established.*

## Proposed physics

mu+mu- -> H1+ H2- + H1- H2+,
H2+- -> H1+- Z,
H1+- -> t b.

The off-diagonal ZH1H2 vertex is already established by
Florentino, Romao, Silva, EPJC 81 (2021) 1148:
https://link.springer.com/article/10.1140/epjc/s10052-021-09956-2

This is **not** the same as ordinary 2HDM H+H- pair production,
but the Z-only source is equally available in e+e- annihilation
at the same sqrt(s), neglecting lepton masses. Thus publication
requires an additional distinction: muon-specific Yukawa-mediated
production; reconstruction of both unequal scalar masses;
neutrino–Yukawa correlation; or demonstrable complementarity to
e+e- and pp machines.

Related precedent:
- Ait Ouazghour et al, PRD 110 (2024) 095026, associated charged
  Higgs production in the 2HDM at e+e- versus muon colliders:
  https://arxiv.org/abs/2408.13952
- Han et al, BSM Higgs Production at a Muon Collider (2022):
  https://arxiv.org/abs/2205.11730
- Jueid et al, Probing Zee-Babu states at muon colliders (2024),
  a DIFFERENT model: https://doi.org/10.1103/PhysRevD.109.075011
- 2024 Zee-type related off-diagonal coupling discussion:
  https://doi.org/10.1103/PhysRevD.109.095002

Targeted literature search did not identify a direct published
Zee **unequal-mass charged-pair at muon collider** detector study.
That is a provisional gap, not guaranteed novelty.

## Analytic Z-only cross section and checks

From Florentino Appendix B,
g_ZH1H2 = +/- e/(4 sW cW) sin(2gamma);
g_Zmu,L = e/(sW cW) (-1/2+sW²),
g_Zmu,R = e/(sW cW) (sW²).

With s=E_CM² and
beta12=sqrt[(1-(m1+m2)²/s)(1-(m1-m2)²/s)],
the tree-level unpolarized rate per charge-conjugate channel is

sigma_one = pi alpha²/(3s) * beta12³
  * sin²(2gamma) *
    [(-1/2+sW²)²+(sW²)²]/[32(sW²(1-sW²))²]
  * [s/(s-mZ²)]².

sigma_sum = 2 sigma_one, because H1+H2- and H1-H2+
are distinct final states. This normalization is independently
compared with textbook scalar QED
sigma(e+e- -> H+H-)_photon = pi alpha² beta³/(3s).
No off-diagonal photon vertex exists. Angular signal at Born level:
d sigma/dcos(theta) proportional sin²(theta). The unequal-mass
beta12³ vanishes at threshold.

Use fixed alpha=1/128, sW²=0.23122, mZ=91.1876 GeV.
Do not conflate this fixed-scheme LO approximation with
MG5 EW input scheme; exact numerical closure requires matching them.

For B4_0000318, m1=207.258 GeV, m2=686.474 GeV,
gamma=1.184531, gauge-only **charge-summed**:
- sqrt(s)=1.5 TeV: sigma = 0.594902 fb;
- sqrt(s)=3 TeV: sigma = 0.280793 fb;
- sqrt(s)=10 TeV: sigma = 0.0296865 fb.

Production near 1.5 TeV is more effective per unit luminosity
than 3 TeV for these masses, but published collider luminosity
assumptions must be attached to energy choices.

**Approximate truth-only event ceiling** using the B3 *included
channel* branching fractions for this benchmark,
BR2(H2->H1Z)=0.793008,
BR1(H1->tb)=0.99978,
and both H1 -> tb (thus BR1²):

 Energy | assumed L | produced pairs | tb tb Z | Z->ee,mumu | Z->hadrons
 1.5 TeV | 0.5 ab-1 | 297 | 236 | 15.9 | 165
 3 TeV | 1 ab-1 | 281 | 223 | 15.0 | 156
 10 TeV | 10 ab-1 | 297 | 235 | 15.8 | 165

These are deliberately **illustrative luminosities**, not
machine guarantees. All yields are before top branching,
object cuts, b tagging, trigger, detector acceptance, ISR, BIB,
or reconstruction. They are **not signal significances**.
The B3 included-only fractions are NOT model-complete physical BRs.

For H1~207 GeV and t~172.5 GeV, rest-frame b momentum
p*=31.61 GeV, potentially worsening separation and tagging
of H1->tb near threshold, especially in boosted topologies.
The distinct two mass resonances m_tb~m1 and
m_tbZ~m2 are the main reconstruction handles.

## Existing code and exact next step

The repository ALREADY has a Yang/Wu original Zee model with
a locally exported Type-II-like QUARK extension:
`work/Zee_TypeII_LO_UFO` (on AF; not Git-tracked).
MadGraph v3.5.9 previously passed static diagram generation
for Z Hheavy Hlight and tb Hheavy/light:
`docs/gate7c_af_lo_ufo_smoke_pass.md`.

*CRITICAL*: existing Gate7 original
`gate7_map_p2_to_yangwu.py` accepted only default scalar
params. It is now generalized to accept B4 physical spectra:
alpha,gamma,m12sq,mh2,ma,lc,k1,k2,k12.
`gate7_make_diagnostic_param_card.replacements()` also
accepts these scanned options and internally verifies mass/angle
consistency. This avoids silently mapping the NEW m1~207,m2~686
point to OLD (300,700) scalar potential.

The resulting diagnostic card uses f=0 and Type-II diagonal
lepton Yukawas: NOT fitted neutrino masses. Its DECAY widths
are stale; no physical cascade event generation is valid.

### Step A — reproduce analytic rates on all 30 B4C points

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source ~/fccee_zh/scripts/setup_key4hep.sh

python3 -m unittest discover -s tests \
  -p 'test_zee_muon_asymmetric_pair_pilot.py' -v

python3 scripts/zee_muon_asymmetric_pair_pilot.py \
  --joined-csv work/zee_pipeline_b4pilot_v2/B4C_joint_audit/joint_scalar_neutrino_width_flavour_NOT_ALLOWED.csv \
  --output-dir work/zee_muon_P2_gauge_pilot
```

The CSV contains 30 candidates × 3 energies = 90
charge-summed cross-section/conditional-yield rows and
the H1->tb rest-frame b momentum.

### Step B — build B4_0000318 mass/potential matched MG5 card

The template is from the previous Gate7 smoke process; keep
the original untouched.

```bash
python3 -m unittest discover -s tests \
  -p 'test_zee_muon_make_scalar_card.py' -v

python3 scripts/zee_muon_make_scalar_card.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --candidate-id B4_0000318 \
  --ufo-template-param-card work/gate7_mg5_typeii_smoke/Associated_4FS/Cards/param_card.dat \
  --output-card work/zee_muon_B4_0000318_scalar_matched_DIAGNOSTIC.dat \
  --acknowledge-unfitted-neutrino-sector

python3 scripts/gate7_preflight_card.py \
  work/zee_muon_B4_0000318_scalar_matched_DIAGNOSTIC.dat \
  --b4-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --candidate-id B4_0000318
```

### Step C — independent MG5 Z-only and full-tree diagrams

```bash
python3 scripts/zee_muon_prepare_mg5.py \
  --ufo work/Zee_TypeII_LO_UFO \
  --output-dir work/zee_muon_mg5_B4_0000318_decks

export MG5_BIN=/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/madgraph5amc/3.5.9-3xnfke/bin/mg5_aMC

"$MG5_BIN" work/zee_muon_mg5_B4_0000318_decks/Z_only.mg5
"$MG5_BIN" work/zee_muon_mg5_B4_0000318_decks/full_tree.mg5
```

These commands **generate diagrams, not numeric cross sections**.
The Z-only process restricts diagrams to an off-shell s-channel
Z using MG5 syntax (mu+ mu- > z > H+ h-). This is an analytic
normalization diagnostic. The full tree process also includes any
available neutrino t-channel or neutral-Higgs interactions for
the specified (currently *unfitted*) lepton Yukawas.

After diagram gate, copy the new matched SLHA card into each
*generated* subprocess's Cards/param_card.dat and use
beam energies lpp1=lpp2=0, ebeam1=ebeam2=E_CM/2.
Do not generate events from the stale DECAY card;
integrate **stable H+ h-** pair production first.
Only when the gauge-restricted MG5 integrated cross section
matches the analytic calculation at a common EW input scheme
should one compare full tree to Z-only. Process restrictions
can violate gauge invariance in general; the full tree is the
reference for physical production after Yukawa completion.

## BLOCKER: neutrino-compatible muon-specific enhancement

The Yang/Wu UFO contains general lepton Yukawa parameters
ZEEYUKAWAF and ZEEYUKAWAY but its default external couplings
are real, whereas B2 fits COMPLEX f and Y. The 2026 tuned
scalar card intentionally uses f=0 and nonphysical Type-II
lepton Yukawa. A complete flavor UFO card requires compatible
complex couplings, a consistent Higgs basis/phases and PMNS,
matching neutrino and charged leptonic decay amplitudes.
**Do not infer an allowed t-channel enhancement using this
diagnostic Type-II-lepton card.**

Next develop a general Zee lepton UFO exporter allowing
complex f and Y, then compare full and Z-only MG5 predictions
for several B2 solutions spanning muon-row couplings.
Include E+E- versus muon comparison with the same gauge
and neutral-scalar parameters, so we know whether the machine
choice adds genuine physics rather than BIB complications.

## Detector feasibility and decisive backgrounds

Truth channel:
mu+mu- -> Hheavy+- Hlight-+ -> Z Hlight+ Hlight-
 -> t tbar b bbar Z.

One should test:
- Z->ee,mumu with both tops hadronic and semileptonic;
- Z->qq if jet combinatorics and BIB are manageable;
- mass-based pairing m(tb)~mH1 and m(tbZ)~mH2;
- SM t tbar b bbar Z irreducible background, including
  electroweak + QCD contributions and t tbar Z plus jets,
  with consistent diagrams and generation-level cuts;
- BIB effects, b/top tagging, ISR and reconstruction.

A previous official *generic target* Delphes muon card explicitly
states it is NOT validated by full simulation:
https://github.com/delphes/delphes/blob/master/cards/delphes_card_MuonColliderDet.tcl
A 2024 official muon-collider fast-simulation release:
https://zenodo.org/records/14001529
and MAIA performance with BIB:
https://arxiv.org/abs/2502.00181 .
No universal Delphes card is equivalent to a full muon-collider
BIB-overlay simulation. Sensitivity forecasts must label this.

## Decision criteria

Proceed to a full Paper 2 detector study only if:
1. Independent MG5 Z-only LO agreement (EW-scheme matched)
   within ~2–5% numerical integration/inputs; any discrepant
   vertex-factor-of-two is a STOP.
2. The chosen allowed-BSM-inspired benchmark does not rely
   on missing Type-II quark/lepton symmetry assumptions;
   neutrino Yukawas and scalar widths can be represented.
3. Signal topology has adequate reconstructable event yields
   and a statistically meaningful improvement over full SM
   backgrounds with BIB/efficiency robustness.
4. There is a distinctive muon-collider result relative to
   equivalent e+e- gauge production (or a novel reconstruction
   result beyond an existing topology).
5. Clear non-overlap with Paper 1: model constraints can be
   imported, but not counted as a second independent physics result.

If the leptonic Z channel stays <= O(10) selected events and
hadronic Z fails over backgrounds, revisit the second paper
process instead of forcing an optimistic sensitivity plot.


## Step D — MG5 numerical stable-pair cross-section closure (now implemented)

After both diagram-generation decks complete, use
`scripts/zee_muon_integrate_mg5.py` to run four independent
parton-only LO integrations and compare the **charge-summed**
Z-only cross section against the analytic result at the
**same Yang/Wu UFO electroweak scheme**.

The original Yang/Wu Parameters.fr does not use externally specified
sin²thetaW; it derives MW from SMINPUTS alpha and GF plus MASS[23]=MZ,
then computes sin²thetaW=1-(MW/MZ)². The runner computes that same
tree-level input scheme before evaluating the analytic reference;
this prevents misleading percent-level discrepancy with the
illustrative fixed sin²thetaW=0.23122 values from Step A.

Test it before executing:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_muon_integrate_mg5.py' -v

python3 scripts/zee_muon_integrate_mg5.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
  --candidate-id B4_0000318 \
  --param-card work/zee_muon_B4_0000318_scalar_matched_DIAGNOSTIC.dat \
  --z-only-dir work/zee_muon_mg5_B4_0000318_decks/MG5_Z_only \
  --full-tree-dir work/zee_muon_mg5_B4_0000318_decks/MG5_full_tree \
  --energies-GeV 1500,3000 \
  --events 3000 \
  --tolerance 0.05 \
  --output-dir work/zee_muon_P2_mg5_xsec_v1
```

If the dry preflight passes, rerun with the same arguments and add
`--execute`. The runner verifies the process cards contain **both
charge conjugates**, the fully matched B4 scalar + singlet quartic
card, and antisymmetric f=0 (so it *cannot* be mislabeled a neutrino
fit). It backs up each generated process's default run/param cards
once, configures lepton beams `lpp1=lpp2=0`, unpolarized
`polbeam1=polbeam2=0`, beams at `E_CM/2`, no shower/detector,
and runs:

```text
bin/generate_events P2Z1500 -f --laststep=parton
bin/generate_events P2Z3000 -f --laststep=parton
bin/generate_events P2F1500 -f --laststep=parton
bin/generate_events P2F3000 -f --laststep=parton
```

Cross sections are extracted from each LHE banner
`<MGGenerationInfo> Integrated weight (pb)` and reported in
fb. They are NOT scraped from console text.

Output: `cross_sections.csv`, `manifest.json`, four run logs,
and normal MG5 events in their process output directories.

**Strict stop conditions:** if the Z-only integration differs from
the matched analytic reference by more than 5%, report
`Z_ONLY_CLOSURE_FAIL_STOP` and do NOT interpret full-tree
enhancements; inspect EW scheme, process definitions,
Hheavy/Hlight angle mapping and normalization. This threshold
is a numerical integration/input sanity criterion, not a
theory uncertainty. Do not fit the threshold to make it pass.

The full-tree diagnostic is **NOT** a physical muon-specific
neutrino-exchange enhancement: f=0, Type-II-like diagonal charged
lepton Yukawa are an artificial tree-level reference. Complex
neutrino-compatible f,Y from B2 require a separate mapped UFO
card with verified flavor convention.
