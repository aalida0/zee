"""C5 dimensionful Zee charge-breaking vacuum search: analytic proof regressions.

No finite multistart search is labelled a global vacuum proof. Negative
potential-value witness *is* an exact disproof if found and reproduced.
"""
from pathlib import Path
import math
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from gate6_benchmark import benchmark
from zee_gateC1_joined_uv_pilot import (
    VEV,scalar_lagrangian
)
from zee_gateC2_paired_uv_rescue import varied_point
from zee_gateC5_charge_breaking_vacuum_search import (
    EMBED,WITNESS_MARGIN,scalar_cache,full_field,
    potential_gradient_hessian,gauge_value_and_gradient,
    electroweak_check,candidate_starts,evaluate_multistart,
    cohort_summary,TARGET_VARIANTS
)

def fixture():
    return {
        'id':'C5_SYNTHETIC_NOT_ALLOWED','beta':1.394,
        'alpha':1.398,'gamma':1.089,'mH1':300.,'mH2':700.,
        'mh2':580.7,'ma':633.7,'m12sq':57700.,
        'lc':4.473,'k1':1.082,'k2':.00398,'k12':-.001266
    }

def state_from(p):
    q,_=scalar_lagrangian(p)
    return q

class TestGateC5GlobalVacuumSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.point=fixture()
        cls.state=state_from(cls.point)
        cls.cache=scalar_cache(cls.state)

    def test_six_dimensional_gauge_embedding(self):
        x=np.array((1,2,3,4,5,6),float)
        r=full_field(x)
        self.assertEqual(r.shape,(10,))
        np.testing.assert_allclose(r[EMBED],x)
        self.assertEqual(np.sum(abs(r[[0,1,3,5]])),0.)

    def test_invalid_gauge_vectors_rejected(self):
        with self.assertRaisesRegex(ValueError,'six-component'):
            full_field(np.ones(7))
        with self.assertRaisesRegex(ValueError,'finite'):
            full_field(np.array([1,2,3,4,5,np.nan]))

    def test_ew_vacuum_is_stationary_with_physical_mass_hessian(self):
        e=electroweak_check(self.point,self.cache)
        self.assertLess(e['stationarity_max_gradient_over_v3'],1e-9)
        self.assertLess(e['physical_plus_goldstone_spectrum_relmax'],1e-7)
        self.assertEqual(len(e['physical_eigenvalues_GeV2']),7)
        self.assertEqual(len(e['goldstone_eigenvalues_GeV2']),3)

    def test_mass_spectrum_closure_after_lowering_both_quartics(self):
        for cfg in ((1.,1.),(.4,.5)):
            p=varied_point(self.point,cfg[0],cfg[1])
            d=electroweak_check(p,scalar_cache(state_from(p)))
            self.assertLess(d['physical_plus_goldstone_spectrum_relmax'],1e-7)

    def test_exact_ten_field_potential_matches_quadratic_cubic_quartic_parts(self):
        from zee_section8_Q4_independent_dimensional_scalar_gate import (
            potential_quadratic,potential_cubic
        )
        from zee_section8_Q4_independent_scalar_hessian_gate import (
            invariants
        )
        rng=np.random.default_rng(20261019)
        for _ in range(16):
            r=rng.normal(size=10)*450
            c=self.cache
            actual,_,_=potential_gradient_hessian(r,c)
            q=invariants(r)
            expected=(potential_quadratic(r,c['mass_terms'])+
                      potential_cubic(r,c['muZee'])+q@c['C']@q)
            self.assertAlmostEqual(actual/VEV**4,expected/VEV**4,delta=1e-10)

    def test_ten_field_analytic_gradient_finite_difference(self):
        rng=np.random.default_rng(20261020)
        r=rng.normal(size=10)*200
        _,analytical,_=potential_gradient_hessian(r,self.cache)
        for k in range(10):
            h=1e-3
            rp=r.copy();rm=r.copy();rp[k]+=h;rm[k]-=h
            vp=potential_gradient_hessian(rp,self.cache)[0]
            vm=potential_gradient_hessian(rm,self.cache)[0]
            fd=(vp-vm)/(2*h)
            self.assertAlmostEqual(fd/VEV**3,analytical[k]/VEV**3,
                                   delta=1e-7)

    def test_ten_field_analytic_hessian_finite_difference(self):
        rng=np.random.default_rng(20261021)
        r=rng.normal(size=10)*120
        _,_,H=potential_gradient_hessian(r,self.cache)
        for k in range(10):
            h=1e-3
            rp=r.copy();rm=r.copy();rp[k]+=h;rm[k]-=h
            gp=potential_gradient_hessian(rp,self.cache)[1]
            gm=potential_gradient_hessian(rm,self.cache)[1]
            fd=(gp-gm)/(2*h)
            np.testing.assert_allclose(fd,H[:,k],rtol=2e-6,atol=1e-4)

    def test_gauge_variable_derivative_chain_rule(self):
        x=np.array([.6,.12,.7,-.1,.17,.05])
        val,g=gauge_value_and_gradient(x,self.cache)
        self.assertTrue(np.isfinite(g).all())
        for i in range(6):
            h=1e-5
            a=x.copy();b=x.copy();a[i]+=h;b[i]-=h
            fd=(gauge_value_and_gradient(a,self.cache)[0]-
                gauge_value_and_gradient(b,self.cache)[0])/(2*h)
            self.assertAlmostEqual(fd,g[i],delta=1e-8)

    def test_multistart_reproducible_128_distinct_initial_modes(self):
        a=candidate_starts(128,20261019)
        b=candidate_starts(128,20261019)
        np.testing.assert_array_equal(a,b)
        self.assertEqual(a.shape,(128,6))
        self.assertGreater(len(np.unique(a,axis=0)),100)

    def test_at_least_64_starts_required(self):
        with self.assertRaisesRegex(ValueError,'64'):
            candidate_starts(32,1)

    def test_ew_reference_rechecked_and_perturbed_point_evaluated(self):
        p=self.point;c=self.cache
        s=candidate_starts(64,20261019)
        # Allow discovery of a deeper vacuum! The output must remain
        # noncertifying whatever the optimizer finds.
        out=evaluate_multistart(p,self.state,s,maxiter=250)
        self.assertTrue(out['search_is_not_a_global_minimization_certificate'])
        self.assertEqual(out['starts_requested'],66)
        self.assertIn(out['status'],{
            'EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS',
            'NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE'})
        self.assertGreater(out['successful_field_evaluations'],40)

    def test_exact_deeper_witness_can_exist_for_tachyonic_charged_singlet(self):
        # Artificial nonphysical potential for NEGATIVE-WITNESS unit test.
        s=dict(self.state)
        s['mchi']=-1.e6
        cache=scalar_cache(s)
        ew=electroweak_check(self.point,cache,strict=False)
        x=np.array((np.cos(self.point['beta']),0.,
                    np.sin(self.point['beta']),0.,3.,0.))
        val,_=gauge_value_and_gradient(x,cache)
        self.assertLess(val-ew['vacuum_V_over_v4'],-WITNESS_MARGIN)

    def test_electroweak_spectrum_wrong_singlet_mass_is_rejected(self):
        s=dict(self.state)
        s['mchi']+=1.e5
        with self.assertRaisesRegex(ValueError,'physical scalar Hessian'):
            electroweak_check(self.point,scalar_cache(s),strict=True)

    def test_dimensional_mu3_is_retained(self):
        c=self.cache
        r=np.zeros(10)
        r[[0,6,8]]=[150.,170.,120.]
        orig=potential_gradient_hessian(r,c)[0]
        modified=dict(self.state)
        modified['muZee']=0.
        zero=potential_gradient_hessian(r,scalar_cache(modified))[0]
        self.assertGreater(abs(orig-zero)/VEV**4,1e-6)

    def test_charged_and_neutral_classifiers_explicit_field_vector(self):
        p=self.point
        orig=np.array([VEV*np.cos(p['beta']),0.,VEV*np.sin(p['beta']),0,0,0])
        self.assertEqual(orig[1],0.)
        self.assertEqual(orig[4],0.)
        displaced=orig.copy();displaced[4]=.2*VEV
        self.assertGreater(abs(displaced[4]),1e-4)

    def test_cohort_summary_does_not_claim_global_or_allowed(self):
        rows=[]
        for variant in TARGET_VARIANTS:
            for i in range(2):
                rows.append({'variant':variant,'C4_running_theory_pass':True,
                             'C5_deeper_witness':i==1})
        out=cohort_summary(rows)
        self.assertEqual(out[TARGET_VARIANTS[0]]['tested'],2)
        self.assertEqual(
            out[TARGET_VARIANTS[0]]['explicit_deeper_tree_potential_witness'],1)
        self.assertEqual(
            out[TARGET_VARIANTS[0]]
            ['C4_pass_and_no_C5_deeper_witness_found_NOT_allowed'],1)

if __name__=='__main__':
    unittest.main()
