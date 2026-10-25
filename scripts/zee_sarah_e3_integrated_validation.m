(* ONE INTEGRATED Chen/E3-to-SARAH tree-coupling and loop-kernel check.
   Input: independently generated A1b/B2/B3/Chen fixture.
   Validates f factor 2, Higgs-basis Y factor sqrt(2), complex
   field indices, gauge/physical f amplitudes, both charged states,
   doublet chiral amplitudes, tree mass matrix, B3 included widths,
   and the convention-chosen neutrino log-kernel contraction.
   DOES NOT compute SARAH neutrino self-energy diagrams: the sign and
   factor of the Majorana self-energy remain independent open work.
   No complete E3 309 source or physical model acceptance claimed. *)

zeeRoot=Directory[];
zeeOut=FileNameJoin[{zeeRoot,"work","sarah_zee"}];
If[!DirectoryQ[zeeOut],CreateDirectory[zeeOut,CreateIntermediateDirectories->True]];
zeeStatusFile=FileNameJoin[{zeeOut,"e3_integrated_status.txt"}];
zeeAuditFile=FileNameJoin[{zeeOut,"e3_integrated_residuals.txt"}];
zeeSetStatus[zeeText_String]:=(
 Export[zeeStatusFile,zeeText<>"\n","Text"];
 Print["ZEE_E3_INTEGRATED_STATUS ",zeeText]
);
zeeSetStatus["E3_SARAH_CONVENTION_NOT_VALIDATED"];
zeeFixture=FileNameJoin[{zeeOut,"e3_charged_loop_fixture.m"}];
If[!FileExistsQ[zeeFixture],
 zeeSetStatus["E3_FIXTURE_NOT_FOUND"];Exit[2]];
zeeSfile=FileNameJoin[{$HomeDirectory,".Mathematica","Applications",
 "SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[zeeSfile],
 zeeSetStatus["SARAH_NOT_FOUND"];Exit[3]];
PrependTo[$Path,DirectoryName[zeeSfile]];
zeeLoaded=CheckAbort[(Get[zeeSfile];True),False];
If[!TrueQ[zeeLoaded]||!ValueQ[SA`Version],
 zeeSetStatus["SARAH_LOAD_FAILED"];Exit[4]];
(* Keep all generated native output inside this checkout. *)
SARAH[OutputDirectory]=FileNameJoin[{Directory[],"work","sarah_zee","native_output"}];
If[!DirectoryQ[SARAH[OutputDirectory]],CreateDirectory[SARAH[OutputDirectory],CreateIntermediateDirectories->True]];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],
 FileNameJoin[{zeeRoot,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],
 zeeSetStatus["MODEL_START_FAILED"];Exit[5]];
Get[zeeFixture];
If[!ListQ[zeeE3Cases]||Length[zeeE3Cases]!=2||
   !And@@(AssociationQ/@zeeE3Cases),
 zeeSetStatus["E3_FIXTURE_INVALID"];Exit[6]];
Print["ZEE_E3_SARAH_VERSION ",SA`Version];
Print["ZEE_E3_FIXTURE_STATUS ",zeeE3FixtureStatus];
Print["ZEE_E3_FIXTURE_N_CASES ",Length[zeeE3Cases]];

(* Extract exactly ONE specified chirality; the presence of zero
   co-factors is legitimate, but non-finite expressions are not.
   Two Weyl fermions have Lorentz structure 1, Dirac states PL/PR. *)
zeeCoefficient[zeeFields_List,zeeBasis_,zeeChiral_,zeeRequire_]:=
 Module[{zeeVtx,zeeMatches},
 zeeVtx=CheckAbort[SARAH`Vertex[zeeFields,Eigenstates->zeeBasis],
  $Aborted];
 If[zeeVtx===$Aborted||!ListQ[zeeVtx]||Length[zeeVtx]<2,
  Print["FAIL E3_VERTEX_RETURN ",InputForm[zeeFields]," ",
   InputForm[zeeVtx]];Return[$Failed]];
 zeeMatches=Cases[Rest[zeeVtx],
  {zeeCoeff_,zeeLor_}/;zeeLor===zeeChiral:>zeeCoeff,{1}];
 If[Length[zeeMatches]!=1,
  Print["FAIL E3_VERTEX_CHIRALITY ",InputForm[zeeFields],
    " wanted=",InputForm[zeeChiral],
    " got=",InputForm[zeeVtx]];Return[$Failed]];
 If[zeeRequire=!=None && FreeQ[zeeMatches[[1]],zeeRequire],
  Print["FAIL E3_VERTEX_MISSING_PARAMETER ",InputForm[zeeFields],
   " required=",InputForm[zeeRequire]];
  Return[$Failed]];
 zeeMatches[[1]]
];

(* All indices are frozen with With, avoiding Global a,b,k,n
   assignments that previously corrupted SARAH differentiation. *)
zeeQueries={};
zeeAdd[zeeLabel_String,zeeFields_List,zeeBasis_,zeeChiral_,
       zeeRequire_,zeeKind_String,zeeI_Integer,zeeJ_Integer,
       zeeK_Integer]:=
 AppendTo[zeeQueries,{zeeLabel,zeeFields,zeeBasis,zeeChiral,
   zeeRequire,zeeKind,zeeI,zeeJ,zeeK}];

Do[
 With[{zeeLepton=ii,zeeNeutrino=jj},
  zeeAdd["gauge_"<>ToString[zeeLepton]<>ToString[zeeNeutrino],
   {eL[{zeeLepton}],vL[{zeeNeutrino}],Sp},GaugeES,1,
   If[zeeLepton===zeeNeutrino,None,Fzee],
   "gauge",zeeLepton,zeeNeutrino,0];
  Do[
   With[{zeeCharged=kk},
    zeeAdd["fplus_"<>ToString[zeeLepton]<>ToString[zeeNeutrino]<>
       "_"<>ToString[zeeCharged],
       {Fe[{zeeLepton}],Fv[{zeeNeutrino}],conj[Hm[{zeeCharged}]]},
       EWSB,PL,If[zeeLepton===zeeNeutrino,None,Fzee],
       "fplus",zeeLepton,zeeNeutrino,zeeCharged];
    zeeAdd["fminus_"<>ToString[zeeLepton]<>ToString[zeeNeutrino]<>
       "_"<>ToString[zeeCharged],
       {bar[Fe[{zeeLepton}]],bar[Fv[{zeeNeutrino}]],Hm[{zeeCharged}]},
       EWSB,PR,If[zeeLepton===zeeNeutrino,None,Fzee],
       "fminus",zeeLepton,zeeNeutrino,zeeCharged];
    zeeAdd["Yminus_"<>ToString[zeeLepton]<>ToString[zeeNeutrino]<>
       "_"<>ToString[zeeCharged],
       {bar[Fe[{zeeLepton}]],Fv[{zeeNeutrino}],Hm[{zeeCharged}]},
       EWSB,PL,Ye2,"Yminus",
       zeeLepton,zeeNeutrino,zeeCharged];
    zeeAdd["Yplus_"<>ToString[zeeLepton]<>ToString[zeeNeutrino]<>
       "_"<>ToString[zeeCharged],
       {bar[Fv[{zeeNeutrino}]],Fe[{zeeLepton}],conj[Hm[{zeeCharged}]]},
       EWSB,PR,Ye2,"Yplus",
       zeeLepton,zeeNeutrino,zeeCharged]
   ],{kk,{2,3}}]
 ],{ii,1,3},{jj,1,3}
];
If[Length[zeeQueries]!=81,
 Print["FAIL E3_QUERY_COUNT ",Length[zeeQueries]];
 zeeSetStatus["E3_QUERY_BOOKKEEPING_FAILED"];Exit[7]];
zeeSentinel=SARAH`Vertex[{eL[{1}],vL[{2}],Sp},
 Eigenstates->GaugeES];
If[FreeQ[zeeSentinel,Fzee],
 Print["FAIL E3_FZEE_SENTINEL ",InputForm[zeeSentinel]];
 zeeSetStatus["E3_FZEE_SENTINEL_FAILED"];Exit[8]];
Print["ZEE_E3_QUERY_COUNT ",Length[zeeQueries]];
Print["ZEE_E3_F_SENTINEL_PASS"];

zeeRaw=zeeCoefficient[#[[2]],#[[3]],#[[4]],#[[5]]]&/@zeeQueries;
If[MemberQ[zeeRaw,$Failed],
 zeeSetStatus["E3_VERTEX_EXTRACTION_FAILED"];Exit[9]];
zeeMassRaw=SARAH`MassMatrix[Fe];

zeeEval[zeeExpr_,zeeF_,zeeYe_,zeeYe2_,zeeMix_]:=
 Module[{zeeValue},
 zeeValue=zeeExpr //. HoldPattern[sum[zeeSum_,1,3,zeeTerm_]]:>
   Total[Table[zeeTerm,{zeeSum,1,3}]];
 zeeValue=zeeValue/.{
  Fzee[zeeR_Integer,zeeC_Integer]:>zeeF[[zeeR,zeeC]],
  Ye[zeeR_Integer,zeeC_Integer]:>zeeYe[[zeeR,zeeC]],
  Ye2[zeeR_Integer,zeeC_Integer]:>zeeYe2[[zeeR,zeeC]],
  Ue[zeeR_Integer,zeeC_Integer]:>KroneckerDelta[zeeR,zeeC],
  Ve[zeeR_Integer,zeeC_Integer]:>KroneckerDelta[zeeR,zeeC],
  ZP[zeeR_Integer,zeeC_Integer]:>zeeMix[[zeeR,zeeC]],
  v1->zeeV1,v2->zeeV2
 };
 N[zeeValue/.HoldPattern[conj[zeeZ_?NumericQ]]:>Conjugate[zeeZ]]
];

zeeLog={};zeeMaxVertex=0.;zeeMaxWidth=0.;
zeeMaxNu=0.;zeeMaxFinite=0.;zeeMaxScale=0.;
zeeFailures={};zeeCoeffCount=0;
Do[
 Module[{zeeCase=zeeE3Cases[[zeeCaseIndex]],
    zeeF,zeeFC,zeeYC,zeeYe,zeeYe2,zeeGamma,zeeBeta,
    zeeMix,zeeD,zeeSinglet,zeeWk,zeeV,zeeVs,
    zeeExpected,zeeActual,zeeCoeffKind,zeeIi,zeeJj,zeeKk,
    zeeResidual,zeeCoeffArray,zeeMraw,zeeMdiag,zeeMasses,
    zeeMassDiagResidual,zeeMassHiggsBasisResidual,
    zeeWidth,zeeWidthTarget,zeeWidthErr,
    zeeNuFromVertex,zeeMuScaleNu,zeeNuTarget,zeeLoopErr,
    zeeLoopApprox,zeeFiniteErr,zeeNeutralIndex,
    zeeLeptonIndex,zeePart,zeeScale,zeeCaseMaxVertex},

 zeeF=zeeCase["FSARAH"];zeeFC=zeeCase["FChen"];
 zeeYC=zeeCase["YChen"];zeeYe=zeeCase["YeSARAH"];
 zeeYe2=zeeCase["Ye2SARAH"];
 zeeGamma=zeeCase["Gamma"];zeeBeta=zeeCase["Beta"];
 zeeMasses={zeeCase["M1"],zeeCase["M2"]};
 zeeV=zeeCase["V"];
 zeeV1=zeeV*Cos[zeeBeta];zeeV2=zeeV*Sin[zeeBeta];
 zeeMix=N[{{Cos[zeeBeta],Sin[zeeBeta],0},
  {-Sin[zeeBeta]*Cos[zeeGamma],Cos[zeeBeta]*Cos[zeeGamma],
    Sin[zeeGamma]},
  {Sin[zeeBeta]*Sin[zeeGamma],-Cos[zeeBeta]*Sin[zeeGamma],
    Cos[zeeGamma]}}];
 zeeD=N[-Sin[zeeBeta]*zeeYe+Cos[zeeBeta]*zeeYe2];
 zeeSinglet=N[Cos[zeeBeta]*zeeYe+Sin[zeeBeta]*zeeYe2];
 zeeMassDiagResidual=Max[Abs[Flatten[
   zeeEval[zeeMassRaw,zeeF,zeeYe,zeeYe2,zeeMix]-
   DiagonalMatrix[zeeCase["LeptonMasses"]]]]];
 zeeMassHiggsBasisResidual=Max[Abs[Flatten[
   zeeSinglet-Sqrt[2]*DiagonalMatrix[zeeCase["LeptonMasses"]]/zeeV]]];
 If[Max[{zeeMassDiagResidual,zeeMassHiggsBasisResidual,
         Max[Abs[Flatten[zeeD-Sqrt[2]*zeeYC]]],
         Max[Abs[Flatten[zeeF-2*zeeFC]]]}]>1.*^-10,
  Print["FAIL E3_MASS_OR_HIGGS_BASIS ",
      zeeCase["Label"]];
  AppendTo[zeeFailures,"mass_mapping_"<>zeeCase["Label"]]];

 zeeCaseMaxVertex=0.;
 zeeCoeffArray=Table[
   zeeEval[zeeRaw[[zeeIdx]],zeeF,zeeYe,zeeYe2,zeeMix],
   {zeeIdx,Length[zeeRaw]}];
 If[!VectorQ[zeeCoeffArray,NumericQ],
  Print["FAIL E3_NONNUMERIC ",zeeCase["Label"],
    " ",InputForm[zeeCoeffArray]];
  zeeSetStatus["E3_VERTEX_SUBSTITUTION_FAILED"];Exit[10]];

 (* Coefficients are directly from original field definitions.
    For gauge and singlet vertices the first f index follows the
    charged lepton and the second follows the neutrino; f antisymmetry
    flips that ordering in the neutrino mass matrix contraction. *)
 Do[
  zeeCoeffKind=zeeQueries[[zeeIdx,6]];
  zeeIi=zeeQueries[[zeeIdx,7]];zeeJj=zeeQueries[[zeeIdx,8]];
  zeeKk=zeeQueries[[zeeIdx,9]];
  zeeExpected=Switch[zeeCoeffKind,
   "gauge", I*zeeF[[zeeIi,zeeJj]],
   "fplus", I*zeeMix[[zeeKk,3]]*zeeF[[zeeIi,zeeJj]],
   "fminus", I*zeeMix[[zeeKk,3]]*Conjugate[zeeF[[zeeIi,zeeJj]]],
   "Yminus",-I*(
        zeeMix[[zeeKk,1]]*zeeYe[[zeeIi,zeeJj]]+
        zeeMix[[zeeKk,2]]*zeeYe2[[zeeIi,zeeJj]]),
   "Yplus",-I*(
        zeeMix[[zeeKk,1]]*Conjugate[zeeYe[[zeeIi,zeeJj]]]+
        zeeMix[[zeeKk,2]]*Conjugate[zeeYe2[[zeeIi,zeeJj]]]),
   _, $Failed];
  zeeActual=zeeCoeffArray[[zeeIdx]];
  zeeResidual=N[Abs[zeeActual-zeeExpected]];
  zeeMaxVertex=Max[zeeMaxVertex,zeeResidual];
  zeeCaseMaxVertex=Max[zeeCaseMaxVertex,zeeResidual];
  zeeCoeffCount++;
  AppendTo[zeeLog,{zeeCase["Label"],zeeQueries[[zeeIdx,1]],
       zeeActual,zeeExpected,zeeResidual}];
  If[zeeResidual>1.*^-12,
    AppendTo[zeeFailures,"vertex_"<>zeeCase["Label"]<>"/"<>
      zeeQueries[[zeeIdx,1]]]],
  {zeeIdx,Length[zeeQueries]}];

 (* Reconstruct B3 widths directly from SARAH vertex magnitudes.
    Using massless neutrinos, the f- and Y-origin terms have
    opposite chiralities and no interference. *)
 zeeWidth=Table[
   zeeKk=zeeState;
   zeeWk=zeeMasses[[zeeKk-1]];
   zeeLeptonIndex=zeeEll;
   zeePart=Total[Table[
    zeeIdx=FirstPosition[zeeQueries,
     {_,_,_,_ ,_,"fplus",zeeEll,zeeNu,zeeState}][[1]];
    Abs[zeeCoeffArray[[zeeIdx]]]^2+
    With[{zeePosition=FirstPosition[zeeQueries,
     {_,_,_,_,_,"Yminus",zeeEll,zeeNu,zeeState}][[1]]},
     Abs[zeeCoeffArray[[zeePosition]]]^2],
    {zeeNu,1,3}]];
   N[zeeWk/(16 Pi)*zeePart*
       (1-zeeCase["LeptonMasses"][[zeeEll]]^2/zeeWk^2)^2],
   {zeeEll,1,3},{zeeState,{2,3}}];
 zeeWidthTarget=zeeCase["ExpectedWidths"];
 zeeWidthErr=Max[Abs[Flatten[zeeWidth-zeeWidthTarget]]];
 zeeMaxWidth=Max[zeeMaxWidth,zeeWidthErr];
 If[zeeWidthErr>1.*^-10,
  AppendTo[zeeFailures,"width_"<>zeeCase["Label"]]];

 (* Convention-chosen Majorana self-energy contraction. The sign
    is chosen from f_{ell,nu}=-f_{nu,ell}; it is NOT a derivation from
    a generated SARAH one-loop neutrino self-energy. The factor
    of 1/(16pi^2) is the usual one-loop scalar-fermion integral.
    Cancellation of subtraction-scale dependence is independently
    checked by varying scale. *)
 zeeNuFromVertex[zeeReferenceScale_?NumericQ]:=Module[
  {zeeAmp=ConstantArray[0.+0.I,{3,3}],zeeNuI,zeeNuJ,
   zeeLept,zeeState,zeeF12,zeeY12,zeeF21,zeeY21,
   zeeIdxF,zeeIdxY},
  Do[
   zeeAmp[[zeeNuI,zeeNuJ]] += -(
     zeeCase["LeptonMasses"][[zeeLept]]*1.*^9/(16 Pi^2))*
    Sum[
      zeeIdxF=FirstPosition[zeeQueries,
       {_,_,_,_,_,"fplus",zeeLept,zeeNuI,zeeState}][[1]];
      zeeIdxY=FirstPosition[zeeQueries,
       {_,_,_,_,_,"Yminus",zeeLept,zeeNuJ,zeeState}][[1]];
      zeeF12=zeeCoeffArray[[zeeIdxF]];
      zeeY12=zeeCoeffArray[[zeeIdxY]];
      zeeIdxF=FirstPosition[zeeQueries,
       {_,_,_,_,_,"fplus",zeeLept,zeeNuJ,zeeState}][[1]];
      zeeIdxY=FirstPosition[zeeQueries,
       {_,_,_,_,_,"Yminus",zeeLept,zeeNuI,zeeState}][[1]];
      zeeF21=zeeCoeffArray[[zeeIdxF]];
      zeeY21=zeeCoeffArray[[zeeIdxY]];
      (zeeF12*zeeY12+zeeF21*zeeY21)*
         Log[zeeMasses[[zeeState-1]]^2/zeeReferenceScale^2],
       {zeeState,{2,3}}],
    {zeeNuI,1,3},{zeeNuJ,1,3},{zeeLept,1,3}];
   N[zeeAmp]
 ];
 zeeNuTarget=zeeCase["ChenMnuEV"];
 zeeLoopApprox=zeeNuFromVertex[100.];
 zeeLoopErr=Max[Abs[Flatten[zeeLoopApprox-zeeNuTarget]]];
 zeeMuScaleNu=zeeNuFromVertex[1000.];
 zeeScale=N[Max[Abs[Flatten[zeeMuScaleNu-zeeLoopApprox]]]];
 zeeFiniteErr=Max[Abs[Flatten[
    zeeCase["FiniteMnuEV"]-zeeNuTarget]]];
 zeeMaxNu=Max[zeeMaxNu,zeeLoopErr];
 zeeMaxFinite=Max[zeeMaxFinite,zeeFiniteErr];
 zeeMaxScale=Max[zeeMaxScale,zeeScale];
 Print["ZEE_E3_CASE_RESULT ",zeeCase["Label"],
  " massResidual_GeV=",InputForm[zeeMassDiagResidual],
  " amplitudes=",Length[zeeQueries],
  " vertexResidual=",InputForm[zeeCaseMaxVertex],
  " widthResidual_GeV=",InputForm[zeeWidthErr],
  " mnuFromVerticesResidual_eV=",InputForm[zeeLoopErr],
  " scaleResidual_eV=",InputForm[zeeScale],
  " finiteMassCorrection_eV=",InputForm[zeeFiniteErr]];
 If[zeeLoopErr>1.*^-8,
  AppendTo[zeeFailures,"neutrino_convention_"<>zeeCase["Label"]]];
 If[zeeScale>1.*^-8,
  AppendTo[zeeFailures,"loop_scale_cancel_"<>zeeCase["Label"]]];
 ],
 {zeeCaseIndex,Length[zeeE3Cases]}
];
Export[zeeAuditFile,
 StringRiffle[Table[
 ToString[zeeLog[[zeeIdx,1]]]<>"/"<>
 ToString[zeeLog[[zeeIdx,2]]]<>
 " actual="<>ToString[InputForm[zeeLog[[zeeIdx,3]]]]<>
 " expected="<>ToString[InputForm[zeeLog[[zeeIdx,4]]]]<>
 " absres="<>ToString[InputForm[zeeLog[[zeeIdx,5]]]],
 {zeeIdx,Length[zeeLog]}],"\n"]<>"\n","Text"];
Print["ZEE_E3_VERTEX_COMPARISONS ",zeeCoeffCount];
Print["ZEE_E3_MAX_VERTEX_RESIDUAL ",InputForm[zeeMaxVertex]];
Print["ZEE_E3_MAX_WIDTH_RESIDUAL_GEV ",InputForm[zeeMaxWidth]];
Print["ZEE_E3_MAX_MNU_CONVENTION_RESIDUAL_EV ",InputForm[zeeMaxNu]];
Print["ZEE_E3_MAX_SCALE_RESIDUAL_EV ",InputForm[zeeMaxScale]];
Print["ZEE_E3_MAX_FINITE_LEPTON_MASS_CORRECTION_EV ",InputForm[zeeMaxFinite]];
Print["ZEE_E3_GENERATED_SELFENERGY_CHECKED False"];
Print["ZEE_E3_REAL_309_ARCHIVE_TESTED False"];
Print["ZEE_E3_FAILURE_LABELS ",InputForm[zeeFailures]];
If[Length[zeeFailures]>0||zeeCoeffCount!=162||
    zeeMaxVertex>1.*^-12||zeeMaxWidth>1.*^-10||
    zeeMaxNu>1.*^-8||zeeMaxScale>1.*^-8,
 zeeSetStatus["E3_SARAH_CONVENTION_OR_KERNEL_MISMATCH"];Exit[11]];
zeeSetStatus[
 "E3_SARAH_TREE_CONVENTION_AND_CHEN_KERNEL_CONSISTENT_SELFENERGY_UNVALIDATED"];
Exit[0];
