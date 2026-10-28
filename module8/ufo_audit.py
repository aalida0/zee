"""Evaluate the fresh native UFO against independent D3/D4 amplitudes.

Run in a fresh Python process (the generated UFO uses absolute imports).
No MG5 rate is certified here. All generated model/card files remain local.
"""
import argparse
import cmath
import importlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from module1.scalar_constraints import reconstruct
from module2.interface import decode
from module7.d4_inputs import native_cards, ckm, yukawa_masses, sha

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT/'validation/module8/local'
UFO = LOCAL/'native/sarah/ZeeTypeII/EWSB/UFO'


def external_values(parameters, card):
    """Map by actual LHA blocks/codes, never a public sample card."""
    p, r = card['physical'], card['rules']
    v = p['v']; mw = 80.379; mz = 91.1876
    cw = mw/mz; g = 2*mw/v; e = g*math.sqrt(1-cw*cw)
    pars, _, closure = reconstruct(p)
    matrices = {'YU':'Yu','YD':'Yd','YE':'Ye','YEE2':'Ye2','FZEE':'Fzee',
                'SCALARMIX':'ZH','PSEUDOSCALARMIX':'ZA','CHARGEMIX':'ZP',
                'UDLMIX':'Vd','UDRMIX':'Ud','UULMIX':'Vu','UURMIX':'Uu',
                'UELMIX':'Ve','UERMIX':'Ue'}
    mass = {1:.00470,2:.00216,3:.0935,4:1.273,5:4.78,6:172.4,
            11:.00051099895,13:.1056583755,15:1.77686,23:mz,
            25:p['mh1'],35:p['mh2'],36:p['ma'],37:p['mH1'],9000037:p['mH2']}
    quartics = [pars['Lambda'+str(i)] for i in range(1,6)]+[pars['LambdaC'],pars['K1'],pars['K2'],pars['K12']]
    values={}; addresses=set()
    for a in parameters:
        if a.nature!='external':continue
        block=a.lhablock.upper();code=tuple(a.lhacode)
        if (block,code) in addresses:raise ValueError('Duplicate LHA address '+str((block,code)))
        addresses.add((block,code))
        imag=block.startswith('IM');base=block[2:] if imag else block
        if base in matrices:
            z=r[matrices[base]]
            z=decode(z) if isinstance(z,dict) else np.array(z)
            value=z[code[0]-1,code[1]-1]
            value=value.imag if imag else value.real
        elif block=='MASS':value=mass[code[0]]
        elif block=='DECAY':
            # Stable external H1/H2. Other defaults are audited as metadata only.
            value=0. if code[0] in (37,9000037) else float(a.value)
        elif block=='ZEEPOT' and code==(5,):value=pars['Mu4']
        elif block=='ZEEQUARTIC':value=quartics[code[0]-1]
        elif block=='SMINPUTS':value={1:4*math.pi/e**2,2:1/(math.sqrt(2)*v*v),3:.118}[code[0]]
        elif block=='HMIX' and code==(10,):value=p['beta']
        elif block=='EFFHIGGSCOUPLINGS':value=0. # LO tree only
        else:raise ValueError('Unmapped external '+str((a.name,block,code)))
        if not math.isfinite(float(value)):raise ValueError('Nonfinite external '+a.name)
        values[a.name]=float(value)
    return values, closure


def evaluate_parameters(parameters, values, functions):
    env=dict(functions,**values);pending=[a for a in parameters if a.nature=='internal']
    while pending:
        next_pending=[]
        for a in pending:
            try:env[a.name]=eval(str(a.value),{'__builtins__':{}},env)
            except NameError:next_pending.append(a)
        if len(next_pending)==len(pending):raise ValueError('Unresolved internals '+','.join(a.name for a in pending))
        pending=next_pending
    for a in parameters:
        z=complex(env[a.name])
        if not math.isfinite(abs(z)):raise ValueError('Nonfinite internal '+a.name)
        if a.type=='real' and abs(z.imag)>1e-10:raise ValueError('Complex real parameter '+a.name)
    return env


def write_card(path, parameters, values):
    blocks=defaultdict(list);decays=[]
    for a in parameters:
        if a.nature!='external':continue
        if a.lhablock.upper()=='DECAY':decays.append(f'DECAY {a.lhacode[0]} {values[a.name]:.17e} # {a.name}')
        else:blocks[a.lhablock.upper()].append('  '+' '.join(map(str,a.lhacode))+f' {values[a.name]:.17e} # {a.name}')
    path.write_text('\n'.join(['# D5 native mapping audit; NOT production certified']+
        [f'BLOCK {b}\n'+'\n'.join(lines) for b,lines in sorted(blocks.items())]+decays)+'\n')


def read_card(path, parameters):
    addresses={};block=None
    for line in path.read_text().splitlines():
        cols=line.split('#')[0].split()
        if not cols:continue
        if cols[0].upper()=='BLOCK':block=cols[1].upper();continue
        if cols[0].upper()=='DECAY':key=('DECAY',(int(cols[1]),));value=float(cols[2]);block=None
        else:
            if block is None:raise ValueError('Entry outside LHA block')
            key=(block,tuple(map(int,cols[:-1])));value=float(cols[-1])
        if key in addresses:raise ValueError('Duplicate serialized LHA entry')
        addresses[key]=value
    result={}
    for a in parameters:
        if a.nature=='external':result[a.name]=addresses.pop((a.lhablock.upper(),tuple(a.lhacode)))
    if addresses:raise ValueError('Extra LHA entries')
    return result


def audit(ufo=UFO):
    export=json.loads((LOCAL/'native/export.json').read_text())
    if export['status']!='D5_UFO_EXPORTED_UNCERTIFIED' or export['sarah_version']!='4.15.4' or '15.0.1' not in export['math_version']:
        raise ValueError('Fresh native export/version missing')
    for path,want in export['source_sha256'].items():
        if sha(ROOT/path)!=want:raise ValueError('Frozen source mismatch '+path)
    sys.path.insert(0,str(ufo.resolve()))
    for m in ['parameters','particles','couplings','lorentz','vertices']:importlib.import_module(m)
    o=importlib.import_module('object_library');f=importlib.import_module('function_library')
    functions={n:getattr(f,n) for n in ['complexconjugate','re','im','csc','sec','acsc','asec']}
    functions.update(cmath=cmath,complex=complex)
    vertices={tuple(a.pdg_code for a in v.particles):v for v in o.all_vertices}
    cards=native_cards(); results=[];count=0
    for card in cards:
        values,closure=external_values(o.all_parameters,card)
        path=LOCAL/'cards'/(card['id'].replace('/','_')+'.dat');path.parent.mkdir(exist_ok=True)
        write_card(path,o.all_parameters,values)
        reread=read_card(path,o.all_parameters)
        if values!=reread:raise ValueError('LHA round trip conflict')
        env=evaluate_parameters(o.all_parameters,reread,functions)
        # Evaluate every exported coupling, including those outside selected processes.
        cv={a.name:complex(eval(a.value,{'__builtins__':{}},env)) for a in o.all_couplings}
        if any(not math.isfinite(abs(z)) for z in cv.values()):raise ValueError('Nonfinite coupling')
        p=card['physical'];r=card['rules'];res={}; comparisons=0
        def check(sector, got, want):
            nonlocal comparisons
            delta=abs(complex(got)-complex(want));res[sector]=max(res.get(sector,0.),delta);comparisons+=1
            if not math.isfinite(delta) or delta>2e-10*max(1.,abs(want)):
                raise ValueError(f'{card["id"]} {sector}: got {got}, expected {want}')
        def vertex(ids, structure, sector, want, color):
            vtx=vertices.get(tuple(ids))
            # An exact-zero absent vertex is legitimate; a nonzero one must exist.
            if vtx is None:
                check(sector,0.,want);return
            if vtx.color!=color:raise ValueError('Color conflict '+vtx.name)
            selected=[cv[c.name] for (ci,li),c in vtx.couplings.items() if vtx.lorentz[li].structure==structure and ci==0]
            if len(selected)>1:raise ValueError('Ambiguous Lorentz coefficient')
            check(sector,sum(selected),want)
        for n,want in [('g1',r['g1']),('g2',r['g2']),('v',p['v']),('vd',r['v1']),('vu',r['v2']),('MWm',80.379),('MHm2',p['mH1']),('MHm3',p['mH2']),('Mhh1',p['mh1']),('Mhh2',p['mh2']),('MAh2',p['ma'])]:
            check('physical_parameters',env[n],want)
        zp=np.array(r['ZP']);cw=80.379/91.1876;sw2=1-cw*cw;g=r['g2'];electric=g*math.sqrt(sw2)
        for k,pk in enumerate((37,9000037),1):
            for l,pl in enumerate((37,9000037),1):
                delta=float(k==l)
                # UFO SSV convention: ordered H-,H+,V; P(3,1)-P(3,2).
                vertex([pk,-pl,22],'P(3,1) - P(3,2)','photon',-1j*electric*delta,['1'])
                t3=.5*float(zp[k,:2]@zp[l,:2])
                vertex([pk,-pl,23],'P(3,1) - P(3,2)','Z',-1j*g/cw*(t3-sw2*delta),['1'])
        V=ckm();m=yukawa_masses(card['Q_GeV']);beta=p['beta'];gamma=p['gamma']
        check('CKM_unitarity',np.max(abs(V@V.conj().T-np.eye(3))),0.)
        for k,pk in enumerate((37,9000037),1):
            d=math.cos(gamma) if k==1 else -math.sin(gamma)
            s=math.sin(gamma) if k==1 else math.cos(gamma)
            for i,up in enumerate((2,4,6)):
                for j,down in enumerate((1,3,5)):
                    a=math.sqrt(2)*m[i]*d*V[i,j]/(p['v']*math.tan(beta))
                    b=math.sqrt(2)*m[j+3]*d*V[i,j]*math.tan(beta)/p['v']
                    # The UFO FFS chain has spinor indices (2,1). Relative to
                    # native SARAH PL/PR coefficients this reverses projectors.
                    for ids,wp,wm in [([-up,down,-pk],1j*a,1j*b),([-down,up,pk],1j*b.conjugate(),1j*a.conjugate())]:
                        vertex(ids,'ProjP(2,1)','quarks',wp,['Identity(1,2)'])
                        vertex(ids,'ProjM(2,1)','quarks',wm,['Identity(1,2)'])
            F=decode(r['Fzee']);Ye=decode(r['Ye']);Ye2=decode(r['Ye2'])
            D=-math.sin(beta)*Ye+math.cos(beta)*Ye2
            for i,lepton in enumerate((11,13,15)):
                for j,nu in enumerate((12,14,16)):
                    a=-1j*s*F[j,i];b=-1j*d*D[i,j].conjugate()
                    for ids,wp,wm in [([nu,lepton,-pk],a,b),([-lepton,nu,pk],-b.conjugate(),-a.conjugate())]:
                        vertex(ids,'ProjP(2,1)','complex_leptons',wp,['1'])
                        vertex(ids,'ProjM(2,1)','complex_leptons',wm,['1'])
        results.append({'id':card['id'],'comparisons':comparisons,'residuals':res,
                        'scalar_closure':closure,'card_sha256':sha(path)})
        count+=comparisons
    return {'status':'D5_UFO_VERTEX_PASS','scope':'LO mapped masses, kinetic gauge, signed Type-II and general complex lepton coefficients; not an MG5 integration or physical BR certification',
            'export':export,'ufo_sha256':{p.name:sha(p) for p in sorted(ufo.glob('*.py'))},
            'cases':results,'comparisons':count,'native_card_count':len(cards),
            'lha_mapping':'all external entries explicitly mapped and serialized/reloaded; unused noncharged DECAY defaults retained as metadata; effective loop vertices zero',
            'frozen_mass_terms':'M112,M222,MCS2,M12Sq absent from UFO three/four-point parameters; reconstructed and Hessian/tadpole-checked in Module1, never added as fictitious LHA inputs',
            'particles':[{'name':a.name,'pdg':a.pdg_code,'charge':a.charge} for a in o.all_particles],
            'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'module8/ufo_audit.py',ROOT/'scripts/zee_d5_export.m',ROOT/'module7/d4_inputs.py',ROOT/'module1/scalar_constraints.py']}}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--ufo',type=Path,default=UFO)
    a=parser.parse_args()
    report={'status':'D5_UFO_RUNTIME_BLOCKED'}
    try:report=audit(a.ufo)
    except Exception as e:report['diagnostic']=f'{type(e).__name__}: {e}'
    (LOCAL/'ufo_audit.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(report['status'],report.get('diagnostic',report.get('comparisons')))
    return 0 if report['status']=='D5_UFO_VERTEX_PASS' else 2

if __name__=='__main__':raise SystemExit(main())
