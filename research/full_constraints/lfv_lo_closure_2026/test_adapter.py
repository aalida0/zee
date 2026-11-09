import math, unittest
from adapter import al_kernel
from run import current
from research.full_constraints.lfv.source_to_code import box_kernel
class AdapterTests(unittest.TestCase):
 def test_null_rejected(self):
  with self.assertRaises(ValueError): al_kernel(None,*([0]*9))
 def test_components_and_interference(self):
  z=[0j]*10
  def calc(**kw):
   keys=['DL','DR','gpLV','gnLV','gpRV','gnRV','gpLS','gnLS','gpRS','gnRS']; a=z.copy()
   for k,v in kw.items(): a[keys.index(k)]=v
   return al_kernel(*a)
  for k in ['DR','gpLV','gpRS']:
   self.assertGreater(calc(**{k:1})[2],0)
  a=calc(gpLV=1+2j,gnLV=-.4j,gpRS=2-1j,gnRS=.3)[0]
  b=calc(gpLV=1+2j,gnLV=-.4j)[0]+calc(gpRS=2-1j,gnRS=.3)[0]
  self.assertLess(abs(a-b),1e-18)
  self.assertNotAlmostEqual(calc(gpLV=1,gpRS=1)[2],calc(gpLV=1,gpRS=1j)[2],places=10)
  self.assertNotEqual(calc(gpRS=1)[2],calc(gnRS=1)[2])
  self.assertAlmostEqual(current(13,14,2+1j,-1j),13*(2+1j)+14*(-1j))
 def test_exchange_and_degenerate(self):
  self.assertAlmostEqual(box_kernel(300,500,.6),box_kernel(500,300,math.pi/2-.6),places=19)
  self.assertAlmostEqual(box_kernel(300,300,.6)*300**2,1,places=14)
 def test_phase(self):
  a=[1+2j,-2+3j,1j,2,3j,4,5,6j,-7,8j]; x=al_kernel(*a); phase=complex(math.cos(.7),math.sin(.7)); y=al_kernel(*(phase*v for v in a))
  self.assertLess(abs(y[0]-phase*x[0]),1e-18); self.assertAlmostEqual(y[2]/x[2],1,places=14)
if __name__=='__main__': unittest.main()
