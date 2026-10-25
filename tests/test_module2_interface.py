import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest
import numpy as np
from module2.interface import canonical_hash, encode, decode, evaluate, strict_loads, validate_schema
from module2.schema import load_schema, validate_instance
from module2.core import forward
from module2.data import compare
from test_module2_physics import target, ML

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE={}


def example():
    M,_,_=target('NO')
    record={'schema_version':'1.0.0','model':'ZeeTypeII_Module0_v1_restricted_CP','parameter_convention':'SARAH_ZeeTypeII_Florentino_v1','units':{'masses':'GeV','angles':'rad'},'physical':{'mH1':300.,'mH2':700.,'beta':1.394,'gamma':1.089,'v':246.21965}}
    return {'schema_version':'1.0.0','benchmark_id':'complex_NO_family','mode':'inverse','ordering':'NO','scalar':{'kind':'explicit','record':record,'sha256':canonical_hash(record)},'lepton_masses_GeV':ML.tolist(),'target_eV':encode(M),'null_cone':{'t':{'real':.25,'imag':.1},'scale':.002,'root':0,'chart':[0,1,2],'phase_rad':.43},'homogeneous_coefficients':{'real':[1e-7,-2e-7,3e-7,1e-7],'imag':[2e-7,0,-1e-7,3e-7]}}


class InterfaceTests(unittest.TestCase):
    def test_roundtrips_and_schemas(self):
        for path in (ROOT/'module2').glob('*.schema.json'):
            validate_instance({}, {'type': 'object'})
            self.assertIsInstance(load_schema(path), dict)
        for ordering in ['NO','IO']:
            x=example();x['ordering']=ordering;x['target_eV']=encode(target(ordering)[0])
            x['dataset']=json.loads((ROOT/f'module2/data/nufit60_ic19_{ordering.lower()}.json').read_text())
            validate_schema(x['dataset'],'dataset.schema.json')
            y=evaluate(x)
            self.assertIsNone(y['global_zee_acceptance'])
            self.assertEqual(y['gates']['inverse'],'PASS')
            self.assertIsNone(y['comparison']['experimental_acceptance'])
            self.assertEqual(y['comparison']['likelihood'],'GAUSSIAN_APPROXIMATION')
            validate_schema(y,'output.schema.json')
            fwd={k:v for k,v in x.items() if k not in ['target_eV','null_cone','homogeneous_coefficients']}
            fwd.update(mode='forward',F=y['F'],D=y['D'])
            d=evaluate(fwd)
            self.assertLess(np.max(abs(decode(d['Mnu'])-decode(x['target_eV']))),1e-12)
            fwd.pop('D');fwd['Ye2']=y['Ye2']
            e=evaluate(fwd)
            self.assertLess(np.max(abs(decode(e['Mnu'])-decode(y['Mnu']))),2e-12)
            masses=y['observables']['masses_eV']
            EVIDENCE[ordering]={'masses_eV':masses,'dm21_eV2':y['observables']['dm21_eV2'],'dm3l_eV2':y['observables']['dm3l_eV2'],'delta_rad':y['observables']['delta_rad'],'m_beta_eV':y['observables']['m_beta_eV'],'m_bb_eV':y['observables']['m_bb_eV'],'chi2_gaussian':y['comparison']['chi2'],'closure_eV':float(np.max(abs(decode(y['Mnu'])-decode(x['target_eV']))))}
        self.assertEqual(evaluate(example())['comparison']['status'],'NOT_EVALUATED')

    def test_data_covariance_and_periodic_phase(self):
        d=json.loads((ROOT/'module2/data/nufit60_ic19_no.json').read_text())
        o={k:v for k,v in zip(d['observables'],d['mean'])};o['ordering']='NO'
        self.assertEqual(compare(o,d)['chi2'],0)
        # Nonzero supplied correlations are preserved; independently invert 2x2.
        d['covariance'][0][1]=d['covariance'][1][0]=.2*math.sqrt(d['covariance'][0][0]*d['covariance'][1][1])
        o['sin2_theta12']+=math.sqrt(d['covariance'][0][0]);o['sin2_theta13']+=2*math.sqrt(d['covariance'][1][1])
        self.assertAlmostEqual(compare(o,d)['chi2'],(1+4-.8)/.96,places=12)
        for field,value in [('covariance',[[1]*5]*5),('ordering','IO'),('likelihood','OFFICIAL'),('source',{})]:
            bad=copy.deepcopy(d);bad[field]=value
            with self.assertRaises(ValueError):compare(o,bad)
        p=copy.deepcopy(d);p.update(observables=['delta_rad'],units={'delta_rad':'rad'},mean=[.01],covariance=[[.04]])
        self.assertAlmostEqual(compare({'ordering':'NO','delta_rad':2*math.pi-.01},p)['chi2'],.01,places=12)
        self.assertEqual(compare({'ordering':'NO','delta_rad':None},p)['status'],'UNKNOWN')
        shifted=copy.deepcopy(o);shifted['dm21_eV2']+=1e-3
        self.assertGreater(compare(shifted,d)['chi2'],1e5)

    def test_module1_input_and_actual_output(self):
        from module1.scalar_constraints import evaluate as scalar_evaluate
        r=json.loads((ROOT/'module1/example.json').read_text())
        x=example();x['scalar']={'kind':'module1_input','record':r,'sha256':canonical_hash(r)}
        a=evaluate(x)
        self.assertEqual(a['provenance']['scalar']['scalar_gates'],'NOT_EVALUATED')
        # Real Module1 evaluation, including its UNKNOWN vacuum semantics.
        s=scalar_evaluate(r)
        x['scalar']={'kind':'module1_output','record':s,'sha256':canonical_hash(s)}
        b=evaluate(x)
        self.assertLess(np.max(abs(decode(a['Mnu'])-decode(b['Mnu']))),1e-14)
        self.assertEqual(b['provenance']['scalar']['scalar_gates'],s['gates'])
        s['provenance']['schema_sha256']='0'*64;x['scalar']['sha256']=canonical_hash(s)
        with self.assertRaises(ValueError):evaluate(x)
        s['provenance'].pop('schema_sha256');s['schema_version']='0.0.0';x['scalar']['sha256']=canonical_hash(s)
        with self.assertRaises(ValueError):evaluate(x)
        EVIDENCE['module1_actual_output_interoperability']='PASS'

    def test_fail_closed_and_jsonl(self):
        x=example()
        bads=[]
        for key,value in [('schema_version','2.0.0'),('ordering','both'),('lepton_masses_GeV',[1,2,float('nan')]),('unknown',3),('benchmark_id','  ')]:
            y=copy.deepcopy(x);y[key]=value;bads.append(y)
        y=copy.deepcopy(x);y['null_cone']['chart'][0]=True;bads.append(y)
        for field,value in [('sha256','0'*64),('kind','legacy')]:
            y=copy.deepcopy(x);y['scalar'][field]=value;bads.append(y)
        y=copy.deepcopy(x);y['scalar']['record']['units']['masses']='eV';y['scalar']['sha256']=canonical_hash(y['scalar']['record']);bads.append(y)
        y=copy.deepcopy(x);y['target_eV']['imag'][0][1]+=.01;bads.append(y)
        y=copy.deepcopy(x);y['homogeneous_coefficients']['real'][0]=True;bads.append(y)
        for y in bads:
            with self.assertRaises((ValueError,TypeError)):evaluate(y)
        for s in ['{"x":1,"x":2}','{"x":NaN}','{"x":1e999}']:
            with self.assertRaises(ValueError):strict_loads(s)
        lines=[json.dumps(x),'{"schema_version":"invalid"}',json.dumps(x)]
        cp=subprocess.run([sys.executable,'-m','module2.interface','--jsonl'],input='\n'.join(lines)+'\n',text=True,capture_output=True,cwd=ROOT)
        self.assertEqual(cp.returncode,2,cp.stderr)
        results=[json.loads(v) for v in cp.stdout.splitlines()]
        self.assertEqual(len(results),3)
        self.assertEqual(results[0],results[2])
        self.assertEqual(results[1]['status'],'INPUT_OR_EVALUATION_ERROR')
        for r in results:validate_schema(r,'output.schema.json')
        zero=copy.deepcopy(x);zero['scalar']['record']['physical']['gamma']=0;zero['scalar']['sha256']=canonical_hash(zero['scalar']['record'])
        cp=subprocess.run([sys.executable,'-m','module2.interface'],input=json.dumps(zero),text=True,capture_output=True,cwd=ROOT)
        self.assertEqual(cp.returncode,2,cp.stderr);self.assertEqual(json.loads(cp.stdout)['status'],'UNKNOWN')
        cp=subprocess.run([sys.executable,'-m','module2.interface'],input=json.dumps(x),text=True,capture_output=True,cwd=ROOT)
        self.assertEqual(cp.returncode,0,cp.stderr);validate_schema(json.loads(cp.stdout),'output.schema.json')


if __name__=='__main__':unittest.main()
