"""Actual next W-parent reduction and minimal remaining-calculation reproducer.

Taylor-reduce the saved native WWW parent's six propagators to two-loop
vacuum families BEFORE attempting loop integration. No 4D cutoff integral
is used. The resulting sunset integrals still need d-dimensional numerator,
IBP, crossed placement, physical charged currents and LSZ/counterterms.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import sympy as s
from .external_2hdm import pack,sha
from .parent_integrals import exact_parent_integrand

HERE=Path(__file__).resolve().parent


def reduce_denominators():
    x,y,z,w,h,a,b,c,t,u=s.symbols('l2 r2 lr mW2 Ms2 lp lq rp tp tq')
    # The unpinched charged lepton is (p-r)^2, not a constant. External
    # masses are expanded in denominators only, as in the frozen matching.
    den=((x-w)*(x-2*u*b-w)*(x+y-2*z-w)*(x-2*t*a)
         *(y-h)*(y-2*t*c))
    f=1/den
    coeff={
        'p0_q0':f.subs({t:0,u:0}),
        'p1_q0':s.diff(f,t).subs({t:0,u:0}),
        'p0_q1':s.diff(f,u).subs({t:0,u:0}),
        'p1_q1':s.diff(f,t,u).subs({t:0,u:0}),
    }
    v=s.symbols('v2') # (l-r)^2; replaces lr, NOT an independent propagator
    partial={}
    for name,expr in coeff.items():
        expr=expr.subs(z,(x+y-v)/2)
        # Apart only in the repeated loop momenta. The third mass line
        # (v2-mW2) is part of each sunset master and must stay in place.
        expr=s.apart(s.apart(expr*(v-w),x),y)/(v-w)
        partial[name]=s.factor_terms(expr)
    # Verify the first Taylor coefficient by an independent geometric product.
    target=2*b/(x-w)*2*(a/x+c/y)*coeff['p0_q0']
    residual=s.cancel(coeff['p1_q1']-target)
    if residual!=0:
        raise ArithmeticError('External-momentum denominator expansion failed')
    return dict(exact_denominator=str(den),taylor={k:str(v) for k,v in coeff.items()},
        sunset_partial_fractions={k:str(v) for k,v in partial.items()},
        symbolic_residual=str(residual),
        remaining='Full d-dimensional open-Dirac numerator/IBP plus crossed, physical-H, BRST and LSZ sum. Vacuum families have overlapping UV subtractions; fixed-r eps^0 is insufficient.')


def reproduce():
    reduction=reduce_denominators()
    # Real nonzero saved native integrand: two independent complex chiral
    # vertices, three gauge parameters, no inference of a missing compensator.
    args=dict(loop=np.array([.2,.6,-.5,.4]),outer=np.array([.1,-.4,.3,.2]),
        p=np.array([1.,0.,0.,0.]),q=np.array([.5,0.,0.,.5]),
        mw2=80.379**2,ms2=310.**2,lepton_mass=1.,left=.03+.02j,right=-.01+.04j)
    vals={str(xi):exact_parent_integrand(**args,xi=xi) for xi in (.5,1.,3.)}
    return dict(status='BLOCKED_OUTER_W_DIPLOLE_REDUCTION',reduction=reduction,
        exact_integrand=vals,inputs=args,
        max_integrand_xi_variation=float(max(np.max(abs(v-vals['1.0'])) for v in vals.values())),
        physical_C_LR=None,
        source_sha256={f.name:sha(f) for f in (Path(__file__),HERE/'parent_integrals.py',
            HERE/'native_integrands.py',HERE/'st_sources.json')})


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--require-completion',action='store_true')
    args=ap.parse_args();result=reproduce()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(pack(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],'Taylor identity',result['reduction']['symbolic_residual'])
    if args.require_completion:
        raise SystemExit(2)
