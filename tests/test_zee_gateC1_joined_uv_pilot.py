"""Gate C1 end-to-end boundary conditions and numerical pilot controls.

Focus is PHYSICS PROVENANCE and input normalization, not another list
of isolated beta coefficient tests. Fake-RGE fixture tests only the
RK4 orchestration; actual RGEs.py is used in the AF run.
"""
from pathlib import Path
import sys
import math
import unittest
import tempfile
import json
from types import SimpleNamespace
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

from gate6_benchmark import benchmark
from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,scalar_kappa,ML,
)
from zee_gateC1_joined_uv_pilot import (
    VEV,NAMES,MATRIX_KEYS,QUARK_BOUNDARY,
    scalar_lagrangian,convert_higgs_basis_Y,illustrative_quarks,
    build_model_state,diagnostics,numerical_control,
    vector_distance,run_flow,public_row,verify_rge_validation,numerical_control,
    limiting_couplings,locate_boundary,
)

def sample_point():
    return {
        'id':'TEST_ONLY_NOT_ALLOWED',
        'beta':1.394,'alpha':1.398,'gamma':1.089,
        'mH1':300.,'mH2':700.,'mh2':580.7,'ma':633.7,
        'm12sq':57700.,
        'lc':4.473,'k1':1.082,'k2':.00398,'k12':-.001266,
    }

def packed(matrix):
    m=np.asarray(matrix,complex)
    return {'real':m.real.tolist(),'imag':m.imag.tolist()}

def test_solution(point):
    target,_=target_neutrino_matrix()
    f,_=antisymmetric_f_with_null_condition(target)
    kap=scalar_kappa(point['mH1'],point['mH2'],point['gamma'])
    Y,rank,_=solve_lepton_yukawa(f,target,kappa=kap)
    if rank!=5:raise AssertionError('Unexpected neutrino rank')
    from gateA1b_hierarchical_no_seed import reconstruct_neutrino
    error=float(np.max(abs(reconstruct_neutrino(f,Y,kappa=kap)-target)))
    return {'candidate_id':point['id'],
            'f':packed(f),'Y':packed(Y),
            'neutrino_matrix_closure_eV':error,
            'partial_LFV_score_NOT_EXCLUSION':1.e-7,
            'status':'NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED'}

def zero_mod():
    funcs={}
    for k in NAMES:
        v=np.zeros((3,3),complex) if k in MATRIX_KEYS else 0.
        def make(value):
            return lambda nLoop: value
        funcs['beta_'+k]=make(v)
    return SimpleNamespace(**funcs)

class TestGateC1JoinedUV(unittest.TestCase):
    def test_reproduced_restricted_2021_scalar_potential(self):
        p=sample_point()
        vals,meta=scalar_lagrangian(p)
        for key in ('l1','l2','l3','l4','l5','lh','l8','l9','l10',
                    'm1','m2','m12','mchi','muZee'):
            self.assertTrue(np.isfinite(abs(vals[key])))
        self.assertEqual(vals['l6'],0.)
        self.assertEqual(vals['l7'],0.)
        self.assertEqual(vals['l10'],-p['k12'])
        self.assertEqual(vals['lh'],p['lc'])
        self.assertTrue(meta['scalar_mass_closure']=='PASS')
        self.assertTrue(meta['quartic_BFB_sufficient_at_matching'])
        self.assertTrue(meta['tree_unitarity_at_matching'])

    def test_electroweak_tadpoles_stationary_at_v1_v2(self):
        p=sample_point()
        a,_=scalar_lagrangian(p)
        beta=p['beta'];cb=math.cos(beta);sb=math.sin(beta)
        lam345=a['l3']+a['l4']+a['l5']
        v1,v2=VEV*cb,VEV*sb
        t1=a['m1']*v1-a['m12']*v2+.5*a['l1']*v1**3+.5*lam345*v1*v2**2
        t2=a['m2']*v2-a['m12']*v1+.5*a['l2']*v2**3+.5*lam345*v1**2*v2
        self.assertLess(abs(t1),1e-6)
        self.assertLess(abs(t2),1e-6)

    def test_higgs_basis_exact_lepton_rotation(self):
        p=sample_point()
        rng=np.random.default_rng(20261019)
        Y=.023*(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))
        ye1,ye2,meta=convert_higgs_basis_Y(Y,p['beta'])
        cb=math.cos(p['beta']);sb=math.sin(p['beta'])
        rho=-sb*ye1+cb*ye2
        sm=cb*ye1+sb*ye2
        np.testing.assert_allclose(
            rho.conj().T/np.sqrt(2.),Y,rtol=1e-13,atol=1e-14)
        np.testing.assert_allclose(
            sm*VEV/np.sqrt(2.),ML,rtol=1e-12,atol=1e-12)
        self.assertLess(meta['Y_from_rho_dagger_over_sqrt2_max_abs'],1e-12)

    def test_matrix_orientation_not_silently_transposed(self):
        Y=np.array([[0,.011+2j*.003,0],[.037,0,0],[0,0,.021]],complex)
        ye1,ye2,_=convert_higgs_basis_Y(Y,1.394)
        rho=-math.sin(1.394)*ye1+math.cos(1.394)*ye2
        np.testing.assert_allclose(rho,np.sqrt(2)*Y.conj().T,atol=1e-13)
        self.assertGreater(np.max(abs(rho-np.sqrt(2)*Y)),.01)

    def test_initial_general_zee_f_and_y_neutrino_algebra(self):
        p=sample_point()
        solution=test_solution(p)
        s,info=build_model_state(p,solution)
        self.assertEqual(set(s),set(NAMES))
        self.assertLess(info['neutrino_matrix_closure_eV'],1e-10)
        self.assertEqual(np.max(abs(s['f']+s['f'].T)),0.)
        self.assertTrue(info['k12_hard_Z2_breaking_nonzero'])
        self.assertFalse(info['modern_bsgamma_tested'])

    def test_typeii_quark_ansatz_explicit_CKM_identity(self):
        p=sample_point()
        q=illustrative_quarks(p['beta'])
        self.assertEqual(np.max(abs(q['Yd2'])),0.)
        self.assertEqual(np.max(abs(q['Yu1'])),0.)
        self.assertAlmostEqual(q['Yu2'][2,2],
                               QUARK_BOUNDARY['yu'][2]/math.sin(p['beta']))
        self.assertAlmostEqual(q['Yd1'][2,2],
                               QUARK_BOUNDARY['yd'][2]/math.cos(p['beta']))

    def test_reject_corrupted_neutrino_matrix(self):
        p=sample_point()
        solution=test_solution(p)
        solution['Y']['real'][0][0]+=1.
        with self.assertRaisesRegex(ValueError,'neutrino'):
            build_model_state(p,solution)

    def test_reject_solution_claimed_allowed(self):
        p=sample_point()
        solution=test_solution(p)
        solution['status']='FULL_ZEE_ALLOWED'
        with self.assertRaisesRegex(ValueError,'NOT_ALLOWED'):
            build_model_state(p,solution)

    def test_reject_inconsistent_saved_neutrino_diagnostic(self):
        p=sample_point()
        solution=test_solution(p)
        solution['neutrino_matrix_closure_eV']*=1.20
        with self.assertRaisesRegex(ValueError,'saved'):
            build_model_state(p,solution)

    def test_reject_inconsistent_stored_B4_quartic(self):
        p=sample_point()
        p['lambda1']=-52.
        with self.assertRaisesRegex(ValueError,'lambda1'):
            scalar_lagrangian(p)

    def test_numerical_control_is_not_vacuum_or_lfv_exclusion(self):
        p=sample_point()
        s,_=build_model_state(p,test_solution(p))
        self.assertIsNone(numerical_control(s))
        s['lh']=4*math.pi+.1
        self.assertEqual(numerical_control(s),'QUARTIC_ABS_GE_4PI')

    def test_diagonal_quark_initial_has_rge_induced_names(self):
        p=sample_point()
        s,_=build_model_state(p,test_solution(p))
        d=diagnostics(s)
        self.assertEqual(d['wrong_doublet_quark_norms']['Yd2'],0.)
        self.assertEqual(d['wrong_doublet_quark_norms']['Yu1'],0.)
        self.assertEqual(d['lambda6_abs'],0.)
        self.assertEqual(d['lambda7_abs'],0.)

    def test_zero_beta_orchestration_to_10tev(self):
        p=sample_point()
        s,_=build_model_state(p,test_solution(p))
        report=run_flow(zero_mod(),s,mu0=p['mH2'],
                        mu1=10000.,steps=8)
        self.assertEqual(report['status'],
                         'REACHED_END_SCALE_ONE_LOOP_DIAGNOSTIC_ONLY')
        self.assertEqual(len(report['history']),3)
        self.assertAlmostEqual(report['history'][-1]['mu_GeV'],10000.)
        self.assertLess(max(vector_distance(report['endpoint'],s).values()),1e-12)

    def test_boundary_is_not_a_physical_uv_cutoff(self):
        p=sample_point()
        s,_=build_model_state(p,test_solution(p))
        s['lh']=4*math.pi+1.
        report=run_flow(zero_mod(),s,mu0=700.,
                        mu1=10000.,steps=8)
        self.assertEqual(report['status'],'INITIAL_PERTURBATIVITY_CONTROL_FAILED')
        self.assertIsNone(report['endpoint'])

    def test_q4v13_exact_source_checksum_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'RGEs.py'
            source.write_text('# exact generated RGEs fixture')
            import hashlib
            digest=hashlib.sha256(source.read_bytes()).hexdigest()
            report=Path(directory)/'q4v13.json'
            report.write_text(json.dumps({
                'source_SHA256':digest,'compared_total':676,
                'compared_passed':676,
                'one_loop_full_Zee_source_consistency_passed':True,
                'failed_checks':[]}))
            got=verify_rge_validation(report,source)
            self.assertEqual(got['RGE_exact_source_sha256'],digest)

    def test_q4v13_changed_source_rejected_before_flow(self):
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'RGEs.py'
            source.write_text('# actual generator changed')
            report=Path(directory)/'q4v13.json'
            report.write_text(json.dumps({
                'source_SHA256':'old source','compared_total':676,
                'compared_passed':676,
                'one_loop_full_Zee_source_consistency_passed':True,
                'failed_checks':[]}))
            with self.assertRaisesRegex(ValueError,'676/676'):
                verify_rge_validation(report,source)

    def test_exact_quartic_riccati_boundary_is_bracketed(self):
        """Check boundary localization against d lambda/dt=20 lambda²/(16pi²)."""
        p=sample_point()
        state,_=build_model_state(p,test_solution(p))
        start_quartic=4.
        state['lh']=start_quartic
        fake=zero_mod()
        fake.beta_lh=lambda nLoop,lh:20*lh*lh
        analytical=700*math.exp(
            (16*math.pi**2/20)*(1/start_quartic-1/(4*math.pi))
        )
        coarse=run_flow(fake,state,mu0=700.,mu1=10000.,steps=24)
        refined=run_flow(fake,state,mu0=700.,mu1=10000.,steps=48)
        for result in (coarse,refined):
            self.assertEqual(result['status'],
                             'DIAGNOSTIC_BOUNDARY_REACHED_NOT_PHYSICAL_CUTOFF')
            self.assertEqual(result['reason'],'QUARTIC_ABS_GE_4PI')
            self.assertEqual(result['limiting_couplings'][0]['coupling'],'lh')
            bracket=result['boundary_bracket']
            self.assertIsNotNone(bracket)
            self.assertLess(bracket['relative_bracket_width'],1e-3)
            self.assertLess(bracket['last_accepted_mu_GeV'],
                            bracket['first_rejected_mu_GeV'])
            self.assertAlmostEqual(
                bracket['estimated_boundary_GeV']/analytical,1.,
                delta=.045)
        a=coarse['boundary_bracket']['estimated_boundary_GeV']
        b=refined['boundary_bracket']['estimated_boundary_GeV']
        self.assertLess(abs(a-b)/max(a,b),.025)

    def test_sole_numeric_gauge_negative_is_never_ignored(self):
        p=sample_point()
        state,_=build_model_state(p,test_solution(p))
        state['gp']=-.1
        self.assertEqual(numerical_control(state),'GAUGE_NEGATIVE')

    def test_ranked_coupling_diagnostic_identifies_largest_portal(self):
        state,_=build_model_state(sample_point(),test_solution(sample_point()))
        state['l10']=11.+0.4j
        top=limiting_couplings(state,1)[0]
        self.assertEqual(top['coupling'],'l10')
        self.assertEqual(top['sector'],'quartic')
        self.assertGreater(top['ratio'],.85)

    def test_public_output_is_not_physical_acceptance(self):
        p=sample_point()
        s,preflight=build_model_state(p,test_solution(p))
        flow=run_flow(zero_mod(),s,mu0=p['mH2'],
                      mu1=10000.,steps=8)
        out=public_row(p,1,preflight,flow,0.)
        self.assertEqual(out['physically_allowed'],'UNKNOWN')
        self.assertEqual(out['UV_vacuum_consistency'],'NOT_EVALUATED')
        self.assertEqual(out['full_LFV'],'NOT_EVALUATED')
        self.assertEqual(out['modern_BtoXsGamma'],'NOT_EVALUATED')
        self.assertEqual(out['HiggsTools'],'NOT_EVALUATED')

if __name__=='__main__':
    unittest.main()
