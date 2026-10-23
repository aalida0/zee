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
Get[FileNameJoin[{Directory[],"scripts","zee_paper1_F17_exact_complex_json_helpers.m"}]];
If[!ValueQ[zeeF17MatrixJSONStatus]||
    zeeF17MatrixJSONStatus=!="F17_EXACT_7_COMPLEX_MATRIX_NUMERIC_JSON_PAIRS",
 Print["F17_FAIL_MATHEMATICA_COMPLEX_MATRIX_HELPER_NOT_LOADED"];Exit[6]];
cases=Table[
 Module[{o=zeeF16Cases[[i]],mat},
  mat=zeeF17Matrices[o];
  If[mat===$Failed,
    Print["F17_BAD_SOURCE_COMPLEX_MATRIX ",o["ID"]];
    Return[$Failed]];
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
If[MemberQ[cases,$Failed]||!And@@(AssociationQ/@cases)||
   Length[cases]=!=3,
 Print["F17_FAIL_COMPLEX_MATRICES_MISSING"];Exit[6]];
payload=<|
 "status"->"F17_F16_SOURCE_EXACT_THREE_COMPLEX_MATRICES_NOT_UFO_PARAM_CARD",
 "candidate_ids"->expected,
 "matrices"->cases,
 "SARAH_three_tree_vertex_gate"->pass,
 "full_Zee_param_card_validated"->False
|>;
(* Produce a complete JSON string BEFORE writing any output file.
   A strict RawJSON export must not be allowed to create an empty or
   truncated artifact that a subsequent run mistakes for complete. *)
jsonText=Quiet[Check[ExportString[payload,"RawJSON"],$Failed]];
If[!StringQ[jsonText]||StringLength[jsonText]<3000,
 Print["F17_FAIL_JSON_COMPLEX_MATRICES_EXPORT"];
 Exit[7]];
exportCheck=Quiet[Check[ImportString[jsonText,"RawJSON"],$Failed]];
If[!AssociationQ[exportCheck]||
  Length[Lookup[exportCheck,"matrices",{}]]=!=3||
  Lookup[exportCheck,"full_Zee_param_card_validated",Missing[]]=!=False,
 Print["F17_FAIL_JSON_SOURCE_ROUNDTRIP"];Exit[8]];
Export[output,jsonText,"Text"];
If[!FileExistsQ[output]||FileByteCount[output]<3000,
 Print["F17_FAIL_JSON_COMPLEX_MATRICES_EXPORT"];Exit[9]];
Print["F17_COMPLEX_SOURCE_EXPORT_OK ",output," CASES 3"];
Exit[0];
