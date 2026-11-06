"""Finite joint LO-NP response audit using existing binaries; no theory bound."""
import json
import math
from m2026_route import HERE, ROOT, digest


def response(points, field, h=.01):
    """B=B0+s7*c7+s8*c8+q77*c7^2+q78*c7*c8+q88*c8^2.

    q78 is the polynomial cross coefficient, not the off-diagonal tensor entry.
    """
    def b(x, y):
        return points[x, y][field]
    b0 = b(0., 0.)
    s7 = (b(h, 0.) - b(-h, 0.)) / (2*h)
    s8 = (b(0., h) - b(0., -h)) / (2*h)
    q77 = ((b(h, 0.) + b(-h, 0.))/2 - b0) / h**2
    q88 = ((b(0., h) + b(0., -h))/2 - b0) / h**2
    q78 = (b(h, h) - b(h, -h) - b(-h, h) + b(-h, -h)) / (4*h*h)
    def residual(x, y):
        return b(x, y) - (b0+s7*x+s8*y+q77*x*x+q78*x*y+q88*y*y)
    return {'baseline_BR': b0, 'slope_C7': s7, 'slope_C8': s8,
            'quadratic_C7_squared': q77, 'quadratic_C7_C8': q78,
            'quadratic_C8_squared': q88,
            'fit_grid_max_abs_residual': max(abs(residual(x,y)) for x,y in points
                                            if abs(x) <= h and abs(y) <= h),
            'held_out_residuals': [{'DeltaC7': x, 'DeltaC8': y, 'BR_residual': residual(x,y)}
                                  for x,y in points if abs(x) > h or abs(y) > h]}


def run():
    # Lazy imports keep the equation adapter independent of external runtimes.
    from final_validation import Native, ZERO, compare, digest_parameters
    import numpy as np
    old = json.loads((HERE / 'final_validation.json').read_text())
    digest_parameters()
    for name, info in old['builds']['builds'].items():
        if digest(HERE / ('local/final_si_'+name+'_probe')) != info['binary_sha256']:
            raise RuntimeError('Preserved SuperIso binary changed')
    provenance = json.loads((HERE/'bridge_sources.json').read_text())
    if digest(HERE/'local/eos_evolve_probe.so') != provenance['native_wrapper_sha256']:
        raise RuntimeError('Preserved EOS evolution binary changed')
    for name, expected in provenance['installed_sha256'].items():
        if digest(HERE/'local/venv/lib/python3.10/site-packages'/name) != expected:
            raise RuntimeError('Pinned runtime changed: '+name)
    z = old['benchmarks']['zero_NP']['SuperIso']
    sm = np.array(old['SM_ordinary_low_from_SI'])
    n = Native(); n.as0 = z['alpha_s_mu0']; n.asb = z['alpha_s_mu_b']
    points = {}
    for x,y,label in [(0.,0.,'zero_NP'),(.01,0.,'C7_+1'),(-.01,0.,'C7_-1'),
                      (0.,.01,'C8_+1'),(0.,-.01,'C8_-1')]:
        points[x,y] = {'raw': old['benchmarks'][label], 'origin': 'preserved:'+label}
    for x,y in [(-.01,-.01),(-.01,.01),(.01,-.01),(.01,.01),(-.017,.023),(.026,-.019)]:
        raw = {**ZERO, 'C7_LO': x, 'C8_LO': y}
        points[x,y] = {'raw': compare(raw, n, old['shared_EOS_parameter_overrides'], sm,
                                    old['EOS_SM_BR_common_low_card']), 'origin': 'executed'}
    rows = {}
    for key, item in points.items():
        r = item['raw']
        if any(r['raw_matching'][k] != 0 for k in ('C4_NLO_raw','C7_NLO_raw','C8_NLO_raw')):
            raise RuntimeError('NP matching orders mixed')
        rows[key] = {'DeltaC7': key[0], 'DeltaC8': key[1], 'origin': item['origin'],
                     'EOS': r['EOS_BR_EOS_evolved_NP'], 'SuperIso_D9B': r['SuperIso']['NP_BR_NLO']}
    result = {'status': 'DIAGNOSTIC_ONLY', 'remainder_certified': False,
              'accuracy_domain': 'VALIDITY_DOMAIN_UNKNOWN',
              'definition': 'Raw BR polynomial; slopes dBR/dDeltaCi, q78 multiplies c7*c8 (tensor off-diagonal=q78/2). No SM rebasing.',
              'input_order': 'Ordinary NP C7_LO,C8_LO at 160 GeV only; all NP NLO inputs zero',
              'mu0_GeV': 160., 'mu_b_GeV': 4.2, 'photon_cut_GeV': 1.6,
              'step': .01, 'fit_points': 9, 'held_out_points': 2,
              'reused_points': 5, 'new_joint_or_holdout_points': 6,
              'EOS_version': '1.0.21', 'SuperIso_version': '5.0 with exact frozen D9B patch',
              'source_build_provenance': {f: digest(HERE / f) for f in
                  ('final_validation.json','bridge_results.json','final_sources.json','requirements.lock',
                   'bridge.py','eos_evolve_probe.cc','final_superiso_probe.c','m2026_legacy.py')},
              'binary_sha256': {'EOS_evolve': digest(HERE/'local/eos_evolve_probe.so'),
                               'SuperIso_D9B': digest(HERE/'local/final_si_d9b_probe')},
              'common_parameters': old['shared_EOS_parameter_overrides'],
              'SM_low_vector': sm.tolist(),
              'prescription_differences': old['comparison_card_status'],
              'responses': {field: response(rows,field) for field in ('EOS','SuperIso_D9B')},
              'points': list(rows.values()),
              'preserved_C4_NLO_and_matching_sensitivity': {
                  'source': 'final_validation.json signed_high_scale_responses; bridge_results.json records',
                  'qualification': 'Existing NLO/C4 sensitivity is not a complete omitted-term bound; not reexecuted.'}}
    (HERE/'m2026_legacy_results.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(result['responses'], indent=2))


if __name__ == '__main__':
    run()
