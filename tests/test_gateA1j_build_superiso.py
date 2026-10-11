"""Offline mock-source tests for Gate A1J build wrapper / SM exit audit.

Fixtures emulate SuperIso stdout but are NOT vendor SuperIso physics.
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
        self.vendor = self.path / 'SuperIso_v5.0'
        self.vendor.mkdir()
        (self.vendor / 'src').mkdir()
        (self.vendor / 'src' / 'fixture.c').write_text('/* not vendor source */\n')
        (self.vendor / 'sm.c').write_text('int main(void) {\nreturn 0;\n}\n')
        (self.vendor / 'Makefile').write_text('''\
all:
\t@echo fake library
sm:
\t@printf '#!/bin/sh\\n' > sm.x
\t@printf 'echo "SuperIso v5.0 - 2025"\\n' >> sm.x
\t@printf 'echo "Standard Model predictions"\\n' >> sm.x
\t@printf 'echo "BR(b->s gamma) 3.382e-04"\\n' >> sm.x
\t@printf 'echo "Br(KL->pi0mumu)_dest-interf.: 9.43e-12"\\n' >> sm.x
\t@chmod +x sm.x
scan_coeffs:
\t@echo fake coefficient tools
predict:
\t@echo fake prediction tools
''')
        self.out = self.path / 'output'

    def run_build(self, *, jobs=1):
        return subprocess.run(
            ['bash', str(SHELL), str(self.vendor), str(self.out), str(jobs)],
            capture_output=True, text=True,
        )

    def result(self):
        return json.loads((self.out / 'result.json').read_text())

    def add_return_code(self, code):
        mk = self.vendor / 'Makefile'
        contents = mk.read_text()
        needle = 'scan_coeffs:\n'
        self.assertIn(needle, contents)
        mk.write_text(contents.replace(
            needle, f"\t@echo 'exit {code}' >> sm.x\n" + needle))

    def test_missing_source_rejected(self):
        (self.vendor / 'Makefile').unlink()
        p = self.run_build()
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Makefile and src', p.stderr)

    def test_exit_zero_complete_sm_accepted(self):
        p = self.run_build()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        r = self.result()
        self.assertEqual(r['sm_run'], 'PASS')
        self.assertEqual(r['sm_exit_code'], 0)
        self.assertEqual(r['sm_exit_audit']['status'], 'PASS_EXIT0')
        self.assertAlmostEqual(
            r['sm_exit_audit']['br_b_to_s_gamma_sm'], 3.382e-4)
        self.assertFalse(r['physical_BR_B_to_Xs_gamma_calculated'])
        self.assertFalse(r['confirmed_Zee_two_charged_NLO_NNLO_matching'])

    def test_verified_upstream_exit_one_accepted(self):
        (self.vendor / 'sm.c').write_text('int main(void) {\nreturn 1;\n}\n')
        self.add_return_code(1)
        p = self.run_build()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        r = self.result()
        self.assertEqual(r['sm_exit_code'], 1)
        self.assertEqual(r['sm_run'], 'PASS')
        self.assertEqual(r['sm_exit_audit']['status'],
                         'PASS_SOURCE_VERIFIED_EXIT1')
        self.assertTrue(r['sm_exit_audit']['sm_c_ends_in_return_1'])
        self.assertTrue(r['sm_exit_audit']['output_complete'])

    def test_unverified_exit_one_rejected(self):
        self.add_return_code(1)
        p = self.run_build()
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.result()['sm_exit_audit']['status'],
                         'FAIL_INCOMPLETE_OR_UNKNOWN_EXIT')

    def test_truncated_exit_one_rejected(self):
        (self.vendor / 'sm.c').write_text('int main(void) {\nreturn 1;\n}\n')
        self.add_return_code(1)
        mk = self.vendor / 'Makefile'
        mk.write_text(mk.read_text().replace(
            'Br(KL->pi0mumu)_dest-interf.: 9.43e-12', 'INCOMPLETE_OUTPUT'))
        p = self.run_build()
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse(self.result()['sm_exit_audit']['output_complete'])

    def test_exit_two_rejected_even_with_complete_output(self):
        (self.vendor / 'sm.c').write_text('int main(void) {\nreturn 1;\n}\n')
        self.add_return_code(2)
        p = self.run_build()
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.result()['sm_exit_code'], 2)

    def test_optional_target_failure_does_not_mask_success(self):
        mk = self.vendor / 'Makefile'
        mk.write_text(mk.read_text().replace(
            '@echo fake prediction tools', '@false'))
        p = self.run_build()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertEqual(self.result()['optional_targets']['predict'],
                         'UNAVAILABLE_OR_FAILED')

    def test_library_build_failure_rejected(self):
        (self.vendor / 'Makefile').write_text('all:\n\t@false\nsm:\n\t@false\n')
        p = self.run_build()
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.result()['library_build'], 'FAIL')

    def test_parallel_jobs_rejected(self):
        p = self.run_build(jobs=12)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('JOBS must be 1', p.stderr)

    def test_output_inside_vendor_tree_rejected(self):
        self.out = self.vendor / 'logs'
        p = self.run_build()
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('cannot be within', p.stderr)


if __name__ == '__main__':
    unittest.main()
