"""Gate A1P: regression tests for analytically diagnosed C3/C4 logs."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1p_verify_nnlo_log_difference import d3,d4,predicted_shift

MT=163.10709645657508
MU=160.7384
TANB=5.597170833164245

OBSERVED={
    300.:(-0.007486068757928677,+0.018263691796955004),
    700.:(-0.007333742627289074,+0.02278235276814626),
    1000.:(-0.005800221095394414,+0.01929192873686826),
    2000.:(-0.0029934144094091943,+0.010914545187582574),
}

class TestGateA1PNNLOLog(unittest.TestCase):
    def test_complete_eight_observed_residuals_reproduced(self):
        for mass,(expected3,expected4) in OBSERVED.items():
            for order,expected in ((3,expected3),(4,expected4)):
                actual,d,ls,lh=predicted_shift(order,mass,MT,MU,TANB)
                self.assertAlmostEqual(actual,expected,delta=1e-12,
                                       msg=f"mass={mass} C{order}")
                self.assertTrue(math.isfinite(d))
                self.assertAlmostEqual(lh,math.log((MU/MT)**2),places=14)

    def test_log_derivative_has_opposite_sign_between_sources(self):
        # Distinguishes the audit from a vacuous fit to eight numbers.
        for mass in OBSERVED:
            x=(MT/mass)**2
            for order,fn in ((3,d3),(4,d4)):
                dd=fn(x)
                self.assertNotEqual(dd,0.)
                eps=1e-5
                f0=predicted_shift(order,mass,MT,MU,TANB)[0]
                f1=predicted_shift(order,mass,MT,
                                   MU*math.exp(eps/2),TANB)[0]
                derivative=(f1-f0)/eps
                self.assertAlmostEqual(
                    derivative,-2*dd/TANB**2,
                    delta=2e-7,msg=f"mass={mass} C{order}")

    def test_reject_mass_below_running_top_for_this_audit(self):
        with self.assertRaisesRegex(ValueError,"masses > running top"):
            predicted_shift(3,160,MT,MU,TANB)

if __name__=="__main__":
    unittest.main()
