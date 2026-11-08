import json,unittest
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent
class Ledger(unittest.TestCase):
 def test_card_ledger_and_complex_interference(self):
  d=json.loads((P/'DIPOLE_TERMS.json').read_text());self.assertEqual(len(d['cards']),4)
  for r in d['cards']:
   b=np.array([complex(*v) for v in r['baseline_C']]);z=np.array([complex(*v) for v in r['zgamma_C']]);h=np.array([complex(*v) for v in r['hZ_provisional_source_C']]);s=np.array([complex(*v) for v in r['sum_C']]);self.assertTrue(np.allclose(s,b+z+h,rtol=1e-14,atol=0));self.assertNotEqual(np.vdot(b+z,h).real,0);self.assertGreater(r['missing_norm_budget_GeV_minus2'],0)
 def test_control_and_missing(self):
  x=json.loads((P/'HZ_CONTROLS.json').read_text());self.assertLess(max(max(c['relative_error']) for c in x['controls']),1e-4)
  o=json.loads((P/'OPERATOR_LEDGER.json').read_text());self.assertIsNone(o['mu3e']['coefficient']);self.assertIsNone(o['muAl_conversion']['coefficient'])
 def test_phase_invariance(self):
  r=json.loads((P/'DIPOLE_TERMS.json').read_text())['cards'][0];v=np.array([complex(*x) for x in r['sum_C']]);self.assertAlmostEqual(np.linalg.norm(v*np.exp(.73j))/np.linalg.norm(v),1.)
if __name__=='__main__': unittest.main(verbosity=2)
