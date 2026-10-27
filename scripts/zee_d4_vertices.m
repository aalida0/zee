(* Read-only SARAH EWSB extraction. Run from repository root. *)
root=Directory[];
out=FileNameJoin[{root,"validation","module7","local"}];
If[!DirectoryQ[out],CreateDirectory[out,CreateIntermediateDirectories->True]];
report=<|"status"->"NATIVE_EXTRACTION_BLOCKED","math_version"->$Version|>;
save[]:=Export[FileNameJoin[{out,"d4_native.json"}],report,"RawJSON"];
save[];
sarah=FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[sarah],save[];Exit[2]];
Get[sarah];
SARAH[OutputDirectory]=FileNameJoin[{out,"d4_sarah_output"}];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],save[];Exit[3]];
report["sarah_version"]=ToString[SA`Version];
queries=Join[
 Flatten[Table[{{bar[Fu[{i}]],Fd[{j}],conj[Hm[{k}]]},
 {bar[Fd[{j}]],Fu[{i}],Hm[{k}] }},{k,2,3},{i,1,3},{j,1,3}],3],
 Flatten[Table[{{hh[{j}],conj[Hm[{k}]],VWm},
 {hh[{j}],Hm[{k}],conj[VWm]}},{k,2,3},{j,1,2}],2],
 Flatten[Table[{{Ah[{2}],conj[Hm[{k}]],VWm},
 {Ah[{2}],Hm[{k}],conj[VWm]}},{k,2,3}],1],
 {{hh[{1}],conj[Hm[{2}]],Hm[{3}]},
 {hh[{2}],conj[Hm[{2}]],Hm[{3}]},
 {Ah[{2}],conj[Hm[{2}]],Hm[{3}]},
 {hh[{1}],conj[Hm[{3}]],Hm[{2}]},
 {hh[{2}],conj[Hm[{3}]],Hm[{2}]},
 {Ah[{2}],conj[Hm[{3}]],Hm[{2}]}},
 Flatten[Table[{{bar[Fv[{j}]],Fe[{i}],conj[Hm[{k}]]},
 {bar[Fe[{i}]],Fv[{j}],Hm[{k}]}},{k,2,3},{i,1,3},{j,1,3}],3],
 {{conj[Hm[{2}]],Hm[{3}],VP},{conj[Hm[{2}]],Hm[{3}],VZ},
 {conj[Hm[{2}]],VWm,VZ},{conj[Hm[{2}]],VWm,VP},
 {conj[Hm[{3}]],VWm,VZ},{conj[Hm[{3}]],VWm,VP},
 {Hm[{2}],conj[VWm],VZ},{Hm[{2}],conj[VWm],VP},
 {Hm[{3}],conj[VWm],VZ},{Hm[{3}],conj[VWm],VP}}];
raw=SARAH`Vertex[#,Eigenstates->EWSB]& /@ queries;
report["queries"]=ToString[#,InputForm]& /@ queries;
report["raw_vertices"]=ToString[#,InputForm]& /@ raw;
momentumDifference[expr_]:=Module[{terms},
 terms=Cases[expr,e:(h_Symbol)[_,_]/;SymbolName[h]==="Mom":>e,Infinity];
 Length[terms]===2 && (expr===terms[[1]]-terms[[2]] || expr===terms[[2]]-terms[[1]])];
report["momentum_differences_verified"]=And@@Table[momentumDifference[raw[[i,2,2]]],
 {i,Join[Range[37,48],{91,92}]}];
report["chirality_labels_verified"]=And@@Table[raw[[i,2;;,2]]==={PL,PR},
 {i,Join[Range[1,36],Range[55,90]]}];
expanded=raw /. HoldPattern[sum[index_,lo_,hi_,term_]] :> Sum[term,{index,lo,hi}];
expanded=expanded //. HoldPattern[sum[index_,lo_,hi_,term_]] :> Sum[term,{index,lo,hi}];
coeffs=Map[#[[2;;,1]]&,expanded];
(* SARAH's color Delta has its own context; strip only that named head.
   The resulting fixed-color amplitude receives Nc=3 in the spin sum. *)
colorStripped=coeffs/.(e:(h_Symbol)[_,_]/;SymbolName[h]==="Delta":>1);
numericRules[card_]:=Flatten[KeyValueMap[Function[{key,value},
 If[AssociationQ[value],With[{s=ToExpression[key],a=value["real"]+I*value["imag"]},
  Flatten[Table[s[i,j]->a[[i,j]],{i,Length[a]},{j,Length[a[[1]]]}]]],
 If[ListQ[value],With[{s=ToExpression[key],a=value},
  Flatten[Table[s[i,j]->a[[i,j]],{i,Length[a]},{j,Length[a[[1]]]}]]],
  ToExpression[key]->value]]],card]];
inputs=Import[FileNameJoin[{out,"d4_native_inputs.json"}],"RawJSON"];
report["input_sha256"]=FileHash[FileNameJoin[{out,"d4_native_inputs.json"}],"SHA256","HexString"];
report["numeric_cases"]=Table[
 vals=N[colorStripped/.numericRules[card["rules"]]/.conj->Conjugate];
 If[!And@@(NumberQ/@Flatten[vals]),
  Export[FileNameJoin[{out,"d4_unresolved.txt"}],ToString[{card["id"],vals,numericRules[card["rules"]]},InputForm],"Text"];
  report["status"]="NATIVE_NUMERIC_SUBSTITUTION_BLOCKED";
  report["unresolved_case"]=card["id"];save[];Exit[5]];
 <|"id"->card["id"],"coefficients"->Map[<|"real"->Re[#],"imag"->Im[#]|>&,vals,{2}]|>,
 {card,inputs}];
(* Exact physical CP-odd and photon zeros, before numerical substitution. *)
mix={{Cos[b],Sin[b],0},{-Sin[b]*Cos[y],Cos[b]*Cos[y],Sin[y]},
 {Sin[b]*Sin[y],-Cos[b]*Sin[y],Cos[y]}};
symRules=Join[Flatten[Table[ZP[i,j]->mix[[i,j]],{i,3},{j,3}]],
 {ZA[2,1]->-Sin[b],ZA[2,2]->Cos[b],v1->v*Cos[b],v2->v*Sin[b],
 g1->g2*Tan[ThetaW]}];
report["exact_zero_CP_A"]=TrueQ[FullSimplify[coeffs[[51,1]]/.symRules]===0]&&
 TrueQ[FullSimplify[coeffs[[54,1]]/.symRules]===0];
report["exact_zero_offdiagonal_photon"]=TrueQ[FullSimplify[coeffs[[91,1]]/.symRules]===0];
report["exact_zero_WZ_Wphoton"]=And@@Table[TrueQ[FullSimplify[c/.symRules]==={0}],{c,coeffs[[93;;100]]}];
report["source_sha256"]=Association[Table[
 f->FileHash[FileNameJoin[{root,f}],"SHA256","HexString"],
 {f,{"models/SARAH/ZeeTypeII/ZeeTypeII.m","models/SARAH/ZeeTypeII/parameters.m",
 "models/SARAH/ZeeTypeII/particles.m","scripts/zee_d4_vertices.m"}}]];
report["sarah_sha256"]=FileHash[sarah,"SHA256","HexString"];
report["status"]="NATIVE_VERTICES_EXTRACTED_NOT_YET_VALIDATED";
save[];
Print["D4_NATIVE ",Length[raw]];
Exit[0];
