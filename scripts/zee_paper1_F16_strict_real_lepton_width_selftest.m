(* F16 regression: actual kernel must numerically reduce 3x2 reference
   lepton width matrix encoded as real + 0 I by exact F13 fixtures.
   Old Max[complex,real] left the residual symbolic and could falsely PASS.
*)
root=Directory[];
Get[FileNameJoin[{root,"scripts",
   "zee_paper1_F16_strict_real_lepton_width_residual.m"}]];
If[!ValueQ[zeeF16WidthResidualStatus]||
   zeeF16WidthResidualStatus=!="F16_STRICT_REAL_COMPLEX_WIDTH_RESIDUAL_GUARD",
 Print["F16_LEPTON_WIDTH_SELFTEST_FAIL_MODULE_NOT_LOADED"];Exit[20]];
reference={
 {5.8547843232606706*^-5+0.*I,1.3995630170870587*^-4+0.*I},
 {7.38722349896239*^-4+0.*I,8.419849212048413*^-4+0.*I},
 {0.+0.*I,0.+0.*I}};
computed=Re[reference];
(* Source-comparison must be numerical, exactly zero for identical widths. *)
r0=zeeF16RelativeLeptonWidthResidual[computed,reference];
If[!NumericQ[r0]||!TrueQ[r0==0],
 Print["F16_LEPTON_WIDTH_SELFTEST_FAIL_REAL_ZERO ",InputForm[r0]];
 Exit[21]];
(* Perturb a real entry by a known controlled fractional error. *)
scaled=computed;
scaled[[1,1]]=computed[[1,1]]*(1+1.*^-7);
r1=zeeF16RelativeLeptonWidthResidual[scaled,reference];
If[!NumericQ[r1]||!TrueQ[8.*^-8<r1<1.2*^-7],
 Print["F16_LEPTON_WIDTH_SELFTEST_FAIL_REAL_PERTURBATION ",
   InputForm[r1]];Exit[22]];
(* A genuine imaginary partial width is unphysical and MUST fail. *)
unphysical=reference;
unphysical[[1,1]]=unphysical[[1,1]]+1.*^-6*I;
r2=zeeF16RelativeLeptonWidthResidual[computed,unphysical];
If[r2=!=$Failed,
 Print["F16_LEPTON_WIDTH_SELFTEST_FAIL_NONZERO_IM ",InputForm[r2]];
 Exit[23]];
(* Source or calculated array with missing symbol cannot be accepted. *)
r3=zeeF16RelativeLeptonWidthResidual[
  ReplacePart[computed,{1,1}->F16UnknownSymbol],reference];
If[r3=!=$Failed,
 Print["F16_LEPTON_WIDTH_SELFTEST_FAIL_SYMBOLIC_RESIDUAL ",
   InputForm[r3]];Exit[24]];
(* Invalid or negative width must fail, not be silently rounded away. *)
r4=zeeF16RelativeLeptonWidthResidual[
  ReplacePart[computed,{1,1}->-1.*^-3],reference];
If[r4=!=$Failed,
 Print["F16_LEPTON_WIDTH_SELFTEST_FAIL_NEGATIVE ",InputForm[r4]];
 Exit[25]];
r5=zeeF16RelativeLeptonWidthResidual[{{1.,2.}},reference];
If[r5=!=$Failed,
 Print["F16_LEPTON_WIDTH_SELFTEST_FAIL_SHAPE ",InputForm[r5]];
 Exit[26]];
Print["F16_LEPTON_WIDTH_NUMERICAL_SELFTEST_PASS"];
Exit[0];
