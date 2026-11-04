"""Build only a disposable two-flavor charged-conjugate dipole toy.

Uses the already recovered toolchain; never regenerates the Zee model.
"""
from pathlib import Path
import subprocess
import json
import hashlib
import argparse
ROOT=Path(__file__).resolve().parent
LOCAL=ROOT/'local'
TOOL=None
OUT=LOCAL/'crossing_bridge'


def prepare():
    OUT.mkdir(exist_ok=True)
    source=(TOOL/'FeynArts-3.9/Models/Lorentz.gen').read_text()
    old='''{ NonCommutative[DiracMatrix[li3], ChiralityProjector[-1]], 
        NonCommutative[DiracMatrix[li3], ChiralityProjector[+1]] }'''
    new='''{ NonCommutative[DiracMatrix[li3], ChiralityProjector[-1]],
        NonCommutative[DiracMatrix[li3], ChiralityProjector[+1]],
        NonCommutative[DiracSlash[mom3],DiracMatrix[li3],ChiralityProjector[-1]]-
        NonCommutative[DiracMatrix[li3],DiracSlash[mom3],ChiralityProjector[-1]],
        NonCommutative[DiracSlash[mom3],DiracMatrix[li3],ChiralityProjector[+1]]-
        NonCommutative[DiracMatrix[li3],DiracSlash[mom3],ChiralityProjector[+1]] }'''
    assert source.count(old)==1
    source=source.replace(old,new)
    oldflip='''M$FlippingRules =
  NonCommutative[dm:_DiracMatrix | _DiracSlash, ChiralityProjector[pm_]] ->
    -NonCommutative[dm, ChiralityProjector[-pm]]'''
    flip='''M$FlippingRules = {
 NonCommutative[dm:_DiracMatrix | _DiracSlash,ChiralityProjector[pm_]] ->
 -NonCommutative[dm,ChiralityProjector[-pm]],
 NonCommutative[a:_DiracMatrix | _DiracSlash,b:_DiracMatrix | _DiracSlash,ChiralityProjector[pm_]] ->
 NonCommutative[b,a,ChiralityProjector[pm]] }'''
    assert source.count(oldflip)==1
    (OUT/'DipoleLorentz.gen').write_text(source.replace(oldflip,flip))
    (OUT/'Dipole.mod').write_text('''M$ModelName="OrderedDipole";
M$Information={Authors->{"D15 disposable effective-action test"}};
M$ClassesDescription={
 F[1]=={SelfConjugate->False,Mass->mI,Indices->{},QuantumNumbers->{Charge->1},PropagatorLabel->"chiI",PropagatorType->Straight,PropagatorArrow->Forward},
 F[2]=={SelfConjugate->False,Mass->mJ,Indices->{},QuantumNumbers->{Charge->1},PropagatorLabel->"chiJ",PropagatorType->Straight,PropagatorArrow->Forward},
 V[1]=={SelfConjugate->True,Mass->0,Indices->{},QuantumNumbers->{Charge->0},PropagatorLabel->"A",PropagatorType->Sine,PropagatorArrow->None}};
(* chi_a=C bar(l_a)^T. Tensor bilinears acquire a minus on
   charge-conjugating Grassmann fields; HC is taken BEFORE differentiation.
   Original action has normalization e mI/2 in both orientations.
   The all-incoming iL rule is -i e mI/2 [pslash_A,gamma_mu]. *)
M$CouplingMatrices={
 C[-F[1],F[1],V[1]]==-I ee {{1},{1},{0},{0}},
 C[-F[2],F[2],V[1]]==-I ee {{1},{1},{0},{0}},
 C[-F[2],F[1],V[1]]==-I ee {{gV},{gV},{fFourier mI Conjugate[cR]/2},{fFourier mI Conjugate[cL]/2}},
 C[-F[1],F[2],V[1]]==-I ee {{Conjugate[gV]},{Conjugate[gV]},{fFourier mI cL/2},{fFourier mI cR/2}}};
''')
    load=f'''BeginPackage["LoopTools`"]
{{bb0,bb1,cc0,cc00,cc1,cc2,cc12,cc22,cc11,dd0,dd00}};
EndPackage[]
Get["{TOOL}/FeynArts-3.9/FeynArts.m"];
Get["{TOOL}/FormCalc-7.5/FormCalc.m"];
Get["{TOOL}/PreSARAH-1.0.3/PreSARAH_package.m"];
Unprotect[Paint];Clear[Paint];Paint[___]:=Null;
Get[ToFileName[{{$preSARAHdir,"Input"}},"PhotonLLp.m"]];InitProcess;
$ModelPath=Prepend[$ModelPath,"{OUT}"];
SetOptions[DeclareProcess,MomElim->2];
extractors=Cases[DownValues[CalcAnalyticPenguins2Fermion],c:HoldPattern[Coefficient[__]]:>HoldComplete[c],Infinity];
If[Length[extractors]=!=1,Quit[1]];
result={{}}; numeric={{}};
originalLoops=Get["{TOOL}/ampSave.m"];
Do[
 polynomial=Expand[originalLoops[[d,1]]/.HoldPattern[G[a_][b_][c__][z_]]:>tt G[a][b][c][z]];
 If[Expand[polynomial-tt^3 originalLoops[[d,1]]]=!=0,Print["BAD_VERTEX_DEGREE",d];Quit[2]],
 {{d,Length[originalLoops]}}];
Print["D15_TRIANGLE_VERTEX_DEGREE ",Length[originalLoops]," diagrams, degree 3"];

Do[
 process=If[orientation==1,{{F[1],-F[2]}}->V[1],{{F[2],-F[1]}}->V[1]];
 ins=InsertFields[CreateTopologies[0,2->1],process,Model->"Dipole",GenericModel->"DipoleLorentz",InsertionLevel->{{Classes}}];
 fa=CreateFeynAmp[ins];
 Put[fa,"{OUT}/feynamp-"<>ToString[orientation]<>".m"];
 ClearProcess[];
 calc=CalcFeynAmp[fa,FermionChains->Chiral,FermionOrder->{{1,2}},Invariants->False];
 expanded=calc//.Subexpr[]//.Abbr[]/.GenericList[];
 Put[expanded,"{OUT}/chains-"<>ToString[orientation]<>".m"];
 Print["D15_PHYSICAL_M ",orientation," ",InputForm[expanded]];
 (* Physical class couplings contain i. PreSARAH's triangle replacement
    G -> coup omits these three vertex factors, so use M / i^3.
    The FA -i prefactor and FORM loop-measure convention are not altered. *)
 normalized=Map[#/I^3&,expanded];
 masses=If[orientation==1,{{MassEx1->mI,MassEx2->mJ}},{{MassEx1->mJ,MassEx2->mI}}];
 ops=TriangleOperators/.masses;
 raw=Block[{{amp=normalized,TriangleOperators=ops,neglect={{}},internalfields={{Field[4]->S,Field[5]->F,Field[6]->F}}}},Table[PS`sign ReleaseHold[extractors[[1]]],{{j,1,2}}]];
 wrapper=Simplify[-raw/(2 ee (MassEx1/.masses))];
 Print["D15_RAW ",orientation," ",InputForm[raw]];
 Print["D15_WRAPPER ",orientation," ",InputForm[wrapper]];
 expected=fFourier If[orientation==1,-{{Conjugate[cL],Conjugate[cR]}},-mI/mJ {{cR,cL}}];
 If[Simplify[wrapper-expected]=!={{0,0}},Print["BAD_MAP"];Quit[3]];
 transformed=wrapper/.{{cL->phase cL,cR->phase cR}};
 phaseExpected=If[orientation==1,Conjugate[phase],phase] wrapper;
 If[Simplify[transformed-phaseExpected]=!={{0,0}},Quit[4]];
 If[Simplify[(wrapper-expected)/.fFourier->-1]=!={{0,0}},Quit[5]];
 numericRules={{mI->3,mJ->7/10,ee->3/10,cL->37/100+83 I/100,cR->-29/100+41 I/100,gV->1,fFourier->1}};
 chainCoeffs=Table[
   chain=DiracChain[Spinor[k[1],MassEx1/.masses,-1],chir,Sequence@@extra,Spinor[k[2],MassEx2/.masses,1]];
   val=Coefficient[Expand[expanded[[1]]],Mat[chain]];
   If[extra==={{}},val=val/Pair[ec[3],k[1]]];
   val=Simplify[val/.numericRules];
   {{chir,Length[extra],Re[val],Im[val]}},{{chir,{{6,7}}}},{{extra,{{{{}},{{ec[3]}}}}}}];
 AppendTo[numeric,chainCoeffs];
 AppendTo[result,wrapper];,
 {{orientation,1,2}}];
Put[result,"{OUT}/result.m"];
insQED=InsertFields[CreateTopologies[0,2->1],{{F[1],-F[1]}}->V[1],Model->"Dipole",GenericModel->"DipoleLorentz",InsertionLevel->{{Classes}}];
ClearProcess[];
qed=CalcFeynAmp[CreateFeynAmp[insQED],FermionChains->Chiral,FermionOrder->{{1,2}},Invariants->False];
qed=qed//.Subexpr[]//.Abbr[]/.GenericList[];
expectedQED=-ee Sum[Mat[DiracChain[Spinor[k[1],mI,-1],ch,ec[3],Spinor[k[2],mI,1]]],{{ch,{{6,7}}}}];
If[Expand[qed[[1]]-expectedQED]=!=0,Print["BAD_QED",InputForm[qed]];Quit[6]];
Put[qed,"{OUT}/QED.m"];
Print["D15_DIAGONAL_QED_PASS"];

Export["{OUT}/chains-numeric.json",numeric,"JSON"];
Print["D15_TOY_FINISHED"];
Quit[];
'''
    (OUT/'run.m').write_text(load)


def main():
    global TOOL,OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--toolchain',type=Path)
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args()
    if args.toolchain is None:
        candidates=[p for p in LOCAL.glob('d15_projector_*') if (p/'ampSave.m').is_file() and (p/'FeynArts-3.9/FeynArts.m').is_file()]
        if not candidates:raise RuntimeError('Supply the already recovered toolchain via --toolchain')
        TOOL=max(candidates,key=lambda p:p.stat().st_mtime)
    else:TOOL=args.toolchain.resolve()
    OUT=args.output.resolve()
    prepare()
    with (OUT/'run.log').open('w') as log:
        p=subprocess.run(['math','-noprompt','-script',str(OUT/'run.m')],stdout=log,stderr=log,timeout=180)
    print((OUT/'run.log').read_text()[-6000:])
    p.check_returncode()
    assert 'D15_TOY_FINISHED' in (OUT/'run.log').read_text()
    evidence={'status':'PASS','relation':'K2L(i,j)=-conj(C_L(i->j)); K2R(i,j)=-conj(C_R(i->j))',
      'reverse':'K(j,i)=-(m_i/m_j) [C_R,C_L]',
      'source_phase':'actual physical classes amplitude / I^3; triangle G degree checked for all six saved source diagrams',
      'QED_reference':'true diagonal QED vertex plus same-state normalized vector spurion',
      'post_projection_candidate_substitution':False,
      'artifacts_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.suffix in ['.m','.mod','.gen','.json','.log']},
      'source_sha256':{str(p.relative_to(TOOL)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [TOOL/'PreSARAH-1.0.3/PreSARAH_package.m',TOOL/'FeynArts-3.9/FeynArts/Analytic.m',TOOL/'FormCalc-7.5/FormCalc75.m']}}
    (OUT/'projector-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')

if __name__=='__main__':main()
