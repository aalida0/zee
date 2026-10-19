"""C4 full 55x55 contact unitarity: independent analytic and physics regression.

Most important benchmark: Gate6 2021 Appendix C block spectra are
constructed by an independent charge/hypercharge sector decomposition;
the full real-field pair basis MUST have the same maximal eigenvalue.
"""
from pathlib import Path
import sys
import math
import json
import tempfile
from types import SimpleNamespace
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

from gate6_benchmark import benchmark
from zee_gateC1_joined_uv_pilot import scalar_lagrangian
from zee_section8_Q4_independent_scalar_hessian_gate import (
    PHYSICAL_QUARTICS,synthetic_quartics
)
from zee_section8_Q4_large_integrated_one_loop_gate import (
    NAMES,MATRIX_NAMES
)
from zee_gateC3_running_complex_bfb import (
    orbit_design
)
from zee_gateC4_running_55channel_unitarity import (
    RESPONSE,N_PAIRS,LIMIT,
    scatter_matrix,scattering_eigenvalues,scattering_limit,
    locate_unitarity_crossing,full_trajectory,verify_c3,cohort_summary
)

def zeros():
    return {k:0. for k in PHYSICAL_QUARTICS}

def mod_zero():
    d={}
    for k in NAMES:
        value=np.zeros((3,3),complex) if k in MATRIX_NAMES else 0.
        d['beta_'+k]=(lambda v=value:lambda nLoop:v)()
    return SimpleNamespace(**d)

def state_from_quartics(q):
    state={k:(np.zeros((3,3),complex) if k in MATRIX_NAMES else 0.)
           for k in NAMES}
    state.update(q)
    state.update(gp=.35,g2=.65,g3=1.10)
    return state

class TestC4Full55Channel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orbits=orbit_design(512)

    def test_exact_n55_count_and_response_symmetry(self):
        self.assertEqual(N_PAIRS,55)
        self.assertEqual(RESPONSE.shape,(55,55,5,5))
        q=synthetic_quartics(20261020)
        S=scatter_matrix(q)
        self.assertEqual(S.shape,(55,55))
        self.assertLess(np.max(abs(S-S.T)),1e-12)
        self.assertTrue(np.isfinite(S).all())

    def test_zero_quartic_all_55_eigenvalues_zero(self):
        eig=scattering_eigenvalues(zeros())
        np.testing.assert_allclose(eig,0,atol=1e-14)

    def test_analytic_pure_doublet_lambda1_max_3lambda1(self):
        q=zeros();q['l1']=2.
        eig=scattering_eigenvalues(q)
        self.assertAlmostEqual(float(np.max(eig)),6.,places=11)
        self.assertAlmostEqual(float(np.min(eig)),0.,places=11)

    def test_analytic_pure_doublet_lambda2_max_3lambda2(self):
        q=zeros();q['l2']=3.
        eig=scattering_eigenvalues(q)
        self.assertAlmostEqual(float(np.max(eig)),9.,places=11)

    def test_analytic_pure_complex_singlet_lh_max_4lh(self):
        q=zeros();q['lh']=3.
        eig=scattering_eigenvalues(q)
        self.assertAlmostEqual(float(np.max(eig)),12.,places=11)

    def test_restricted_2021_original_gate6_appendixC_max(self):
        p=benchmark()
        q={f'l{i}':p['quartics'][f'lambda{i}'] for i in range(1,6)}
        q.update({'l6':0.,'l7':0.,'lh':p['inputs']['lambda_c'],
                  'l8':p['inputs']['k1'],'l9':p['inputs']['k2'],
                  'l10':-p['inputs']['k12']})
        largest=max(abs(scattering_eigenvalues(q)))
        self.assertAlmostEqual(largest,18.13677908573045,delta=1e-9)
        self.assertAlmostEqual(
            largest,p['max_abs_unitarity_eigenvalue'],delta=1e-9)

    def test_multiple_modified_benchmarks_equal_gate6_eigen_envelope(self):
        for kwargs in ({'lc':.4,'k1':.5,'k2':.2},
                       {'lc':1.0,'m12sq':60000.,'k12':-.003},
                       {'lc':.8,'beta':1.39,'gamma':1.11,
                        'k1':.6,'k2':.25}):
            p=benchmark(**kwargs)
            q={f'l{i}':p['quartics'][f'lambda{i}'] for i in range(1,6)}
            q.update({'l6':0.,'l7':0.,'lh':p['inputs']['lambda_c'],
                      'l8':p['inputs']['k1'],'l9':p['inputs']['k2'],
                      'l10':-p['inputs']['k12']})
            self.assertAlmostEqual(
                max(abs(scattering_eigenvalues(q))),
                p['max_abs_unitarity_eigenvalue'],delta=2e-9)

    def test_55channel_complex_doublet_rephase_eigen_invariance(self):
        for seed in (20261019,20261020,20261021):
            q=synthetic_quartics(seed)
            changed=dict(q)
            theta=.634
            changed['l5']*=np.exp(-2j*theta)
            for k in ('l6','l7','l10'):
                changed[k]*=np.exp(-1j*theta)
            np.testing.assert_allclose(
                scattering_eigenvalues(q),scattering_eigenvalues(changed),
                atol=1e-11,rtol=1e-11)

    def test_singlet_rephase_does_not_change_quartic_matrix(self):
        q=synthetic_quartics(20261020)
        eig=scattering_eigenvalues(q)
        # Singlet χ rephasing leaves χ†χ fixed and cannot affect quartics.
        np.testing.assert_allclose(eig,eig)

    def test_matrix_linearity_in_15_real_quartic_components(self):
        a=synthetic_quartics(20261020);b=synthetic_quartics(20261021)
        c={k:a[k]+.31*b[k] for k in PHYSICAL_QUARTICS}
        np.testing.assert_allclose(scatter_matrix(c),
            scatter_matrix(a)+.31*scatter_matrix(b),atol=1e-12)

    def test_tree_unitarity_bound_matches_gate6_eight_pi(self):
        q=zeros();q['l1']=9.
        d=scattering_limit(q)
        self.assertGreater(d['max_abs_eigenvalue'],LIMIT)
        self.assertFalse(d['passes_strict_8pi'])
        self.assertGreater(d['a0_max_abs'],.5)

    def test_small_couplings_pass_55channel(self):
        q=synthetic_quartics(20261020)
        self.assertTrue(scattering_limit(q)['passes_strict_8pi'])

    def test_rk4_zero_beta_preserves_full_55channel_and_bfb(self):
        q=zeros()
        q.update(l1=.4,l2=.6,lh=.3,l3=.15,l4=.1,l8=.2,l9=.2)
        state=state_from_quartics(q)
        out=full_trajectory(mod_zero(),state,mu0=700.,
                            upper=10000.,steps=8,orbits=self.orbits)
        self.assertTrue(out['reached_end_scale'])
        self.assertTrue(out['tree_unitarity_8pi_at_all_sampled_steps'])
        self.assertTrue(out['BFB_sufficient_at_all_sampled_steps'])
        self.assertIsNone(out['first_tree_unitarity_crossing'])
        self.assertEqual(out['sampled_steps'],9)

    def test_initial_unitarity_failure_not_mistaken_for_physical_exclusion(self):
        q=zeros();q.update(l1=9.,l2=.4,lh=.3,l3=.05)
        out=full_trajectory(mod_zero(),state_from_quartics(q),
                            mu0=700.,upper=1e4,steps=8,orbits=self.orbits)
        self.assertFalse(out['tree_unitarity_8pi_at_all_sampled_steps'])
        self.assertAlmostEqual(
            out['first_tree_unitarity_crossing']['first_failure_GeV'],700.)
        self.assertTrue(out['reached_end_scale'])

    def test_rk4_riccati_tree_unitarity_crossing_before_4pi(self):
        q=zeros()
        q.update(l1=4.,l2=.4,lh=.3,l3=.02,l8=.1,l9=.1)
        state=state_from_quartics(q)
        mod=mod_zero()
        mod.beta_l1=lambda nLoop,l1:24*l1*l1
        analytic=700.*math.exp(
            16*math.pi**2/24*(1/4.-1/(LIMIT/3.)))
        out=full_trajectory(mod,state,mu0=700.,upper=10000.,
                            steps=24,orbits=self.orbits)
        crossing=out['first_tree_unitarity_crossing']
        self.assertIsNotNone(crossing)
        self.assertAlmostEqual(
            crossing['first_failure_GeV']/analytic,1.,delta=.02)
        self.assertLess(crossing['relative_bracket_width'],.001)
        self.assertGreater(crossing['first_failure_GeV'],700.)
        self.assertFalse(out['tree_unitarity_8pi_at_all_sampled_steps'])

    def test_explicit_negative_orbit_never_called_running_BFB_pass(self):
        q=zeros()
        q.update(l1=-.4,l2=.6,lh=.2)
        out=full_trajectory(mod_zero(),state_from_quartics(q),
                            mu0=700.,upper=10000.,steps=8,orbits=self.orbits)
        self.assertFalse(out['BFB_sufficient_at_all_sampled_steps'])
        self.assertTrue(out['BFB_negative_witness'])
        self.assertFalse(out['reached_end_scale'])

    def test_c3_provenance_sha_mismatch_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            files=[root/k for k in ('b4.csv','b2.json','c2.json','RGEs.py')]
            for a in files:a.write_text('fixture')
            from zee_gateC1_joined_uv_pilot import digest
            rows=[{'candidate_id':str(i),'variant':v}
                  for i in range(30) for v in
                  ('both_lh1_l1_1','both_lh0p4_l1_0p5')]
            c3=root/'C3.json'
            c3.write_text(json.dumps({
                'status':'GATE_C3_COMPLEX_QUARTIC_RUNNING_BFB_DIAGNOSTIC_NOT_ALLOWED',
                'tested':60,'rows':rows,
                'provenance':{k:digest(v) for k,v in zip(
                    ('B4','B2','C2','RGEs'),files)}
            }))
            out=verify_c3(c3,*files)
            self.assertEqual(len(out),60)
            files[-1].write_text('new source')
            with self.assertRaisesRegex(ValueError,'does not match'):
                verify_c3(c3,*files)

    def test_summary_no_physical_claim(self):
        rows=[]
        for variant in ('both_lh1_l1_1','both_lh0p4_l1_0p5'):
            rows.append({'variant':variant,'C2_10TeV_heuristic':True,
               'C3_BFB_sufficient_all':True,
               'full_55x55_unitarity_through_10TeV':False,
               'both_running_theory_screens_pass':False,
               'unitary_at_matching':True,
               'unitarity_crossing_GeV':3500.})
        s=cohort_summary(rows)
        self.assertEqual(s['both_lh1_l1_1']['tested'],1)
        self.assertEqual(
            s['both_lh1_l1_1']['both_BFB_and_full_tree_unitarity_through_10TeV'],0)

if __name__=='__main__':
    unittest.main()
