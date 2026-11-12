# Zee Type-II all-64 µ→3e and coherent µ−e conversion: exact-source execution handoff

**Date:** 12 November 2026; research branch `research/zee-full-constraints`.

## Status — evidence, not aspiration

| Component | Executed on exact 64 new neutrino-compatible cards? | Physical status |
|---|---:|---|
| 16 tree-vacuum-certified scalar spectra + 4 NO/IO homogeneous textures each | **YES** | Scalar source is selected, not random |
| Complex `F`, `Ye2` SLHA source cards and source scalar potential `MINPAR` | **YES: 64/64** | Input generation only, original template unvalidated in CI |
| Exact source hashes and calculated lepton source rotation | **Tests YES** | Runtime source not in GitHub |
| Original 2017–2026 SARAH 4.15.4 `CalculateGamma2l` photon/Z/box and `Calculate_Lto3Lp` | **NO on these 64** | **PHYSICAL_MU3E=UNKNOWN** |
| Original `Calculate_MuEconversion` full U/D/S and scalar nucleons | **NO on these 64** | **PHYSICAL_CONVERSION=UNKNOWN** |
| Historical four prior D7/F13 low-joint one-loop rates | **YES, four older cards only** | **Cannot transfer to new F/D** |
| Fixed-order Zee full radiative mixed-gauge two-loop + nuclear EFT errors | **NO** | **FULL_PHYSICAL_LFV=UNKNOWN** |

The source-independent source-index and input-builder code is under `research/full_constraints/lfv_64_native_2026/`; the old model's input map is `module14/physics_adapters/SPheno.m` and the generated-original SHA manifest is `research/full_constraints/lfv/SOURCE_TO_CODE_SOURCES.json`.

The exact all-64 source-generation workflow is `.github/workflows/zee-native-lfv-64-source-gate.yml`. Its output artifact is intentionally named `zee-exact-64-inputs-NOT-native-LFV-rates`. It constructs all 64 original cards and runs input/spectrum/source/fail-closed tests, **not the original generated Fortran**, which is absent from public GitHub and this conversation.

## Original non-public model files genuinely needed

These SHA-256 digests are verified against the original 10 November four-card source audit:

```text
2d30006d8d4759b2b7bfe76e2e4795bd2cf2f19ef5cb5772390ed3155b1bc41d FlavorKit_LFV_ZeeTypeII.f90
a0de851498f3e68e7421538098b3979381a3ecf5245021fce9d1c2df46a42e8c Couplings_ZeeTypeII.f90
8142a813fcc00283d1de2865266be04ff1de25c09422b24b04d57523a6595a24 LoopFunctions.f90
b179e6fea1fe3afe08e34e6d481380b7d4b669ffb904898ac6ee6f8555aa3784 FlavorKit_Observables_ZeeTypeII.f90
cf3552d25de21a6df0869d1fc013dded8efe26206195a08f84ab6ec251d63727 LowEnergy_ZeeTypeII.f90
```

The original 10 Nov successful source-based four-card evaluations used all five exact files, but no copies were committed to the research repository. A *different* Zee package or the public restrepo/Zee-Toolbox source is **not an acceptable replacement**, and copying the old numerical Wilsons is invalid because all 64 Yukawas differ.

## Local source recovery — one command (READ ONLY)

From the actual machine containing the 10 Nov SARAH source installation:

```bash
cd ~/zee
git fetch origin research/zee-full-constraints
git checkout research/zee-full-constraints
git pull --ff-only origin research/zee-full-constraints
python3 -m research.full_constraints.lfv_64_native_2026.export_all_original_sources \
  --output ~/zee_TypeII_original_five_LFV_sources.zip
```

If the five files remain at the exact original locations, this writes one locally owned private ZIP with the 5 SHA-matched original files and a machine manifest. It neither compiles code nor uploads the private files to GitHub. The original local source paths are automatically obtained from the frozen source manifest; wrongly located or mismatching source is rejected. The ZIP can be supplied as a conversation attachment for source-matched scientific completion.

## Reconstruct the 64 exact new family inputs (requires pinned Python environment)

```bash
python3 -m research.full_constraints.scan_pilot_2026.bounded_16_scalar_64_family \
  --output /tmp/zee-source-16x4.json

# The template MUST be an independently validated native input from
# the original generated ZeeTypeII model, for example a previously
# calibrated tree-scheme SPheno input. Never use the CI's synthetic
# example template to claim complete physics.
python3 -m research.full_constraints.lfv_64_native_2026.spheno_64_source_gate \
  --source /tmp/zee-source-16x4.json \
  --template /path/to/validated/original/ZeeTypeII-tree-scheme.in \
  --cards-dir /tmp/zee-64-source-SLHA
```

The template must have `SPhenoInput[57]=1` to enable low-energy observables; `FZEE` and `YEE2` real model blocks must exist. All original `SMINPUTS`, quark CKM and mass schemes are preserved, not silently retuned.

### Why the native model output must be checked

Each execution requires
- original scalar mass agreement for h,H,A,H1,H2 (no unchecked full pole-spectrum drift);
- exact complex F and Ye2, beta and recovered D=-sinβ Ye+cosβ Ye2 agreement, with suppression of physical D[e,µ] and D[µ,e] retained;
- actual `FlavorKitLFV` entries 701 (µeγ), 901 (µ3e), 800 (Al), 804 (Au); missing, negative, nonfinite or duplicate inputs are fatal;
- complete amplitude inventory (photon K1 and K2, Z penguins, four-lepton boxes/tree/scalar penguins, quark scalar/vector penguins/boxes) and common signed source-order interference;
- original generated observable `Calculate_Lto3Lp` and `Calculate_MuEconversion` must be the model-specific source, not a generic template.

The runtime accepts exact original source file paths and an existing rebuilt model-specific SPheno executable:

```bash
python3 -m research.full_constraints.lfv_64_native_2026.spheno_64_source_gate \
  --source /tmp/zee-source-16x4.json \
  --template /path/to/validated/original/ZeeTypeII-tree-scheme.in \
  --cards-dir /tmp/zee-64-source-SLHA \
  --execute /path/to/hash-identified/SPhenoZeeTypeII \
  --result-dir /tmp/zee-64-native-one-loop \
  --FlavorKit_LFV_ZeeTypeII /path/to/FlavorKit_LFV_ZeeTypeII.f90 \
  --Couplings_ZeeTypeII /path/to/Couplings_ZeeTypeII.f90 \
  --LoopFunctions /path/to/LoopFunctions.f90 \
  --FlavorKit_Observables_ZeeTypeII /path/to/FlavorKit_Observables_ZeeTypeII.f90 \
  --LowEnergy_ZeeTypeII /path/to/LowEnergy_ZeeTypeII.f90
```

**Important:** This is a source-checking prototype until the binary is attested as rebuilt from the original five files. The initial native `µ-e` converter output has a known scalar proton/neutron interchange, so the source-generated historical nuclear rate must not be called a modern physical conversion result.

### Correct the nuclear scalar interchange without changing the original

```bash
python3 -m research.full_constraints.lfv_64_native_2026.patch_original_nuclear_source \
  --original /path/to/FlavorKit_Observables_ZeeTypeII.f90 \
  --output /tmp/FlavorKit_Observables_ZeeTypeII.scalar-pn-corrected.f90
```

Recompile a **separate SPhenoZeeTypeII binary** using that exact copy and the unchanged other original model sources. Record original/corrected source and binary SHA-256 values; compare native rates to the original 4-card benchmark source outputs before accepting new 64. The corrected binary must not be presumed equivalent to an old unpatched binary.

Do not transplant modern EFT conversion limits onto an unvalidated historical coherent nuclear convention. Validate the proton/neutron scalar form factors and quark threshold matching with a current reference (e.g. Kitano–Koike–Okada, hep-ph/0203110; Crivellin *et al.*, 1702.03020).

## Known earlier native four-card cross-checks (NOT new 64)

At original D7/F13 NO/IO: full generated one-loop `BR(µ→3e)` ≈ 1.0883e−21, 7.5294e−21, 4.5462e−22, 1.4571e−21. Corrected historical coherent Au ≈ 6.9893e−22, 4.5497e−21, 6.3468e−21, 1.9220e−20. These values document the original source execution benchmark and phase normalization, but **cannot be assigned to any of the 64 new families**.

Source reports: `research/full_constraints/lfv_lo_closure_2026/NATIVE_COMPLETE_ONELOOP_LFV_REPORT_2026-11-10.md` and `NATIVE_FULL_UDS_CONVERSION_AND_ONE_LOOP_LFV_2026-11-10.md`.

## Acceptance policy

Only once the original source is reproduced on all 64 with native-vs-independent scalar/dipole/box/Z controls, corrected nuclear source and quantified input/scheme uncertainties may a specific one-loop-order `µ3e` or `µe` status be set to `PASS` or `FAIL`. Otherwise: `physical_mu3e=null`, `physical_conversion=null`, `full_LFV=UNKNOWN` and `global_acceptance=null`.

A one-loop source completeness test is not a bound on omitted Zee two-loop electroweak gauge effects. No paper-wide full-model acceptance follows automatically.
