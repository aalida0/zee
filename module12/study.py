"""Same-input D12 observables; frozen Modules 0--11 are read-only.

python3 -m module12.study evaluates 112 controlled solutions, then runs the
complete Module3 interface for four physics-chosen finalists in each group.
"""
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from module11.d11b_offline_fit import (scalar_records, target_specs, inverse_input,
                                      execute, file_hash)
from module2.interface import canonical_hash, decode, encode as encode2
from module3 import tree
from module3.core import vertices, radiative_width, universality
from module3.interface import evaluate as lfv3, encode
from module4.interface import evaluate as lfv4
from module7.d4_inputs import native_card, SM
from module7.d4_native import expected_coefficients
from module7.d4_decay_table import nonleptonic, leptons, complete_total

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT/'validation/module12/local'
OUTPUT = ROOT/'validation/module12/d12_benchmarks.json'
SEED = 121103


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False)+'\n')


def module3_input(inp):
    base = json.loads((ROOT/'module3/example.json').read_text())
    base.update(benchmark_id=inp['benchmark_id'], module2_input=inp)
    return base


def proposals(scalar, ordering):
    """28 designs/group: F/D balance, homogeneous direction, nuisance diversity."""
    spec = target_specs(ordering)[4]
    cone = dict(t=dict(real=.25, imag=.1), scale=.001, root=0,
                chart=[0, 1, 2], phase_rad=.43)
    direction = np.array([1+2j, -2+.5j, .7-1j, -.3+.8j])
    direction /= np.linalg.norm(direction)
    for scale in (1e-7, 1e-6, 1e-5, 1e-4, .001, .01, .1):
        yield 'scale_'+str(scale), spec, inverse_input(
            scalar, ordering, spec, dict(cone, scale=scale), np.zeros(4))
    for amplitude in (1e-4, .001, .01, .1, .3, 1.):
        yield 'hom_'+str(amplitude), spec, inverse_input(
            scalar, ordering, spec, cone, amplitude*direction)
    rng = np.random.default_rng(SEED+(ordering == 'IO'))
    for i in range(12):
        s = target_specs(ordering)[i % 9]
        c = dict(cone, scale=(1e-4, .001, .01)[i % 3],
                 phase_rad=float(rng.uniform(-math.pi, math.pi)),
                 t=dict(real=float(rng.uniform(-1, 1)), imag=float(rng.uniform(-1, 1))),
                 root=i % 2, chart=list(((0, 1, 2), (1, 2, 0), (2, 0, 1))[i % 3]))
        z = (0., 1e-4, .01, .1)[i % 4]*(rng.uniform(-1, 1, 4)+1j*rng.uniform(-1, 1, 4))
        yield 'diverse_'+str(i), s, inverse_input(scalar, ordering, s, c, z)
    # Minimum-norm complex least squares in the *native* four-dimensional
    # homogeneous basis. Suppress the two direct e-mu entries without changing
    # the neutrino target. Check all actual outputs again through Module2.
    for scale in (.0001, .001, .01):
        c = dict(cone, scale=scale)
        base = inverse_input(scalar, ordering, spec, c, np.zeros(4))
        _, out = execute(base)
        d0 = decode(out['inverse']['D0'])
        basis = decode(out['inverse']['homogeneous'], (4, 3, 3))
        a = np.array([basis[:, 0, 1], basis[:, 1, 0]])
        z = np.linalg.lstsq(a, -np.array([d0[0, 1], d0[1, 0]]), rcond=None)[0]
        if np.linalg.norm(z) > .01:
            raise ValueError('Texture construction outside bounded coefficient norm')
        base['homogeneous_coefficients'] = encode2(z)
        yield 'texture_'+str(scale), spec, base


def decays(inp, nout):
    """Reevaluate the general D4 dictionary, never reuse historical BRs.

    expected_coefficients was tested against native SARAH at generic angles
    and complex matrices in D4. This is an analytic application of that frozen
    dictionary, not a fresh SARAH export at the D10 points.
    """
    evidence = json.loads((ROOT/'validation/module7/d4_native_validation.json').read_text())
    for name, digest in evidence['source_sha256'].items():
        if file_hash(name) != digest:
            raise ValueError('D4 native source identity changed: '+name)
    p = inp['scalar']['record']['physical']
    result = {}
    for k in (1, 2):
        card = native_card(p, nout, p[f'mH{k}'], 'D12')
        cs = expected_coefficients(card)
        case = {'coefficients': [[dict(real=c.real, imag=c.imag) for c in row] for row in cs]}
        rows = nonleptonic(p, case, k)+leptons(p, case, k)
        total = complete_total(rows, k)
        if total['status'] != 'D4_COMPLETE_TWO_BODY_BR_PASS':
            raise ValueError('Incomplete D4 inventory')
        result[f'H{k}'] = dict(total=total, channels=rows)
    return result


def signed_summary(out, inp):
    """Retain each signed complex contribution and exact rate interference."""
    ml = inp['module2_input']['lepton_masses_GeV']
    c = inp['constants']
    result = {}
    for name, i, j in [('mu_to_e_gamma', 1, 0), ('tau_to_e_gamma', 2, 0), ('tau_to_mu_gamma', 2, 1)]:
        channel = out['channels'][name]
        pairs = {k: np.array([complex(**row[x]) for x in ('C_L', 'C_R')])
                 for k, row in channel['ledger'].items()}
        diag = {k: radiative_width(v, ml[i], ml[j], c['alpha_em'])/
                c['total_lepton_widths_GeV'][i-1] for k, v in pairs.items()}
        grouped = {}
        for key, pair in pairs.items():
            group = ('scalar_one_loop' if key.startswith('module3_') else
                     'charged_scalar_photon_BZ' if key.endswith('_scalar_gamma') else 'fermion_photon_BZ')
            grouped[group] = grouped.get(group, np.zeros(2, complex))+pair
        group_diag = {k: radiative_width(v, ml[i], ml[j], c['alpha_em'])/
                      c['total_lepton_widths_GeV'][i-1] for k, v in grouped.items()}
        interference = []
        for ka, a in grouped.items():
            for kb, b in grouped.items():
                if ka >= kb:
                    continue
                cross = (radiative_width(np.array(a)+b, ml[i], ml[j], c['alpha_em'])/
                         c['total_lepton_widths_GeV'][i-1]-group_diag[ka]-group_diag[kb])
                interference.append(dict(a=ka, b=kb, signed_BR=cross))
        result[name] = dict(BR_implemented=channel['partial_BR'],
                            C_L=channel['C_L'], C_R=channel['C_R'],
                            signed_amplitudes={k: {x: row[x] for x in ('C_L', 'C_R')}
                                               for k, row in channel['ledger'].items()},
                            isolated_BR=diag, grouped_amplitudes=encode(grouped),
                            grouped_BR=group_diag, interference=interference,
                            coherence_ratio=channel['partial_BR']/sum(diag.values()))
    return result


def evaluate_case(inp, full_tree=False):
    metrics, nout = execute(inp)  # frozen 2e-9 closure check, never relaxed
    if not metrics['selection']['below_one']:
        raise ValueError('D12 design requires every Yukawa element <1')
    data3 = module3_input(inp)
    extra = json.loads((ROOT/'module4/example.json').read_text())['two_loop_inputs']
    data4 = dict(schema_version='1.0.0', kind='module3_matching_input_v1',
                 module3_input=data3, module2_output=nout, two_loop_inputs=extra)
    out4 = lfv4(data4)  # includes Module3 dipole ONCE; W candidates excluded
    p = inp['scalar']['record']['physical']
    ml = np.array(inp['lepton_masses_GeV'])
    neutral = vertices(decode(nout['D']), p, ml)
    widths = [tree.width(neutral, 1, 0, 0, ml, order) for order in (24, 48)]
    change = abs(widths[1]-widths[0])/max(widths[1], 1e-300)
    if change > data3['numerics']['tree_relative_tolerance']:
        raise ArithmeticError('mu3e quadrature not converged')
    result = dict(metrics=metrics, module2_input=inp, module2_output_sha256=canonical_hash(nout),
                  yukawa_sha256={k: canonical_hash(nout[k]) for k in ('F', 'D', 'Ye', 'Ye2')},
                  radiative={k: v['partial_BR'] for k, v in out4['channels'].items()},
                  mu_to_3e_tree=widths[1]/data3['constants']['total_lepton_widths_GeV'][0],
                  tree_quadrature_relative_change=change,
                  universality=encode(universality(decode(nout['F']), p, data3['constants']['GF_GeV_minus2'])),
                  decays=decays(inp, nout), module4_output_sha256=canonical_hash(out4))
    if full_tree:
        out3 = lfv3(data3)
        # Independent interface replay also checks Module3 signed ledger identity.
        data4['module3_output'] = out3
        replay = lfv4(data4)
        if replay['channels'] != out4['channels']:
            raise ValueError('Double-counting or Module3 ledger mismatch')
        result.update(signed_radiative=signed_summary(out4, data3),
                      tree_observables={k: v for k, v in out3['observables'].items()
                                        if v['physical_status'] == 'TREE_SUBSET_ONLY'},
                      module3_output_sha256=canonical_hash(out3),
                      yukawas={k: nout[k] for k in ('F', 'D', 'Ye', 'Ye2')})
        if out3['gates']['tree'] != 'PASS':
            raise ArithmeticError('Finalist tree quadrature incomplete')
    return result


def cascade_product(row):
    d = row['decays']
    return (d['H2']['total']['branching_fractions']['H1 Z']*
            d['H1']['total']['branching_fractions']['t anti-b'])


def run():
    LOCAL.mkdir(parents=True, exist_ok=True)
    scalars, statuses = scalar_records()
    previous = json.loads((ROOT/'validation/module11/d11b_offline_fit.json').read_text())
    groups = []
    allrows = []
    for scalar_name, scalar in scalars.items():
        for ordering in ('NO', 'IO'):
            rows = []
            for name, spec, inp in proposals(scalar, ordering):
                row = evaluate_case(inp)
                row.update(id=scalar_name+'/'+ordering+'/'+name, design=name, target=spec,
                           scalar_sha256=scalar['sha256'])
                # Objective uses separately sourced published measured limits as
                # reference scales only; no likelihood or exclusion operation.
                row['objective'] = max(row['radiative']['mu_to_e_gamma']/1.5e-13,
                                       row['mu_to_3e_tree']/1e-12)
                row['cascade_product'] = cascade_product(row)
                rows.append(row)
                print(row['id'], row['objective'], row['cascade_product'], flush=True)
            reference = next(r for r in rows if r['design'] == 'scale_0.001')
            oldgroup = next(g for g in previous['groups'] if g['benchmark_id'] == scalar_name and g['ordering'] == ordering)
            oldref = oldgroup['witnesses']['reference_bestfit']
            if (reference['metrics']['input_sha256'] != oldref['metrics']['input_sha256'] or
                    reference['yukawa_sha256'] != {k: canonical_hash(oldref['Yukawas'][k])
                                                  for k in ('F', 'D', 'Ye', 'Ye2')}):
                raise ValueError('Central reference differs from D11B witness')
            finalists = {'central': reference,
                         'low_joint': min(rows, key=lambda r: r['objective']),
                         'high_joint': max(rows, key=lambda r: r['objective']),
                         'high_F': next(r for r in rows if r['design'] == 'scale_0.1')}
            witnesses = {}
            for role, row in finalists.items():
                detail = evaluate_case(row['module2_input'], full_tree=True)
                detail.update({k: row[k] for k in ('id', 'design', 'target', 'scalar_sha256', 'objective', 'cascade_product')})
                witnesses[role] = detail
            compact = [{k: r[k] for k in ('id', 'design', 'target', 'metrics', 'radiative', 'mu_to_3e_tree',
                        'tree_quadrature_relative_change', 'module2_output_sha256', 'yukawa_sha256',
                        'module4_output_sha256', 'objective', 'cascade_product')} |
                       {'BR_cascade': r['decays']['H2']['total']['branching_fraction'],
                        'BR_H1_tb': r['decays']['H1']['total']['branching_fractions']['t anti-b'],
                        'max_F': r['metrics']['selection']['max_abs']['F'],
                        'max_D': r['metrics']['selection']['max_abs']['D']} for r in rows]
            groups.append(dict(scalar=scalar_name, ordering=ordering, scalar_sha256=scalar['sha256'],
                               count=len(rows), witnesses=witnesses, family=compact,
                               d11b_reference_group_sha256=canonical_hash(oldgroup)))
            allrows.extend(rows)
            dump(LOCAL/'checkpoint.json', groups)
    dump(LOCAL/'trials.json', allrows)
    sources = ['AGENTS.md', 'module1/d10_benchmarks.json', 'validation/module1/d10_vacuum_global.json',
               'validation/module11/d11b_offline_fit.json', 'module11/d11b_offline_fit.py',
               'module11/nufit61_bestfit_ranges_secondary.json', 'validation/module7/d4_native_validation.json',
               'validation/module5/d9b_superiso_repair.json']
    sources += [str(p.relative_to(ROOT)) for d in ('module2', 'module3', 'module4', 'module7', 'module12')
                for p in sorted((ROOT/d).glob('*.py'))]
    report = dict(schema_version='1.0', seed=SEED, groups=groups, scalar_vacuum_statuses=statuses,
                  source_sha256={p: file_hash(p) for p in sources},
                  trial_log_sha256=hashlib.sha256((LOCAL/'trials.json').read_bytes()).hexdigest(),
                  COMPLETE_LFV=False, global_zee_acceptance=None, mass_exclusion=None,
                  **{'2026_GLOBAL_FLAVOR_FILTER_READY': False},
                  production={'status': 'NOT_EXECUTED', 'sigma_13p6_TeV_pb': None, 'sigma_14_TeV_pb': None,
                              'reason': 'No exact D10 generator/cards/PDF execution or authenticated same-point rate available; D5/D6 700 GeV rates not reused.'},
                  B_to_Xs_gamma={'status': 'NOT_EXECUTED'},
                  accuracy='Implemented signed dipole subset; coherent neutral tree subset; D4 on-shell tree two-body decay dictionary; no complete flavor prediction',
                  objective='Discrete minimum of max(BR_implemented(mu e gamma)/1.5e-13, BR_tree(mu3e)/1e-12) over exactly 28 specified designs/group; no statistical interpretation. Three minimum-norm texture constructions impose D_e_mu=D_mu_e=0 with coefficient norm <0.01.',
                  SM_decay_card=SM)
    dump(OUTPUT, report)


if __name__ == '__main__':
    run()
