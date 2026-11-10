import math
import unittest
from unittest.mock import patch

from research.full_constraints.scan_pilot_2026 import reseed_lfv_pilot as impl
from research.full_constraints.scan_pilot_2026.vacuum_followup import strict_inputs

class ReseededFamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.cards={r["id"]:r for r in strict_inputs()}
    def test_pinned_old_families_reproduce_existing_partial_lfv(self):
        # Required physics closure: the old family #0 must reproduce the
        # exact retained 400-pilot complex amplitude at 1e-10 relative.
        for id,ordering in ((284,"NO"),(284,"IO"),(112,"NO")):
            r=impl.evaluate_one(self.cards[id],ordering,0)
            self.assertEqual(r["LFV"],"PARTIAL")
            self.assertEqual(r["physical_LFV"],"UNKNOWN")
            self.assertIsNone(r["global_acceptance"])
            self.assertAlmostEqual(r["partial_mu_to_e_gamma_BR"]/impl.FROZEN[id,ordering,0],1,places=9)
    def test_proposed_perturbativity_inversion_failure_has_no_rate(self):
        with patch.object(impl,"neutrino_family",return_value={
                "status":"FAIL","closure_status":"PASS",
                "seed_sha256":"0"*64,"input_sha256":None,"target_sha256":None,"input":None}):
            x=impl.evaluate_one(self.cards[284],"NO",2)
        self.assertEqual(x["LFV"],"NOT_EVALUATED")
        self.assertNotIn("partial_mu_to_e_gamma_BR",x)
    def test_invalid_seed_or_flavor(self):
        for q,f in (("XX",0),("NO",-1),("NO",1.0)):
            with self.assertRaises(ValueError):impl.evaluate_one(self.cards[284],q,f)

if __name__=="__main__":
    unittest.main()
