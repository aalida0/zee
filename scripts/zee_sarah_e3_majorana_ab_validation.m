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
Print["ZEE_E3_MAJORANA_AB_COMPLEX_MNU_MATRIX_EXTRACTED False"];
Print["ZEE_E3_MAJORANA_AB_CHEN_E3_NUMERIC_MATCH False"];
Export[zeeABExport,StringRiffle[{
 "SARAH-GENERATED MAJORANA-PACKAGED Fv FORM FACTORS",
 "Not a physical one-loop Majorana mass certificate.",
 "Spinor variant: "<>zeeABName,
 "Fv classified Majorana: "<>ToString[zeeABClassified],
 "SigmaS:\\n"<>ToString[InputForm[zeeABS]],
 "SigmaR:\\n"<>ToString[InputForm[zeeABR]],
 "SigmaL:\\n"<>ToString[InputForm[zeeABL]],
 "Diagrams:\\n"<>ToString[InputForm[zeeABDiagrams[[zeeABNuIndex]]]]
 },"\n\n"]<>"\n","Text"];
Print["ZEE_E3_MAJORANA_AB_SIGMA_FILE ",zeeABExport];
If[!And@@{zeeABMassScalarB0,zeeABMassScalarFe,
 zeeABMassScalarHm,zeeABMassScalarCps},
 zeeABSetStatus["MAJORANA_AB_SIGMAS_REQUIRED_STRUCTURE_NOT_PRESENT"];
 Exit[16]];
(* Critical: a new four-component representation changes which
   charge-conjugated contractions SARAH generates; only explicit
   flavor- and complex-phase comparison can certify the Majorana Mnu. *)
zeeABSetStatus[
 "MAJORANA_AB_SARAH_SIGMAS_GENERATED_NUMERIC_MNU_AND_LNV_UNVALIDATED"];
Exit[0];
