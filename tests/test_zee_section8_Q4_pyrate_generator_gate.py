"""Q4 input integrity, gauge group check and fail-closed generator contract.

Does not calculate or validate any full Zee beta function.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_section8_Q4_pyrate_generator_gate import (
    MODEL,EXPECTED,FIELD_Y,block,declared_terms,gauge_from_content,
    preflight,sha256,PYRATE_SHA,isolated_pyrate_command,isolated_environment,dependency_manifest
)

class TestQ4GeneratorInput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=MODEL.read_text()
    def mutated(self,original,replacement):
        self.assertIn(original,self.src)
        t=self.src.replace(original,replacement)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'mutated.model'
            p.write_text(t)
            return preflight(p)
    def test_current_exact_operator_inventory(self):
        d=preflight(MODEL)
        self.assertEqual(len(d['operators']['Yukawas']),7)
        self.assertEqual(len(d['operators']['QuarticTerms']),11)
        self.assertEqual(len(d['operators']['TrilinearTerms']),1)
        self.assertEqual(len(d['operators']['ScalarMasses']),4)
        self.assertEqual(d['couplings_quartic_real_components'],15)
        self.assertEqual(d['field_content_real_scalar_dof'],10)
        self.assertFalse(d['full_complex_beta_functions_verified'])
    def test_independent_gauge_coefficients(self):
        d=preflight(MODEL)
        self.assertEqual(d['gauge_1loop_SM_gprime'],['22/3','-3','-7'])
    def test_explicit_hypercharge_for_f_and_mu(self):
        self.assertEqual(2*FIELD_Y['LL']+FIELD_Y['chi'],0)
        self.assertEqual(FIELD_Y['Phi1']+FIELD_Y['Phi2']+FIELD_Y['chibar'],0)
    def test_input_hashed(self):
        self.assertEqual(preflight(MODEL)['input_SHA256'],sha256(MODEL))
        self.assertEqual(len(PYRATE_SHA),40)
    def test_reject_missing_f(self):
        with self.assertRaisesRegex(ValueError,'missing='):
            self.mutated('f: Eps[i,j] LL[i] LL[j] chi','')
    def test_reject_f_with_wrong_hypercharge(self):
        with self.assertRaisesRegex(ValueError,'nonzero Y'):
            self.mutated('f: Eps[i,j] LL[i] LL[j] chi',
                         'f: Eps[i,j] LL[i] LL[j] chibar')
    def test_reject_f_bad_SU2_structure(self):
        with self.assertRaisesRegex(ValueError,'antisymmetric SU2'):
            self.mutated('f: Eps[i,j] LL[i] LL[j] chi',
                         'f: LL[i] LL[j] chi')
    def test_reject_forbidden_lambda6_zero(self):
        with self.assertRaisesRegex(ValueError,'Forbidden'):
            self.mutated('g_U1Y: gp,','l6: 0,\n  g_U1Y: gp,')
    def test_reject_forbidden_GUT_g1(self):
        with self.assertRaisesRegex(ValueError,'Forbidden'):
            self.mutated('g_U1Y: gp,','g_U1Y: sqrt(5/3) * gp,')
    def test_reject_removed_portal(self):
        with self.assertRaisesRegex(ValueError,'missing='):
            self.mutated('l10: chibar chi Phi1bar[i] Phi2[i]','')
    def test_reject_wrong_singlet_charge(self):
        with self.assertRaisesRegex(ValueError,'Wrong hypercharges'):
            self.mutated('U1Y: 1, SU2L: 1','U1Y: 2, SU2L: 1')
    def test_reject_missing_trilinear_epsilon(self):
        with self.assertRaisesRegex(ValueError,'trilinear missing SU2'):
            self.mutated('muZee: Eps[i,j] Phi1[i] Phi2[j] chibar',
                         'muZee: Phi1[i] Phi2[j] chibar')
    def test_key4hep_pythonpath_removed_in_generator_environment(self):
        from unittest.mock import patch
        with patch.dict(os.environ,{'PYTHONPATH':'/bogus/key4hep/Particles.py',
                                    'PYTHONHOME':'/bogus/python',
                                    'PYTHONSTARTUP':'/bogus/start.py',
                                    'Q4_NATIVE_LIBRARY_TEST':'preserved'}):
            result=isolated_environment()
            for key in ('PYTHONPATH','PYTHONHOME','PYTHONSTARTUP'):
                self.assertNotIn(key,result)
            self.assertEqual(result['Q4_NATIVE_LIBRARY_TEST'],'preserved')
    def test_pinned_source_particles_takes_precedence_over_key4hep_collision(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            src=p/'pyrate';core=src/'src'/'Core'
            core.mkdir(parents=True)
            malicious=p/'key4hep';malicious.mkdir()
            (core/'Particles.py').write_text('ORIGIN="PINNED_PYRATE"\n')
            (malicious/'Particles.py').write_text('ORIGIN="KEY4HEP_COLLISION"\n')
            (src/'pyR@TE.py').write_text(
                'import sys,Particles\n'
                'from pathlib import Path\n'
                'Path(sys.argv[sys.argv.index("--Results")+1]).joinpath("origin.txt").write_text(Particles.ORIGIN)\n'
            )
            output=p/'out';output.mkdir()
            cmd=isolated_pyrate_command(src,src/'pyR@TE.py',MODEL,output)
            self.assertEqual(cmd[1],'-I')
            env=os.environ.copy()
            env['PYTHONPATH']=str(malicious)
            run=subprocess.run(cmd,cwd=src,env=env,capture_output=True,
                               text=True,timeout=20)
            self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            self.assertEqual((output/'origin.txt').read_text(),'PINNED_PYRATE')
    def test_missing_source_particles_fails_closed_not_using_key4hep(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);src=p/'pyrate';(src/'src'/'Core').mkdir(parents=True)
            malicious=p/'key4hep';malicious.mkdir()
            (malicious/'Particles.py').write_text('ORIGIN="KEY4HEP_COLLISION"\n')
            (src/'pyR@TE.py').write_text('print("UNSAFE_EXECUTION")\n')
            output=p/'out';output.mkdir()
            cmd=isolated_pyrate_command(src,src/'pyR@TE.py',MODEL,output)
            env=os.environ.copy();env['PYTHONPATH']=str(malicious)
            run=subprocess.run(cmd,cwd=src,env=env,capture_output=True,
                               text=True,timeout=20)
            self.assertNotEqual(run.returncode,0)
            self.assertIn('PyR@TE Particles import collision',run.stderr)
            self.assertNotIn('UNSAFE_EXECUTION',run.stdout)
    def test_parent_can_find_yaml_for_isolated_child(self):
        d=dependency_manifest(('yaml',))
        self.assertEqual(set(d),{'yaml'})
        self.assertTrue(Path(d['yaml']['origin']).is_file())
        self.assertTrue(Path(d['yaml']['search_root']).is_dir())

    def test_allowlisted_nonstandard_yaml_import_without_key4hep_particles(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'pyrate';core=src/'src/Core'
            core.mkdir(parents=True)
            packages=root/'nonstandard_dep_root'
            (packages/'yaml').mkdir(parents=True)
            (packages/'yaml/__init__.py').write_text(
                'ORIGIN="ALLOWLIST_YAML"\n')
            (core/'Particles.py').write_text('ORIGIN="PINNED_PYRATE"\n')
            (src/'pyR@TE.py').write_text(
                'import sys,Particles,yaml\n'
                'from pathlib import Path\n'
                'Path(sys.argv[sys.argv.index("--Results")+1]).joinpath("imports.txt").write_text('
                'yaml.ORIGIN + ":" + Particles.ORIGIN)\n')
            bad=root/'key4hep'
            bad.mkdir()
            (bad/'Particles.py').write_text('ORIGIN="BAD_KEY4HEP"\n')
            out=root/'output';out.mkdir()
            deps={'yaml':{'origin':str(packages/'yaml/__init__.py'),
                          'search_root':str(packages)}}
            cmd=isolated_pyrate_command(src,src/'pyR@TE.py',MODEL,out,deps)
            env=os.environ.copy();env['PYTHONPATH']=str(bad)
            proc=subprocess.run(cmd,cwd=src,capture_output=True,
                                text=True,env=env,timeout=20)
            self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
            self.assertEqual((out/'imports.txt').read_text(),
                             'ALLOWLIST_YAML:PINNED_PYRATE')
            self.assertIn('Q4_IMPORT_PROVENANCE',proc.stdout)

    def test_dependency_origin_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/'pyrate';core=src/'src/Core'
            core.mkdir(parents=True)
            packages=root/'external';(packages/'yaml').mkdir(parents=True)
            (packages/'yaml/__init__.py').write_text('ORIGIN="REAL"\n')
            (core/'Particles.py').write_text('ORIGIN="PINNED"\n')
            (src/'pyR@TE.py').write_text('print("SHOULD_NOT_EXECUTE")\n')
            out=root/'output';out.mkdir()
            deps={'yaml':{'origin':str(packages/'yaml/MISSING.py'),
                          'search_root':str(packages)}}
            cmd=isolated_pyrate_command(src,src/'pyR@TE.py',MODEL,out,deps)
            proc=subprocess.run(cmd,cwd=src,capture_output=True,
                                text=True,timeout=20,env=isolated_environment())
            self.assertNotEqual(proc.returncode,0)
            self.assertIn('dependency yaml import mismatch',proc.stderr)
            self.assertNotIn('SHOULD_NOT_EXECUTE',proc.stdout)

    def test_preflight_only_does_not_claim_betas(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'q4_out'
            p=subprocess.run([sys.executable,
                str(Path(__file__).resolve().parents[1]/'scripts/zee_section8_Q4_pyrate_generator_gate.py'),
                '--model',str(MODEL),'--output-dir',str(target),'--preflight-only'],
                text=True,capture_output=True,timeout=20)
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            r=json.loads((target/'summary.json').read_text())
            self.assertEqual(r['result'],'PREFLIGHT_ONLY_GENERATOR_NOT_EXECUTED')
            self.assertFalse(r['full_Zee_RGE_calculation_accepted'])
            self.assertNotIn('generator',r)
            p=subprocess.run([sys.executable,
                str(Path(__file__).resolve().parents[1]/'scripts/zee_section8_Q4_pyrate_generator_gate.py'),
                '--model',str(MODEL),'--output-dir',str(target),'--preflight-only'],
                text=True,capture_output=True,timeout=20)
            self.assertNotEqual(p.returncode,0)
            self.assertIn('Refusing to overwrite',p.stderr)

if __name__=='__main__':unittest.main()
