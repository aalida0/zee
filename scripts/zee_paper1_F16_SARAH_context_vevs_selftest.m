(* F16 local Mathematica-only VEV symbol context self-test. *)
Get[FileNameJoin[{Directory[],"scripts",
  "zee_paper1_F16_SARAH_context_vevs.m"}]];
If[zeeF16VEVResolverStatus=!="F16_CONTEXT_SAFE_PHYSICAL_F13_VEVS",
  Print["F16_VEV_CONTEXT_SELFTEST_FAIL_RESOLVER_NOT_LOADED"];Exit[31]];
m=246.22;b=1.393;
(* Explicit context symbols reproduce the Global/SARAH/Susyno shadowing
   reported by the actual local F16 SARAH mass matrices. *)
input={
 {Global`v1,Global`v2},
 {SARAH`v1,SARAH`v2},
 {Susyno`LieGroups`v1,Susyno`LieGroups`v2},
 {Global`v1^2+SARAH`v2^2,
  Susyno`LieGroups`v1*SARAH`v2}
};
actual=zeeF16ResolveVEVs[input,m,b];
v1=m Cos[b];v2=m Sin[b];
expected={{v1,v2},{v1,v2},{v1,v2},{v1^2+v2^2,v1*v2}};
If[!MatrixQ[actual,NumericQ] ||
    Max[Abs[Flatten[actual-expected]]]>1.*^-10,
  Print["F16_VEV_CONTEXT_SELFTEST_FAIL_VALUES ",InputForm[actual]];
  Exit[32]];
(* An unknown context must NOT be guessed/mapped. The audit's NumericQ
   requirement will then terminate rather than silently invent values. *)
other=zeeF16ResolveVEVs[{UnknownF16Context`v1,Global`v2},m,b];
If[NumericQ[other[[1]]],
  Print["F16_VEV_CONTEXT_SELFTEST_FAIL_UNHANDLED_CONTEXT_GUESSED"];
  Exit[33]];
If[!NumericQ[other[[2]]],
  Print["F16_VEV_CONTEXT_SELFTEST_FAIL_GLOBAL_CONTEXT"];
  Exit[34]];
Print["F16_VEV_CONTEXT_SELFTEST_PASS"];
Exit[0];
