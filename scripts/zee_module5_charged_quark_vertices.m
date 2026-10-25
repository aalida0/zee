(* Module5 independent raw charged-quark SARAH vertex extraction.
   Run from repository root:
   /usr/local/bin/math -script scripts/zee_module5_charged_quark_vertices.m
   Raw vertices are NOT Wilson-coefficient matching. *)
root=Directory[];
out=FileNameJoin[{root,"validation","module5","local"}];
If[!DirectoryQ[out],CreateDirectory[out,CreateIntermediateDirectories->True]];
report=<|"schema_version"->"1.0.0","status"->"NATIVE_VERTICES_NOT_EXTRACTED",
         "math_version"->$Version,"physics_scope"->"RAW_EWSB_VERTICES_ONLY_NOT_C7_C8_MATCHING"|>;
save[]:=Export[FileNameJoin[{out,"charged_quark_vertices.json"}],report,"RawJSON"];
save[];
sarahFile=FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH","SARAH.m"}];
If[!FileExistsQ[sarahFile],report["error"]="SARAH.m not found";save[];Exit[2]];
CheckAbort[Get[sarahFile],report["error"]="SARAH load aborted";save[];Exit[3]];
SARAH[OutputDirectory]=FileNameJoin[{out,"sarah_output"}];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],FileNameJoin[{root,"models","SARAH"}]];
CheckAbort[SARAH`Start["ZeeTypeII"],report["error"]="Model load aborted";save[];Exit[4]];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],
 report["error"]="SARAH model not loaded";save[];Exit[5]];
report["sarah_version"]=ToString[SA`Version];
(* Both orientations, Goldstone and both physical states, all flavors.
   CKM conventions and chiral/phase factors must be derived, not assumed. *)
plus=Flatten[Table[
 {"plus_"<>ToString[{k,a,b}],{bar[Fu[{a}]],Fd[{b}],conj[Hm[{k}]]}},
 {k,1,3},{a,1,3},{b,1,3}],2];
minus=Flatten[Table[
 {"minus_"<>ToString[{k,b,a}],{bar[Fd[{b}]],Fu[{a}],Hm[{k}]}},
 {k,1,3},{b,1,3},{a,1,3}],2];
currents={
 {"photon_top",{bar[Fu[{3}]],Fu[{3}],VP}},
 {"photon_bottom",{bar[Fd[{3}]],Fd[{3}],VP}},
 {"gluon_top",{bar[Fu[{3}]],Fu[{3}],VG}},
 {"gluon_bottom",{bar[Fd[{3}]],Fd[{3}],VG}}
};
queries=Join[plus,minus,currents];
raw=Association[];
Do[
 vertex=CheckAbort[SARAH`Vertex[query[[2]],Eigenstates->EWSB],$Aborted];
 raw[query[[1]]]=ToString[vertex,InputForm];
 Print["MODULE5_NATIVE_VERTEX ",query[[1]]," ",InputForm[vertex]],
 {query,queries}];
report["query_count"]=Length[queries];
report["raw_vertex_keys"]=Keys[raw];
report["raw_vertices"]=raw;
report["status"]=If[Length[queries]==58 && 
 FreeQ[Values[raw],"_Aborted"|"SARAH`Vertex"],
 "RAW_VERTICES_EXTRACTED_NOT_MATCHED","VERTEX_EXTRACTION_BLOCKED"];
report["warning"]="Raw vertices do not prove Hamiltonian, sigma or Wilson coefficient normalization.";
save[];
Print["MODULE5_VERTEX_STATUS ",report["status"]];
Exit[If[report["status"]==="VERTEX_EXTRACTION_BLOCKED",6,0]];
