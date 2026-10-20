(* ONE consolidated SARAH 4.15.4 tree-level Zee lepton validation.
   Covers complex antisymmetric f, general Ye/Ye2, lepton masses,
   nontrivial unitary charged-lepton rotations, neutral and charged
   scalar vertices, both chiralities, complex HC, Goldstone/mixing.
   Synthetic fixtures; NOT E3 neutrino loop/LFV matching or exclusions.
   Run once from ~/zee after gate6_fixture.py. *)
root=Directory[];
out=FileNameJoin[{root,"work","sarah_zee"}];
If[!DirectoryQ[out],CreateDirectory[out,CreateIntermediateDirectories->True]];
statusPath=FileNameJoin[{out,"integrated_lepton_status.txt"}];
detailsPath=FileNameJoin[{out,"integrated_lepton_residuals.txt"}];
setGate[zeeGate_String]:=(
 Export[statusPath,zeeGate<>"\n","Text"];
 Print["ZEE_INTEGRATED_STATUS ",zeeGate]
);
setGate["INTEGRATED_TREE_LEPTON_NOT_VALIDATED"];
fixture=FileNameJoin[{out,"gate6_fixture.m"}];
If[!FileExistsQ[fixture],setGate["GATE6_FIXTURE_MISSING"];Exit[2]];
sarahSource=FileNameJoin[{$HomeDirectory,".Mathematica","Applications",
 "SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[sarahSource],setGate["SARAH_MISSING"];Exit[3]];
PrependTo[$Path,DirectoryName[sarahSource]];
loaded=CheckAbort[(Get[sarahSource];True),False];
If[!TrueQ[loaded]||!ValueQ[SA`Version],
 setGate["SARAH_LOAD_FAILED"];Exit[4]];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],
 FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],
 setGate["ZEE_MODEL_START_FAILED"];Exit[5]];
Get[fixture];
If[!And@@(NumericQ/@{zeeGate6Beta,zeeGate6Gamma,zeeGate6Alpha}),
 setGate["GATE6_MIXING_ANGLES_MISSING"];Exit[6]];
symMeta=Select[ParameterDefinitions,#[[1]]===Fzee&];
If[Length[symMeta]!=1||FreeQ[symMeta,Symmetry->AntiSymmetric],
 Print["FAIL FZEE_ANTISYMMETRIC_METADATA ",InputForm[symMeta]];
 setGate["FZEE_SYMMETRY_METADATA_FAILED"];Exit[7]];
Print["ZEE_INTEGRATED_SARAH_VERSION ",SA`Version];
Print["ZEE_INTEGRATED_SYMMETRY ",InputForm[symMeta]];
Print["ZEE_INTEGRATED_NOTE GaugeES diagonal f vertex is identically zero; no literal Fzee required"];

beta=zeeGate6Beta; gamma=zeeGate6Gamma; alpha=zeeGate6Alpha;
zp=N[{{Cos[beta],Sin[beta],0},
 {-Sin[beta]*Cos[gamma],Cos[beta]*Cos[gamma],Sin[gamma]},
 {Sin[beta]*Sin[gamma],-Cos[beta]*Sin[gamma],Cos[gamma]}}];
zh=N[{{Cos[alpha],Sin[alpha]},{-Sin[alpha],Cos[alpha]}}];
v1val=N[v1/.zeeGate6Rules];
v2val=N[v2/.zeeGate6Rules];
If[!And@@(NumericQ/@{v1val,v2val})||v1val<=0||v2val<=0,
 setGate["GATE6_VEV_INVALID"];Exit[8]];
zpOrth=Max[Abs[Flatten[zp.Transpose[zp]-IdentityMatrix[3]]]];
zhOrth=Max[Abs[Flatten[zh.Transpose[zh]-IdentityMatrix[2]]]];
massCharged=N[SARAH`MassMatrix[Hm] /. zeeGate6Rules];
massNeutral=N[SARAH`MassMatrix[hh] /. zeeGate6Rules];
If[!MatrixQ[massCharged,NumericQ]||!MatrixQ[massNeutral,NumericQ],
 setGate["SCALAR_MASSES_NOT_NUMERIC"];Exit[9]];
chargedDiag=Max[Abs[Flatten[zp.massCharged.Transpose[zp]-
 DiagonalMatrix[{0.,300.^2,700.^2}]]]];
neutralDiag=Max[Abs[Flatten[zh.massNeutral.Transpose[zh]-
 DiagonalMatrix[{125.^2,580.7^2}]]]];
Print["ZEE_INTEGRATED_SCALAR_MIX_RESIDS ",
 InputForm[{zpOrth,zhOrth,chargedDiag,neutralDiag}]];
If[Max[{zpOrth,zhOrth,chargedDiag,neutralDiag}]>1.*^-5,
 setGate["GATE6_SCALAR_MIXING_FAILED"];Exit[10]];

(* Two distinct complex f/Y/rotation fixtures. Full charged-lepton
   Yukawa Ye is derived to satisfy the chosen physical masses after
   BOTH left and right rotations; Ye2 is independent and complex.
   No E3 fitting/physical point claim is attached to these data. *)
makeF[a_,b_,c_]:={{0,a,b},{-a,0,c},{-b,-c,0}};
rot[theta_,phi_]:={{Cos[theta],Exp[I phi]*Sin[theta],0},
 {-Exp[-I phi]*Sin[theta],Cos[theta],0},{0,0,1}};
masses={0.00051099895,0.1056583755,1.77686};
configs={
 {"identity",makeF[0.002+0.003 I,-0.0007+0.001 I,0.004-0.0012 I],
  IdentityMatrix[3],IdentityMatrix[3],
  {{0.0005+0.0004 I,0.0012-0.0002 I,-0.0008+0.0003 I},
   {-0.0007+0.0001 I,0.0020-0.0007 I,0.0008+0.0006 I},
   {0.0003-0.0005 I,-0.0011+0.0009 I,0.0030+0.0002 I}}},
 {"rotated",makeF[-0.006+0.001 I,0.002+0.004 I,-0.001-0.003 I],
  rot[0.37,0.61],rot[0.23,-0.79],
  {{-0.0003+0.0009 I,0.0018+0.0006 I,0.0005-0.0012 I},
   {0.0011-0.0002 I,-0.0004+0.0004 I,0.0009+0.0003 I},
   {-0.0008+0.0001 I,0.0006-0.0007 I,0.0016-0.0005 I}}}
};

(* The first index of SARAH's Ye and Ye2 is right-handed; second
   is left-handed, since the raw matrix M_ij =
   (v1*Ye[j,i]+v2*Ye2[j,i])/sqrt2.
   For arbitrary unitary Ve(left), Ue(right), use the convention
   Conjugate[Ve]. M . ConjugateTranspose[Ue] = diag(masses). *)
makePhysicsCase[cfg_]:=Module[{fmat,vmat,umat,y2,ymat,mweak},
 fmat=N[cfg[[2]]];vmat=N[cfg[[3]]];umat=N[cfg[[4]]];
 y2=N[cfg[[5]]];
 mweak=Transpose[vmat].DiagonalMatrix[masses].umat;
 ymat=N[(Sqrt[2]*Transpose[mweak]-v2val*y2)/v1val];
 {cfg[[1]],fmat,vmat,umat,ymat,y2,mweak}
];
physicsCases=makePhysicsCase/@configs;

(* SARAH's sum[a,i,j,expr] is an explicit finite flavor sum.
   Expand it before substituting indexed matrices; never impose
   antisymmetry by rewriting SARAH's generated vertex itself. *)
evaluate[expr_,fmat_,vmat_,umat_,ymat_,y2_]:=Module[{x},
 x=expr //. HoldPattern[sum[j_,lo_Integer,hi_Integer,z_]]:>
     Total[Table[z,{j,lo,hi}]];
 x=x/.{
   Fzee[i_Integer,j_Integer]:>fmat[[i,j]],
   Ve[i_Integer,j_Integer]:>vmat[[i,j]],
   Ue[i_Integer,j_Integer]:>umat[[i,j]],
   Ye[i_Integer,j_Integer]:>ymat[[i,j]],
   Ye2[i_Integer,j_Integer]:>y2[[i,j]],
   ZP[i_Integer,j_Integer]:>zp[[i,j]],
   ZH[i_Integer,j_Integer]:>zh[[i,j]],
   v1->v1val,v2->v2val
 };
 N[x/.HoldPattern[conj[z_?NumericQ]]:>Conjugate[z]]
];

(* Get a specific chirality rather than depending on the number of
   terms of Vertex[]; a zero can contain no Fzee (gauge11).
   All nonzero vertices must carry their source parameter family. *)
vertexCoeff[fields_List,basis_,chir_,required_] := Module[{vtx,parts},
 vtx=CheckAbort[SARAH`Vertex[fields,Eigenstates->basis],$Aborted];
 If[vtx===$Aborted||!ListQ[vtx]||Length[vtx]<2,
  Print["FAIL VERTEX_RETURN ",InputForm[fields]," ",InputForm[vtx]];
  Return[$Failed]];
 parts=Cases[Rest[vtx],{co_,la_}/;la===chir:>co,{1}];
 If[Length[parts]!=1,
  Print["FAIL VERTEX_STRUCTURE ",InputForm[fields],
   " chir=",InputForm[chir]," value=",InputForm[vtx]];
  Return[$Failed]];
 If[required=!=None && FreeQ[parts[[1]],required],
  Print["FAIL SOURCE_PARAMETER_ABSENT ",InputForm[fields],
    " symbol=",InputForm[required]];
  Return[$Failed]];
 parts[[1]]
];
(* Query all needed distinct component vertices ONCE. *)
pairs={{1,2},{2,1},{1,1},{2,3}};
queries={};
addQuery[name_String,fields_List,basis_,chir_,required_,expectedFn_]:=
 AppendTo[queries,{name,fields,basis,chir,required,expectedFn}];

Do[
 a=pp[[1]];b=pp[[2]];
 addQuery["f_gauge_"<>ToString[a]<>ToString[b],
  {eL[{a}],vL[{b}],Sp},GaugeES,1,
  If[a===b,None,Fzee],
  Function[{fmat,vmat,umat,ymat,y2},
   I*fmat[[a,b]]]],
 {pp,{{1,2},{2,1},{1,1},{2,3}}}
];
Do[
 a=pp[[1]];b=pp[[2]];
 Do[
  k=kk;
  addQuery["f_plus_"<>ToString[a]<>ToString[b]<>"_"<>ToString[k],
    {Fe[{a}],Fv[{b}],conj[Hm[{k}]]},EWSB,PL,
    If[a===b,None,Fzee],
    Function[{fmat,vmat,umat,ymat,y2},
     I*zp[[k,3]]*Sum[Conjugate[vmat[[a,j]]]*fmat[[j,b]],
       {j,1,3}]]];
  addQuery["f_hc_"<>ToString[a]<>ToString[b]<>"_"<>ToString[k],
    {bar[Fe[{a}]],bar[Fv[{b}]],Hm[{k}]},EWSB,PR,
    If[a===b,None,Fzee],
    Function[{fmat,vmat,umat,ymat,y2},
     I*zp[[k,3]]*Sum[vmat[[a,j]]*Conjugate[fmat[[j,b]]],
       {j,1,3}]]];
  addQuery["Y_hminus_"<>ToString[a]<>ToString[b]<>"_"<>ToString[k],
    {bar[Fe[{a}]],Fv[{b}],Hm[{k}]},EWSB,PL,Ye2,
    Function[{fmat,vmat,umat,ymat,y2},
     -I*Sum[Conjugate[umat[[a,j]]]*
      (zp[[k,1]]*ymat[[j,b]]+zp[[k,2]]*y2[[j,b]]),
       {j,1,3}]]];
  addQuery["Y_hplus_"<>ToString[a]<>ToString[b]<>"_"<>ToString[k],
    {bar[Fv[{b}]],Fe[{a}],conj[Hm[{k}]]},EWSB,PR,Ye2,
    Function[{fmat,vmat,umat,ymat,y2},
     -I*Sum[umat[[a,j]]*
       (zp[[k,1]]*Conjugate[ymat[[j,b]]]+
        zp[[k,2]]*Conjugate[y2[[j,b]]]),
       {j,1,3}]]],
  {kk,{2,3}}];
 Do[
  n=nn;
  addQuery["Y_neutralPL_"<>ToString[a]<>ToString[b]<>"_"<>ToString[n],
    {bar[Fe[{a}]],Fe[{b}],hh[{n}]},EWSB,PL,Ye2,
    Function[{fmat,vmat,umat,ymat,y2},
      -I/Sqrt[2]*Sum[
         Conjugate[umat[[a,r]]]*Conjugate[vmat[[b,l]]]*
         (zh[[n,1]]*ymat[[r,l]]+zh[[n,2]]*y2[[r,l]]),
         {r,1,3},{l,1,3}]]];
  addQuery["Y_neutralPR_"<>ToString[a]<>ToString[b]<>"_"<>ToString[n],
    {bar[Fe[{a}]],Fe[{b}],hh[{n}]},EWSB,PR,Ye2,
    Function[{fmat,vmat,umat,ymat,y2},
      -I/Sqrt[2]*Sum[
         umat[[b,r]]*vmat[[a,l]]*
         (zh[[n,1]]*Conjugate[ymat[[r,l]]]+
          zh[[n,2]]*Conjugate[y2[[r,l]]]),
         {r,1,3},{l,1,3}]]],
  {nn,{1,2}}],
 {pp,pairs}
];
Print["ZEE_INTEGRATED_VERTEX_QUERIES ",Length[queries]];
raw=vertexCoeff[#[[2]],#[[3]],#[[4]],#[[5]]]&/@queries;
If[MemberQ[raw,$Failed],
 setGate["LEPTON_VERTEX_EXTRACTION_OR_CHIRALITY_FAILED"];Exit[11]];
massRaw=SARAH`MassMatrix[Fe];
Print["ZEE_INTEGRATED_MASS_MATRIX_SHAPE ",InputForm[Dimensions[massRaw]]];
If[Dimensions[massRaw]=!={3,3},
 setGate["LEPTON_MASS_MATRIX_SHAPE_FAILED"];Exit[12]];

log={};sectorMax=<||>;maxAll=0.;failed=False;
record[caseName_,name_,observed_,wanted_]:=Module[{err,sector},
 If[!NumericQ[observed]||!NumericQ[wanted],
  Print["FAIL NONNUMERIC ",caseName,"/",name,
    " observed=",InputForm[observed],
    " expected=",InputForm[wanted]];
  failed=True;Return[]];
 err=N[Abs[observed-wanted]];
 sector=First[StringSplit[name,"_"]];
 sectorMax[sector]=Max[Lookup[sectorMax,sector,0.],err];
 maxAll=Max[maxAll,err];
 AppendTo[log,{caseName,name,observed,wanted,err}];
 If[err>1.*^-10,
  Print["FAIL VERTEX_RESIDUAL ",caseName,"/",name,
    " abs=",InputForm[err]];failed=True]
];
Do[
 cfg=physicsCases[[ix]];
 label=cfg[[1]];fm=cfg[[2]];vm=cfg[[3]];um=cfg[[4]];
 yy=cfg[[5]];y2=cfg[[6]];mweak=cfg[[7]];
 fSym=Max[Abs[Flatten[fm+Transpose[fm]]]];
 fDiag=Max[Abs[Diagonal[fm]]];
 vUnit=Max[Abs[Flatten[vm.ConjugateTranspose[vm]-IdentityMatrix[3]]]];
 uUnit=Max[Abs[Flatten[um.ConjugateTranspose[um]-IdentityMatrix[3]]]];
 computedM=evaluate[massRaw,fm,vm,um,yy,y2];
 If[!MatrixQ[computedM,NumericQ],
  Print["FAIL LEPTON_MASS_NONNUMERIC ",label,
   " ",InputForm[computedM]];
  setGate["LEPTON_MASS_SUBSTITUTION_FAILED"];Exit[13]];
 mSource=Max[Abs[Flatten[computedM-mweak]]];
 mPhysical=Max[Abs[Flatten[
   Conjugate[vm].computedM.ConjugateTranspose[um]-
   DiagonalMatrix[masses]]]];
 (* Independent alignment identity: the v-directed neutral scalar
    has flavor-diagonal SM mass-proportional lepton couplings. *)
 aligned=Conjugate[um].
   ((v1val*yy+v2val*y2)/Sqrt[2]).
   ConjugateTranspose[vm];
 alignedResid=Max[Abs[Flatten[aligned-DiagonalMatrix[masses]]]];
 Print["ZEE_INTEGRATED_CASE ",label,
  " f_antisym=",InputForm[fSym],
  " f_diag=",InputForm[fDiag],
  " Ve_unitarity=",InputForm[vUnit],
  " Ue_unitarity=",InputForm[uUnit],
  " mass_source=",InputForm[mSource],
  " mass_diag=",InputForm[mPhysical],
  " aligned_mass_Y=",InputForm[alignedResid]];
 If[Max[{fSym,fDiag,vUnit,uUnit,mSource,mPhysical,alignedResid}]>1.*^-9,
  setGate["LEPTON_FLAVOR_INPUT_OR_MASS_CLOSURE_FAILED"];Exit[14]];
 Do[
  measured=evaluate[raw[[qi]],fm,vm,um,yy,y2];
  want=N[queries[[qi,6]][fm,vm,um,yy,y2]];
  record[label,queries[[qi,1]],measured,want],
  {qi,Length[queries]}],
 {ix,Length[physicsCases]}
];
Print["ZEE_INTEGRATED_N_COMPARISONS ",Length[log]];
Print["ZEE_INTEGRATED_MAX_RESIDUAL ",InputForm[maxAll]];
Print["ZEE_INTEGRATED_SECTOR_MAX_RESIDUALS ",InputForm[sectorMax]];
Export[detailsPath,StringRiffle[
 Table[
 ToString[log[[ix,1]]]<>"/"<>ToString[log[[ix,2]]]<>
 " actual="<>ToString[InputForm[log[[ix,3]]]]<>
 " expected="<>ToString[InputForm[log[[ix,4]]]]<>
 " absres="<>ToString[InputForm[log[[ix,5]]]],
 {ix,Length[log]}],"\n"]<>"\n","Text"];
If[failed||Length[log]=!=Length[queries]*Length[physicsCases]||
   maxAll>1.*^-10,
 Print["ZEE_INTEGRATED_DIAGNOSTIC_FILE ",detailsPath];
 setGate["INTEGRATED_TREE_LEPTON_COMPLEX_MISMATCH"];Exit[15]];
setGate["SARAH_ZEE_INTEGRATED_TREE_LEPTON_COMPLEX_PASS_E3_LOOP_UNMATCHED"];
Exit[0];
