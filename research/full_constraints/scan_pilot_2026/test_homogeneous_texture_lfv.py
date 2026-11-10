import math,unittest
from research.full_constraints.scan_pilot_2026 import homogeneous_texture_lfv as t
from research.full_constraints.scan_pilot_2026.vacuum_followup import strict_inputs

class HomogeneousLFVTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.points={r["id"]:r for r in strict_inputs()}
    def test_eta1_replays_original_native_module4(self):
        x=t.evaluate_texture(self.points[284],"IO",0,1.0)
        self.assertEqual(x["status"],"NEUTRINO_PASS_LFV_PARTIAL")
        self.assertAlmostEqual(x["partial_lfv"]["mu_to_e_gamma_BR"]/t.FROZEN[284,"IO",0],1,places=11)
        self.assertFalse(x["partial_lfv"]["complete_Zee_LFV"])
        self.assertIsNone(x["global_acceptance"])
    def test_zero_homogeneous_preserves_exact_neutrino_target(self):
        p=t.evaluate_texture(self.points[284],"NO",0,0.0)
        self.assertEqual(p["status"],"NEUTRINO_PASS_LFV_PARTIAL")
        self.assertLess(p["neutrino_closure"],2e-9)
        self.assertEqual(p["nu_input"]["homogeneous_coefficients"]["real"],[0.0]*4)
        self.assertEqual(p["nu_input"]["homogeneous_coefficients"]["imag"],[0.0]*4)
        self.assertIsNone(p["global_acceptance"])
        self.assertEqual(p["physical_LFV"],"UNKNOWN")
    def test_scale_maintains_Zee_F_and_target(self):
        r1=t.evaluate_texture(self.points[284],"NO",0,1.0)
        r0=t.evaluate_texture(self.points[284],"NO",0,0.0)
        for key in ("null_cone","target_eV","scalar","ordering"):
            self.assertEqual(r0["nu_input"][key],r1["nu_input"][key])
    def test_undefined_scale_fails(self):
        with self.assertRaises(ValueError):
            t.evaluate_texture(self.points[284],"NO",0,0.002)

if __name__=="__main__":
    unittest.main()
