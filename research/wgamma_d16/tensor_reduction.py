"""Independent dimensionally regulated parameter reduction of native tensors.

PV normalization: (mu^2 exp(gamma_E))^eps integral d^d l/(i*pi^(d/2)).
DeltaUV=1/eps; finite parts are MSbar with mu explicit. Tensor moments
are integrated analytically before ordinary bounded parameter quadrature.
The epsilon coefficient of every d contraction multiplies the pole.
"""
from functools import lru_cache
import math

import numpy as np
import sympy as s

from .native_integrands import D, M2, S2, XI, L2, LQ, LK, Q2, K2, QK, xi1_graphs

EXT_BASIS = ('g', 'qq', 'qk', 'kq', 'kk')
U, V, DELTA, LOG = s.symbols('u v Delta logDelta')
R2 = U*U*Q2+2*U*V*QK+V*V*K2
RQ, RK = U*Q2+V*QK, U*QK+V*K2
T2, TQ, TK = s.symbols('t2 tq tk')


@lru_cache(None)
def wick_pairings(labels):
    """Pair linear t factors; return a covariant polynomial, including free mu,nu."""
    if not labels:
        return (((), s.S.One),)
    first, rest = labels[0], labels[1:]
    sums = {}
    for i, other in enumerate(rest):
        if first in ('mu', 'nu') and other in ('mu', 'nu'):
            factor, free = 1, (('mu', 'nu', 'g'),)
        elif first in ('mu', 'nu') or other in ('mu', 'nu'):
            idx, p = (first, other) if first in ('mu', 'nu') else (other, first)
            factor, free = 1, ((idx, p),)
        else:
            factor, free = {('q', 'q'): Q2, ('k', 'k'): K2,
                            ('q', 'k'): QK, ('k', 'q'): QK}[(first, other)], ()
        for f, c in wick_pairings(rest[:i]+rest[i+1:]):
            key = tuple(sorted(f+free))
            sums[key] = sums.get(key, 0)+factor*c
    return tuple(sums.items())


def _free_basis(free):
    if ('mu', 'nu', 'g') in free:
        return 'g'
    mapping = dict(free)
    return mapping['mu']+mapping['nu']


def reduce_general(numerator, n):
    """Arbitrary polynomial-rank analytic DR moments; no four-dimensional trace.

    Gamma(n) cancels the parameter prefactor. A Wick tensor with 2r t's is
    (-1)^(n+r) Gamma(n-r-2+eps) Delta^(2+r-n-eps)/2^r.
    """
    moments = {}
    for basis, coeff in numerator.items():
        shifted = s.Poly(s.expand(coeff.subs({L2: T2+2*U*TQ+2*V*TK+R2,
                                              LQ: TQ+RQ, LK: TK+RK}, simultaneous=True)), T2, TQ, TK)
        # t on a free index or its shifted mean; other free vectors stay fixed.
        slots = [((a, 't'), (a, 'q', U), (a, 'k', V)) if p == 'l' else ((a, p, 1),)
                 for a, p in zip(('mu', 'nu'), basis)] if basis != 'g' else [((None, None, 1),)]
        import itertools
        for selected in itertools.product(*slots):
            labels_free, fixed, factor = [], [], s.S.One
            if basis == 'g':
                fixed = [('mu', 'nu', 'g')]
            else:
                for entry in selected:
                    if len(entry) == 2:
                        labels_free.append(entry[0])
                    else:
                        fixed.append(entry[:2])
                        factor *= entry[2]
            for (a, b, c), value in shifted.terms():
                labels = tuple(['q']*b+['k']*c+labels_free)
                if len(labels) % 2:
                    continue
                r = a+len(labels)//2
                trace = s.prod(D+len(labels)+2*j for j in range(a))
                for free, pair in wick_pairings(labels):
                    target = _free_basis(tuple(fixed)+free)
                    key = target, r
                    moments[key] = moments.get(key, 0)+factor*value*trace*pair
    out = {b: [s.S.Zero, s.S.Zero] for b in EXT_BASIS}
    for (b, r), c in moments.items():
        c = s.expand(c)
        power = 2+r-n
        if power >= 0:
            residue = DELTA**power/(2**r*s.factorial(power))
            out[b][0] += c.subs(D, 4)*residue
            out[b][1] += residue*(c.subs(D, 4)*(s.harmonic(power)-LOG)-
                                  2*s.diff(c, D).subs(D, 4))
        else:
            out[b][1] += (-1)**(n+r)*s.gamma(-power)*DELTA**power/2**r*c.subs(D, 4)
    return {b: tuple(s.expand(x) for x in values) for b, values in out.items()}


def rank2_moments(n):
    """After Feynman parametrization (Gamma(n) included), pole and finite."""
    if n == 3:
        return (0, -1/DELTA), (s.Rational(1, 2), -LOG/2)
    if n == 2:
        return (1, -LOG), (DELTA/2, DELTA*(1-LOG)/2)
    raise NotImplementedError(n)


def reduce_rank2(numerator, n):
    """Translate an at-most-quadratic loop numerator into exact moments."""
    i0, i2 = s.symbols('I0 I2')
    out = dict.fromkeys(EXT_BASIS, s.S.Zero)
    for b, c in numerator.items():
        if b == 'g':
            if s.Poly(c, L2, LQ, LK).total_degree() > 1:
                raise ValueError('Higher rank requires the general Wick reducer')
            out['g'] += c.subs({L2: D*i2+R2*i0, LQ: RQ*i0, LK: RK*i0,
                               }, simultaneous=True)
            # Constant and linear terms must each have exactly ONE moment.
            const = c.subs({L2: 0, LQ: 0, LK: 0})
            out['g'] += const*(i0-1)
        else:
            if c.has(L2, LQ, LK):
                raise ValueError('Unexpected higher-rank covariant')
            if b == 'll':
                out['g'] += c*i2
            choices = [((('q', U), ('k', V)) if a == 'l' else ((a, 1),)) for a in b]
            for a, ca in choices[0]:
                for z, cz in choices[1]:
                    out[a+z] += c*ca*cz*i0
    moments = rank2_moments(n)
    result = {}
    for b, expr in out.items():
        pole = s.expand(expr.subs({i0: moments[0][0], i2: moments[1][0]}))
        finite = s.expand(expr.subs({i0: moments[0][1], i2: moments[1][1]}))
        # d=4-2eps, retaining eps * 1/eps rational remnants.
        result[b] = (pole.subs(D, 4), s.expand(finite.subs(D, 4)-2*s.diff(pole, D).subs(D, 4)))
    return result


@lru_cache(None)
def reduced_graphs():
    return [dict(g, reduced=reduce_rank2(g['numerator'], len(g['routing']))) for g in xi1_graphs()]


@lru_cache(None)
def compiled_graphs():
    args = (U, V, DELTA, LOG, M2, S2, XI, Q2, K2, QK)
    return [(g, s.lambdify(args, [g['reduced'][b][0] for b in EXT_BASIS]+[
        g['reduced'][b][1] for b in EXT_BASIS], 'numpy', cse=True)) for g in reduced_graphs()]


@lru_cache(None)
def compiled_longitudinal():
    """Compute each unitary/longitudinal term independently from native vertices."""
    args = (U, V, DELTA, LOG, M2, S2, XI, Q2, K2, QK)
    result, seen = [], {}
    for g in xi1_graphs(True):
        pieces = []
        for piece in g.get('pieces', [dict(numerator=g['numerator'],
                                          mass_xi=tuple(sp != 'W' for sp in g['species']))]):
            signature = tuple(sorted(piece['numerator'].items())), len(g['routing'])
            if signature not in seen:
                reduced = reduce_general(piece['numerator'], len(g['routing']))
                fn = s.lambdify(args, [reduced[b][0] for b in EXT_BASIS]+[
                    reduced[b][1] for b in EXT_BASIS], 'numpy', cse=True)
                seen[signature] = fn, reduced
            fn, reduced = seen[signature]
            pieces.append((dict(g, mass_xi=piece['mass_xi'], reduced=reduced), fn))
        result.append((g, pieces))
    return result


def exact_uv():
    """Integrate every pole polynomial on its simplex with exact rational moments."""
    x, y = s.symbols('x y')
    rows, total = {}, dict.fromkeys(EXT_BASIS, s.S.Zero)
    for graph, pieces in compiled_longitudinal():
        residues = dict.fromkeys(EXT_BASIS, s.S.Zero)
        for g, _ in pieces:
            n = len(g['routing'])
            params = (x, 1-x) if n == 2 else (x, y, 1-x-y)
            route = g['routing']
            u = -sum(z*p[1] for z, p in zip(params, route))
            v = -sum(z*p[2] for z, p in zip(params, route))
            delta = M2*sum(z*(XI if mx else 1) for z, mx in zip(params, g['mass_xi']))
            for i in range(n):
                for j in range(i):
                    dq, dk = route[i][1]-route[j][1], route[i][2]-route[j][2]
                    delta -= params[i]*params[j]*(dq*dq*Q2+2*dq*dk*QK+dk*dk*K2)
            for b in EXT_BASIS:
                expr = g['reduced'][b][0].subs({U: u, V: v, DELTA: delta}, simultaneous=True)
                poly = s.Poly(s.expand(expr), *((x,) if n == 2 else (x, y)))
                for powers, coeff in poly.terms():
                    moment = (1/s.Integer(powers[0]+1) if n == 2 else
                              s.factorial(powers[0])*s.factorial(powers[1])/s.factorial(sum(powers)+2))
                    residues[b] += coeff*moment
        rows[graph['id']] = {b: s.factor(c) for b, c in residues.items()}
        for b in EXT_BASIS:
            total[b] += residues[b]
    return dict(graphs=rows, total={b: s.factor(c) for b, c in total.items()})


def calculate_longitudinal(*, mw2=80.379**2, ms2=125.**2, q2=0., k2=-7000., qk=-1200.,
                           xi=1., mu2=None, order=40):
    rows, total = [], np.zeros((2, 5))
    for g, pieces in compiled_longitudinal():
        a, b = np.zeros((2, 5)), np.zeros((2, 5))
        args = dict(mw2=mw2, ms2=ms2, q2=q2, k2=k2, qk=qk, xi=xi, mu2=mu2)
        for piece, fn in pieces:
            a += integrate_graph(piece, fn, order=order, **args)
            b += integrate_graph(piece, fn, order=max(8, order//2), **args)
        total += a
        rows.append(dict(id=g['id'], fa_number=g['fa_number'], longitudinal_pieces=len(pieces),
                         uv_pole=dict(zip(EXT_BASIS, a[0])), finite=dict(zip(EXT_BASIS, a[1])),
                         quadrature_change=dict(zip(EXT_BASIS, abs(a[1]-b[1])))))
    return dict(normalization='i*e^2*kappa/(16*pi^2*v); MSbar finite',
                invariants_GeV2=dict(mw2=mw2, ms2=ms2, q2=q2, k2=k2, qk=qk, mu2=mu2 or mw2),
                xi=xi, order=order, tensor_basis=list(EXT_BASIS), graphs=rows,
                uv_pole=dict(zip(EXT_BASIS, total[0])), finite=dict(zip(EXT_BASIS, total[1])))


def _grid(order, n):
    x, w = np.polynomial.legendre.leggauss(order)
    x, w = (x+1)/2, w/2
    if n == 2:
        return np.array([1-x, x]), w
    a, t = x[:, None], x[None, :]
    weights = (w[:, None]*w[None, :]*(1-a)).ravel()
    return np.array([np.broadcast_to(a, (order, order)).ravel(),
                     ((1-a)*t).ravel(), ((1-a)*(1-t)).ravel()]), weights


def integrate_graph(g, fn, *, mw2, ms2, q2, k2, qk, xi=1., mu2=None, order=40):
    """Finite quadrature of analytically regulated moments, not a cutoff loop."""
    if xi != 1 and 'W' in g['species'] and 'mass_xi' not in g:
        raise ValueError('Use longitudinal_graphs for xi != 1 W propagators')
    mu2 = mw2 if mu2 is None else mu2
    params, weights = _grid(order, len(g['routing']))
    route = np.array(g['routing'], float)
    # denominator (l + a*q + b*k)^2 - mass^2; l=t+R.
    u, v = -route[:, 1]@params, -route[:, 2]@params
    mx = g.get('mass_xi', tuple(sp != 'W' for sp in g['species']))
    masses = [mw2*(xi if isxi else 1) for isxi in mx]
    delta = np.array(masses)@params
    for i in range(len(route)):
        for j in range(i):
            dq, dk = route[i, 1:]-route[j, 1:]
            inv = dq*dq*q2+2*dq*dk*qk+dk*dk*k2
            delta -= params[i]*params[j]*inv
    if not (mw2 > 0 and ms2 > 0 and xi > 0 and mu2 > 0) or np.min(delta) <= 0:
        raise ValueError('Require positive masses/xi/mu and positive parameter Delta')
    values = fn(u, v, delta, np.log(delta/mu2), mw2, ms2, xi, q2, k2, qk)
    return np.array([float(np.sum(value*weights)) for value in values]).reshape(2, 5)


def calculate(*, mw2=80.379**2, ms2=125.**2, q2=0., k2=-7000., qk=-1200.,
              xi=1., mu2=None, order=40):
    rows, total = [], np.zeros((2, 5))
    for g, fn in compiled_graphs():
        args = dict(mw2=mw2, ms2=ms2, q2=q2, k2=k2, qk=qk, xi=xi, mu2=mu2)
        a = integrate_graph(g, fn, order=order, **args)
        b = integrate_graph(g, fn, order=max(8, order//2), **args)
        error = np.abs(a-b)
        total += a
        rows.append(dict(id=g['id'], fa_number=g['fa_number'],
                         uv_pole=dict(zip(EXT_BASIS, a[0])), finite=dict(zip(EXT_BASIS, a[1])),
                         quadrature_change=dict(zip(EXT_BASIS, error[1]))))
    return dict(normalization='i*e^2*kappa/(16*pi^2*v); MSbar finite',
                invariants_GeV2=dict(mw2=mw2, ms2=ms2, q2=q2, k2=k2, qk=qk, mu2=mu2 or mw2),
                xi=xi, order=order, tensor_basis=list(EXT_BASIS), graphs=rows,
                uv_pole=dict(zip(EXT_BASIS, total[0])), finite=dict(zip(EXT_BASIS, total[1])))


if __name__ == '__main__':
    import json
    print(json.dumps(calculate(), indent=2))
