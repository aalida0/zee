(* Fresh native source check on two saved D12 cards, no spectrum generation. *)
root=Directory[];out=Environment["ZEE_SUSHI_NATIVE_OUT"];
If[!StringQ[out]||!DirectoryQ[out],Exit[2]];
sarah=FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH-4.15.4","SARAH.m"}];
Get[sarah];
SARAH[OutputDirectory]=FileNameJoin[{out,"sarah_output"}];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],Exit[3]];
queries=Join[Flatten[Table[{bar[q[{3}]],q[{3}],s},{s,{hh[{2}],Ah[{2}]}},{q,{Fu,Fd}}],1],
 Flatten[Table[{s,conj[Hm[{k}]],VWm},{s,{hh[{2}],Ah[{2}]}},{k,{2,3}}],1],
 {{hh[{2}],hh[{1}],hh[{1}]},{Ah[{2}],hh[{1}],VZ}}];
raw=SARAH`Vertex[#,Eigenstates->EWSB]& /@ queries;
expanded=raw //.
 HoldPattern[sum[index_,lo_,hi_,term_]]:>Sum[term,{index,lo,hi}];
coeffs=Map[#[[2;;,1]]&,expanded];
coeffs=coeffs/.(e:(h_Symbol)[_,_]/;SymbolName[h]==="Delta":>1);
numericRules[card_]:=Flatten[KeyValueMap[Function[{key,value},
 If[AssociationQ[value],With[{s=ToExpression[key],a=value["real"]+I*value["imag"]},
 Flatten[Table[s[i,j]->a[[i,j]],{i,Length[a]},{j,Length[a[[1]]]}]]],
 If[ListQ[value],With[{s=ToExpression[key],a=value},
 Flatten[Table[s[i,j]->a[[i,j]],{i,Length[a]},{j,Length[a[[1]]]}]]],
 ToExpression[key]->value]]],card]];
cards=Import[FileNameJoin[{out,"native_inputs.json"}],"RawJSON"];
cases=Table[vals=N[coeffs/.numericRules[card["rules"]]/.conj->Conjugate];
 If[!And@@(NumberQ/@Flatten[vals]),Print[InputForm[vals]];Exit[5]];
 <|"id"->card["id"],"coefficients"->Map[<|"real"->Re[#],"imag"->Im[#]|>&,vals,{2}]|>,{card,cards}];
Export[FileNameJoin[{out,"native_vertices.json"}],
 <|"status"->"NATIVE_EXTRACTED_REQUIRES_COMPARISON","math_version"->$Version,
 "sarah_version"->ToString[SA`Version],"sarah_sha256"->FileHash[sarah,"SHA256","HexString"],
 "raw"->(ToString[#,InputForm]& /@ raw),"cases"->cases,
 "input_sha256"->FileHash[FileNameJoin[{out,"native_inputs.json"}],"SHA256","HexString"]|>,"RawJSON"];
Exit[0];
