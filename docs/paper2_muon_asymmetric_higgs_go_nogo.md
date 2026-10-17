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


## Step E — actual MG5 result and neutrino-Yukawa screening (2026-10-17)

**User-reported MG5 result: integrated rates, both charge conjugates.**

| E_CM | analytic Z-only, matched Yang/Wu EW | MG5 Z-only | MG5 all-tree, unfitted-lepton limit |
|---|---:|---:|---:|
| 1500 GeV | 0.58622616 fb | 0.585910 fb | 0.587394 fb |
| 3000 GeV | 0.27669813 fb | 0.277090 fb | 0.2773455 fb |

**Z-only analytic closure:** -0.0539% at 1.5 TeV, +0.1416%
at 3 TeV: PASS, much better than prespecified 5%.
**Full-tree/Z-only diagnostic:** +0.2533% and +0.0922%.
No integrated numerical uncertainties were provided. These small
differences are not a demonstrated muon-specific enhancement.

The existing diagnostic leptons have **f=0 and Type-II diagonal
charged-lepton Yukawa**; this is mathematically incompatible with
our nonzero Zee neutrino-mass targets, and must not be used as a
physical Yukawa-rate conclusion. The resulting gauge production
is equally available to an electron machine at equal energy.

**Upstream UFO technical blocker, independently verified:** the
Yang Ma/Yongcheng Wu `ZEE_UFO/parameters.py` declares
`fem`, `fet`, `fmt` and `ylzee`–`ylztt` as
`type='real'` external parameters, whereas our neutrino-compatible
B2 matrices contain **complex** entries. Real-part substitution
is not a consistent Zee model point. A FeynRules re-export with
appropriately declared complex parameters (and accompanying
imaginary SLHA blocks or equivalent) must retain Hermiticity
and validate charged-current vertices before physical MadGraph
Yukawa production can be calculated.

### Cheap flavor screen before a complex UFO re-export

The new `scripts/zee_muon_yukawa_screen.py` reads the saved 150
complex B2 Yukawa solutions and constructs only
muon-COLUMN invariants. The original Yang/Wu lepton Yukawa
Lagrangian is `-ylz[i,j] bar(LL_i) lR_j H2`; so the muon
coupling is the **column** `Y[:,mu]` (not the row `Y[mu,:]`).
The charged singlet antisymmetric `f[:,mu]` contributes to
other initial-state chiral structures.

For `H1 = cos(gamma)HD + sin(gamma)chi`,
`H2 = -sin(gamma)HD + cos(gamma)chi`,
muon-flavor-summed, same-chirality t-channel vertex PRODUCTS have
magnitudes proportional to
`|sin(gamma)cos(gamma)| * ||Y[:,mu]||²` and
`|sin(gamma)cos(gamma)| * ||f[:,mu]||²` separately.
The `f` vertex normalization, complex phase interference,
massless-neutrino propagators and complete helicity amplitudes
are NOT included. These norms are **not cross sections**,
and small numbers alone are not a calibrated exclusion.

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests -p 'test_zee_muon_yukawa_screen.py' -v

python3 scripts/zee_muon_yukawa_screen.py \
  --b2-json work/zee_pipeline_b4pilot_v2/B2_neutrino/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --output-dir work/zee_muon_B2_complex_yukawa_screen_v1
```

Read the maximum muon doublet/singlet overlaps and top-five
candidates, then decide if a complex parameter re-export is
justified. **Important selection bias:** B2 saved the five
**lowest partial-LFV-score** configurations per scalar point,
not the maximum muon collider Yukawa solutions. No conclusion
about all allowed Zee Yukawas can be drawn from those 150.

Paper 2 remains **GO for a Yukawa-specific physics pilot,
not yet GO for Delphes nor an independent publication**.
A genuinely muon-specific production effect must be shown
using the same complex f/Y solution that reconstructs neutrino
masses; then compare e+e- versus mu+mu- and evaluate the
full final state against backgrounds and BIB.


## Step F — user B2 muon-Yukawa screen: negative muon-specific evidence

On 2026-10-17, the user ran
`scripts/zee_muon_yukawa_screen.py` on all 150 B2 saved solutions:

- `MAX_MIXING_ABS_Y_Y = 5.8092699e-09`.
- `MAX_MIXING_ABS_f_f = 1.5016428e-07`.
- Top Y-column candidates:
  `B4_0000469` rank 2, `5.80927e-09`, partial LFV `3.04449e-08`;
  `B4_0000759` rank 5, `4.686855e-09`, partial LFV `1.47582e-07`;
  `B4_0000820` rank 5, `4.390315e-09`, partial LFV `4.84249e-07`;
  `B4_0000777` rank 5, `4.149567e-09`, partial LFV `1.22755e-07`;
  `B4_0000469` rank 3, `3.147335e-09`, partial LFV `5.27832e-08`.

**Interpretation**: In these deliberately low-partial-LFV-selected
neutrino-mass-closed B2 Yukawa solutions, the candidate t-channel
coupling products are extremely small compared with ordinary
electroweak gauge products; no plausible *large* muon-specific
enhancement is evident from the screen. This is NOT a computed
neutrino-exchange cross section, nor a universal no-go theorem
for all mathematically allowed general Zee Yukawas. All 150
configurations were biased by B2's partial-LFV top-five selection,
which suppresses large LFV couplings. Full LFV was not imposed.

**Updated literature warning:** Dev, Heeck and Thapa,
*Neutrino mass models at muTRISTAN*, EPJC 84 (2024) 148
https://doi.org/10.1140/epjc/s10052-024-12496-0
already studied the Zee model at a muon-based collider with
mu+e- and mu+mu+ beams, LFV processes, and neutrino correlations.
This is NOT our mu+mu- unequal-mass scalar pair mode,
but rules out a broad novelty claim of "first Zee muon collider
study." The ZH1H2 vertex was established earlier by
Florentino et al 2021.

**Current recommendation:** HOLD a mu+mu- detector-level Paper 2
based only on this Z-mediated rate; do not re-export the full complex
lepton-Yukawa UFO unless a targeted optimization/stress test
identifies significantly enhanced muon couplings under defensible
complete neutrino/LFV constraints. If no enhancement emerges,
either reframe as a *lepton-collider* mixed-pair reconstruction
study conditional on background-rejection novelty or prioritize
Paper 1 instead. No cross section has been calculated from
the 150 B2 f,Y complex solutions.


## Step G — expand beyond one benchmark (2026-10-17)

The validated numerical MG5 Z-only closure pertains ONLY to
`B4_0000318` (m1≈207, m2≈686, gamma≈1.185). The B2 low-partial-LFV
Yukawa screen covered 30 scalar spectra in a NARROW mass slice
(mH1≈203–351 GeV, mH2≈637–722 GeV) and is not a global Zee no-go.

The new `scripts/zee_muon_mass_mixing_grid.py` varies mH1, mH2,
gamma and energy using the already MG5-validated analytic Z-only
formula; all rows are marked kinematic-only, NOT allowed models.
It uses the matched Yang/Wu alpha/G_F/MZ derived sW²=0.2336991334,
not the former approximate fixed 0.23122 scheme. It includes both
charge-conjugate final states; reported luminosity-weighted counts
are **produced stable pairs before decay**, not final-state yields.
Kinematic flags require H1->tb open and H2->H1Z open; no
potential/stability/LFV/HiggsTools validity is inferred.

On AF:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_muon_mass_mixing_grid.py' -v

python3 scripts/zee_muon_mass_mixing_grid.py \
  --mH1-GeV 200,250,300,400,600,800 \
  --mH2-GeV 500,700,1000,1200,1500,2000 \
  --gamma-rad 0.4,0.7853981633974483,1.1845311184933986 \
  --energies-GeV 1500,3000,10000 \
  --luminosities-ab-inverse 0.5,1,10 \
  --output-dir work/zee_muon_P2_broad_mass_grid_v1
```

Outputs:
`mixed_pair_Z_only_mass_mixing_grid_NOT_ALLOWED.csv` and
`summary.json` with highest cross sections by energy
subject to kinematic H1->tb and H2->H1Z opening.

Examples at gamma=1.18453 (fb; Z-only, charge summed):

| mH1,mH2 GeV | 1.5 TeV | 3 TeV | 10 TeV |
|---|---:|---:|---:|
| (200,500) | 0.8655 | 0.2995 | 0.02945 |
| (200,700) | 0.5707 | 0.2752 | 0.02924 |
| (300,700) | 0.4931 | 0.2698 | 0.02920 |
| (300,1000) | 0.1143 | 0.2226 | 0.02875 |
| (400,800) | 0.2572 | 0.2478 | 0.02900 |
| (400,1200) | closed | 0.1792 | 0.02830 |
| (600,1200) | closed | 0.1592 | 0.02813 |

These are NOT independent MG5 validations at every mass/mixing
point. The full general-Zee allowed space may correlate masses and
gamma strongly via the scalar potential and EW precision constraints.

**Go/no-go amendment:** Do not declare Paper2 no-go from one
benchmark or the 150 low-partial-LFV Yukawa solutions.
Use the grid to select two additional distinct MASS benchmarks
and one near-maximal-mixing benchmark, then validate the mapped
UFO against the analytic Z result. Separately investigate whether
a physically viable choice of complex neutrino-compatible f,Y
can enhance muon t-channel production (requiring full LFV and
complex Yukawa UFO support). Still postpone Delphes until this
physics pilot justifies it.


## Step H — user broad mass grid: gauge rate peaks, but require B4 physical context (2026-10-17)

User executed `scripts/zee_muon_mass_mixing_grid.py` successfully:
297 analytic gauge-only rows (33 distinct ordered m1<m2 pairs × 3 gamma
× 3 energies). Truth-level maximum cross sections with gamma=pi/4:

| mH1,mH2 [GeV] | 1.5 TeV [fb] | 3 TeV [fb] | 10 TeV [fb] |
|---|---:|---:|---:|
| 200,500 | 1.77671 | 0.614786 | 0.0604597 |
| 250,500 | 1.70002 | 0.609758 | 0.0604186 |
| 300,500 | 1.60877 | 0.603649 | 0.0603683 |

At 0.5 ab^-1, these yield 888, 850, 804 produced **stable
charged-pair** events respectively, before all branching fractions,
top decays, acceptance, backgrounds or BIB. A higher production rate
alone is not a discovery significance; an mH1 around 200 GeV also
leaves a soft b from H1->tb. The (250,500) and (300,500) hypotheses
are more useful reconstruction starting points.

This mass grid is **not screened** for scalar theory, EWPO, flavor
or direct searches. In particular, charged masses around 250 and
500 GeV in a Type-II-like quark sector require a careful two-state
B->Xs gamma analysis; one cannot infer viability from the
existence of the gauge signal.

### Before more unrestricted MG5 benchmarks: rank the B4-scalar-screened points

Our Gate B4 existing pilot retained ~314 diverse
**scalar BFB/unitarity + correlated S,T,U**-screened records,
broader than the 30 B2-selected spectra. The new
`scripts/zee_muon_rank_B4_scalar_points.py` reads that original
full screened file, without treating the arbitrary grid as a physical
model, and ranks by s-channel Z-only rate and separately by
**B4 partial-width-conditional tb tb Z truth-count ceiling**.
The latter uses [BR(H2->H1Z)_included] ×
[BR(H1->tb)_included]^2. It cannot stand in for a complete
Zee branching fraction or statistical reach.

Run:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_muon_rank_B4_scalar_points.py' -v

python3 scripts/zee_muon_rank_B4_scalar_points.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/all_screened_candidates_NOT_ALLOWED.csv \
  --output-dir work/zee_muon_P2_B4_scalar_screened_rank_v1
```

It prints B4 mH1,mH2,gamma ranges, max gauge σ for each of
1.5,3,10 TeV, and four mass-bin-distinct candidate IDs/energies
with their *conditional* Z->ee,mumu truth ceilings. It writes
`scalar_EWPO_screened_Z_only_conditional_ceiling_NOT_ALLOWED.csv`
and `summary.json`.

The B4 records still originate from a narrow neighborhood of the
earlier 300/700-GeV benchmark. If the resulting mH1/mH2 ranges
do not include 250/500 or 300/500, the correct next work is a
**targeted correlated scalar-potential/EWPO exploration centered
on the new mass region**, not an unqualified claim that those
optimistic grid points are allowed. Independent MadGraph
cross-section checks at additional chosen physical candidates
are useful only once that parameter mapping can pass the
implemented scalar consistency gates.


## Step I — actual 314-point B4 scan and targeted correlated lighter-mass feasibility

User-reported result for `scripts/zee_muon_rank_B4_scalar_points.py`
(2026-10-17):

- 314 scalar BFB/unitarity + correlated STU-screened spectra; 942
  energy-scenario rows.
- Mass ranges mH1=201.128–371.712 GeV, mH2=593.040–725.033 GeV,
  gamma=1.02486–1.36850 rad. **The B4 scan did not reach
  the 250/500 or 300/500 region**; this is a limitation of
  that benchmark-seeded search, NOT an exclusion.
- Maximum gauge-only s-channel cross section:
  1.5 TeV **0.937342 fb**,
  3 TeV **0.445928 fb**,
  10 TeV **0.0472829 fb**.
- Maximum B4 *included-channel conditional*
  truth Z->e+e-/mu+mu-, H1->tb twice:
  **26.682, 25.7834, 27.373** events for the illustrative
  0.5, 1 and 10 ab^-1 luminosities.
- `B4_0000822`: (m1,m2)=(220.93,690.99) GeV, gamma=1.025,
  sigma(1.5 TeV)=0.92179 fb, conditional truth Zll=26.68,
  and b momentum in H1 rest frame about 43 GeV.
- `B4_0001150`: (255.95,691.49) GeV, gamma=1.05,
  sigma(1.5 TeV)=0.83088 fb, conditional truth Zll=23.11,
  and harder b momentum ~70 GeV, potentially better reconstruction.

The **high-rate 1.78 fb** mass-grid case at (200,500) GeV and
gamma=pi/4 remains an *arbitrary* gauge-kinematic hypothesis,
not even B4-screened. The main next physics question is whether
a nearby scalar spectrum at light mH2 can satisfy our implemented
potential and precision tests at all.

### New targeted correlated potential/oblique search

`scripts/zee_muon_targeted_light_scalar_scan.py` reuses
`gateB4_adaptive_zee_scalar_scan.scalar_screen`,
`ewpo_screen` and `make_record` with no cut changes.
It starts from the 314 B4-screened points and moves *together*:
- mH1 and mH2 toward selected 250/500,300/500,250/550,300/550;
- heavy neutral mH and pseudoscalar mA correlated with the charged scale;
- soft M² proportional to the squared charged scale;
- beta, alpha-beta, gamma (including a near-pi/4 proposal family);
- singlet lc, k1, k2 and k12 retaining their original sufficient BFB domain.

The experiment is stochastic and local to deformed B4 seeds;
**zero survivors does not exclude that mass region**. It records
counts for failed proposal-domain, scalar-theory, STU ellipsoid,
and numerical/partial-width gates separately. Accepted rows
have the complete original B4 CSV columns for provenance plus
muon collider gauge-only rate and **conditional** Zll truth counts.

Pilot:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_muon_targeted_light_scalar_scan.py' -v

python3 scripts/zee_muon_targeted_light_scalar_scan.py \
  --b4-csv work/gateB4_zee_adaptive_pilot/all_screened_candidates_NOT_ALLOWED.csv \
  --targets 250:500,300:500,250:550,300:550 \
  --trials-per-target 750 \
  --sources 32 \
  --quadrature-nodes 64 \
  --seed 20261017 \
  --output-dir work/zee_muon_P2_light_scalar_target_pilot_v1
```

Only if this has useful accepted scalar/EWPO spectra, increase
`--trials-per-target` to 3000 (new empty output directory).
If no samples pass, inspect rejection-stage fractions before
trying a correlated continuation/optimizer; do not loosen BFB,
unitarity or STU fits to force a benchmark.

**Scientific go/no-go:** Even with more scalar/EWPO survivors,
the physical published Paper 2 reach requires full neutrino/LFV,
Type-II-like quark flavor, HiggsTools direct search constraints,
complete Zee widths and SM backgrounds with muon BIB effects.
A high s-channel rate alone is not a muon-specific paper.


## Step J — user 43 successful targeted scalar+EWPO solutions and urgent Type-II flavor gate

User executed the `zee_muon_targeted_light_scalar_scan.py`
3,000-point correlated proposal pilot:

- 55/3000 passed the implemented Zee sufficient BFB/tree unitarity.
- 43/55 scalar survivors also passed BOTH correlated published
  3D S,T,U 95%-ellipsoid screens (43 distinct candidates, about
  1.43% of all **targeted nonuniform** proposals).
- Rejected: scalar 2904, outside original B4 proposal domain 35,
  mass/decay domain 5, EWPO 12, numerical or width 1.
  These rejection fractions are *proposal-specific* and not
  exclusion probabilities or parameter-space posterior volumes.
- Top conditional Z->e/mu event ceilings at sqrt(s)=1.5 TeV,
  0.5 ab^-1 (NO detector and NOT complete widths):
  - `P2L_0000563`: (225.5,527.7) GeV; gamma=0.832;
    gauge sigma=1.64516 fb; 44.29 Z->ee/mumu conditional events;
    b rest momentum 46.6 GeV.
  - `P2L_0001019`: (284.5,534.7) GeV; gamma=0.901;
    sigma=1.45745 fb; 35.26 conditional Zll events;
    b rest momentum 89.9 GeV.
  - `P2L_0001913`: (255.3,541.6) GeV; gamma=0.935;
    sigma=1.43450 fb; 37.67 conditional Zll events;
    b rest momentum 69.3 GeV.
  - `P2L_0002555`: (292.6,546.9) GeV; gamma=0.821;
    sigma=1.48001 fb; 40.05 conditional Zll events;
    b rest momentum 95.4 GeV.

**Urgent physics qualification:** Florentino, Romão and Silva,
EPJC 81 (2021) 1148, Sec.4.3.2, explicitly report that under
their historical two-charged Zee-Type-II `B->Xs gamma` treatment
points with **both charged Higgs masses below the standalone
Type-II ~580 GeV threshold are excluded** by their implemented
flavor cut; only one can be substantially lighter with the
other above that threshold. See:
https://link.springer.com/article/10.1140/epjc/s10052-021-09956-2
Sec.4.3.2 paragraphs under Fig.2 and Appendix C. All FOUR top
light-mass candidates have mH2=528-547 GeV, below 580 GeV,
so these collider-optimized mass points are HIGH RISK for
historical Type-II flavor rejection. A **modern 2026 two-state
NNLO theoretical/experimental likelihood has NOT been validated**,
and that historical threshold MUST NOT be copied as a current
hard statistical bound. The complete charged-Higgs flavor
observable must be evaluated pointwise.

### Next practical step: A1V diagnostic scan of all 43

The existing A1V source-audited two-state SuperIso backend can
scan the *original* P2L input CSV directly: it has all four
required columns `mH1,mH2,gamma,tanbeta`. No model rewrite,
standalone new gating layer or MG5 generation needed.

```bash
cd /home/aalida/zee
python3 scripts/gateA1v_run_legacy_response.py \
  --vendor-root work/gateA1m_isolated_nlo_v1/isolated_superiso \
  --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
  --a1u-result work/gateA1u_legacy_zee_br_v1/legacy_two_state_br.json \
  --grid-csv work/zee_muon_P2_light_scalar_target_pilot_v1/all_screened_candidates_NOT_ALLOWED.csv \
  --max-points 1000 --skip-scale-diagnostic \
  --output-dir work/zee_muon_P2_light_A1V_flavour_v1
```

Output `scan_flavour_only.csv` with all 43 B->Xs gamma
legacy predictions. **Do not report experimental accepted or
excluded points**: A1V is a source-validated *legacy diagnostic*,
not the NNLO-matched full likelihood. Comparison to the Florentino
2021 **historical** window
2.78e-4 < BR(B->Xs gamma) < 3.77e-4 is a qualitative
source-era stress test ONLY, not a current physical constraint.

If all 43 strongly overshoot that historical band, deprioritize
the lighter 500–550 GeV region and target mH2 >= 600–800 GeV with
larger mixed charged overlap and a heavier mH1 for reconstruction.
If some are close to the band, mark for independent modern
calibrated flavor check before expensive MG5/Delphes work.

Even if a modern two-state flavor calculation passes, we still
need neutrino-compatible general f/Y and fully predicted widths,
HiggsTools direct bounds, background/BIB and a muon-specific
novelty or reconstruction result.


## Step K — actual legacy B->Xs gamma for 43 lighter scalar/EWPO candidates (2026-10-17)

User ran Gate A1V for all 43 lighter scalar/EWPO-screened
P2L candidates. Saved `scan_flavour_only.csv`:

- count 43
- legacy BR mean 4.17e-4, std 0.12e-4,
  min 3.93e-4, median 4.17e-4, max 4.44e-4.
- 5 lowest: (m1,m2,gamma,tanbeta,BR):
  (275.411222,560.788383,1.431680,8.236477,3.93e-4),
  (313.094538,547.211799,1.273383,3.896588,3.98e-4),
  (301.250800,566.952471,1.144114,4.787277,4.01e-4),
  (277.508911,539.316858,1.233299,5.482108,4.02e-4),
  (243.347015,517.611128,1.309336,6.216845,4.03e-4).

**CRITICAL: comparing these absolute values to the 2021 Florentino
historical 2.78e-4 < BR < 3.77e-4 is INVALID** because the
same A1V legacy implementation yields SM-only BR approximately
3.9250054453230092e-4, which ALREADY violates the 2021 bound!
That procedure would exclude the benchmark generator's SM point.
Do not count 43 'excluded' candidates from this incompatible
SM baseline. The meaningful diagnostic is the *within-the-same-code*
NP shift
  delta_BR_legacy = BR_full_Zee_legacy - BR_SM_legacy,
not the absolute uncalibrated physical branching ratio.

The September 1, 2026 SM update by Tobias Huber,
arXiv:2609.01005, reports [E_gamma > 1.6 GeV]:
  BR_SM=(3.54 +/- 0.14)e-4,
  BR_exp=(3.49 +/- 0.19)e-4.
See https://arxiv.org/abs/2609.01005 .
These are the most recent published references identified in
this audit. The proceedings reference supplies an updated SM
baseline, NOT an NNLO-matched Zee NP prediction. DO NOT combine
'new 2026 SM BR + old SuperIso deltaBR_legacy' and label it
physical NNLO. The Wilson matching/evolution, interference
and uncertainties are scheme dependent.

The minimum-BR sample at gamma=1.431680 has
sin²(2gamma)≈0.075, and independently validated *analytic*
Z-only charge-summed cross section ≈0.112 fb at 1.5 TeV:
flavor suppression via singlet mixing comes at significant cost
to asymmetric charged-pair collider production. Other low-BR
samples have higher rates and merit Pareto analysis (small
legacy deltaBR vs large sigma or conditional truth yield).

**Updated decision:** neither declare the 43 points experimentally
excluded nor promote to allowed. Do not spend on Delphes.
Report a provenance-consistent 43-point deltaBR–sigma Pareto
frontier, then resolve modern two-state b->s gamma normalization
and current combined experimental/theory likelihood before
selecting physical benchmarks. For Type-II-like quarks, charged
mass eigenstates contribute to Wilson coefficients with the
doublet weights cos²gamma and sin²gamma at matching, not as
a naive sum of charged-Higgs branching fractions.


## Step L — P2L 43-point A1V deltaBR–collider Pareto frontier, and SM-baseline ERRATUM (2026-10-17)

User joined the 43-point scalar/EWPO-screened lighter spectra to
Gate A1V `scan_flavour_only.csv`, matching all four charged-flavor
inputs exactly, and obtained 13 nondominated points when minimizing
`full_Zee_BR - SM_BR` and maximizing analytic, both-charge Z-only
sigma at sqrt(s)=1.5 TeV. Representative records:

| Candidate | mH1, mH2 [GeV] | gamma | deltaBR_legacy [10^-4] | sigma_Z [fb] | conditional Zll truth (0.5 ab^-1) |
|---|---|---|---|---|---|
| P2L_0001962 | 275.4,560.8 | 1.432 | +0.5466 | 0.1115 | 0.46 |
| P2L_0002450 | 301.3,567.0 | 1.144 | +0.6274 | 0.8014 | 16.78 |
| P2L_0002457 | 297.4,579.1 | 1.023 | +0.6780 | 1.0929 | 25.29 |
| P2L_0002267 | 299.6,555.8 | 0.979 | +0.7197 | 1.2405 | 32.00 |
| P2L_0000563 | 225.5,527.7 | 0.832 | +0.9924 | 1.6452 | 44.29 |
| P2L_0000481 | 258.8,482.7 | 0.717 | +1.0209 | 1.7021 | 35.73 |

**ERRATUM — earlier Step K erroneously compared/identified
A1V's SM reference as 3.9250054453230092e-4.**
That number came from a separate A1U *fixed-low* diagnostic,
and must not be asserted to equal the within-run `SM_BR` in
the A1V Pareto data. The user's printed A1V results imply a
lower common SM reference around **3.38e-4**, e.g.
3.93e-4 - 0.5466e-4 ~ 3.3834e-4.
This is an approximation using rounded printed absolute BRs,
**NOT independent verification of the exact SM_BR field**.
Before assigning physical significance, read the original
`SM_BR` values from `scan_flavour_only.csv` and verify
their uniqueness and consistency with the A1V `SM_BR` column.
The C backend defines its SM rate as the unperturbed
k=0 Wilson-coefficient member `b0 = br[1]`, independently
checked by `real_br(&sm,...)`. It must not be substituted
with A1U fixed-low SM.

The primary Misiak et al. 2026 updated calculation is
https://arxiv.org/abs/2608.29863, reporting
BR_SM=(3.54 +/- 0.14)e-4, BR_exp=(3.49 +/- 0.19)e-4
(Egamma>1.6 GeV) and a **95% CL single-Type-II-2HDM
charged-Higgs lower mass bound 670 GeV**. This does not
directly exclude either Zee mass eigenstate: both charged
doublet fractions enter the Wilson coefficients, approximately
cos²gamma C7,8^TypeII(mH1) +
sin²gamma C7,8^TypeII(mH2) in the alignment/quark
Yukawa convention being screened.

The Pareto frontend's small-legacy-deltaBR points sacrifice
gauge-production rate; the maximum-rate ones have
deltaBR_legacy around +1e-4. It is inappropriate to
treat `deltaBR_legacy` as an NNLO correction to be
naively added to Misiak 2026 SM. These numbers point to
potential modern-flavor tension, not a calibrated 95% CL
exclusion. P2L_0002457 is a useful *conditional study point*:
mH1~297 GeV (b-rest momentum ~98.6 GeV), mH2~579 GeV,
sigma~1.093 fb, deltaBR_legacy~0.678e-4;
it is explicitly NOT currently "allowed".
Prioritize modern two-state Wilson-matching and full-theory
uncertainty validation before committing to MG5 cascades or
detector-level publication claims.

**One-line AF check** to settle A1V SM baseline:
```bash
python3 - <<'PY'
import pandas as pd
p='work/zee_muon_P2_light_A1V_flavour_v1/scan_flavour_only.csv'
d=pd.read_csv(p)
print('A1V SM_BR unique values:',d.SM_BR.unique())
print('A1V SM range:',d.SM_BR.min(),d.SM_BR.max())
print('A1V NP shifts range:',(d.full_Zee_BR-d.SM_BR).min(),(d.full_Zee_BR-d.SM_BR).max())
PY
```


## Step M — A1V SM baseline independently reported by the actual 43-point AF run

The user supplied `pandas.DataFrame.describe()` directly from
`work/zee_muon_P2_light_A1V_flavour_v1/scan_flavour_only.csv`:

- `SM_BR`: **3.382458e-4** uniformly across all 43 points
  (standard deviation 5.49e-20).
- `full_Zee_BR-SM_BR`: **+0.55 to +1.06** in units 1e-4;
  mean **+0.78e-4**, std **0.12e-4**.
- `linear_delta_BR`: mean **+0.74e-4**, range
  **+0.53 to +0.99e-4**.
- `quadratic_delta_BR`: mean **+0.04e-4**, range
  **+0.02 to +0.07e-4**.
- `max |delta - linear - quadratic|=7.939070408025106e-17`.

This directly and decisively **corrects the earlier Step K
incorrect A1U fixed-low SM=3.925e-4 statement**:
A1V's exact within-run k=0 SM reference, controlled by C backend
`b0=br[1]` and independent `real_br(&sm,...)` call,
is 3.382458e-4. Nearly 95% of the mean NP branching-ratio
increase is interference; the smaller quadratic term cannot
resolve the positive shift.

**Physics priority is now decisive under the Type-II-like quark
assumption.** Florentino et al (2021), EPJC 81 1148,
Sec. 4.3.2, explicitly showed both charged Higgs states
below their old 580-GeV Type-II threshold were outside their
B->Xs gamma band. The 2026 Misiak et al.
arXiv:2608.29863 modernized single-Type-II lower bound is
670 GeV at 95% CL, with SM 3.54 +/-0.14 e-4 and experiment
3.49 +/- 0.19 e-4. **All 43 new P2L candidates have both
charged masses below 670 GeV**. The Yukawa mixing does not
yield opposite-signed quark-loop contributions:
X1=tan(beta)cos(gamma), Y1=cot(beta)cos(gamma);
X2=-tan(beta)sin(gamma), Y2=-cot(beta)sin(gamma);
hence X_i Y_i* are nonnegative cos²/sin² weights.
A two-state NNLO confidence-level calculation has NOT
been performed, so no literal model-wide CL exclusion
should be claimed yet.

**Low-cost diagnostic next:** for all 43 original P2L tanbeta
values, run A1V *at the same tanbeta* with
`mH1=670,mH2=700,gamma=0`, yielding a **single**
physical-quark-Type-II charged scalar at 670 GeV (H2 decoupled).
Compare each `deltaBR_Zee` against the single-Type-II
`deltaBR_670` using the SAME legacy SuperIso internals,
and verify its SM_BR agrees with the P2L SM_BR. A finding
`deltaBR_Zee > deltaBR_670` uniformly would be a strong
*within-the-same-legacy-scheme* ranking of flavor pressure,
though still not a 2026 95%-CL two-state exclusion.
This control does not require new model/UFO generation.

No Delphes yet, and do not prioritize light mH2~500-GeV
collider yields until this flavor risk is settled.
