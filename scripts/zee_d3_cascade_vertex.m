(* Read-only frozen model, native Vertex only; no Make* or rebuild. *)
root=Directory[];
out=FileNameJoin[{root,"validation","module7","local"}];
If[!DirectoryQ[out],CreateDirectory[out,CreateIntermediateDirectories->True]];
report=<|"status"->"NATIVE_VERTEX_NOT_VERIFIED","math_version"->$Version|>;
save[]:=Export[FileNameJoin[{out,"native_vertex.json"}],report,"RawJSON"];
save[];
sarah=FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[sarah],save[];Exit[2]];
Get[sarah];
SARAH[OutputDirectory]=FileNameJoin[{out,"sarah_output"}];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],save[];Exit[3]];
report["sarah_version"]=ToString[SA`Version];
raw=Table[SARAH`Vertex[fields,Eigenstates->EWSB],{fields,{
 {conj[Hm[{2}]],Hm[{3}],VZ},{conj[Hm[{3}]],Hm[{2}],VZ},
 {conj[Hm[{2}]],Hm[{3}],VP}}}];
report["raw_vertices"]=ToString[#,InputForm]& /@ raw;
Print["D3_RAW ",InputForm[raw]];
(* Verify the native all-incoming scalar momentum difference structurally. *)
momentumDifference[expr_]:=Module[{terms},
 terms=Cases[expr,e:(h_Symbol)[_,_]/;SymbolName[h]==="Mom":>e,Infinity];
 Length[terms]===2 && (expr===terms[[1]]-terms[[2]] || expr===terms[[2]]-terms[[1]])];
lorentz=And@@Table[momentumDifference[v[[2,2]]],{v,raw}];
report["momentum_difference_verified"]=lorentz;
cases={};
Do[
 mix={{Cos[b],Sin[b],0},{-Sin[b]*Cos[y],Cos[b]*Cos[y],Sin[y]},
      {Sin[b]*Sin[y],-Cos[b]*Sin[y],Cos[y]}};
 cw=w/z;g=2*w/v;sw=Sqrt[1-cw^2];
 rules=Join[Flatten[Table[ZP[i,j]->mix[[i,j]],{i,3},{j,3}]],
  {g2->g,g1->g*sw/cw,ThetaW->ArcCos[cw]}];
 expanded=raw[[All,2,1]] //. HoldPattern[sum[index_,lo_,hi_,term_]] :> Sum[term,{index,lo,hi}];
 coeff=N[expanded/.rules/.conj->Conjugate];
 expected=I*g*Sin[2*y]/(4*cw);
 residual=Max[Abs[coeff-{expected,expected,0}]];
 AppendTo[cases,<|"beta_rad"->N[b],"gamma_rad"->N[y],"mW_GeV"->w,"mZ_GeV"->z,
  "v_GeV"->v,"absolute_coefficients"->Abs[coeff],
  "expected_absolute_coefficient"->Abs[expected],"signed_max_residual"->residual|>],
 {b,{1.394,0.6}},{y,{1.089,-1.089,0.,Pi/2,-Pi/2,Pi/2-1.089}},
 {w,{80.379}},{z,{91.1876}},{v,{246.21965,250.}}];
report["cases"]=cases;
report["max_residual"]=Max[Lookup[cases,"signed_max_residual"]];
Print["D3_CASE ",InputForm[First[cases]]];
report["model_sha256"]=FileHash[FileNameJoin[{root,"models","SARAH","ZeeTypeII","ZeeTypeII.m"}],"SHA256","HexString"];
report["driver_sha256"]=FileHash[FileNameJoin[{root,"scripts","zee_d3_cascade_vertex.m"}],"SHA256","HexString"];
report["status"]=If[TrueQ[lorentz]&&NumericQ[report["max_residual"]]&&report["max_residual"]<10^-12,
 "NATIVE_VERTEX_VERIFIED","NATIVE_VERTEX_NOT_VERIFIED"];
save[];Print["D3_NATIVE ",report["status"]];
Exit[If[report["status"]==="NATIVE_VERTEX_VERIFIED",0,4]];
