#!/usr/bin/env python3
"""Full-field contract audit on exactly one saved D10 PASS and UNKNOWN card."""
from pathlib import Path
import argparse
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from module14.conditional_scan.workflow import load
from module14.scan import encode, file_sha
from module1.scalar_constraints import reconstruct
from module1.potential import Potential, component_value
from module1.d10_polynomial import evaluate, symbolic, NAMES
from module1.d10_search import verify
from module1.d10_certificate import attempt_certificate


def audit():
    path=Path('module1/d10_benchmarks.json'); records=load(path)['records']; result=[]
    for name in ('d7_NO_neutral_near_heavy_07','P2_beta_shift'):
        card=next(r['input'] for r in records if r['input']['benchmark_id']==name)
        p=reconstruct(card['physical'])[0];x=card['physical'];v=x['v']
        ew=np.zeros(10);ew[[2,6]]=[v*np.cos(x['beta']),v*np.sin(x['beta'])]
        # Fixed field probes are derivative checks at this SAME potential,
        # not additional model parameter points or minimization starts.
        probes=[ew, np.arange(-5,5,dtype=float)*v/7, np.array([1,-2,3,-4,5,-6,7,-8,9,-10])*v/11]
        residuals=np.zeros(3)
        for r in probes:
            a=evaluate(r,p);b=Potential(p).evaluate(r)
            for k,power in enumerate((4,3,2)):
                residuals[k]=max(residuals[k],float(np.max(abs(a[k]-b[k])))/v**power)
            assert abs(a[0]-component_value(r,p))/v**4<1e-12
        assert max(residuals)<1e-12
        checked=verify(ew,p,x)
        cert=attempt_certificate(p,x)['certified']
        result.append({'benchmark_id':name,'certificate':'PASS' if cert else 'UNKNOWN',
                       'max_scaled_value_gradient_hessian_residual':residuals.tolist(),
                       'EW_energy_GeV4':evaluate(ew,p)[0],'EW_stationarity':checked})
    assert [r['certificate'] for r in result]==['PASS','UNKNOWN']
    r,parameters,value,gradient,hessian=symbolic()
    # Gauge orbits make the full 10-equation system non-isolated. A square
    # array of equations alone does not meet root-exhaustion certification.
    return {'status':'ZEE_VEVACIOUS_ADAPTER_UNVALIDATED','full_real_fields':10,
            'field_order':'H1p_Re,Im,H10_Re,Im,H2p_Re,Im,H20_Re,Im,Sp_Re,Im; all /sqrt(2)',
            'parameters':list(NAMES),'polynomial_degree':4,
            'gauge_obstruction':'SU(2)xU(1) orbits; rank 3 at EW, generic rank 4; singular strata need separate charts',
            'solver_executed':False,'global_minimum_claim':None,
            'input_sha256':file_sha(path),'comparisons':result,
            'source_sha256':{n:file_sha(n) for n in ('models/SARAH/ZeeTypeII/ZeeTypeII.m','module1/potential.py','module1/d10_polynomial.py','module1/d10_search.py')}}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);a=p.parse_args()
    with open(a.output,'x') as f:f.write(encode(audit())+'\n')
