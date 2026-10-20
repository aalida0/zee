# Mathematica only on local computer — supported Zee SARAH/SPheno/FlexibleSUSY handoff

The user's UChicago AF audit found gfortran and cmake, but no Wolfram kernel, no SARAH Zee model, no model-specific SPheno/FlexibleSUSY executables, no MadGraph, and no BSMArt. **This is compatible with our workflow. We do NOT need Mathematica on AF.** We do need a validated SARAH general-Zee model definition and actual generated code.

## Workstation (Mathematica): derive code, no production scan

1. Check Mathematica and SARAH/FeynRules locally. For SARAH, inside Mathematica: Needs["SARAH`"]. The script must load an **actually implemented** ZeeTypeII model; our prior audit showed no such model in the current AF repository. Do not invoke the sample below pretending a model exists. FeynRules uses the separately derived TypeII complex Zee source and original scripts/gate7_export_typeii_ufo.m.
2. Once the SARAH source model is implemented under SARAH/Models/ZeeTypeII, run locally (in Mathematica):

   Needs["SARAH`"];
   Start["ZeeTypeII"];
   CheckModel[];
   MakeSPheno[];

   SARAH usually writes the generated Fortran into SARAH/Output/ZeeTypeII/EWSB/SPheno (find the actual generated path). CheckModel is a useful diagnostic, not proof that the Zee flavor/loop theory is complete.

3. **FlexibleSUSY** has documented split-machine support. On the local Mathematica computer with SARAH installed and a correct FlexibleSUSY model definition:

   cd /path/to/FlexibleSUSY
   ./createmodel --name=ZeeTypeII
   # Configure/check the actual generated models/ZeeTypeII/FlexibleSUSY.m.
   ./configure --with-models=ZeeTypeII --disable-compile
   make
   make pack-ZeeTypeII-src

   The packed ZeeTypeII.tar.gz contains generated source. None of these commands work without correct model files and installed SARAH; do not confuse success of a built-in THDM model with a complete Zee model.

4. Pack **existing generated source** using the repository script, omitting any component not yet produced:

   cd /path/to/local/zee
   git switch feature/global-scan-priority1
   git pull --ff-only
   python3 scripts/zee_p1_local_af_handoff.py pack \
     --sarah-model /path/to/SARAH/Models/ZeeTypeII \
     --spheno-source /path/to/SARAH/Output/ZeeTypeII/EWSB/SPheno \
     --flexible-package /path/to/FlexibleSUSY/ZeeTypeII.tar.gz \
     --ufo /path/to/Zee_TypeII_Complex_LO_UFO \
     --out "$HOME/zee-generated-source-v1.tar.gz"
   python3 scripts/zee_p1_local_af_handoff.py check \
     --bundle "$HOME/zee-generated-source-v1.tar.gz"

   This requires actual paths; if one of the 4 packages is missing, **remove its option**. The archive records SHA256 per file and explicitly states no physics model validation.

5. Copy this **model source** to UChicago AF (use your working SSH hostname if different):

   scp "$HOME/zee-generated-source-v1.tar.gz" \
     aalida@login01.af.uchicago.edu:/home/aalida/zee/work/

## UChicago AF: compile and validate without Mathematica

   cd /home/aalida/zee
   git switch feature/global-scan-priority1
   git pull --ff-only
   python3 scripts/zee_p1_local_af_handoff.py check \
     --bundle work/zee-generated-source-v1.tar.gz
   python3 scripts/zee_p1_local_af_handoff.py unpack \
     --bundle work/zee-generated-source-v1.tar.gz \
     --dest work/zee-generated-source-v1

Outputs under work/zee-generated-source-v1:
- sarah_model/ — pure Mathematica source model definition (for review/source provenance).
- spheno_source/ — already generated **Fortran**, copy into the appropriate SPheno/models/ZeeTypeII source directory for compilation; no Mathematica required for compilation.
- flexible_package/ZeeTypeII.tar.gz — generated FlexibleSUSY model C++ source package. Extract into fresh /home work directory and run its ./configure and make there.
- ufo/ — FeynRules generated LO UFO. Run the existing scripts/zee_p1_ufo_model_audit.py against it, then verify amplitudes/parameter mapping independently.

The [upstream SPheno source-build instructions](https://github.com/JP-Ellis/SPheno/blob/master/README.md) specify copying SARAH Output/MODEL/EWSB/SPheno to models/MODEL and compiling with the model enabled. [FlexibleSUSY instructions](https://github.com/FlexibleSUSY/FlexibleSUSY) explicitly support Mathematica-only source generation (--disable-compile), generated model packaging (make pack-MODEL-src), and separate compilation (--disable-meta or source package ./configure, make). Choose compilation commands appropriate to the actual installed versions and build environment.

### BSMArt on AF

BSMArt itself does **not** require Mathematica for a scan consuming compiled external model executables; the preparation step BSMArt-PrepareModel normally does require SARAH/Mathematica, so it belongs to the local code generation stage or must be adapted to use previously generated sources. Use a dedicated AF venv:

   cd /home/aalida/zee
   python3 -m venv .venv-bsmart
   source .venv-bsmart/bin/activate
   python -m pip install bsmart
   BSMArt-CheckPackages --scan Random --tool SPheno FlexibleSUSY HiggsTools

When ready, configure BSMArt explicit paths to compiled SPheno/FlexibleSUSY/HiggsTools. It will not automatically validate neutrino loop structures, complete two-loop LFV or matched modern B->Xs gamma.

### Checks before real scans

A working SARAH/SPheno compilation is **not** yet an experimentally viable general Zee model. Check for the TypeII quark Yukawa structure, two charged states and mixing, full complex antisymmetric f + complex general Y, exact one-loop neutrino mass, scalar potential and trilinears, all necessary gauge/Goldstone interactions, comparison with the independent FeynRules/MadWidth vertices and decay modes, and 2026 flavor order matching.

The transfer script includes no private data other than contents of model source you choose to bundle; do not pack SSH credentials, tokens, personal files, confidential MC data or external licenses.
