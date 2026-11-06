"""Read-only C1 adapter and predeclared reference sensitivity comparison."""
import math
from pathlib import Path

from module5.bsgamma_2026_linear_diagnostic import finite_real, run_contract
from module5.hyperiso_patch_contract import make_contract
from module14.scan import digest, file_sha

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = {
    'absolute_pull_threshold': 1.959963984540054,
    'boundary_half_width_in_pull': 0.01,
    'sigma_SM_times_1e4': 0.14, 'sigma_experiment_times_1e4': 0.19,
    'assumptions': 'Symmetric Gaussian quoted SM and experimental errors; rho=0; no NP error. Reference sensitivity only, not a Zee likelihood or validated 95% CL test.',
}


def classification(pull):
    pull = finite_real(pull, 'conditional pull')
    distance = abs(pull) - REFERENCE['absolute_pull_threshold']
    if abs(distance) <= REFERENCE['boundary_half_width_in_pull']:
        return 'APPROX_BOUNDARY'
    return 'APPROX_COMPATIBLE' if distance < 0 else 'APPROX_DISFAVORED'


def evaluate(scalar, card):
    """Require complete validated scalar input and an explicit matching card."""
    from module1.scalar_constraints import validate_input
    validate_input(scalar)
    if set(card) != {'mt_MSbar_GeV', 'matching_scale_GeV', 'quark_scheme', 'provenance'}:
        raise ValueError('Explicit matching card required')
    if card['quark_scheme'] != 'MSbar_top_at_matching_scale_real_top_only_ms0':
        raise ValueError('Unsupported quark scheme')
    if not isinstance(card['provenance'], str) or not card['provenance'].strip():
        raise ValueError('Top input provenance required')
    p = scalar['physical']
    inputs = {'mH1_GeV': p['mH1'], 'mH2_GeV': p['mH2'],
              'beta_rad': p['beta'], 'gamma_rad': p['gamma'],
              'mt_MSbar_GeV': card['mt_MSbar_GeV'], 'matching_scale_GeV': card['matching_scale_GeV']}
    contract = make_contract(inputs)
    diagnostic = run_contract(contract)
    central = diagnostic['linearized']['conditional_B_times_1e4']
    pull = finite_real((central - 3.49) / math.hypot(0.14, 0.19), 'conditional pull')
    return {
        'status': 'DIAGNOSTIC_ONLY', 'BR_linear_2026': central * 1e-4,
        'DeltaC7_LO': diagnostic['shift_input']['DeltaC7'],
        'DeltaC8_LO': diagnostic['shift_input']['DeltaC8'],
        'contribution_splits': contract['scalar_rows'],
        'linear_terms_times_1e4': diagnostic['linearized'],
        'matching_input': inputs, 'matching_card': card,
        'matching_input_sha256': digest(inputs), 'scalar_sha256': digest(scalar),
        'conditional_pull': pull, 'reference_comparison': REFERENCE,
        'bsg_nominal_classification': classification(pull),
        'bsg_physical_classification': 'UNKNOWN', 'np_theory_sigma': None,
        'bsg_exclusion': None, 'globally_allowed': None,
        'method_robustness': 'NOT_EVALUATED',
        'method_robustness_reason': 'No new EOS/SuperIso/NLO variants executed; legacy method spread is not an NP sigma.',
        'C1_scope': diagnostic['convention_scope'],
        'limitations': diagnostic['limitations'],
    }


def source_hashes():
    files = [*ROOT.glob('module14/conditional_scan/*.py'),
             *ROOT.glob('module14/conditional_scan/*config.json'),
             ROOT/'module14/conditional_scan/matching_card.json',
             ROOT/'module14/scan.py', ROOT/'module14/collect.py', ROOT/'module14/decays.py',
             ROOT/'module14/disk_rows.py',
             ROOT/'module1/scalar_constraints.py', ROOT/'module1/d10_certificate.py',
             *ROOT.glob('module7/*.py'), ROOT/'module5/bsgamma_lo.py',
             ROOT/'module5/hyperiso_patch_contract.py', ROOT/'module5/bsgamma_2026_linear_diagnostic.py',
             ROOT/'module5/BSGAMMA_2026_CONVENTION.md', ROOT/'validation/module5/linear_2026.json']
    return {str(p.relative_to(ROOT)): file_sha(p) for p in sorted(set(files))}
