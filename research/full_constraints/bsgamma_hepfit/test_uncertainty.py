import json, unittest
from pathlib import Path
import numpy as np
from execute import sha, parse
H=Path(__file__).resolve().parent
class UncertaintyEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.d=json.loads((H/'UNCERTAINTY_RUNS.json').read_text())
    def test_receipts(self):
        self.assertEqual(len(self.d['runs']),69)
        for label,r in self.d['runs'].items():
            p=H/'uncertainty_receipts'/label
            self.assertEqual(sha(Path(str(p)+'.txt')),r['input_sha256'])
            self.assertEqual(sha(Path(str(p)+'.log')),r['stdout_sha256'])
            self.assertEqual(parse(Path(str(p)+'.log').read_text()),r['values'])
    def test_correlated_covariance(self):
        d=self.d; l=np.array(d['cholesky']); c=np.array(d['covariance'])
        np.testing.assert_allclose(l@l.T,c,atol=1e-16)
        self.assertGreater(abs(c[3,4]),.001)
        j=np.array(d['fit_direction_sensitivity'])
        np.testing.assert_allclose(j@j.T,d['partial_fit_output_covariance'],atol=1e-25)
    def test_subtraction_and_preserved_central(self):
        old=json.loads((H/'execution/HEPFIT_EXECUTION.json').read_text())
        for label,r in self.d['responses'].items():
            for bid in ('d7_NO_neutral_near_heavy_07','F13_heavy_0001330'):
                self.assertAlmostEqual(r[bid]-r['SM'],r[bid+'_delta'],places=17)
                if label=='central': self.assertAlmostEqual(r[bid],old['runs'][bid+'_central']['values']['BR_NLO'],places=16)
    def test_no_promotion(self):
        for name in ('UNCERTAINTY_RUNS.json','UNCERTAINTY_COMPONENTS.json'):
            d=json.loads((H/name).read_text()); self.assertIsNone(d['theory_sigma']);self.assertIsNone(d['exclusion']);self.assertEqual(d['physical_bsgamma'],'UNKNOWN')
    def test_table_confidence_mismatch_retained(self):
        d=json.loads((H/'ONE_STATE_CONFIDENCE.json').read_text())
        self.assertTrue(472<d['mass_root_GeV']<474)
        self.assertFalse(d['Zee_transfer'])
if __name__=='__main__': unittest.main()
