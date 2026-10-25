"""Run focused Module 2 regressions and write reproducible concise evidence."""
import hashlib
import importlib
import json
import platform
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validation/module2'
LOG = OUT / 'local/validation.log'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    test_dir = ROOT / 'tests'
    sys.path.insert(0, str(test_dir))
    physics = importlib.import_module('test_module2_physics')
    interface = importlib.import_module('test_module2_interface')
    suite = unittest.TestSuite()
    for module in (interface, physics):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
    OUT.joinpath('local').mkdir(parents=True, exist_ok=True)
    with LOG.open('w') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    if not result.wasSuccessful():
        sys.stderr.write(LOG.read_text())
        return 1
    pyfiles = sorted((ROOT / 'module2').glob('*.py'))
    code = {str(p.relative_to(ROOT)): sha(p) for p in pyfiles}
    aggregate = hashlib.sha256(''.join(k + ':' + v + '\n' for k, v in code.items()).encode()).hexdigest()
    foundation = json.loads((ROOT / 'module1/foundation.json').read_text())
    ancestry = subprocess.run(['git', 'merge-base', '--is-ancestor', 'zee-sarah-module0-v1', 'HEAD'], cwd=ROOT).returncode
    module1_base = subprocess.run(['git', 'merge-base', '--is-ancestor', '687fba61640424406661601e92312b8481673b83', 'HEAD'], cwd=ROOT).returncode
    branch = subprocess.run(['git', 'branch', '--show-current'], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    if branch != 'feature/zee-neutrino-module2' or ancestry != 0 or module1_base != 0:
        raise RuntimeError('Validation requires the pinned Module 2 branch and verified Module 0/1 ancestry')
    datafiles = sorted((ROOT / 'module2/data').glob('*.json'))
    evidence = {
        'schema_version': '1.0.0', 'overall': 'PARTIAL',
        'test_count': result.testsRun, 'failures': 0, 'errors': 0,
        'gates': {
            'forward': {'status': 'PASS', 'archived_native_E3': physics.EVIDENCE.get('archived_native_E3', [])},
            'inverse_families': {'status': 'PASS', 'max_random_family_closure_eV': physics.EVIDENCE.get('family_max_closure_eV'),
                                 'complex_nullity': 4, 'witnesses': len(physics.EVIDENCE.get('physical_witnesses', []))},
            'observables': {'status': 'PASS', 'max_signed_delta_error_rad': physics.EVIDENCE.get('max_signed_Dirac_phase_error_rad'),
                            'max_takagi_relative_reconstruction': physics.EVIDENCE.get('takagi_max_relative_reconstruction')},
            'data_comparison': {'status': 'PARTIAL_GAUSSIAN_APPROXIMATION', 'dataset_ids': [json.loads(p.read_text())['dataset_id'] for p in datafiles],
                                'official_joint_likelihood': False, 'official_profiled_projections_ingested': False,
                                'experimental_acceptance': None},
            'interface': {'status': 'PASS', **interface.EVIDENCE},
            'regression_and_evidence': {'status': 'PASS', 'test_count': result.testsRun},
        },
        'physical_witnesses': physics.EVIDENCE.get('physical_witnesses', []),
        'numerics': {'max_kernel_relative_error_vs_80_digit_quadrature': physics.EVIDENCE.get('kernel_max_relative_error_vs_80_digit_quadrature'),
                     'max_signed_Dirac_phase_error_rad': physics.EVIDENCE.get('max_signed_Dirac_phase_error_rad'),
                     'max_Takagi_relative_reconstruction': physics.EVIDENCE.get('takagi_max_relative_reconstruction')},
        'provenance': {'validated_code_sha256': aggregate, 'module2_python_sha256': code,
                       'module1_snapshot_commit': foundation['snapshot_commit'],
                       'module1_source_commit_ancestry_verified': module1_base == 0,
                       'branch': branch,
                       'module0_tag_ancestry_verified_locally': ancestry == 0,
                       'native_sarah_rerun': False},
        'limitations': ['Official NuFIT profiled projections are not ingested; only explicit pinned Gaussian approximations are evaluated.',
                        'LFV/Barr-Zee, SPheno, RG closure, collider/flavor, and global vacuum proof are not evaluated.',
                        'Archived Module 0 SARAH self-energy report is used; no native Mathematica/SARAH rerun was performed.'],
        'environment': {'python': platform.python_version()}
    }
    (OUT / 'results.json').write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
    manifest = {
        'schema_version': '1.0.0', 'branch': branch,
        'validated_code_sha256': aggregate, 'module2_python_sha256': code,
        'module1_foundation': foundation,
        'experimental_datasets': [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p),
                                   'dataset_id': json.loads(p.read_text())['dataset_id']} for p in datafiles],
        'e3_reference': {'path': 'validation/module0/fixtures/e3_charged_loop_fixture.m',
                         'sha256': sha(ROOT / 'validation/module0/fixtures/e3_charged_loop_fixture.m'),
                         'physical_closure_report': 'validation/module0/report/majorana_physical.json',
                         'physical_closure_sha256': sha(ROOT / 'validation/module0/report/majorana_physical.json'),
                         'native_rerun': False},
        'module1_source_commit_ancestry_verified': module1_base == 0,
        'module0_tag_ancestry_verified_locally': ancestry == 0,
        'validation_log': 'validation/module2/local/validation.log (ignored locally)'
    }
    (OUT / 'source_manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
