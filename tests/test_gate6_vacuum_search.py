"""Gate 6 charged-breaking potential sanity checks."""
import math
import sys
import unittest
import numpy as np
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate6_benchmark import benchmark
from gate6_vacuum_search import potential,search


class Gate6VacuumTest(unittest.TestCase):
    def test_normal_vacuum_is_stationary(self):
        p=benchmark()
        x=p["inputs"]
        beta=x["beta"];v=x["v"]
        vec=np.array([v*math.cos(beta)/math.sqrt(2),0,0,
                      v*math.sin(beta)/math.sqrt(2),0,0,0],float)
        h=1e-4
        for i in range(7):
            plus=vec.copy(); minus=vec.copy()
            plus[i]+=h;minus[i]-=h
            derivative=(potential(plus,p)-potential(minus,p))/(2*h)
            self.assertLess(abs(derivative),.02)

    def test_multistart_explicitly_not_global_certificate(self):
        out=search(beta=1.394,nstarts=2,seed=1)
        self.assertIn("NOT_A_GLOBAL_CERTIFICATE",out["status"])
        self.assertFalse(out["deeper_point_found"])
        self.assertLess(abs(out["best_minus_neutral_GeV4"]),1e-3)


if __name__=="__main__":
    unittest.main()
