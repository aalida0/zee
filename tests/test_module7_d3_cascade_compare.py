"""Independent linkage falsifiers. Never execute pilot/vacuum/matching."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from module7.d3_cascade_compare import compare, verify_sources, attach_point, scope_guard, ROOT, D2_SHA, sha
from module2.interface import canonical_hash


class D3CompareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seed_raw=(ROOT/'module3/example.json').read_bytes()
        cls.d2_raw=(ROOT/'validation/module6/d2_scoped_scan.json').read_bytes()
        cls.seed,cls.d2=verify_sources(cls.seed_raw,cls.d2_raw)
        with patch('module1.scalar_constraints.search_vacuum',side_effect=AssertionError('Forbidden vacuum rerun')), \
             patch('module6.coherent_pilot.pilot',side_effect=AssertionError('Forbidden coherent rerun')):
            cls.result=compare(cls.seed_raw,cls.d2_raw)

    def test_real_replay_cutflow_dedup_and_twelve(self):
        r=self.result
        self.assertEqual((r['scoped_pass'],r['control_only_fail'],r['linked_points']),(29,6,12))
        self.assertEqual(r['status'],'D3_COUPLED_DIAGNOSTIC_PASS')
        self.assertEqual(sum(p['control_only'] for p in r['scalar_spectra']),6)
        self.assertLess(r['distinct_charged_spectra'],29)
        self.assertEqual(r['repeated_vacuum_searches'],0)
        for p in r['points']:
            self.assertEqual(p['bound_scalar_sha256'],canonical_hash(p['full_scalar_input']))
            self.assertTrue(p['cascade']['is_kinematically_open'])
        self.assertIsNone(r['global_zee_acceptance'])
        self.assertEqual(r['BR_status'],'BR_NOT_EVALUATED')

    def test_fixed_spectrum_gauge_flavor_invariance_lfv_response(self):
        for group in self.result['comparisons']['within_spectrum'].values():
            self.assertEqual(group['cascade_width_max_minus_min_GeV'],0.)
            self.assertTrue(all(v==0. for v in group['flavor_max_minus_min'].values()))
            self.assertEqual(group['distinct_D_outputs'],4)
            self.assertGreater(group['higgs_lfv_widths_GeV']['h_to_e_tau']['max_over_min'],60.)
            self.assertGreater(group['radiative_subset_BR']['mu_to_e_gamma']['max_over_min'],1.)
        from module6.d2_family_runner import compare as compare_families
        bad=copy.deepcopy(self.d2['points']);bad[1]['delta_C7']+=1e-12
        with self.assertRaisesRegex(ValueError,'invariance falsified'):
            compare_families(bad)

    def test_complete_seed_and_d2_byte_hashes(self):
        self.assertEqual(sha(self.d2_raw),D2_SHA)
        for raw in (self.seed_raw+b' ',self.seed_raw.replace(b'700.0',b'701.0')):
            with self.assertRaises(ValueError):verify_sources(raw,self.d2_raw)
        for raw in (self.d2_raw+b' ',self.d2_raw.replace(b'700.0',b'701.0')):
            with self.assertRaises(ValueError):verify_sources(self.seed_raw,raw)

    def test_wrong_manifest_and_frozen_source_hash(self):
        d=copy.deepcopy(self.d2);d['source_sha256']['module3/example.json']='0'*64
        with self.assertRaises(ValueError):verify_sources(self.seed_raw,json.dumps(d).encode())
        read=Path.read_bytes
        def corrupt_source(path):
            raw=read(path)
            return raw+b' ' if path==ROOT/'module1/scalar_constraints.py' else raw
        with patch.object(Path,'read_bytes',corrupt_source):
            with self.assertRaisesRegex(ValueError,'Frozen source SHA mismatch'):
                verify_sources(self.seed_raw,self.d2_raw)

    def test_direct_linkage_falsifiers_even_without_archive_hash(self):
        original=self.d2['points'][0];spectrum=self.d2['selected_spectra'][0]
        cases=[('bound_scalar_sha256','0'*64),('benchmark_id','wrong'),
               ('input_sha256','0'*64),('module2_input_sha256','0'*64),
               ('flavor_derived_input_sha256','0'*64),('source_manifest_sha256','0'*64),
               ('target_sha256','0'*64),('family_name','invented')]
        for key,value in cases:
            p=copy.deepcopy(original);p[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                attach_point(self.seed,spectrum,p,self.d2['source_manifest_sha256'])
        for key in ('mH1','mH2','gamma','v'):
            p=copy.deepcopy(original);p['physical'][key]+=1e-6
            with self.subTest(key=key),self.assertRaises(ValueError):
                attach_point(self.seed,spectrum,p,self.d2['source_manifest_sha256'])

    def test_duplicates_nan_threshold_and_invented_quantities(self):
        from module2.interface import strict_loads
        for text in ('{"a":1,"a":2}','{"a":NaN}'):
            with self.assertRaises(ValueError):strict_loads(text)
        bad=copy.deepcopy(self.d2);bad['points'][1]=bad['points'][0]
        with self.assertRaises(ValueError):compare(self.seed_raw,json.dumps(bad).encode())
        for key,val in [('allowed',False),('is_allowed',True),('COMPLETE_LFV',True),
                        ('total_width_GeV',1.),('branching_fraction',1.),('cascade_br',1.),
                        ('production_cross_section_pb',1.),('global_zee_acceptance',True),('x',float('nan'))]:
            with self.subTest(key=key),self.assertRaises(ValueError):scope_guard({key:val})
        from module7.d3_cascade_compare import scalar_width
        record=copy.deepcopy(self.seed['module2_input']['scalar']['record'])
        record['physical']['mH2']=record['physical']['mH1']+record['electroweak']['mZ']
        self.assertFalse(scalar_width(record)['is_kinematically_open'])
        self.assertEqual(scalar_width(record)['partial_width_GeV'],0.)

    def test_cli_replay(self):
        out=ROOT/'validation/module7/local/test_cli.json'
        p=subprocess.run([sys.executable,'-m','module7.d3_cascade_compare','--seed','module3/example.json',
            '--d2-evidence','validation/module6/d2_scoped_scan.json','--output',str(out)],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(out.read_text()),self.result)


if __name__=='__main__':unittest.main()
