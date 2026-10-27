"""D2 controls and independent verification of real outputs; no repeated vacuum suite."""
import copy
import json
from pathlib import Path
import unittest

import numpy as np
from module2.interface import canonical_hash, decode, evaluate
from module6.d2_family_runner import (select_spectra, generate, compare, matching_provenance,
                                    validate_row, scoped, SOURCE_TOP_MS_160, LHA_SOURCE_SHA256)
from module6.coherent_pilot import STATUS

ROOT=Path(__file__).resolve().parents[1]


class D2FamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed=json.loads((ROOT/'module3/example.json').read_text())
        cls.screen=json.loads((ROOT/'validation/module6/d2_scoped_scan.json').read_text())['scalar_screen']
        cls.selected=select_spectra(cls.seed,cls.screen)
        cls.rows,cls.entries=generate(cls.seed,cls.selected)

    def test_selection_diverse_and_directly_verified(self):
        self.assertEqual([p['name'] for p in self.selected],['source','mH1_m50p0','mH1_p50p0'])
        self.assertEqual(len({tuple(p['physical'].values()) for p in self.selected}),3)
        for p in self.selected:
            self.assertTrue(all(g['assessment']=='PASS' for g in p['gates'].values()))

    def test_independent_directions_exact_target_ids_hashes_and_nonmutation(self):
        old=copy.deepcopy(self.seed);rows,entries=generate(self.seed,self.selected)
        self.assertEqual(self.seed,old);self.assertEqual(len(rows),12)
        original=decode(self.seed['module2_input']['homogeneous_coefficients'],(4,))
        for row,entry in zip(rows,entries):
            validate_row(row)
            self.assertEqual(row['module2_input']['target_eV'],self.seed['module2_input']['target_eV'])
            self.assertEqual(row['module2_input']['ordering'],'NO')
            actual=decode(row['module2_input']['homogeneous_coefficients'],(4,))
            self.assertEqual(np.flatnonzero(actual!=original).tolist(),entry['changed_indices'])
            self.assertEqual(canonical_hash(row),entry['input_sha256'])
            for i in entry['changed_indices']:
                ratio=actual[i]/original[i]
                self.assertNotEqual(ratio.imag,0.)
                self.assertNotAlmostEqual(abs(ratio),1.)

    def test_numerical_bounds_and_invalid_nested_types(self):
        for bad in (True,'x',float('nan'),1e308):
            s=copy.deepcopy(self.seed);s['module2_input']['homogeneous_coefficients']['real'][0]=bad
            with self.subTest(bad=bad),self.assertRaises(ValueError):generate(s,self.selected)

    def test_stale_hash_and_wrong_ids_rejected(self):
        for kind in ('sha','id','mass_type','scale_type'):
            row=copy.deepcopy(self.rows[0]);s=row['module2_input']['scalar']
            if kind=='sha':s['record']['physical']['mH1']+=1
            if kind=='id':s['record']['benchmark_id']='bad';s['sha256']=canonical_hash(s['record'])
            if kind=='mass_type':s['record']['physical']['mH1']=True;s['sha256']=canonical_hash(s['record'])
            if kind=='scale_type':row['module2_input']['null_cone']['scale']=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):validate_row(row)

    def test_exact_matching_provenance(self):
        matching_provenance(160.,SOURCE_TOP_MS_160,LHA_SOURCE_SHA256)
        for mu,mt,lha in ((True,SOURCE_TOP_MS_160,LHA_SOURCE_SHA256),(161.,SOURCE_TOP_MS_160,LHA_SOURCE_SHA256),
                          (160.,173.,LHA_SOURCE_SHA256),(160.,SOURCE_TOP_MS_160,'0'*64)):
            with self.assertRaises(ValueError):matching_provenance(mu,mt,lha)

    def test_screen_fails_closed(self):
        s=copy.deepcopy(self.screen)
        for p in s['points'][1:]:p['gates']['ewpo']['assessment']='UNKNOWN'
        with self.assertRaisesRegex(ValueError,'D2_NO_ALTERNATIVE_SCOPED_SCALAR'):select_spectra(self.seed,s)
        s=copy.deepcopy(self.screen);s['points'][0]['scalar_sha256']='0'*64
        with self.assertRaises(ValueError):select_spectra(self.seed,s)

    def test_real_evidence_independent_closure_yukawa_and_vacuum(self):
        report=json.loads((ROOT/'validation/module6/d2_scoped_scan.json').read_text())
        self.assertEqual(report['completed_coherent_points'],12)
        self.assertEqual(report['blocked_coherent_points'],0)
        self.assertIsNone(report['global_zee_acceptance'])
        self.assertFalse(report['constraints_complete'])
        for row,p in zip(self.rows,report['points']):
            with self.subTest(point=p['benchmark_id']):
                self.assertEqual(canonical_hash(row),p['input_sha256'])
                # Real fresh Module2 evaluation, independent of runner summary logic.
                nout=evaluate(row['module2_input'])
                target=decode(self.seed['module2_input']['target_eV'])
                residual=float(np.linalg.norm(decode(nout['Mnu'])-target)/np.linalg.norm(target))
                self.assertEqual(residual,p['target_vs_reconstructed_relative_error'])
                self.assertLess(residual,2e-9)
                self.assertEqual(canonical_hash(nout['D']),p['D_sha256'])
                for k in ('F','D','Ye2'):
                    self.assertEqual(float(np.max(abs(decode(nout[k])))),p['matrix_max_abs_entries'][k])
                self.assertEqual(p['vacuum_execution'],'FRESH_FULL_FROZEN_SEARCH')
                vacuum=p['scalar_gates']['vacuum']
                self.assertEqual(vacuum['assessment'],'UNKNOWN')
                self.assertFalse(vacuum['global_stability_proven'])
                self.assertTrue(vacuum['runs'])
                for k in ('bfb','reconstruction','unitarity','ewpo'):
                    self.assertEqual(p['scalar_gates'][k]['assessment'],'PASS')
        contrasts=compare(report['points'])
        self.assertEqual(contrasts,report['comparisons'])
        for g in contrasts['within_spectrum'].values():
            self.assertEqual(g['distinct_D_outputs'],4)
            self.assertTrue(all(v==0. for v in g['flavor_max_minus_min'].values()))
        self.assertTrue(all(v['matches'] for v in contrasts['D0_D1_regression'].values()))
        self.assertTrue(all(p['second_minus_source']['delta_C7']!=0. for p in contrasts['cross_spectrum_baseline']))
        broken=copy.deepcopy(report['points']);broken[1]['delta_C7']+=1e-12
        with self.assertRaises(ValueError):compare(broken)

    def test_invented_acceptance_or_complete_lfv_rejected(self):
        # Minimal scope-validator fixture; numerical results are tested above.
        # This control must also run in a clean checkout without ignored outputs.
        full={'status':STATUS,'constraints_complete':False,'global_zee_acceptance':None,
              'neutrino_lfv':{'COMPLETE_LFV':False,
                             'gates':{'full_lfv':'NOT_EVALUATED','exact_one_loop':'UNKNOWN'},
                             'module4_Barr_Zee_and_W_completion':'NOT_EVALUATED'},
              'neutrino':{'gates':{'data_comparison':'NOT_EVALUATED'}},
              'scalar':{'global_vacuum_certification':'NOT_ESTABLISHED'},
              'bsgamma':{'experiment_comparison':'NOT_EVALUATED','flavor_classification':'UNCLASSIFIED',
                         'nonlinear_reliability':'UNKNOWN'}}
        scoped(full)
        for kind in ('acceptance','lfv','allowed','experimental','invented_flag','invented_complete'):
            value=copy.deepcopy(full)
            if kind=='acceptance':value['global_zee_acceptance']=True
            if kind=='lfv':value['neutrino_lfv']['COMPLETE_LFV']=True
            if kind=='allowed':value['bsgamma']['flavor_classification']='ALLOWED'
            if kind=='experimental':value['bsgamma']['experiment_comparison']='PASS'
            if kind=='invented_flag':value['allowed']=True
            if kind=='invented_complete':value['COMPLETE_LFV']=True
            with self.subTest(kind=kind),self.assertRaises(ValueError):scoped(value)


if __name__=='__main__':unittest.main()
