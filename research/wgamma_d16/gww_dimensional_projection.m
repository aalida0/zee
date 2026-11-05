(* Native GWW open line; FeynCalc Tdec covariance, no 4D gamma trace. *)
$FeynCalcStartupMessages=False;
fc=Environment["D16_FEYNCALC_ROOT"];out=Environment["D16_OUTPUT_DIR"];
If[!StringQ[fc]||!DirectoryQ[fc]||!StringQ[out],Exit[2]];
Get[FileNameJoin[{fc,"FeynCalc.m"}]];
If[$FeynCalcVersion!="10.2.1",Exit[2]];
DataType[t,FCVariable]=True;DataType[u,FCVariable]=True;
num=GAD[mu].GSD[t p-l].GSD[l+r].GSD[t p-r];
num=DiracSimplify[ExpandScalarProduct[DiracGammaExpand[num]],DiracSubstitute67->True];
num=ExpandScalarProduct[MomentumExpand[num]];
n0=DiracSimplify[num/.{t->0,u->0}];
np=DiracSimplify[D[num,t]/.{t->0,u->0}];
nq=DiracSimplify[D[num,u]/.{t->0,u->0}];
avg[expr_]:=Module[{terms,one},
terms=List@@Expand[Uncontract[expr,l,r,Pair->{p,q}]];
one[term_]:=Module[{slots,factors,dec},
 slots=Cases[term,Pair[LorentzIndex[i_,D],Momentum[k:(l|r),D]]:>{k,i},Infinity];
 If[slots==={},Return[term]];
 factors=Times@@(FCI[FVD[#[[1]],#[[2]]]]&/@slots);
 dec=FCI[Tdec[slots,{},List->False]];
 DiracSimplify[Cancel[term/factors]dec]];
Total[one/@terms]];
rep=Thread[FCI[{SPD[l],SPD[r],SPD[l,r]}]->{x,y,z}];
wp=avg[np+2(SPD[l,p]/x+SPD[r,p]/y)n0];
wq=avg[nq+2 SPD[l,q]/(x-mw^2)n0];
wp=FCI[wp]/.rep;wq=FCI[wq]/.rep;
rules={FCI[GAD[mu].GSD[p]]->ap,FCI[GSD[p].GAD[mu]]->bp,FCI[FVD[p,mu]]->cp,
FCI[GAD[mu].GSD[q]]->aq,FCI[GSD[q].GAD[mu]]->bq,FCI[FVD[q,mu]]->cq};
polys=Factor[{wp,wq}/.rules];
dip=Factor[Coefficient[polys[[1]],cp]/2+Coefficient[polys[[1]],bp]+Coefficient[polys[[2]],bq]-Coefficient[polys[[2]],aq]];
If[!FreeQ[{polys,dip},Pair|DiracGamma|Derivative],Exit[2]];
Export[FileNameJoin[{out,"gww_projection.json"}],<|
 "FeynCalc"->$FeynCalcVersion,"Wolfram"->$Version,
 "polynomial_basis"->{"ap=gamma_mu slash_p","bp=slash_p gamma_mu","cp=p_mu","aq=gamma_mu slash_q","bq=slash_q gamma_mu","cq=q_mu"},
 "polynomials"->(ToString[#,InputForm]&/@polys),
 "dipole_numerator"->ToString[dip,InputForm],
 "scope"->"TOPOLOGY_ONLY; xiW=1; GWW, scalar before W currents; leading external degree; not a physical Wilson"|>,"RawJSON"];
Print["D16_GWW_OPEN_DIRAC_REDUCED"];
Quit[];
