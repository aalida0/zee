"""Executed source regressions, physics identities and invalid-interface controls."""
import json
import math
import unittest
from pathlib import Path
import pilot


class PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.card=json.loads((pilot.HERE/'input_card.json').read_text())
        cls.par=pilot.flavio.default_parameters.get_central_all()
        cls.saved=json.loads((pilot.HERE/'results.json').read_text())

    def test_independent_matching_archived_D9B_point(self):
        # Independent historical native/BMU comparison, not this pilot's output.
        ref={'C7_LO':-.05924467746457921,'C8_LO':-.06413402661914894,
             'C4_NLO_raw':.00163554035224135,'C7_NLO_raw':1.165884840387206,
             'C8_NLO_raw':.6133972999122068}
        actual=pilot.matching(550,5.3,163.16587299291515,160)
        for k,v in ref.items():
            self.assertAlmostEqual(actual[k],v,delta=3e-13)

    def test_flavio_upstream_published_SM_regression(self):
        self.assertAlmostEqual(pilot.rate({'C7':0,'C8':0},self.par)*1e4,3.36,delta=.2)
        self.assertAlmostEqual(pilot.rate({'C7':0,'C8':0},self.par),
                               self.saved['records'][0]['BR'],delta=1e-15)

    def test_EOS_three_upstream_regressions(self):
        for cut,ref in [(1.6,3.13699e-4),(1.8,3.09211e-4),(2.,3.00017e-4)]:
            self.assertAlmostEqual(pilot.eos_rate(self.card['eos_regression_overrides'],cut),ref,delta=1e-9)

    def test_dipoles_have_measurable_quadratic_response(self):
        zero=pilot.rate({'C7':0,'C8':0},self.par)
        for k in ('C7','C8'):
            def f(h):
                v={'C7':0,'C8':0};v[k]=h
                return pilot.rate(v,self.par)
            even=lambda h:(f(h)+f(-h))/2-zero
            self.assertGreater(abs(even(.01)),1e-10)
            self.assertAlmostEqual(even(.02),4*even(.01),delta=2e-18)
            self.assertGreater(abs(f(.01)-f(-.01)),1e-8)

    def test_two_state_rate_identities(self):
        _,v1=pilot.vector(550,5.3,self.card)
        _,v2=pilot.vector(900,5.3,self.card)
        def f(v):
            return pilot.rate({k:v[k] for k in ('C7','C8')},self.par)
        for a,b,g,target in [(v1,v2,0,f(v1)),(v1,v2,math.pi/2,f(v2)),
                             (v1,v1,1.09,f(v1)),
                             (v2,v1,math.pi/2-1.09,f(pilot.coherent(v1,v2,1.09)))]:
            self.assertAlmostEqual(f(pilot.coherent(a,b,g)),target,delta=1e-18)
        averaged=math.cos(1.09)**2*f(v1)+math.sin(1.09)**2*f(v2)
        self.assertGreater(abs(f(pilot.coherent(v1,v2,1.09))-averaged),1e-9)

    def test_decoupling_and_opposite_sign(self):
        zero=pilot.rate({'C7':0,'C8':0},self.par)
        def f(m,flip=False):
            _,v=pilot.vector(m,5.3,self.card,flip)
            return pilot.rate({k:v[k] for k in ('C7','C8')},self.par)
        self.assertGreater(f(550),f(900))
        self.assertLess(abs(f(100000)-zero),1e-8)
        self.assertLess(f(550,True),zero)

    def test_reject_unsupported_C4_and_invalid_inputs(self):
        with self.assertRaises(ValueError):
            pilot.wc_object({'C4':1e-5,'C7':0.,'C8':0.})
        self.assertFalse('C4_bs' in pilot.wcxf.Basis['WET','flavio'].all_wcs)
        with self.assertRaises((AssertionError,KeyError,ValueError)):
            w=pilot.flavio.WilsonCoefficients();w.set_initial({'C4_bs':1e-5},160)
        for m,tb in [(0,5.3),(550,0),(float('nan'),2),(550,float('inf'))]:
            with self.assertRaises(ValueError): pilot.vector(m,tb,self.card)
        with self.assertRaises(ValueError):
            pilot.vector(550,5.3,dict(self.card,mu0_GeV=120))

    def test_EOS_C4_is_a_total_low_scale_coefficient(self):
        p=pilot.eos.Parameters.Defaults(); k='b->s::c4';c=p[k].evaluate()
        baseline=pilot.eos_rate()
        shifted=pilot.eos_rate({k:c+.01})
        self.assertGreater(abs(shifted-baseline),1e-9)
        # WET intentionally ignores the requested coefficient scale; no RG here.
        self.assertAlmostEqual(shifted,pilot.eos_rate({k:c+.01,'b->s::mu_0t':160}),delta=1e-18)

    def test_flavio_cut_rejection(self):
        with self.assertRaises(ValueError):
            pilot.flavio.physics.bdecays.bxgamma.BRBXgamma(pilot.wc_object({}),self.par,'s',1.8)


if __name__=='__main__': unittest.main()
