(* Numeric cross-check of SARAH charged-Higgs Z/photon vertices.
   REQUIRES scripts/zee_sarah_gate6_fixture.py -- same physical Gate6 benchmark.
   This checks only tree-level gauge vertices; NOT full Zee physics. *)
root=Directory[];
outDir=FileNameJoin[{root,"work","sarah_zee"}];
If[!DirectoryQ[outDir],CreateDirectory[outDir,CreateIntermediateDirectories->True]];
fixture=FileNameJoin[{outDir,"gate6_fixture.m"}];
statusFile=FileNameJoin[{outDir,"z_vertex_numeric_status.txt"}];
setGaugeStatus[zeeGaugeStatus_String]:=(
 Export[statusFile,zeeGaugeStatus<>"\n","Text"];
 Print["ZEE_Z_NUMERIC_STATUS ",zeeGaugeStatus]
);
setGaugeStatus["Z_VERTEX_NUMERIC_NOT_VALIDATED"];
If[!FileExistsQ[fixture],setGaugeStatus["Z_VERTEX_FIXTURE_MISSING"];Exit[2]];
sarahFile=FileNameJoin[{$HomeDirectory,".Mathematica","Applications",
 "SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[sarahFile],setGaugeStatus["Z_VERTEX_SARAH_MISSING"];Exit[3]];
PrependTo[$Path,DirectoryName[sarahFile]];
loaded=CheckAbort[(Get[sarahFile];True),False];
If[!TrueQ[loaded]||!ValueQ[SA`Version],
 setGaugeStatus["Z_VERTEX_SARAH_LOAD_FAILED"];Exit[4]];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],
 FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],
 setGaugeStatus["Z_VERTEX_SARAH_START_FAILED"];Exit[5]];
Get[fixture];

(* Charged 3x3 mixing: rows G-, H1-, H2-;
   columns doublet1, doublet2, charged singlet. *)
If[!NumericQ[zeeGate6Beta]||!NumericQ[zeeGate6Gamma],
 setGaugeStatus["Z_VERTEX_BETA_GAMMA_FIXTURE_MISSING"];Exit[6]];
cb=Cos[zeeGate6Beta];sb=Sin[zeeGate6Beta];
cg=Cos[zeeGate6Gamma];sg=Sin[zeeGate6Gamma];
mix=N[{{cb,sb,0},{-sb*cg,cb*cg,sg},{sb*sg,-cb*sg,cg}}];
matC=N[SARAH`MassMatrix[Hm] /.
 HoldPattern[SARAH`RXi[___]]:>0 /.zeeGate6Rules];
If[!MatrixQ[matC,NumericQ]||Dimensions[matC]=!={3,3},
 Print["FAIL CHARGED_MASS_MATRIX_NONNUMERIC ",InputForm[matC]];
 setGaugeStatus["Z_VERTEX_CHARGED_MATRIX_FAILED"];Exit[7]];
orthResid=Max[Abs[Flatten[mix.Transpose[mix]-IdentityMatrix[3]]]];
diagC=N[mix.matC.Transpose[mix]];
diagResid=Max[Abs[Flatten[diagC-DiagonalMatrix[{0.,90000.,490000.}]]]];
Print["ZEE_Z_ORTHOGONAL_RESID ",InputForm[orthResid]];
Print["ZEE_Z_DIAGONALIZATION_RESID_GEV2 ",InputForm[diagResid]];
If[orthResid>1.*^-10||diagResid>1.*^-5,
 setGaugeStatus["Z_VERTEX_MIXING_MASS_MISMATCH"];Exit[8]];

zpRules=Flatten[Table[ZP[ii,jj]->mix[[ii,jj]],
 {ii,1,3},{jj,1,3}],1];
(* Use exact SM tree-level coupling identity g1=g2 tan(thetaW). *)
g2Value=0.652;sin2w=0.23122;
sw=Sqrt[sin2w];cw=Sqrt[1-sin2w];
g1Value=g2Value*sw/cw;
charge=g2Value*sw;
ewRules={g2->g2Value,g1->g1Value,ThetaW->ArcSin[sw]};
allRules=Join[zpRules,ewRules];
getCoupling[zeeFields_List]:=Module[{vtx,coeff},
 vtx=SARAH`Vertex[zeeFields,Eigenstates->EWSB];
 If[!ListQ[vtx]||Length[vtx]!=2||!ListQ[vtx[[2]]]||
  Length[vtx[[2]]]!=2,
  Print["FAIL VERTEX_STRUCTURE ",InputForm[vtx]];Return[$Failed]];
 coeff=N[vtx[[2,1]]/.allRules];
 If[!NumericQ[coeff],
  Print["FAIL VERTEX_COEFF_NONNUMERIC ",InputForm[coeff]];
  Return[$Failed]];
 Print["ZEE_Z_VERTEX_NUMERIC_FIELDS ",InputForm[zeeFields]];
 Print["ZEE_Z_VERTEX_NUMERIC_COEFF ",InputForm[coeff]];
 Print["ZEE_Z_VERTEX_LORENTZ ",InputForm[vtx[[2,2]]]];
 (* The current SARAH convention has two scalar momenta in a difference.
    Reject a future output that loses this derivative structure. *)
 If[StringCount[ToString[InputForm[vtx[[2,2]]]],"Mom["]!=2 ||
    !StringContainsQ[ToString[InputForm[vtx[[2,2]]]]," - "],
   Print["FAIL VERTEX_MOMENTUM_DIFFERENCE ",InputForm[vtx[[2,2]]]];
   Return[$Failed]];
 coeff
];
cZ23=getCoupling[{conj[Hm[{2}]],Hm[{3}],VZ}];
cZ32=getCoupling[{conj[Hm[{3}]],Hm[{2}],VZ}];
cP23=getCoupling[{conj[Hm[{2}]],Hm[{3}],VP}];
cP22=getCoupling[{conj[Hm[{2}]],Hm[{2}],VP}];
cP33=getCoupling[{conj[Hm[{3}]],Hm[{3}],VP}];
cZ22=getCoupling[{conj[Hm[{2}]],Hm[{2}],VZ}];
cZ33=getCoupling[{conj[Hm[{3}]],Hm[{3}],VZ}];
observed={cZ23,cZ32,cP23,cP22,cP33,cZ22,cZ33};
If[!And@@(NumericQ/@observed),
 setGaugeStatus["Z_VERTEX_EXTRACTION_FAILED"];Exit[9]];

(* Gate6 sign convention: row2=+cos(gamma)*H_D+sin(gamma)*s,
 row3=-sin(gamma)*H_D+cos(gamma)*s.
 For this orientation the all-incoming SARAH coefficient is
 +i*g2*sin(2gamma)/(4cos(thetaW)).
 The photon matrix MUST be diagonal and equal to -i*e. *)
expectedZ23=I*g2Value*Sin[2*zeeGate6Gamma]/(4*cw);
expectedPhotonDiag=-I*charge;
expectedZ22=-I*g2Value/cw*((1-mix[[2,3]]^2)/2-sin2w);
expectedZ33=-I*g2Value/cw*((1-mix[[3,3]]^2)/2-sin2w);
names={"Z23","Z32","Photon23","Photon22","Photon33","Z22","Z33"};
expected={expectedZ23,expectedZ23,0,
 expectedPhotonDiag,expectedPhotonDiag,expectedZ22,expectedZ33};
residuals=N[Abs[observed-expected]];
Do[Print["ZEE_Z_VERTEX_RESID ",names[[i]]," ",
 InputForm[residuals[[i]]]],{i,1,Length[names]}];
Print["ZEE_Z_COEFF_EXPECTED ",InputForm[expectedZ23]];
Print["ZEE_Z_COEFF_ABS ",InputForm[Abs[cZ23]]];
Print["ZEE_Z_GAMMA ",InputForm[zeeGate6Gamma]];
Export[FileNameJoin[{outDir,"z_vertex_numeric_results.txt"}],
 StringRiffle[Table[
 names[[i]]<>": actual="<>ToString[InputForm[observed[[i]]]]<>
 " expected="<>ToString[InputForm[expected[[i]]]]<>
 " residual="<>ToString[InputForm[residuals[[i]]]],
 {i,Length[names]}],"\n"]<>"\n","Text"];
If[!VectorQ[residuals,NumericQ]||Max[residuals]>1.*^-10,
 setGaugeStatus["Z_VERTEX_NUMERIC_COEFFICIENT_MISMATCH"];Exit[10]];
setGaugeStatus["SARAH_GATE6_CHARGED_GAUGE_VERTEX_NUMERIC_PASS"];
Exit[0];
