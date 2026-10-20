(* SARAH 4.15.4: charge-conjugated Zee LL s+ interaction probe.
   Diagnostics ONLY; does not certify f normalization, LFV or neutrino masses.
   Run from repo root: math -script scripts/zee_sarah_fzee_orientation_probe.m *)
root=Directory[];
outDir=FileNameJoin[{root,"work","sarah_zee"}];
If[!DirectoryQ[outDir],CreateDirectory[outDir,CreateIntermediateDirectories->True]];
statusFile=FileNameJoin[{outDir,"fzee_orientation_status.txt"}];
setFStatus[zeeFStatus_String]:=(
 Export[statusFile,zeeFStatus<>"\n","Text"];
 Print["ZEE_F_ORIENTATION_STATUS ",zeeFStatus]
);
setFStatus["FZEE_ORIENTATION_NOT_VALIDATED"];
src=FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[src],setFStatus["SARAH_NOT_FOUND"];Exit[2]];
PrependTo[$Path,DirectoryName[src]];
loaded=CheckAbort[(Get[src];True),False];
If[!TrueQ[loaded]||!ValueQ[SA`Version],
 setFStatus["SARAH_LOAD_FAILED"];Exit[3]];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],
 FileNameJoin[{root,"models","SARAH"}]];
SA`Start["ZeeTypeII"];
If[!TrueQ[SA`ModelLoaded]||TrueQ[SA`AbortStart],
 setFStatus["SARAH_START_FAILED"];Exit[4]];

(* SARAH's symmetry rules can be guarded by UseSymmASymm == True.
   Read symbol names and current values; do not toggle the user's
   Mathematica session or interpret symbolic Fzee[i,i] as a failure. *)
switches=Names["*UseSymmASymm"];
Print["ZEE_F_SYMMETRY_SWITCH_NAMES ",InputForm[switches]];
Do[Print["ZEE_F_SYMMETRY_SWITCH_VALUE ",name," ",
 InputForm[ToExpression[name]]],{name,switches}];
Print["ZEE_F_PARAMETER_METADATA ",
 InputForm[Select[ParameterDefinitions,Function[z,z[[1]]===Fzee]]]];
Print["ZEE_F_DIRECT_DIAGONAL ",InputForm[Fzee[1,1]]];
Print["ZEE_F_DIRECT_ANTISYM ",InputForm[Fzee[1,2]+Fzee[2,1]]];

(* The ordinary barred/unbarred fermion orientations isolate Ye,Ye2;
   LL s+ instead couples two same-orientation spinors, and its HC
   couples their conjugates. Probe BOTH charges and BOTH external
   field orders. Repeating with generation indices avoids conflating
   a generic and a component-expanded SARAH Vertex query. *)
queries={
 {"ordinary_Ye_Hm",{bar[Fe],Fv,Hm},EWSB},
 {"ordinary_Ye_Hp",{bar[Fv],Fe,conj[Hm]},EWSB},
 {"LL_Hp",{Fe,Fv,conj[Hm]},EWSB},
 {"LL_Hp_rev",{Fv,Fe,conj[Hm]},EWSB},
 {"LL_Hm",{Fe,Fv,Hm},EWSB},
 {"LL_Hm_rev",{Fv,Fe,Hm},EWSB},
 {"barbar_Hm",{bar[Fe],bar[Fv],Hm},EWSB},
 {"barbar_Hm_rev",{bar[Fv],bar[Fe],Hm},EWSB},
 {"barbar_Hp",{bar[Fe],bar[Fv],conj[Hm]},EWSB},
 {"barbar_Hp_rev",{bar[Fv],bar[Fe],conj[Hm]},EWSB},
 {"LL_Hp_12",{Fe[{1}],Fv[{2}],conj[Hm[{2}]]},EWSB},
 {"LL_Hp_21",{Fe[{2}],Fv[{1}],conj[Hm[{2}]]},EWSB},
 {"LL_Hp_12_heavy",{Fe[{1}],Fv[{2}],conj[Hm[{3}]]},EWSB},
 {"barbar_Hm_12",{bar[Fe[{1}]],bar[Fv[{2}]],Hm[{2}]},EWSB},
 {"gauge_LL_splus",{eL,vL,Sp},GaugeES},
 {"gauge_LL_splus_rev",{vL,eL,Sp},GaugeES},
 {"gauge_LL_sminus",{eL,vL,conj[Sp]},GaugeES}
};
results={};
Do[
 label=item[[1]]; fields=item[[2]]; basis=item[[3]];
 Print["ZEE_F_QUERY_BEGIN ",label];
 value=CheckAbort[SA`Vertex[fields,Eigenstates->basis],$Aborted];
 hasF=!FreeQ[value,Fzee];
 Print["ZEE_F_QUERY_RESULT ",label," HAS_FZEE=",hasF,
 " HAS_YE=",!FreeQ[value,Ye],
 " HAS_YE2=",!FreeQ[value,Ye2],
 " ABORTED=",value===$Aborted];
 If[hasF,Print["ZEE_F_FOUND_VERTEX ",label," ",InputForm[value]]];
 AppendTo[results,{label,fields,basis,value,hasF}],
 {item,queries}
];
dump=FileNameJoin[{outDir,"fzee_orientation_vertices.txt"}];
Export[dump,StringRiffle[Table[
 ToString[results[[i,1]]]<>" [Basis="<>
 ToString[InputForm[results[[i,3]]]]<>
 "] HAS_FZEE="<>ToString[results[[i,5]]]<>":\n"<>
 ToString[InputForm[results[[i,4]]]],
 {i,Length[results]}],"\n\n"]<>"\n","Text"];
hits=Cases[results,{label_,_,_,_,True}:>label];
Print["ZEE_F_MATCH_COUNT ",Length[hits]];
Print["ZEE_F_MATCH_LABELS ",InputForm[hits]];
Print["ZEE_F_RAW_FILE ",dump];
If[AnyTrue[results,#[[4]]===$Aborted&],
 setFStatus["FZEE_VERTEX_PROBE_ABORTED"];Exit[5]];
If[Length[hits]==0,
 setFStatus["FZEE_NOT_FOUND_IN_PROBED_ORIENTATIONS_NOT_VALIDATED"];
 Exit[6]];
setFStatus["FZEE_PRESENT_IN_PROBED_VERTICES_NORMALIZATION_NOT_VALIDATED"];
Exit[0];
