"""Real Module1/2 interoperability, complex family witnesses, negative cases."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
import numpy as np
from module2.interface import evaluate as m2_evaluate, decode, canonical_hash, encode
from module3.interface import evaluate, foundations, strict_loads, validate
from module3.witnesses import example, ML, target

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE={}


class InterfaceTests(unittest.TestCase):
    def test_foundation_hashes_and_branch_ancestry(self):
        pins=foundations()
        self.assertEqual(subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'feature/zee-lfv-module3')
        for k in ['module0_tag_commit','module1_commit','module2_commit']:
            cp=subprocess.run(['git','merge-base','--is-ancestor',pins[k],'HEAD'],cwd=ROOT,capture_output=True)
            self.assertEqual(cp.returncode,0,cp.stderr)
        sha=subprocess.check_output(['git','rev-parse','zee-neutrino-module2-physics-v1^{}'],cwd=ROOT,text=True).strip()
        self.assertEqual(sha,pins['module2_commit'])
        EVIDENCE['frozen_files_verified']=len(pins['sha256'])

    def test_NO_IO_full_current_family_three_spectra(self):
        rng=np.random.default_rng(934)
        evidence=[]
        for ordering in ['NO','IO']:
            for spectrum in range(3):
                x=example(ordering,spectrum)
                # Independent random coefficients in all four homogeneous
                # directions of the CURRENT audited Module2 family.
                x['module2_input']['homogeneous_coefficients']=encode((rng.normal(size=4)+1j*rng.normal(size=4))*1e-7)
                m2=m2_evaluate(x['module2_input']);x['module2_output']=m2
                out=evaluate(x)
                validate(out,'output.schema.json')
                err=float(np.max(abs(decode(m2['Mnu'])-target(ordering))))
                ye,y2=decode(m2['Ye']),decode(m2['Ye2'])
                p=x['module2_input']['scalar']['record']['physical']
                mass=np.cos(p['beta'])*ye+np.sin(p['beta'])*y2
                merr=float(np.max(abs(mass-np.diag(np.sqrt(2)*ML/p['v']))))
                self.assertLess(err,1e-11);self.assertLess(merr,1e-16)
                self.assertEqual(out['gates']['tree'],'PASS')
                self.assertFalse(out['COMPLETE_LFV']);self.assertIsNone(out['global_zee_acceptance'])
                self.assertEqual(len(out['observables']),17)
                qs=[v['quadrature_relative_change'] for v in out['observables'].values() if 'quadrature_relative_change' in v]
                evidence.append({'ordering':ordering,'spectrum':spectrum,'physical':p,
                                 'homogeneous_coefficients':x['module2_input']['homogeneous_coefficients'],
                                 'module2_input_sha256':canonical_hash(x['module2_input']),
                                 'neutrino_closure_max_abs_eV':err,'Yukawa_mass_rotation_max_abs':merr,
                                 'family_relative_residual':m2['inverse']['family_relative_residual'],
                                 'tree_max_quadrature_relative_change':max(qs),
                                 'radiative_partial_BR':{k:v['partial_BR'] for k,v in out['observables'].items() if k.endswith('gamma')}})
        EVIDENCE['NO_IO_family_spectra']=evidence

    def test_actual_Module1_output_and_Module2_output(self):
        from module1.scalar_constraints import evaluate as m1_evaluate
        x=example();inp=x['module2_input']
        scalar=m1_evaluate(inp['scalar']['record'])
        inp['scalar']={'kind':'module1_output','record':scalar,'sha256':canonical_hash(scalar)}
        x['module2_output']=m2_evaluate(inp)
        result=evaluate(x)
        self.assertEqual(result['provenance']['scalar']['scalar_gates'],scalar['gates'])
        self.assertEqual(result['gates']['provenance'],'PASS')
        EVIDENCE['actual_Module1_output_Module2_output_roundtrip']='PASS'

    def test_tampered_full_Module2_output_rejected(self):
        x=example();x['module2_output']=m2_evaluate(x['module2_input'])
        mutations=[('F',lambda r:r['F']['imag'][0].__setitem__(1,.7)),
                   ('D',lambda r:r['D']['real'][1].__setitem__(0,.1)),
                   ('Ye',lambda r:r['Ye']['imag'][0].__setitem__(0,.1)),
                   ('Mnu',lambda r:r['Mnu']['imag'][1].__setitem__(1,.3)),
                   ('input_sha',lambda r:r['provenance'].__setitem__('input_sha256','0'*64)),
                   ('source_sha',lambda r:r['provenance']['code_sha256'].__setitem__('module2/core.py','0'*64)),
                   ('scalar_sha',lambda r:r['provenance']['scalar'].__setitem__('sha256','0'*64)),
                   ('identity',lambda r:r.__setitem__('benchmark_id','wrong'))]
        for label,mutation in mutations:
            with self.subTest(label=label):
                bad=copy.deepcopy(x);mutation(bad['module2_output'])
                with self.assertRaises(ValueError):evaluate(bad)
        bad=copy.deepcopy(x)
        bad['module2_input']['homogeneous_coefficients']['imag'][2]+=.001
        with self.assertRaises(ValueError):evaluate(bad)
        EVIDENCE['deliberately_mismatched_Module2_outputs_rejected']=len(mutations)+1

    def test_strict_input_negative_cases(self):
        x=example();bad=[]
        for key,value in [('schema_version','2.0.0'),('extra',1),('benchmark_id','wrong')]:
            y=copy.deepcopy(x);y[key]=value;bad.append(y)
        for field,value in [('alpha_em',True),('GF_GeV_minus2',0),('total_lepton_widths_GeV',[1,float('nan')])]:
            y=copy.deepcopy(x);y['constants'][field]=value;bad.append(y)
        for key,value in [('tree_quadrature_order',True),('tree_quadrature_order',2),('tree_relative_tolerance',.1)]:
            y=copy.deepcopy(x);y['numerics'][key]=value;bad.append(y)
        y=copy.deepcopy(x);del y['module2_input']['scalar']['record']['physical']['alpha'];bad.append(y)
        y=copy.deepcopy(x);y['module2_input']['F']=encode(np.eye(3));bad.append(y)
        y=copy.deepcopy(x);y['module2_input']['scalar']['record']['physical']['mh1']=1.;y['module2_input']['scalar']['sha256']=canonical_hash(y['module2_input']['scalar']['record']);bad.append(y)
        y=copy.deepcopy(x);y['module2_input']['lepton_masses_GeV']=[3,2,1];bad.append(y)
        for y in bad:
            with self.assertRaises((ValueError,TypeError)):evaluate(y)
        for s in ['{"a":1,"a":2}','{"a":NaN}','{"a":1e999}']:
            with self.assertRaises(ValueError):strict_loads(s)
        EVIDENCE['strict_negative_input_cases_rejected']=len(bad)+3

    def test_unsupported_minimal_scalar_record_rejected(self):
        x=example();inp=x['module2_input']
        p=inp['scalar']['record']['physical']
        record={'schema_version':'1.0.0','model':'ZeeTypeII_Module0_v1_restricted_CP','parameter_convention':'SARAH_ZeeTypeII_Florentino_v1',
                'units':{'masses':'GeV','angles':'rad'},'physical':{k:p[k] for k in ['mH1','mH2','gamma','beta','v']}}
        inp['scalar']={'kind':'explicit','record':record,'sha256':canonical_hash(record)}
        # Valid Module2, insufficient neutral-scalar information for Module3.
        self.assertEqual(m2_evaluate(inp)['status'],'NEUTRINO_COMPUTED')
        with self.assertRaisesRegex(ValueError,'full Module1'):evaluate(x)

    def test_quadrature_nonconvergence_is_UNKNOWN(self):
        x=example();x['numerics']={'tree_quadrature_order':12,'tree_relative_tolerance':1e-9}
        out=evaluate(x)
        self.assertEqual(out['gates']['tree'],'UNKNOWN')
        self.assertEqual(out['observables']['mu_to_3e']['status'],'UNKNOWN')

    def test_typed_output_contract_rejects_false_completeness(self):
        x=example();x['numerics']['tree_quadrature_order']=12
        out=evaluate(x)
        bad=copy.deepcopy(out);bad['COMPLETE_LFV']=True
        with self.assertRaises(ValueError):validate(bad,'output.schema.json')
        bad=copy.deepcopy(out);bad['ledger']['mu_to_e_gamma']['H1_F']['loop_order']=2
        with self.assertRaises(ValueError):validate(bad,'output.schema.json')
        bad=copy.deepcopy(out);bad['observables']['mu_to_3e']['width_GeV']=-1.
        with self.assertRaises(ValueError):validate(bad,'output.schema.json')
        bad=copy.deepcopy(out);bad['observables']['h_to_e_mu']['global_allowed']=True
        with self.assertRaises(ValueError):validate(bad,'output.schema.json')

    def test_cli_single_and_JSONL_batch_error_isolation(self):
        x=example();x['numerics']['tree_quadrature_order']=12
        cp=subprocess.run([sys.executable,'-m','module3.interface'],input=json.dumps(x),cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(cp.returncode,0,cp.stderr)
        out=json.loads(cp.stdout);validate(out,'output.schema.json')
        rows=[json.dumps(x),'{"schema_version":"bad"}',json.dumps(x)]
        cp=subprocess.run([sys.executable,'-m','module3.interface','--jsonl'],input='\n'.join(rows)+'\n',cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(cp.returncode,2,cp.stderr)
        out=[json.loads(line) for line in cp.stdout.splitlines()]
        self.assertEqual(len(out),3);self.assertEqual(out[0],out[2])
        self.assertEqual(out[1]['status'],'INPUT_OR_EVALUATION_ERROR')
        for r in out:validate(r,'output.schema.json')


if __name__=='__main__':unittest.main()
