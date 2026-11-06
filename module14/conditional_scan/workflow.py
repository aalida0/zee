"""Join complete, receipt-checked D14 outputs to conditional flavor/cascade data.

Usage: python -m module14.conditional_scan.workflow --help
"""
import argparse
from collections import Counter
import json
import math
from pathlib import Path

from module5.hyperiso_patch_contract import unique_pairs
from module7.cascade_z import cascade_width
from module7.d4_decay_table import complete_total
from module7.d4_inputs import SM
from module14.collect import collect
from module14.scan import digest, file_sha
from .flavor import evaluate, finite_real, source_hashes


def load(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=unique_pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON '+x)))


def lines(path):
    with open(path) as f:
        for line in f:
            yield json.loads(line, object_pairs_hook=unique_pairs,
                             parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON '+x)))


def production(path, scalar, family):
    """Explicit per-family H2 production contract; artifacts must be available."""
    if path is None or not Path(path).exists():
        return {'status': 'NOT_EVALUATED', 'reason': 'No documented same-point production supplied'}
    path = Path(path)
    row = load(path)
    expected = {'scalar_sha256': digest(scalar), 'yukawa_sha256':
                {k: digest(family[k]) for k in ('F', 'D', 'Ye', 'Ye2')},
                'module2_input_sha256': family['input_sha256']}
    if any(row.get(k) != v for k, v in expected.items()):
        raise ValueError('Production point identity mismatch')
    for k in ('energy_TeV', 'sigma_pb'):
        if finite_real(row[k], k) < 0 or (k == 'energy_TeV' and row[k] == 0):
            raise ValueError('Invalid production input')
    if row['state'] != 'H2' or row['model'] != 'ZeeTypeII':
        raise ValueError('Wrong production state/model')
    for k in ('process', 'charge_definition', 'order', 'pdf', 'scale_scheme', 'documentation', 'uncertainty'):
        if not isinstance(row.get(k), str) or not row[k].strip():
            raise ValueError('Missing production documentation: '+k)
    if not isinstance(row.get('artifacts_sha256'), dict) or not row['artifacts_sha256']:
        raise ValueError('Missing production artifacts')
    for name, sha in row['artifacts_sha256'].items():
        artifact = (path.parent/name).resolve()
        if path.parent.resolve() not in artifact.parents or file_sha(artifact) != sha:
            raise ValueError('Invalid production artifact: '+name)
    return dict(row, status='SUPPLIED_DOCUMENTED', input_file_sha256=file_sha(path))


def cascade(scalar, family, widths):
    p = scalar['physical']
    # D4 uses its frozen SM card; do not mix it with another EW card.
    result = cascade_width({'mH1_GeV': p['mH1'], 'mH2_GeV': p['mH2'],
                            'gamma_rad': p['gamma'], 'v_GeV': p['v'],
                            'mW_GeV': SM['EW']['mW'], 'mZ_GeV': SM['EW']['mZ']})
    result.update(BR_H2_H1Z=None, br_status='NOT_EVALUATED', scope='D4 complete on-shell tree two-body only; off-shell/loop and decay uncertainties unknown')
    if widths is None or widths.get('status') != 'PASS':
        return result
    if (widths['scalar_sha256'] != digest(scalar) or
        widths['module2_input_sha256'] != family['input_sha256'] or
        widths['yukawa_sha256'] != {k: digest(family[k]) for k in ('F', 'D', 'Ye', 'Ye2')} or
        widths['sm_card_sha256'] != digest(SM)):
        raise ValueError('Decay identity mismatch')
    for name, sha in widths['source_sha256'].items():
        root = Path(__file__).resolve().parents[2]
        source = (root/name).resolve()
        if root not in source.parents or file_sha(source) != sha:
            raise ValueError('Decay source identity changed: '+name)
    for state in (1, 2):
        mother = widths['mothers'][f'H{state}']
        total = complete_total(mother['channels'], state)
        if total != mother['total']:
            raise ValueError('Stored decay total mismatch')
        if total['status'] != 'D4_COMPLETE_TWO_BODY_BR_PASS':
            return result
    heavy = widths['mothers']['H2']
    partial = next(r['width_GeV'] for r in heavy['channels'] if r['channel'] == 'H1 Z')
    if not math.isclose(partial, result['partial_width_GeV'], rel_tol=2e-13, abs_tol=1e-14):
        raise ValueError('Cascade partial-width mismatch')
    br = partial/heavy['total']['total_width_GeV']
    if not math.isclose(br, heavy['br_H1_Z'], rel_tol=2e-13, abs_tol=1e-15):
        raise ValueError('Cascade BR mismatch')
    result.update(BR_H2_H1Z=br, br_status='PASS', total_width_GeV=heavy['total']['total_width_GeV'])
    return result


def join(manifest, config, triples, card, source_commit, source_bundle_sha256,
         families=2, production_dir=None):
    if not source_commit or not source_bundle_sha256:
        raise ValueError('Explicit worker source identity required')
    audit = collect(manifest, config, triples, families=families,
                    source_commit=source_commit, source_bundle_sha256=source_bundle_sha256)
    if audit['status'] != 'COMPLETE' or audit['missing_points']:
        raise ValueError('Complete collection required before interpretation')
    inputs = {row['id']: row for row in lines(manifest)}
    rows, by_arm = [], {}
    for _, output, _ in triples:
        for out in lines(output):
            row = inputs[out['id']]
            scalar = row['scalar']
            flavor = evaluate(scalar, card)
            p = scalar['physical']
            arm = by_arm.setdefault(row['arm'], {'proposals': 0, 'stages': {}})
            arm['proposals'] += 1
            def count(stage, status):
                c = arm['stages'].setdefault(stage, Counter())
                c[status] += 1
            for k, v in out['gates'].items(): count(k, v['assessment'])
            count('conditional_bsgamma', flavor['bsg_nominal_classification'])
            ns = out['neutrino']
            if not isinstance(ns, list):
                for ordering in ('NO', 'IO'):
                    for _ in range(families): count('neutrino_'+ordering, 'NOT_EVALUATED')
                ns = [None]
            for family in ns:
                entry = {'id': row['id'], 'arm': row['arm'], 'input_card': scalar,
                         'scalar_sha256': row['scalar_sha256'], 'gates': out['gates'],
                         'scalar_status': out['scalar_status'], 'flavor': flavor,
                         'neutral_spectrum_GeV': {k: p[k] for k in ('mh1', 'mh2', 'ma')},
                         'bsg_physical_classification': 'UNKNOWN', 'np_theory_sigma': None,
                         'bsg_exclusion': None, 'globally_allowed': None,
                         'rank': None, 'yield_proxy_pb': None,
                         'label': 'Conditional benchmark requiring further flavor/vacuum/LFV validation'}
                if family is None:
                    entry.update(neutrino='NOT_EVALUATED', widths='NOT_EVALUATED',
                                 lfv='NOT_EVALUATED', higgstools='NOT_EVALUATED',
                                 production=production(None, scalar, None), cascade=None)
                else:
                    count('neutrino_'+family['ordering'], family['status'])
                    def stage(name):
                        data = out.get(name)
                        return next((v for v in data if (v['ordering'], v['family']) ==
                                     (family['ordering'], family['family'])), None) if isinstance(data, list) else None
                    widths = stage('widths')
                    decays = cascade(scalar, family, widths)
                    prodfile = Path(production_dir)/(family['input_sha256']+'.json') if production_dir else None
                    prod = production(prodfile, scalar, family)
                    entry.update(neutrino=family, widths=widths or 'NOT_EVALUATED',
                                 lfv=stage('lfv') or 'NOT_EVALUATED',
                                 higgstools=stage('higgstools') or 'NOT_EVALUATED',
                                 production=prod, cascade=decays)
                    hard_failure = any(v['assessment'] in ('FAIL', 'ERROR') for v in out['gates'].values())
                    if (not hard_failure and family['status'] == 'PASS' and family['closure_status'] == 'PASS'
                        and decays['is_kinematically_open'] and decays['br_status'] == 'PASS'
                        and decays['partial_width_GeV'] > 0 and prod['status'] == 'SUPPLIED_DOCUMENTED'):
                        entry['yield_proxy_pb'] = finite_real(prod['sigma_pb']*decays['BR_H2_H1Z'], 'yield proxy')
                        entry['comparison_group'] = {k: prod[k] for k in
                            ('energy_TeV', 'process', 'charge_definition', 'order', 'pdf', 'scale_scheme')}
                rows.append(entry)
    groups = {}
    for row in rows:
        if row['yield_proxy_pb'] is not None:
            groups.setdefault(digest(row['comparison_group']), []).append(row)
    for group in groups.values():
        for rank, row in enumerate(sorted(group, key=lambda r: -r['yield_proxy_pb']), 1): row['rank'] = rank
    return {'status': 'CONDITIONAL_DATASET', 'collection': audit, 'by_arm': by_arm,
            'proposal_interpretation': 'Arm-dependent proposal counts, not model-volume fractions',
            'source_sha256': source_hashes(), 'matching_card_sha256': digest(card),
            'input_files_sha256': {str(p): file_sha(p) for t in triples for p in t},
            'globally_allowed': None, 'rows': rows,
            'ranking_scope': 'Within documented energy/process/charge/order/PDF/scale group; no flavor hard cut; missing production/complete BR remains unranked.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('manifest', 'config', 'matching-card', 'source-commit', 'source-bundle-sha256', 'output'):
        parser.add_argument('--'+name, required=True)
    parser.add_argument('--part', nargs=3, action='append', required=True)
    parser.add_argument('--families', type=int, default=2)
    parser.add_argument('--production-dir')
    a = parser.parse_args()
    result = join(a.manifest, load(a.config), a.part, load(a.matching_card),
                  a.source_commit, a.source_bundle_sha256, a.families, a.production_dir)
    with open(a.output, 'x') as f: json.dump(result, f, sort_keys=True, indent=2, allow_nan=False); f.write('\n')


if __name__ == '__main__': main()
