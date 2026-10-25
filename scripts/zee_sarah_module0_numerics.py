#!/usr/bin/env python3
"""Independent finite-integral, phase covariance and scalar-edge regressions.

No generated SARAH result is replaced by these analytic identities. The
native Majorana gate must compare its actual diagrams to this convention.
"""
import json
import math
from pathlib import Path
import numpy as np
from scipy.integrate import quad
from gate6_benchmark import benchmark
from gate6_width_inventory import inventory, vector_width, scalar_width, tb_width
from zee_sarah_e3_convention_fixture import lepton_log_kernel


def main():
    out = Path('work/sarah_zee/module0_numerics.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    checks = []
    inputs = []

    def check(label, actual, wanted, atol=2e-12):
        residual = float(np.max(np.abs(np.asarray(actual)-wanted)))
        checks.append(dict(label=label,residual=residual,tolerance=atol))
        if not math.isfinite(residual) or residual > atol:
            raise AssertionError(checks[-1])

    # These include equal scalar masses, equal fermion/scalar masses,
    # exactly massless fermions and a nearly degenerate scalar pair.
    for m1,m2,ml in ((300.,700.,1.77686),(375.,925.,.105658),
                     (300.,300.,1.7),(300.,300.00001,1.7),
                     (300.,700.,0.),(300.,700.,300.),
                     (300.,700.,700.),(300.,700.,1e-7)):
        a,b,z=m1*m1,m2*m2,ml*ml
        def integrand(t):
            # t=1-x keeps the small-fermion endpoint at t=0.
            return math.log((z+(a-z)*t)/(z+(b-z)*t))
        independent = sum(quad(integrand,l,r,epsabs=5e-14,epsrel=5e-14,
                               limit=250)[0] for l,r in
                          ((0.,1e-6),(1e-6,1e-3),(1e-3,1.)))
        check('finite_integral_'+str((m1,m2,ml)),
              lepton_log_kernel(m1,m2,ml),independent)
        inputs.append(dict(m1=m1,m2=m2,ml=ml,kernel=independent))

    rng=np.random.default_rng(20261025)
    masses=np.array([.00051099895,.1056583755,1.77686])
    for case,(m1,m2,gamma) in enumerate(((300.,700.,1.089),(375.,925.,.71))):
        raw=(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.002
        f=raw-raw.T
        d=(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.004

        def formula(ff,dd,mm1=m1,mm2=m2,angle=gamma):
            weights=masses*np.array([lepton_log_kernel(mm1,mm2,m) for m in masses])
            contraction=(ff*weights)@dd
            return math.sin(2*angle)/2/(16*math.pi**2)*(contraction+contraction.T)

        analytic=formula(f,d)
        integrated=np.zeros((3,3),complex)
        for i in range(3):
            for j in range(3):
                for ell,m in enumerate(masses):
                    integ=quad(lambda x: math.log((x*m*m+(1-x)*m1*m1)/
                                                   (x*m*m+(1-x)*m2*m2)),
                               0.,1.,points=[.99,.99999],epsabs=1e-12,limit=250)[0]
                    integrated[i,j]+=math.sin(2*gamma)/2/(16*math.pi**2)*m*integ*(
                        f[i,ell]*d[ell,j]+f[j,ell]*d[ell,i])
        check(f'complex_matrix_integral_{case}',analytic,integrated,2e-16)
        check(f'majorana_symmetry_{case}',analytic,analytic.T,1e-20)
        p=np.diag(np.exp(1j*np.array([.31,-.82,1.27])))
        check(f'complex_rephasing_{case}',formula(p@f@p,p.conj()@d@p),p@analytic@p,1e-20)
        check(f'mass_swap_{case}',formula(f,d,m2,m1,-gamma),analytic,1e-20)
        check(f'degenerate_{case}',formula(f,d,m1,m1),np.zeros((3,3)),1e-20)
        check(f'zero_mixing_{case}',formula(f,d,angle=0.),np.zeros((3,3)),1e-20)
        check(f'zero_f_{case}',formula(f*0,d),np.zeros((3,3)),1e-20)
        check(f'zero_d_{case}',formula(f,d*0),np.zeros((3,3)),1e-20)
        # Takagi: U^T M U = positive diagonal. This tests the full
        # complex matrix, including the phases of its diagonalizer.
        left,singular,_=np.linalg.svd(analytic)
        phase=np.diag(left.conj().T@analytic@left.conj())
        u=left.conj()@np.diag(np.exp(-.5j*np.angle(phase)))
        check(f'takagi_{case}',u.T@analytic@u,np.diag(singular),1e-20)
        inputs.append(dict(case=case,m1=m1,m2=m2,gamma=gamma,
                           f_real=f.real.tolist(),f_imag=f.imag.tolist(),
                           d_real=d.real.tolist(),d_imag=d.imag.tolist(),
                           neutrino_GeV_real=analytic.real.tolist(),
                           neutrino_GeV_imag=analytic.imag.tolist()))

    for case,kwargs in enumerate(({},dict(beta=.72,alpha=.23,gamma=.39,mH1=240.,
                                        mH2=820.,m12sq=20000.,mh2=540.,ma=610.,
                                        lc=.8,k1=.3,k2=.2,k12=-.04))):
        point=benchmark(**kwargs)
        check(f'scalar_charged_spectrum_{case}',point['rebuilt_charged_masses_GeV'],
              [point['inputs']['mH1'],point['inputs']['mH2']],1e-8)
        inputs.append(dict(scalar_case=case,benchmark=point,widths=inventory(**kwargs)))
    for name,value in (('vector_threshold',vector_width(100,50,50,1)),
                       ('scalar_threshold',scalar_width(100,50,50,1)),
                       ('tb_threshold',tb_width(100,2,1))):
        check(name,value,0.,1e-30)
    out.write_text(json.dumps(dict(status='PASS_ANALYTIC_NUMERICAL_REGRESSIONS_ONLY',
                                  seed=20261025,checks=checks,inputs=inputs),indent=2)+'\n')
    print('MODULE0_NUMERICS_PASS',len(checks),'checks;',out)


if __name__=='__main__':
    main()
