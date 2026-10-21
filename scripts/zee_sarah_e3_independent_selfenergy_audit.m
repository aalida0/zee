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

(* SARAH's loopCorrections.m source sets
     SelfEnergy1LoopSum = Join[SelfEnergies1Loop,SelfEnergyUnmixed]
     ParticlesSelfEnergy1LoopSum = entryParticles
     SelfEnergy1LoopList = {{external_particle,diagram1,...},...}.
   A summed self-energy expression is NOT {particle,expression}.
   Never take First/@SelfEnergy1LoopSum as the particle inventory.
   Verify the corresponding external labels before selecting a neutrino. *)
zeeLoopLabels=SARAH`ParticlesSelfEnergy1LoopSum[EWSB];
zeeLoopSourceList=SA`LoopMassesParticle;
Print["ZEE_E3_SELFENERGY_N_SUM_ENTRIES ",Length[zeeLoopSum]];
Print["ZEE_E3_SELFENERGY_N_LIST_ENTRIES ",Length[zeeLoopList]];
Print["ZEE_E3_SELFENERGY_N_EXTERNAL_LABELS ",
 If[ListQ[zeeLoopLabels],Length[zeeLoopLabels],"NOT_A_LIST"]];
Print["ZEE_E3_SELFENERGY_LABELS ",
 If[ListQ[zeeLoopLabels],InputForm[zeeLoopLabels],"UNAVAILABLE"]];
Print["ZEE_E3_SELFENERGY_LOOP_SOURCE_PARTICLE_LABELS ",
 InputForm[zeeLoopSourceList]];
If[!ListQ[zeeLoopLabels] ||
 Length[zeeLoopLabels]=!=Length[zeeLoopSum] ||
 Length[zeeLoopSum]==0,
 Print["FAIL SELFENERGY_LABEL_SUM_ALIGNMENT ",
  " sums=",Length[zeeLoopSum],
  " labels=",If[ListQ[zeeLoopLabels],Length[zeeLoopLabels],-1]];
 zeeLoopStatus["SARAH_SELFENERGY_LABEL_ALIGNMENT_FAILED"];Exit[11]];

(* Only a whole EXTERNAL label, never the contents of a summand,
   may define a neutrino self-energy. This supports Fv, UFv, vL,
   and gauge-state Fv1; other representations remain diagnostic. *)
zeeNeutrinoExternalQ[zeeLabel_]:=Module[
 {zeeName=ToString[InputForm[zeeLabel]],zeeToken,zeeBase},
 (* Match a COMPLETE external particle name only. Remove wrappers
    and generation suffix; never grep inside the entire self-energy. *)
 zeeToken=StringReplace[zeeName,{
   "{"->"","}"->"","bar["->"","conj["->""}];
 zeeBase=First[StringSplit[zeeToken,"["]];
 MemberQ[{"Fv","UFv","Fv1","vL"},zeeBase]
];
zeeExternalPairs=MapThread[List,{zeeLoopLabels,zeeLoopSum}];
zeeNuPairs=Select[zeeExternalPairs,zeeNeutrinoExternalQ[#[[1]]]&];
zeeDiagPairs=Select[zeeLoopList,
 ListQ[#]&&Length[#]>=1&&zeeNeutrinoExternalQ[#[[1]]]&];

(* Explicitly verify list order/labels. The summed expressions may
   be vectors/matrices indexed by external fermion generations. *)
zeeLoopLabelLedger=Table[
 "INDEX "<>ToString[zeeIndex]<>
 " EXTERNAL "<>ToString[InputForm[zeeLoopLabels[[zeeIndex]]]]<>
 " SUM_HEAD "<>ToString[Head[zeeLoopSum[[zeeIndex]]]]<>
 " SUM_DIMENSIONS "<>ToString[InputForm[Dimensions[zeeLoopSum[[zeeIndex]]]]],
 {zeeIndex,Length[zeeLoopSum]}];
Export[zeeLoopInventoryFile,
 StringRiffle[zeeLoopLabelLedger,"\n"]<>"\n","Text"];
Print["ZEE_E3_SELFENERGY_EXTERNAL_INVENTORY_FILE ",zeeLoopInventoryFile];
Print["ZEE_E3_SELFENERGY_NEUTRINO_EXTERNAL_SUM_ENTRIES ",Length[zeeNuPairs]];
Print["ZEE_E3_SELFENERGY_NEUTRINO_EXTERNAL_DIAGRAM_ENTRIES ",
 Length[zeeDiagPairs]];
Print["ZEE_E3_SELFENERGY_NEUTRINO_EXTERNAL_LABELS ",
 InputForm[If[Length[zeeNuPairs]==0,{},zeeNuPairs[[All,1]]]]];

(* A leptonic charged-scalar loop is a CANDIDATE contribution.
   SARAH can return B0 scalar integrals that are purely
   lepton-number-preserving. A nonzero Majorana Sigma^S
   requires the appropriate chiral combination and f-Y interference. *)
zeeNuSumExpressions=If[Length[zeeNuPairs]==0,{},zeeNuPairs[[All,2]]];
zeeHasB0Q=!FreeQ[zeeNuSumExpressions,B0[___]];
zeeHasFeMassQ=!FreeQ[zeeNuSumExpressions,Mass[Fe[___]]];
zeeHasHmQ=!FreeQ[zeeNuSumExpressions,Hm[___]] ||
 !FreeQ[zeeDiagPairs,Hm[___]];
zeeHasFeQ=!FreeQ[zeeNuSumExpressions,Fe[___]] ||
 !FreeQ[zeeDiagPairs,Fe[___]];
Print["ZEE_E3_SELFENERGY_NEUTRINO_SECTOR_HAS_B0 ",zeeHasB0Q];
Print["ZEE_E3_SELFENERGY_NEUTRINO_SECTOR_HAS_MASS_FE ",zeeHasFeMassQ];
Print["ZEE_E3_SELFENERGY_NEUTRINO_SECTOR_HAS_CHARGED_HIGGS ",zeeHasHmQ];
Print["ZEE_E3_SELFENERGY_NEUTRINO_SECTOR_HAS_CHARGED_LEPTON ",zeeHasFeQ];

Export[zeeLoopRawFile,StringRiffle[Join[
  {"SARAH GENERATED LOOP EXPRESSIONS; NO NUMERIC MAJORANA MASS CLAIM",
   "SUMS INDEXED BY ParticlesSelfEnergy1LoopSum[EWSB]"},
  (ToString[InputForm[#]]&/@zeeNuPairs),
  {"DIAGRAM_LIST INDEXED BY FIRST ELEMENT OF EACH LIST"},
  (ToString[InputForm[#]]&/@zeeDiagPairs)
 ],"\n\n"]<>"\n","Text"];
Print["ZEE_E3_SELFENERGY_RAW_FILE ",zeeLoopRawFile];

If[Length[zeeNuPairs]==0 && Length[zeeDiagPairs]==0,
 Print["ZEE_E3_SELFENERGY_NO_EXTERNAL_NEUTRINO_LABEL ",
  "No identified Fv/vL-type EXTERNAL entry in SARAH output."];
 zeeLoopStatus["SARAH_NEUTRINO_EXTERNAL_SECTOR_NOT_IDENTIFIED"];
 Exit[12]];
If[Length[zeeNuPairs]==0 || Length[zeeDiagPairs]==0,
 Print["ZEE_E3_SELFENERGY_UNALIGNED_NEUTRINO_SUM_AND_DIAGRAM_INVENTORY"];
 zeeLoopStatus["SARAH_NEUTRINO_SECTOR_INVENTORY_INCOMPLETE"];
 Exit[13]];
Print["ZEE_E3_SELFENERGY_MAJORANA_MASS_NUMERICALLY_EXTRACTED False"];
Print["ZEE_E3_SELFENERGY_E3_MNU_NUMERICALLY_MATCHED False"];
Print["ZEE_E3_SELFENERGY_REAL_309_SOURCE_TESTED False"];
If[!TrueQ[zeeHasB0Q] || !TrueQ[zeeHasFeMassQ] ||
   !TrueQ[zeeHasHmQ] || !TrueQ[zeeHasFeQ],
 zeeLoopStatus["SARAH_NEUTRINO_SECTOR_REQUIRED_LOOP_INGREDIENTS_NOT_IDENTIFIED"];
 Exit[14]];
(* This PASS is for correct EXTERNAL sector and loop ingredients only;
   it is NOT evidence of a completed Majorana self-energy evaluation. *)
zeeLoopStatus[
 "SARAH_NEUTRINO_EXTERNAL_SECTOR_FE_HM_B0_CANDIDATE_MAJORANA_UNVALIDATED"];
Exit[0];
