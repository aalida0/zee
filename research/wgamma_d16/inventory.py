"""Enumerate labeled inner graphs; unfinished parent completion stays explicit."""
from itertools import product


def inner_diagrams():
    rows = []
    # Edge labels: (s,q), (q,k), (k,s). s,q,k are labeled external vertices.
    # A charge orientation fixes all +/- field incidences around the loop.
    for edges in product(('W', 'G'), repeat=3):
        for charge in (-1, 1):
            vertices = [edges[2]+edges[0], edges[0]+edges[1], edges[1]+edges[2]]
            rows.append(dict(id='triangle_'+''.join(edges)+f'_{charge:+}',
                edges=list(edges), external_vertices=['s'+vertices[0], 'photon'+vertices[1],
                                                     'photon'+vertices[2]],
                charge_orientation=charge, symmetry_factor=1, closed_loop_sign=1,
                xi_dependence='W longitudinal propagators and/or G mass xi*mW^2',
                status='NOT_EVALUATED', missing='Signed dimensionally regulated tensor integral'))
    for ghost in ('gWm', 'gWmC'):
        for orientation in (-1, 1):
            rows.append(dict(id=f'ghost_triangle_{ghost}_{orientation:+}',
                edges=[ghost]*3, external_vertices=['sGhost', 'photonGhost', 'photonGhost'],
                charge_orientation=-1 if ghost == 'gWm' else 1,
                ghost_arrow_orientation=orientation, symmetry_factor=1, closed_loop_sign=-1,
                xi_dependence='ghost mass xi*mW^2 AND native sGhost coupling proportional to xi',
                status='NOT_EVALUATED', missing='Signed FP ghost tensor integral'))
    for species in ('W', 'G'):
        rows.append(dict(id=f'bubble_{species}', edges=[species]*2,
            external_vertices=['s'+species*2, 'photonPhoton'+species*2],
            charge_orientation='complex pair; counted once', symmetry_factor=1, closed_loop_sign=1,
            xi_dependence='W longitudinal propagator' if species == 'W' else 'G mass xi*mW^2',
            status='NOT_EVALUATED', missing='Signed regulated seagull integral'))
    for photon in ('q', 'k'):
        for charge in (-1, 1):
            rows.append(dict(id=f'bubble_s{photon}WG_{charge:+}', edges=['W', 'G'],
                external_vertices=['sPhotonWG', 'photonWG'],
                charge_orientation=charge, scalar_contact_photon=photon,
                symmetry_factor=1, closed_loop_sign=1,
                xi_dependence='W longitudinal propagator and G mass xi*mW^2',
                status='NOT_EVALUATED', missing='Signed mixed contact integral'))
    for row in rows:
        row['status'] = 'EVALUATED_INNER_ONLY'
        row['integral_evidence'] = 'gauge_ledger.json; native_integrands.py; tensor_reduction.py'
        row['missing'] = 'Full projected two-loop parent/ST/LSZ sum, not the regulated inner integral'
    return rows


PARENTS = {
    'P_WWW': 'Fixed-r WWW subloop and neutrino pinch calculated, including finite Rxi witnesses; outer integral and opposite scalar placement missing',
    'P_WG': 'All eight W/G fixed-r subloops calculated at xi=1 for one scalar placement; other placement and general-xi mixed outer matching missing',
    'P_GG': 'GGG fixed-r parent subloop calculated at xi=1; complete outer/two-placement sum missing',
    'P_longitudinal_xi': 'Inner longitudinal poles and finite tensors calculated; full open-Dirac BRST/ghost insertion functional and outer sum missing',
    'P_Zee_completion': 'Test physical H1/H2 derivative-current parents and charged Yukawa sum rules before omitting their pinch parts',
    'P_LSZ_audit': 'Establish which external self-energy, reducible photon attachments and counterterm pieces the on-shell Slavnov-Taylor reduction requires',
}


def missing_contributions():
    return [row['id'] for row in inner_diagrams()] + list(PARENTS)


def require_complete(contributions):
    """A missing/noncomputed nonzero graph is an exception, never numeric zero."""
    for name in missing_contributions():
        if name not in contributions or contributions[name] is None:
            raise RuntimeError('BLOCKED_GAUGE_MATCHING: missing signed contribution '+name)


def require_gauge_independence(values, rtol=1e-9, atol=1e-24):
    """For future independently computed projected CL,CR, not inner Ward tensors."""
    import numpy as np
    xis = sorted(values)
    if len(xis) < 3 or 1. not in xis or min(xis) >= 1 or max(xis) <= 1:
        raise RuntimeError('BLOCKED_GAUGE_MATCHING: need xi below, at and above 1')
    arrays = [np.asarray(values[xi], dtype=complex) for xi in xis]
    if any(a.shape != (2,) or not np.isfinite(a).all() for a in arrays):
        raise ValueError('Two computed finite complex projected coefficients required at each xi')
    ref = arrays[xis.index(1.)]
    if any(np.any(abs(a-ref) > atol+rtol*np.maximum(abs(a), abs(ref))) for a in arrays):
        raise RuntimeError('FAIL: projected dipole depends on xi')
