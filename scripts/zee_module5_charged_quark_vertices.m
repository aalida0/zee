(* Module5 independent raw charged-quark SARAH vertex extraction.
   Run from repository root:
   /usr/local/bin/math -script scripts/zee_module5_charged_quark_vertices.m
   Raw vertices are NOT Wilson-coefficient matching. *)
root=Directory[];
out=FileNameJoin[{root,"validation","module5","local"}];
If[!DirectoryQ[out],CreateDirectory[out,CreateIntermediateDirectories->True]];
numericalFile=FileNameJoin[{out,"native_numerical.json"}];
If[FileExistsQ[numericalFile],DeleteFile[numericalFile]];
report=<|"schema_version"->"1.1.0","status"->"NATIVE_VERTICES_NOT_EXTRACTED",
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
raw=Association[]; expressions=Association[];
Do[
 vertex=CheckAbort[SARAH`Vertex[query[[2]],Eigenstates->EWSB],$Aborted];
 expressions[query[[1]]]=vertex;
 raw[query[[1]]]=ToString[vertex,InputForm];
 Print["MODULE5_NATIVE_VERTEX ",query[[1]]," ",InputForm[vertex]],
 {query,queries}];
report["query_count"]=Length[queries];
report["raw_vertex_keys"]=Keys[raw];
report["raw_vertices"]=raw;
report["status"]=If[Length[queries]==58 &&
 And@@(ListQ[#] && Length[#]>=2 && FreeQ[#, $Aborted|SARAH`Vertex]& /@ Values[expressions]),
 "RAW_VERTICES_EXTRACTED_NOT_MATCHED","VERTEX_EXTRACTION_BLOCKED"];
report["warning"]="Raw vertices do not prove Hamiltonian, sigma or Wilson coefficient normalization.";
save[];
(* Supplement the original 58-entry inventory with the scalar photon current.
   Numerical rules are generated independently by zee_module5_native_compare.py.
   Keep expressions native: never substitute a historical charged-Higgs formula. *)
scalarRaw=Association[];
Do[key="photon_scalar_"<>ToString[k];
 vertex=SARAH`Vertex[{Hm[{k}],conj[Hm[{k}]],VP},Eigenstates->EWSB];
 expressions[key]=vertex;scalarRaw[key]=ToString[vertex,InputForm],{k,1,3}];
report["scalar_photon_vertices"]=scalarRaw;save[];
If[FileExistsQ[FileNameJoin[{out,"native_witnesses.m"}]],
 Get[FileNameJoin[{out,"native_witnesses.m"}]];
 numerical=Association[];
 Do[values=Association[];
  Do[expanded=expressions[key][[2;;,1]] //.
    HoldPattern[sum[index_,lo_,hi_,term_]] :> Sum[term,{index,lo,hi}];
   coeff=N[expanded /. witness[[2]] /. conj->Conjugate];
   If[!VectorQ[coeff,NumericQ],Print["NONNUMERIC ",key," ",InputForm[coeff]];Exit[7]];
   values[key]=({Re[#],Im[#]}& /@ coeff),{key,Keys[expressions]}];
  numerical[witness[[1]]]=values,{witness,nativeWitnesses}];
 Export[numericalFile,<|"status"->"NATIVE_NUMERICAL_EVALUATED",
  "driver_sha256"->FileHash[FileNameJoin[{root,"scripts","zee_module5_charged_quark_vertices.m"}],"SHA256","HexString"],
  "raw_sha256"->FileHash[FileNameJoin[{out,"charged_quark_vertices.json"}],"SHA256","HexString"],
  "witness_sha256"->FileHash[FileNameJoin[{out,"native_witnesses.m"}],"SHA256","HexString"],
  "cases"->numerical|>,"RawJSON"]];
Print["MODULE5_VERTEX_STATUS ",report["status"]];
Exit[If[report["status"]==="VERTEX_EXTRACTION_BLOCKED",6,0]];
