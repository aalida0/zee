"""D6 falsifiers use actual retained native outputs when available."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from module8.d6_production import LOCAL, PROCESSES, parameter_card
from module8.d6_generator_validate import validate_one
from module8.real_run_validation import lha_values
from module8.run_capture import sha

class ProcessTests(unittest.TestCase):
    def test_full_tree_scope_and_stable_5FS_mapping(self):
        self.assertEqual(len(PROCESSES['F']),4)
        self.assertEqual(len(set(PROCESSES['F'])),4)
        for line in PROCESSES['F']:
            self.assertNotIn('> z >',line)
            self.assertIn('QCD=0 QED=2 HIG=0 HIW=0',line)
        if not (LOCAL/'cards/d2_NO_source_baseline_H2.dat').exists():self.skipTest('Native input absent')
        values=lha_values(parameter_card('source'))
        for code in (1,2,3,4,5):self.assertEqual(values['MASS',(code,)],0.)
        for code in (6,37,9000037):self.assertEqual(values['DECAY',(code,)],0.)
        self.assertEqual(values['MASS',(6,)],172.4)

    def test_evolved_scheme_changes_only_quark_yukawas(self):
        if not (LOCAL/'cards/d2_NO_source_baseline_H2.dat').exists():self.skipTest('Native input absent')
        import math
        from module7.d4_inputs import yukawa_masses,ckm
        from module8.d6_evolved import evolved_card
        base=lha_values(parameter_card('source'))
        for q in (350.,1400.):
            got=lha_values(evolved_card('source',q));m=yukawa_masses(q);v=246.21965;b=1.394;V=ckm().conj().T
            for key,value in base.items():
                if key[0] not in ('YU','IMYU','YD','IMYD'):self.assertEqual(got[key],value)
            for i in range(3):
                for j in range(3):
                    yu=math.sqrt(2)*m[i]/(v*math.sin(b)) if i==j else 0.
                    yd=math.sqrt(2)*m[3+i]*V[i,j]/(v*math.cos(b))
                    self.assertAlmostEqual(got['YU',(i+1,j+1)],yu,places=14)
                    self.assertAlmostEqual(got['YD',(i+1,j+1)],yd.real,places=14)
                    self.assertAlmostEqual(got['IMYD',(i+1,j+1)],yd.imag,places=14)

class NativeFalsifiers(unittest.TestCase):
    def setUp(self):
        self.original=LOCAL/'d6_receipts/d6_A_source_700_700'
        if not (self.original/'receipt.json').exists():self.skipTest('Executed native evidence absent')
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)/'capture';shutil.copytree(self.original,self.folder)
        self.path=self.folder/'receipt.json';self.r=json.loads(self.path.read_text())
    def save(self):self.path.write_text(json.dumps(self.r))
    def rebind(self,name):
        self.r['artifacts_sha256'][name]=sha(self.folder/name)
        for key in self.r['input_sha256']:
            if key.endswith('/Cards/'+name):self.r['input_sha256'][key]=sha(self.folder/name)
        self.save()
    def test_real_capture_passes(self):
        self.assertEqual(validate_one(self.path)['sigma_LO_pb'],.0045246)
    def test_scale_and_scheme_tampering(self):
        for key,value in [('muR',350.),('yukawa_scheme','unspecified'),('returncode',1)]:
            old=self.r[key];self.r[key]=value;self.save()
            with self.subTest(key=key),self.assertRaises(ValueError):validate_one(self.path)
            self.r[key]=old
    def test_missing_beam_order_even_with_updated_hash(self):
        p=self.folder/'proc_card_mg5.dat';p.write_text(p.read_text().replace(PROCESSES['A'][-1],''));self.rebind(p.name)
        with self.assertRaisesRegex(ValueError,'charges/beam'):validate_one(self.path)
    def test_seed_even_with_updated_hash(self):
        p=self.folder/'run_card.dat';p.write_text(p.read_text().replace('4154 = iseed','4155 = iseed'));self.rebind(p.name)
        with self.assertRaisesRegex(ValueError,'Seed'):validate_one(self.path)
    def test_nonfinite_native_result_even_with_updated_hash(self):
        p=self.folder/'results.dat';lines=p.read_text().splitlines();v=lines[0].split();v[9]='nan';lines[0]=' '.join(v);p.write_text('\n'.join(lines)+'\n');self.rebind(p.name)
        with self.assertRaisesRegex(ValueError,'integration'):validate_one(self.path)
    def test_empty_executable_manifest_even_with_updated_hash(self):
        p=self.folder/'sources.json';s=json.loads(p.read_text());s['Source']={};p.write_text(json.dumps(s));self.r['source_tree_sha256']=hashlib.sha256(b'{}').hexdigest();self.rebind(p.name)
        with self.assertRaisesRegex(ValueError,'Empty executable'):validate_one(self.path)
    def test_compiled_snapshot_integrity(self):
        relative='Source/vector.inc';p=self.folder/'compiled_sources'/relative
        p.parent.mkdir(parents=True);p.write_bytes((LOCAL/'d6_A'/relative).read_bytes())
        self.r['compiled_source_snapshot_sha256']={relative:sha(p)};self.save()
        p.write_text(p.read_text()+'! changed\n')
        with self.assertRaisesRegex(ValueError,'snapshot changed'):validate_one(self.path)
    def test_changed_width_even_with_updated_hash(self):
        p=self.folder/'param_card.dat';p.write_text(p.read_text().replace('DECAY 6 0.0','DECAY 6 1.0'));self.rebind(p.name)
        with self.assertRaisesRegex(ValueError,'parameter'):validate_one(self.path)

if __name__=='__main__':unittest.main()
