"""Offline mock-source regression tests for Gate A1J build wrapper.

These exercise error handling/provenance, NOT vendor SuperIso physics.
"""
from pathlib import Path
import json
import subprocess
import tempfile
import unittest

SHELL = Path(__file__).resolve().parents[1] / 'scripts/gateA1j_build_superiso.sh'


class TestSuperIsoBuildBootstrap(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.vendor = self.path/'superiso_v5.0'
        self.vendor.mkdir()
        (self.vendor/'src').mkdir()
        (self.vendor/'src'/'foo.c').write_text('/* test fixture, not SuperIso */\n')
        (self.vendor/'Makefile').write_text('''\
all:
\t@echo fake vendor library
sm:
\t@printf '#!/bin/sh\\n' > sm.x
\t@printf 'echo "BR(B->Xs gamma): TEST_FIXTURE_ONLY"\\n' >> sm.x
\t@chmod +x sm.x
scan_coeffs:
\t@echo fake coeff build
predict:
\t@echo fake predict build
''')
        self.output = self.path/'out'

    def run_build(self, *args):
        return subprocess.run(['bash', str(SHELL), *map(str,args)],
                              capture_output=True, text=True)

    def test_reject_missing_vendor_sources(self):
        p = self.run_build(self.path/'not_source', self.output)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Makefile and src', p.stderr)

    def test_mock_build_and_no_physical_false_positive(self):
        p = self.run_build(self.vendor, self.output, 1)
        self.assertEqual(p.returncode, 0, p.stdout+'\n'+p.stderr)
        j = json.loads((self.output/'result.json').read_text())
        self.assertEqual(j['status'],'SUPERISO_SM_BASELINE_BUILT_AND_RUN')
        self.assertEqual(j['sm_run'],'PASS')
        self.assertFalse(j['physical_BR_B_to_Xs_gamma_calculated'])
        self.assertFalse(j['confirmed_Zee_two_charged_NLO_NNLO_matching'])
        self.assertEqual(j['optional_targets']['scan_coeffs'],'PASS')
        self.assertGreater(j['source_manifest_entries'],0)
        self.assertIn('TEST_FIXTURE_ONLY', (self.output/'sm_output.log').read_text())

    def test_optional_target_failures_do_not_hide_sm_success(self):
        mk = self.vendor/'Makefile'
        mk.write_text(mk.read_text().replace('@echo fake predict build', '@false'))
        p = self.run_build(self.vendor, self.output, 1)
        self.assertEqual(p.returncode, 0, p.stderr)
        j = json.loads((self.output/'result.json').read_text())
        self.assertEqual(j['optional_targets']['predict'],'UNAVAILABLE_OR_FAILED')
        self.assertEqual(j['status'],'SUPERISO_SM_BASELINE_BUILT_AND_RUN')

    def test_unsafe_parallel_jobs_rejected(self):
        p = self.run_build(self.vendor, self.output, 12)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('JOBS must be 1', p.stderr)

    def test_core_build_failure_is_not_pass(self):
        (self.vendor/'Makefile').write_text('all:\n\t@false\nsm:\n\t@false\n')
        p = self.run_build(self.vendor, self.output, 1)
        self.assertNotEqual(p.returncode,0)
        j = json.loads((self.output/'result.json').read_text())
        self.assertEqual(j['library_build'],'FAIL')
        self.assertEqual(j['status'],'SUPERISO_INSTALL_BUILD_OR_SM_SMOKE_FAILED')

    def test_output_must_not_be_inside_vendor_source(self):
        p = self.run_build(self.vendor, self.vendor/'mylogs')
        self.assertNotEqual(p.returncode,0)
        self.assertIn('cannot be within',p.stderr)

if __name__=='__main__':
    unittest.main()
