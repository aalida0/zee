(* F17 exact F13 three-Zee-case complex matrix serialization helpers.
   Isolated from the main source exporter so the SAME Wolfram functions
   are tested by a real Mathematica-kernel preflight. No SARAH required. *)
zeeF17MatrixJSONStatus="F17_EXACT_7_COMPLEX_MATRIX_NUMERIC_JSON_PAIRS";
zeeF17Names={"FSARAH","YeSARAH","Ye2SARAH","YChen",
             "MixCharged","MixCPeven","MixCPodd"};
zeeF17Dims={{3,3},{3,3},{3,3},{3,3},{3,3},{2,2},{2,2}};
zeeF17Pair[z_?NumericQ]:={N[Re[z]],N[Im[z]]};
zeeF17GetMat[o_Association,name_String,dims_List]:=
 Module[{a=Lookup[o,name,Missing["AbsentMatrix"]],res},
  If[!MatrixQ[a,NumericQ]||Dimensions[a]=!=dims,
   Print["F17_BAD_MATRIX ",Lookup[o,"ID","NO_ID"]," ",name,
         " ",InputForm[a]];
   Return[$Failed]];
  res=Map[zeeF17Pair,a,{2}];
  If[!ArrayQ[res,3,NumericQ]||
     Dimensions[res]=!=Append[dims,2],
     Print["F17_INVALID_COMPLEX_RE_IM_ENCODING ",name];
     Return[$Failed]];
  res
 ];
zeeF17Matrices[o_Association]:=
 Module[{mat},
  mat=AssociationThread[zeeF17Names,
    Table[zeeF17GetMat[o,zeeF17Names[[j]],zeeF17Dims[[j]]],
     {j,Length[zeeF17Names]}]];
  If[Length[mat]=!=Length[zeeF17Names]||
     MemberQ[Values[mat],$Failed]||
     !And@@Table[
       ArrayQ[mat[zeeF17Names[[j]]],3,NumericQ]&&
       Dimensions[mat[zeeF17Names[[j]]]]===
          Append[zeeF17Dims[[j]],2],
       {j,Length[zeeF17Names]}],
   Print["F17_FAIL_CLOSED_COMPLEX_MATRIX_NUMERIC_SHAPE ",
     Lookup[o,"ID","NO_ID"]];
   Return[$Failed]];
  mat
 ];
