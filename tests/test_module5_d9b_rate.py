"""Live physical falsifiers for the explicitly NLO, top-only local fork."""
import json
import math
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


def execute(command):
    r = subprocess.run(command,capture_output=True,text=True,check=True,timeout=60)
    out = dict((k,float(v)) for k,v in (line.split() for line in r.stdout.splitlines()))
    if not all(math.isfinite(v) for v in out.values()):
        raise AssertionError('Nonfinite executable result')
    return out


class MatchedRateFalsifiers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = json.loads((ROOT/'validation/module5/d9b_superiso_repair.json').read_text())
        cls.rows = [(r,execute(r['command'])) for r in cls.e['rows']]
        cls.two = {k:execute(r['command']) for k,r in cls.e['two_state'].items()}
        cls.base = execute([str(ROOT/'validation/module5/local/d9b/rate_probe')])

    def test_full_Q1_Q8_LO_NLO_against_independent_ordinary_BMU(self):
        self.assertEqual(self.base['zero_NP_BR'],self.base['SM_BR'])
        self.assertEqual(self.base['zero_NP_max_matching_residual'],0.)
        for r,o in self.rows:
            c = r['independent_BMU_ordinary']
            for order,expected in [('LO',{7:c['C7_LO'],8:c['C8_LO']}),
                                   ('NLO',{4:c['C4_NLO_raw'],7:c['C7_NLO_raw'],8:c['C8_NLO_raw']})]:
                for i in range(1,9):
                    self.assertAlmostEqual(o[f'native_{order}_C{i}']-o[f'SM_{order}_C{i}'],
                                           expected.get(i,0.),delta=5e-11)
            # Original convergence caps are retained and inactive in this domain.
            a = o['alpha_s_match']/(4*math.pi)
            for i in (7,8):
                self.assertLess(abs(a*c[f'C{i}_NLO_raw']),abs(o[f'native_LO_C{i}']))

    def test_same_order_one_state_rates_and_exact_alpha_s_factor(self):
        for r,o in self.rows:
            self.assertAlmostEqual(o['native_BR'],o['injected_BR'],delta=5e-13)
            self.assertEqual(o['native_P2'],0.)
            self.assertEqual(o['injected_P2'],0.)
        o = self.rows[0][1]
        self.assertGreater(abs(o['double_effective_map_BR']-o['injected_BR']),1e-9)
        self.assertGreater(abs(o['extra_alpha_s_BR']-o['injected_BR']),1e-6)

    def test_no_hidden_model_metadata_and_high_matching_reaches_all_terms(self):
        for _,o in self.rows:
            for term in ('BR','P0','P1','P2','P_em','N_E0'):
                self.assertEqual(o['injected_'+term],o['metadata_'+term])
            for term in ('BR','P0','P_em','N_E0'):
                self.assertNotEqual(o['injected_'+term],o['high_C7_'+term])
            self.assertEqual(o['reject_scheme'],1.)
            self.assertEqual(o['reject_unsupported_LO'],1.)

    def test_C4_cannot_be_dropped(self):
        o = self.rows[0][1]
        self.assertGreater(abs(o['injected_BR']-o['omit_C4_BR']),1e-9)

    def test_legacy_rate_and_dynamic_NNLO_branch_remain_explicit(self):
        for _,o in self.rows:
            self.assertEqual(o['legacy_full_BR'],o['legacy_original_entry_BR'])
            self.assertEqual(bool(o['legacy_full_nnlo_dropped']),abs(o['legacy_full_nnlo_relative'])>0.4)
            self.assertNotEqual(o['legacy_full_P2'],0.)
            self.assertEqual(o['forced_fallback_nnlo_dropped'],1.)
            self.assertEqual(o['forced_fallback_P2'],0.)
            self.assertEqual(o['forced_fallback_BR'],o['forced_NLO_BR'])
        self.assertFalse(self.e['C2_matching_used_in_accepted_rate'])
        self.assertFalse(self.e['2026_GLOBAL_FLAVOR_FILTER_READY'])
        self.assertIsNone(self.e['global_zee_acceptance'])

    def test_one_state_decoupling_second_tanbeta_and_signed_Yukawa(self):
        for tb in (5.3,2.):
            selected = [o['injected_BR'] for r,o in self.rows if r['tanbeta']==tb and not r['opposite_ld']]
            self.assertTrue(all(x>y for x,y in zip(selected,selected[1:])))
            self.assertLess(abs(selected[-1]-self.base['SM_BR']),3e-9)
        self.assertLess(self.rows[-1][1]['injected_BR'],self.base['SM_BR'])
        self.assertNotEqual(self.rows[0][1]['injected_BR'],self.rows[5][1]['injected_BR'])

    def test_two_state_endpoints_equal_masses_interchange_and_coherence(self):
        t = self.two
        for k,expected in [('gamma_zero',self.rows[0][1]['injected_BR']),
                           ('gamma_half_pi',self.rows[1][1]['injected_BR']),
                           ('equal_masses',self.rows[0][1]['injected_BR']),
                           ('interchanged',t['example']['injected_BR'])]:
            self.assertAlmostEqual(t[k]['injected_BR'],expected,delta=5e-13)
        w = self.e['two_state']['example']['weights']
        weighted_rates = sum(a*o['injected_BR'] for a,(_,o) in zip(w,self.rows[:2]))
        self.assertGreater(abs(t['example']['injected_BR']-weighted_rates),1e-8)

    def test_two_state_decoupling_sign_and_matching_scale_response(self):
        t = self.two
        self.assertLess(abs(t['decoupled']['injected_BR']-self.base['SM_BR']),3e-9)
        self.assertLess(t['opposite_ld']['injected_BR'],self.base['SM_BR'])
        for k in ('mu0_120','mu0_200'):
            self.assertGreater(abs(t[k]['injected_BR']-t['example']['injected_BR']),1e-8)

    def test_repeated_live_outputs_reproduce_archived_evidence(self):
        for r,o in self.rows:
            self.assertEqual(o,r['output'])
        for name,o in self.two.items():
            self.assertEqual(o,self.e['two_state'][name]['output'])
        self.assertEqual(self.base,self.e['baseline'])


if __name__=='__main__':
    unittest.main()
