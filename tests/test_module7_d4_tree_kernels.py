"""Generic matrix-element kernels only; real Zee vertex validation is D4 work."""
import math
import unittest

from module7.d4_tree_kernels import (
    STATUS,phase_space,scalar_vector,scalar_scalar,scalar_fermions
)
from module7.cascade_z import cascade_width


class TreeKernelTests(unittest.TestCase):
    def test_vector_agrees_independently_with_validated_D3(self):
        for m in (250.,300.,350.):
            args=dict(mH1_GeV=m,mH2_GeV=700.,mZ_GeV=91.1876,
                      mW_GeV=80.379,v_GeV=246.21965,gamma_rad=1.089)
            src=cascade_width(args)["partial_width_GeV"]
            g=2*args["mW_GeV"]/args["v_GeV"]
            cw=args["mW_GeV"]/args["mZ_GeV"]
            coeff=-g/(4*cw)*math.sin(2*args["gamma_rad"])
            dest=scalar_vector(args["mH2_GeV"],m,args["mZ_GeV"],coeff)
            self.assertAlmostEqual(dest,src,delta=2e-13)
        self.assertEqual(STATUS,"GENERIC_TREE_PARTIAL_WIDTH_KERNEL_ONLY")

    def test_vector_longitudinal_scaling(self):
        M,ms,mv,c=700.,300.,91.1876,0.15207461883074225
        lam=phase_space(M,ms,mv)
        explicit=abs(c)**2*lam**3/(16*math.pi*M**3*mv*mv)
        self.assertAlmostEqual(scalar_vector(M,ms,mv,c),explicit,places=13)
        self.assertAlmostEqual(scalar_vector(M,ms,mv,1j*c),
                               explicit,places=13)

    def test_scalar_scalar_known_constant_amplitude(self):
        M,m1,m2,t=700.,250.,125.,42.5
        val=scalar_scalar(M,m1,m2,t)
        p=phase_space(M,m1,m2)/(2*M)
        independent=t*t*p/(8*math.pi*M*M)
        self.assertAlmostEqual(val,independent,places=13)
        self.assertAlmostEqual(val,scalar_scalar(M,m1,m2,-1j*t),places=13)
        self.assertEqual(scalar_scalar(100.,250.,125.,t),0.)

    def test_fermion_massless_oracle_and_cp(self):
        M=700.
        self.assertAlmostEqual(scalar_fermions(M,0.,0.,1.,0.,3),
                               3*M/(16*math.pi),places=12)
        self.assertAlmostEqual(scalar_fermions(M,0.,0.,0.,1j,1),
                               M/(16*math.pi),places=12)
        a,b=.13+.19j,-.08+.02j
        x=scalar_fermions(M,172.7,4.2,a,b,3)
        y=scalar_fermions(M,172.7,4.2,a.conjugate(),b.conjugate(),3)
        self.assertAlmostEqual(x,y,places=13)
        self.assertGreater(x,0.)

    def test_fermion_interference_and_threshold(self):
        M,mi,mj=700.,172.7,4.2
        x=scalar_fermions(M,mi,mj,1.,1.,3)
        y=scalar_fermions(M,mi,mj,1.,-1.,3)
        self.assertGreater(y,x)
        self.assertEqual(scalar_fermions(100.,mi,mj,.1,.2,3),0.)
        self.assertEqual(scalar_fermions(mi+mj,mi,mj,.1,.2,3),0.)

    def test_strict_types_and_no_fake_color_factor(self):
        samples=[
            lambda:phase_space(True,100.,0.),
            lambda:phase_space(700.,float("nan"),0.),
            lambda:scalar_vector(700.,300.,0.,.5),
            lambda:scalar_vector(700.,300.,91.,complex(float("nan"),0.)),
            lambda:scalar_scalar(700.,300.,125.,None),
            lambda:scalar_fermions(700.,172.,4.,.1,.2,True),
            lambda:scalar_fermions(700.,172.,4.,.1,.2,2),
            lambda:scalar_fermions(700.,172.,4.,.1,float("inf"),3),
        ]
        for fn in samples:
            with self.subTest(fn=fn),self.assertRaises((ValueError,TypeError)):
                fn()


if __name__=="__main__":
    unittest.main()
