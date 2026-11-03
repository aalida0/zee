"""Independent expanded SARAH polynomial oracle; no Module1 A/C/T tensors."""
from functools import lru_cache

import numpy as np
import sympy as sp

NAMES = ('M112', 'M222', 'M12Sq', 'MCS2', 'Mu4', 'Lambda1', 'Lambda2',
         'Lambda3', 'Lambda4', 'Lambda5', 'LambdaC', 'K1', 'K2', 'K12')


@lru_cache(None)
def symbolic():
    r = sp.symbols('r:10', real=True)
    coefficients = sp.symbols(' '.join(NAMES), real=True)
    p = dict(zip(NAMES, coefficients))
    h1p, h10, h2p, h20, s = [(r[i]+sp.I*r[i+1])/sp.sqrt(2)
                            for i in range(0, 10, 2)]
    norm = lambda a: sp.expand(a*sp.conjugate(a))
    x, y, w = norm(h1p)+norm(h10), norm(h2p)+norm(h20), norm(s)
    z = sp.conjugate(h1p)*h2p+sp.conjugate(h10)*h20
    d = sp.conjugate(s)*(h1p*h20-h10*h2p)
    re = lambda a: sp.expand((a+sp.conjugate(a))/2)
    expression = sp.expand(
        p['M112']*x+p['M222']*y-2*p['M12Sq']*re(z)+p['MCS2']*w
        +2*p['Mu4']*re(d)+p['Lambda1']*x*x/2+p['Lambda2']*y*y/2
        +p['Lambda3']*x*y+p['Lambda4']*norm(z)+p['Lambda5']*re(z*z)
        +p['LambdaC']*w*w+(p['K1']*x+p['K2']*y-2*p['K12']*re(z))*w)
    gradient = [sp.diff(expression, a) for a in r]
    return r, coefficients, expression, gradient, sp.hessian(expression, r)


@lru_cache(None)
def functions(backend='numpy'):
    r, p, value, gradient, hessian = symbolic()
    return tuple(sp.lambdify((r, p), expr, backend, cse=True)
                 for expr in (value, gradient, hessian))


def evaluate(r, p):
    args = [p[k] for k in NAMES]
    value, gradient, hessian = functions()
    return float(value(r, args)), np.asarray(gradient(r, args), float), np.asarray(hessian(r, args), float)


def invariants(r):
    z = (np.asarray(r)[::2]+1j*np.asarray(r)[1::2])/np.sqrt(2)
    x, y, s = float(np.vdot(z[:2], z[:2]).real), float(np.vdot(z[2:4], z[2:4]).real), abs(z[4])**2
    overlap = np.vdot(z[:2], z[2:4])
    determinant = z[0]*z[3]-z[1]*z[2]
    return np.array([x, y, overlap.real, overlap.imag, s]), determinant, z[4]
