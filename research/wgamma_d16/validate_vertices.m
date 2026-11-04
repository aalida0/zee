(* Evaluate the actual saved SARAH expressions, independently of SARAH startup. *)
out=FileNameJoin[{Directory[],"research","wgamma_d16","local"}];
raw=Get[FileNameJoin[{out,"vertices_raw.m"}]];
expanded=Map[Function[x,x//.HoldPattern[sum[ind_,lo_Integer,hi_Integer,body_]]:>
 Total[Table[body,{ind,lo,hi}]]],raw];
checks={};
coefficient[v_,ch_]:=Total[Cases[Rest[v],{c_,l_}/;l===ch:>c]];
record[key_,ch_,expected_,rules_]:=Module[{actual,res},
 actual=N[coefficient[expanded[key],ch]/.rules//.conj[x_]:>Conjugate[x]];
 res=If[NumericQ[actual],Abs[actual-expected],1.*^300];
 AppendTo[checks,<|"key"->key,"structure"->ToString[ch,InputForm],
 "actual"->{Re[actual],Im[actual]},"expected"->{Re[expected],Im[expected]},
 "residual"->res|>]];
Get[FileNameJoin[{out,"vertex_witnesses.m"}]];
report=<|"status"->If[Max[Lookup[checks,"residual"]]<1.*^-8,"PASS","FAIL"],
 "scope"->"Native vertex coefficients only; no loop or gauge matching acceptance",
 "max_abs_residual"->Max[Lookup[checks,"residual"]],"checks"->checks,
 "returned_structures"->Map[ToString[Rest[#][[All,2]],InputForm]&,raw]|>;
Export[FileNameJoin[{out,"vertex_checks.json"}],report,"RawJSON"];
Print["D16_NATIVE_COEFFICIENT_CHECKS ",report["status"]," ",Length[checks],
 " max=",report["max_abs_residual"]];
Exit[If[report["status"]==="PASS",0,1]];
