(* TARCER raw two-loop measure = minus PV-normalized two-loop measure. *)
$FeynCalcStartupMessages=False;$LoadAddOns={"TARCER"};
fc=Environment["D16_FEYNCALC_ROOT"];
If[!StringQ[fc]||!DirectoryQ[fc],Exit[2]];
Get[FileNameJoin[{fc,"FeynCalc.m"}]];
out=Environment["D16_OUTPUT_DIR"];
expr=Get[FileNameJoin[{out,"w_ibp_input.m"}]];
res=TimeConstrained[TarcerRecurse[expr],90,$Failed];
If[res===$Failed,Exit[2]];
Put[res,FileNameJoin[{out,"w_ibp_reduced.m"}]];
r=Expand[res/.{TAI[D,0,{{1,Sqrt[h]}}]->I th,TAI[D,0,{{1,Sqrt[w]}}]->I tw,
TJI[D,0,{{1,Sqrt[w]},{1,0},{1,0}}]->s0,
TJI[D,0,{{1,Sqrt[w]},{1,Sqrt[h]},{1,0}}]->s1,
TJI[D,0,{{1,Sqrt[w]},{1,Sqrt[w]},{1,Sqrt[h]}}]->s2}];
co=Table[Factor[Coefficient[Expand[-r],k]],{k,{th tw,tw^2,s0,s1,s2}}];
If[!FreeQ[r,TAI|TJI],Exit[2]];
If[Together[r+co.{th tw,tw^2,s0,s1,s2}]=!=0,Exit[2]];
Export[FileNameJoin[{out,"w_ibp_coefficients.json"}],<|"basis"->{"AhAw","AwAw","S_w00_E","S_wh0_E","S_wwh_E"},"coefficients"->(ToString[#,InputForm]&/@co)|>,"RawJSON"];
Print["EXPORTED ",Length[co]];Quit[];
