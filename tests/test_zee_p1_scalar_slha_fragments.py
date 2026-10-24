"""Yang/Wu scalar basis MASSES, ZEELAMS, ZEEINPUTS real source fragments."""
import math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_p1_scalar_higgs_basis_map import check_quartic
from zee_p1_scalar_slha_fragments import fragment,NAMES,STATUS

def point():
 return {"id":"B4_SCALAR","mH1":300.,"mH2":700.,
 "mh2":580.7,"ma":633.7,"alpha":1.398,"beta":1.394,
 "gamma":1.089,"m12sq":57700.,"lc":4.473,
 "k1":1.082,"k2":.00398,"k12":-.001266}

class ScalarCards(unittest.TestCase):
 def test_original_model_full_basis_card_indices(self):
  p=point();source=check_quartic(p,trial_count=30)
  txt=fragment(p,source)
  self.assertEqual(txt.count("BLOCK "),3)
  self.assertIn("BLOCK MASS",txt)
  self.assertIn("BLOCK ZEEINPUTS",txt)
  self.assertIn("BLOCK ZEELAMS",txt)
  self.assertEqual(len([x for x in txt.splitlines()
    if x.startswith(" ") ]),5+4+7)
  self.assertEqual(set(source["YangWu_external"]),set(NAMES))

 def test_wrong_potential_reconstruction_is_rejected(self):
  p=point();src=check_quartic(p,trial_count=5)
  src["internal_mass_and_mu4_muzee_closed"]=False
  with self.assertRaisesRegex(ValueError,"not verified"):
   fragment(p,src)

 def test_bad_mass_is_rejected(self):
  p=point();src=check_quartic(p,trial_count=5)
  p["mH2"]=-500.
  with self.assertRaisesRegex(ValueError,"Nonphysical scalar"):
   fragment(p,src)

if __name__=="__main__":unittest.main()
