"""Read-only C1 audit adapter. No uncertainty model or operative scan filter."""
import hashlib
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from module5.bsgamma_2026_linear_diagnostic import eq4_conditional, run_contract
from module5.hyperiso_patch_contract import make_contract

RESULT = 'M2026_DIAGNOSTIC_ONLY_AUTHOR_INPUT_REQUIRED'
MT = 163.96892236746697  # Frozen C1 input; not refitted to 2026 SM inputs.


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(data):
    return json.dumps(data, sort_keys=True, allow_nan=False).encode()


def source_hashes():
    files = ['module5/bsgamma_2026_linear_diagnostic.py', 'module5/bsgamma_lo.py',
             'module5/hyperiso_patch_contract.py', 'scripts/zee_module5_bmu_nlo.py',
             'validation/module5/linear_2026.json', 'validation/module5/scan_triage.json',
             'validation/module5/accuracy_2026.json']
    files += [str((HERE / name).relative_to(ROOT)) for name in
              ('m2026_route.py', 'm2026_sources.json')]
    return {f: digest(ROOT / f) for f in files}


def linear_audit(delta_c7, delta_c8):
    """Only ordinary, real, alpha_s^0 NP dipoles at 160 GeV are accepted."""
    terms = eq4_conditional(delta_c7, delta_c8)
    return {'DeltaC7': delta_c7, 'DeltaC8': delta_c8,
            'BR_linear_2026': terms['conditional_B_times_1e4'] * 1e-4,
            'signed_C7_BR_contribution': terms['C7_linear_term_times_1e4'] * 1e-4,
            'signed_C8_BR_contribution': terms['C8_linear_term_times_1e4'] * 1e-4,
            'status': 'DIAGNOSTIC_ONLY', 'classification': 'UNKNOWN',
            'validity_domain': 'VALIDITY_DOMAIN_UNKNOWN', 'exclusion': None,
            'NP_theory_sigma': None, 'complete_remainder_bound': None}


def audit_point(mH1_GeV, mH2_GeV, tanbeta, gamma_rad, mt_MSbar_GeV=MT,
                matching_scale_GeV=160.):
    if isinstance(tanbeta, bool) or not isinstance(tanbeta, (float, int)) or not math.isfinite(tanbeta) or tanbeta <= 0:
        raise ValueError('Positive finite real tanbeta required')
    data = dict(mH1_GeV=mH1_GeV, mH2_GeV=mH2_GeV,
                beta_rad=math.atan(tanbeta), gamma_rad=gamma_rad,
                mt_MSbar_GeV=mt_MSbar_GeV, matching_scale_GeV=matching_scale_GeV)
    # Reuse the audited coherent LO matching and strict C1 convention/scale gate.
    raw = encoded(data)
    contract = make_contract(data)
    contract['input_sha256'] = hashlib.sha256(raw).hexdigest()
    c1 = run_contract(contract, raw)
    r = linear_audit(**{'delta_c7': c1['shift_input']['DeltaC7'],
                       'delta_c8': c1['shift_input']['DeltaC8']})
    return {**r, 'input': {**data, 'tanbeta': tanbeta},
            'input_sha256': contract['input_sha256'],
            'input_hash_encoding': 'sorted Python JSON of six matching inputs, UTF-8',
            'weighted_per_state_LO': contract['coefficients'],
            'coefficient_order': 'ALPHA_S_0', 'basis': 'ordinary unprimed Eq.(2)',
            'photon_cut_GeV': 1.6, 'source': 'arXiv:2608.29863v1 p.4 Eq.(4)',
            'source_hashes': source_hashes()}


def run():
    rows = []
    for m1 in (300., 550., 900.):
        for m2 in (700., 900., 1400.):
            if m1 > m2:
                continue
            for tb in (2., 5.3, 50.):
                for gamma in (0., 1.09, math.pi / 2):
                    rows.append(audit_point(m1, m2, tb, gamma))
    example = audit_point(550., 900., 5.3, 1.09)
    c1 = json.loads((ROOT / 'validation/module5/linear_2026.json').read_text())
    prior = c1['reference_run']['diagnostic']['linearized']['conditional_B_times_1e4'] * 1e-4
    residual = example['BR_linear_2026'] - prior
    if abs(residual) > 1e-17:
        raise RuntimeError('Frozen C1 reference not reproduced')
    decoupling = audit_point(1e5, 1e5, 5.3, 1.09)
    result = {'classification': RESULT, 'status': 'DIAGNOSTIC_ONLY',
              'validity_domain': 'VALIDITY_DOMAIN_UNKNOWN', 'exclusion': None,
              'NP_theory_sigma': None, 'scan_filter_created': False,
              'confidence_test': 'NOT_EVALUATED',
              'published_values': {'SM_BR': 3.54e-4, 'SM_reported_sigma': .14e-4,
                                   'experimental_BR': 3.49e-4, 'experimental_reported_sigma': .19e-4,
                                   'source': '2608.29863v1 Eqs.(1),(3)',
                                   'NP_uncertainty_or_covariance': 'UNKNOWN'},
              'source_audit': json.loads((HERE / 'm2026_sources.json').read_text()),
              'top_mass_provenance': c1['matching_mass_provenance'],
              'frozen_C1_reference': example, 'C1_reference_BR_residual': residual,
              'zero_NP': linear_audit(0., 0.), 'decoupling_100TeV': decoupling,
              'grid': rows, 'grid_summary': {'points': len(rows),
                  'minimum_BR_linear': min(r['BR_linear_2026'] for r in rows),
                  'maximum_BR_linear': max(r['BR_linear_2026'] for r in rows),
                  'UNKNOWN_count': len(rows)},
              'D14_points': [],
              'D14_points_note': 'Pilot summary specifies IDs/rates only; no fully specified matching card imported.',
              'legacy_response': json.loads((HERE / 'm2026_legacy_results.json').read_text()),
              'legacy_response_sha256': digest(HERE / 'm2026_legacy_results.json'),
              'source_hashes': source_hashes()}
    (HERE / 'm2026_route_results.json').write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({'classification': RESULT, **result['grid_summary'],
                      'reference_BR': example['BR_linear_2026']}))


if __name__ == '__main__':
    run()
