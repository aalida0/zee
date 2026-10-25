(* F16 real numerical width residual verifier. All 3x2 family x charged
   scalar entries must evaluate to real, finite, non-negative numbers.
   The exact F13 Mathematica fixture encodes widths as "real + 0 I".
   A bare Max[complex,real] leaves an unevaluated symbolic expression;
   that formerly allowed a false PASS in the outer audit.

   This module returns $Failed for symbolic, complex-imaginary, negative,
   nonfinite, or wrong-shape data. NEVER silently discard a nonzero
   imaginary width. Abs[reference] is used for the denominator to avoid
   ordering Max over a complex value even when its imaginary part is 0.
*)
zeeF16WidthResidualStatus="F16_STRICT_REAL_COMPLEX_WIDTH_RESIDUAL_GUARD";
zeeF16RelativeLeptonWidthResidual[computed_,source_] :=
 Module[{aa=N[computed],bb=N[source],ar,br,diff,rr,
         toleranceImag=1.*^-12,floor=1.*^-14},
  If[!MatrixQ[aa,NumericQ]||!MatrixQ[bb,NumericQ]||
     Dimensions[aa]=!={3,2}||Dimensions[bb]=!={3,2},
     Return[$Failed]];
  If[!TrueQ[Max[Abs[Flatten[Im[aa]]]]<=toleranceImag]||
     !TrueQ[Max[Abs[Flatten[Im[bb]]]]<=toleranceImag],
     Return[$Failed]];
  ar=Re[aa];br=Re[bb];
  If[!MatrixQ[ar,NumericQ]||!MatrixQ[br,NumericQ]||
     !TrueQ[Min[Flatten[ar]]>=-floor]||
     !TrueQ[Min[Flatten[br]]>=-floor],
     Return[$Failed]];
  diff=MapThread[
    Abs[#1-#2]/Max[Abs[#2],floor]&,
    {ar,br},2];
  If[!MatrixQ[diff,NumericQ]||Dimensions[diff]=!={3,2}||
     !TrueQ[Min[Flatten[diff]]>=0],
     Return[$Failed]];
  rr=N[Max[Flatten[diff]]];
  If[!NumericQ[rr]||!TrueQ[Im[rr]==0]||
     !TrueQ[0<=rr<Infinity],Return[$Failed]];
  rr
 ];
