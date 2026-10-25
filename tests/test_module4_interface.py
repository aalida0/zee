"""Provenance, frozen-output append, schema and CLI regression tests."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from module2.interface import canonical_hash, strict_loads
from module3.interface import evaluate as evaluate3
from module4.interface import evaluate, validate
from test_module4_physics import cases, EXTRA, ROOT

EVIDENCE={}


def record(case=0):
    inp,nout=cases()[case]
    return copy.deepcopy(dict(schema_version='1.0.0',kind='module3_matching_input_v1',
        module3_input=inp,module2_output=nout,two_loop_inputs=EXTRA))


class InterfaceTests(unittest.TestCase):
    def test_Module4_foundations_correct_branch_and_ancestry(self):
        from module3.interface import foundations
        pins=foundations()
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
        self.assertEqual(branch,'feature/zee-barrzee-module4')
        for k in ('module0_tag_commit','module1_commit','module2_commit'):
            self.assertEqual(subprocess.run(['git','merge-base','--is-ancestor',pins[k],'HEAD'],cwd=ROOT).returncode,0)
        self.assertEqual(subprocess.check_output(['git','rev-parse','zee-neutrino-module2-physics-v1^{}'],cwd=ROOT,text=True).strip(),pins['module2_commit'])
        EVIDENCE['module4_frozen_files_verified']=len(pins['sha256'])
        EVIDENCE['inherited_branch_guard']='Run unchanged and reported as expected branch conflict in full regression; replacement ancestry assertions pass here'

    def test_all_NO_IO_matching_records_no_neutrino_fit(self):
        counts=[]
        with patch('module2.interface.evaluate',side_effect=AssertionError('No neutrino fit in Module4')):
            for k in range(6):
                out=evaluate(record(k))
                validate(out,'output.schema.json')
                counts.append(sum(len(c['ledger'])+len(c['two_loop_candidates']) for c in out['channels'].values()))
                self.assertFalse(out['COMPLETE_LFV']);self.assertIsNone(out['global_zee_acceptance'])
                for ch in out['channels'].values():
                    self.assertEqual(ch['rate_scope'],'INCLUDED_TOPOLOGIES_ONLY')
                    self.assertEqual(ch['experimental_comparison'],'NOT_EVALUATED')
                    self.assertTrue(all(r['coherent_inclusion'] is False for r in ch['two_loop_candidates'].values()))
                    self.assertTrue(all(r['status']=='UNKNOWN' for r in ch['two_loop_candidates'].values()))
                    self.assertEqual(len(ch['ledger']),40)
                    self.assertEqual(len(ch['two_loop_candidates']),2)
                    self.assertTrue(all(r['loop_species']=='W+Goldstone+ghost' for r in ch['two_loop_candidates'].values()))
                    for k in ('C_L','C_R'):
                        expected=sum(complex(**r[k]) for r in ch['ledger'].values())
                        self.assertEqual(complex(**ch[k]),expected)
        self.assertEqual(counts,[126]*6)
        EVIDENCE['witnesses_channels_components']={'witnesses':6,'channels_each':3,'components_each_channel':42}

    def test_complete_Module3_output_preserved_and_signed_components_reproduced(self):
        data=record();old=evaluate3(data['module3_input']);before=canonical_hash(old)
        data['module3_output']=old
        out=evaluate(data)
        self.assertEqual(out['module3_output'],old)
        self.assertEqual(canonical_hash(old),before)
        for key,channel in out['channels'].items():
            for name,r in old['ledger'][key].items():
                added=channel['ledger']['module3_'+name]
                for k,v in r.items():
                    if k!='validation_status':self.assertEqual(added[k],v)
        EVIDENCE['complete_module3_output_roundtrip']='PASS; original entire record preserved; all signed components reproduced'
        for mutate in ('input_sha256','module2_output_sha256','dipole_normalization'):
            bad=copy.deepcopy(data);bad['module3_output']['provenance'][mutate]='bad'
            with self.assertRaises(ValueError):evaluate(bad)
        bad=copy.deepcopy(data)
        bad['module3_output']['ledger']['mu_to_e_gamma']['h']['C_L']['real']+=1e-10
        with self.assertRaises(ValueError):evaluate(bad)

    def test_provenance_tampering_rejected(self):
        mutations=[lambda d:d['module2_output']['provenance'].__setitem__('input_sha256','wrong'),
                   lambda d:d['module2_output']['provenance']['code_sha256'].__setitem__('module2/core.py','wrong'),
                   lambda d:d['module2_output']['D']['imag'][0].__setitem__(1,.2),
                   lambda d:d['module2_output']['Ye2']['real'][0].__setitem__(1,.2),
                   lambda d:d['module3_input']['module2_input']['scalar'].__setitem__('sha256','wrong'),
                   lambda d:d['module3_input'].__setitem__('benchmark_id','wrong'),
                   lambda d:d['module2_output'].__setitem__('status','INPUT_OR_EVALUATION_ERROR')]
        for fn in mutations:
            data=record();fn(data)
            with self.assertRaises((ValueError,KeyError)):evaluate(data)

    def test_schema_version_finite_unknown_fields_and_mass_scheme_rejected(self):
        bads=[]
        for key,value in [('schema_version','0.9'),('kind','old_scan'),('unrecognized',1)]:
            data=record();data[key]=value;bads.append(data)
        for key,value in [('mass_yukawa_scheme','MSbar_claim_without_matching'),('mW_GeV',float('nan'))]:
            data=record();data['two_loop_inputs'][key]=value;bads.append(data)
        data=record();del data['two_loop_inputs']['fermion_masses_GeV']['charm'];bads.append(data)
        data=record();data['two_loop_inputs']['fermion_masses_GeV']['tau']=1.8;bads.append(data)
        for data in bads:
            with self.assertRaises(ValueError):evaluate(data)
        with self.assertRaises(ValueError):strict_loads('{"x":1,"x":2}')

    def test_cli_real_example_and_fail_closed_no_partial_output(self):
        with tempfile.TemporaryDirectory() as name:
            out=Path(name)/'result.json'
            result=subprocess.run([sys.executable,'-m','module4.interface','--input',str(ROOT/'module4/example.json'),'--output',str(out)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            validate(strict_loads(out.read_text()),'output.schema.json')
            bad=Path(name)/'bad.json';bad.write_text('{"schema_version":"bad"}')
            rejected=Path(name)/'rejected.json'
            result=subprocess.run([sys.executable,'-m','module4.interface','--input',str(bad),'--output',str(rejected)],capture_output=True,text=True)
            self.assertEqual(result.returncode,2);self.assertFalse(rejected.exists())


if __name__=='__main__':unittest.main()
