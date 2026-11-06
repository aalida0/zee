"""Fail-closed evidence and source-lock checks; no new parameter proposals."""
from pathlib import Path
import tempfile
import unittest

from module14.conditional_scan.workflow import load
from module14.physics_adapters.lfv_reference import load_reference
from module14.scan import file_sha

ROOT=Path(__file__).resolve().parents[1]


class AdapterTests(unittest.TestCase):
    def test_lfv_reference_scope_and_original_bindings(self):
        e=load(ROOT/'module14/physics_adapters/lfv_reference_evidence.json')
        self.assertEqual(e['status'],'REFERENCE_ONLY');self.assertEqual(e['two_loop_full_Zee'],'UNKNOWN')
        self.assertEqual(e['input_file_sha256'],file_sha(ROOT/'validation/module12/d12_benchmarks.json'))
        self.assertEqual(len(e['comparisons']),12)
        self.assertLess(max(r['max_relative_residual'] for r in e['comparisons']),1e-9)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises((ValueError,FileNotFoundError)):load_reference(tmp)

    def test_vacuum_scope_and_saved_cards(self):
        e=load(ROOT/'module14/physics_adapters/vacuum_contract_evidence.json')
        self.assertFalse(e['solver_executed']);self.assertIsNone(e['global_minimum_claim'])
        self.assertEqual(e['full_real_fields'],10)
        self.assertEqual([r['certificate'] for r in e['comparisons']],['PASS','UNKNOWN'])
        for name,sha in e['source_sha256'].items():self.assertEqual(file_sha(ROOT/name),sha)
        for r in e['comparisons']:
            self.assertLess(max(r['max_scaled_value_gradient_hessian_residual']),1e-12)
            self.assertLess(r['EW_stationarity']['gradient_over_v3'],1e-12)

    def test_optional_pinned_lfv_nonzero_replay(self):
        candidates=list(Path('/tmp/zee-public-source').glob('general*/thdm.py'))
        if not candidates:self.skipTest('Pinned optional third-party source absent')
        from scripts.zee_d14_lfv_reference import compare
        r=compare(candidates[0].parent)
        self.assertEqual(r,load(ROOT/'module14/physics_adapters/lfv_reference_evidence.json'))

    def test_spheno_build_is_separate_from_observable_validation(self):
        e=load(ROOT/'module14/physics_adapters/spheno_build_evidence.json')
        self.assertEqual(e['build_status'],'SPHENO_FULL_BUILD_VALIDATED')
        self.assertEqual(e['physics_adapter_status'],'UNVALIDATED');self.assertEqual(e['operative_observables'],[])
        self.assertEqual(e['input_reference_sha256'],file_sha(ROOT/'validation/module12/d12_benchmarks.json'))
        self.assertEqual(e['spheno_archive_sha256'],load(ROOT/'module14/public_spheno_evidence.json')['spheno_archive_sha256'])
        self.assertEqual(len(e['comparisons']),4)
        for r in e['runtime_summary']+e['tree_runtime_summary']:
            self.assertEqual(r['returncode'],0);self.assertTrue(r['spectrum_exists'])
        for c in e['comparisons']:
            self.assertLess(c['tree_scalar_mass_max_relative_difference'],2e-8)
            self.assertLess(c['charged_mixing_absolute_magnitude_max_difference'],2e-8)
            self.assertLess(c['neutrino_UV_unitarity_max_residual'],2e-8)
            self.assertLess(c['matched_native_gauge_D4_relative_difference'],2e-8)
            self.assertGreater(c['h_light_full_mass_GeV'],200)

    def test_optional_isolated_model_patch_reproduction(self):
        source=Path('/home/amine/.Mathematica/Applications/SARAH-4.15.4')
        if not source.exists():self.skipTest('Optional pinned SARAH source absent')
        from scripts.zee_d14_prepare_sarah import prepare
        with tempfile.TemporaryDirectory() as tmp:
            r=prepare(source,Path(tmp)/'isolated')
            e=load(ROOT/'module14/physics_adapters/spheno_build_evidence.json')
            self.assertEqual(r['corrected_model_sha256'],e['corrected_model_sha256'])
            self.assertEqual(r['original_model_sha256'],e['original_model_sha256'])
            self.assertFalse(r['operative_constraint'])
