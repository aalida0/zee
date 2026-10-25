"""Independent mass-basis tree-vertex witnesses; NOT a loop matching proof.

Prepare, run the genuine SARAH driver, then --check. All detailed data stay local.
The expected rules follow from diagonal quark masses and Type-II X,Y, rather
than parsing/reimplementing SARAH's nested Yukawa sums.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np

LOCAL = Path(__file__).resolve().parents[1] / 'validation/module5/local'


def witnesses():
    rng = np.random.default_rng(20261025)
    def unitary():
        q, _ = np.linalg.qr(rng.normal(size=(3, 3))+1j*rng.normal(size=(3, 3)))
        return q
    vd, uu, ud = unitary(), unitary(), unitary()
    # Standard CKM parametrization, deliberately sizeable angles and CP phase.
    s12, s23, s13 = .225, .17, .09
    c12, c23, c13 = (math.sqrt(1-s*s) for s in (s12,s23,s13))
    phase = np.exp(1j*1.13)
    ckm = np.array([[c12*c13,s12*c13,s13/phase],
        [-s12*c23-c12*s23*s13*phase,c12*c23-s12*s23*s13*phase,s23*c13],
        [s12*s23-c12*c23*s13*phase,-c12*s23-s12*c23*s13*phase,c23*c13]])
    vu = ckm @ vd
    for name,beta,gamma,mu,md in [
        ('complex_base',.91,.63,[.0023,1.27,163.],[.0048,.093,4.18]),
        ('up_zero',.91,.63,[0.,0.,0.],[.0048,.093,4.18]),
        ('down_zero',.91,.63,[.0023,1.27,163.],[0.,0.,0.]),
        ('gamma_zero',.91,0.,[.0023,1.27,163.],[.0048,.093,4.18]),
        ('gamma_halfpi',.91,math.pi/2,[.0023,1.27,163.],[.0048,.093,4.18]),
        ('beta_small',.31,.63,[.0023,1.27,163.],[.0048,.093,4.18]),
        ('beta_large',1.41,.63,[.0023,1.27,163.],[.0048,.093,4.18]),
        ('state_exchange',.91,.63+math.pi/2,[.0023,1.27,163.],[.0048,.093,4.18])]:
        sb,cb,sg,cg = math.sin(beta),math.cos(beta),math.sin(gamma),math.cos(gamma)
        zp=np.array([[cb,sb,0],[-sb*cg,cb*cg,sg],[sb*sg,-cb*sg,cg]])
        yield dict(name=name,beta=beta,gamma=gamma,mu=np.array(mu),md=np.array(md),
            v=246.22,ckm=ckm,Vu=vu,Vd=vd,Uu=uu,Ud=ud,ZP=zp,
            Yu=uu.T @ np.diag(np.array(mu)*math.sqrt(2)/(246.22*sb)) @ vu,
            Yd=ud.T @ np.diag(np.array(md)*math.sqrt(2)/(246.22*cb)) @ vd)


def expected(w):
    result={}
    b,g=w['beta'],w['gamma']
    # Goldstone X=-1,Y=1; physical X=tan(beta)*a, Y=cot(beta)*a.
    xy=[(-1.,1.)]+[(math.tan(b)*a,a/math.tan(b)) for a in (math.cos(g),-math.sin(g))]
    for k,(x,y) in enumerate(xy,1):
        for a in range(3):
            for d in range(3):
                l=math.sqrt(2)/w['v']*w['mu'][a]*y*w['ckm'][a,d]
                r=math.sqrt(2)/w['v']*w['md'][d]*x*w['ckm'][a,d]
                result[f'plus_{{{k}, {a+1}, {d+1}}}']=np.array([1j*l,1j*r])
                # Lagrangian h.c. swaps PL/PR. The Feynman rule keeps its i.
                result[f'minus_{{{k}, {d+1}, {a+1}}}']=np.array([1j*r.conjugate(),1j*l.conjugate()])
    for key,q in [('photon_top',2/3),('photon_bottom',-1/3)]:
        result[key]=np.array([-1j*.313*q]*2)
    for key in ('gluon_top','gluon_bottom'):
        result[key]=np.array([-1j*1.17]*2)  # normalize Lam/2=T=1
    for k in range(1,4):
        # Native Lorentz structure is p(H+)-p(H-).
        result[f'photon_scalar_{k}']=np.array([-1j*.313])
    return result


def prepare():
    LOCAL.mkdir(parents=True,exist_ok=True)
    def number(z):
        z=complex(z)
        def real(x):
            return format(x,'.17g').replace('e','*^')
        return f'({real(z.real)}+I*({real(z.imag)}))'
    records=[]
    for w in witnesses():
        rules=[]
        for key in ('Yu','Yd','Vu','Vd','Uu','Ud','ZP'):
            for i in range(3):
                for j in range(3):
                    rules.append(f'{key}[{i+1},{j+1}]->{number(w[key][i,j])}')
        rules+=['Delta[ct1,ct2]->1','Lam[ct3,ct1,ct2]->2',
            'g1->'+number(.313/math.cos(.47)), 'g2->'+number(.313/math.sin(.47)),
            'g3->1.17','ThetaW->.47']
        records.append('{"'+w['name']+'",{'+','.join(rules)+'}}')
    (LOCAL/'native_witnesses.m').write_text('nativeWitnesses={'+',\n'.join(records)+'};\n')


def compare(actual):
    if actual.get('status')!='NATIVE_NUMERICAL_EVALUATED':
        raise ValueError('No successful numerical extraction')
    for key,path in [('driver_sha256',LOCAL.parents[2]/'scripts/zee_module5_charged_quark_vertices.m'),
                     ('raw_sha256',LOCAL/'charged_quark_vertices.json'),
                     ('witness_sha256',LOCAL/'native_witnesses.m')]:
        if actual.get(key)!=hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError('Stale or mismatched numerical evidence: '+key)
    actual=actual['cases']
    cases=list(witnesses())
    if set(actual)!={w['name'] for w in cases}:
        raise ValueError('Missing/extra witness cases')
    maximum=0.;count=0;worst=None
    for w in cases:
        target=expected(w)
        if set(actual[w['name']])!=set(target):
            raise ValueError('Missing/extra numerical vertices')
        for key,ref in target.items():
            pairs=np.asarray(actual[w['name']][key],dtype=float)
            if pairs.shape!=(len(ref),2) or not np.isfinite(pairs).all():
                raise ValueError('Nonfinite/malformed native coefficient')
            value=pairs[:,0]+1j*pairs[:,1]
            error=float(np.max(np.abs(value-ref)))
            if error>maximum: maximum=error;worst=[w['name'],key]
            count+=len(ref)
            if error>2e-12:
                raise ValueError(f'Native tree-rule mismatch {w["name"]} {key}: {error}')
    ckm=cases[0]['ckm'];lam=ckm[2,1].conjugate()*ckm[2,2]
    return dict(status='PASS',scope='NATIVE_TREE_VERTICES_ONLY_NOT_LOOP_MATCHING',
        witnesses=len(cases),complex_coefficients=count,max_absolute_residual=maximum,
        worst=worst,tolerance=2e-12,ckm_Vts_star_Vtb=[lam.real,lam.imag],
        charged_masses_GeV=[550.,900.],
        mass_note='Nondegenerate loop masses reserved; tree rules do not depend on them')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepare',action='store_true');p.add_argument('--check',action='store_true')
    a=p.parse_args()
    if a.prepare: prepare()
    if a.check:
        r=compare(json.loads((LOCAL/'native_numerical.json').read_text()))
        (LOCAL/'native_comparison.json').write_text(json.dumps(r,indent=2)+'\n')
        print(json.dumps(r,sort_keys=True))
    if not (a.prepare or a.check): p.error('Choose --prepare and/or --check')


if __name__=='__main__': main()
