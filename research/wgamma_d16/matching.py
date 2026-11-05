"""Minimal diagnostic interface; unavailable physical W Wilsons are JSON null.

No routine here grants WGAMMA_GAUGE_MATCHING_PASS. The A-only numbers remain
explicitly conditional, even when the source-tensor identities pass.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from module3.core import OPERATOR, vertices
from .algebra import (abe_A_double_integral, goldstone_F2, projected_source_check,
                      reference_kernels, source_tensors)
from .inventory import PARENTS, inner_diagrams

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def encode(z):
    return dict(real=float(complex(z).real), imag=float(complex(z).imag))


def decode_matrix(data):
    a = np.asarray(data, dtype=float)
    if a.shape != (3, 3, 2) or not np.isfinite(a).all():
        raise ValueError('D must be a finite 3x3 array of [real,imag] pairs')
    return a[:, :, 0]+1j*a[:, :, 1]


def example(index=0):
    p = json.loads((ROOT/'module1/example.json').read_text())['physical']
    if index == 1:
        p.update(mh2=437., ma=469., mH1=347., mH2=861., alpha=.31,
                 beta=1.07, gamma=-.43, m12sq=31000.)
    elif index != 0:
        raise ValueError('Only two diagnostic examples defined')
    rng = np.random.default_rng(16031+index)
    D = .03*(rng.normal(size=(3, 3))+1j*rng.normal(size=(3, 3)))
    return dict(physical=p, D=[[[z.real, z.imag] for z in row] for row in D],
                lepton_masses_GeV=[.00051099895, .1056583755, 1.77686],
                i=1, j=0, mw=.647*p['v']/2, alpha_em=.313**2/(4*math.pi))


def conditional_source_A(inp, method='kernel'):
    """Signed outer reduction of Abe's *source* A tensor, NOT physical matching.

    The independent double integral tests radial reduction, not W diagrams.
    """
    if method not in ('kernel', 'double-integral'):
        raise ValueError('Unknown radial integration method')
    p, D = inp['physical'], decode_matrix(inp['D'])
    ml = np.asarray(inp['lepton_masses_GeV'], dtype=float)
    i, j = inp['i'], inp['j']
    if ml.shape != (3,) or not np.isfinite(ml).all() or np.any(ml <= 0):
        raise ValueError('Three positive finite external masses required')
    if (i, j) not in ((1, 0), (2, 0), (2, 1)):
        raise ValueError('Select a physical downward LFV channel')
    if any(not math.isfinite(p[k]) for k in ('alpha', 'beta', 'v', 'mh1', 'mh2', 'ma')):
        raise ValueError('Finite scalar inputs required')
    if min(p['v'], p['mh1'], p['mh2'], p['ma'], inp['mw'], inp['alpha_em']) <= 0:
        raise ValueError('Positive masses, vev and alpha required')
    if not math.isfinite(inp['mw']) or not math.isfinite(inp['alpha_em']):
        raise ValueError('Finite EW constants required')
    scalars = vertices(D, p, ml)
    delta = p['beta']-p['alpha']
    total, pieces = np.zeros(2, complex), {}
    for name, kap in zip(('h', 'H'), (math.cos(delta), math.sin(delta))):
        C, ms = scalars[name]
        z = (inp['mw']/ms)**2
        kernel = (reference_kernels(z)['Abe_A'] if method == 'kernel'
                  else abe_A_double_integral(z))
        pref = inp['alpha_em']*kap/(16*math.pi**3*p['v']*ml[i])
        value = pref*kernel*np.array([C[j, i], C[i, j].conjugate()])
        total += value
        pieces[name] = value
    return total, pieces


def goldstone_projection(inp, xi):
    """Actual G triangle+seagull subset in the frozen external-invariant limit.

    Native G_sGG=Ms^2*kappa_s/v; G propagator mass^2=xi*mW^2.
    Gauge dependent by itself; this is NEVER a physical Wilson coefficient.
    """
    if not math.isfinite(xi) or xi <= 0:
        raise ValueError('Positive finite xi required')
    p, D = inp['physical'], decode_matrix(inp['D'])
    ml, i, j = np.asarray(inp['lepton_masses_GeV']), inp['i'], inp['j']
    scalars = vertices(D, p, ml)
    delta = p['beta']-p['alpha']
    out = np.zeros(2, complex)
    for name, kap in zip(('h', 'H'), (math.cos(delta), math.sin(delta))):
        C, ms = scalars[name]
        out += (inp['alpha_em']*kap/(16*math.pi**3*p['v']*ml[i]) *
                goldstone_F2(xi*(inp['mw']/ms)**2)*np.array([C[j, i], C[i, j].conjugate()]))
    return out


def gauge_falsifier(inp):
    """Reject the tempting xi=1 result + only Goldstone mass replacement.

    This is a calculated incomplete prescription, NOT the full Rxi amplitude.
    Its failure identifies precisely the compensating term still required.
    """
    a, _ = conditional_source_A(inp)
    g1 = goldstone_projection(inp, 1.)
    rows, values = [], {}
    for xi in (.5, 1., 3.):
        gx = goldstone_projection(inp, xi)
        partial = a+gx-g1
        values[xi] = partial
        rows.append(dict(xi=xi, goldstone_subset=list(map(encode, gx)),
                         incomplete_prescription=list(map(encode, partial)),
                         missing_compensator_relative_to_xi1=list(map(encode, -(gx-g1)))))
    ref = values[1.]
    relative = max(float(np.max(abs(v-ref)/np.maximum(abs(ref), 1e-30))) for v in values.values())
    return dict(status='FAIL' if relative > 1e-9 else 'NOT_EVALUATED',
                scope='Falsifier of Goldstone-only mass replacement, NOT full Rxi amplitude',
                max_relative_xi_variation=relative, points=rows,
                required_identity='Delta_xi(C_W + C_mixed + C_ghost + C_pinch) = -Delta_xi C_G',
                complete_projected_Rxi=dict(status='NOT_EVALUATED', C_L=None, C_R=None))


def evaluate(inp):
    a, pieces = conditional_source_A(inp)
    p = inp['physical']
    references = {name: reference_kernels((inp['mw']/p[mass])**2)
                  for name, mass in (('h', 'mh1'), ('H', 'mh2'))}
    q, k = np.array([1., 0., 0., 1.]), np.array([.4, 2., -.3, 3.])
    tensors = {}
    for name, mass in (('h', 'mh1'), ('H', 'mh2')):
        t = source_tensors(q, k, p[mass], inp['mw'])
        tensors[name] = {key: t[key].tolist() for key in ('A', 'P', 'B', 'C', 'pinch')}
        tensors[name]['form_factors'] = t['form_factors']
    return dict(status='BLOCKED_GAUGE_MATCHING', physical_status='UNKNOWN',
                C_L=None, C_R=None, coherent_inclusion=False, operator=OPERATOR,
                approximation='Leading external-invariant expansion for radial diagnostics; B/C on-shell identities retain unequal masses',
                conditional_source_A=dict(status='NOT_EVALUATED',
                    scope='Signed source-A outer reduction only; W/gauge matching unvalidated',
                    C_L=encode(a[0]), C_R=encode(a[1]),
                    pieces={name: list(map(encode, value)) for name, value in pieces.items()},
                    accepted_for_physics=False),
                source_tensors_xi1=tensors, source_BC_check=projected_source_check(),
                known_physical_zeros=dict(
                    A_pure_W_G_sector=dict(status='NOT_APPLICABLE', vertex_value=0,
                        reason='CP-conserving scalar sector; AWW=AGG=AWG=0 and neutral ghost VEV overlap=0'),
                    photon_W_physical_H=dict(status='NOT_APPLICABLE', vertex_value=0,
                        reason='Native v1*ZP[a,1]+v2*ZP[a,2]=0 for both physical charged states')),
                gauge_falsifier=gauge_falsifier(inp), conditional_references=references,
                diagram_inventory=inner_diagrams(), missing_parent_reductions=PARENTS,
                gates=dict(A='BLOCKED_GAUGE_MATCHING', B='BLOCKED_GAUGE_MATCHING',
                           C='NOT_EVALUATED', D='BLOCKED_GAUGE_MATCHING'),
                provenance=dict(input_sha256=hashlib.sha256(json.dumps(inp, sort_keys=True,
                    separators=(',', ':'), allow_nan=False).encode()).hexdigest(),
                    frozen_D15_commit='f6676356a95517f2820dea79298a938cc8786968',
                    crossing='K2L/R=-conj(C_L/R), same parent mass; D15 CROSSING_BRIDGE.md',
                    source='Conditional source diagnostic: Abe1311.4704v3 Eq3.8-3.16 + 2016 erratum',
                    independent_inner_evidence='gauge_ledger.json: regulated Rxi inner tensors and partial parent subloops; no physical outer matching'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--example', type=int, default=1)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--require-pass', action='store_true', help='Exit 2 while gauge matching is blocked')
    args = parser.parse_args()
    inp = json.loads(args.input.read_text()) if args.input else example(args.example)
    result = evaluate(inp)
    text = json.dumps(result, indent=2, allow_nan=False)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end='')
    return 2 if args.require_pass else 0


if __name__ == '__main__':
    raise SystemExit(main())
