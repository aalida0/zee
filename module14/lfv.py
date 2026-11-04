"""D12/Module4 coherent partial LFV observables; diagnostic comparisons only."""
import json
import hashlib
from pathlib import Path
import numpy as np

from module2.interface import canonical_hash, decode, evaluate as neutrino_evaluate
from module3 import tree
from module3.core import vertices
from module4.interface import evaluate as lfv_evaluate
from module12.study import module3_input

ROOT = Path(__file__).resolve().parents[1]
LIMITS = {'version': 'D12_experimental_reference_2026-11-03',
          'mu_to_e_gamma': {'upper_limit': 1.5e-13, 'confidence_level': 0.90,
                            'source': 'https://arxiv.org/abs/2504.15711v2'},
          'mu_to_3e_tree': {'upper_limit': 1e-12, 'confidence_level': 0.90,
                            'source': 'SINDRUM Bellgardt et al., NPB299 (1988) 1; PDG 2026'}}


def evaluate_family(family, tree_enabled=False):
    inp = family['input']
    if canonical_hash(inp) != family['input_sha256']:
        raise ValueError('Neutrino input hash mismatch')
    nout = neutrino_evaluate(inp)
    for k in ('F', 'D', 'Ye', 'Ye2', 'Mnu'):
        if canonical_hash(nout[k]) != canonical_hash(family[k]):
            raise ValueError('Recomputed Module2 output differs: ' + k)
    data3 = module3_input(inp)
    extra = json.loads((ROOT/'module4/example.json').read_text())['two_loop_inputs']
    extra['mW_GeV'] = inp['scalar']['record']['electroweak']['mW']
    data4 = {'schema_version': '1.0.0', 'kind': 'module3_matching_input_v1',
             'module3_input': data3, 'module2_output': nout, 'two_loop_inputs': extra}
    out = lfv_evaluate(data4)
    channels = {}
    for name, c in out['channels'].items():
        limit = LIMITS.get(name)
        channels[name] = {'partial_BR': c['partial_BR'], 'C_L': c['C_L'], 'C_R': c['C_R'],
                          'comparison': {'status': 'DIAGNOSTIC_ONLY', 'limit': limit,
                                         'partial_to_limit': c['partial_BR']/limit['upper_limit'] if limit else None,
                                         'reason': 'Incomplete amplitudes' if limit else 'No D12 reference limit supplied'},
                          'omitted_topologies': {k: v['status'] for k, v in c['omitted_topologies'].items()}}
    tree_result = {'status': 'NOT_EVALUATED', 'reason': 'Optional three-body calculation disabled'}
    if tree_enabled:
        p = inp['scalar']['record']['physical']
        ml = np.array(inp['lepton_masses_GeV'])
        neutral = vertices(decode(nout['D']), p, ml)
        widths = [tree.width(neutral, 1, 0, 0, ml, order) for order in (24, 48)]
        change = abs(widths[1]-widths[0])/max(widths[1], 1e-300)
        if change > data3['numerics']['tree_relative_tolerance']:
            raise ArithmeticError('mu3e quadrature not converged')
        br = widths[1]/data3['constants']['total_lepton_widths_GeV'][0]
        tree_result = {'status': 'PASS', 'tree_subset_BR': br, 'quadrature_relative_change': change,
                       'comparison': {'status': 'DIAGNOSTIC_ONLY', 'limit': LIMITS['mu_to_3e_tree'],
                                      'partial_to_limit': br/LIMITS['mu_to_3e_tree']['upper_limit']}}
    return {'status': 'PARTIAL', 'comparison_status': 'DIAGNOSTIC_ONLY', 'channels': channels,
            'mu_to_3e': tree_result, 'complete_lfv': False,
            'module2_input_sha256': family['input_sha256'], 'module2_output_sha256': canonical_hash(nout),
            'module4_input_sha256': canonical_hash(data4), 'module4_output_sha256': canonical_hash(out),
            'module4_provenance': out['provenance'],
            'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in [Path(__file__), ROOT/'module12/study.py', ROOT/'module3/example.json', ROOT/'module4/example.json',
                                        *sorted((ROOT/'module3').glob('*.py')), *sorted((ROOT/'module4').glob('*.py'))]},
            'limit_dataset': LIMITS,
            'limit_dataset_sha256': canonical_hash(LIMITS),
            'missing_contributions': out['missing_contributions']}
