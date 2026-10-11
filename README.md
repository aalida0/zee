# Zee-type charged-Higgs discovery pilot

This repository is for a **14 TeV HL-LHC feasibility study** of the Zee-type scalar-sector cascade

```
pp -> tbar b H2+  (+ charge conjugate)
                  H2+ -> H1+ Z
                         H1+ -> t bbar
```

The characteristic final state is `ttbar + bbbar + Z` (four b quarks before acceptance). Candidate channels include `Z -> ee/mumu`, with one top decaying leptonically, and a **3-lepton + at least 3 b-tags** signal region.

Reference: Florentino, Romão, Silva, *Off diagonal charged scalar couplings with the Z boson: Zee-type models as an example*, EPJC 81 (2021) 1148, [arXiv:2106.08332](https://arxiv.org/abs/2106.08332), [DOI](https://doi.org/10.1140/epjc/s10052-021-09956-2).

## Why a 2HDM UFO appears in a two-charged-Higgs study

A **standard 2HDM** has one charged mass-eigenstate pair `H+`/`H-`: these are antiparticles of **one** species. The official FeynRules `2HDMtII_NLO` UFO represents it with `h+` and `h-` (PDG ±37).

A **Zee-type 2HDM plus charged singlet** has **two different physical charged-Higgs pairs** `H1+`/`H1-` and `H2+`/`H2-`. They arise because the charged doublet scalar mixes with the charged singlet, with angle gamma:

```
H1+ =  cos(gamma)*H_D+ + sin(gamma)*chi+
H2+ = -sin(gamma)*H_D+ + cos(gamma)*chi+
```

For the paper's Type-II-like **quark sector**, only `H_D+` couples directly to `tb`. At *leading order*, a 2HDM **production-only proxy** of mass `mH2` and matching `tanbeta` can be converted as

```
sigma(pp -> tb H2±) ≈ sin(gamma)^2 * sigma_2HDM(pp -> tb h±)
```

provided the Born amplitudes are governed by those same Yukawas. This factor is **not a full Zee-model calculation** and does not provide its decay kinematics, widths, or validated branching ratios. It is only an economical first **rate-screening gate**.

In MadGraph,

```
generate p p > t~ b h+
add process p p > t b~ h-
```

are the positive and negative charge-conjugate production channels of the **single** 2HDM `h±` species. They are **not** `H1` and `H2`! The full cascade requires a distinct Zee-model UFO that contains both charged states and the `Z H1 H2` interaction.

## Illustrative input (not a validated point)

The source's P2 benchmark region contains `alpha=1.398`, `gamma=1.089`, `mH1=250–360 GeV`, and `mH2=635–800 GeV`. The *selected illustrative pair* `mH1=300`, `mH2=700 GeV`, `beta=alpha` gives `tanbeta=5.7294463`, `sin(gamma)^2=0.7852866`. This mass pair has **not been shown simultaneously viable**, and the reference does **not** fully fit neutrino masses or charged-lepton flavour violation.

**Stop conditions:** No full event simulation or claimed discovery sensitivity until (i) a viable exact Zee parameter point is established; (ii) the 14 TeV production rate is calculated and its scheme/PDF/scale uncertainty assessed; (iii) a two-state Zee UFO is validated including `H2 -> H1 Z`; and (iv) event acceptance and the dominant `ttZ+heavy-flavour` background are quantified.

## Workflow on AF — run and store the pilot under /home/aalida

**Do not reuse the /data MG5 process directory.** Its cards were corrupted by an earlier
line-ending bug. The repaired editor preserves all line breaks and has regression tests.
MG5 setup now refuses to run when the repository is under /data.

```bash
cd "$HOME"
git clone https://github.com/aalida0/zee.git  # if not already cloned
cd "$HOME/zee"
mkdir -p models
cp -a /data/aalida/zee/models/2HDMtII_NLO models/

source ~/fccee_zh/scripts/setup_key4hep.sh
python3 -m unittest discover -s tests -v

MG5_BIN=/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/madgraph5amc/3.5.9-3xnfke/bin/mg5_aMC \
  bash scripts/setup_4fs.sh

cd "$HOME/zee/work/ZeeProductionProxy_4FS_14TeV"
grep -A12 -i 'block mass' Cards/param_card.dat | head -15
grep -A4 -i 'block frblock' Cards/param_card.dat
./bin/generate_events run_01 -f 2>&1 | tee "$HOME/zee/work/gate3_run01.log"
```

If $HOME/zee already exists, do not clone twice: run
```bash
cd "$HOME/zee"
git pull --ff-only
```

Do **not** copy the corrupted process output from /data into $HOME.
Copy **only** the original extracted UFO from the prior model directory.
The proxy uses m(h±)=700 GeV, tanbeta=5.7294463, sin(beta-alpha)=1 at 14 TeV.
Convert its LO cross section to the Zee heavy charged state with sin(1.089)^2 = 0.7852866.
This is production-only and cannot model H2± -> H1± Z.

Review Cards/param_card.dat and Cards/run_card.dat before launching. Internal
pdlabel=nn23lo1 is for an initial rate screen, not a production-quality nf=4 PDF.
Never add four-flavour and five-flavour cross sections.

The `models/`, `work/`, and `results/` directories hold locally downloaded model files and generated outputs and are ignored by Git.

## Gate 4: first actual LO production rate

MG5 4FS Type-II proxy at 14 TeV, m(h±)=700 GeV, tanβ=5.729446:
`σ_2HDM^LO = (0.008737 ± 0.00004079) pb`, both charges.
Scaling by sin²γ = 0.7852866098 yields `σ_Zee^LO,proxy = 6.86105 fb`.
The quoted error is **only integration uncertainty**, not PDF/scale/4FS theory uncertainty.

Reproduce the rate and **assumption-dependent** yields with the new calculator:

```bash
cd ~/zee
git pull --ff-only
python3 -m unittest discover -s tests -v
python3 scripts/gate4_rate_summary.py --mg5-log work/gate3_run01.log \
  --output work/gate4_rate_summary.json
```

At 3 ab−1 with **illustrative** BR(H2→H1Z)=0.70 and BR(H1→tb)=0.95:
the direct-e/μ 3-lepton mode has `2×0.216×0.674 = 0.291168` top branching fraction,
and `N≈268` before detector selection. An assumed 5% (10%) selection
efficiency would leave ≈13 (27) signal events. The old 0.338 top branching
factor was incorrect for direct e/μ and has been corrected. No real
acceptance, model completeness or background significance is established.

**Next gate before full detector simulation:** construct an exact simultaneously
allowed P2-like Zee scalar potential point (the illustrative 300/700 GeV
masses are not validated), include all open competing decays in the total
H2/H1 widths (including bosonic channels), recheck flavour/Higgs/electroweak
constraints and the untested Zee neutrino/LFV sector. Then assess acceptance
versus `ttZ+bb` and other irreducible backgrounds. Do not infer discovery from
the inclusive cross section alone.

## Gate 5A: FCC-hh 80–100 TeV LO rate screen

Two complementary channels: (A) tbH2± (Type-II 2HDM Yukawa-production proxy, scaled by sin²γ),
and (B) pp→Z*→H1+H2- + H1-H2+ (off-diagonal Z-coupling Drell–Yan).
The photon coupling of differently-massed charged scalars is diagonal; the mixed channel is Z-mediated.
These are NOT full constrained Zee-model predictions: neither the illustrative P2 masses
nor total widths and branching fractions have been validated.

Start under /home/aalida/zee; do not run MG5 in /data.
```bash
cd ~/zee
git pull --ff-only
source ~/fccee_zh/scripts/setup_key4hep.sh
python3 -m unittest discover -s tests -v
python3 -c 'import lhapdf; print(lhapdf.availablePDFSets()[:40])'
```

The analytic mixed-pair calculator needs an installed five-flavor LO LHAPDF set.
If NNPDF31_lo_as_0130 is not listed, supply an installed suitable LO set explicitly.
```bash
cd ~/zee
python3 scripts/fcc_hh_mixed_pair_dy.py \
 --energy-tev 80 100 --m1 300 --m2 700 \
 --pdf-set NNPDF31_lo_as_0130 --nodes-tau 60 --nodes-y 40 \
 --output work/fcc_hh_mixed_pair_lo.json
python3 scripts/fcc_hh_mixed_pair_dy.py \
 --energy-tev 100 --m1 300 --m2 700 \
 --pdf-set NNPDF31_lo_as_0130 --nodes-tau 90 --nodes-y 60 \
 --output work/fcc_hh_mixed_pair_lo_highres.json
```

The JSON sigma_both_charges_fb is a parton-level inclusive rate before
decays, b-tagging, and backgrounds. Check integration convergence.
The calculation implements ONLY the s-channel Z* component, with
g12 = 0.1520746183 from the previous analytic pilot.

To generate the 100 TeV associated-production 4FS MG5 proxy:
```bash
cd ~/zee
MG5_BIN=/cvmfs/sw.hsf.org/key4hep/releases/2026-04-08/x86_64-almalinux9-gcc14.2.0-opt/madgraph5amc/3.5.9-3xnfke/bin/mg5_aMC \
 bash scripts/setup_fcc_hh_4fs_proxy.sh 100
cd ~/zee/work/ZeeProductionProxy_4FS_100TeV
grep -E 'ebeam[12]|pdlabel|maxjetflavor' Cards/run_card.dat
grep -A6 -i 'block frblock' Cards/param_card.dat
./bin/generate_events run_01 -f 2>&1 | tee ~/zee/work/gate5_fcc_100tev.log
```

Apply sin²(1.089)=0.7852866098 to the 100 TeV 2HDM LO production rate.
Internal nn23lo1 is ONLY a preliminary screening choice, not an nf=4 precision PDF.
PDF/scale/scheme uncertainties and NLO effects must be evaluated later.

**Important physical limitations:** The real Zee model needs 2HDM+charged singlet,
two physically distinct charged mass eigenstates, and a validated ZH1H2 vertex.
The Zee–Babu UFO does not supply this theory. For the full signal
we still need an exact potential point obeying vacuum/EW/Higgs/flavour
constraints plus neutrino/LFV consistency, and a complete Zee UFO.
Do not launch expensive Delphes samples before those checks.


## Gate 6: original Zee scalar-sector benchmark screen

**Latest finding:** the initial beta=alpha=1.398 point is INVALID:
lambda1≈−1.609 violates necessary BFB. The slightly shifted
beta=1.394 point passes conservative BFB and scalar tree-level
unitarity (max |Λ|≈18.137<8π) but is **NOT yet a validated model point**.
Reconstructing the scalar potential uses P2 m12²=57700 GeV² and
k12=−0.001266 (corrected from an earlier transcription).

At shifted beta, included two-body tree-level partial widths (GeV):
H2→H1Z 9.4113; H2→Whheavy 1.0710; H2→H1h125 0.2670;
H2→tb 1.5581; H2→tauν 0.0357. The fraction H1Z/sum(included)
≈0.7624 **is not a physical Zee branching ratio**. Full antisymmetric
lepton Yukawas and LFV/neutrino constraints are not yet specified.

All running is under $HOME/zee, NOT /data:

```bash
cd ~/zee
git pull --ff-only
source ~/fccee_zh/scripts/setup_key4hep.sh
python3 -m unittest discover -s tests -v

python3 scripts/gate6_benchmark.py --beta 1.398 \
  --output work/gate6_beta_equals_alpha.json
python3 scripts/gate6_benchmark.py --beta 1.394 \
  --output work/gate6_beta_shifted.json
python3 scripts/gate6_width_inventory.py --beta 1.394 \
  --output work/gate6_partial_widths.json
python3 scripts/gate6_beta_scan.py \
  --output work/gate6_beta_scan.csv
python3 scripts/gate6_vacuum_search.py --beta 1.394 \
  --nstarts 80 --seed 20261011 \
  --output work/gate6_vacuum_search.json
```

Read the [Gate 6 benchmark audit](docs/gate6_benchmark_validation.md)
and the [requirements for a **full**, gauge-complete Zee UFO]
(docs/zee_full_ufo_implementation_contract.md).
The repository **does not yet contain** that full UFO, a lepton-sector fit,
electroweak/flavour constraints or a certified global vacuum. This stage
is a theory-only filter before committing to a gauge-complete event model.


### Gate 6 AF replication (2026-10-11)

Independent AF execution of `gate6_benchmark.py`, `gate6_width_inventory.py`,
`gate6_beta_scan.py`, and `gate6_vacuum_search.py` succeeded.
Scalar-only necessary/sufficient gates pass at beta=1.394 and the 82-start
vacuum search found no deeper minimum. This **does not prove a physical Zee point**.
See [exact AF results and hard blockers](docs/gate6_af_validation_20261011.md).

The next mandatory gate is the **physical full-model implementation plus
lepton-flavor/neutrino fit**, electroweak oblique S/T/U, B→Xs gamma
and Higgs/direct search constraints. Do not substitute
[the Zee–Babu FeynRules UFO](https://cp3.irmp.ucl.ac.be/projects/feynrules/wiki/ZeeBabu):
it has a different field content (singly and doubly charged singlets,
not two Higgs doublets plus a singly charged singlet).


### Existing original Zee UFO found (2026-10-11)

**We located a real, public Zee UFO**, so a gauge-sector implementation
need not start from scratch: [YangPhy/Zee-Model]
(https://github.com/YangPhy/Zee-Model), with
`ZEE_UFO` and `ZEE_NLO` and original FeynRules source.
The source UFO has two charged Higgs fields (`H±` PDG 227 and `h±`
PDG 228), **including off-diagonal `Z H h` vertices**.

**Critical:** the published UFO has no physical `tb H±` or
`tb h±` vertices, because its quark Yukawas only involve
the vev-carrying Higgs-basis doublet. It therefore
cannot implement our Type-II-driven associated-production
`tbH2` channel or the signal decay `H1→tb` as-is.
We can first test the real Z-mediated mixed-pair channel,
then extend the *FeynRules Lagrangian* with correct quark Yukawas.

Read the [direct UFO vertex/particle audit and safe MG5 smoke test]
(docs/gate7_existing_zee_ufo_audit.md).


### Gate 7: existing Zee UFO import succeeded; Type-II adaptation started

The user's 2026-10-11 MG5_aMC 3.5.9 import of
`external/Zee-Model/ZEE_UFO` passed: `u u~ > H+ h-`
and `u u~ > H- h+` generated 3 diagrams each.
The Yang/Wu implementation has the Z mixed-charge vertices,
but **no physical tbH± Yukawas**. It is therefore only a starting
point for our Type-II associated-production analysis.

See [Florentino-vs-Yang/Wu convention audit, source patch and NLO plan]
(docs/gate7_florentino_vs_yangwu_typeii_nlo_plan.md).
Run `python3 scripts/gate7_prepare_typeii_feynrules.py`
after checking out the upstream repository under `external/Zee-Model`.
The script creates *FeynRules source only*, never an MG5 UFO.
Old `ZEE_NLO` UV/R2 counterterms **must not be reused** after
changing the quark Yukawas.


### Gate 7: patched Type-II quark source confirmed on AF

The FeynRules source patch was executed successfully on AF and both
`Tan[beta]` (down) and `Cot[beta]` (up) terms were observed in
`models/Zee_TypeII_FR/Lagrangian.fr`. An LO UFO must still be
**exported and validated** before signal simulations.

New export/validation tools:
`scripts/gate7_export_typeii_ufo.m`,
`scripts/gate7_validate_typeii_ufo.py`,
`scripts/gate7_mg5_typeii_smoke.sh`, with accompanying static
vertex tests. Read [the LO UFO export instructions]
(docs/gate7_typeii_lo_ufo_export.md).
Mathematica and FeynRules may need to run on a separate licensed
machine if not available on ATLAS AF; do not invent a local path.
