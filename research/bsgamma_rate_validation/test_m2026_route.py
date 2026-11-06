"""Focused equation, matching reuse, provenance and closed-validity-gate tests."""
import json
import math
import unittest
from m2026_route import HERE, ROOT, RESULT, audit_point, digest, linear_audit
from m2026_legacy import response


class M2026RouteTests(unittest.TestCase):
    def test_zero_np_units_and_signed_separate_terms(self):
        self.assertAlmostEqual(linear_audit(0., 0.)['BR_linear_2026'], 3.54e-4, places=18)
        for c7, c8 in [(.01, 0.), (-.01, 0.), (0., .01), (0., -.01), (.03, -.02)]:
            r = linear_audit(c7, c8)
            self.assertEqual(r['signed_C7_BR_contribution'], -8.51*c7*1e-4)
            self.assertEqual(r['signed_C8_BR_contribution'], -2.16*c8*1e-4)
            self.assertAlmostEqual(r['BR_linear_2026'], (3.54-8.51*c7-2.16*c8)*1e-4, places=18)

    def test_c1_reference_reused_without_nlo_or_alpha_s_factor(self):
        r = audit_point(550., 900., 5.3, 1.09)
        old = json.loads((ROOT/'validation/module5/linear_2026.json').read_text())['reference_run']
        for key in ('C7','C8'):
            self.assertAlmostEqual(r['Delta'+key], old['coefficient_components'][key]['real'], places=15)
        self.assertAlmostEqual(r['BR_linear_2026'], 3.9494799731787267e-4, places=18)
        # There is no keyword for silently inserting full or NLO matching.
        for key in ('C4_NLO_raw', 'C7_NLO_raw', 'C8_NLO_raw', 'alpha_s'):
            with self.assertRaises(TypeError):
                audit_point(550., 900., 5.3, 1.09, **{key: 1.})
        with self.assertRaises(ValueError):
            audit_point(550., 900., 5.3, 1.09, matching_scale_GeV=81.)

    def test_gamma_identities_and_coherent_vectors(self):
        a = audit_point(550.,900.,5.3,0.)
        b = audit_point(550.,900.,5.3,math.pi/2)
        mixed = audit_point(550.,900.,5.3,1.09)
        exchange = audit_point(900.,550.,5.3,math.pi/2-1.09)
        equal = audit_point(550.,550.,5.3,1.09)
        for key in ('DeltaC7','DeltaC8','BR_linear_2026'):
            self.assertAlmostEqual(mixed[key], exchange[key], places=15)
            self.assertAlmostEqual(a[key], equal[key], places=15)
        for key in ('DeltaC7','DeltaC8'):
            self.assertAlmostEqual(mixed[key], math.cos(1.09)**2*a[key]+math.sin(1.09)**2*b[key], places=15)

    def test_decoupling_and_unknown_even_at_zero_np(self):
        heavy = audit_point(1e5,1e5,5.3,1.09)
        self.assertLess(abs(heavy['BR_linear_2026']-3.54e-4), 2e-8)
        for r in (heavy, linear_audit(0.,0.), linear_audit(-1.,-1.)):
            self.assertEqual(r['status'], 'DIAGNOSTIC_ONLY')
            self.assertEqual(r['classification'], 'UNKNOWN')
            self.assertEqual(r['validity_domain'], 'VALIDITY_DOMAIN_UNKNOWN')
            self.assertIsNone(r['exclusion'])
            self.assertIsNone(r['NP_theory_sigma'])
            self.assertIsNone(r['complete_remainder_bound'])

    def test_invalid_inputs_are_rejected(self):
        for tb in (0., -1., True, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                audit_point(550.,900.,tb,1.09)
        for v in (True, float('nan'), float('inf'), 1j):
            with self.assertRaises(ValueError):
                linear_audit(v,0.)

    def test_recorded_grid_coverage_and_closed_gate(self):
        d = json.loads((HERE/'m2026_route_results.json').read_text())
        self.assertEqual(d['classification'], RESULT)
        self.assertFalse(d['scan_filter_created'])
        self.assertEqual(len(d['grid']), 72)
        expected = {(a,b,t,g) for a in (300.,550.,900.) for b in (700.,900.,1400.) if a<=b
                    for t in (2.,5.3,50.) for g in (0.,1.09,math.pi/2)}
        self.assertEqual({tuple(r['input'][k] for k in ('mH1_GeV','mH2_GeV','tanbeta','gamma_rad'))
                          for r in d['grid']}, expected)
        for r in d['grid']:
            self.assertEqual(r['classification'], 'UNKNOWN')
            self.assertIsNone(r['exclusion'])
            self.assertIsNone(r['complete_remainder_bound'])
        self.assertEqual(d['legacy_response_sha256'], digest(HERE/'m2026_legacy_results.json'))
        self.assertTrue((HERE/'AUTHOR_QUESTION_DRAFT.md').is_file())

    def test_recorded_inputs_sources_and_results_reproduce(self):
        d = json.loads((HERE/'m2026_route_results.json').read_text())
        for f,h in d['source_hashes'].items():
            self.assertEqual(digest(ROOT/f), h)
        for row in d['grid']:
            v = row['input']
            r = audit_point(v['mH1_GeV'], v['mH2_GeV'], v['tanbeta'], v['gamma_rad'])
            self.assertEqual(r, row)

    def test_legacy_joint_response_and_holdouts(self):
        d = json.loads((HERE/'m2026_legacy_results.json').read_text())
        self.assertFalse(d['remainder_certified'])
        self.assertEqual(d['new_joint_or_holdout_points'], 6)
        rows = {(r['DeltaC7'],r['DeltaC8']):r for r in d['points']}
        for field in ('EOS','SuperIso_D9B'):
            self.assertEqual(response(rows,field), d['responses'][field])
            q = d['responses'][field]
            self.assertLess(q['slope_C7'],0.)
            self.assertLess(q['slope_C8'],0.)
            self.assertGreater(q['quadratic_C7_C8'],0.)
            self.assertEqual(len(q['held_out_residuals']),2)
            self.assertLess(max(abs(p['BR_residual']) for p in q['held_out_residuals']),2e-18)
        old = json.loads((HERE/'final_validation.json').read_text())['benchmarks']
        for xy,label in [((0.,0.),'zero_NP'),((.01,0.),'C7_+1'),((-.01,0.),'C7_-1'),
                         ((0.,.01),'C8_+1'),((0.,-.01),'C8_-1')]:
            self.assertEqual(rows[xy]['EOS'],old[label]['EOS_BR_EOS_evolved_NP'])
            self.assertEqual(rows[xy]['SuperIso_D9B'],old[label]['SuperIso']['NP_BR_NLO'])


if __name__ == '__main__':
    unittest.main()
