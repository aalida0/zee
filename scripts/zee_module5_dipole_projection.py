"""Audit-only leading dipole projection, with diagram-resolved parameter integrals.

Derivation and explicit sign conventions: module5/NATIVE_OPERATOR_MATCHING.md.
This is NOT a certification of the external 2026/HyperIso conventions or BR.
Keep separate from the frozen production implementation.
"""
import mpmath as mp


def diagrams(x):
    """Dimensionless Wilson projections for unit internal charge/generator.

    t is the total Feynman weight of top propagators. Numerator reduction
    produces the polynomials below, separately for internal/external flips.
    No rational/log scalar kernels are used here.
    """
    x=mp.mpf(x)
    if not mp.isfinite(x) or x<=0: raise ValueError('Positive finite mass ratio required')
    d=lambda t: 1+(x-1)*t
    return {
        'top_YY':-x/4*mp.quad(lambda t:t**2*(1-t)/d(t),[0,1]),
        'scalar_YY':-x/4*mp.quad(lambda t:t*(1-t)**2/d(t),[0,1]),
        'top_XY':-x/2*mp.quad(lambda t:t**2/d(t),[0,1]),
        'scalar_XY':-x/2*mp.quad(lambda t:t*(1-t)/d(t),[0,1])}


def coefficients(x,yy,xy,qt=mp.mpf(2)/3,qs=1):
    d=diagrams(x)
    return (yy*(qt*d['top_YY']+qs*d['scalar_YY'])+
            xy*(qt*d['top_XY']+qs*d['scalar_XY']),
            yy*d['top_YY']+xy*d['top_XY'])
