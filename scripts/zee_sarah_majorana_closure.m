(* Physical mass closure, separately from raw diagram extraction.
   The sign/conjugation is fixed by chiral inverse-propagator algebra
   and the local SARAH mass constructor, never selected by a fit.
   See validation/module0/CONVENTIONS.md for the full correspondence. *)
zeeCRoot=Directory[];zeeCOut=FileNameJoin[{zeeCRoot,"work","sarah_zee"}];
zeeCState=FileNameJoin[{zeeCOut,"module0_majorana_status.txt"}];
Export[zeeCState,"MAJORANA_PHYSICAL_CLOSURE_NOT_VALIDATED\n","Text"];
zeeCStop[msg_]:=(Export[zeeCState,msg<>"\n","Text"];Print[msg];Exit[2]);
zeeCDataPath=FileNameJoin[{zeeCOut,"module0_majorana_closure_inputs.m"}];
If[!FileExistsQ[zeeCDataPath],zeeCStop["GENERATED_CHIRAL_FORM_FACTORS_MISSING"]];
zeeCManifest=Import[FileNameJoin[{zeeCOut,"e3_majorana_variant_manifest.json"}],"RawJSON"];
If[!TrueQ[zeeCManifest["production_majorana"]]||
 zeeCManifest["changed_lines_exactly"]=!={"Model name"},
 zeeCStop["PRODUCTION_AND_DIAGNOSTIC_MAJORANA_REPRESENTATIONS_DIFFER"]];
zeeCModel=FileNameJoin[{zeeCRoot,"models","SARAH","ZeeTypeII","ZeeTypeII.m"}];
If[IntegerString[FileHash[zeeCModel,"SHA256"],16,64]=!=
 zeeCManifest["baseline_sha256"]["ZeeTypeII.m"],zeeCStop["STALE_MAJORANA_MODEL_PROVENANCE"]];
zeeCSource=FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH",
 "Package","SPheno","SPhenoLoopMasses.m"}];
zeeCText=Import[zeeCSource,"Text"];
(* SigmaSL = CpR_i conj(CpL_j), SigmaSR = CpL_i conj(CpR_j).
   For the mass operator -1/2 nu_L^T M nu_L+h.c., the Majorana
   inverse propagator yields delta M=-1/2(conj(SigmaSL)+SigmaSR).
   Wavefunction terms multiply M_tree=0 and are O(hbar^2).
   Below are exact source anchors in the independent mass constructor. *)
zeeCAnchors={
 "mat1 = mat1a - 0.5_dp*(Conjg(SigSL) + SigSR + &",
 "SumSL(gO1,gO2) = coupR1*coupL2*B0m2",
 "SumSR(gO1,gO2) = coupL1*coupR2*B0m2"};
If[!And@@(StringContainsQ[zeeCText,#]&/@zeeCAnchors),zeeCStop["UPSTREAM_MASS_CONVENTION_CHANGED"]];
zeeCData=Get[zeeCDataPath];
If[!ListQ[zeeCData]||Length[zeeCData]!=2,zeeCStop["CHIRAL_MATRIX_LEDGER_INVALID"]];
zeeCResults={};zeeCFailures={};
Do[
 zeeCSL=zeeCCase["SigmaSLRaw"];zeeCSR=zeeCCase["SigmaSRRaw"];
 (* Restore exactly one universal loop factor and GeV -> eV. *)
 zeeCMass=-10.^9/(32*Pi^2)*(Conjugate[zeeCSL]+zeeCSR);
 zeeCRef=zeeCCase["ReferenceEV"];zeeCP=zeeCCase["Rephasing"];
 zeeCChirality=Max[Abs[Flatten[zeeCSR-Conjugate[zeeCSL]]]];
 zeeCResidual=Max[Abs[Flatten[zeeCMass-zeeCRef]]];
 zeeCRelative=zeeCResidual/Max[Abs[Flatten[zeeCRef]]];
 zeeCRephased=-10.^9/(16*Pi^2)*Conjugate[zeeCCase["RephasedSigmaSLRaw"]];
 zeeCPhaseResidual=Max[Abs[Flatten[zeeCRephased-zeeCP.zeeCMass.zeeCP]]];
 {zeeCU,zeeCW,zeeCV}=SingularValueDecomposition[zeeCMass];
 zeeCDiag=Diagonal[ConjugateTranspose[zeeCU].zeeCMass.Conjugate[zeeCU]];
 zeeCTakagi=Conjugate[zeeCU].DiagonalMatrix[Exp[-I/2*Arg[zeeCDiag]]];
 zeeCTakagiResidual=Max[Abs[Flatten[Transpose[zeeCTakagi].zeeCRef.zeeCTakagi-zeeCW]]];
 (* Phase-sensitive rephasing-invariant complex products; retain both
    real and imaginary parts, not only Takagi masses. *)
 zeeCCPProduct[mat_]:=mat[[1,1]]*mat[[2,2]]*Conjugate[mat[[1,2]]]^2;
 zeeCCPResidual=Abs[zeeCCPProduct[zeeCMass]-zeeCCPProduct[zeeCRef]];
 If[!And@@(NumericQ/@{zeeCChirality,zeeCResidual,zeeCPhaseResidual,zeeCTakagiResidual,zeeCCPResidual})||
  zeeCChirality>1.*^-16||zeeCResidual>5.*^-11||zeeCRelative>1.*^-8||
  zeeCPhaseResidual>5.*^-11||zeeCTakagiResidual>5.*^-11||zeeCCPResidual>1.*^-17,
  AppendTo[zeeCFailures,zeeCCase["label"]]];
 AppendTo[zeeCResults,<|"label"->zeeCCase["label"],
 "opposite_chirality_residual_GeV"->zeeCChirality,
 "physical_matrix_residual_eV"->zeeCResidual,"physical_relative_residual"->zeeCRelative,
 "rephasing_residual_eV"->zeeCPhaseResidual,"takagi_reference_residual_eV"->zeeCTakagiResidual,
 "CP_product_residual_eV4"->zeeCCPResidual,
 "mass_matrix_real_eV"->Re[zeeCMass],"mass_matrix_imag_eV"->Im[zeeCMass],
 "takagi_masses_eV"->Diagonal[zeeCW],
 "takagi_rotation_real"->Re[zeeCTakagi],"takagi_rotation_imag"->Im[zeeCTakagi]|>],
 {zeeCCase,zeeCData}];
Export[FileNameJoin[{zeeCOut,"module0_majorana_physical_report.json"}],
 <|"source_mass_constructor_sha256"->IntegerString[FileHash[zeeCSource,"SHA256"],16,64],
 "source_anchors"->zeeCAnchors,"formula"->"deltaM=-1/2(conj(SigmaSL)+SigmaSR)/(16 pi^2)",
 "tree_mass_zero"->True,"tolerance_matrix_eV"->5.*^-11,
 "tolerance_relative"->1.*^-8,"results"->zeeCResults,
 "failures"->zeeCFailures|>,"RawJSON"];
If[Length[zeeCFailures]>0,zeeCStop["PHYSICAL_COMPLEX_MAJORANA_MATRIX_MISMATCH"]];
Export[zeeCState,"PHYSICAL_COMPLEX_MAJORANA_MASS_AND_PHASE_CLOSURE_PASS\n","Text"];
Print["PHYSICAL_COMPLEX_MAJORANA_MASS_AND_PHASE_CLOSURE_PASS"];
Exit[0];
