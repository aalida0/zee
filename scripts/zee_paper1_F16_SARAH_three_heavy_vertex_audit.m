(* F16: independent SARAH 4.15.4 generator charged scalar and lepton tree
   widths for three EXACT F13 Zee complex source points. Not MadWidth.
   ZEE_F16_DIR=<transferred_F16_fixture_dir> math -script THIS.m *)
root=Directory[];dir=Environment["ZEE_F16_DIR"];
If[!StringQ[dir]||StringLength[dir]==0||!DirectoryQ[dir],
 Print["F16_FAIL_CLOSED_MISSING_ZEE_F16_DIR"];Exit[2]];
fixture=FileNameJoin[{dir,"F16_three_exact_F13_Zee_SARAH_charged_vertices.m"}];
If[!FileExistsQ[fixture],Print["F16_FAIL_MISSING_FIXTURE ",fixture];Exit[3]];
status=FileNameJoin[{dir,"F16_local_SARAH_vertex_status.txt"}];
report=FileNameJoin[{dir,"F16_local_SARAH_vertex_report.txt"}];log={};
finish[s_String,c_Integer]:=(
 Export[status,s<>"\n","Text"];
 Export[report,StringRiffle[log,"\n"]<>"\n","Text"];
 Print["F16_SARAH_STATUS ",s];Exit[c]);
Get[fixture];
If[!ListQ[zeeF16Cases]||Length[zeeF16Cases]=!=3||
    !And@@(AssociationQ/@zeeF16Cases),
 finish["F16_INVALID_EXACT_THREE_SOURCE_FIXTURE",4]];
sfile=FileNameJoin[{$HomeDirectory,".Mathematica","Applications",
   "SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[sfile],finish["F16_SARAH_4_15_4_MISSING",5]];
PrependTo[$Path,DirectoryName[sfile]];
CheckAbort[Get[sfile],finish["F16_SARAH_LOAD_FAILED",7]];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],
 FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],
 finish["F16_SARAH_START_FAILED",8]];
Print["F16_SARAH_INDEPENDENT_START_OK"];

getS[v_,what_String]:=Module[{c},
 c=If[ListQ[v]&&Length[v]>=2,
   Cases[Rest[v],{a_,b_}:>a,{1}],{}];
 If[Length[c]!=1,
   Print["F16_BAD_SCALAR_VERTEX ",what," ",InputForm[v]];
   Return[$Failed]];
 c[[1]]];
getL[fields_,chir_,tag_]:=Module[{v,c},
 v=SARAH`Vertex[fields,Eigenstates->EWSB];
 c=If[ListQ[v]&&Length[v]>=2,
   Cases[Rest[v],{e_,lor_}/;lor===chir:>e,{1}],{}];
 If[Length[c]!=1,
    Print["F16_BAD_LEPTON_VERTEX ",tag," ",InputForm[v]];
    Return[$Failed]];
 c[[1]]];
cz=getS[SARAH`Vertex[{conj[Hm[{2}]],Hm[{3}],VZ},
                    Eigenstates->EWSB],"Z H1 H2"];
cp=getS[SARAH`Vertex[{conj[Hm[{2}]],Hm[{3}],VP},
                    Eigenstates->EWSB],"photon H1 H2"];
ch=getS[SARAH`Vertex[{conj[Hm[{2}]],Hm[{3}],hh[{1}]},
                    Eigenstates->EWSB],"h H1 H2"];
cH=getS[SARAH`Vertex[{conj[Hm[{2}]],Hm[{3}],hh[{2}]},
                    Eigenstates->EWSB],"H H1 H2"];
If[MemberQ[{cz,cp,ch,cH},$Failed],
 finish["F16_MISSING_SARAH_CHARGED_BOSONIC_VERTEX",9]];
massRaws={SARAH`MassMatrix[hh],SARAH`MassMatrix[Ah],
          SARAH`MassMatrix[Hm]};
massLepton=SARAH`MassMatrix[Fe];
queries=Flatten[Table[
 With[{a=i,b=j,c=k},{
  {a,b,c,"f",getL[{Fe[{a}],Fv[{b}],conj[Hm[{c}]]},PL,"f"]},
  {a,b,c,"Y",getL[{bar[Fe[{a}]],Fv[{b}],Hm[{c}]},PL,"Y"]}
 }],{i,1,3},{j,1,3},{k,{2,3}}],3];
If[Length[queries]!=36||MemberQ[queries,$Failed,Infinity],
 finish["F16_36_SARAH_LEPTON_VERTEX_EXTRACTION_FAILED",10]];

reduce[expr_,o_]:=Module[{z=expr,ss,sw,cw,g,gt},
 sw=Sqrt[0.23122];cw=Sqrt[1.-0.23122];
 g=2*91.1876*cw/o["V"];gt=g*sw/cw;
 z=z //. HoldPattern[sum[n_,1,3,t_]]:>Total[Table[t,{n,1,3}]];
 ss={
  ZP[i_Integer,j_Integer]:>o["MixCharged"][[i,j]],
  ZH[i_Integer,j_Integer]:>o["MixCPeven"][[i,j]],
  ZA[i_Integer,j_Integer]:>o["MixCPodd"][[i,j]],
  Fzee[i_Integer,j_Integer]:>o["FSARAH"][[i,j]],
  Ye[i_Integer,j_Integer]:>o["YeSARAH"][[i,j]],
  Ye2[i_Integer,j_Integer]:>o["Ye2SARAH"][[i,j]],
  Ue[i_Integer,j_Integer]:>KroneckerDelta[i,j],
  Ve[i_Integer,j_Integer]:>KroneckerDelta[i,j],
  g2->g,g1->gt,ThetaW->ArcSin[sw],
  HoldPattern[SARAH`RXi[___]]:>0
 };
 z=N[z/.o["ScalarRules"]/.ss];
 N[z/.HoldPattern[conj[n_?NumericQ]]:>Conjugate[n]]
];
vecW[M_,m_,V_,g_]:=If[M<=m+V,0.,
 N[Abs[g]^2*((M^2-(m+V)^2)*(M^2-(m-V)^2))^(3/2)/
        (16 Pi M^3 V^2)]];
scaW[M_,m_,h_,g_]:=If[M<=m+h,0.,
 N[Abs[g]^2*Sqrt[(M^2-(m+h)^2)*(M^2-(m-h)^2)]/
        (16 Pi M^3)]];
rel[a_,b_,scale_:1.*^-10]:=N[Abs[a-b]/Max[Abs[b],scale]];
fails={};
Do[
 Module[{id=o["ID"],mm,gauge,photon,hc,Hc,msource,
         mbos,lepMass,lepDiff,lepW,relL,relB,mErr,k,m,el,j,
         pair,weight,sec=AbsoluteTime[]},
 Print["F16_CASE ",id];
 mm=reduce[#,o]&/@massRaws;
 msource={o["ExpectedHH"],o["ExpectedAh"],o["ExpectedHm"]};
 If[!And@@(MatrixQ[#,NumericQ]&/@mm),
   AppendTo[fails,id<>"/non_numeric_scalar_mass"];
   Print["F16_NONNUMERIC_MASS ",InputForm[mm]];Continue[]];
 mErr=Max[Abs[Flatten[mm-msource]]];
 {gauge,photon,hc,Hc}=reduce[#,o]&/@{cz,cp,ch,cH};
 If[!And@@(NumericQ/@{gauge,photon,hc,Hc}),
   AppendTo[fails,id<>"/non_numeric_scalar_vertex"];
   Print["F16_NONNUMERIC_VERTEX ",
     InputForm[{gauge,photon,hc,Hc}]];Continue[]];
 mbos={
   vecW[o["M2"],o["M1"],91.1876,gauge],
   scaW[o["M2"],o["M1"],125.,hc],
   scaW[o["M2"],o["M1"],o["MH"],Hc]};
 relB=Max[Join[{
    rel[Abs[gauge],o["ExpectedZ12"],1.*^-10],
    rel[Abs[hc],Abs[o["ExpectedH1h"]],1.*^-9],
    rel[Abs[Hc],Abs[o["ExpectedH1H"]],1.*^-9],
    Abs[photon]},
    Table[rel[mbos[[k]],o["ExpectedWidths"][[k]],1.*^-10],
    {k,1,3}]]];
 lepMass=reduce[massLepton,o];
 If[!MatrixQ[lepMass,NumericQ],
    AppendTo[fails,id<>"/non_numeric_lepton_mass"];Continue[]];
 lepDiff=Max[Abs[Flatten[lepMass-
    DiagonalMatrix[o["LeptonMasses"]]]]];
 lepW=Table[
   k=state;m=If[k==2,o["M1"],o["M2"]];weight=0.;
   Do[
    pair=Select[queries,#[[1]]===el&&#[[2]]===j&&#[[3]]===k&];
    If[Length[pair]!=2,
      AppendTo[fails,id<>"/missing_lepton_chirality"];Continue[]];
    weight+=Total[(Abs[reduce[#[[5]],o]]^2&)/@pair],
    {j,1,3}];
   N[m/(16 Pi)*weight*(1-o["LeptonMasses"][[el]]^2/m^2)^2],
   {el,1,3},{state,{2,3}}];
 If[!MatrixQ[lepW,NumericQ],
   AppendTo[fails,id<>"/non_numeric_lepton_width"];Continue[]];
 relL=Max[Abs[Flatten[lepW-o["LeptonicWidths"]]]/
    Map[Max[#,1.*^-14]&,Flatten[o["LeptonicWidths"]]]];
 Print["F16_MASS_MAX_ABS_GEV2 ",id," ",InputForm[mErr]];
 Print["F16_BOSON_WIDTH_MAX_REL ",id," ",InputForm[relB]];
 Print["F16_LEPTON_MASS_MAX_ABS_GEV ",id," ",InputForm[lepDiff]];
 Print["F16_LEPTON_WIDTH_MAX_REL ",id," ",InputForm[relL]];
 Print["F16_CASE_SECONDS ",id," ",AbsoluteTime[]-sec];
 AppendTo[log,id<>" massGeV2="<>ToString[InputForm[mErr]]<>
    " bosRel="<>ToString[InputForm[relB]]<>
    " lepRel="<>ToString[InputForm[relL]]<>
    " lepMassGeV="<>ToString[InputForm[lepDiff]]];
 If[mErr>1.*^-5||relB>1.*^-7||relL>5.*^-7||lepDiff>1.*^-9,
    AppendTo[fails,id<>"/vertex_or_mass_mismatch"]],
 {o,zeeF16Cases}];
If[Length[fails]>0,
 Print["F16_SARAH_FAILURES ",InputForm[fails]];
 finish["F16_THREE_HEAVY_SARAH_VERTEX_MISMATCH_NOT_COMPLETE_WIDTH",11]];
finish["F16_THREE_HEAVY_SARAH_MASS_GAUGE_CUBIC_COMPLEX_LEPTON_PASS_NOT_MADWIDTH",0];
