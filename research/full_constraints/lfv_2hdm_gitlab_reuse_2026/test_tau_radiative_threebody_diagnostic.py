import json
import math
import tempfile
import unittest
from pathlib import Path

from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_radiative_threebody_diagnostic import (
    GATE, EXPECTED_IDS, M_E_GEV, M_MU_GEV, M_TAU_GEV,
    dipole_threebody_ratio, evaluate,
)


class TauRadiativeThreeBodyTests(unittest.TestCase):
    def test_ratios_independent_leading_log(self):
        result = evaluate()
        re = (1 / 137.035999084) / (3 * math.pi) * (math.log(M_TAU_GEV**2 / M_E_GEV**2) - 2.75)
        rm = (1 / 137.035999084) / (3 * math.pi) * (math.log(M_TAU_GEV**2 / M_MU_GEV**2) - 2.75)
        self.assertAlmostEqual(result['ratios']['tau3e_over_tauegamma_dipole'], re, places=14)
        self.assertAlmostEqual(result['ratios']['tau3mu_over_taumugamma_dipole'], rm, places=14)
        self.assertAlmostEqual(re, 0.0104975811678193, places=14)
        self.assertAlmostEqual(rm, 0.002241353578249, places=14)

    def test_four_cards_and_numerical_rates(self):
        x = evaluate()
        self.assertEqual(tuple(x['cards']), EXPECTED_IDS)
        self.assertAlmostEqual(x['cards']['D7_NO']['taumugamma']['partial_coherent_neutral_BZ_dipole_only_threebody_BR']/4.101677048195734e-14, 1, places=10)
        self.assertAlmostEqual(x['cards']['D7_IO']['tauegamma']['partial_coherent_neutral_BZ_dipole_only_threebody_BR']/2.8471539643359505e-15, 1, places=10)
        self.assertAlmostEqual(x['cards']['F13_IO']['taumugamma']['partial_coherent_neutral_BZ_dipole_only_threebody_BR']/6.271083176582974e-18, 1, places=10)

    def test_missing_amplitude_not_assumed_small(self):
        x=evaluate(40)
        self.assertTrue(x['all_conditional_radiative_sufficient_pass'])
        self.assertAlmostEqual(x['cards']['D7_IO']['taumugamma']['max_assumed_missing_amplitude_norm_over_partial_norm'], 43.72348929067133)
        y=evaluate(50)
        self.assertFalse(y['cards']['D7_IO']['taumugamma']['conditional_radiative_sufficient_pass'])
        self.assertFalse(y['cards']['D7_NO']['taumugamma']['conditional_radiative_sufficient_pass'])
        self.assertFalse(y['all_conditional_radiative_sufficient_pass'])

    def test_all_physical_rates_and_gate_fail_closed(self):
        x=evaluate()
        self.assertEqual(x['physical_lfv'], 'UNKNOWN')
        self.assertIsNone(x['global_acceptance'])
        for channels in x['cards'].values():
            for value in channels.values():
                self.assertIsNone(value['physical_threebody_BR'])
                self.assertIsNone(value['physical_radiative_BR'])

    def test_invalid_approximation_domain(self):
        for triple in [(1,0.2,0.007), (0,0.1,0.007), (1,-1,0.007), (1,0.01,float('nan'))]:
            with self.assertRaises(ValueError):
                dipole_threebody_ratio(*triple)

    def test_invalid_kappa(self):
        for k in (-1, float('nan'), float('inf'), float('-inf')):
            with self.assertRaises(ValueError):evaluate(k)

    def test_reject_false_completeness_or_provenance(self):
        raw=json.loads(GATE.read_text())
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'gate.json'
            for mutate in ('gate', 'card', 'sha', 'empty'):
                x=json.loads(json.dumps(raw))
                if mutate=='gate': x['physical_lfv']='PASS'
                if mutate=='card': x['cards'][0]['full_Zee_two_loop_qualified']=True
                if mutate=='sha': x['authors_uploaded_thdm_sha256']='unverified'
                if mutate=='empty': x['cards']=[]
                path.write_text(json.dumps(x))
                with self.assertRaises(ValueError):evaluate(input_gate=path)

    def test_ratio_times_radiative_and_monotonic(self):
        a,b=evaluate(0),evaluate(2)
        for card in EXPECTED_IDS:
            for ch in ('tauegamma','taumugamma'):
                aa,bb=a['cards'][card][ch],b['cards'][card][ch]
                self.assertAlmostEqual(aa['native_one_loop_dipole_only_threebody_BR']/aa['native_Zee_one_loop_radiative_BR'],aa['dipole_only_threebody_over_radiative_factor'])
                self.assertAlmostEqual(bb['radiative_worst_case_given_assumption']/aa['radiative_worst_case_given_assumption'],9)


if __name__ == '__main__':
    unittest.main()
