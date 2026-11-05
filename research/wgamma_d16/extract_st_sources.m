(* NEW sources needed for charged-parent ST identities, not a rerun of the
   completed 58-vertex inventory. Read-only model; no model/code generation. *)
root=Directory[];
out=FileNameJoin[{root,"research","wgamma_d16","local"}];
Get[FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH","SARAH.m"}]];
SARAH[OutputDirectory]=FileNameJoin[{out,"sarah_st_output"}];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded] || TrueQ[SARAH`AbortStart],Exit[2]];
raw=Association[];
queries=Flatten[Table[{ToString[{k,a,c},InputForm],
 If[c==1,{hh[{k}],Hm[{1}],conj[Hm[{a}]]},
         {hh[{k}],conj[Hm[{1}]],Hm[{a}]}]},{k,2},{a,{2,3}},{c,2}],2];
(* Do not dynamically bind a or c while calling SARAH: its old routines
   use these symbols in patterns without localizing every intermediate. *)
Do[raw[d16entry[[1]]]=SARAH`Vertex[d16entry[[2]],Eigenstates->EWSB],{d16entry,queries}];
gf=DEFINITION[EWSB][GeneratedGaugeFixing];
gt=Select[GaugeTransformation, !FreeQ[First[#],VWm|VP|Hm|hh]&];
If[Head[gf]=!=List,Print["Missing generated gauge fixing"];Exit[3]];
report=<|"scope"->"New s-G-H charged-parent sources and generated BRST/gauge fixing; not physical matching",
 "raw"->Map[ToString[#,InputForm]&,raw],
 "generated_gauge_fixing"->ToString[gf,InputForm],
 "gauge_transformations"->ToString[gt,InputForm],
 "mathematica"->$Version,"sarah_version"->ToString[SA`Version]|>;
Put[raw,FileNameJoin[{out,"st_vertices_raw.m"}]];
Export[FileNameJoin[{out,"st_sources.json"}],report,"RawJSON"];
Print["D16_NEW_ST_SOURCES ",Length[raw]," GF=",InputForm[gf]];
Exit[0];
