"""D2 general Zee neutrino-exact continuous LFV optimization checks.

One *mathematical* test verifies exact 4-complex Yukawa homogeneous
directions, one physical test reproduces D1 amplitude/3-lepton scoring
at an existing B2-compatible root, and negative controls reject bad
provenance or accidental 'allowed' labels.
"""
from pathlib import Path
import sys
import math
import json
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,scalar_kappa,reconstruct_neutrino
)
from gateB2_zee_neutrino_family_scan import (
    subset_lfv,linear_neutrino_operator
)
from zee_gateC1_joined_uv_pilot import digest
from zee_gateD1_joint_300_neutrino_lfv_inventory import candidate_flavor,STATUS as D1_STATUS
from zee_gateD2_neutrino_exact_partial_LFV_optimization import (
    STATUS,PERT,verify_d1,neutrino_family,make_yukawas,
    optimize_kernels_cache,amplitude_subset,objective,
    final_solution,optimize_start
)

def point():
    return {'id':'D2_TEST_ONLY_NOT_ALLOWED','mH1':300.,'mH2':700.,
            'mh2':580.7,'ma':633.7,'alpha':1.398,'beta':1.394,
            'gamma':1.089}

def packed(mat):
    m=np.asarray(mat,complex)
    return {'real':m.real.tolist(),'imag':m.imag.tolist()}

def data():
    p=point()
    target,_=target_neutrino_matrix()
    f,_=antisymmetric_f_with_null_condition(target)
    k=scalar_kappa(p['mH1'],p['mH2'],p['gamma'])
    Y,rank,_=solve_lepton_yukawa(f,target,kappa=k)
    if rank!=5:raise AssertionError('Wrong neutrino rank')
    err=float(np.max(abs(reconstruct_neutrino(f,Y,kappa=k)-target)))
    rates,ratios=subset_lfv(p,f,Y)
    sol={
        'candidate_id':p['id'],'mH1':p['mH1'],
        'mH2':p['mH2'],'gamma':p['gamma'],
        'f':packed(f),'Y':packed(Y),
        'neutrino_matrix_closure_eV':err,
        'partial_LFV_rates_NOT_FULL':rates,
        'partial_LFV_ratios_NOT_EXCLUSION':ratios,
        'partial_LFV_score_NOT_EXCLUSION':max(ratios.values()),
        'max_abs_f':float(np.max(abs(f))),
        'max_abs_Y':float(np.max(abs(Y))),
        'status':'NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED',
    }
    return p,sol,f,Y

class TestD2NeutrinoExactLFV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        optimize_kernels_cache()

    def test_4_complex_homogeneous_neutrino_Yukawa_directions(self):
        p,sol,f,Y=data()
        target,_=target_neutrino_matrix()
        k=scalar_kappa(p['mH1'],p['mH2'],p['gamma'])
        op=linear_neutrino_operator(f,k)
        _,sing,vh=np.linalg.svd(op,full_matrices=True)
        null=vh[5:,:].conj().T
        self.assertEqual(null.shape,(9,4))
        self.assertLess(np.max(abs(op@null)),1e-9)
        np.testing.assert_allclose(null.conj().T@null,np.eye(4),atol=1e-10)

    def test_seed_roundtrips_yukawa_null_family(self):
        p,sol,f,Y=data()
        family=neutrino_family(p,sol)
        gotf,gotY=make_yukawas(family,family['starting_coords'])
        np.testing.assert_allclose(gotf,f,rtol=1e-12,atol=1e-13)
        np.testing.assert_allclose(gotY,Y,rtol=1e-10,atol=1e-11)

    def test_neutrino_matrix_stays_closed_for_random_9dim_variations(self):
        p,sol,_,_=data()
        family=neutrino_family(p,sol)
        rng=np.random.default_rng(20261019)
        target,_=target_neutrino_matrix()
        for _ in range(40):
            x=family['starting_coords'].copy()
            x[0]+=rng.uniform(-2,2)
            x[1:]+=rng.normal(size=8)*.5
            f,Y=make_yukawas(family,x)
            k=scalar_kappa(p['mH1'],p['mH2'],p['gamma'])
            err=float(np.max(abs(reconstruct_neutrino(f,Y,kappa=k)-target)))
            self.assertLess(err,1e-9)

    def test_initial_amplitude_score_matches_existing_D1(self):
        p,sol,f,Y=data()
        reference=candidate_flavor(p,sol,1)
        score=max(amplitude_subset(p,f,Y).values())
        self.assertAlmostEqual(score,
            reference['joint_incomplete_LFV_score_NOT_EXCLUSION'],
            delta=2e-8*max(1,score))
        family=neutrino_family(p,sol)
        self.assertAlmostEqual(
            objective(family,family['starting_coords']),
            math.log10(score),delta=2e-8)

    def test_final_solution_rechecked_through_unmodified_B2_and_D1(self):
        p,sol,f,Y=data()
        final,check,channels=final_solution(p,sol,f,Y)
        self.assertLess(final['neutrino_matrix_closure_eV'],1e-9)
        self.assertEqual(check['experimental_LFV_allowed_or_excluded'],'UNKNOWN')
        self.assertEqual(len(channels),8)
        self.assertEqual(final['status'],
                         'NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED')

    def test_extreme_f_rescaling_penalized_not_recorded(self):
        p,sol,_,_=data()
        family=neutrino_family(p,sol)
        x=family['starting_coords'].copy()
        x[0]=25.
        self.assertGreater(objective(family,x),1000.)

    def test_wrong_shape_neutrino_coordinates_rejected(self):
        p,sol,_,_=data()
        family=neutrino_family(p,sol)
        with self.assertRaisesRegex(ValueError,'Nine real optimizer'):
            make_yukawas(family,np.zeros(7))

    def test_local_optimizer_keeps_start_as_fallback_and_no_allowed_label(self):
        p,sol,_,_=data()
        reference=candidate_flavor(p,sol,1)
        result=optimize_start(p,sol,reference,max_evals=90)
        self.assertLessEqual(
            result['best_score'],
            reference['joint_incomplete_LFV_score_NOT_EXCLUSION']*(1+1e-8))
        self.assertIn(result['source'],('saved_B2_start','Powell_optimized'))
        self.assertEqual(
            result['solution']['status'],
            'NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED')
        self.assertLess(result['solution']['neutrino_matrix_closure_eV'],1e-9)

    def test_optimizer_requires_exact_D1_original_score(self):
        p,sol,_,_=data()
        fake=candidate_flavor(p,sol,1)
        fake['joint_incomplete_LFV_score_NOT_EXCLUSION']*=2.
        with self.assertRaisesRegex(ValueError,'does not reproduce'):
            optimize_start(p,sol,fake,max_evals=90)

    def test_wrong_neutrino_Y_seed_cannot_form_null_family(self):
        p,sol,_,_=data()
        sol['Y']['real'][0][0]+=1.
        with self.assertRaisesRegex(ValueError,'not represented'):
            neutrino_family(p,sol)

    def test_fermion_BZ_kernel_memoization_preserves_loop_value(self):
        import zee_barr_zee_fermion_dipoles as bz
        from zee_barr_zee_kernels import f as raw_f,g as raw_g
        for z in (.031,.33,1.31):
            self.assertAlmostEqual(bz.scalar_f(z)[0],raw_f(z)[0],delta=1e-12)
            self.assertAlmostEqual(bz.pseudoscalar_g(z)[0],raw_g(z)[0],
                                   delta=1e-12)
        self.assertTrue(hasattr(bz.scalar_f,'cache_info'))

    def test_D1_source_provenance_150_requires_exact_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            inputs={k:root/(k+'.txt') for k in ('B4','B2','C2','C3','C4','C5')}
            for k,v in inputs.items():v.write_text('fixture-'+k)
            original=root/'D1.json'
            rows=[{'candidate_id':f'S{i}','solution_rank_original_B2':j}
                  for i in range(30) for j in range(1,6)]
            original.write_text(json.dumps({
                'status':D1_STATUS,
                'input_sha256':{k:digest(v) for k,v in inputs.items()},
                'B2_saved_solution_count_per_candidate':{
                    f'S{i}':5 for i in range(30)},
                'cohort':{'independent_complex_neutrino_solutions':150},
                'all_available_incomplete_LFV_details':rows
            }))
            result,idx=verify_d1(original,*inputs.values())
            self.assertEqual(len(idx),150)
            inputs['B2'].write_text('changed original B2')
            with self.assertRaisesRegex(ValueError,'SHA mismatch'):
                verify_d1(original,*inputs.values())

if __name__=='__main__':
    unittest.main()
