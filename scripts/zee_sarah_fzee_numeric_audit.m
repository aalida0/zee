(* LEGACY standalone test, superseded by zee_sarah_integrated_lepton_validation.m.
   Independent complex numerical normalization of Zee f-induced vertices.
   SARAH 4.15.4 + Gate6 gamma fixture. E3 matching is NOT certified.
   Run: python3 scripts/zee_sarah_gate6_fixture.py
        math -script scripts/zee_sarah_fzee_numeric_audit.m *)
root=Directory[];
outDir=FileNameJoin[{root,"work","sarah_zee"}];
If[!DirectoryQ[outDir],CreateDirectory[outDir,CreateIntermediateDirectories->True]];
statusFile=FileNameJoin[{outDir,"fzee_numeric_status.txt"}];
setStatus[zeeStatus_String]:=(
 Export[statusFile,zeeStatus<>"\n","Text"];
 Print["ZEE_F_NUMERIC_STATUS ",zeeStatus]
);
setStatus["FZEE_COMPLEX_NUMERIC_NOT_VALIDATED"];
fixture=FileNameJoin[{outDir,"gate6_fixture.m"}];
If[!FileExistsQ[fixture],setStatus["FZEE_FIXTURE_MISSING"];Exit[2]];
sarahFile=FileNameJoin[{$HomeDirectory,".Mathematica","Applications",
 "SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[sarahFile],setStatus["SARAH_NOT_FOUND"];Exit[3]];
PrependTo[$Path,DirectoryName[sarahFile]];
loaded=CheckAbort[(Get[sarahFile];True),False];
If[!TrueQ[loaded]||!ValueQ[SA`Version],
 setStatus["SARAH_LOAD_FAILED"];Exit[4]];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],
 FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],
 setStatus["SARAH_START_FAILED"];Exit[5]];
Get[fixture];
If[!NumericQ[zeeGate6Beta]||!NumericQ[zeeGate6Gamma],
 setStatus["GATE6_ANGLES_MISSING"];Exit[6]];
(* Rows Goldstone,H1-,H2-, columns H1-doublet,H2-doublet,s-. *)
cb=N[Cos[zeeGate6Beta]];sb=N[Sin[zeeGate6Beta]];
cg=N[Cos[zeeGate6Gamma]];sg=N[Sin[zeeGate6Gamma]];
zp=N[{{cb,sb,0},{-sb*cg,cb*cg,sg},{sb*sg,-cb*sg,cg}}];
orth=Max[Abs[Flatten[zp.Transpose[zp]-IdentityMatrix[3]]]];
If[orth>1.*^-12,
 Print["FAIL MIXING_ORTHOGONAL ",InputForm[orth]];
 setStatus["MIXING_MATRIX_INVALID"];Exit[7]];
Print["ZEE_F_MIXING_SINGLET_H1 ",InputForm[zp[[2,3]]]];
Print["ZEE_F_MIXING_SINGLET_H2 ",InputForm[zp[[3,3]]]];

(* Check two independent complex antisymmetric f fixtures and a
   nontrivial unitary charged-lepton rotation. These are synthetic
   coupling tests, NOT points from the E3 neutrino fit. *)
makeF[f12_,f13_,f23_]:={
 {0,f12,f13},{-f12,0,f23},{-f13,-f23,0}
};
makeVe[theta_,phase_]:={
 {Cos[theta],Exp[I phase]*Sin[theta],0},
 {-Exp[-I phase]*Sin[theta],Cos[theta],0},
 {0,0,1}
};
cases={
 {"identity_rotation",makeF[0.002+0.003 I,-0.0007+0.001 I,
                           0.004-0.0012 I],IdentityMatrix[3]},
 {"complex_rotation",makeF[-0.006+0.001 I,0.002+0.004 I,
                           -0.001-0.003 I],makeVe[0.37,0.61]}
};
(* Extract SARAH amplitudes once. Explicit external generation labels
   eliminate ambiguity from generic gt1,gt2. *)
vertices={
 {"gauge12",{eL[{1}],vL[{2}],Sp},GaugeES,2,1},
 {"gauge21",{eL[{2}],vL[{1}],Sp},GaugeES,2,1},
 {"gauge11",{eL[{1}],vL[{1}],Sp},GaugeES,2,1},
 {"plus12_H1",{Fe[{1}],Fv[{2}],conj[Hm[{2}]]},EWSB,2,PL},
 {"plus21_H1",{Fe[{2}],Fv[{1}],conj[Hm[{2}]]},EWSB,2,PL},
 {"plus12_H2",{Fe[{1}],Fv[{2}],conj[Hm[{3}]]},EWSB,2,PL},
 {"minus12_H1",{bar[Fe[{1}]],bar[Fv[{2}]],Hm[{2}]},EWSB,3,PR},
 {"minus12_H2",{bar[Fe[{1}]],bar[Fv[{2}]],Hm[{3}]},EWSB,3,PR}
};
raw={};
Do[
 vtx=CheckAbort[SARAH`Vertex[spec[[2]],Eigenstates->spec[[3]]],$Aborted];
 If[vtx===$Aborted||!ListQ[vtx]||Length[vtx]<spec[[4]]||
    !ListQ[vtx[[spec[[4]]]]],
    Print["FAIL VERTEX_EXTRACTION ",spec[[1]]," ",InputForm[vtx]];
    setStatus["FZEE_VERTEX_EXTRACTION_FAILED"];Exit[8]];
 If[vtx[[spec[[4]],2]]=!=spec[[5]],
    Print["FAIL VERTEX_CHIRALITY ",spec[[1]],
     " observed=",InputForm[vtx]];
    setStatus["FZEE_CHIRAL_STRUCTURE_MISMATCH"];Exit[9]];
 (* An identically vanishing diagonal Zee vertex is expected to
    lose every literal Fzee occurrence after symbolic cancellation. *)
 If[FreeQ[vtx,Fzee] && spec[[1]]=!="gauge11",
    Print["FAIL FZEE_ABSENT ",spec[[1]]];
    setStatus["FZEE_NOT_IN_REQUIRED_VERTICES"];Exit[10]];
 AppendTo[raw,vtx[[spec[[4]],1]]],
 {spec,vertices}
];
Print["ZEE_F_NUMERIC_N_VERTICES ",Length[raw]];

(* Expand SARAH symbolic sums BEFORE substituting indexed matrices.
   Keep antisymmetry explicit: no UseSymmASymm toggle, no guessed
   symmetry replacements to make SARAH agree with expectations. *)
evaluate[expr_,fm_,vm_]:=Module[{x},
 x=expr //. HoldPattern[sum[j_,a_,b_,z_]]:>Sum[z,{j,a,b}];
 x=x/.{
    Fzee[i_Integer,j_Integer]:>fm[[i,j]],
    Ve[i_Integer,j_Integer]:>vm[[i,j]],
    ZP[i_Integer,j_Integer]:>zp[[i,j]]
   };
 x=x/.HoldPattern[conj[z_?NumericQ]]:>Conjugate[z];
 N[x]
];
(* Independent expectation from L_f=-(f_ij/2)L_i L_j s+ +hc:
   gauge eLi nuLj s+: i f_ij,
   mass state Fe_a Fv_b Hk+: i ZP[k,3] sum_j conj(Ve[a,j])*f[j,b],
   conjugate: i ZP[k,3] sum_j Ve[a,j]*conj(f[j,b]).
   This checks complex conjugation, antisymmetry and the factor two. *)
expectedValues[fm_,vm_]:=Module[{left12,left21,right12},
 left12=Sum[Conjugate[vm[[1,j]]]*fm[[j,2]],{j,1,3}];
 left21=Sum[Conjugate[vm[[2,j]]]*fm[[j,1]],{j,1,3}];
 right12=Sum[vm[[1,j]]*Conjugate[fm[[j,2]]],{j,1,3}];
 N[I*{fm[[1,2]],fm[[2,1]],fm[[1,1]],
      zp[[2,3]]*left12,zp[[2,3]]*left21,
      zp[[3,3]]*left12,zp[[2,3]]*right12,
      zp[[3,3]]*right12}]
];
logs={};
maxResidual=0.;
Do[
 label=case[[1]];
 fm=N[case[[2]]];vm=N[case[[3]]];
 If[Max[Abs[Flatten[fm+Transpose[fm]]]]>1.*^-13||
    Max[Abs[Diagonal[fm]]]>1.*^-13||
    Max[Abs[Flatten[vm.ConjugateTranspose[vm]-IdentityMatrix[3]]]]>1.*^-12,
   Print["FAIL INPUT_NOT_ANTISYMMETRIC_OR_UNITARY ",label];
   setStatus["FZEE_TEST_INPUT_INVALID"];Exit[11]];
 observed=evaluate[#,fm,vm]&/@raw;
 expected=expectedValues[fm,vm];
 If[!VectorQ[observed,NumericQ],
   Print["FAIL NONNUMERIC ",label," ",InputForm[observed]];
   setStatus["FZEE_NUMERIC_EVALUATION_FAILED"];Exit[12]];
 diffs=N[Abs[observed-expected]];
 Do[
   Print["ZEE_F_COMPLEX_RESULT ",label," ",vertices[[k,1]],
     " actual=",InputForm[observed[[k]]],
     " expected=",InputForm[expected[[k]]],
     " residual=",InputForm[diffs[[k]]]];
   AppendTo[logs,{label,vertices[[k,1]],observed[[k]],
                   expected[[k]],diffs[[k]]}],
   {k,Length[raw]}];
 maxResidual=Max[maxResidual,Max[diffs]],
 {case,cases}
];
Print["ZEE_F_COMPLEX_MAX_RESIDUAL ",InputForm[maxResidual]];
Export[FileNameJoin[{outDir,"fzee_numeric_results.txt"}],
 StringRiffle[Table[
 ToString[logs[[k,1]]]<>"/"<>ToString[logs[[k,2]]]<>
 " actual="<>ToString[InputForm[logs[[k,3]]]]<>
 " expected="<>ToString[InputForm[logs[[k,4]]]]<>
 " absres="<>ToString[InputForm[logs[[k,5]]]],
 {k,Length[logs]}],"\n"]<>"\n","Text"];
If[!NumericQ[maxResidual]||maxResidual>1.*^-11,
 setStatus["FZEE_COMPLEX_NUMERIC_MISMATCH"];Exit[13]];
setStatus["SARAH_ZEE_F_COMPLEX_VERTEX_NORMALIZATION_PASS_E3_UNMATCHED"];
Exit[0];
