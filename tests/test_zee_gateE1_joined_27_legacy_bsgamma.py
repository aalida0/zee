"""E1 27-spectrum complete two-charged legacy B->Xs gamma report tests.

Controls include exact D5 ancestry, 27 unique spectra and full charged
mixing, A1V Wilson-response quadratic algebra, both pure-mass endpoints,
equal-mass mixing closure, and explicit NO-exclusion semantics.
"""
from pathlib import Path
import csv
import json
import math
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

from zee_gateC1_joined_uv_pilot import digest
from zee_gateD5_h125_direct_LFV_27 import STATUS as D5_STATUS
from zee_gateE1_joined_27_legacy_bsgamma import (
    STATUS,HFLAV_EXP_ERROR_REFERENCE,HFLAV_EXP_REFERENCE,
    ENDPOINT_ABS_TOL,validate_provenance,build_grid,
    compare_legacy_result,endpoint_controls,aggregate,
)

def initial():
    return {'candidate_id':'B4_0000648','mH1':208.8,
            'mH2':681.9,'gamma':1.12,'tanbeta':5.65}

def result(seed=None,*,br=.00039311954,sm=.00033824577):
    if seed is None:seed=initial()
    linear=br-sm-3e-7
    return {
        'input':{k:seed[k] for k in ('mH1','mH2','gamma','tanbeta')},
        'SM_BR':sm,'full_Zee_BR':br,'linear_delta_BR':linear,
        'quadratic_delta_BR':3e-7,
        'classification':'LEGACY_FLAVOUR_OBSERVABLE_ONLY_NO_EXCLUSION'
    }

class TestGateE1Legacy27Bsgamma(unittest.TestCase):
    def test_model_delta_and_linear_quadratic_closure(self):
        s=initial()
        ret=compare_legacy_result(s,result(s))
        self.assertAlmostEqual(
            ret['NP_delta_BR_legacy'],
            ret['NP_linear_BR_term_legacy']+ret['NP_quadratic_BR_term_legacy'])
        self.assertTrue(ret['theory_and_exp_likelihood_NOT_COMPUTED'])

    def test_legacy_reference_HFLAV_error_not_used_as_95CL(self):
        row=compare_legacy_result(initial(),result())
        self.assertAlmostEqual(
            row['legacy_difference_over_HFLAV_experimental_error_ONLY_NOT_PULL'],
            (row['B_to_Xs_gamma_legacy_Zee_BR']-HFLAV_EXP_REFERENCE)/
            HFLAV_EXP_ERROR_REFERENCE)
        self.assertTrue(row['modern_2026_SM_prediction_NOT_applied_to_legacy_rate'])

    def test_incorrect_mass_or_mixing_fails_closed(self):
        wrong=result()
        wrong['input']['mH1']+=30.
        with self.assertRaisesRegex(ValueError,'grid order'):
            compare_legacy_result(initial(),wrong)

    def test_wrong_linear_or_quadratic_content_fails_closed(self):
        wrong=result()
        wrong['quadratic_delta_BR']*=3.
        with self.assertRaisesRegex(ValueError,'not closed'):
            compare_legacy_result(initial(),wrong)

    def test_a1v_wrong_physics_classification_rejected(self):
        wrong=result()
        wrong['classification']='ALLOWED'
        with self.assertRaisesRegex(ValueError,'unexpected classification'):
            compare_legacy_result(initial(),wrong)

    def test_27_spectrum_grid_and_quark_tan_beta(self):
        with tempfile.TemporaryDirectory() as d:
            pts={f'B4_{i:07d}':{
                'mH1':250.+i,'mH2':700.+i,
                'gamma':.99,'beta':math.atan(5.)
                } for i in range(27)}
            names=set(pts)
            file=Path(d)/'grid.csv'
            rows=build_grid(pts,names,file)
            self.assertEqual(len(rows),27)
            for x in rows:
                self.assertAlmostEqual(x['tanbeta'],5.)
                self.assertAlmostEqual(
                    x['doublet_fraction_H1']+x['doublet_fraction_H2'],1.)
            with file.open(newline='') as f:
                parsed=list(csv.DictReader(f))
            self.assertEqual(len(parsed),27)
            self.assertEqual(list(parsed[0]),['mH1','mH2','gamma','tanbeta'])

    def test_mass_order_and_onshell_h1z_required(self):
        with tempfile.TemporaryDirectory() as d:
            p={'A':{'mH1':550.,'mH2':600.,
                    'gamma':.8,'beta':1.3}}
            with self.assertRaisesRegex(ValueError,'cascade closed'):
                build_grid(p,['A'],Path(d)/'bad.csv')

    def test_nonphysical_mixing_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p={'A':{'mH1':250.,'mH2':700.,
                    'gamma':math.pi,'beta':1.3}}
            with self.assertRaisesRegex(ValueError,'Invalid charged'):
                build_grid(p,['A'],Path(d)/'bad.csv')

    def test_A1V_endpoint_equal_mass_mixing_independence(self):
        original=initial()
        def mock_eval(exe,m1,m2,g,t):
            x=dict(original,mH1=m1,mH2=m2,gamma=g,tanbeta=t)
            response=result(x,br=.00039 if m1==m2 else
                            (.00037 if abs(g)<1e-6 else .00042))
            return response,'synthetic vendor'
        with patch('zee_gateE1_joined_27_legacy_bsgamma.superiso_evaluate',
                   side_effect=mock_eval):
            a=endpoint_controls(Path('/not/executed'),original,result())
        self.assertTrue(a['all_source_pinned_endpoints_consistent'])
        self.assertEqual(a['degenerate_mass_gamma_dependence_residual'],0.)

    def test_bad_A1V_degenerate_endpoint_detected(self):
        original=initial()
        def mock_eval(exe,m1,m2,g,t):
            x=dict(original,mH1=m1,mH2=m2,gamma=g,tanbeta=t)
            br=.0004
            if m1==m2 and g!=0.:
                br+=2e-7
            return result(x,br=br),'synthetic vendor'
        with patch('zee_gateE1_joined_27_legacy_bsgamma.superiso_evaluate',
                   side_effect=mock_eval):
            with self.assertRaisesRegex(ValueError,'Degenerate'):
                endpoint_controls(Path('/not/executed'),original,result())

    def test_D5_27_ancestry_checksums_and_unique_ids(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            files={k:root/f'{k}.json' for k in
                   ('B4','B2','C2','C3','C4','C5','D1','D2','D3','D4')}
            for k,p in files.items():p.write_text(k)
            d5=root/'D5.json'
            rows=[{'candidate_id':f'B4_{i:07d}',
                   'physical_Zee_allowed':'UNKNOWN'} for i in range(27)]
            details={r['candidate_id']:{} for r in rows}
            d5.write_text(json.dumps({
                'status':D5_STATUS,'tested':27,
                'rows':rows,'per_spectrum_details':details,
                'input_SHA256':{k:digest(v) for k,v in files.items()}
            }))
            got=validate_provenance({**files,'D5':d5})
            self.assertEqual(len(got),27)
            files['D2'].write_text('new D2')
            with self.assertRaisesRegex(ValueError,'SHA mismatch'):
                validate_provenance({**files,'D5':d5})

    def test_D5_wrong_acceptance_and_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            files={k:root/f'{k}.txt' for k in
                   ('B4','B2','C2','C3','C4','C5','D1','D2','D3','D4')}
            for k,p in files.items():p.write_text(k)
            d5=root/'D5.json'
            rows=[{'candidate_id':str(i),
                   'physical_Zee_allowed':'UNKNOWN'} for i in range(27)]
            details={x['candidate_id']:{} for x in rows}
            origin={'status':D5_STATUS,'tested':27,'rows':rows,
                    'per_spectrum_details':details,
                    'input_SHA256':{k:digest(v) for k,v in files.items()}}
            origin['rows'][0]['physical_Zee_allowed']='ALLOWED'
            d5.write_text(json.dumps(origin))
            with self.assertRaisesRegex(ValueError,'improperly'):
                validate_provenance({**files,'D5':d5})
            origin['rows'][0]['physical_Zee_allowed']='UNKNOWN'
            origin['rows'][1]['candidate_id']=origin['rows'][0]['candidate_id']
            d5.write_text(json.dumps(origin))
            with self.assertRaisesRegex(ValueError,'duplicate'):
                validate_provenance({**files,'D5':d5})

    def test_27_observable_summary_is_explicitly_not_exclusion(self):
        rows=[]
        for i in range(27):
            old=result(br=.00035+i*1e-7)
            checked=compare_legacy_result(initial(),old)
            rows.append({
                **checked,'all_source_pinned_endpoints_consistent':True})
        s=aggregate(rows)
        self.assertEqual(s['model_spectra'],27)
        self.assertTrue(s['all_endpoint_controls_pass'])
        self.assertIsNone(s['Zee_model_allowed_or_excluded'])
        self.assertFalse(s['2026_precision_SM_and_NP_scheme_consistently_combined'])

if __name__=='__main__':
    unittest.main()
