(* Read-only frozen model; all generated output stays in D16 scratch.
   Run from repository root: math -script research/wgamma_d16/extract_vertices.m *)
root = Directory[];
out = FileNameJoin[{root,"research","wgamma_d16","local"}];
If[!DirectoryQ[out],CreateDirectory[out,CreateIntermediateDirectories->True]];
Get[FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH","SARAH.m"}]];
SARAH[OutputDirectory] = FileNameJoin[{out,"sarah_output"}];
SARAH[InputDirectories] = Prepend[SARAH[InputDirectories],FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded] || TrueQ[SARAH`AbortStart],Exit[2]];
queries = Join[
 Table[{"sWW_"<>ToString[k],{hh[{k}],VWm,conj[VWm]}},{k,2}],
 Table[{"sGG_"<>ToString[k],{hh[{k}],Hm[{1}],conj[Hm[{1}]]}},{k,2}],
 Flatten[Table[{"sWH_"<>ToString[{k,a}],{hh[{k}],Hm[{a}],conj[VWm]}},{k,2},{a,{2,3}}],1],
 Table[{"AWG_"<>ToString[c],If[c==1,{Ah[{2}],Hm[{1}],conj[VWm]},
   {Ah[{2}],conj[Hm[{1}]],VWm}]},{c,2}],
 Flatten[Table[{"sWG_"<>ToString[{k,c}],If[c==1,
   {hh[{k}],Hm[{1}],conj[VWm]},{hh[{k}],conj[Hm[{1}]],VWm}]},{k,2},{c,2}],1],
 Flatten[Table[{"sGhost_"<>ToString[{k,c}],{hh[{k}],bar[c],c}},{k,2},{c,{gWm,gWmC}}],1],
 Table[{"photonWG_"<>ToString[k],{VP,conj[VWm],Hm[{k}]}},{k,3}],
 Table[{"photonWGconj_"<>ToString[k],{VP,VWm,conj[Hm[{k}]]}},{k,3}],
 Table[{"photonGG_"<>ToString[k],{VP,Hm[{k}],conj[Hm[{k}]]}},{k,3}],
 Flatten[Table[{"sPhotonWG_"<>ToString[{k,c}],If[c==1,
   {hh[{k}],VP,conj[VWm],Hm[{1}]},{hh[{k}],VP,VWm,conj[Hm[{1}]]}]},{k,2},{c,2}],1],
 {{"photonWW",{VP,VWm,conj[VWm]}},
  {"photonPhotonWW",{VP,VP,VWm,conj[VWm]}},
  {"photonPhotonGG",{VP,VP,Hm[{1}],conj[Hm[{1}]]}},
  {"photonGhostMinus",{VP,bar[gWm],gWm}},
  {"photonGhostPlus",{VP,bar[gWmC],gWmC}},
  {"AWW",{Ah[{2}],VWm,conj[VWm]}},
  {"AGG",{Ah[{2}],Hm[{1}],conj[Hm[{1}]]}},
  {"AGhostMinus",{Ah[{2}],bar[gWm],gWm}},
  {"AGhostPlus",{Ah[{2}],bar[gWmC],gWmC}},
  {"Glepton",{bar[Fe[{1}]],Fv[{1}],Hm[{1}]}},
  {"Wlepton",{bar[Fe[{1}]],Fv[{1}],VWm}}},
 Flatten[Table[{"Hlepton_"<>ToString[{k,a,b}],{bar[Fe[{a}]],Fv[{b}],Hm[{k}]}},
  {k,{2,3}},{a,2},{b,2}],2],
 Flatten[Table[{"LFV_"<>ToString[{k,a,b}],{bar[Fe[{a}]],Fe[{b}],hh[{k}]}},
  {k,2},{a,2},{b,2}],2]
];
raw=Association[];
Do[vtx=SARAH`Vertex[item[[2]],Eigenstates->EWSB];
 raw[item[[1]]]=vtx;Print["D16_VERTEX ",item[[1]]," ",InputForm[vtx]],{item,queries}];
Export[FileNameJoin[{out,"vertices_raw.m"}],raw,"Package"];
report=<|"status"->"RAW_EXTRACTED_NOT_VALIDATED","mathematica_version"->$Version,
 "sarah_version"->ToString[SA`Version],"raw"->Map[ToString[#,InputForm]&,raw],
 "query_count"->Length[queries],
 "goldstone_mass_matrix"->ToString[SARAH`MassMatrix[Hm],InputForm]|>;
If[!FreeQ[Values[raw],$Aborted|$Failed|SARAH`Vertex],report["status"]="FAIL"];
Export[FileNameJoin[{out,"vertices.json"}],report,"RawJSON"];
Print["D16_VERTEX_STATUS ",report["status"]];
Exit[If[report["status"]==="FAIL",3,0]];
