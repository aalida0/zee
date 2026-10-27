"""Narrow executable regression tests; SM integration must fail closed on v1.0.3."""
import copy
import json
import math
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'scripts')]
from module5.hyperiso_patch_contract import make_contract
from zee_module5_two_state_patch import build, command, parse_output, run, validate_contract
from zee_module5_hyperiso_bridge import spectrum

BASE = dict(mH1_GeV=550., mH2_GeV=900., beta_rad=math.atan(5.3), gamma_rad=1.09,
            mt_MSbar_GeV=163.96892236746697, matching_scale_GeV=160.)


class PayloadTests(unittest.TestCase):
    def test_contract_roundtrip_and_tampering(self):
        c = make_contract(BASE)
        self.assertEqual(validate_contract(c), c)
        for field, value in [('contribution','SM'), ('contribution','TOTAL'),
                             ('order','NLO'), ('zee_lo_source_sha256','bad')]:
            bad = copy.deepcopy(c);bad[field] = value
            with self.assertRaises(ValueError):validate_contract(bad)
        bad = copy.deepcopy(c);bad['coefficients']['C7']['real'] *= -1
        with self.assertRaises(ValueError):validate_contract(bad)

    def test_scale_and_mass_definition_rejected(self):
        with self.assertRaises(ValueError):
            validate_contract(make_contract({**BASE, 'matching_scale_GeV':81.}))
        bad = make_contract(BASE);bad['input']['top_mass_input_definition'] = 'POLE'
        with self.assertRaises(ValueError):validate_contract(bad)


class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.environ.get('HYPERISO_UPSTREAM') or not os.environ.get('HYPERISO_BINARY'):
            raise unittest.SkipTest('Set explicit pinned HYPERISO_UPSTREAM and HYPERISO_BINARY for runtime evidence')
        cls.up = Path(os.environ['HYPERISO_UPSTREAM']).resolve()
        cls.local = ROOT/'validation/module5/local/two_state'
        cls.exe, cls.provenance = build(cls.up, Path(os.environ['HYPERISO_BINARY']), cls.local)
        cls.template = (cls.up/'reproducibility/inputs/thdm_reference.lha').read_text()
        cls.records = [];cls.cache = {};cls.residuals = []
        seed = cls.native(550.)
        cls.mt = seed['mt']

    @classmethod
    def tearDownClass(cls):
        (cls.local/'runtime.json').write_text(json.dumps(dict(provenance=cls.provenance,
            executable_runs=cls.records, quantitative_residuals=cls.residuals), indent=2, allow_nan=False)+'\n')

    @classmethod
    def invoke(cls, args, label):
        r = run([cls.exe]+args, cls.up, check=False)
        cls.records.append(dict(label=label, argv=list(map(str,args)), returncode=r.returncode,
                                stdout=r.stdout, stderr=r.stderr))
        return r, parse_output(r.stdout) if 'C0 MT ' in r.stdout else None

    @classmethod
    def native(cls, mass, tanb=5.3, flip=False):
        key=(mass,tanb,flip)
        if key in cls.cache:return cls.cache[key]
        inp=cls.local/f'native_{mass}_{tanb}_{flip}.lha'
        inp.write_text(spectrum(cls.template,mass,tanb,flip))
        args=['--mode','native','--model','THDM','--lha',str(inp),'--spectrum','true',
              '--contribution','BSM','--order','LO','--top-scheme','MSBAR_AT_QMATCH',
              '--qmatch','160','--qhad','4.8']
        r, data=cls.invoke(args, 'native '+str(key))
        if r.returncode:raise RuntimeError(r.stderr)
        cls.cache[key]=data
        return data

    def contract(self, **updates):
        return make_contract({**BASE,'mt_MSbar_GeV':self.mt,**updates})

    def close(self, a, b, label):
        residual=abs(a-b);self.residuals.append(dict(label=label,absolute=residual))
        self.assertLessEqual(residual, 2e-14+2e-11*abs(b),label)

    def composition(self, data, stage):
        for c, values in data[stage].items():
            for scale in (0,1):
                self.close(values[2][scale],values[0][scale]+values[1][scale],f'{stage} {c} total scale{scale}')

    def test_sm_patch_is_dropped_and_adapter_stops(self):
        c=self.contract()
        args=command(self.exe,c,4.8,self.up/'reproducibility/inputs/thdm_reference.lha')[1:]
        r,data=self.invoke(args,'production SM two-state rejection')
        self.assertEqual(r.returncode,3);self.assertIn('SM_BSM_PATCH_DROPPED',r.stderr)
        self.assertEqual(data['mt'],self.mt)
        for key in ('C7','C8'):
            self.assertLess(c['coefficients'][key]['real'],0.)
            self.assertEqual(data['AFTER'][key][1],(0j,0j))
            self.assertEqual(data['BEFORE'][key],data['AFTER'][key])
        self.composition(data,'AFTER')

    def test_native_weighted_two_state_and_limits(self):
        cases=[{}, {'gamma_rad':0.}, {'gamma_rad':math.pi/2,'mH1_GeV':900.,'mH2_GeV':550.},
               {'mH2_GeV':550.}, {'mH1_GeV':900.,'mH2_GeV':550.,'gamma_rad':math.pi/2-BASE['gamma_rad']},
               {'mH1_GeV':100000.,'mH2_GeV':200000.}]
        for case in cases:
            c=self.contract(**case); inp=c['input'];g=inp['gamma_rad']
            a=self.native(inp['mH1_GeV']);b=self.native(inp['mH2_GeV'])
            for key in ('C7','C8'):
                expected=math.cos(g)**2*a['BEFORE'][key][1][0]+math.sin(g)**2*b['BEFORE'][key][1][0]
                self.close(c['coefficients'][key]['real'],expected,'native weighted '+key+str(case))
                for part,weight,native in zip(c['coefficients'][key]['per_state_real'],
                        (math.cos(g)**2,math.sin(g)**2),(a,b)):
                    self.close(part,weight*native['BEFORE'][key][1][0],'per state '+key)
            if inp['mH1_GeV']==100000.:
                self.assertLess(abs(c['coefficients']['C7']['real']),1e-4)
        c=self.contract(gamma_rad=0.)
        self.assertEqual(c['coefficients']['C7']['per_state_real'][1],0.)
        # A state with zero doublet fraction contributes zero even at a distinct mass.
        self.assertEqual(c['scalar_rows'][1]['doublet_fraction'],0.)

    def test_native_four_quark_zero_and_sign_flipped_ld(self):
        c=self.contract(gamma_rad=0.)
        n=self.native(550.);f=self.native(550.,flip=True)
        for name in ('C1','C2','C3','C4','C5','C6'):
            self.assertEqual(n['BEFORE'][name][1][0],0.)
            self.assertEqual(f['BEFORE'][name][1][0],0.)
        for key in ('C7','C8'):
            yy=c['scalar_rows'][0]['delta_'+key+'_YY']
            self.close(f['BEFORE'][key][1][0],2*yy-n['BEFORE'][key][1][0],'ld sign '+key)
            self.assertGreater(f['BEFORE'][key][1][0].real,0.)
        self.composition(n,'BEFORE')

    def diagnostic(self, shifts, split=False):
        # Explicit THDM API diagnostic; never accepted by production launcher.
        inp=self.local/'native_550.0_5.3_False.lha'
        args=['--mode','diagnostic','--model','THDM','--lha',str(inp),'--spectrum','true',
              '--contribution','BSM','--order','LO','--top-scheme','MSBAR_AT_QMATCH',
              '--qmatch','160','--qhad','4.8','--mt',str(self.mt),'--split',str(split).lower()]
        for key,value in zip(('c7','c8'),shifts):
            args += ['--'+key,str(value.real),'--'+key+'-imag',str(value.imag)]
        r,data=self.invoke(args,'THDM diagnostic split='+str(split))
        self.assertEqual(r.returncode,0,r.stderr)
        return data

    def test_double_count_trap_and_production_thdm_rejection(self):
        c=self.contract(gamma_rad=0.)
        shifts=[complex(c['coefficients'][k]['real']) for k in ('C7','C8')]
        data=self.diagnostic(shifts)
        for key,shift in zip(('C7','C8'),shifts):
            self.close(data['BEFORE'][key][1][0],shift,'native gamma0 '+key)
            self.close(data['AFTER'][key][1][0],2*shift,'double counting '+key)
        args=command(self.exe,c,4.8,self.up/'reproducibility/inputs/thdm_reference.lha')[1:]
        args[args.index('--model')+1]='THDM'
        r,_=self.invoke(args,'production THDM rejected')
        self.assertEqual(r.returncode,2);self.assertIn('double-count risk',r.stderr)

    def test_complex_api_running_linearity_and_scalar_patch_additivity(self):
        shifts=[complex(-.002,.006),complex(.003,-.004)]
        combined=self.diagnostic(shifts);split=self.diagnostic(shifts,True)
        separate=[self.diagnostic([shifts[0],0j]),self.diagnostic([0j,shifts[1]])]
        for key,shift in zip(('C7','C8'),shifts):
            self.close(combined['AFTER'][key][1][0]-combined['BEFORE'][key][1][0],shift,'complex matching '+key)
            self.assertGreater(abs(combined['AFTER'][key][1][1]-combined['BEFORE'][key][1][1]),1e-5)
            for scale in (0,1):
                delta=combined['AFTER'][key][1][scale]-combined['BEFORE'][key][1][scale]
                self.close(split['AFTER'][key][1][scale],combined['AFTER'][key][1][scale],'split additivity '+key)
                expect=sum(x['AFTER'][key][1][scale]-x['BEFORE'][key][1][scale] for x in separate)
                self.close(delta,expect,'separate dipole running '+key)
        self.composition(combined,'AFTER')
        for key in ('C1','C2','C3','C4','C5','C6'):
            self.assertEqual(combined['BEFORE'][key],combined['AFTER'][key])

    def test_runtime_scale_mass_scheme_and_contribution_guards(self):
        args=command(self.exe,self.contract(),4.8,self.up/'reproducibility/inputs/thdm_reference.lha')[1:]
        for flag,value in [('--qmatch','81'),('--mt','163'),('--top-scheme','POLE'),
                           ('--contribution','SM'),('--contribution','TOTAL'),('--order','NLO'),('--qhad','nan')]:
            bad=args.copy();bad[bad.index(flag)+1]=value
            r,_=self.invoke(bad,'guard '+flag+'='+value)
            self.assertEqual(r.returncode,2)


if __name__=='__main__':unittest.main()
