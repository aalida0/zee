(* Controlled A/B diagnostic with a temporarily MAJORANA-packaged Fv field.
   Production ZeeTypeII Lagrangian is NEVER modified.
   This tests whether SARAH can represent the LNV self energy with
   Fv -> {vL,conj[vL]} instead of Fv -> {vL,0}.
   A generated SigmaS is not independently validated Mnu. *)
zeeABRoot=Directory[];
zeeABDir=FileNameJoin[{zeeABRoot,"work","sarah_zee"}];
zeeABStatus=FileNameJoin[{zeeABDir,"e3_majorana_ab_status.txt"}];
zeeABExport=FileNameJoin[{zeeABDir,"e3_majorana_ab_sigma.txt"}];
zeeABSetStatus[zeeValue_String]:=(
 Export[zeeABStatus,zeeValue<>"\n","Text"];
 Print["ZEE_E3_MAJORANA_AB_STATUS ",zeeValue]
);
zeeABSetStatus["MAJORANA_AB_NOT_VALIDATED"];
zeeABName="ZeeTypeIIMajoranaAudit";
zeeABParent=FileNameJoin[{zeeABDir,"sarah_model_variants"}];
zeeABModel=FileNameJoin[{zeeABParent,zeeABName,zeeABName<>".m"}];
If[!FileExistsQ[zeeABModel],
 zeeABSetStatus["MAJORANA_AB_VARIANT_MODEL_MISSING"];Exit[2]];
zeeABManifest=FileNameJoin[{zeeABDir,
 "e3_majorana_variant_manifest.json"}];
If[!FileExistsQ[zeeABManifest],
 zeeABSetStatus["MAJORANA_AB_MANIFEST_MISSING"];Exit[3]];
zeeABManifestObj=Import[zeeABManifest,"RawJSON"];
If[!AssociationQ[zeeABManifestObj]||
   !TrueQ[zeeABManifestObj["production_untouched"]]||
   !TrueQ[zeeABManifestObj["no_majorana_mass_added"]],
 zeeABSetStatus["MAJORANA_AB_MANIFEST_UNVERIFIED"];Exit[4]];
zeeABEarlierFile=FileNameJoin[{zeeABDir,
 "e3_sarah_selfenergy_status.txt"}];
If[!FileExistsQ[zeeABEarlierFile] ||
 StringTrim[Import[zeeABEarlierFile,"Text"]]=!=
  "SARAH_FV_SIGMAS_FE_HM_B0_EXTRACTED_MAJORANA_AMPLITUDE_UNVALIDATED",
 zeeABSetStatus["MAJORANA_AB_BASELINE_SIGMAS_NOT_VALIDATED"];Exit[5]];

zeeABPackage=FileNameJoin[{$HomeDirectory,".Mathematica",
 "Applications","SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[zeeABPackage],
 zeeABSetStatus["MAJORANA_AB_SARAH_NOT_FOUND"];Exit[6]];
PrependTo[$Path,DirectoryName[zeeABPackage]];
zeeABLoaded=CheckAbort[(Get[zeeABPackage];True),False];
If[!TrueQ[zeeABLoaded]||!ValueQ[SA`Version],
 zeeABSetStatus["MAJORANA_AB_SARAH_LOAD_FAILED"];Exit[7]];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],zeeABParent];
SARAH`Start[zeeABName];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],
 zeeABSetStatus["MAJORANA_AB_SARAH_START_FAILED"];Exit[8]];

zeeABDiracSpinors=DEFINITION[EWSB][DiracSpinors];
zeeABSpinorExpected=MemberQ[zeeABDiracSpinors,Fv->{vL,conj[vL]}];
zeeABClassified=MemberQ[MajoranaPart,Fv];
zeeABSelfConjugate=(AntiField[Fv]===Fv);
Print["ZEE_E3_MAJORANA_AB_SPINOR_DEFINITION_EXPECTED ",
 zeeABSpinorExpected];
Print["ZEE_E3_MAJORANA_AB_LISTED_AS_MAJORANA ",zeeABClassified];
Print["ZEE_E3_MAJORANA_AB_ANTIFIELD_SELF_CONJUGATE ",
 zeeABSelfConjugate];
If[!And@@{zeeABSpinorExpected,zeeABClassified,zeeABSelfConjugate},
 zeeABSetStatus["MAJORANA_AB_NEUTRINO_SPINOR_CLASSIFICATION_FAILED"];
 Exit[9]];

(* Gauge-basis Weyl vertex is unchanged by four-component packaging. *)
zeeABFsentinel=SARAH`Vertex[{eL[{1}],vL[{2}],Sp},
 Eigenstates->GaugeES];
If[FreeQ[zeeABFsentinel,Fzee],
 zeeABSetStatus["MAJORANA_AB_GAUGE_WEYL_F_VERTEX_MISSING"];Exit[10]];
Print["ZEE_E3_MAJORANA_AB_FZEE_GAUGE_VERTEX_PRESENT True"];

Print["ZEE_E3_MAJORANA_AB_LOOP_SOURCE SARAH_COMPUTED"];
If[DownValues[SARAH`CalcLoopCorrections]==={},
 zeeABSetStatus["MAJORANA_AB_SARAH_LOOP_API_MISSING"];Exit[11]];
zeeABLoopSucceeded=CheckAbort[
 (SARAH`CalcLoopCorrections[EWSB];True),False];
If[!TrueQ[zeeABLoopSucceeded],
 zeeABSetStatus["MAJORANA_AB_LOOP_ABORTED"];Exit[12]];

zeeABSummed=SARAH`SelfEnergy1LoopSum[EWSB];
zeeABLabels=SARAH`ParticlesSelfEnergy1LoopSum[EWSB];
zeeABDiagrams=SARAH`SelfEnergy1LoopList[EWSB];
If[!And@@(ListQ/@{zeeABSummed,zeeABLabels,zeeABDiagrams}) ||
 Length[zeeABSummed]=!=Length[zeeABLabels] ||
 Length[zeeABDiagrams]=!=Length[zeeABLabels],
 Print["FAIL MAJORANA_AB_LOOP_LABEL_ALIGNMENT"];
 zeeABSetStatus["MAJORANA_AB_LOOP_LABEL_ALIGNMENT_FAILED"];Exit[13]];
zeeABNuIndex=Flatten[Position[zeeABLabels,Fv,{1},Heads->False]];
If[Length[zeeABNuIndex]!=1,
 Print["ZEE_E3_MAJORANA_AB_NEUTRINO_LABEL_INDICES ",
 InputForm[zeeABNuIndex]];
 zeeABSetStatus["MAJORANA_AB_FV_EXTERNAL_LABEL_NOT_UNIQUE"];
 Exit[14]];
zeeABNuIndex=First[zeeABNuIndex];
zeeABFormFactors=zeeABSummed[[zeeABNuIndex]];
If[!ListQ[zeeABFormFactors] ||
 Length[zeeABFormFactors]!=3,
 Print["ZEE_E3_MAJORANA_AB_FV_SUM_SHAPE ",
 InputForm[Dimensions[zeeABFormFactors]]];
 zeeABSetStatus["MAJORANA_AB_FV_FORM_FACTOR_SHAPE_UNKNOWN"];
 Exit[15]];
zeeABS=zeeABFormFactors[[1]];
zeeABR=zeeABFormFactors[[2]];
zeeABL=zeeABFormFactors[[3]];
zeeABMassScalarB0=!FreeQ[zeeABS,B0[___]];
zeeABMassScalarFe=!FreeQ[zeeABS,Mass[Fe[___]]];
zeeABMassScalarHm=!FreeQ[zeeABS,Hm[___]] ||
 !FreeQ[zeeABDiagrams[[zeeABNuIndex]],Hm[___]];
zeeABMassScalarCps=!FreeQ[zeeABS,Cp[___]];
Print["ZEE_E3_MAJORANA_AB_NEUTRINO_EXTERNAL ",InputForm[Fv]];
Print["ZEE_E3_MAJORANA_AB_SIGMAS_DIMENSIONS ",
 InputForm[Dimensions[zeeABFormFactors]]];
Print["ZEE_E3_MAJORANA_AB_SIGMAS_B0 ",zeeABMassScalarB0];
Print["ZEE_E3_MAJORANA_AB_SIGMAS_MASS_FE ",zeeABMassScalarFe];
Print["ZEE_E3_MAJORANA_AB_SIGMAS_CHARGED_HIGGS ",zeeABMassScalarHm];
Print["ZEE_E3_MAJORANA_AB_SIGMAS_COUPLINGS ",zeeABMassScalarCps];

(* An actual independent loop calculation must retain its original
   diagrammatic coupling factors. Capture EVERY chirality-labeled Cp
   vertex in SigmaS before performing any guessed contractions.
   SARAH's loopCorrections.m AddLoopFermion inserts products of
   Cp[..][PR] and conjugates of Cp[..][PL]. Tree-level vertex
   structure changes when Fv is repackaged as self-conjugate. *)
zeeABCouplingAtoms=DeleteDuplicates[
 Cases[zeeABS,HoldPattern[(Cp[___])[PL|PR]],Infinity]];
zeeABCouplingInventoryFile=FileNameJoin[{zeeABDir,
 "e3_majorana_ab_sigma_couplings.txt"}];
zeeABSigmaMachineFile=FileNameJoin[{zeeABDir,
 "e3_majorana_ab_sigma_machine.m"}];
Print["ZEE_E3_MAJORANA_AB_SIGMAS_CP_ATOMS ",
 Length[zeeABCouplingAtoms]];
Print["ZEE_E3_MAJORANA_AB_SIGMAS_EXPLICIT_F_AND_Y ",
 (!FreeQ[zeeABS,Fzee] && !FreeQ[zeeABS,Ye2])];
Put[zeeABS,zeeABSigmaMachineFile];
Export[zeeABCouplingInventoryFile,
 StringRiffle[
  Join[{"Independent SARAH SigmaS coupling-factor inventory",
    "These are Cp operators from SARAH, not yet matched to Zee f/Y."},
    (ToString[InputForm[#]]&/@zeeABCouplingAtoms)
  ],"\n"]<>"\n","Text"];
Print["ZEE_E3_MAJORANA_AB_SIGMA_COUPLING_INVENTORY ",
 zeeABCouplingInventoryFile];
Print["ZEE_E3_MAJORANA_AB_SIGMA_MACHINE_EXPRESSION ",
 zeeABSigmaMachineFile];

(* Compare the two PHYSICAL charged-lepton/Higgs field orientations
   directly in the Majorana variant. This prevents the original
   spinor representation's 162/162 PASS from being misapplied to
   the Majorana representation after its FFS topology count changes.
   Do not REQUIRE the Dirac and Majorana vertex field ordering
   to look identical; inventory all amplitudes for a later complete
   complex amplitude-level conversion. *)
zeeABTreeProbeFields={
 {"f_plus_12_H1",{Fe[{1}],Fv[{2}],conj[Hm[{2}]]}},
 {"f_plus_12_H2",{Fe[{1}],Fv[{2}],conj[Hm[{3}]]}},
 {"f_reverse_12_H1",{Fv[{2}],Fe[{1}],conj[Hm[{2}]]}},
 {"Y_minus_12_H1",{bar[Fe[{1}]],Fv[{2}],Hm[{2}]}},
 {"Y_minus_12_H2",{bar[Fe[{1}]],Fv[{2}],Hm[{3}]}},
 {"Y_plus_12_H1",{bar[Fv[{2}]],Fe[{1}],conj[Hm[{2}]]}},
 {"f_hc_12_H1",{bar[Fe[{1}]],bar[Fv[{2}]],Hm[{2}]}}
};
zeeABTreeProbeResults=Table[
 {zeeABTreeProbeFields[[zeeABIdx,1]],
  CheckAbort[
   SARAH`Vertex[zeeABTreeProbeFields[[zeeABIdx,2]],
    Eigenstates->EWSB],$Aborted]},
 {zeeABIdx,Length[zeeABTreeProbeFields]}];
zeeABTreeProbeFile=FileNameJoin[{zeeABDir,
 "e3_majorana_ab_physical_vertices.txt"}];
Export[zeeABTreeProbeFile,StringRiffle[
 Table[
 ToString[zeeABTreeProbeResults[[zeeABIdx,1]]]<>
 " HAS_FZEE="<>ToString[
  !FreeQ[zeeABTreeProbeResults[[zeeABIdx,2]],Fzee]]<>
 " HAS_YE2="<>ToString[
  !FreeQ[zeeABTreeProbeResults[[zeeABIdx,2]],Ye2]]<>
 " EXPR="<>ToString[
  InputForm[zeeABTreeProbeResults[[zeeABIdx,2]]]],
 {zeeABIdx,Length[zeeABTreeProbeResults]}],
 "\n\n"]<>"\n","Text"];
Print["ZEE_E3_MAJORANA_AB_TREE_F_VERTEX_COUNT ",
 Count[zeeABTreeProbeResults,
  {_,zeeTerm_}/;!FreeQ[zeeTerm,Fzee]]];
Print["ZEE_E3_MAJORANA_AB_TREE_Y_VERTEX_COUNT ",
 Count[zeeABTreeProbeResults,
  {_,zeeTerm_}/;!FreeQ[zeeTerm,Ye2]]];
Print["ZEE_E3_MAJORANA_AB_TREE_VERTEX_INVENTORY ",
 zeeABTreeProbeFile];
Print["ZEE_E3_MAJORANA_AB_TREE_E3_AMPLITUDE_MATCH_VERIFIED False"];


(* A radiative Majorana mass is generated with zero TREE neutrino
   mass. Inspect whether the scalar form factor vanishes after setting
   only explicit Fv masses to zero. This is a syntactic check and does
   not by itself identify an LNV two-point function. *)
zeeABNuMassZeroSigmaS=zeeABS/.{
  HoldPattern[Mass[Fv[___]]]:>0,
  HoldPattern[Mass[Fv]]:>0,
  HoldPattern[Mass2[Fv[___]]]:>0,
  HoldPattern[Mass2[Fv]]:>0
};
zeeABNuMassZeroSigmaIsZero=(zeeABNuMassZeroSigmaS===0);
Print["ZEE_E3_MAJORANA_AB_SIGMAS_TREE_MNU_ZERO_IDENTICALLY_ZERO ",
 zeeABNuMassZeroSigmaIsZero];
Print["ZEE_E3_MAJORANA_AB_SIGMAS_TREE_MNU_ZERO_MASS_SYMBOL_REMAINING ",
 !FreeQ[zeeABNuMassZeroSigmaS,Mass[Fv[___]]]];

Print["ZEE_E3_MAJORANA_AB_COMPLEX_MNU_MATRIX_EXTRACTED False"];
Print["ZEE_E3_MAJORANA_AB_CHEN_E3_NUMERIC_MATCH False"];
Print["ZEE_E3_MAJORANA_AB_CP_EXPANSION_TO_FLAVOR_COUPLINGS_VERIFIED False"];
Export[zeeABExport,StringRiffle[{
 "SARAH-GENERATED MAJORANA-PACKAGED Fv FORM FACTORS",
 "Not a physical one-loop Majorana mass certificate.",
 "Spinor variant: "<>zeeABName,
 "Fv classified Majorana: "<>ToString[zeeABClassified],
 "SigmaS:\\n"<>ToString[InputForm[zeeABS]],
 "SigmaS_tree_mnu_zero:\\n"<>ToString[InputForm[zeeABNuMassZeroSigmaS]],
 "SigmaR:\\n"<>ToString[InputForm[zeeABR]],
 "SigmaL:\\n"<>ToString[InputForm[zeeABL]],
 "Diagrams:\\n"<>ToString[InputForm[zeeABDiagrams[[zeeABNuIndex]]]]
 },"\n\n"]<>"\n","Text"];
Print["ZEE_E3_MAJORANA_AB_SIGMA_FILE ",zeeABExport];
If[Length[zeeABCouplingAtoms]===0,
 zeeABSetStatus["MAJORANA_AB_SIGMAS_COUPLING_ATOMS_NOT_IDENTIFIED"];
 Exit[17]];
If[!And@@{zeeABMassScalarB0,zeeABMassScalarFe,
 zeeABMassScalarHm,zeeABMassScalarCps},
 zeeABSetStatus["MAJORANA_AB_SIGMAS_REQUIRED_STRUCTURE_NOT_PRESENT"];
 Exit[16]];
(* FULL COMPLEX MATRIX DIAGNOSTIC — evaluated from the SARAH SigmaS
   expression and SARAH EWSB vertices, NOT the Chen E3 formula.
   No normalization/sign adjustment is allowed merely to obtain PASS.
   All physically necessary null tests are enforced first. *)
zeeABFixture=FileNameJoin[{zeeABDir,"e3_charged_loop_fixture.m"}];
If[!FileExistsQ[zeeABFixture],
 zeeABSetStatus["MAJORANA_AB_E3_NUMERIC_FIXTURE_MISSING"];Exit[18]];
Get[zeeABFixture];
If[!ListQ[zeeE3Cases]||Length[zeeE3Cases]!=2,
 zeeABSetStatus["MAJORANA_AB_E3_NUMERIC_FIXTURE_INVALID"];Exit[19]];
zeeABNumericalReport=FileNameJoin[{zeeABDir,
 "e3_majorana_ab_numeric_matrix_report.txt"}];
zeeABNumericalLedger={};
zeeABMW=80.379;

(* Preserve only precisely the five zero-tree-mass diagrams
   evidenced by the uploaded 2026-10-21 self-energy text:
   two charged scalar and two W terms after the Z term is zero.
   If SARAH changes them, reject the calculation instead of silently
   discarding diagrams. *)
zeeABZeroTreeExpanded=Expand[zeeABNuMassZeroSigmaS];
zeeABTopLevel=If[Head[zeeABZeroTreeExpanded]===Plus,
 List@@zeeABZeroTreeExpanded,{zeeABZeroTreeExpanded}];
zeeABScalarTerms=Select[zeeABTopLevel,!FreeQ[#,Hm[___]]&];
zeeABGaugeTerms=Select[zeeABTopLevel,FreeQ[#,Hm[___]]&];
Print["ZEE_E3_MAJORANA_AB_ZERO_TREE_TERM_COUNT ",
 Length[zeeABTopLevel]];
Print["ZEE_E3_MAJORANA_AB_ZERO_TREE_HM_TERM_COUNT ",
 Length[zeeABScalarTerms]];
Print["ZEE_E3_MAJORANA_AB_ZERO_TREE_W_TERM_COUNT ",
 Length[zeeABGaugeTerms]];
If[Length[zeeABScalarTerms]!=2||Length[zeeABGaugeTerms]!=2,
 zeeABSetStatus["MAJORANA_AB_UNEXPECTED_SIGMAS_ZERO_TREE_DIAGRAMS"];
 Exit[20]];
zeeABScalarExpression=Total[zeeABScalarTerms];
zeeABGaugeExpression=Total[zeeABGaugeTerms];

(* A requested SARAH vertex is cached by its exact field ordering,
   generation labels and chirality. No dummy global a/b/k variables. *)
Clear[zeeABStoredVertex];
zeeABStoredVertex[zeeABKind_String,zeeABNu_Integer,
 zeeABLep_Integer,zeeABState_Integer,zeeABProj_]:=
 zeeABStoredVertex[zeeABKind,zeeABNu,zeeABLep,
   zeeABState,zeeABProj]=Module[
 {zeeABFields,zeeABVtx,zeeABChiral},
 zeeABFields=Switch[zeeABKind,
  "hm",{Fv[{zeeABNu}],bar[Fe[{zeeABLep}]],
       Hm[{zeeABState}]},
  "hmConj",{Fv[{zeeABNu}],conj[Hm[{zeeABState}]],
       Fe[{zeeABLep}]},
  "wm",{Fv[{zeeABNu}],bar[Fe[{zeeABLep}]],VWm},
  "wmConj",{Fv[{zeeABNu}],conj[VWm],Fe[{zeeABLep}]},
  _,Return[$Failed]];
 zeeABVtx=CheckAbort[
  SARAH`Vertex[zeeABFields,Eigenstates->EWSB],$Aborted];
 If[zeeABVtx===0,Return[0]];
 If[zeeABVtx===$Aborted||!ListQ[zeeABVtx]||
  Length[zeeABVtx]<2,
  Print["FAIL MAJORANA_AB_VERTEX ",InputForm[zeeABFields],
    " value=",InputForm[zeeABVtx]];Return[$Failed]];
 (* Scalar vertices use bare PL/PR. Vector vertices use
    LorentzProduct[gamma[lt],PL/PR]; both describe the same
    chirality coefficient for SARAH's Cp[...] accessor. *)
 zeeABChiral=Cases[Rest[zeeABVtx],
  {zeeABExpression_,zeeABLorentz_}/;
   (zeeABLorentz===zeeABProj ||
    MatchQ[zeeABLorentz,
      LorentzProduct[gamma[_],zeeABProj]]):>
    zeeABExpression,{1}];
 If[Length[zeeABChiral]!=1,
  Print["FAIL MAJORANA_AB_VERTEX_CHIRALITY ",
   InputForm[zeeABFields]," ",InputForm[zeeABVtx]];
  Return[$Failed]];
 First[zeeABChiral]
];

(* One early all-orientations preflight prevents a broken Vertex API or
   chirality schema from spawning hundreds of noisy `$Failed` entries. *)
zeeABVertexPreflight={
 zeeABStoredVertex["hm",1,2,2,PL],
 zeeABStoredVertex["hm",1,2,2,PR],
 zeeABStoredVertex["hmConj",1,2,2,PL],
 zeeABStoredVertex["hmConj",1,2,2,PR],
 zeeABStoredVertex["wm",1,2,0,PL],
 zeeABStoredVertex["wm",1,2,0,PR],
 zeeABStoredVertex["wmConj",1,2,0,PL],
 zeeABStoredVertex["wmConj",1,2,0,PR]
};
If[MemberQ[zeeABVertexPreflight,$Failed],
 Print["FAIL MAJORANA_AB_VERTEX_CHIRALITY_PREFLIGHT ",
 InputForm[zeeABVertexPreflight]];
 zeeABSetStatus["MAJORANA_AB_VERTEX_CHIRALITY_PREFLIGHT_FAILED"];
 Exit[20]];
Print["ZEE_E3_MAJORANA_AB_VERTEX_CHIRALITY_PREFLIGHT_PASS ",
 Length[zeeABVertexPreflight]];

zeeABMixingMatrix[zeeABBeta_?NumericQ,
 zeeABGamma_?NumericQ]:=N[{
 {Cos[zeeABBeta],Sin[zeeABBeta],0},
 {-Sin[zeeABBeta]*Cos[zeeABGamma],
   Cos[zeeABBeta]*Cos[zeeABGamma],Sin[zeeABGamma]},
 {Sin[zeeABBeta]*Sin[zeeABGamma],
   -Cos[zeeABBeta]*Sin[zeeABGamma],Cos[zeeABGamma]}
}];

zeeABEvaluateVertex[zeeABVertex_,zeeABCase_Association]:=
 Module[{zeeABValue,zeeABFF,zeeABYe,zeeABYe2,zeeABZP,
 zeeABMasses,zeeABBeta,zeeABv},
 If[zeeABVertex===$Failed,Return[$Failed]];
 zeeABFF=zeeABCase["FSARAH"];
 zeeABYe=zeeABCase["YeSARAH"];
 zeeABYe2=zeeABCase["Ye2SARAH"];
 zeeABBeta=zeeABCase["Beta"];zeeABv=zeeABCase["V"];
 zeeABZP=zeeABMixingMatrix[zeeABBeta,zeeABCase["Gamma"]];
 zeeABValue=zeeABVertex //.
  HoldPattern[sum[zeeABIndex_,zeeABLo_Integer,
    zeeABHi_Integer,zeeABBody_]]:>
   Total[Table[zeeABBody,{zeeABIndex,zeeABLo,zeeABHi}]];
 zeeABValue=zeeABValue/.{
  Fzee[zeeABRow_Integer,zeeABCol_Integer]:>
   zeeABFF[[zeeABRow,zeeABCol]],
  Ye[zeeABRow_Integer,zeeABCol_Integer]:>
   zeeABYe[[zeeABRow,zeeABCol]],
  Ye2[zeeABRow_Integer,zeeABCol_Integer]:>
   zeeABYe2[[zeeABRow,zeeABCol]],
  ZP[zeeABRow_Integer,zeeABCol_Integer]:>
   zeeABZP[[zeeABRow,zeeABCol]],
  Ve[zeeABRow_Integer,zeeABCol_Integer]:>
   KroneckerDelta[zeeABRow,zeeABCol],
  Ue[zeeABRow_Integer,zeeABCol_Integer]:>
   KroneckerDelta[zeeABRow,zeeABCol],
  v1->zeeABv*Cos[zeeABBeta],
  v2->zeeABv*Sin[zeeABBeta],
  g2->2*zeeABMW/zeeABv
 };
 zeeABValue=zeeABValue/.
  HoldPattern[conj[zeeABNumber_?NumericQ]]:>
  Conjugate[zeeABNumber];
 N[zeeABValue]
];
zeeABGetNumCp[zeeABKind_String,zeeABNu_Integer,
 zeeABLep_Integer,zeeABState_Integer,
 zeeABProj_,zeeABCase_Association]:=
 zeeABEvaluateVertex[
  zeeABStoredVertex[zeeABKind,zeeABNu,zeeABLep,
   zeeABState,zeeABProj],zeeABCase];

(* Finite dimensional regularization B0 at p^2=0. The difference
   of the two physical Hm terms must be Q-independent; the
   divergent universal UV pole is not put back by hand. *)
zeeABFiniteB0[zeeABArg1_?NumericQ,
 zeeABArg2_?NumericQ,zeeABScale_?NumericQ]:=
 Module[{zeeABOne=N[zeeABArg1],zeeABTwo=N[zeeABArg2],
  zeeABQ2=N[zeeABScale^2]},
 If[zeeABOne<=0||zeeABTwo<=0,Return[$Failed]];
 If[Abs[zeeABOne-zeeABTwo]<
   1.*^-10 Max[zeeABOne,zeeABTwo],
  N[-Log[zeeABOne/zeeABQ2]],
  N[1-(zeeABOne Log[zeeABOne/zeeABQ2]-
    zeeABTwo Log[zeeABTwo/zeeABQ2])/
     (zeeABOne-zeeABTwo)]]
 ];

(* Numeric substitution of a generated CP-containing term.
   External indices and both internal sums are explicitly expanded
   BEFORE substituting numerical EWSB vertex coefficients.
   Any unsupported Cp ordering is left unevaluated and causes a
   fail-closed nonnumerical status, never an invented zero. *)
zeeABEvaluateSigma[zeeABExpr_,zeeABI_Integer,
 zeeABJ_Integer,zeeABCase_Association,
 zeeABScale_?NumericQ,zeeABrMS_Integer]:=
 Module[{zeeABResult,zeeABM,zeeABHmass},
 zeeABM=zeeABCase["LeptonMasses"];
 zeeABHmass={zeeABMW,
   zeeABCase["M1"],zeeABCase["M2"]};
 zeeABResult=zeeABExpr/.{gO1->zeeABI,gO2->zeeABJ};
 zeeABResult=zeeABResult //.
  HoldPattern[sum[zeeABIndex_,zeeABLo_Integer,
    zeeABHi_Integer,zeeABBody_]]:>
   Total[Table[zeeABBody,{zeeABIndex,zeeABLo,zeeABHi}]];
 zeeABResult=zeeABResult/.{
  Mass[Fe[{zeeABIndex_Integer}]]:>zeeABM[[zeeABIndex]],
  Mass2[Fe[{zeeABIndex_Integer}]]:>
     zeeABM[[zeeABIndex]]^2,
  Mass2[Hm[{zeeABIndex_Integer}]]:>
     zeeABHmass[[zeeABIndex]]^2,
  Mass2[VWm]->zeeABMW^2,
  p->0,rMS->zeeABrMS
 };
 zeeABResult=zeeABResult/.
  HoldPattern[B0[zeeABP_,zeeABA_?NumericQ,
    zeeABB_?NumericQ]]:>
    zeeABFiniteB0[zeeABA,zeeABB,zeeABScale];
 zeeABResult=zeeABResult/.{
  HoldPattern[Cp[Fv[{zeeABNu_Integer}],
    bar[Fe[{zeeABLep_Integer}]],
    Hm[{zeeABState_Integer}]][zeeABProj_]]:>
   zeeABGetNumCp["hm",zeeABNu,zeeABLep,
    zeeABState,zeeABProj,zeeABCase],
  HoldPattern[Cp[Fv[{zeeABNu_Integer}],
    conj[Hm[{zeeABState_Integer}]],
    Fe[{zeeABLep_Integer}]][zeeABProj_]]:>
   zeeABGetNumCp["hmConj",zeeABNu,zeeABLep,
    zeeABState,zeeABProj,zeeABCase],
  HoldPattern[Cp[Fv[{zeeABNu_Integer}],
    bar[Fe[{zeeABLep_Integer}]],
    VWm][zeeABProj_]]:>
   zeeABGetNumCp["wm",zeeABNu,zeeABLep,
    0,zeeABProj,zeeABCase],
  HoldPattern[Cp[Fv[{zeeABNu_Integer}],
    conj[VWm],Fe[{zeeABLep_Integer}]][zeeABProj_]]:>
   zeeABGetNumCp["wmConj",zeeABNu,zeeABLep,
    0,zeeABProj,zeeABCase]
 };
 zeeABResult=zeeABResult/.
  HoldPattern[conj[zeeABNumber_?NumericQ]]:>
  Conjugate[zeeABNumber];
 N[zeeABResult]
];

zeeABMatrix[zeeABExpr_,zeeABCase_Association,
 zeeABScale_?NumericQ,zeeABrMS_Integer]:=
 Table[zeeABEvaluateSigma[zeeABExpr,zeeABI,zeeABJ,
   zeeABCase,zeeABScale,zeeABrMS],
 {zeeABI,1,3},{zeeABJ,1,3}];

(* Null tests modify only the physically relevant Lagrangian
   parameters, not the stored Chen reference matrix. *)
zeeABNullCases[zeeABCase_Association]:=Module[
 {zeeABFNull,zeeABMixNull,zeeABYNull,zeeABMassDegenerate,zeeABAlign,
  zeeABBeta=zeeABCase["Beta"],zeeABv=zeeABCase["V"]},
 zeeABFNull=Association[zeeABCase,
   "FSARAH"->ConstantArray[0.+0.I,{3,3}]];
 zeeABMixNull=Association[zeeABCase,"Gamma"->0.];
 zeeABMassDegenerate=Association[zeeABCase,
  "M2"->zeeABCase["M1"]];
 zeeABAlign=DiagonalMatrix[
  Sqrt[2]*zeeABCase["LeptonMasses"]/zeeABv];
 zeeABYNull=Association[zeeABCase,
  "YeSARAH"->Cos[zeeABBeta]*zeeABAlign,
  "Ye2SARAH"->Sin[zeeABBeta]*zeeABAlign];
 {{"f_zero",zeeABFNull},
  {"gamma_zero",zeeABMixNull},
  {"charged_masses_degenerate",zeeABMassDegenerate},
  {"nonvev_Y_zero",zeeABYNull}}
];

(* Independent complex phase convention check at the level of
   SARAH's PHYSICAL vertices. The Lagrangian terms determine
      Cp[Fv_i,bar[Fe_l],Hm_k][PL]  = -i D_{l i k}
      Cp[Fv_i,bar[Fe_l],Hm_k][PR]  = -i (f_{i l})* ZP[k,3]
      Cp[Fv_i,conj[Hm_k],Fe_l][PL]= -i f_{i l} ZP[k,3]
      Cp[Fv_i,conj[Hm_k],Fe_l][PR]= -i (D_{l i k})*
   where D_{l i k}=ZP[k,1] Ye_{l i}+ZP[k,2] Ye2_{l i}.
   The explicit conjugation on PR in the first orientation
   explains why the SARAH SigmaS matrix has conjugated complex
   Yukawas relative to the E3 f*M_l*Y convention.
   The sign of the on-shell Majorana mass still depends on
   whether SigmaS enters the inverse propagator as +Sigma
   or -Sigma; this script reports the -Conjugate mapping as
   a physical-CONVENTION hypothesis, not a fitted correction. *)
zeeABCheckVertexOrientation[zeeABCase_Association]:=Module[
 {zeeABMix=zeeABMixingMatrix[
    zeeABCase["Beta"],zeeABCase["Gamma"]],
  zeeABF=zeeABCase["FSARAH"],
  zeeABY1=zeeABCase["YeSARAH"],
  zeeABY2=zeeABCase["Ye2SARAH"],
  zeeABMax=0.,zeeABCount=0,
  zeeABD,zeeABValues,zeeABExpected,zeeABDeltas},
 Do[
  zeeABD=zeeABMix[[kk,1]]*zeeABY1[[ll,ii]]+
      zeeABMix[[kk,2]]*zeeABY2[[ll,ii]];
  zeeABValues={
    zeeABGetNumCp["hm",ii,ll,kk,PL,zeeABCase],
    zeeABGetNumCp["hm",ii,ll,kk,PR,zeeABCase],
    zeeABGetNumCp["hmConj",ii,ll,kk,PL,zeeABCase],
    zeeABGetNumCp["hmConj",ii,ll,kk,PR,zeeABCase]};
  zeeABExpected={
   -I*zeeABD,
   -I*Conjugate[zeeABF[[ii,ll]]]*zeeABMix[[kk,3]],
   -I*zeeABF[[ii,ll]]*zeeABMix[[kk,3]],
   -I*Conjugate[zeeABD]};
  If[!VectorQ[zeeABValues,NumericQ],
   Print["FAIL MAJORANA_AB_COMPLEX_VERTEX_NONNUMERIC ",
     InputForm[{ii,ll,kk,zeeABValues}]];
   Return[$Failed]];
  zeeABDeltas=Abs[zeeABValues-zeeABExpected];
  zeeABMax=Max[zeeABMax,Max[zeeABDeltas]];
  zeeABCount+=Length[zeeABValues],
 {ii,1,3},{ll,1,3},{kk,{2,3}}];
 Print["ZEE_E3_MAJORANA_COMPLEX_VERTEX_CONVENTIONS ",
   zeeABCase["Label"]," COUNT=",zeeABCount,
   " MAX_RESIDUAL=",InputForm[zeeABMax]];
 If[zeeABCount!=72||zeeABMax>1.*^-12,Return[$Failed]];
 {zeeABCount,zeeABMax}
];

zeeABMatrixResults={};zeeABMatrixErrors={};
zeeABMatrixNumericQ[zeeABValue_]:=
 MatrixQ[zeeABValue,NumericQ] &&
 Dimensions[zeeABValue]==={3,3};

Do[
 Module[{zeeABCase=zeeE3Cases[[zeeABCaseIdx]],
  zeeABRaw,zeeABScalar,zeeABGauge,zeeABScaleTest,
  zeeABrMSTest,zeeABNullValue,zeeABNullData,
  zeeABRef,zeeABPrefactor,zeeABPlus,zeeABMinus,
  zeeABSymResidual,zeeABScaleResidual,
  zeeABGaugeResidual,zeeABrMSResidual,
  zeeABResidualPlus,zeeABResidualMinus,
  zeeABResidualConjPlus,zeeABResidualConjMinus,
  zeeABVertexConventions,zeeABCanonicalResidual,
  zeeABReferenceScale},
 Print["ZEE_E3_MAJORANA_NUMERIC_CASE_BEGIN ",
  zeeABCase["Label"]];
 zeeABVertexConventions=zeeABCheckVertexOrientation[zeeABCase];
 If[zeeABVertexConventions===$Failed,
   zeeABSetStatus["MAJORANA_AB_COMPLEX_VERTEX_PHASE_CONVENTION_MISMATCH"];
   Exit[23]];

 zeeABRaw=zeeABMatrix[zeeABNuMassZeroSigmaS,
  zeeABCase,100.,0];
 zeeABScalar=zeeABMatrix[zeeABScalarExpression,
  zeeABCase,100.,0];
 zeeABGauge=zeeABMatrix[zeeABGaugeExpression,
  zeeABCase,100.,0];
 zeeABScaleTest=zeeABMatrix[zeeABNuMassZeroSigmaS,
  zeeABCase,1000.,0];
 zeeABrMSTest=zeeABMatrix[zeeABNuMassZeroSigmaS,
  zeeABCase,100.,1];
 If[!And@@(zeeABMatrixNumericQ/@{
   zeeABRaw,zeeABScalar,zeeABGauge,zeeABScaleTest,
   zeeABrMSTest}),
   Print["FAIL MAJORANA_AB_NONNUMERIC_SIGMAS ",
    InputForm[zeeABRaw]];
   zeeABSetStatus["MAJORANA_AB_NUMERIC_SIGMAS_NOT_RESOLVED"];
   Exit[21]];
 zeeABPrefactor=10.^9/(16 Pi^2);
 zeeABRef=zeeABCase["FiniteMnuEV"];
 zeeABPlus=N[zeeABPrefactor*zeeABRaw];
 zeeABMinus=-zeeABPlus;
 zeeABSymResidual=Max[Abs[Flatten[
   zeeABRaw-Transpose[zeeABRaw]]]];
 zeeABScaleResidual=Max[Abs[Flatten[
   zeeABRaw-zeeABScaleTest]]];
 zeeABGaugeResidual=Max[Abs[Flatten[zeeABGauge]]];
 zeeABrMSResidual=Max[Abs[Flatten[
   zeeABRaw-zeeABrMSTest]]];
 zeeABResidualPlus=Max[Abs[Flatten[
   zeeABPlus-zeeABRef]]];
 zeeABResidualMinus=Max[Abs[Flatten[
   zeeABMinus-zeeABRef]]];
 zeeABResidualConjPlus=Max[Abs[Flatten[
   Conjugate[zeeABPlus]-zeeABRef]]];
 zeeABResidualConjMinus=Max[Abs[Flatten[
   Conjugate[zeeABMinus]-zeeABRef]]];
 (* The convention comparison is FIXED, not a minimum over signs.
    From the explicit chiral-coupling identities checked above,
    SigmaS is the charge-conjugated matrix in SARAH conventions.
    We report the inverse-propagator minus sign separately and
    still require an independent phase/sigma-sign derivation
    before labeling a physical neutrino mass implementation. *)
 zeeABCanonicalResidual=Max[Abs[Flatten[
   -Conjugate[zeeABPlus]-zeeABRef]]];
 zeeABReferenceScale=Max[Abs[Flatten[zeeABRef]]];
 Print["ZEE_E3_MAJORANA_FIXED_NEGCONJ_COMPARISON ",
  zeeABCase["Label"],
  " ABS_RESIDUAL_EV=",InputForm[zeeABCanonicalResidual],
  " REL_RESIDUAL=",InputForm[
    zeeABCanonicalResidual/Max[zeeABReferenceScale,1.*^-12]]];
 If[zeeABCanonicalResidual>5.*^-11,
  AppendTo[zeeABMatrixErrors,
   "fixed_negconj_E3_reference_residual_"<>zeeABCase["Label"]]];

 If[Max[Abs[Flatten[zeeABPlus]]]<1.*^-4,
   AppendTo[zeeABMatrixErrors,
    "nonzero_Zee_signal_not_detected_"<>zeeABCase["Label"]]];
 Print["ZEE_E3_MAJORANA_NUMERIC_CASE ",zeeABCase["Label"],
  " MNU_RAW=",InputForm[zeeABRaw],
  " SARAH_PLUS_EV=",InputForm[zeeABPlus],
  " REFERENCE_E3_FINITE_EV=",InputForm[zeeABRef]];
 Print["ZEE_E3_MAJORANA_NUMERIC_SIGNAL_MAX_EV ",
  zeeABCase["Label"]," ",
  InputForm[Max[Abs[Flatten[zeeABPlus]]]]];
 Print["ZEE_E3_MAJORANA_NUMERIC_RESIDUALS ",
  zeeABCase["Label"],
  " SYMMETRY_GEV=",InputForm[zeeABSymResidual],
  " SCALE_GEV=",InputForm[zeeABScaleResidual],
  " W_GAUGE_GEV=",InputForm[zeeABGaugeResidual],
  " SCHEME_GEV=",InputForm[zeeABrMSResidual],
  " E3_PLUS_EV=",InputForm[zeeABResidualPlus],
  " E3_MINUS_EV=",InputForm[zeeABResidualMinus],
  " E3_CONJ_PLUS_EV=",InputForm[zeeABResidualConjPlus],
  " E3_CONJ_MINUS_EV=",InputForm[zeeABResidualConjMinus]];
 AppendTo[zeeABMatrixResults,
  {zeeABCase["Label"],"raw",zeeABRaw,
   "scalar",zeeABScalar,"gauge",zeeABGauge,
   "reference",zeeABRef,
   "plus",zeeABPlus}];
 (* The four diagnostics with signs/conjugations expose
    potential convention discrepancies but NEVER pick the smallest
    as the declared physical answer. *)
 If[Max[{zeeABSymResidual,zeeABScaleResidual,
  zeeABGaugeResidual,zeeABrMSResidual}]>1.*^-15,
  AppendTo[zeeABMatrixErrors,
   "structure_or_null_"<>zeeABCase["Label"]]];
 Do[
  zeeABNullValue=zeeABMatrix[zeeABNuMassZeroSigmaS,
   zeeABNull[[2]],100.,0];
  If[!zeeABMatrixNumericQ[zeeABNullValue],
   Print["FAIL MAJORANA_AB_NULL_NONNUMERIC ",
    zeeABCase["Label"],"/",zeeABNull[[1]]];
   AppendTo[zeeABMatrixErrors,
    "null_not_numeric_"<>zeeABCase["Label"]<>"/"<>zeeABNull[[1]]],
   Print["ZEE_E3_MAJORANA_NULL_RESULT ",
     zeeABCase["Label"],"/",zeeABNull[[1]],
     " MAX_GEV=",InputForm[Max[
     Abs[Flatten[zeeABNullValue]]]]];
   If[Max[Abs[Flatten[zeeABNullValue]]]>1.*^-15,
    AppendTo[zeeABMatrixErrors,
     "null_nonzero_"<>zeeABCase["Label"]<>"/"<>zeeABNull[[1]]]]],
  {zeeABNull,zeeABNullCases[zeeABCase]}];
 ],{zeeABCaseIdx,Length[zeeE3Cases]}
];
Export[zeeABNumericalReport,
 StringRiffle[
  (ToString[InputForm[#]]&/@zeeABMatrixResults),"\n\n"]<>
  "\nFAILURE_LABELS="<>ToString[InputForm[zeeABMatrixErrors]]<>"\n",
 "Text"];
Print["ZEE_E3_MAJORANA_NUMERIC_REPORT ",zeeABNumericalReport];
Print["ZEE_E3_MAJORANA_NUMERIC_FAILURE_LABELS ",
 InputForm[zeeABMatrixErrors]];
Print["ZEE_E3_MAJORANA_NUMERIC_MNU_INDEPENDENTLY_MATCHED False"];
If[Length[zeeABMatrixErrors]>0,
 zeeABSetStatus["MAJORANA_AB_NUMERIC_MATRIX_STRUCTURE_OR_NULL_FAILURE"];
 Exit[22]];
(* A successful status here certifies only evaluated raw diagrams
   plus independent null tests; a physical Majorana-sign convention
   must still be fixed before declaring E3 matching. *)
zeeABSetStatus[
 "MAJORANA_AB_SARAH_3X3_FINITE_B0_NEGCONJ_MATCH_PHASE_SIGN_DERIVATION_PENDING"];
Exit[0];

