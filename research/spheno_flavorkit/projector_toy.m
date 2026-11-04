BeginPackage["LoopTools`"]
{bb0,bb1,cc0,cc00,cc1,cc2,cc12,cc22,cc11,bb1,dd0,dd00};
EndPackage[]

(* Load in a fresh kernel with D15Local set to the absolute local/ directory. *)
Get[FileNameJoin[{D15Local,"FeynArts-3.9","FeynArts.m"}]];
Get[FileNameJoin[{D15Local,"FormCalc-7.5","FormCalc.m"}]];
Get[FileNameJoin[{D15Local,"PreSARAH-1.0.3","PreSARAH_package.m"}]];
(* Suppress graphical rendering only. *)
Unprotect[Paint]; Clear[Paint]; Paint[___]:=Null;
SetOptions[DeclareProcess,MomElim->2];

Get[ToFileName[{$preSARAHdir,"Input"},"PhotonLLp.m"]]; InitProcess;
ins=InsertFields[CreateTopologies[0,2->1],{F[3,{1}],-F[3,{1}]}->V[2],InsertionLevel->{Generic}];
fa=CreateFeynAmp[ins]/.MU->MassEx1/.MZ->0;
fa=fa/.(-F[3,{1,Index[Colour,2]}])->(-F[2,{1}]);
fa=fa/.{f_,FourMomentum[Incoming,2],MassEx1}:>{f,FourMomentum[Incoming,2],MassEx1};
mu=Index[Lorentz,1]; q=FourMomentum[Outgoing,1];
v=NonCommutative[DiracSpinor[-FourMomentum[Incoming,2],MassEx1]];
u=NonCommutative[DiracSpinor[FourMomentum[Incoming,1],MassEx1]];
chain[chir_]:=FermionChain[v,
 NonCommutative[DiracMatrix[q],DiracMatrix[mu],ChiralityProjector[chir]]-
 NonCommutative[DiracMatrix[mu],DiracMatrix[q],ChiralityProjector[chir]],u];
TriangleOperators=TriangleOperators/.MassEx2->MassEx1;
(* Direct i L vertex for outgoing-created photon; sigma=i[gamma,gamma]/2. *)
vertex=-I ee MassEx1/2 (cl chain[-1]+cr chain[1]) Conjugate[PolarizationVector][V[2],q,mu];
fa=fa/.FeynAmp[id_,int_,a_]:>FeynAmp[id,int,vertex];
ClearProcess[];
amp=CalcFeynAmp[fa,FermionChains->Chiral,FermionOrder->{1,2},Invariants->False];
expanded=amp//.Subexpr[]//.Abbr[]/.GenericList[];
Print["D15_TOY_AMP ",InputForm[expanded]];
(* Use the actual held Coefficient expression from the official routine. *)
extractors=Cases[DownValues[CalcAnalyticPenguins2Fermion],
 c:HoldPattern[Coefficient[__]]:>HoldComplete[c],Infinity];
If[Length[extractors]=!=1,Print["BAD_EXTRACTOR_COUNT"];Quit[1]];
actual=Block[{amp=expanded,neglect={},internalfields={Field[4]->S,Field[5]->F,Field[6]->F}},
 Table[PS`sign ReleaseHold[extractors[[1]]],{j,1,2}]];
expected=-2 ee MassEx1 {cr,cl};
If[Simplify[actual-expected]=!={0,0},Print["FAIL ",InputForm[actual]];Quit[2]];
(* Source sign /I is exercised with two independently chosen complex values. *)
values={cl->2+3 I,cr->-5+7 I};
(* Both Fourier signs and HC coefficient exchange, at the extractor level. *)
Do[
 transformed=(actual/.{cl->phase Conjugate[cr],cr->phase Conjugate[cl]});
 target=-2 ee MassEx1 phase {Conjugate[cl],Conjugate[cr]};
 If[Simplify[(transformed-target)/.values]=!={0,0},Quit[4]],
 {phase,{-1,1}}];
If[Simplify[(actual-expected)/.values]=!={0,0},Quit[3]];
Print["D15_EXTRACTED ",InputForm[actual]];
Print["D15_WRAPPED ",InputForm[Simplify[-actual/(2 ee MassEx1)]]];
(* Historical raw-chain algebra test only. The physical action and crossing
   proof now live in crossing_bridge_toy.py/crossing_bridge_spinors.py.
   No candidate-map substitution is made in this intermediate test. *)
Print["D15_TOY_DONE"];
Quit[];
