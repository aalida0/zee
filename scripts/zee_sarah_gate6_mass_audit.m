(* Tree-level SARAH vs original Gate6 mass-matrix audit.
   Run from repo root after python3 scripts/zee_sarah_gate6_fixture.py.
   A PASS does not validate LFV, one-loop neutrino masses, widths or RGEs. *)
root = Directory[];
logDir = FileNameJoin[{root,"work","sarah_zee"}];
fixture = FileNameJoin[{logDir,"gate6_fixture.m"}];
statusFile = FileNameJoin[{logDir,"mass_audit_status.txt"}];
setMassStatus[zeeAuditStatus_String] := (
 Export[statusFile,zeeAuditStatus<>"\n","Text"];
 Print["ZEE_MASS_AUDIT_STATUS ",zeeAuditStatus]
);
If[!DirectoryQ[logDir],CreateDirectory[logDir,CreateIntermediateDirectories->True]];
setMassStatus["MASS_AUDIT_NOT_VALIDATED"];
If[!FileExistsQ[fixture],Print["FAIL GATE6_FIXTURE_MISSING ",fixture];Exit[2]];
install=FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[install],Print["FAIL SARAH_INSTALL_MISSING ",install];Exit[3]];
PrependTo[$Path,DirectoryName[install]];
loaded=CheckAbort[(Get[install];True),False];
If[!TrueQ[loaded] || !ValueQ[SA`Version],
 Print["FAIL SARAH_LOAD"];Exit[4]];
(* Keep all generated native output inside this checkout. *)
SARAH[OutputDirectory]=FileNameJoin[{Directory[],"work","sarah_zee","native_output"}];
If[!DirectoryQ[SARAH[OutputDirectory]],CreateDirectory[SARAH[OutputDirectory],CreateIntermediateDirectories->True]];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],
 FileNameJoin[{root,"models","SARAH"}]];
Print["ZEE_MASS_AUDIT_START_MODEL"];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded] || TrueQ[SARAH`AbortStart],
 setMassStatus["MASS_AUDIT_START_FAILED"];Exit[5]];
Get[fixture];

massHHRaw=SARAH`MassMatrix[hh];
massAhRaw=SARAH`MassMatrix[Ah];
massHmRaw=SARAH`MassMatrix[Hm];
rawDump=StringRiffle[{
 "HH:\n"<>ToString[InputForm[massHHRaw]],
 "AH:\n"<>ToString[InputForm[massAhRaw]],
 "HM:\n"<>ToString[InputForm[massHmRaw]]
},"\n\n"];
Export[FileNameJoin[{logDir,"mass_matrices_raw.txt"}],rawDump,"Text"];

(* SARAH includes gauge-fixing-dependent Goldstone masses in R_xi gauge.
   Gate6 compares the Hessian of the SCALAR POTENTIAL, so set xi=0
   (Landau gauge) before evaluating the CP-odd and charged matrices.
   Do not silently set any OTHER unresolved symbol to zero. *)
landauRaw = {massHHRaw,massAhRaw,massHmRaw} /.
  HoldPattern[SARAH`RXi[___]] :> 0;
Print["ZEE_MASS_AUDIT_GAUGE Landau_Rxi_equal_zero"];
actual=N[#/.zeeGate6Rules]& /@ landauRaw;
expected={zeeGate6ExpectedHH,zeeGate6ExpectedAh,zeeGate6ExpectedHm};
labels={"hh","Ah","Hm"};
dims={{2,2},{2,2},{3,3}};

(* Record the actual post-gauge-fixing, post-fixture expressions BEFORE
   any pass/fail check. This is essential for distinguishing a SARAH
   convention issue from a missing fixture substitution. *)
diagPath=FileNameJoin[{logDir,"mass_matrices_substituted.txt"}];
Export[diagPath,StringRiffle[Table[
 labels[[i]]<>":\n"<>ToString[InputForm[actual[[i]]]],
 {i,1,3}], "\n\n"],"Text"];
Do[
 If[MatrixQ[actual[[i]]] && Dimensions[actual[[i]]]===dims[[i]],
  Do[
   If[!NumericQ[actual[[i,irow,j]]],
    Print["ZEE_MASS_NONNUMERIC ",labels[[i]],
      " row=",irow," col=",j,
      " expr=",InputForm[actual[[i,irow,j]]]];
    Print["ZEE_MASS_NONNUMERIC_VARIABLES ",labels[[i]],
      " row=",irow," col=",j,
      " symbols=",InputForm[Variables[actual[[i,irow,j]]]]]
   ],
   {irow,1,dims[[i,1]]},{j,1,dims[[i,2]]}
  ],
  Print["ZEE_MASS_INVALID_DIMENSIONS ",labels[[i]],
    " got=",InputForm[Dimensions[actual[[i]]]]]
 ],
 {i,1,3}
];
If[!And@@Table[
 MatrixQ[actual[[i]],NumericQ] && Dimensions[actual[[i]]]===dims[[i]],
 {i,1,3}],
 Print["FAIL MASS_MATRIX_SHAPE_OR_NUMERIC_EVALUATION ",
 InputForm[Dimensions/@actual]];
 Print["ZEE_MASS_DIAGNOSTICS ",diagPath];
 Print["ZEE_MASS_RAW_FILE ",FileNameJoin[{logDir,"mass_matrices_raw.txt"}]];
 setMassStatus["MASS_MATRIX_SHAPE_OR_SUBSTITUTION_FAILED"];Exit[6]
];
delta=Table[Max[Abs[Flatten[actual[[i]]-expected[[i]]]]],{i,1,3}];
Do[Print["ZEE_MASS_DELTA_GEV2 ",labels[[i]]," ",
 ScientificForm[delta[[i]],8]],{i,1,3}];
neutralGoldstone=Norm[actual[[2]].zeeGate6GoldstoneNeutral,Infinity];
chargedGoldstone=Norm[actual[[3]].zeeGate6GoldstoneCharged,Infinity];
Print["ZEE_MASS_GOLDSTONE_NEUTRAL_GEV2 ",ScientificForm[neutralGoldstone,8]];
Print["ZEE_MASS_GOLDSTONE_CHARGED_GEV2 ",ScientificForm[chargedGoldstone,8]];
Print["ZEE_MASS_HH_EIGEN_GEV ",InputForm[Sort[Sqrt[Eigenvalues[actual[[1]]]]]]];
Print["ZEE_MASS_AH_EIGENVALUES_GEV2 ",InputForm[Sort[Eigenvalues[actual[[2]]]]]];
Print["ZEE_MASS_HM_EIGENVALUES_GEV2 ",InputForm[Sort[Eigenvalues[actual[[3]]]]]];
tol=1.*^-5;
If[Max[Join[delta,{neutralGoldstone,chargedGoldstone}]]<tol,
 setMassStatus["SARAH_GATE6_TREE_MASS_MATRICES_NUMERIC_PASS"],
 setMassStatus["SARAH_GATE6_TREE_MASS_MATRICES_MISMATCH"];
 Print["FAIL inspect ",FileNameJoin[{logDir,"mass_matrices_raw.txt"}]];
 Exit[7]
];
Exit[0];
