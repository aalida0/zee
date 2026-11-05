"""Reproduce the signed regulated inner calculation and actual parent subloops.

python3 -m research.wgamma_d16.regulated_pilot
python3 -m research.wgamma_d16.regulated_pilot --require-completion  # exit 2
No completed B/C reductions, diagram count or old vertex inventory is rerun.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import subprocess
import time

import numpy as np
import scipy
import sympy

from module3.core import vertices
from .algebra import ETA, decay_momenta, dot, outer_current, source_tensors, bar, spinor
from .longitudinal_identities import scalar_contraction, contracted_triple, PARENT_TERMS
from .matching import example, decode_matrix, encode
from .native_integrands import xi1_graphs
from .parent_integrals import (calculate_parent, calculate_native_parents, calculate_parent_rxi,
                               exact_parent_integrand, attach_scalar_leg, pointwise_pinch_residual)
from .tensor_reduction import calculate, calculate_longitudinal, exact_uv, EXT_BASIS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def encode_tensor(a):
    return np.stack((a.real, a.imag), axis=-1).tolist()


def attached_inner(finite, q, k, current):
    from .algebra import METRIC
    tensor = finite['g']*METRIC
    for key, a, b in [('qq', q, q), ('qk', q, k), ('kq', k, q), ('kk', k, k)]:
        tensor = tensor+finite[key]*np.outer(a, b)
    return tensor@(ETA*current)


def tensor_summary(encoded):
    a = np.asarray(encoded)
    c = a[..., 0]+1j*a[..., 1]
    indices = np.argwhere(abs(c) > np.max(abs(c))*1e-10)
    return dict(shape=list(c.shape), max_abs=float(np.max(abs(c))),
        sha256=hashlib.sha256(json.dumps(encoded, separators=(',', ':')).encode()).hexdigest(),
        components=[dict(index=idx.tolist(), **encode(c[tuple(idx)])) for idx in indices[:4]])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--order', type=int, default=40)
    parser.add_argument('--parent-power', type=int, default=13)
    parser.add_argument('--require-completion', action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    local = HERE/'local'
    local.mkdir(exist_ok=True)
    # Bound the new calculation to the already validated native rules/model.
    native = json.loads((HERE/'native_vertices.json').read_text())
    for path, expected in native['frozen_source_sha256'].items():
        if sha(ROOT/path) != expected:
            raise RuntimeError('Frozen source hash mismatch: '+path)
    poles = exact_uv()
    if any(v != 0 for v in poles['total'].values()):
        raise RuntimeError('Actual regulated inner UV cancellation failed')
    cases, reference_checks, independent_ff = [], [], []
    longitudinal_xi1_residual = 0.
    for index in (0, 1):
        inp = example(index)
        p, ml = inp['physical'], np.array(inp['lepton_masses_GeV'])
        i, j = inp['i'], inp['j']
        Cs = vertices(decode_matrix(inp['D']), p, ml)
        pi, pj, q = decay_momenta(ml[i], ml[j])
        k = np.array([.13, .91, -.37, 1.12])*inp['mw']*(1+index*.3)
        k2, qk = dot(k, k), dot(q, k)
        for xi in (.5, 1., 3.):
            scalar_rows, attached = [], np.zeros((2, 4), complex)
            for name, kap in zip(('h', 'H'), (math.cos(p['beta']-p['alpha']), math.sin(p['beta']-p['alpha']))):
                C, ms = Cs[name]
                result = calculate_longitudinal(mw2=inp['mw']**2, ms2=ms**2,
                    k2=k2, qk=qk, xi=xi, order=args.order)
                scalar_rows.append(dict(scalar=name, kappa=kap,
                    yukawa_L=encode(C[j, i]), yukawa_R=encode(C[i, j].conjugate()), **result))
                for chirality in (0, 1):
                    L, R = (C[j, i], 0.) if chirality == 0 else (0., C[i, j].conjugate())
                    current = outer_current(pi, pj, k, ml[i], ml[j], L, R)
                    attached[chirality] += (inp['alpha_em']*kap/(4*math.pi*p['v'])*
                        attached_inner(result['finite'], q, k, current)/(dot(q+k, q+k)-ms*ms))
                if xi == 1:
                    direct = calculate(mw2=inp['mw']**2, ms2=ms**2, k2=k2, qk=qk, order=args.order)
                    longitudinal_xi1_residual = max(longitudinal_xi1_residual,
                        max(abs(direct['finite'][b]-result['finite'][b]) for b in EXT_BASIS))
                    reference = source_tensors(q, k, ms, mw=inp['mw'], order=args.order)
                    ff = reference['form_factors']
                    predicted = dict(kq=2*ff['A'], kk=2*ff['B'],
                        g=2*(-qk*ff['A']+k2*ff['P']+(k2+2*qk-ms*ms)*ff['C']))
                    reference_checks.append(dict(benchmark=index, scalar=name,
                        native=dict((b, direct['finite'][b]) for b in predicted),
                        source=predicted, residual={b: abs(direct['finite'][b]-predicted[b]) for b in predicted}))
            cases.append(dict(benchmark=index, xi=xi, q_GeV=q.tolist(), k_GeV=k.tolist(),
                input_sha256=hashlib.sha256(json.dumps(inp, sort_keys=True).encode()).hexdigest(),
                scalars=scalar_rows, attached_complex_LR=encode_tensor(attached),
                attached_scope='INNER ONLY at fixed k, spin 0->0; NOT Wilson coefficients or physical amplitude'))
            if xi == 1.:
                us = [(row['finite']['g']+qk*row['finite']['kq'])/2 for row in scalar_rows]
                masses2 = [row['invariants_GeV2']['ms2'] for row in scalar_rows]
                c = -(us[1]-us[0])/(masses2[1]-masses2[0])
                pff = (us[0]-c*(k2+2*qk-masses2[0]))/k2
                independent_ff.append(dict(benchmark=index, A_h=scalar_rows[0]['finite']['kq']/2,
                    A_H=scalar_rows[1]['finite']['kq']/2, B=scalar_rows[0]['finite']['kk']/2,
                    P=pff, C=c, extraction='C from native mass slope of (Tg+q.k Tkq)/2; P from remaining metric coefficient'))
    parent_rows = []
    for index, (mi, mj, r, ms) in enumerate(((3., .7, [.8, 31., -17., 29.], 125.),
                                            (4.1, 1.1, [-.6, -23., 37., 19.], 437.))):
        pi, pj, q = decay_momenta(mi, mj)
        r, mw2 = np.asarray(r), 80.379**2
        closed = calculate_parent(pi, q, r, mw2, order=24)
        all_parents = calculate_native_parents(pi, q, r, mw2, ms*ms, mj, order=16)
        lower = calculate_native_parents(pi, q, r, mw2, ms*ms, mj, order=8)
        left, right = ((.037+.019j, -.021+.043j) if index == 0 else (-.024+.033j, .051-.017j))
        norms = {}
        for sp, block in all_parents.items():
            norms[sp] = dict(finite_block=encode_tensor(block), uv_pole=0,
                max_quadrature_change=float(np.max(abs(block-lower[sp]))),
                attached_complex_LR=[encode_tensor(attach_scalar_leg(block, pi, r, mj, L, R))
                                    for L, R in ((left, 0.), (0., right))],
                external_spin0_amplitudes_LR=[encode_tensor(np.array([
                    bar(spinor(pj, mj, 0))@matrix@spinor(pi, mi, 0)
                    for matrix in attach_scalar_leg(block, pi, r, mj, L, R)]))
                    for L, R in ((left, 0.), (0., right))])
        sampled = []
        for xi in (.5, 1., 3.):
            numerical = calculate_parent_rxi(pi, q, r, mw2, ms*ms, mj, xi=xi,
                power=args.parent_power, replicates=6, seed=16083+100*index)
            sampled.append(dict(xi=xi, finite=encode_tensor(numerical['finite']),
                standard_error=numerical['standard_error'].tolist(), uv_pole=0,
                xi1_parameter_difference=(float(np.max(abs(numerical['finite']-all_parents['WWW'])))
                                          if xi == 1 else None),
                exact_integrand_witness=encode_tensor(exact_parent_integrand([1., 2., 3., 4.], r,
                    pi, q, mw2, ms*ms, mj, left, right, xi=xi))))
        parent_rows.append(dict(benchmark=index, p=pi.tolist(), q=q.tolist(), r=r.tolist(), mw2=mw2,
            ms2=ms*ms, daughter_mass=mj, left=encode(left), right=encode(right),
            scalar_placement='before both weak currents, other placement NOT_EVALUATED',
            normalization='i*e*g2^2*kappa/(32*pi^2*v); fixed r; no outer scalar/charged propagators',
            parents_xi1=norms, WWW_rxi_RQMC=sampled,
            WWW_pinch_scalar=closed['pinch_scalar'],
            cancelled_box_scalar=closed['cancelled_box_scalar'],
            pinch_split_residual=closed['integral_split_residual'],
            native_WWW_vs_reduced=float(np.max(abs(all_parents['WWW']-2*mw2*closed['full'])))))
    sources = ['native_integrands.py', 'tensor_reduction.py', 'parent_integrals.py',
               'longitudinal_identities.py', 'regulated_pilot.py', 'test_regulated.py',
               'native_vertices.json', 'st_sources.json', 'extract_st_sources.m', 'check_st_sources.py',
               'matching.py', 'inventory.py']
    hashes = {name: sha(HERE/name) for name in sources}
    output = dict(status='BLOCKED_GAUGE_MATCHING',
        milestones=dict(INNER_XI1='PASS_INNER_SCOPE', LONGITUDINAL_ST='PARTIAL',
            PARENT_COMPLETION='PARTIAL_SUBLOOPS', PHYSICAL_GAUGE_INDEPENDENCE='NOT_EVALUATED'),
        physical=dict(C_L=None, C_R=None, coherent_inclusion=False),
        starting_evidence_commit='4221e39d76a3a1886e7aa7ecefdb06fd54e365ae',
        source_parent_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        code_sha256=hashes, code_bundle_sha256=hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest(),
        environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, sympy=sympy.__version__),
        exact_uv_poles={g: {b: str(v) for b, v in p.items()} for g, p in poles['graphs'].items()},
        exact_uv_sum={b: str(v) for b, v in poles['total'].items()},
        xi1_longitudinal_vs_direct_max_abs=longitudinal_xi1_residual,
        xi1_reference_checks=reference_checks, xi1_independently_extracted_APBC=independent_ff,
        inner_cases=cases, parent_cases=parent_rows,
        new_ST_sources_sha256=sha(HERE/'st_sources.json'), parent_term_ledger=PARENT_TERMS,
        missing=dict(first_integrand='parent_integrals.exact_parent_integrand',
            exact_outer='integral d^d r d^d l: three bosons, massless neutrino, S_j(p-r) X_s/(r^2-Ms^2)',
            obstruction='No complete d-dimensional outer projection plus crossed scalar placement, charged-H parents and BRST/LSZ subtraction. Finite inner subloops do not provide their missing O(eps) terms when outer UV poles occur.',
            projected_Delta_xi_remaining_LR=None, compensator_injected=False),
        elapsed_s=time.monotonic()-start, peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    detail = local/'regulated-details.json'
    detail.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False)+'\n')
    compact = copy.deepcopy(output)
    compact['full_tensor_details'] = dict(path='local/regulated-details.json', sha256=sha(detail),
                                         reproduction='python3 -m research.wgamma_d16.regulated_pilot')
    compact['logs'] = {name: sha(local/name) for name in ('regulated-tests.log', 'st-checks.log',
                       'st-sources.log') if (local/name).exists()}
    for case in compact['parent_cases']:
        for block in case['parents_xi1'].values():
            block['finite_block'] = tensor_summary(block['finite_block'])
            block['attached_complex_LR'] = list(map(tensor_summary, block['attached_complex_LR']))
        for row in case['WWW_rxi_RQMC']:
            row['finite'] = tensor_summary(row['finite'])
            row['standard_error_max'] = float(np.max(row.pop('standard_error')))
            row['exact_integrand_witness'] = tensor_summary(row['exact_integrand_witness'])
    (HERE/'gauge_ledger.json').write_text(json.dumps(compact, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps(dict(status=output['status'], exact_uv_sum=output['exact_uv_sum'],
          cases=len(cases), scalar_integrals=sum(len(c['scalars']) for c in cases),
          parent_benchmarks=len(parent_rows), elapsed_s=output['elapsed_s'],
          ledger_sha256=sha(HERE/'gauge_ledger.json')), indent=2))
    return 2 if args.require_completion else 0


if __name__ == '__main__':
    raise SystemExit(main())
