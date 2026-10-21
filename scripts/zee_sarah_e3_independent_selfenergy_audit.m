(* ONE integrated, independent SARAH one-loop neutrino self-energy audit.
   This is the next physics stage after the 162-vertex E3 convention gate.
   Calculates SARAH's OWN one-loop self energies rather than assembling
   a Chen input formula from already-matched tree-level vertices.
   Fail-closed: never certify Majorana neutrino masses unless a genuine
   lepton-number-violating mass form factor is identified and numerically
   evaluated against independent E3 test data.

   Run from repo root via:
      bash scripts/zee_sarah_e3_one_loop_one_shot.sh
*)
zeeLoopRoot=Directory[];
zeeLoopDir=FileNameJoin[{zeeLoopRoot,"work","sarah_zee"}];
If[!DirectoryQ[zeeLoopDir],
 CreateDirectory[zeeLoopDir,CreateIntermediateDirectories->True]];
zeeLoopStatusFile=FileNameJoin[{zeeLoopDir,"e3_sarah_selfenergy_status.txt"}];
zeeLoopRawFile=FileNameJoin[{zeeLoopDir,"e3_sarah_selfenergy_neutrino_raw.txt"}];
zeeLoopInventoryFile=FileNameJoin[{zeeLoopDir,"e3_sarah_selfenergy_inventory.txt"}];
zeeLoopStatus[zeeLoopLabel_String]:=(
 Export[zeeLoopStatusFile,zeeLoopLabel<>"\n","Text"];
 Print["ZEE_E3_SELFENERGY_STATUS ",zeeLoopLabel]
);
zeeLoopStatus["E3_SARAH_SELFENERGY_NOT_VALIDATED"];

(* Preserve only an independently source-closed E3 fixture; do not
   silently replace this with unvalidated 309 model candidates. *)
zeeLoopFixture=FileNameJoin[{zeeLoopDir,"e3_charged_loop_fixture.m"}];
zeePreviousGate=FileNameJoin[{zeeLoopDir,"e3_integrated_status.txt"}];
If[!FileExistsQ[zeeLoopFixture]||!FileExistsQ[zeePreviousGate],
 zeeLoopStatus["E3_PREVIOUS_CONVENTION_GATE_MISSING"];Exit[2]];
zeeEarlier=StringTrim[Import[zeePreviousGate,"Text"]];
If[zeeEarlier =!=
 "E3_SARAH_TREE_CONVENTION_AND_CHEN_KERNEL_CONSISTENT_SELFENERGY_UNVALIDATED",
 Print["FAIL PREVIOUS_E3_GATE ",zeeEarlier];
 zeeLoopStatus["E3_PREVIOUS_CONVENTION_GATE_NOT_PASSED"];Exit[3]];
Get[zeeLoopFixture];
If[!ListQ[zeeE3Cases]||Length[zeeE3Cases]!=2,
 zeeLoopStatus["E3_FIXTURE_INVALID"];Exit[4]];

zeeSarah=FileNameJoin[{$HomeDirectory,".Mathematica",
 "Applications","SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[zeeSarah],
 zeeLoopStatus["SARAH_INSTALLATION_NOT_FOUND"];Exit[5]];
PrependTo[$Path,DirectoryName[zeeSarah]];
zeeSarahLoaded=CheckAbort[(Get[zeeSarah];True),False];
If[!TrueQ[zeeSarahLoaded]||!ValueQ[SA`Version],
 zeeLoopStatus["SARAH_LOAD_FAILED"];Exit[6]];
SARAH[InputDirectories]=Prepend[
 SARAH[InputDirectories],FileNameJoin[{zeeLoopRoot,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],
 zeeLoopStatus["SARAH_MODEL_START_FAILED"];Exit[7]];
Print["ZEE_E3_SELFENERGY_SARAH_VERSION ",SA`Version];
Print["ZEE_E3_SELFENERGY_METHOD CalcLoopCorrections[EWSB]"];
Print["ZEE_E3_SELFENERGY_DIAGRAMS_SOURCE SARAH_COMPUTED_NOT_CHEN_ASSEMBLED"];

(* SARAH's documented loop correction facility computes full 1-loop
   self-energy contributions from generated model vertices. Do NOT
   restrict internal states with OnlyWith: doing so would make a
   completeness claim impossible and may hide cancellations. *)
If[DownValues[SARAH`CalcLoopCorrections]==={},
 Print["FAIL SARAH_CALCLOOPCORRECTIONS_NOT_DEFINED"];
 zeeLoopStatus["SARAH_LOOP_API_NOT_AVAILABLE"];Exit[8]];
zeeLoopFinished=CheckAbort[
 (SARAH`CalcLoopCorrections[EWSB];True),False];
If[!TrueQ[zeeLoopFinished],
 zeeLoopStatus["SARAH_LOOP_CALC_ABORTED"];Exit[9]];

(* Both lists below MUST be populated by SARAH, not by our wrapper.
   These are structurally distinct: summed contributions, and an
   inventory of individual one-loop diagram topologies. *)
zeeLoopSum=SARAH`SelfEnergy1LoopSum[EWSB];
zeeLoopList=SARAH`SelfEnergy1LoopList[EWSB];
Print["ZEE_E3_SELFENERGY_SUM_HEAD ",Head[zeeLoopSum]];
Print["ZEE_E3_SELFENERGY_LIST_HEAD ",Head[zeeLoopList]];
If[!ListQ[zeeLoopSum]||!ListQ[zeeLoopList],
 Print["FAIL SARAH_SELFENERGY_OUTPUT_MISSING ",
    InputForm[{Head[zeeLoopSum],Head[zeeLoopList]}]];
 zeeLoopStatus["SARAH_LOOP_OUTPUT_UNAVAILABLE"];Exit[10]];

(* Keep the first column of every result as a particle inventory.
   This also helps discover whether SARAH classifies a massless
   two-component neutrino as Fv, vL, or another internal object. *)
zeeRows=Select[zeeLoopSum,ListQ[#]&&Length[#]>=2&];
zeeParticleHeads=If[Length[zeeRows]>0,First/@zeeRows,{}];
Export[zeeLoopInventoryFile,
 StringRiffle[ToString[InputForm[#]]&/@zeeParticleHeads,"\n"]<>"\n",
 "Text"];
Print["ZEE_E3_SELFENERGY_PARTICLE_ENTRIES ",Length[zeeRows]];
Print["ZEE_E3_SELFENERGY_PARTICLE_NAMES ",
 InputForm[zeeParticleHeads]];

zeeNuRows=Select[zeeRows,
 !FreeQ[#[[1]],Fv]||!FreeQ[#[[1]],vL]||
 !FreeQ[#[[1]],Fv1]&];
zeeNuListRows=Select[zeeLoopList,
 ListQ[#]&&Length[#]>0&&(
 !FreeQ[#[[1]],Fv]||!FreeQ[#[[1]],vL]||
 !FreeQ[#[[1]],Fv1])&];
Print["ZEE_E3_SELFENERGY_NEUTRINO_SUM_ROWS ",Length[zeeNuRows]];
Print["ZEE_E3_SELFENERGY_NEUTRINO_DIAGRAM_LIST_ROWS ",
 Length[zeeNuListRows]];
Export[zeeLoopRawFile,
 StringRiffle[
 Join[{"STATUS: generated SARAH 1-loop expressions, not numeric E3 closure",
       "SCHEME: SARAH non-SUSY MSbar; gauge assumptions per SARAH"},
      {"SUMS:"},
      (ToString[InputForm[#]]&/@zeeNuRows),
      {"DIAGRAM_LIST:"},
      (ToString[InputForm[#]]&/@zeeNuListRows)
 ],"\n\n"]<>"\n","Text"];
Print["ZEE_E3_SELFENERGY_RAW_FILE ",zeeLoopRawFile];

If[Length[zeeNuRows]==0,
 Print["ZEE_E3_SELFENERGY_NOTE No neutrino self-energy output was found.",
       " Fv is defined as a one-chirality Dirac spinor;",
       " this may require a different neutrino/Majorana definition",
       " or a dedicated mass-insertion/diagram calculation."];
 zeeLoopStatus["SARAH_NO_NEUTRINO_SELFENERGY_IN_CURRENT_FIELD_REPRESENTATION"];
 Exit[11]];

(* Classify what was generated but DO NOT claim the radiative
   Majorana mass matrix was calculated just because Fv has a
   wave-function self energy. Inspect mass-type Sigma^S entries and
   the lepton-number-violating f-Y interference separately. *)
zeeHasMassTypeQ=!FreeQ[zeeNuRows,B0]||
 !FreeQ[zeeNuRows,Mass]||
 !FreeQ[zeeNuRows,SA`B0];
zeeHasChargedLoopQ=!FreeQ[zeeNuRows,Hm]||
 !FreeQ[zeeNuListRows,Hm];
zeeHasLeptonLoopQ=!FreeQ[zeeNuRows,Fe]||
 !FreeQ[zeeNuListRows,Fe];
Print["ZEE_E3_SELFENERGY_HAS_LOOP_MASS_STRUCTURE ",
 zeeHasMassTypeQ];
Print["ZEE_E3_SELFENERGY_HAS_CHARGED_SCALAR_TOPOLOGY ",
 zeeHasChargedLoopQ];
Print["ZEE_E3_SELFENERGY_HAS_CHARGED_LEPTON_TOPOLOGY ",
 zeeHasLeptonLoopQ];
Print["ZEE_E3_SELFENERGY_MAJORANA_MASS_NUMERICALLY_EXTRACTED False"];
Print["ZEE_E3_SELFENERGY_E3_MNU_NUMERICALLY_MATCHED False"];
Print["ZEE_E3_SELFENERGY_REAL_309_SOURCE_TESTED False"];
If[!TrueQ[zeeHasChargedLoopQ]||!TrueQ[zeeHasLeptonLoopQ],
 zeeLoopStatus["SARAH_NEUTRINO_LOOP_REQUIRED_TOPOLOGY_ABSENT"];
 Exit[12]];
zeeLoopStatus[
 "SARAH_NEUTRINO_LOOP_TOPOLOGIES_EXTRACTED_MAJORANA_MASS_UNVALIDATED"];
Exit[0];
