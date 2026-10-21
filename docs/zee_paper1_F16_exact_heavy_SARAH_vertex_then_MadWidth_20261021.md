# F16 — Three exact heavy Zee benchmarks into independent SARAH tree-level vertices

**Status, 21 October 2026:** physically matched source-input preparation implemented. The local SARAH/MadWidth stages have **not** been run against the three AF-only files. All earlier F15 estimates (0.52–0.58 fb at 13 TeV) remain *included-channel*, not physical full-model rates.

## Why this path, not another set of ad hoc partial widths

The original Gate6/B3 charged Higgs widths omit possible gauge-invariant tree 3-body final states, loop modes and QCD effects. The accepted F13 neutrino matrices are complex. An old Yang/Wu real-only UFO, or a single-charged Type-II UFO, would not represent those points. The repo already has a ZeeTypeII SARAH 4.15.4 model with numerically tested scalar masses, Z/offdiagonal and photon vertices, and independent 162 complex-lepton-vertex/source neutrino-loop comparisons in the original SARAH studies. **This F16 path uses the actual gauge-invariant model and exact three F13 source-point Yukawas.**

### Step 1: Run on UChicago AF

```bash
cd /home/aalida/zee
git switch feature/global-scan-priority1
git pull --ff-only
bash scripts/zee_paper1_F16_AF_exact_SARAH_one_shot.sh
```

This refuses source mismatches; joins immutable exact F13 eight-point selection and F14 summary+CSV; reconstructs the fully complex optimized f/Y for the three priority benchmarks; checks exact fixed-NO neutrino closure against B3; reconstructs the actual CP-even, CP-odd and charged Hessians; tests scalar potential quartic equivalence at random complex SU2 doublets; verifies the original H2->H1Z and H2->H1h/H partial-width formulas. It converts the original Chen/E3 couplings into the actual SARAH weak-basis convention **FSARAH=2 fE3, YD=sqrt(2) YE3**, including independent external charged-lepton mass matrices. No complex phases are discarded.

Output `work/zee_paper1_F16_exact_SARAH_three_heavy_<UTC timestamp>/` contains the explicit Mathematica association `F16_three_exact_F13_Zee_SARAH_charged_vertices.m`, detailed JSON for the three matched scalar/mass/complex Yukawa inputs, and source SHA256 manifest. This is NOT an SLHA/UFO parameter card.

### Step 2: Transfer the generated AF output to your LOCAL Mathematica machine

Example (on your local computer, replace the AF directory shown by F16 with the real one):

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only
scp -r aalida@login01.af.uchicago.edu:/home/aalida/zee/work/zee_paper1_F16_exact_SARAH_three_heavy_<REAL_UTCSTAMP> ./work/
export ZEE_F16_DIR="$HOME/zee/work/zee_paper1_F16_exact_SARAH_three_heavy_<REAL_UTCSTAMP>"
bash scripts/zee_paper1_F16_local_SARAH_three_heavy_one_shot.sh
```

Before Mathematica starts, the local runner invokes `scripts/zee_paper1_F16_verify_AF_to_local_bundle.py`, requiring full SHA256 closure of the original transferred complex f/Y, physical scalar fixture, source manifest, and the **identical local ZeeTypeII SARAH model file**. A stale or modified fixture is rejected. Both the actual F16 model-handoff test and a separate transfer-tampering regression test run in CI.

The local script explicitly locates your installed `~/.Mathematica/Applications/SARAH-4.15.4/SARAH.m`, loads the unchanged `models/SARAH/ZeeTypeII`, retrieves **actual SARAH-generated** `MassMatrix[hh]`, `MassMatrix[Ah]`, `MassMatrix[Hm]`, offdiagonal Z, offdiagonal photon, H2-H1-h/H, 36 charged-lepton f and Y vertices, and the full generated charged-lepton mass matrix. It substitutes all three independent source fixtures, recomputes the three bosonic two-body widths and six lepton-family/state widths, and reports maximum source-amplitude residuals. A nonnumeric/mismatched vertex fails closed. Unlike F15, this is a genuine cross-generator amplitude calculation **when run locally**.

Expected success label (do not claim before the actual local run):

`F16_THREE_HEAVY_SARAH_MASS_GAUGE_CUBIC_COMPLEX_LEPTON_PASS_NOT_MADWIDTH`.

The model SARAH charged-state PDGs are H1=37, H2=9000037, not the older Yang/Wu FeynRules 228/227; neutral H=35, A=36. Cards/generator decay requests must use the **generated model's own** PDG convention.

### Step 3: Generate the complete LO UFO source only after the above PASS

After passing actual vertex checks, set `ZEE_F16_EXPORT_UFO=1` and run the same local shell script. The guarded `scripts/zee_paper1_F16_SARAH_MakeUFO_after_vertex_gate.m` calls the actual SARAH `MakeUFO[]` function and copies its newly written five-state UFO to the F16 output. It refuses stale cached SARAH output, missing generated model Python files and overwriting existing files.

**Export is conditional and is NOT itself proof of a matched physical parameter card.** For MadWidth, still need to source-match every external/internally derived SARAH mixing and vev, CKM quark convention, neutral couplings, all charged mode matrices, finite gauge/Ward tests, and a gauge-consistent param card for each original F13 benchmark. The existing Yang/Wu-specific static UFO audit and PDG map cannot be applied blindly to SARAH output.

### What remains to call the charged widths complete

1. The actual three source-matched SARAH vertex PASS and generated model UFO.
2. A model-specific, independently verified *full SLHA* param-card matching the original F13 quartics, masses/mixing, CKM and all complex Y,f.
3. True MG5/MadWidth two- and three-body calculations plus consistency comparisons of H2->H1 Z and H1->tb; avoid off-shell/2-body double counting.
4. Appropriate QCD corrections/running-mass scheme to tb and other hadronic widths.
5. Recomputed post-MadWidth actual H2->H1Z and H1->tb branching fractions and the 13 TeV production-normalized rate, then independent 14/85/100 TeV hadronic cross sections and detector acceptances.
6. Modern NNLO-consistent two-charged B->Xs gamma and complete Zee flavor/Higgs/vacuum constraints.

**Fail-closed verdict:** this code does not assert complete widths, physical 13/14/85/100 TeV signal rates, exclusion/allowance, or publication readiness. The required local Mathematica step cannot be executed on GitHub CI.
