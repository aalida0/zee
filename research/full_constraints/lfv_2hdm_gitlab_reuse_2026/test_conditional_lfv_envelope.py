import math
import unittest
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.conditional_lfv_envelope import (
    SOURCE,LIMITS_90CL,evaluate,
)

class ConditionalEnvelopeTests(unittest.TestCase):
    def test_strict_incomplete_scope_never_physical(self):
        a=evaluate(300.)
        self.assertTrue(a['all_conditional_sufficient_pass'])
        self.assertEqual(a['physical_lfv'],'UNKNOWN')
        self.assertIsNone(a['global_acceptance'])
        for card in a['cards'].values():
            for p in card.values():
                self.assertTrue(p['conditional_sufficient_pass'])
                self.assertIsNone(p['physical_pass'])

    def test_source_only_and_monotonic(self):
        a,b=evaluate(0),evaluate(100)
        for card in SOURCE:
            for p in LIMITS_90CL:
                self.assertAlmostEqual(a['cards'][card][p]['worst_case_rate_given_assumption'],SOURCE[card][p])
                self.assertGreater(b['cards'][card][p]['worst_case_rate_given_assumption'],
                                   a['cards'][card][p]['worst_case_rate_given_assumption'])

    def test_boundary_reproduces_experimental_limit(self):
        a=evaluate(0)
        for card in SOURCE:
            for p in LIMITS_90CL:
                k=a['cards'][card][p]['max_assumed_missing_amplitude_over_source_amplitude']
                value=(1+k)**2*SOURCE[card][p]
                self.assertAlmostEqual(value/LIMITS_90CL[p],1.0,places=12)

    def test_all_300_assumptions_pass(self):
        a=evaluate(300)
        for card in SOURCE:
            self.assertTrue(all(x['conditional_sufficient_pass'] for x in a['cards'][card].values()))

    def test_above_tightest_d7io_radiative_fails(self):
        a=evaluate(400)
        self.assertFalse(a['cards']['D7_IO']['muegamma']['conditional_sufficient_pass'])
        self.assertFalse(a['all_conditional_sufficient_pass'])

    def test_invalid_kappa(self):
        for bad in [-1,float('nan'),float('inf'),float('-inf')]:
            with self.assertRaises(ValueError):evaluate(bad)

    def test_missing_process_or_rate(self):
        with self.assertRaises(ValueError):evaluate(1,{'x':{'muegamma':1e-20}})
        with self.assertRaises(ValueError):evaluate(1,{'x':{'muegamma':1e-20,'mu3e':0,'muAu':1e-20}})
        with self.assertRaises(ValueError):evaluate(1,limits={'muegamma':1e-13})

if __name__=='__main__':unittest.main()
