(* F17 mandatory local REAL Mathematica regression for the SAME matrix
   serializer used on the immutable original F16 three-case source. *)
root=Directory[];
Get[FileNameJoin[{root,"scripts","zee_paper1_F17_exact_complex_json_helpers.m"}]];
If[!ValueQ[zeeF17MatrixJSONStatus]||
    zeeF17MatrixJSONStatus=!="F17_EXACT_7_COMPLEX_MATRIX_NUMERIC_JSON_PAIRS",
 Print["F17_COMPLEX_JSON_SELFTEST_FAIL_MISSING_HELPER"];Exit[21]];
m3=Table[If[i==j,1.*^-4+I*1.*^-5,-3.*^-6+I*2.*^-6],
 {i,1,3},{j,1,3}];
mix3={{.9,.1,.0},{-.1,.9,.0},{0.,0.,1.}};
mix2={{.8,.6},{-.6,.8}};
o=<|"ID"->"synthetic_internal_wolfram_test_only",
  "FSARAH"->m3,"YeSARAH"->m3,"Ye2SARAH"->m3,
  "YChen"->m3,"MixCharged"->mix3,
  "MixCPeven"->mix2,"MixCPodd"->mix2|>;
data=zeeF17Matrices[o];
If[!AssociationQ[data]||Length[data]=!=7||
    !TrueQ[Dimensions[data["FSARAH"]]==={3,3,2}]||
    !TrueQ[Dimensions[data["MixCPodd"]]==={2,2,2}],
 Print["F17_COMPLEX_JSON_SELFTEST_FAIL_MATRICES ",InputForm[data]];
 Exit[22]];
If[!TrueQ[Abs[data["FSARAH"][[1,1,2]]-1.*^-5]<1.*^-14],
 Print["F17_COMPLEX_JSON_SELFTEST_FAIL_IMAGINARY_DATA"];Exit[23]];
json=Quiet[Check[ExportString[<|"matrices_re_im"->data|>,"RawJSON"],$Failed]];
If[!StringQ[json]||StringLength[json]<200,
 Print["F17_COMPLEX_JSON_SELFTEST_FAIL_JSON_SERIALIZATION ",
   InputForm[json]];Exit[24]];
parsed=Quiet[Check[ImportString[json,"RawJSON"],$Failed]];
If[!AssociationQ[parsed]||
   !TrueQ[Dimensions[parsed["matrices_re_im"]["FSARAH"]]==={3,3,2}],
 Print["F17_COMPLEX_JSON_SELFTEST_FAIL_JSON_ROUNDTRIP"];Exit[25]];
wrong=Join[o,<|"MixCPodd"->m3|>];
If[zeeF17Matrices[wrong]=!=$Failed,
 Print["F17_COMPLEX_JSON_SELFTEST_FAIL_BAD_SHAPE_ACCEPTED"];Exit[26]];
missing=KeyDrop[o,{"FSARAH"}];
If[zeeF17Matrices[missing]=!=$Failed,
 Print["F17_COMPLEX_JSON_SELFTEST_FAIL_MISSING_FZEE_ACCEPTED"];Exit[27]];
symbolic=Join[o,<|"Ye2SARAH"->{{unknownx,0,0},{0,0,0},{0,0,0}}|>];
If[zeeF17Matrices[symbolic]=!=$Failed,
 Print["F17_COMPLEX_JSON_SELFTEST_FAIL_SYMBOLIC_MATRIX_ACCEPTED"];Exit[28]];
Print["F17_COMPLEX_MATRIX_JSON_SELFTEST_PASS"];
Exit[0];
