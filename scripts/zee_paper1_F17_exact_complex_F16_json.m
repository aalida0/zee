(* F17: export source-pinned real+imag three-F13 complex flavor and
   charged mixing to standard JSON. This does NOT inspect UFO parameters
   or certify model-specific SLHA cards. No SARAH initialization needed. *)
dir=Environment["ZEE_F16_DIR"];
If[!StringQ[dir]||StringLength[dir]==0||!DirectoryQ[dir],
 Print["F17_FAIL_NO_SOURCE_F16_DIR"];Exit[2]];
source=FileNameJoin[{dir,"F16_three_exact_F13_Zee_SARAH_charged_vertices.m"}];
status=FileNameJoin[{dir,"F16_local_SARAH_vertex_status.txt"}];
pass="F16_THREE_HEAVY_SARAH_MASS_GAUGE_CUBIC_COMPLEX_LEPTON_PASS_NOT_MADWIDTH";
If[!FileExistsQ[source]||!FileExistsQ[status]||
 StringTrim[Import[status,"Text"]]=!=pass,
 Print["F17_FAIL_SOURCE_THREE_SARAH_TREE_VERTICES_NOT_VALIDATED"];Exit[3]];
output=FileNameJoin[{dir,"F17_three_F13_exact_complex_matrices_from_F16.json"}];
If[FileExistsQ[output],Print["F17_REFUSE_OVERWRITE ",output];Exit[4]];
Get[source];
expected={"F13_heavy_0001330","F13_heavy_0000981","F13_heavy_0001003"};
If[!ListQ[zeeF16Cases]||Length[zeeF16Cases]=!=3||
  Sort[Lookup[zeeF16Cases,"ID"]]=!=Sort[expected],
 Print["F17_FAIL_EXACT_THREE_CASE_SOURCE_SET"];Exit[5]];
pair[z_?NumericQ]:={N[Re[z]],N[Im[z]]};
getMat[o_,name_String_,dims_List]:=Module[{a=Lookup[o,name,Missing[]]},
 If[!MatrixQ[a,NumericQ]||Dimensions[a]=!=dims,
  Print["F17_BAD_MATRIX ",o["ID"]," ",name, " ",InputForm[a]];
  Return[$Failed]];
 Map[pair,a,{2}]
];
names={"FSARAH","YeSARAH","Ye2SARAH","YChen","MixCharged","MixCPeven","MixCPodd"};
sizes={{3,3},{3,3},{3,3},{3,3},{3,3},{2,2},{2,2}};
cases=Table[
 Module[{o=zeeF16Cases[[i]],mat},
  mat=Association@Table[
    names[[j]]->getMat[o,names[[j]],sizes[[j]]],
    {j,Length[names]}];
  If[MemberQ[Values[mat],$Failed],Return[$Failed]];
  <|
   "candidate_id"->o["ID"],
   "mH1_GeV"->N[o["M1"]],
   "mH2_GeV"->N[o["M2"]],
   "mA_GeV"->N[o["MA"]],
   "mHeavyNeutral_GeV"->N[o["MH"]],
   "vev_GeV"->N[o["V"]],
   "beta_rad"->N[o["Beta"]],
   "alpha_rad"->N[o["Alpha"]],
   "gamma_rad"->N[o["Gamma"]],
   "lepton_masses_GeV"->N[o["LeptonMasses"]],
   "matrices_re_im"->mat,
   "full_Zee_param_card_validated"->False,
   "ufo_fermion_couplings_checked"->False
  |>
 ],{i,3}];
If[MemberQ[cases,$Failed]||!And@@(AssociationQ/@cases),
 Print["F17_FAIL_COMPLEX_MATRICES_MISSING"];Exit[6]];
payload=<|
 "status"->"F17_F16_SOURCE_EXACT_THREE_COMPLEX_MATRICES_NOT_UFO_PARAM_CARD",
 "candidate_ids"->expected,
 "matrices"->cases,
 "SARAH_three_tree_vertex_gate"->pass,
 "full_Zee_param_card_validated"->False
|>;
Export[output,payload,"RawJSON"];
If[!FileExistsQ[output]||FileByteCount[output]<3000,
 Print["F17_FAIL_JSON_COMPLEX_MATRICES_EXPORT"];Exit[7]];
Print["F17_COMPLEX_SOURCE_EXPORT_OK ",output," CASES 3"];
Exit[0];
