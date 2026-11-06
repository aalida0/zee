"""Integrity/dataflow tests; no test asserts unestablished physical accuracy."""
import json
import math
import unittest
import numpy as np
from final_validation import HERE, LOCAL, KEYS, ZERO, mix, probe
from pilot import digest, eos_rate


class FinalValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads((HERE/'final_validation.json').read_text())
        cls.card = json.loads((HERE/'final_card.json').read_text())

    def test_gate_remains_closed(self):
        r = self.r
        self.assertEqual(r['classification'], 'BSG_PHYSICAL_ACCURACY_BLOCKED')
        self.assertEqual(r['accuracy_domain'], 'ACCURACY_DOMAIN_UNKNOWN')
        self.assertFalse(r['Stage_A']['published_reference_reproduced'])
        self.assertFalse(r['Stage_A']['matched_independent_kernel_agreement'])
        self.assertIsNone(r['theory_sigma'])
        self.assertFalse(r['scan_filter_created'])
        self.assertIsNone(r['global_zee_acceptance'])
        for row in r['benchmarks'].values():
            self.assertEqual(row['physical_agreement'], 'NOT_EVALUATED')

    def test_sources_builds_and_evidence_are_bound(self):
        self.assertEqual(digest(HERE/'final_card.json'), self.r['input_card_sha256'])
        self.assertEqual(digest(HERE/'final_sources.json'), self.r['source_qualification_sha256'])
        self.assertEqual(digest(HERE/'bridge_results.json'), self.r['preserved_native_EOS_evidence_sha256'])
        for item in json.loads((HERE/'final_sources.json').read_text())['downloads']:
            self.assertEqual(digest(LOCAL/item['file']), item['sha256'])
        for name, item in self.r['builds']['builds'].items():
            self.assertEqual(digest(LOCAL/('final_si_'+name+'_probe')), item['binary_sha256'])
            self.assertTrue(all(code == 0 for code in item['exit_codes']))

    def test_minimal_cases_and_identities(self):
        rows = self.r['benchmarks']
        for m in self.card['one_state_masses_GeV']:
            for tb in self.card['tanbeta']:
                self.assertIn(f'M{m}_tb{tb}', rows)
        for kernel in self.r['identities'].values():
            for residual in kernel.values():
                self.assertLess(abs(residual), self.card['identity_absolute_tolerance'])
        self.assertLess(abs(rows['decoupling_100TeV']['SI_delta_BR']), 1e-8)
        self.assertLess(rows['opposite_coupling_control']['SI_delta_BR'], 0)
        a,b=rows['M550_tb5.3']['raw_matching'],rows['M900_tb5.3']['raw_matching']
        self.assertEqual(mix(a,b,1.09), rows['two_state']['raw_matching'])
        weighted = math.cos(1.09)**2*rows['M550_tb5.3']['SuperIso']['NP_BR_NLO']+math.sin(1.09)**2*rows['M900_tb5.3']['SuperIso']['NP_BR_NLO']
        self.assertGreater(abs(rows['two_state']['SuperIso']['NP_BR_NLO']-weighted),1e-9)

    def test_second_kernel_receives_identical_ordinary_total_vector(self):
        for label in ('zero_NP','M550_tb5.3','C4_+1'):
            row=self.r['benchmarks'][label]
            si=probe(row['raw_matching'])
            low=np.array([si[f'NP_ordinary_low_C{i}'] for i in range(1,9)])
            np.testing.assert_allclose(low,row['identical_low_total_vector_supplied_to_EOS'],
                                       rtol=0,atol=self.card['identical_low_input_absolute_tolerance'])
            br=eos_rate({**self.r['shared_EOS_parameter_overrides'],**dict(zip(KEYS,low))})
            self.assertAlmostEqual(br,row['EOS_BR_shared_low_vector'],delta=2e-15)
            self.assertAlmostEqual(si['NP_BR_NLO'],row['SuperIso']['NP_BR_NLO'],delta=2e-15)

    def test_residuals_and_signed_NLO_counting(self):
        rows=self.r['benchmarks']; zero=rows['zero_NP']
        for row in rows.values():
            si=row['SuperIso']
            self.assertEqual(si['P2'],0.)
            self.assertAlmostEqual(row['signed_BR_residual_EOS_minus_SI'],
                row['EOS_BR_shared_low_vector']-si['NP_BR_NLO'],delta=1e-18)
            self.assertAlmostEqual(row['signed_delta_BR_residual_EOS_minus_SI'],
                row['EOS_delta_BR_shared_low_vector']-row['SI_delta_BR'],delta=1e-18)
        for i in self.card['signed_probe_operators']:
            plus,minus=rows[f'C{i}_+1'],rows[f'C{i}_-1']
            np.testing.assert_allclose(list(plus['raw_matching'].values()),
                                       -np.array(list(minus['raw_matching'].values())),atol=0)
            key='C4_NLO_raw' if i==4 else f'C{i}_LO'
            physical=plus['raw_matching'][key]
            if i==4:physical*=zero['SuperIso']['alpha_s_mu0']/(4*math.pi)
            self.assertAlmostEqual(physical,self.card['signed_high_scale_physical_step'])
            self.assertNotEqual(self.r['signed_high_scale_responses'][f'C{i}']['SI']['odd'],0.)
        # A concrete prescription distinction: NLO-only C4 has no square at NLO.
        self.assertAlmostEqual(self.r['signed_high_scale_responses']['C4']['SI']['even'],0.,delta=2e-15)
        self.assertGreater(self.r['signed_high_scale_responses']['C4']['EOS_BR_shared_low_vector']['even'],1e-9)

    def test_historical_uncut_card_is_actually_rejected(self):
        with self.assertRaises(RuntimeError):
            eos_rate(model='SM',cut=0.)
        self.assertEqual(self.r['EOS_uncut_reference_attempt']['status'],'UNSUPPORTED')
        self.assertIsNone(self.card['independent_physical_rate_tolerance'])


if __name__ == '__main__':
    unittest.main()
