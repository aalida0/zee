"""Signed inner-loop numerators from the saved native rules (linear R_xi).

No source_tensors, published kernel, or Goldstone compensator is used.
All momenta at vertices enter. q,k leave the loop, r=q+k enters it;
the oriented edges (s,q),(q,k),(k,s) carry l,l-q,l-r.
Strip e^2*kappa/v and the final i/(16*pi^2), but retain every vertex and
propagator phase and the closed-ghost minus. The resulting reduced tensors
multiply i*e^2*kappa/(16*pi^2*v). All indices are covariant; contractions
use g^{ab}; the metric trace is d, never 4.
"""
from dataclasses import dataclass
from functools import lru_cache
from itertools import product

import sympy as s

D, M2, S2, XI = s.symbols('d mW2 Ms2 xi', positive=True)
L2, LQ, LK, Q2, K2, QK = s.symbols('l2 lq lk q2 k2 qk')
BASIS = ('g', 'll', 'lq', 'lk', 'ql', 'qq', 'qk', 'kl', 'kq', 'kk')
DOTS = {('l', 'l'): L2, ('l', 'q'): LQ, ('l', 'k'): LK,
        ('q', 'q'): Q2, ('q', 'k'): QK, ('k', 'k'): K2}
DOTS.update({(b, a): v for (a, b), v in list(DOTS.items())})


@dataclass(frozen=True)
class Term:
    c: object = 1
    metrics: tuple = ()
    vectors: tuple = ()  # (index, basis momentum)


def mul(*tensors):
    terms = [Term()]
    for tensor in tensors:
        terms = [Term(a.c*b.c, a.metrics+b.metrics, a.vectors+b.vectors)
                 for a in terms for b in tensor]
    return terms


def scale(c, tensor):
    return [Term(c*t.c, t.metrics, t.vectors) for t in tensor]


def metric(a, b):
    return [Term(metrics=((a, b),))]


def vec(a, p):
    return [Term(c, vectors=((a, v),)) for v, c in zip(('l', 'q', 'k'), p) if c]


def addp(*ps):
    return tuple(sum(z) for z in zip(*ps))


def neg(p):
    return tuple(-z for z in p)


def contract(terms):
    """Metric-network contraction with two free indices mu,nu in d dimensions."""
    out = dict.fromkeys(BASIS, s.S.Zero)
    for term in terms:
        nodes = set(x for e in term.metrics for x in e) | set(a for a, _ in term.vectors)
        parent = {n: n for n in nodes}

        def find(a):
            while parent[a] != a:
                a = parent[a]
            return a

        for a, b in term.metrics:
            parent[find(a)] = find(b)
        components = {}
        for n in nodes:
            components.setdefault(find(n), [[], []])[0].extend([n] if n in ('mu', 'nu') else [])
        for a, v in term.vectors:
            components[find(a)][1].append(v)
        c, free, basis = term.c, {}, None
        for indices, vs in components.values():
            if len(indices) == 2 and not vs:
                basis = 'g'
            elif len(indices) == 1 and len(vs) == 1:
                free[indices[0]] = vs[0]
            elif not indices and len(vs) == 2:
                c *= DOTS[tuple(vs)]
            elif not indices and not vs:
                c *= D
            else:
                raise ValueError(('invalid Einstein network', term, indices, vs))
        basis = basis or free['mu']+free['nu']
        out[basis] += c
    return {b: s.expand(c) for b, c in out.items() if c != 0}


def photon(a, b, species_a, species_b, pa, pb, pp):
    """Native photon: a is negative charge, b positive; momenta enter."""
    if species_a == species_b == 'G':
        return scale(-s.I, vec('ph', addp(pb, neg(pa))))
    if species_a == species_b == 'W':
        # native photonWW, with lt1=ph, lt2=a(W-), lt3=b(W+)
        return scale(s.I, mul(metric('ph', b), vec(a, addp(neg(pb), pp)))+
                     mul(metric(a, b), vec('ph', addp(pb, neg(pa))))+
                     mul(metric('ph', a), vec(b, addp(neg(pp), pa))))
    return scale(s.I*s.sqrt(M2), metric('ph', a if species_a == 'W' else b))


def scalar(a, b, sa, sb, pa, pb):
    """Native sWW, sGG, sWG; scalar incoming momentum r=q+k."""
    r = (0, 1, 1)
    if sa == sb == 'W':
        return scale(2*s.I*M2, metric(a, b))
    if sa == sb == 'G':
        return [Term(-s.I*S2)]
    # mW/v = g2/2; negative charge a, positive charge b
    return scale(-s.I*s.sqrt(M2),
                 vec(b, addp(r, neg(pa))) if sa == 'G'
                 else vec(a, addp(pb, neg(r))))


def rename(tensor, old, new):
    return [Term(t.c, tuple(tuple(new if x == old else x for x in e) for e in t.metrics),
                 tuple((new if a == old else a, p) for a, p in t.vectors)) for t in tensor]


@lru_cache(None)
def xi1_graphs(longitudinal=False):
    """26 signed tensors; FeynArts IDs reference the pre-existing graph file.

    This computes native vertex products, rather than importing SM amplitudes.
    FeynArts edge fields 4,6,5 correspond to our edges a,b,c.
    """
    graphs = []
    l, b, c = (1, 0, 0), (1, -1, 0), (1, -1, -1)
    fa = {'GGG': (1, 2), 'GWG': (7, 8), 'GGW': (9, 10),
          'WGG': (11, 12), 'GWW': (13, 14), 'WWG': (15, 16),
          'WGW': (17, 18), 'WWW': (19, 20)}
    for species in product(('W', 'G'), repeat=3):
        label = ''.join(species)
        for orientation in (-1, 1):
            # Reverse charge with the same geometrical edge momenta.
            def vertex(fn, ia, ib, sa, sb, pa, pb, *other):
                return fn(ia, ib, sa, sb, pa, pb, *other) if orientation == 1 else fn(
                    ib, ia, sb, sa, pb, pa, *other)
            sv = vertex(scalar, 'a0', 'c1', species[0], species[2], neg(l), c)
            qv = rename(vertex(photon, 'b0', 'a1', species[1], species[0], neg(b), l,
                               (0, -1, 0)), 'ph', 'mu')
            kv = rename(vertex(photon, 'c0', 'b1', species[2], species[1], neg(c), b,
                               (0, 0, -1)), 'ph', 'nu')
            props = [scale(-s.I, metric(e+'0', e+'1')) if sp == 'W' else [Term(s.I)]
                     for e, sp in zip('abc', species)]
            tensor = mul(sv, qv, kv)
            options = _propagator_options(species, (l, b, c), ('a', 'b', 'c')) if longitudinal else [(None, props)]
            pieces = [dict(mass_xi=mass_xi, numerator=contract(mul(tensor, *pr)))
                      for mass_xi, pr in options]
            graphs.append(dict(id=f'triangle_{label}_{orientation:+}',
                               fa_number=fa[label][orientation == 1],
                               species=species, routing=(l, b, c),
                               numerator=pieces[0]['numerator'], pieces=pieces))
    for ghost, fnums in (('gWm', (3, 4)), ('gWmC', (5, 6))):
        for orientation, fnum in zip((-1, 1), fnums):
            # Four independent FP loops, NOT a complex-scalar seagull pair.
            momq, momk = (l, b) if orientation == -1 else (neg(b), neg(c))
            terms = scale(-XI*M2, mul(vec('mu', momq), vec('nu', momk)))
            graphs.append(dict(id=f'ghost_triangle_{ghost}_{orientation:+}', fa_number=fnum,
                               species=('ghost',)*3, routing=(l, b, c), numerator=contract(terms)))
    graphs.append(dict(id='bubble_G', fa_number=21, species=('G',)*2, routing=(l, c),
                       numerator={'g': -2*S2}))
    # Direct native WW seagull contraction: two W propagators and sWW.
    contact = scale(s.I, scale(-2, mul(metric('mu', 'nu'), metric('a1', 'b1')))+
                    mul(metric('mu', 'a1'), metric('nu', 'b1'))+
                    mul(metric('mu', 'b1'), metric('nu', 'a1')))
    graphs.append(dict(id='bubble_W', fa_number=22, species=('W',)*2, routing=(l, c),
                       numerator=contract(mul(scale(2*s.I*M2, metric('a0', 'b0')),
                            contact, scale(-s.I, metric('a0', 'a1')),
                            scale(-s.I, metric('b0', 'b1'))))))
    if longitudinal:
        graphs[-1]['pieces'] = [dict(mass_xi=mx, numerator=contract(mul(
            scale(2*s.I*M2, metric('a0', 'b0')), contact, *pr)))
            for mx, pr in _propagator_options(('W', 'W'), (l, c), ('a', 'b'))]
    for attached, route, fnums in (('k', (1, 1, 0), (23, 24)),
                                  ('q', (1, 0, 1), (25, 26))):
        for orientation, fnum in zip((-1, 1), fnums):
            graphs.append(dict(id=f'bubble_s{attached}WG_{orientation:+}', fa_number=fnum,
                               species=('W', 'G'), routing=(l, route), numerator={'g': -M2}))
            if longitudinal:
                graphs[-1]['pieces'] = [dict(mass_xi=mx, numerator=contract(mul(
                    scale(s.I, metric('mu', 'a0')),
                    scale(s.I*M2, metric('nu', 'a1')), *pr)))
                    for mx, pr in _propagator_options(('W', 'G'), (l, route), ('a', 'b'))]
    return sorted(graphs, key=lambda x: x['fa_number'])


def _propagator_options(species, routes, edges):
    """D_xi = -i[(g-pp/m^2)/(p^2-m^2)+pp/m^2/(p^2-xi*m^2)].

    Each term has only two/three simple denominators, so the regulated
    parameter integrations remain one/two dimensional even away from xi=1.
    Apparent power UV divergences in the separated unitary terms are kept.
    """
    choices = []
    for sp, p, e in zip(species, routes, edges):
        if sp == 'W':
            pp = mul(vec(e+'0', p), vec(e+'1', p))
            choices.append([(False, scale(-s.I, metric(e+'0', e+'1')+scale(-1/M2, pp))),
                            (True, scale(-s.I/M2, pp))])
        else:
            choices.append([(True, [Term(s.I)])])
    return [(tuple(c[0] for c in combination), [c[1] for c in combination])
            for combination in product(*choices)]
