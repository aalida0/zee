"""Run focused Module 2 regressions and write reproducible concise evidence."""
import hashlib
import importlib
import argparse
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--all-tests', action='store_true', help='Include all repository regression tests')
    args = parser.parse_args()
    test_dir = ROOT / 'tests'
    sys.path.insert(0, str(test_dir))
    physics = importlib.import_module('test_module2_physics')
    interface = importlib.import_module('test_module2_interface')
    audit = importlib.import_module('test_module2_audit')
    profiles = importlib.import_module('test_module2_profiles')
    suite = unittest.defaultTestLoader.discover(str(test_dir), pattern='test_*.py' if args.all_tests else 'test_module2_*.py')
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
        'test_count': result.testsRun, 'failures': 0, 'errors': 0, 'skipped': len(result.skipped),
        'complete_repository_regressions': args.all_tests,
        'independent_audit': audit.EVIDENCE,
        'audit_findings': {
            'audited_implementation_commit': 'b88b13c792f10d0b3a713a43d1362e66bc586a67',
            'CONFIRMED': ['SARAH sign, chirality conjugations, normalization, finite charged-lepton kernel and archived complex E3 matrices.',
                          'Rank five, n.T M n=0 and complete D=W^-1(cI+n r.T) homogeneous family, including isotropic n.',
                          'PDG phases, IO dm32 sign, massless-phase exclusions, and independent mass-matrix CP invariant.'],
            'CORRECTED': ['Takagi norm underflow/overflow and finite-diagnostic rejection.',
                          'Majorana phases with theta13=0 use mu/tau row invariants when physically defined.',
                          'Free coordinate in identically zero null-cone chart; scale-invariant cone checks.',
                          'Correlated Gaussian phase lifts and rejection of nonfinite observable values.',
                          'Runner now discovers new Module 2 tests; --all-tests runs the complete repository suite.'],
            'UNRESOLVED': ['Authentic NuFIT 6.1 archive retrieval/validation blocked by official-host timeout/DNS; reader tested on synthetic grids only.',
                           'No new native SARAH/Mathematica execution; archived native closure remains the convention reference.']},
        'gates': {
            'forward': {'status': 'PASS', 'archived_native_E3': physics.EVIDENCE.get('archived_native_E3', [])},
            'inverse_families': {'status': 'PASS', 'max_random_family_closure_eV': physics.EVIDENCE.get('family_max_closure_eV'),
                                 'complex_nullity': 4, 'witnesses': len(physics.EVIDENCE.get('physical_witnesses', []))},
            'observables': {'status': 'PASS', 'max_signed_delta_error_rad': physics.EVIDENCE.get('max_signed_Dirac_phase_error_rad'),
                            'max_takagi_relative_reconstruction': physics.EVIDENCE.get('takagi_max_relative_reconstruction')},
            'data_comparison': {'status': 'PARTIAL_AUTHENTIC_NUFIT61_ARCHIVE_UNAVAILABLE', 'dataset_ids': [json.loads(p.read_text())['dataset_id'] for p in datafiles],
                                'official_joint_likelihood': False, 'official_profiled_projections_ingested': False,
                                'projection_reader': profiles.EVIDENCE,
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
        'limitations': ['NuFIT 6.1 native-format reader passes synthetic tests; real official archives could not be retrieved (host timeout).',
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
        'contracts_tests_and_runner_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted([
            *(ROOT/'module2').glob('*.schema.json'), *(ROOT/'tests').glob('test_module2_*.py'),
            ROOT/'scripts/run_module2_validation.sh'])},
        'nufit61_investigation': {
            'release_url': 'https://www.nu-fit.org/?q=node%2F309',
            'format_source': 'https://www.nu-fit.org/sites/default/files/v61.release-notes.pdf',
            'verified_from_official_indexed_release_notes': '22 one-, two-, and three-dimensional profiled sections; IC23 without SK and IC24 with SK',
            'archive_retrieval': 'UNRESOLVED: www host curl exit 28 after 30 seconds/zero bytes; hostname without www exit 6 DNS failure. Direct web fetches also timed out.',
            'authentic_archive_numeric_validation': 'NOT_EVALUATED',
            'synthetic_native_format_regressions': 'PASS'},
        'validation_log': 'validation/module2/local/validation.log (ignored locally)'
    }
    (OUT / 'source_manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
