"""C3 independent mathematical and integration regression tests.

Proof obligations:
 1. arbitrary complex Zee quartic >= derived x,y,s lower bound,
 2. PSD/copositivity sufficient certification never asserts BFB for
    a deliberately negative physical gauge-orbit witness,
 3. a concrete negative orbit disproves BFB,
 4. inconclusive is never silently renamed stable,
 5. end-to-end snapshot/path machinery preserves all missing-physics flags.
"""
from pathlib import Path
from types import SimpleNamespace
import sys
import math
import json
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_section8_Q4_independent_scalar_hessian_gate import (
    PHYSICAL_QUARTICS,synthetic_quartics,tensor_for_quartics,potential
)
from zee_section8_Q4_large_integrated_one_loop_gate import NAMES,MATRIX_NAMES
from zee_gateC3_running_complex_bfb import (
    TARGET_VARIANTS,BFB_VERDICTS,quartic_lower_bound_matrix,
    copositive_3x3,orbit_design,quartic_orbit_values,quartic_bfb,
    path_with_bfb,verify_c2,summarise,
)
from zee_gateC1_joined_uv_pilot import scalar_lagrangian,build_model_state
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,scalar_kappa,reconstruct_neutrino
)

def sample_point():
    return {
        'id':'B4_TEST_ONLY','beta':1.394,'alpha':1.398,'gamma':1.089,
        'mH1':300.,'mH2':700.,'mh2':580.7,'ma':633.7,
        'm12sq':57700.,'lc':4.473,
        'k1':1.082,'k2':.00398,'k12':-.001266,
    }

def solution(point):
    mass,_=target_neutrino_matrix()
    f,_=antisymmetric_f_with_null_condition(mass)
    k=scalar_kappa(point['mH1'],point['mH2'],point['gamma'])
    Y,_,_=solve_lepton_yukawa(f,mass,kappa=k)
    err=float(np.max(abs(reconstruct_neutrino(f,Y,kappa=k)-mass)))
    def pack(m):
        return {'real':np.asarray(m).real.tolist(),
                'imag':np.asarray(m).imag.tolist()}
    return {
        'candidate_id':point['id'],'f':pack(f),'Y':pack(Y),
        'neutrino_matrix_closure_eV':err,
        'partial_LFV_score_NOT_EXCLUSION':1e-7,
        'status':'NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED',
    }

def weak_positive():
    q={k:0. for k in PHYSICAL_QUARTICS}
    q.update(l1=.4,l2=.6,lh=.3,l3=.15,l4=.1,l8=.2,l9=.2)
    return q

def mock_zero_beta():
    f={}
    for name in NAMES:
        value=np.zeros((3,3),complex) if name in MATRIX_NAMES else 0.
        f['beta_'+name]=(lambda v=value: lambda nLoop:v)()
    return SimpleNamespace(**f)

class TestGateC3RunningComplexBFB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orbits=orbit_design(2048)

    def test_orbit_is_exact_physical_invariant_domain(self):
        o=self.orbits
        self.assertEqual(o.shape[1],5)
        np.testing.assert_allclose(o[:,:3].sum(axis=1),1.,atol=1e-13)
        self.assertGreaterEqual(np.min(o[:,:3]),0.)
        self.assertLessEqual(np.max(o[:,3]**2+o[:,4]**2-o[:,0]*o[:,1]),1e-12)

    def test_orbit_contains_pure_single_field_rays(self):
        o=self.orbits
        for i in range(3):
            w=np.zeros(5);w[i]=1.
            self.assertTrue(np.any(np.max(abs(o-w),axis=1)<1e-14))

    def test_orbit_value_matches_original_ten_real_scalar_potential(self):
        q=synthetic_quartics(20261020)
        o=self.orbits[17]
        x,y,s,zr,zi=o
        # Higgs doublets chosen so phi1†phi2 == zr+i zi, chi real
        h1=np.array([math.sqrt(x),0.],complex)
        h2=np.array([(zr+1j*zi)/math.sqrt(x),
            math.sqrt(max(0.,y-(zr*zr+zi*zi)/x))],complex)
        real=np.zeros(10,float)
        for i in range(2):
            real[2*i:2*i+2]=[math.sqrt(2)*h1[i].real,math.sqrt(2)*h1[i].imag]
            real[4+2*i:6+2*i]=[math.sqrt(2)*h2[i].real,math.sqrt(2)*h2[i].imag]
        real[8]=math.sqrt(2*s)
        from zee_section8_Q4_independent_scalar_hessian_gate import invariants
        np.testing.assert_allclose(invariants(real),o,atol=1e-13)
        self.assertAlmostEqual(
            potential(real,tensor_for_quartics(q)),
            quartic_orbit_values(q,o.reshape(1,5))[0],delta=1e-12)

    def test_rigorous_lower_bound_random_general_complex_quartics(self):
        for seed in (20261019,20261020,20261021,20261022):
            q=synthetic_quartics(seed)
            C=quartic_lower_bound_matrix(q)
            value=quartic_orbit_values(q,self.orbits)
            xy=self.orbits[:,:3]
            lower=np.einsum('ni,ij,nj->n',xy,C,xy,optimize=True)
            self.assertGreaterEqual(float(np.min(value-lower)),-2e-12)

    def test_singlet_only_lower_bound_is_exact(self):
        q=weak_positive()
        M=quartic_lower_bound_matrix(q)
        self.assertAlmostEqual(M[2,2],q['lh'])
        self.assertAlmostEqual(M[0,0],.5*q['l1'])
        self.assertAlmostEqual(M[1,1],.5*q['l2'])

    def test_strongly_positive_sufficient_certificate(self):
        q=weak_positive()
        yes,details=copositive_3x3(quartic_lower_bound_matrix(q))
        self.assertTrue(yes,details)
        x=quartic_bfb(q,self.orbits)
        self.assertEqual(x['verdict'],'BFB_SUFFICIENT_CERTIFIED')
        self.assertGreater(x['sample_min_v4_normalized'],0.)

    def test_positive_semidefinite_copositive_matrix(self):
        M=np.array([[1.,-.4,0.],[-.4,1.,0.],[0.,0.,1.]])
        yes,details=copositive_3x3(M)
        self.assertTrue(yes,details)

    def test_indefinite_but_copositive_matrix(self):
        M=np.array([[1.,2.,0.],[2.,1.,0.],[0.,0.,1.]])
        yes,details=copositive_3x3(M)
        self.assertTrue(yes,details)

    def test_non_copositive_negative_mixed_ray(self):
        M=np.array([[1.,-2.,0.],[-2.,1.,0.],[0.,0.,1.]])
        yes,details=copositive_3x3(M)
        self.assertFalse(yes)

    def test_strictly_negative_lambda1_is_explicit_witness(self):
        q=weak_positive();q['l1']=-.5
        d=quartic_bfb(q,self.orbits)
        self.assertEqual(d['verdict'],'BFB_NEGATIVE_WITNESS')
        self.assertLess(d['sample_min_v4_normalized'],0.)

    def test_negative_doublet_mixed_quartic_is_explicit_witness(self):
        q=weak_positive();q['l3']=-5.
        d=quartic_bfb(q,self.orbits)
        self.assertEqual(d['verdict'],'BFB_NEGATIVE_WITNESS')

    def test_inconclusive_is_not_claimed_certified(self):
        # Lower-bound AM-GM is intentionally conservative for sizeable
        # complex l6, even when coarse orbit sampling finds no witness.
        q=weak_positive();q['l6']=.3j
        d=quartic_bfb(q,self.orbits)
        if d['verdict']=='BFB_INCONCLUSIVE':
            self.assertFalse(d['copositivity_lower_bound'])
        self.assertIn(d['verdict'],BFB_VERDICTS)

    def test_mock_rg_path_keeps_exact_quartic_under_zero_beta(self):
        state={k:(np.zeros((3,3),complex) if k in MATRIX_NAMES
                  else 0.) for k in NAMES}
        state.update(weak_positive())
        state.update(gp=.35,g2=.65,g3=1.1)
        out=path_with_bfb(mock_zero_beta(),state,
             mu0=700.,upper=1e4,steps=8,orbits=self.orbits)
        self.assertEqual(out['status'],'COMPLETE_TO_TARGET')
        self.assertEqual(out['num_certified_steps'],9)
        self.assertTrue(out['certified_sufficient_at_all_steps'])
        self.assertEqual(out['num_negative_witness_steps'],0)

    def test_mock_rg_path_fails_on_explicit_unstable_ray(self):
        state={k:(np.zeros((3,3),complex) if k in MATRIX_NAMES
                  else 0.) for k in NAMES}
        state.update(weak_positive())
        state.update(gp=.35,g2=.65,g3=1.1)
        state['l1']=-.5
        out=path_with_bfb(mock_zero_beta(),state,
             mu0=700.,upper=1e4,steps=8,orbits=self.orbits)
        self.assertEqual(out['status'],'NEGATIVE_QUARTIC_WITNESS')
        self.assertFalse(out['no_negative_witness_at_sampled_steps'])
        self.assertAlmostEqual(out['first_negative_witness_mu_GeV'],700.)

    def test_c2_paired_cohort_report_requires_identical_sha(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            b4=root/'b4.csv';b4.write_text('b4fixture')
            b2=root/'b2.json';b2.write_text('{}')
            source=root/'RGEs.py';source.write_text('same rge')
            from zee_gateC1_joined_uv_pilot import digest
            rows=[{'candidate_id':f'B4_{i:05d}','variant':v}
                  for i in range(30)
                  for v in ('baseline','cap_lh_1','cap_lh_0p4',
                            'target_l1_1','target_l1_0p5',
                            'both_lh1_l1_1','both_lh0p4_l1_1',
                            'both_lh0p4_l1_0p5')]
            report=root/'c2.json'
            report.write_text(json.dumps({
                'status':'GATE_C2_PAIRED_ZEE_SCALAR_RESCUE_ONE_LOOP_DIAGNOSTIC_NOT_ALLOWED',
                'tested_interventions':240,'rows':rows,
                'provenance':{'B4':digest(b4),'B2':digest(b2),
                              'RGE_source':digest(source)}
            }))
            good=verify_c2(report,b4,b2,source)
            self.assertEqual(len(good),240)
            source.write_text('changed RGE')
            with self.assertRaisesRegex(ValueError,'does not match'):
                verify_c2(report,b4,b2,source)

    def test_summary_is_nonphysical_and_tracks_three_categories(self):
        rows=[]
        for i in range(2):
            for variant in TARGET_VARIANTS:
                rows.append({
                    'candidate_id':f'{i}','variant':variant,
                    'C2_heuristic_reached_10TeV':True,
                    'certified_quartic_BFB_along_sampled_path':i==0,
                    'any_explicit_negative_witness':False,
                    'no_witness_but_uncertified':i==1
                })
        s=summarise(rows)
        self.assertIsNone(s['full_physical_Zee_benchmarks_allowed'])
        self.assertTrue(s['no_negative_witness_is_not_a_stability_proof'])
        for key in TARGET_VARIANTS:
            self.assertEqual(s['variants'][key]
                             ['certified_quartic_BFB_along_all_sampled_steps'],1)
            self.assertEqual(s['variants'][key]
                             ['no_explicit_negative_witness_but_not_certified'],1)

if __name__=='__main__':
    unittest.main()
