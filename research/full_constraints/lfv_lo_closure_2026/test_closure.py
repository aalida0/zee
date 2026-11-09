import math, unittest
from run import current
from research.full_constraints.lfv.source_to_code import box_kernel
class Checks(unittest.TestCase):
 def test_complex_scalar_vector_interference(self):
  z,n=13,14; sp,sn=2+3j,-1+2j; vp,vn=1-2j,4+1j
  self.assertAlmostEqual(abs(current(z,n,sp,sn)+current(z,n,vp,vn)-(z*(sp+vp)+n*(sn+vn))),0,places=12)
  wrong=z*sn+n*sp+z*vp+n*vn
  self.assertGreater(abs(wrong-(z*(sp+vp)+n*(sn+vn))),1)
 def test_isovector_interference(self):
  self.assertEqual(current(79,118,1,-1)+current(79,118,1,-1),-78)
 def test_equal_mass_and_exchange(self):
  a,b,g=300.,500.,.6
  self.assertAlmostEqual(box_kernel(a,a,g)*a*a,1.,places=14)
  self.assertAlmostEqual(box_kernel(a,b,g),box_kernel(b,a,math.pi/2-g),places=19)
if __name__=='__main__': unittest.main()
