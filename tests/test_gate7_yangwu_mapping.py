"""Gate 7: independent gauge-to-Higgs-basis quartic polynomial closure."""
import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gate7_map_p2_to_yangwu import map_point
from gate6_benchmark import benchmark

def prod(a,b):
    return sum(x.conjugate()*y for x,y in zip(a,b))


class HiggsBasisMapTests(unittest.TestCase):
    def test_point_closes_mass_derived_zhiggs_lambdas(self):
        out=map_point()
        r=out["closure_mass_basis_residuals"]
        for key,value in r.items():
            self.assertLess(abs(value),1e-8,key)
        self.assertAlmostEqual(out["map"]["ZEEINPUTS"][4],
                               math.pi/2-1.089,places=12)
        self.assertEqual(out["map"]["MASS"][227],700.)
        self.assertEqual(out["map"]["MASS"][228],300.)

    def test_quartic_polynomial_exact_in_arbitrary_complex_fields(self):
        p=benchmark();x=p["inputs"];q=p["quartics"]
        y=map_point()["map"]["ZEELAMS"];v=x["beta"]
        s,c=math.sin(v),math.cos(v)
        l1,l2,l3,l4,l5=[q["lambda"+str(i)] for i in range(1,6)]
        Z2,Z3,Z7=y[1],y[2],y[3]
        Zi=map_point()["internal_higgs_basis_quartics"]
        Z1,Z4,Z5,Z6=[Zi["lambda"+str(i)] for i in (1,4,5,6)]
        rng=random.Random(261011)
        for _ in range(12):
            A=[complex(rng.uniform(-2,2),rng.uniform(-2,2)) for _ in range(2)]
            B=[complex(rng.uniform(-2,2),rng.uniform(-2,2)) for _ in range(2)]
            P1=[c*a-s*b for a,b in zip(A,B)]
            P2=[s*a+c*b for a,b in zip(A,B)]
            X1=prod(P1,P1).real;X2=prod(P2,P2).real;Y=prod(P1,P2)
            original=.5*l1*X1**2+.5*l2*X2**2+l3*X1*X2 + \
                l4*abs(Y)**2+l5*(Y.real**2-Y.imag**2)
            X1=prod(A,A).real;X2=prod(B,B).real;Y=prod(A,B)
            rotated=.5*Z1*X1**2+.5*Z2*X2**2+Z3*X1*X2+ \
                Z4*abs(Y)**2+Z5*(Y.real**2-Y.imag**2)+ \
                2*Z6*X1*Y.real+2*Z7*X2*Y.real
            self.assertAlmostEqual(original,rotated,places=9)

    def test_singlet_quartic_basis_rotation(self):
        p=benchmark();o=map_point()
        b=p["inputs"]["beta"];s,c=math.sin(b),math.cos(b)
        K=o["map"]["ZEELAMS"];k1=p["inputs"]["k1"]
        k2=p["inputs"]["k2"];k12=p["inputs"]["k12"]
        rng=random.Random(7266)
        for _ in range(12):
            A=[complex(rng.uniform(-2,2),rng.uniform(-2,2)) for _ in range(2)]
            B=[complex(rng.uniform(-2,2),rng.uniform(-2,2)) for _ in range(2)]
            P1=[c*a-s*b for a,b in zip(A,B)]
            P2=[s*a+c*b for a,b in zip(A,B)]
            original=k1*prod(P1,P1).real + k2*prod(P2,P2).real - \
                     2*k12*prod(P1,P2).real
            converted=K[4]*prod(A,A).real+K[5]*prod(B,B).real+ \
                      2*K[6]*prod(A,B).real
            self.assertAlmostEqual(original,converted,places=10)


if __name__=="__main__":
    unittest.main()
