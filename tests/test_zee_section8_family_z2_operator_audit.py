"""Regress exact family-Z2 charge audit for Zee + TypeII quarks."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_section8_family_z2_operator_audit import CHARGE,OPERATORS,sign,report

class TestSection8FamilyZ2(unittest.TestCase):
    def test_same_symmetry_suppresses_wrong_doublet_quark_Yukawas(self):
        r=report()
        s=r["operator_invariant_signs"]
        self.assertEqual(s["up_to_Phi2"],1)
        self.assertEqual(s["down_to_Phi1"],1)
        self.assertEqual(s["up_wrong_Phi1"],-1)
        self.assertEqual(s["down_wrong_Phi2"],-1)

    def test_required_neutrino_sources_and_lepton_textures(self):
        s=report()["operator_invariant_signs"]
        self.assertEqual(s["f_e_mu_chi"],1)
        self.assertEqual(s["f_e_tau_chi"],1)
        self.assertEqual(s["f_mu_tau_chi"],-1)
        self.assertEqual(s["lepton_e_to_Phi2"],1)
        self.assertEqual(s["lepton_mu_to_Phi1"],1)
        self.assertEqual(s["lepton_tau_to_Phi1"],1)

    def test_soft_breaking_m12_and_hard_breaking_k12(self):
        s=report()["operator_invariant_signs"]
        self.assertEqual(s["mu4_Phi1_Phi2_chi"],1)
        self.assertEqual(s["m12sq_Phi1dag_Phi2_SOFT"],-1)
        self.assertEqual(s["k12_Phi1dag_Phi2_chichi_HARD"],-1)
        self.assertEqual(s["lambda5_Phi1dagPhi2_squared"],1)
        self.assertFalse(report()["published_P2_nonzero_k12_is_exact_Z2_consistent"])

    def test_z2_rephasing_signs_are_unchanged_by_conjugation(self):
        self.assertEqual(sign(["Phi2","chi"]),1)
        self.assertEqual(sign(["Phi1","Phi2"]),-1)
        self.assertEqual(set(CHARGE.values()),{-1,1})

if __name__=="__main__":
    unittest.main()
