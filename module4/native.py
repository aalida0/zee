"""Prepare independent complex NO/IO witnesses for the one-start SARAH driver."""
import json
import math
from pathlib import Path
import numpy as np
from module2.interface import evaluate, decode, canonical_hash
from module3.witnesses import example
from module3.core import vertices
from module1.scalar_constraints import reconstruct
from .couplings import quarks, rotations, trilinears

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/'validation/module4/local'


def wl(value):
    if isinstance(value,(list,tuple,np.ndarray)):
        return '{'+','.join(wl(v) for v in value)+'}'
    if isinstance(value,(complex,np.complexfloating)):
        return '('+wl(value.real)+'+I*'+wl(value.imag)+')'
    return repr(float(value)).replace('e','*^')


def prepare():
    LOCAL.mkdir(parents=True,exist_ok=True)
    cases=[];blocks=[]
    for ordering in ('NO','IO'):
        for spectrum in range(3):
            inp=example(ordering,spectrum);n=evaluate(inp['module2_input'])
            p=inp['module2_input']['scalar']['record']['physical']
            ml=np.array(inp['module2_input']['lepton_masses_GeV'])
            F,D,ye,y2=[decode(n[k]) for k in ('F','D','Ye','Ye2')]
            zh,za,zp=rotations(p);lag,_,_=reconstruct(p)
            scalar=vertices(D,p,ml);tri=trilinears(p,lag)
            # Nontrivial unitary rotations, shared for a simple independent
            # neutral mass-basis test: Y=U^T diag(y) V. CKM cancels neutrals.
            rng=np.random.default_rng(419+spectrum)
            u,_=np.linalg.qr(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))
            v,_=np.linalg.qr(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))
            yu=u.T@np.diag([.0022,1.27,172.5])*math.sqrt(2)/(p['v']*math.sin(p['beta']))@v
            yd=u.T@np.diag([.0047,.095,4.18])*math.sqrt(2)/(p['v']*math.cos(p['beta']))@v
            mats={'Fzee':F,'Ye':ye,'Ye2':y2,'ZH':zh,'ZA':za,'ZP':zp,
                  'Ue':np.eye(3),'Ve':np.eye(3),'Yu':yu,'Yd':yd,
                  'Uu':u,'Ud':u,'Vu':v,'Vd':v}
            e=.313;sw=.48;g2=e/sw;cw=math.sqrt(1-sw*sw)
            rules=[f'{name}[{a+1},{b+1}]->{wl(val)}' for name,mat in mats.items()
                   for a,line in enumerate(mat) for b,val in enumerate(line)]
            rules += [f'{k}->{wl(val)}' for k,val in dict(lag,v1=p['v']*math.cos(p['beta']),
                     v2=p['v']*math.sin(p['beta']),g2=g2,g1=e/cw,ThetaW=math.asin(sw)).items()]
            rules += ['Delta[ct1,ct2]->1']
            assertions=[]
            def assertion(key,chir,expected):
                assertions.append('{'+json.dumps(key)+','+chir+','+wl(expected)+'}')
            for particle,charge in (('Fe',-1),('Fu',2/3),('Fd',-1/3)):
                for chir in ('PL','PR'):
                    assertion('photon_'+particle,'LorentzProduct[gamma[lt3],'+chir+']',-1j*e*charge)
            for cp,s in enumerate(('h','H','A'),1):
                C=scalar[s][0]
                for a in range(3):
                    for b in range(3):
                        key=f'lepton_{{{cp}, {a+1}, {b+1}}}'
                        assertion(key,'PL',-1j*C[a,b]);assertion(key,'PR',-1j*C[b,a].conjugate())
                for q,name,mass in [('Fu','top',172.5),('Fd','bottom',4.18)]:
                    c=quarks(mass,name,p)[s]
                    assertion(f'quark_{{{cp}, {q}}}','PL',-1j*c)
                    assertion(f'quark_{{{cp}, {q}}}','PR',-1j*c.conjugate())
                for k in (2,3):
                    for l in (2,3):
                        assertion(f'trilinear_{{{cp}, {k}, {l}}}','1',-1j*tri[s][k-1,l-1])
            for k in (2,3):
                d,s=zp[k-1]@np.array([-math.sin(p['beta']),math.cos(p['beta']),0]),zp[k-1,2]
                for a in range(3):
                    for b in range(3):
                        km=f'charged_minus_{{{k}, {a+1}, {b+1}}}'
                        kp=f'charged_plus_{{{k}, {a+1}, {b+1}}}'
                        assertion(km,'PL',-1j*d*D[a,b]);assertion(km,'PR',-1j*s*F[b,a].conjugate())
                        assertion(kp,'PL',-1j*s*F[b,a]);assertion(kp,'PR',-1j*d*D[a,b].conjugate())
            for cp in (1,2):
                norm=math.cos(p['beta']-p['alpha']) if cp==1 else math.sin(p['beta']-p['alpha'])
                assertion('WW_'+str(cp),'g[lt2,lt3]',1j*g2*g2*p['v']/2*norm)
                mass=p['mh1'] if cp==1 else p['mh2']
                assertion('goldstone_'+str(cp),'1',-1j*mass*mass/p['v']*norm)
            assertion('WW_A','ANY',0j)
            # SARAH's canonical momentum tensor is p_plus-p_minus. Orthogonality
            # fixes diagonal electric charge and zero off-diagonal photons.
            for k in (2,3):
                for l in (2,3):
                    assertion(f'scalar_seagull_{{{k}, {l}}}','g[lt3,lt4]',2j*e*e*(k==l))
                    assertion(f'scalar_gauge_{{VP, {k}, {l}}}','ANY',-1j*e*(k==l))
                    zcharge=g2/cw*(.5*(zp[k-1,0]*zp[l-1,0]+zp[k-1,1]*zp[l-1,1])-sw*sw*(k==l))
                    assertion(f'scalar_gauge_{{VZ, {k}, {l}}}','ANY',-1j*zcharge)
            blocks.append('rules={'+','.join(rules)+'};\nchecks={'+','.join(assertions)+'};\n'
                +'Do[observed=coefficient[expanded[item[[1]]],item[[2]]];\n'
                +'actual=N[observed/.rules/.HoldPattern[conj[x_?NumericQ]]:>Conjugate[x]];\n'
                +'expected=item[[3]];res=If[NumericQ[actual],Abs[actual-expected],1.*^300];\n'
                +'AppendTo[audit,<|"witness"->'+json.dumps(inp['benchmark_id'])+',"vertex"->item[[1]],'
                +'"projector"->ToString[item[[2]],InputForm],"actual"->If[NumericQ[actual],{Re[actual],Im[actual]},ToString[actual,InputForm]],'
                +'"expected"->{Re[expected],Im[expected]},"residual"->res|>],{item,checks}];')
            cases.append({'module3_input':inp,'module2_output':n,'input_sha256':canonical_hash(inp)})
    (LOCAL/'witness_records.json').write_text(json.dumps(cases,indent=2)+'\n')
    pre='''(* Generated from valid Module2 NO/IO families; no external fixtures. *)
expanded=Map[Function[x,x//.HoldPattern[sum[ind_,lo_Integer,hi_Integer,body_]]:>Total[Table[body,{ind,lo,hi}]]],raw];
coefficient[v_,ch_]:=If[ch===ANY,If[v===0,0,v[[2,1]]],If[v===0,0,Total[Cases[Rest[v],{c_,l_}/;l===ch:>c]]]];
audit={};
'''
    post='''
report["scalar_gauge_momentum_tensor_checks"]=Table[
 <|"vertex"->key,"pass"->TrueQ[Expand[raw[key][[2,2]]-(Mom[conj[Hm[{l}]],lt3]-Mom[Hm[{k}],lt3])]==0]|>,
 {g,{VP,VZ}},{k,{2,3}},{l,{2,3}},{key,{"scalar_gauge_"<>ToString[{g,k,l}]}}];
report["numerical_checks"]=audit;
report["max_abs_residual"]=Max[Lookup[audit,"residual"]];
report["status"]=If[report["max_abs_residual"]<1.*^-9&&And@@Flatten[Lookup[Flatten[report["scalar_gauge_momentum_tensor_checks"]],"pass"]],"VERTEX_COMPONENTS_PASS","VERTEX_CONFLICT"];
'''
    (LOCAL/'witnesses.m').write_text(pre+'\n'.join(blocks)+post)
    return cases


if __name__=='__main__':
    prepare()
