# F17: Original SARAH five-scalar UFO interface and exact three-point physical input handoff

**Status: SOURCE-VERIFIED F17 INSPECTOR READY, NOT FULL PARAMETER CARDS OR MADWIDTH**

The user reports F16 three/three exact complex Zee masses, bosonic amplitudes,
and charged leptonic amplitudes validated against independent SARAH 4.15.4
vertices to machine precision. Fresh `MakeUFO[]` successfully generated in
`work/zee_paper1_F16_exact_SARAH_three_heavy_20261021T143647Z/`.
The generated source uses charged PDG 37 (H1), 9000037 (H2), neutral
PDG 25 (h), 35 (H), 36 (A). This is a physical-model LO UFO source,
**not** a model-specific physical parameter card or MadWidth decay result.

## One local command

    cd ~/zee
    git switch feature/global-scan-priority1
    git pull --ff-only
    export ZEE_F16_DIR="$HOME/zee/work/zee_paper1_F16_exact_SARAH_three_heavy_20261021T143647Z"
    bash scripts/zee_paper1_F17_local_UFO_inspection_one_shot.sh

The launcher revalidates the F16 original three candidate SHA hashes and
the actual SARAH three-case PASS before exporting exact complex matrices
to JSON (Fzee, Ye, Ye2, YChen, ZP, ZH, ZA). It does **not** re-run the
F13 scalar/neutrino scans or SARAH MakeUFO and does not modify the original
F16 mass/vertex source.

The F17 Python inspector requires exact three F13 IDs, checks positive
scalar inputs and complex matrix shapes, and independently verifies:

- Fzee is antisymmetric and the complete complex (not just real) matrix survived;
- the Ye/Ye2 two-VEV mass relation gives the charged-lepton mass matrix;
- the Higgs-basis YChen relation and rotations close;
- the original charged/CP-even/CP-odd physical mixing matrices match;
- all five scalar PDG species exist in the exported UFO;
- the actual imported UFO Python source files parse as AST;
- three-point Z-H1-H2, both tb couplings, charged scalar trilinears,
  W-scalar gauge, charged lepton-neutrino and offdiagonal photon signatures;
- real scalar LHA external blocks `ZEEPOT` and `ZEEQUARTIC` map to the
  original SARAH Lagrangian coefficient definitions (not physical masses).

AST parsing avoids executing the new generated UFO as arbitrary Python.
Unlike older Yang/Wu FR UFO preflight, this F17 scanner uses the
actual SARAH PDGs 37 and 9000037, rather than 228 and 227.

## Outputs and blocker interpretation

`F17_original_SARAH_UFO_inventory_<UTC>/summary.json` includes all
external SLHA parameter definitions, sensitive symbolic/complex
parameters and numerically checked source Yukawas.
An `F17_UFO_external_parameters.csv` lists actual external LHA slots.

If all 14 real SARAH scalar potential inputs are explicitly declared
external in the generated UFO, F17 also emits three
`*_ZEEPOT_ZEEQUARTIC_SOURCE_ONLY_NOT_FULL_CARD.slha` fragments.
They deliberately omit quark masses/CKM, electric and strong couplings,
charged/neutral output mass spectra, every complex lepton matrix and
DECAY widths. These fragments must **never** be fed alone to MadWidth.
Missing or duplicate external definitions fail closed.

## Remaining stage before MadWidth

Use F17 real UFO inventory to derive every external MASS/SMINPUTS,
vev/mixing, matrix and complex Y/f input in the *actual* SARAH UFO.
Then independently verify UFO evaluation and couplings under those
inputs; only after that build three genuine exact-source MG5 parameter
cards, test H2->H1 Z and H1->tb partial widths and run 2/3-body
MadWidth with an audited decay-channel enumeration.

Even then, all results are model/approximation-specific LO decay
rates; modern 2026 high-order two-state B->Xs gamma and full LFV
restrictions remain necessary for benchmark allowed claims.

F17 synthetic AST interface tests passed at
https://github.com/aalida0/zee/actions/runs/39926660129 .
Those CI tests cannot substitute for the user's real generated UFO.
