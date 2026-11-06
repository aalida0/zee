"""Bounded Stage A experiment. No likelihood, uncertainty assignment or filter."""
import ctypes as ct
import hashlib
import json
import math
import subprocess
import numpy as np
from bridge import Native, KEYS, P
from pilot import HERE, ROOT, digest, eos, eos_rate, matching, write_json

LOCAL = HERE / 'local'
RAW_KEYS = ('C7_LO', 'C8_LO', 'C4_NLO_raw', 'C7_NLO_raw', 'C8_NLO_raw')
ZERO = dict.fromkeys(RAW_KEYS, 0.)


def digest_parameters():
    fingerprint = hashlib.sha256(json.dumps({p.name():p.evaluate() for p in
        eos.Parameters.Defaults()},sort_keys=True).encode()).hexdigest()
    expected = json.loads((HERE/'results.json').read_text())['eos_default_parameters_sha256']
    if fingerprint != expected:
        raise RuntimeError('EOS defaults differ from the pinned prior calculation')
    return fingerprint


def mix(a, b, gamma):
    return {k: math.cos(gamma)**2*a[k]+math.sin(gamma)**2*b[k] for k in a}


def probe(raw, mass=550, tb=5.3, flip=False, original=False):
    exe = LOCAL / ('final_si_original_probe' if original else 'final_si_d9b_probe')
    args = [mass, tb, int(flip), 160, 4.2, *(raw[k] for k in RAW_KEYS)]
    r = subprocess.run([str(exe), *map(str, args)], capture_output=True, text=True, check=True)
    out = dict((k, float(v)) for k, v in (line.split() for line in r.stdout.splitlines()))
    if not all(math.isfinite(x) for x in out.values()):
        raise ValueError('Nonfinite SuperIso result')
    return out


def build_input_inspector():
    src = LOCAL / 'eos-1.0.21'
    libs = LOCAL / 'venv/lib/python3.10/site-packages/_eos_libs'
    cmd = ['g++', '-std=c++20', '-O2', '-shared', '-fPIC', '-I', str(src),
           str(HERE / 'final_eos_inputs.cc'), '-L', str(libs),
           '-Wl,-rpath,$ORIGIN/venv/lib/python3.10/site-packages/_eos_libs',
           '-Wl,--no-as-needed', '-l:libeos.so.0', '-l:libeosmodels.so.0',
           '-l:libeosutils.so.0', '-o', str(LOCAL / 'final_eos_inputs.so')]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr)
    return {'command': cmd, 'exit_code': r.returncode,
            'binary_sha256': digest(LOCAL / 'final_eos_inputs.so')}


def inputs(overrides):
    lib = ct.CDLL(str(LOCAL / 'final_eos_inputs.so'))
    lib.final_eos_inputs.argtypes = [ct.POINTER(ct.c_char_p), P, ct.c_uint, ct.c_double, P]
    lib.final_eos_inputs.restype = ct.c_int
    keys = (ct.c_char_p*len(overrides))(*(k.encode() for k in overrides))
    values = np.array(list(overrides.values()), float); out = np.zeros(6)
    if lib.final_eos_inputs(keys, values.ctypes.data_as(P), len(values), 4.2, out.ctypes.data_as(P)):
        raise RuntimeError('EOS model input inspection failed')
    return dict(zip(('alpha_s_mu_b', 'mb_MSbar_mu_b', 'mb_pole', 'mb_kin_1GeV',
                     'mc_MSbar_mu_b', 'CKM_VtsVtb_squared'), out.tolist()))


def compare(raw, n, common, sm, baseline):
    si = probe(raw)
    si_low = np.array([si[f'NP_ordinary_low_C{i}'] for i in range(1, 9)])
    eos_np = n.np_coefficients(raw)
    # Shared low coefficients are explicitly input to the second kernel once.
    shared = eos_rate({**common, **dict(zip(KEYS, si_low))})
    evolved = eos_rate({**common, **dict(zip(KEYS, sm+eos_np))})
    return {'status': 'DIAGNOSTIC_ONLY', 'physical_agreement': 'NOT_EVALUATED',
            'raw_matching': raw, 'SuperIso': si,
            'EOS_NP_low_C1_to_C8_common_alpha_s': eos_np.tolist(),
            'EOS_minus_SI_NP_low': (eos_np-(si_low-sm)).tolist(),
            'identical_low_total_vector_supplied_to_EOS': si_low.tolist(),
            'EOS_BR_shared_low_vector': shared, 'EOS_BR_EOS_evolved_NP': evolved,
            'EOS_delta_BR_shared_low_vector': shared-baseline,
            'SI_delta_BR': si['NP_BR_NLO']-si['SM_BR_NLO'],
            'signed_BR_residual_EOS_minus_SI': shared-si['NP_BR_NLO'],
            'signed_delta_BR_residual_EOS_minus_SI': shared-baseline-(si['NP_BR_NLO']-si['SM_BR_NLO'])}


def run():
    card = json.loads((HERE / 'final_card.json').read_text())
    sources = json.loads((HERE / 'final_sources.json').read_text())
    for item in sources['downloads']:
        if digest(LOCAL / item['file']) != item['sha256']:
            raise RuntimeError('Pinned source changed: '+item['file'])
    build = json.loads((LOCAL / 'final_build.json').read_text())
    for name, info in build['builds'].items():
        assert digest(LOCAL / ('final_si_'+name+'_probe')) == info['binary_sha256']
        assert digest(HERE / 'final_superiso_probe.c') == info['client_sha256']
    inspector = build_input_inspector()
    si0 = probe(ZERO)
    sm = np.array([si0[f'SM_ordinary_low_C{i}'] for i in range(1, 9)])
    common = {'sb::mu': card['mu_b_GeV'], 'mass::b(MSbar)': si0['mass_b_MSbar'],
              'mass::c': si0['mass_c_MSbar'], 'mass::Z': si0['mass_Z'],
              'QCD::alpha_s(MZ)': si0['alpha_s_MZ'], 'QED::alpha_e(m_b)': si0['alpha_em_rate']}
    baseline = eos_rate({**common, **dict(zip(KEYS, sm))})
    n = Native(); n.as0 = si0['alpha_s_mu0']; n.asb = si0['alpha_s_mu_b']
    rows = {'zero_NP': compare(ZERO, n, common, sm, baseline)}
    one = {}
    for mass in card['one_state_masses_GeV']:
        for tb in card['tanbeta']:
            raw = matching(mass, tb, si0['mt_MSbar_mu0'], card['mu0_GeV'])
            one[mass, tb] = raw
            rows[f'M{mass}_tb{tb}'] = compare(raw, n, common, sm, baseline)
    raw = matching(100000, 5.3, si0['mt_MSbar_mu0'], 160)
    rows['decoupling_100TeV'] = compare(raw, n, common, sm, baseline)
    raw = matching(550, 5.3, si0['mt_MSbar_mu0'], 160, True)
    rows['opposite_coupling_control'] = compare(raw, n, common, sm, baseline)
    a, b = one[550, 5.3], one[900, 5.3]
    for label, raw in [('gamma_zero', mix(a,b,0)), ('two_state', mix(a,b,1.09)),
                       ('gamma_half_pi', mix(a,b,math.pi/2)), ('equal_mass', mix(a,a,1.09)),
                       ('interchange', mix(b,a,math.pi/2-1.09))]:
        rows[label] = compare(raw, n, common, sm, baseline)
    signed = {}
    for i in card['signed_probe_operators']:
        key = 'C4_NLO_raw' if i == 4 else f'C{i}_LO'
        values = {}
        for sign in (-1, 1):
            raw = {**ZERO, key: sign*.01/(n.as0/(4*math.pi)) if i == 4 else sign*.01}
            label = f'C{i}_{sign:+d}'; rows[label] = compare(raw, n, common, sm, baseline)
            values[sign] = rows[label]
        signed[f'C{i}'] = {}
        for field in ('EOS_BR_shared_low_vector', 'EOS_BR_EOS_evolved_NP'):
            signed[f'C{i}'][field] = {'odd': (values[1][field]-values[-1][field])/2,
                'even': (values[1][field]+values[-1][field])/2-baseline}
        signed[f'C{i}']['SI'] = {'odd': (values[1]['SuperIso']['NP_BR_NLO']-values[-1]['SuperIso']['NP_BR_NLO'])/2,
            'even': (values[1]['SuperIso']['NP_BR_NLO']+values[-1]['SuperIso']['NP_BR_NLO'])/2-si0['SM_BR_NLO']}
    identities = {}
    for field in ('EOS_BR_shared_low_vector', 'EOS_BR_EOS_evolved_NP'):
        identities[field] = {k: rows[k][field]-rows[ref][field] for k, ref in
            [('gamma_zero','M550_tb5.3'),('gamma_half_pi','M900_tb5.3'),
             ('equal_mass','M550_tb5.3'),('interchange','two_state')]}
    identities['SI'] = {k: rows[k]['SuperIso']['NP_BR_NLO']-rows[ref]['SuperIso']['NP_BR_NLO'] for k,ref in
            [('gamma_zero','M550_tb5.3'),('gamma_half_pi','M900_tb5.3'),
             ('equal_mass','M550_tb5.3'),('interchange','two_state')]}
    # Complete only the two missing native-EOS minimal cases; reuse prior evidence.
    native = Native()
    missing = {}
    for mass,tb in [(550,50),(900,2)]:
        raw=matching(mass,tb,native.mt,160)
        br, low=native.br(raw)
        missing[f'M{mass}_tb{tb}']={'BR':br,'NP_low':low.tolist(),'raw_matching':raw}
    try:
        eos_rate(model='SM',cut=0.)
    except RuntimeError as e:
        uncut = {'status':'UNSUPPORTED','error':str(e)}
    else:
        raise AssertionError('EOS unexpectedly accepted the historical uncut prescription')
    r = {'classification':'BSG_PHYSICAL_ACCURACY_BLOCKED',
        'accuracy_domain':'ACCURACY_DOMAIN_UNKNOWN', 'status':'DIAGNOSTIC_ONLY',
        'Stage_A':{'published_reference_reproduced':False,'matched_independent_kernel_agreement':False,
                   'EOS_upstream_self_regression':'PASS in preserved prior evidence; distinct from physical validation'},
        'Stage_B':'NOT_EVALUATED: Stage A hard gate unresolved',
        'Stage_C':'NOT_EVALUATED: no calibrated uncertainty, likelihood or filter',
        'theory_sigma':None,'scan_filter_created':False,'global_zee_acceptance':None,
        'input_card_sha256':digest(HERE/'final_card.json'),
        'source_qualification_sha256':digest(HERE/'final_sources.json'),
        'source_base_commit':'3207b6db72d2f5a116b0a88afcc3fd8154722d30',
        'preserved_native_EOS_evidence_sha256':digest(HERE/'bridge_results.json'),
        'preserved_provenance_sha256':{name:digest(HERE/name) for name in
            ('bridge_sources.json','results.json','requirements.lock','input_card.json')},
        'EOS_default_parameters_sha256':digest_parameters(),
        'preserved_EOS_defaults_minimal_cases_completed':missing,
        'EOS_uncut_reference_attempt':uncut,'shared_EOS_parameter_overrides':common,
        'EOS_derived_inputs_common_parameter_card':inputs(common),
        'EOS_derived_inputs_native_defaults':inputs({}),
        'SM_ordinary_low_from_SI':sm.tolist(),'EOS_SM_BR_common_low_card':baseline,
        'upstream_original_TypeII_control':probe(ZERO,original=True),
        'comparison_card_status':'PARTIALLY_MATCHED: identical cut/scales/ordinary low vector; different rate truncation, normalization, charm/mass/QED/HQE prescriptions',
        'benchmarks':rows,'signed_high_scale_responses':signed,'identities':identities,
        'builds':build,'EOS_input_inspector_build':inspector,
        'implementation_sha256':{str(p.relative_to(ROOT)):digest(p) for p in
            [HERE/'final_validation.py',HERE/'final_eos_inputs.cc',HERE/'final_superiso_probe.c',
             HERE/'bridge.py',HERE/'eos_evolve_probe.cc',ROOT/'scripts/zee_module5_bmu_nlo.py']}}
    write_json(HERE/'final_validation.json',r)
    print(json.dumps({'classification':r['classification'],'benchmarks':len(rows),
          'SM_EOS_common_card':baseline,'SM_SI':si0['SM_BR_NLO'],
          '550_EOS':rows['M550_tb5.3']['EOS_BR_shared_low_vector'],
          '550_SI':rows['M550_tb5.3']['SuperIso']['NP_BR_NLO'],
          'identities':identities},indent=2))


if __name__ == '__main__':
    run()
