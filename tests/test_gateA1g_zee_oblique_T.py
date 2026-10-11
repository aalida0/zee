"""Gate A1G regression tests for scalar oblique T and mixing convention."""
import pathlib
import sys
import unittest
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1g_zee_oblique_T import (
    F,F_squared,charged_doublet_overlap,T_terms,oblique_T,report,
    BETA,GAMMA,MA,MH_HEAVY,MH1_CHARGED,MH2_CHARGED
)

class TestObliqueT(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results=report()

    def test_F_symmetric_nonnegative_and_degenerate(self):
        for a,b in [(300,700),(580.7,633.7),(125,700)]:
            self.assertAlmostEqual(F(a,b),F(b,a),places=9)
            self.assertGreaterEqual(F(a,b),0)
        self.assertEqual(F(500,500),0)
        self.assertGreater(F(500.00001,500),0)

    def test_grimus_charge_pair_overlap_from_mixing_matrix(self):
        P=charged_doublet_overlap()
        self.assertAlmostEqual(P[1,2],-np.sin(GAMMA)*np.cos(GAMMA))
        self.assertAlmostEqual(P[1,1],np.cos(GAMMA)**2)
        self.assertAlmostEqual(P[2,2],np.sin(GAMMA)**2)
        self.assertAlmostEqual(P[1,0],0,places=14)
        self.assertAlmostEqual(-2*abs(P[1,2])**2*F(MH1_CHARGED,MH2_CHARGED),
                               T_terms()["offdiagonal_charged_pair"],places=9)

    def test_2hdm_limit_singlet_decouples(self):
        # gamma=0: H1 is doublet and H2 is pure charged singlet.
        a,_=oblique_T(gamma=0,m2=700)
        b,_=oblique_T(gamma=0,m2=1200)
        self.assertAlmostEqual(a,b,places=12)
        self.assertEqual(T_terms(gamma=0)["offdiagonal_charged_pair"],0)

    def test_degenerate_charged_eigenvalues_angle_independent(self):
        # If the physical charged masses coincide, charged basis rotation
        # cannot alter T; charged pair F=0.
        a,_=oblique_T(gamma=.15,m1=510,m2=510)
        b,_=oblique_T(gamma=1.33,m1=510,m2=510)
        self.assertAlmostEqual(a,b,places=12)

    def test_custodial_neutral_and_charged_degeneration(self):
        # In exact neutral alignment and all heavy masses identical,
        # the new scalar-sector T must vanish (relative SM reference).
        a,_=oblique_T(alpha=BETA,mH=600,mA=600,m1=600,m2=600)
        self.assertAlmostEqual(a,0,places=12)

    def test_published_discrepancy_is_not_small(self):
        r=self.results
        self.assertAlmostEqual(r["preferred_general_Grimus_T"],
                               -.00490217831758,places=9)
        self.assertAlmostEqual(r["alternative_Herrero2017_T_not_recommended"],
                               .35538582266563,places=9)
        self.assertGreater(r["T_convention_difference"],.35)
        self.assertIn("NOT_CORRELATED",r["status"])

if __name__=="__main__":
    unittest.main()
