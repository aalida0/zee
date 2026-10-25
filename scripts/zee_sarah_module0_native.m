(* Independent polynomial differentiation, using exactly the stated Zee
   invariants. No SARAH Lagrangian or mass matrix defines this reference. *)
zeeNRoot=Directory[];
zeeNOut=FileNameJoin[{zeeNRoot,"work","sarah_zee"}];
zeeNReport={}; zeeNFailures={};
zeeNStatus[ss_]:=Export[FileNameJoin[{zeeNOut,"module0_native_status.txt"}],ss<>"\n","Text"];
zeeNStatus["INDEPENDENT_NATIVE_NOT_VALIDATED"];
Get[FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH","SARAH.m"}]];
SARAH[OutputDirectory]=FileNameJoin[{zeeNOut,"native_output"}];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],FileNameJoin[{zeeNRoot,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],zeeNStatus["START_FAILED"];Exit[2]];
Get[FileNameJoin[{zeeNOut,"gate6_fixture.m"}]];

zeeNX1=zeeNcm1*zeeNcp1+((v1+zeeNh1)^2+zeeNa1^2)/2;
zeeNX2=zeeNcm2*zeeNcp2+((v2+zeeNh2)^2+zeeNa2^2)/2;
zeeNZ12=zeeNcm1*zeeNcp2+(v1+zeeNh1-I*zeeNa1)*(v2+zeeNh2+I*zeeNa2)/2;
zeeNZ21=zeeNcm2*zeeNcp1+(v2+zeeNh2-I*zeeNa2)*(v1+zeeNh1+I*zeeNa1)/2;
zeeNS=zeeNsm*zeeNsp;
zeeNV=M112*zeeNX1+M222*zeeNX2-M12Sq*(zeeNZ12+zeeNZ21)+MCS2*zeeNS+
 Lambda1/2*zeeNX1^2+Lambda2/2*zeeNX2^2+Lambda3*zeeNX1*zeeNX2+
 Lambda4*zeeNZ12*zeeNZ21+Lambda5/2*(zeeNZ12^2+zeeNZ21^2)+
 LambdaC*zeeNS^2+K1*zeeNS*zeeNX1+K2*zeeNS*zeeNX2-K12*zeeNS*(zeeNZ12+zeeNZ21)+
 Mu4/Sqrt[2]*(zeeNsm*(zeeNcp1*(v2+zeeNh2+I*zeeNa2)-(v1+zeeNh1+I*zeeNa1)*zeeNcp2)+
 zeeNsp*(zeeNcm1*(v2+zeeNh2-I*zeeNa2)-(v1+zeeNh1-I*zeeNa1)*zeeNcm2));
zeeNGaugeVars={zeeNh1,zeeNh2,zeeNa1,zeeNa2,zeeNcm1,zeeNcm2,zeeNsm,zeeNcp1,zeeNcp2,zeeNsp};
zeeNZero=Thread[zeeNGaugeVars->0];
zeeNHessian[rows_,cols_]:=Table[D[zeeNV,xx,yy]/.zeeNZero,{xx,rows},{yy,cols}];
zeeNIndependent={zeeNHessian[{zeeNh1,zeeNh2},{zeeNh1,zeeNh2}],
 zeeNHessian[{zeeNa1,zeeNa2},{zeeNa1,zeeNa2}],
 zeeNHessian[{zeeNcm1,zeeNcm2,zeeNsm},{zeeNcp1,zeeNcp2,zeeNsp}]};
zeeNActual={SARAH`MassMatrix[hh],SARAH`MassMatrix[Ah],SARAH`MassMatrix[Hm]}/.
 HoldPattern[SARAH`RXi[___]]:>0;
zeeNRecord[label_,actual_,expected_,tol_]:=Module[{res},
 res=If[And@@(NumericQ/@Flatten[{actual,expected}]),Max[Abs[Flatten[{actual-expected}]]],1.*^300];
 AppendTo[zeeNReport,<|"label"->label,"actual"->ToString[InputForm[actual]],
 "expected"->ToString[InputForm[expected]],"residual"->res,"tolerance"->tol|>];
 If[!TrueQ[res<tol],AppendTo[zeeNFailures,label];Print["FAIL ",label," ",InputForm[res]]];res];
(* An unrelated Lagrangian point, with tadpole masses solved independently. *)
zeeNSecond={v1->180.,v2->168.,M12Sq->40000.,MCS2->220000.,Mu4->45.,
 Lambda1->.6,Lambda2->.7,Lambda3->.4,Lambda4->-.12,Lambda5->.05,
 LambdaC->.8,K1->.3,K2->.2,K12->-.04};
zeeNTadMasses=First[Solve[Thread[({D[zeeNV,zeeNh1],D[zeeNV,zeeNh2]}/.zeeNZero)=={0,0}],{M112,M222}]];
zeeNSecond=Join[N[zeeNTadMasses/.zeeNSecond],zeeNSecond];
zeeNCases={zeeGate6Rules,zeeNSecond};
(* Mixing at the second point is obtained from the independent Hessians;
   eigenvector signs are preserved in both the potential and SARAH input. *)
zeeNPhysVars=Array[zeeNx,10];
zeeNFields={hh[{1}],hh[{2}],Ah[{1}],Ah[{2}],Hm[{1}],Hm[{2}],Hm[{3}],
 conj[Hm[{1}]],conj[Hm[{2}]],conj[Hm[{3}]]};
zeeNCharges={0,0,0,0,-1,-1,-1,1,1,1};
zeeNTuples[order_]:=Select[DeleteDuplicates[Sort/@Tuples[Range[10],order]],Total[zeeNCharges[[#]]]===0&];
zeeNQueries=Join[zeeNTuples[3],zeeNTuples[4]];
zeeNVertices=Table[Module[{vv,cc},
 vv=SARAH`Vertex[zeeNFields[[tt]],Eigenstates->EWSB];
 cc=If[vv===0,0,If[ListQ[vv]&&Length[vv]===2&&vv[[2,2]]===1,vv[[2,1]],$Failed]];
 cc],{tt,zeeNQueries}];
Print["MODULE0_SCALAR_VERTICES ",Length[zeeNQueries]];
Do[
 zeeNR=zeeNCases[[caseidx]];
 zeeNMat=N[zeeNIndependent/.zeeNR];
 Do[zeeNRecord["hessian_"<>ToString[caseidx]<>"_"<>ToString[sector],
 N[zeeNActual[[sector]]/.zeeNR],zeeNMat[[sector]],1.*^-7],{sector,3}];
 zeeNZH=Eigenvectors[zeeNMat[[1]]];
 zeeNB=ArcTan[(v1/.zeeNR),(v2/.zeeNR)];
 zeeNZA={{Cos[zeeNB],Sin[zeeNB]},{-Sin[zeeNB],Cos[zeeNB]}};
 zeeNZP=Reverse[Eigenvectors[zeeNMat[[3]]]];
 zeeNRecord["goldstone_neutral_"<>ToString[caseidx],zeeNMat[[2]].zeeNZA[[1]],{0,0},1.*^-7];
 zeeNRecord["goldstone_charged_"<>ToString[caseidx],zeeNMat[[3]].Append[zeeNZA[[1]],0],{0,0,0},1.*^-7];
 zeeNRecord["charged_mix_"<>ToString[caseidx],zeeNZP.zeeNMat[[3]].Transpose[zeeNZP],
 DiagonalMatrix[Sort[Eigenvalues[zeeNMat[[3]]]]],1.*^-7];
 zeeNRot=Join[Thread[{zeeNh1,zeeNh2}->Transpose[zeeNZH].zeeNPhysVars[[1;;2]]],
 Thread[{zeeNa1,zeeNa2}->Transpose[zeeNZA].zeeNPhysVars[[3;;4]]],
 Thread[{zeeNcm1,zeeNcm2,zeeNsm}->Transpose[zeeNZP].zeeNPhysVars[[5;;7]]],
 Thread[{zeeNcp1,zeeNcp2,zeeNsp}->Transpose[zeeNZP].zeeNPhysVars[[8;;10]]]];
 zeeNMixRules=Join[Flatten[Table[ZH[ii,jj]->zeeNZH[[ii,jj]],{ii,2},{jj,2}]],
 Flatten[Table[ZA[ii,jj]->zeeNZA[[ii,jj]],{ii,2},{jj,2}]],
 Flatten[Table[ZP[ii,jj]->zeeNZP[[ii,jj]],{ii,3},{jj,3}]]];
 zeeNPoly=Expand[(zeeNV/.zeeNR)/.zeeNRot];
 Do[
 zeeNExpected=-I*Fold[D[#1,#2]&,zeeNPoly,zeeNPhysVars[[zeeNQueries[[queryidx]]]]]/.
 Thread[zeeNPhysVars->0];
 zeeNRecord["scalar_"<>ToString[caseidx]<>"_"<>ToString[zeeNQueries[[queryidx]],InputForm],
 N[zeeNVertices[[queryidx]]/.Join[zeeNMixRules,zeeNR]],N[zeeNExpected],1.*^-7],
 {queryidx,Length[zeeNQueries]}];
 Print["MODULE0_INDEPENDENT_SCALAR_CASE_DONE ",caseidx],
 {caseidx,Length[zeeNCases]}];
(* Retain raw W and Type-II quark chiral/momentum structures for the
   independently derived current comparisons. *)
zeeNCurrentFields={
 {hh[{1}],Hm[{2}],conj[VWm]}, {Ah[{2}],Hm[{2}],conj[VWm]},
 {bar[Fu[{3}]],Fd[{3}],conj[Hm[{2}]]},
 {bar[Fd[{3}]],Fu[{3}],Hm[{2}]}};
zeeNCurrentRaw=SARAH`Vertex[#,Eigenstates->EWSB]&/@zeeNCurrentFields;
Export[FileNameJoin[{zeeNOut,"module0_currents_raw.m"}],zeeNCurrentRaw,"Package"];
(* The covariant derivative convention is fixed by the photon rule
   -i e (p_plus-p_minus). Expansion of |D H|^2 then gives
   W+ h H-: -i g/2 (p_h-p_H-), W+ A H-: +g/2 (p_A-p_H-).
   The charged singlet contributes zero to these SU(2) currents. *)
zeeNRot12[ang_,phase_]:={{Cos[ang],Exp[I*phase]*Sin[ang],0},
 {-Exp[-I*phase]*Sin[ang],Cos[ang],0},{0,0,1}};
zeeNRot23[ang_,phase_]:={{1,0,0},{0,Cos[ang],Exp[I*phase]*Sin[ang]},
 {0,-Exp[-I*phase]*Sin[ang],Cos[ang]}};
zeeNVu=zeeNRot12[.37,.61].zeeNRot23[.24,-.45];
zeeNVd=zeeNRot12[-.21,-.72].zeeNRot23[.13,.39];
zeeNUu=zeeNRot12[.17,-.25].zeeNRot23[-.11,.58];
zeeNUd=zeeNRot12[-.31,.17].zeeNRot23[.22,.81];
zeeNCKM=zeeNVu.ConjugateTranspose[zeeNVd];
zeeNUpMass={.0022,1.27,172.};zeeNDownMass={.0047,.095,4.7};
zeeNEvaluateCurrent[expr_,rules_]:=Module[{val},
 val=expr//.HoldPattern[sum[ind_,lo_Integer,hi_Integer,body_]]:>Total[Table[body,{ind,lo,hi}]];
 val=val/.rules;
 N[val/.HoldPattern[conj[num_?NumericQ]]:>Conjugate[num]]];
Do[
 zeeNR=zeeNCases[[caseidx]];
 zeeNMat=N[zeeNIndependent/.zeeNR];
 zeeNZH=Eigenvectors[zeeNMat[[1]]];zeeNZP=Reverse[Eigenvectors[zeeNMat[[3]]]];
 zeeNB=ArcTan[(v1/.zeeNR),(v2/.zeeNR)];
 zeeNZA={{Cos[zeeNB],Sin[zeeNB]},{-Sin[zeeNB],Cos[zeeNB]}};
 zeeNMixRules=Join[Flatten[Table[ZH[ii,jj]->zeeNZH[[ii,jj]],{ii,2},{jj,2}]],
 Flatten[Table[ZA[ii,jj]->zeeNZA[[ii,jj]],{ii,2},{jj,2}]],
 Flatten[Table[ZP[ii,jj]->zeeNZP[[ii,jj]],{ii,3},{jj,3}]],{g2->.652}];
 Do[
  zeeNF=If[neutraltype===1,hh[{nn}],Ah[{nn}]];
  zeeNCharged=If[orientation===1,Hm[{kk}],conj[Hm[{kk}]]];
  zeeNW=If[orientation===1,conj[VWm],VWm];
  zeeNVtx=SARAH`Vertex[{zeeNF,zeeNCharged,zeeNW},Eigenstates->EWSB];
  zeeNExpected=If[neutraltype===1,If[orientation===1,-I,I],1]*.652/2*
    (If[neutraltype===1,zeeNZH,zeeNZA][[nn]].zeeNZP[[kk,1;;2]]);
  (* Vertex canonicalizes the field order. For h H+ W- it returns
     H+ before h, reversing the momentum difference and its coefficient.
     Project the RETURNED Lorentz tensor onto the REQUESTED difference;
     never infer a sign from numerical coefficient agreement. *)
  zeeNMomentumFactor=zeeNVtx[[2,2]]/.
    {Mom[zeeNF,lt3]->1,Mom[zeeNCharged,lt3]->0};
  zeeNRecord["W_"<>ToString[{caseidx,neutraltype,nn,kk,orientation},InputForm],
   N[zeeNMomentumFactor*zeeNVtx[[2,1]]/.zeeNMixRules],zeeNExpected,1.*^-12];
  If[Expand[zeeNVtx[[2,2]]-zeeNMomentumFactor*(Mom[zeeNF,lt3]-Mom[zeeNCharged,lt3])]=!=0,
   AppendTo[zeeNFailures,"W_momentum_orientation"]],
 {neutraltype,2},{nn,2},{kk,{2,3}},{orientation,2}];
 zeeNYu=Sqrt[2]/(v2/.zeeNR)*Transpose[zeeNUu].DiagonalMatrix[zeeNUpMass].zeeNVu;
 zeeNYd=Sqrt[2]/(v1/.zeeNR)*Transpose[zeeNUd].DiagonalMatrix[zeeNDownMass].zeeNVd;
 zeeNQRules=Join[zeeNMixRules,{
  HoldPattern[Yu[row_Integer,col_Integer]]:>zeeNYu[[row,col]],
  HoldPattern[Yd[row_Integer,col_Integer]]:>zeeNYd[[row,col]],
  HoldPattern[Vu[row_Integer,col_Integer]]:>zeeNVu[[row,col]],
  HoldPattern[Vd[row_Integer,col_Integer]]:>zeeNVd[[row,col]],
  HoldPattern[Uu[row_Integer,col_Integer]]:>zeeNUu[[row,col]],
  HoldPattern[Ud[row_Integer,col_Integer]]:>zeeNUd[[row,col]],Delta[ct1,ct2]->1}];
 zeeNRecord["up_mass_closure_"<>ToString[caseidx],
 (v2/.zeeNR)/Sqrt[2]*(Conjugate[zeeNVu].Transpose[zeeNYu].ConjugateTranspose[zeeNUu]),
 DiagonalMatrix[zeeNUpMass],1.*^-10];
 zeeNRecord["down_mass_closure_"<>ToString[caseidx],
 (v1/.zeeNR)/Sqrt[2]*(Conjugate[zeeNVd].Transpose[zeeNYd].ConjugateTranspose[zeeNUd]),
 DiagonalMatrix[zeeNDownMass],1.*^-10];
 Do[
  zeeNVtx=SARAH`Vertex[{bar[Fu[{uu}]],Fd[{dd}],conj[Hm[{kk}]]},Eigenstates->EWSB];
  zeeNExpected={I*Sqrt[2]*zeeNUpMass[[uu]]/(v2/.zeeNR)*zeeNCKM[[uu,dd]]*zeeNZP[[kk,2]],
  -I*Sqrt[2]*zeeNDownMass[[dd]]/(v1/.zeeNR)*zeeNCKM[[uu,dd]]*zeeNZP[[kk,1]]};
  Do[zeeNChir=If[chir===1,PL,PR];
   zeeNObs=Cases[Rest[zeeNVtx],{coeff_,lor_}/;lor===zeeNChir:>coeff];
   zeeNRecord["TypeII_Hplus_"<>ToString[{caseidx,uu,dd,kk,chir},InputForm],
    zeeNEvaluateCurrent[First[zeeNObs],zeeNQRules],zeeNExpected[[chir]],1.*^-12],{chir,2}];
  zeeNVtx=SARAH`Vertex[{bar[Fd[{dd}]],Fu[{uu}],Hm[{kk}]},Eigenstates->EWSB];
  zeeNExpected={-I*Sqrt[2]*zeeNDownMass[[dd]]/(v1/.zeeNR)*Conjugate[zeeNCKM[[uu,dd]]]*zeeNZP[[kk,1]],
   I*Sqrt[2]*zeeNUpMass[[uu]]/(v2/.zeeNR)*Conjugate[zeeNCKM[[uu,dd]]]*zeeNZP[[kk,2]]};
  Do[zeeNChir=If[chir===1,PL,PR];
   zeeNObs=Cases[Rest[zeeNVtx],{coeff_,lor_}/;lor===zeeNChir:>coeff];
   zeeNRecord["TypeII_Hminus_"<>ToString[{caseidx,uu,dd,kk,chir},InputForm],
    zeeNEvaluateCurrent[First[zeeNObs],zeeNQRules],zeeNExpected[[chir]],1.*^-12],{chir,2}],
 {uu,3},{dd,3},{kk,{2,3}}],{caseidx,Length[zeeNCases]}];
Export[FileNameJoin[{zeeNOut,"module0_native_inputs.m"}],zeeNCases,"Package"];
Export[FileNameJoin[{zeeNOut,"module0_quark_inputs.m"}],
 {zeeNUpMass,zeeNDownMass,zeeNVu,zeeNVd,zeeNUu,zeeNUd},"Package"];
Export[FileNameJoin[{zeeNOut,"module0_native_report.json"}],zeeNReport,"RawJSON"];
Print["MODULE0_INDEPENDENT_FAILURES ",InputForm[zeeNFailures]];
If[Length[zeeNFailures]>0,zeeNStatus["INDEPENDENT_SCALAR_MISMATCH"];Exit[3]];
zeeNStatus["INDEPENDENT_SCALARS_W_AND_COMPLEX_TYPEII_QUARK_VERTICES_PASS"];
Exit[0];
