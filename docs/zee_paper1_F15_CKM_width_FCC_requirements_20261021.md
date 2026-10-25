# F15 — Source-closed charged Zee widths, missing CKM modes, and FCC-hh production requirements

**Scope:** Three original F13 benchmark IDs `F13_heavy_0001330`,
`F13_heavy_0000981`, and `F13_heavy_0001003`, as selected after
source-checked real 13-TeV F14 LHCHXSWG Santander production matching.

## AF command

    cd /home/aalida/zee
    git switch feature/global-scan-priority1
    git pull --ff-only
    bash scripts/zee_paper1_F15_charged_width_CKM_one_shot.sh

F15 refuses overwrite, validates F13/F14 summary+manifest provenance,
recomputes the **exact original complex f and Y neutrino mass matrix**
and the original B3 included charged widths from each priority JSON.
It requires exact closure against both the stored original charged branching
fractions and F14 production-normalized proxy. Reconstructed masses, tanbeta
and gamma must match; old-neutrino target exact closure is tested.

## Previously missing charged fermion channels

Old Gate6 included only `tb` in the charged quark inventory, and fixed
`mt=172GeV, mb=4.7GeV`, with CKM Vtb=1. F15 explicitly adds all 9
LO Type-II charged u_i d_j pair modes `ud,us,ub,cd,cs,cb,td,ts,tb`
at each charged-state mass, using approximate CKM absolute elements.
The old tb partial width is **replaced**, not added a second time.
The exact tree-level spin-trace formula reproduces Gate6 for mb=4.7
and Vtb=1 and is numerically tested on a real heavy CP-conserving
Zee scalar point with a true complex neutrino solution.

Because the old bottom-quark mass is a fixed pole-like input proxy,
F15 computes two **sensitivity scenarios** with mb=3.0 and 2.5 GeV
as well as the source mb=4.7 GeV. These are NOT running mass computations,
perturbative QCD predictions, NLO theory uncertainties or confidence bands.
These scenarios quantify potential branching-ratio instability.

The old included H2->H1 Z, H2->H1 h/H, H2->W h/H/A, H_i->tb,
H_i->lepton neutrino, and H1->W h/H/A inventories remain at
their documented original LO accuracy. F15 flags whether an omitted
possible mixed H2->H1 A two-body scalar channel is kinematically open;
the actual Lagrangian coupling would still need independent validation.
Loop-induced H2->H1 gamma, WZ and virtual three-body decays, QCD
corrections, pole-mass/renormalization-scheme treatment, and complete
five-state UFO/MadWidth widths remain unavailable. Thus NO physical
full total width or experimental allowance is claimed.

## 13-TeV rate correction at fixed included modes

Using original full-complex f/Y and B3 sources, F15 changes only the
nine-quark LO partial-width inventory. It propagates this replacement
through the H1_tb and H2_H1Z included fractions, and multiplies by
the same source-verified F14 unrescaled Type-II 13TeV matched rate.
The doublet weight sin^2gamma remains included ONLY ONCE. This is an
improved on-shell charged tree-subset estimate, not a full physical
decay probability or collider limit.

## FCC-hh comparison without invented hadronic production rates

F15 also outputs *required* baseline Type-II-like pp->tbH2 cross sections
for 10, 25, or 100 selected Z->ee/mumu events, at assumed full selection
efficiencies 1%, 5%, or 10%, using these two explicitly different
studied future-collider scenarios:

- 85 TeV, 20 ab^-1: 2025 FCC-hh Feasibility Study reference
  (e.g. https://indico.in2p3.fr/event/37608/contributions/165110/attachments/98271/151530/FCC-2511261030_MBE_FCC%20Status_ap.pdf).
- 100 TeV, 30 ab^-1: historical FCC-hh CDR physics-study reference
  (CERN-2025-006 foreword discusses this older baseline).

The algebra is N = L_fb * sigma_TypeII_fb *
P_included_Zee(contains sin²gamma) * 0.0673 * epsilon.
This only states what a future **real 85/100TeV** cross section would
need to exceed; it is **NOT an 85 or 100 TeV cross-section calculation,**
detector efficiency, or significance forecast. The future accelerator
energy/luminosity scenarios are not fixed experimental datasets.

## Output

Under `work/zee_paper1_F15_CKM_charged_widths_<UTC>/`:

- `F15_three_real_Zee_CKM_mass_stress_13TeV_NOT_COMPLETE.csv`;
- one `F13_heavy_<ID>_all_LO_quark_channels_NOT_FULL.json` per candidate;
- `F15_85_100TeV_required_TypeII_production_NOT_a_prediction.csv`;
- `summary.json`, `manifest.json`, output and source hashes.

## Mandatory next model-physics gate

Before detector-level sensitivities or publishable envelopes, construct
a truly gauge-consistent, source-matched full complex Zee UFO for the
actual F13 scalar/Y/f parameters, validate masses and amplitudes
independently, then run MadWidth 2/3-body decays, improve QCD widths,
and apply genuinely calibrated high-order B->Xs gamma and full LFV,
vacuum and HiggsTools restrictions. FCC-hh production additionally needs
a validated 85 or 100 TeV associated tbH2 prediction and dominant
background calculation. There is NO formal GO for a physics paper yet.
