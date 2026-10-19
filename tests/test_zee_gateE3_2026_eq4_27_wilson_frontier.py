"""Gate E3: modern 2026 Misiak Eq4 LO C7/C8 Zee two-state 27-point physics checks.

Test an actual published mu0=160GeV operator normalization and
controlled analytic comparison with E2's independent quadratic
SuperIso-v5 legacy response (NEVER combining the schemes).
"""
from pathlib import Path
import math
import json
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

from zee_gateC1_joined_uv_pilot import digest
from gateA1s_run_modern_2026_screen import (
    K7,K8,MODERN_SM,MU0_GEV,combine,parse_probe,linearized_2026
)
from zee_gateE2_flavor_cascade_mixing_frontier import (
    STATUS as E2_STATUS,SOURCE_STATUS as E1_STATUS,
    FLOOR_FACTORS,zee_z_vertex_strength_squared,
    optimum_under_Z_vertex_floor
)
from zee_gateE3_2026_eq4_27_wilson_frontier import (
    STATUS,verify_inputs,modern_affine_profile,
    evaluate_case,summarize
)

def single(m,d7,d8,t=5.6):
    return {
        'mass_GeV':m,'delta_C7_LO':d7,'delta_C8_LO':d8,
        'tanbeta':t,'matching_scale_GeV':160.,'running_mt_mu0_GeV':163.
    }

def fixture():
    g=1.12
    a,b,c=(3.65e-4,1.85e-5,1.3e-6)
    x=math.cos(g)**2
    original=a+b*x+c*x*x
    E1={
        'candidate_id':'B4_SYNTHETIC','mH1':250.,
        'mH2':720.,'tanbeta':5.6,'gamma':g,
        'pure_light_BR':a+b+c,'pure_heavy_BR':a,
        'B_to_Xs_gamma_legacy_Zee_BR':original,
        'SM_BR_legacy':3.38e-4,
        'NP_delta_BR_legacy':original-3.38e-4,
        'all_source_pinned_endpoints_consistent':True,
    }
    E2={
        'candidate_id':E1['candidate_id'],'mH1':E1['mH1'],
        'mH2':E1['mH2'],'original_gamma':g,
        'original_legacy_BR':original,
        'retained_Z_vertex_coupling_frontier':[
            optimum_under_Z_vertex_floor((a,b,c),g,q)
            for q in FLOOR_FACTORS]
    }
    light=single(250.,-.112,-.109)
    heavy=single(720.,-.045,-.05)
    return E1,E2,light,heavy

class TestGateE3WilsonModern2026(unittest.TestCase):
    def test_misiak_2026_Eq4_is_pinned_exactly(self):
        self.assertEqual((K7,K8,MU0_GEV),(-8.51,-2.16,160.))
        self.assertEqual(MODERN_SM['central_times_1e4'],3.54)
        x=linearized_2026(-.04,-.02)
        self.assertAlmostEqual(x['linearized_predicted_central_times_1e4'],
                               3.54+.3404+.0432,places=12)

    def test_exact_doublet_weights_at_endpoints(self):
        e1,e2,light,heavy=fixture()
        self.assertAlmostEqual(
            combine(light,heavy,0.)['LO_delta_C7_mu0_160'],
            light['delta_C7_LO'])
        self.assertAlmostEqual(
            combine(light,heavy,math.pi/2)['LO_delta_C8_mu0_160'],
            heavy['delta_C8_LO'])

    def test_E3_LO_original_matches_direct_C7_and_C8(self):
        row,e2,l,h=fixture()
        result=evaluate_case(row,e2,l,h)
        x=math.cos(row['gamma'])**2
        expect7=x*l['delta_C7_LO']+(1-x)*h['delta_C7_LO']
        expect8=x*l['delta_C8_LO']+(1-x)*h['delta_C8_LO']
        self.assertAlmostEqual(result['LO_delta_C7_Zee_mu0_160'],expect7)
        self.assertAlmostEqual(result['LO_delta_C8_Zee_mu0_160'],expect8)
        self.assertAlmostEqual(
            result['2026_Eq4_original_LO_linearized_BR_times_1e4'],
            3.54-8.51*expect7-2.16*expect8,places=13)

    def test_source_A1S_300_700_2026_eq4_benchmark(self):
        l=single(300.,-.116249118178,-.112989421480)
        h=single(700.,-.0436165310583,-.0489292812783)
        original=combine(l,h,1.089)
        self.assertAlmostEqual(
            original['LO_delta_C7_mu0_160'],
            -.0592117200769,delta=2e-12)
        self.assertAlmostEqual(
            original['linearized_predicted_central_times_1e4'],
            4.17928885635,delta=3e-10)

    def test_affine_Eq4_2026_not_quadratic_full_BR(self):
        r,e2,l,h=fixture()
        p=modern_affine_profile(l,h,r['gamma'])
        self.assertEqual(p[2],0.)
        for g in (0.,.24,.61,1.1,math.pi/2):
            x=math.cos(g)**2
            self.assertAlmostEqual(p[0]+p[1]*x,
              combine(l,h,g)['linearized_predicted_central_times_1e4'],
              delta=1e-12)

    def test_cross_scheme_comparison_does_not_sum_legacy_and_modern(self):
        r,e2,l,h=fixture()
        x=evaluate_case(r,e2,l,h)
        self.assertEqual(x['physical_Zee_model_allowed_or_excluded'],'UNKNOWN')
        self.assertFalse(x['full_NNLO_matching_or_BR_and_likelihood'])
        self.assertIn('legacy_E1_original_BR_NOT_COMMENSURATE',x)

    def test_modern_Z_vertex_at_no_loss_and_half_loss(self):
        r,e2,l,h=fixture()
        x=evaluate_case(r,e2,l,h)
        self.assertEqual(len(x['2026_Eq4_frontier']),5)
        self.assertAlmostEqual(
            x['2026_Eq4_frontier'][-1]['modern_minimum_Eq4_BR_times_1e4'],
            x['2026_Eq4_original_LO_linearized_BR_times_1e4'],
            delta=1e-12)
        self.assertLess(
            x['2026_Eq4_frontier'][2]['modern_minimum_Eq4_BR_times_1e4'],
            x['2026_Eq4_original_LO_linearized_BR_times_1e4'])

    def test_modern_frontier_has_maximal_vertex_at_pi_over_four(self):
        r,e2,l,h=fixture()
        x=evaluate_case(r,e2,l,h)
        for f,v in zip(FLOOR_FACTORS,x['2026_Eq4_frontier']):
            self.assertGreaterEqual(
                v['modern_optimal_sin_squared_2gamma'],
                f*zee_z_vertex_strength_squared(r['gamma'])-2e-12)

    def test_equal_mass_lo_coefficients_no_mix_dependence(self):
        r,e2,l,h=fixture()
        h=single(250.,l['delta_C7_LO'],l['delta_C8_LO'])
        p=modern_affine_profile(l,h,r['gamma'])
        self.assertAlmostEqual(p[1],0.)
        for g in (.01,.33,1.22):
            self.assertAlmostEqual(
                combine(l,h,g)['linearized_predicted_central_times_1e4'],
                p[0],delta=1e-12)

    def test_sign_of_mixing_optimization_changes_if_light_is_better(self):
        r,e2,l,h=fixture()
        # Flip the signed LO Wilson effects so light is favorable.
        h['delta_C7_LO'],l['delta_C7_LO']=-.12,-.045
        h['delta_C8_LO'],l['delta_C8_LO']=-.12,-.04
        p=modern_affine_profile(l,h,r['gamma'])
        self.assertLess(p[1],0.)
        opt=optimum_under_Z_vertex_floor(p,r['gamma'],0.)
        self.assertAlmostEqual(opt['optimal_gamma_rad'],0.,delta=1e-12)

    def test_modern_and_legacy_optimum_mixing_distinct_methods(self):
        r,e2,l,h=fixture()
        case=evaluate_case(r,e2,l,h)
        for z in case['2026_Eq4_frontier']:
            self.assertIn('same_2026_and_legacy_best_gamma',z)
            self.assertIn('legacy_optimized_BR_DONT_COMBINE_WITH_MODERN',z)

    def test_published_A1S_parse_requires_mu0_160(self):
        raw=(
            'STATUS A1S_SOURCE_PINNED_LO_MATCHING_NO_BR_OR_EXCLUSION\\n'
            'INPUT mH_GeV=700 tanbeta=5.6 mu0_GeV=160 '
            'running_mt_mu0_GeV=163\\n'
            'DELTA_C7_LO=-0.04\\nDELTA_C8_LO=-0.05\\n'
            'NO_THEORY_LIKELIHOOD_VALIDATED true\\n')
        got=parse_probe(raw.replace('\\\\n','\\n'),700.,5.6)
        self.assertAlmostEqual(got['delta_C7_LO'],-.04)
        with self.assertRaisesRegex(ValueError,'2026 Eq4 contract'):
            parse_probe(raw.replace('\\\\n','\\n').replace('mu0_GeV=160','mu0_GeV=161'),
                        700.,5.6)

    def test_27_cohort_summary_is_never_95CL_exclusion(self):
        r,e2,l,h=fixture()
        reports=[]
        for i in range(27):
            row=dict(r,candidate_id=f'B4_{i:07d}')
            out=evaluate_case(row,e2,l,h)
            reports.append(out)
        summary=summarize(reports)
        self.assertEqual(summary['spectra'],27)
        self.assertEqual(summary['two_charged_LO_matching_probes'],54)
        self.assertIsNone(summary['physical_Zee_allowed_or_excluded'])
        self.assertFalse(summary['2026_full_TypeII_670GeV_bound_reused_as_Zee_exclusion'])
        self.assertTrue(summary['no_legacy_modern_absolute_BR_addition'])

    def test_exact_E1_E2_source_has_provenance_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            oldfile=root/'E1.json'
            recentfile=root/'E2.json'
            vendor=root/'A1V_source_pinned_kernel'
            vendor.mkdir()
            a1v=vendor/'gateA1v_legacy_response.json'
            a1v.write_text('fixture')
            m=root/'A1M';u=root/'A1U';m.write_text('vendor');u.write_text('endpoint')
            r,e2,_,_=fixture()
            old=[dict(r,candidate_id=f'B4_{i:07d}') for i in range(27)]
            newer=[dict(e2,candidate_id=f'B4_{i:07d}') for i in range(27)]
            oldfile.write_text(json.dumps({
                'status':E1_STATUS,'tested':27,'rows':old,
                '2026_NNLO_full_two_state_validated':False,
                'cohort':{'all_endpoint_controls_pass':True},
                'provenance_sha256':{
                    'A1M':digest(m),'A1U':digest(u),'A1V_report':digest(a1v)}}))
            recentfile.write_text(json.dumps({
                'status':E2_STATUS,'tested':27,'rows':newer,
                'cohort':{'vendor_independent_gamma_crosschecks':108},
                'source_SHA256':{'E1':digest(oldfile),'A1M':digest(m),'A1U':digest(u)},
                'physical_Zee_allowed':None}))
            old_ok,new_ok,_,_=verify_inputs(oldfile,recentfile,m,u)
            self.assertEqual(len(old_ok),27)
            self.assertEqual(len(new_ok),27)
            u.write_text('changed')
            with self.assertRaisesRegex(ValueError,'provenance mismatch'):
                verify_inputs(oldfile,recentfile,m,u)

    def test_E1_E2_gamma_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            v=root/'A1V_source_pinned_kernel';v.mkdir()
            a1v=v/'gateA1v_legacy_response.json';a1v.write_text('fixture')
            m=root/'A1M';u=root/'A1U';m.write_text('vendor');u.write_text('endpoint')
            a,b,_,_=fixture()
            old=[dict(a,candidate_id=str(i)) for i in range(27)]
            newer=[dict(b,candidate_id=str(i)) for i in range(27)]
            newer[0]['original_gamma']+=.02
            oldfile=root/'E1.json';newfile=root/'E2.json'
            oldfile.write_text(json.dumps({
                'status':E1_STATUS,'tested':27,'rows':old,
                '2026_NNLO_full_two_state_validated':False,
                'cohort':{'all_endpoint_controls_pass':True},
                'provenance_sha256':{
                    'A1M':digest(m),'A1U':digest(u),'A1V_report':digest(a1v)}}))
            newfile.write_text(json.dumps({
                'status':E2_STATUS,'tested':27,'rows':newer,
                'cohort':{'vendor_independent_gamma_crosschecks':108},
                'source_SHA256':{'E1':digest(oldfile),'A1M':digest(m),'A1U':digest(u)},
                'physical_Zee_allowed':None}))
            with self.assertRaisesRegex(ValueError,'identity mismatch'):
                verify_inputs(oldfile,newfile,m,u)

if __name__=='__main__':
    unittest.main()
