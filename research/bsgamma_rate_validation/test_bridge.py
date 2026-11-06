"""Analytic operator/RG checks; these do not certify physical rate accuracy."""
import json
import math
import unittest
import numpy as np
from bridge import Native,direct_jms,KEYS,HERE,eos_rate
from wilson.run.wet.classes import WETrunner


class BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n=Native()
        cls.r=json.loads((HERE/'bridge_results.json').read_text())

    def test_direct_JMS_basis_and_chirality(self):
        w,k=direct_jms(.01,-.03,-.04)
        w.validate()
        self.assertAlmostEqual(w.dict['VddLL_1231']/k.conjugate(),.005)
        self.assertAlmostEqual(w.dict['VddLL_2223']/k,.01/3)
        self.assertFalse(any(x in w.dict for x in ['dgamma_32','dG_32']))
        d=w.translate('flavio').dict
        self.assertAlmostEqual(d['C7_bs'],-.03,delta=1e-12)
        self.assertAlmostEqual(d['C8_bs'],-.04,delta=1e-12)

    def test_EOS_translation_phase_defect_is_not_a_basis_inverse(self):
        for gamma in [1e-8,1.27]:
            w,k=direct_jms(.01,0,0,parameters={'gamma':gamma})
            t=w.translate('EOS',parameters={'gamma':gamma}).dict
            for i in [1,2,3,5,6]:self.assertLess(abs(t.get(f'b->s::c{i}',0)),1e-12)
            # Analytic signature of source's np.real-before-CKM-normalization.
            self.assertAlmostEqual(t['b->s::c4']*k,.01*k.real,delta=1e-20)
            if gamma>1:
                self.assertGreater(abs(complex(t['b->s::c4']).imag),1e-5)

    def test_same_scale_matching_and_alpha_s_normalization(self):
        n=self.n;a=np.zeros(15);b=a.copy();c=a.copy()
        b[3]=.2;b[11]=-.03;b[12]=-.04;c[11]=.8;c[12]=.5
        out=n.evolve(a,b,c,n.as0,n.as0);al=n.as0/(4*math.pi)
        self.assertAlmostEqual(out[3],al*.2,delta=1e-13)
        self.assertAlmostEqual(out[11]/al,-.03+al*.8,delta=1e-12)
        self.assertAlmostEqual(out[12]/al,-.04+al*.5,delta=1e-12)

    def test_native_LO_dipole_evolution_matches_analytic_solution(self):
        n=self.n;z=np.zeros(15);b=z.copy();b[11]=-.03;b[12]=-.04
        f=lambda t:n.evolve(z,b,z,n.as0*t,n.asb*t)[11:13]/(n.asb*t/(4*math.pi))
        lo=2*f(1)-f(2);eta=n.as0/n.asb
        ref=[eta**(16/23)*b[11]+8/3*(eta**(14/23)-eta**(16/23))*b[12],eta**(14/23)*b[12]]
        np.testing.assert_allclose(lo,ref,rtol=2e-12,atol=1e-13)
        # The exact polynomial dependence also checks the perturbative projection.
        np.testing.assert_allclose(f(3),2*f(2)-f(1),rtol=1e-12,atol=1e-13)

    def test_C4_induced_operators_and_counting(self):
        n=self.n;z=np.zeros(15);b=z.copy();b[3]=1
        f=lambda t:n.evolve(z,b,z,n.as0*t,n.asb*t)[11:13]/(n.asb*t/(4*math.pi))
        np.testing.assert_allclose(f(2),2*f(1),atol=1e-12)
        raw=dict(C4_NLO_raw=1.,C7_LO=0.,C8_LO=0.,C7_NLO_raw=0.,C8_NLO_raw=0.)
        low=n.np_coefficients(raw)
        self.assertTrue(all(abs(x)>1e-6 for x in low[2:6]))
        np.testing.assert_allclose(low[:2],0,atol=1e-12)
        np.testing.assert_allclose(n.evolve(z,b,z)[6:11],0,atol=1e-12)
        self.assertGreater(abs(low[7]),1e-3)

    def test_SM_and_two_state_live_rate_checks(self):
        n=self.n
        self.assertAlmostEqual(eos_rate(dict(zip(KEYS,n.sm))),eos_rate(model='SM'),delta=1e-15)
        rows={x['label']:x for x in self.r['records']}
        for name in ['zero_NP','M550_tb5.3_flipFalse','M900_tb5.3_flipFalse','two_state','M550_tb5.3_flipTrue']:
            br,_=n.br(rows[name]['raw_matching'])
            self.assertAlmostEqual(br,rows[name]['BR_native_prescription'],delta=1e-15)
        for v in self.r['identities'].values():self.assertLess(abs(v),1e-16)
        self.assertGreater(abs(self.r['coherent_minus_weighted_BR']),1e-9)
        self.assertGreater(rows['M550_tb5.3_flipFalse']['C4_BR_difference'],1e-10)
        self.assertLess(rows['M550_tb5.3_flipTrue']['BR_native_prescription'],rows['zero_NP']['BR_native_prescription'])
        self.assertLess(abs(rows['M100000_tb5.3_flipFalse']['BR_native_prescription']-rows['zero_NP']['BR_native_prescription']),1e-8)

    def test_wilson_has_no_NLO_ADM_option(self):
        w,_=direct_jms(0,.01,0)
        with self.assertRaises(UnboundLocalError):WETrunner(w,qcd_order=2,qed_order=0).run(4.2,sectors=('sb',))


if __name__=='__main__':unittest.main()
