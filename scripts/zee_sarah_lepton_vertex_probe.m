(* Diagnostic-only probe for complex Zee lepton interactions.
   LOCAL: math -script scripts/zee_sarah_lepton_vertex_probe.m
   Gate: do not claim Yukawa normalization/complex E3 agreement from
   source inspection or from a successful Vertex[] extraction alone. *)
root=Directory[];
outputDir=FileNameJoin[{root,"work","sarah_zee"}];
If[!DirectoryQ[outputDir],CreateDirectory[outputDir,CreateIntermediateDirectories->True]];
statusFile=FileNameJoin[{outputDir,"lepton_vertex_probe_status.txt"}];
setLeptonStatus[zeeLeptonStatus_String]:=(
 Export[statusFile,zeeLeptonStatus<>"\n","Text"];
 Print["ZEE_LEPTON_STATUS ",zeeLeptonStatus]
);
setLeptonStatus["LEPTON_VERTICES_NOT_VALIDATED"];
packageFile=FileNameJoin[{$HomeDirectory,".Mathematica","Applications",
  "SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[packageFile],
 setLeptonStatus["SARAH_PACKAGE_NOT_FOUND"];Exit[2]];
PrependTo[$Path,DirectoryName[packageFile]];
loaded=CheckAbort[(Get[packageFile];True),False];
If[!TrueQ[loaded] || !ValueQ[SA`Version],
 setLeptonStatus["SARAH_LOAD_FAILED"];Exit[3]];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],
 FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded] || TrueQ[SARAH`AbortStart],
 setLeptonStatus["SARAH_START_FAILED"];Exit[4]];
Print["ZEE_LEPTON_SARAH_VERSION ",SA`Version];
Print["ZEE_LEPTON_F_SYMMETRY_METADATA ",
 InputForm[Select[ParameterDefinitions,Function[zz,zz[[1]]===Fzee]]]];
Print["ZEE_LEPTON_F_11 ",InputForm[Fzee[1,1]]];
Print["ZEE_LEPTON_F_12 ",InputForm[Fzee[1,2]]];
Print["ZEE_LEPTON_F_21 ",InputForm[Fzee[2,1]]];
Print["ZEE_LEPTON_F_ANTISYM_TEST ",
 InputForm[FullSimplify[Fzee[1,2]+Fzee[2,1]]]];

leptonMass=SARAH`MassMatrix[Fe];
Print["ZEE_LEPTON_MASS_SHAPE ",InputForm[Dimensions[leptonMass]]];
Print["ZEE_LEPTON_MASS_RAW ",InputForm[leptonMass]];

(* Generic EWSB vertices. The two orientations probe both the
   charged singlet f interaction and ordinary doublet Yukawas.
   We do NOT assign f or Y to a numerical E3 source until the
   field basis and Lorentz/projector conventions are established. *)
cases={
 {"Hminus_barFe_Fv",{bar[Fe],Fv,Hm}},
 {"Hplus_barFv_Fe",{bar[Fv],Fe,conj[Hm]}},
 {"Hminus_barFe_Fv_2",{bar[Fe[{1}]],Fv[{2}],Hm[{2}]}},
 {"Hminus_barFe_Fv_3",{bar[Fe[{1}]],Fv[{2}],Hm[{3}]}},
 {"Hplus_barFv_Fe_2",{bar[Fv[{2}]],Fe[{1}],conj[Hm[{2}]]}},
 {"Hplus_barFv_Fe_3",{bar[Fv[{2}]],Fe[{1}],conj[Hm[{3}]]}},
 {"h125_barFe_Fe",{bar[Fe],Fe,hh}},
 {"Hheavy_barFe_Fe",{bar[Fe[{1}]],Fe[{2}],hh[{2}]}}
};
results={};
Do[
 Print["ZEE_LEPTON_VERTEX_BEGIN ",item[[1]]];
 value=CheckAbort[SARAH`Vertex[item[[2]],Eigenstates->EWSB],$Aborted];
 Print["ZEE_LEPTON_VERTEX ",item[[1]]," ",InputForm[value]];
 Print["ZEE_LEPTON_VERTEX_HAS_FZEE ",item[[1]]," ",
       !FreeQ[value,Fzee]];
 Print["ZEE_LEPTON_VERTEX_HAS_YE2 ",item[[1]]," ",
       !FreeQ[value,Ye2]];
 AppendTo[results,{item[[1]],value}],
 {item,cases}
];
Export[FileNameJoin[{outputDir,"lepton_vertices_raw.txt"}],
 StringRiffle[Join[
 {"LEPTON_MASS:\n"<>ToString[InputForm[leptonMass]]},
 Table[ToString[results[[i,1]]]<>":\n"<>
 ToString[InputForm[results[[i,2]]]],{i,Length[results]}]],
 "\n\n"]<>"\n","Text"];
If[MemberQ[results,$Aborted,Infinity],
 setLeptonStatus["LEPTON_VERTEX_PROBE_ABORTED"];Exit[5]];
setLeptonStatus["LEPTON_VERTEX_EXPRESSIONS_EXTRACTED_NOT_VALIDATED"];
Exit[0];
