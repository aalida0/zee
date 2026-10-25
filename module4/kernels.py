"""Haber (2024) Eqs. 1,39,42. Direct integrals avoid large-z cancellation."""
from functools import lru_cache
import math
from scipy.integrate import quad


def _ratio(u, z):
    t = (u-z)/z
    if abs(t) < 1e-4:
        return 1-t/2+t*t/3-t**3/4+t**4/5-t**5/6
    # log(u/z), rather than log1p(t), retains endpoint precision at large z.
    return math.log(u/z)/t


@lru_cache(maxsize=1024)
def kernels(z):
    """Return (f,g,h), absolute integration errors; real positive z only."""
    z = float(z)
    if not math.isfinite(z) or not 1e-24 <= z <= 1e10:
        raise ValueError('Require finite 1e-24 <= z <= 1e10')
    def integrand(x, kind):
        u = x*(1-x)
        t = (u-z)/z
        if kind == 2:
            if abs(t) < 1e-4:
                return -.25+t/6-t*t/8+t**3/10-t**4/12
            return -.5*(1/t-math.log(u/z)/(t*t))
        return .5*_ratio(u,z)*(1-2*u if kind == 0 else 1)
    points=[]
    if z<.25:
        low=2*z/(1+math.sqrt(1-4*z))
        points=[low]
    # Exact reflection symmetry avoids rounding x to 1 in tiny endpoint panels.
    result = [tuple(2*t for t in quad(integrand,0,.5,args=(k,),epsabs=min(1e-12,z*5e-10),
                   epsrel=2e-12,points=points,limit=500)) for k in range(3)]
    if any(not math.isfinite(v) or e > max(2e-10,abs(v)*2e-9) for v,e in result):
        raise ArithmeticError('Uncontrolled Barr-Zee quadrature')
    return tuple(v for v,e in result), tuple(e for v,e in result)


def w_kernel(z):
    """CHK Eqs.14+18; Davidson Eq.24: photon subset including Goldstones."""
    (f,g,h),(ef,eg,eh) = kernels(z)
    return (3*f+23*g/4+3*h/4+(f-g)/(2*z),
            3*ef+23*eg/4+3*eh/4+(ef+eg)/(2*z))


def charged_scalar_kernel(z):
    """Ilisie1502.04199 Eq.27 F2=(f-g)/(2z), direct stable parameters.

    Mathematical form factor only; no LFV amplitude or sign matching implied.
    """
    z=float(z)
    kernels(z) # domain and convergence guard
    value,error=quad(lambda x:-x*(1-x)*_ratio(x*(1-x),z)/(2*z),0,.5,
                     epsabs=1e-11,epsrel=2e-12,limit=500)
    return 2*value,2*error
