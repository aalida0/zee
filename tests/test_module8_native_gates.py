"""Gate falsifiers and analytical controls; synthetic settings certify no rates."""
import math
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from module8.partonic_checks import partonic_pb
from module8.real_run_validation import validate_settings,lha_values,validate_sources

class NativeGateTests(unittest.TestCase):
    def test_partonic_threshold_and_mixing_controls(self):
        for gamma in (0.,math.pi/2,-math.pi/2):
            self.assertEqual(partonic_pb(2000.**2,300.,700.,gamma,2),0.)
        self.assertEqual(partonic_pb(1000.**2,300.,700.,1.089,2),0.)
        self.assertEqual(partonic_pb(999.**2,300.,700.,1.089,2),0.)
        base=partonic_pb(2000.**2,300.,700.,1.089,2)
        self.assertGreater(base,0.)
        self.assertAlmostEqual(partonic_pb(2000.**2,300.,700.,-.4,2)/base,
                               (math.sin(.8)/math.sin(2*1.089))**2,places=14)
        with self.assertRaises(ValueError):partonic_pb(2000.**2,300.,700.,1.089,6)

    def test_lha_duplicates_rejected(self):
        with self.assertRaises(ValueError):lha_values('BLOCK MASS\n 37 300\n 37 350\n')
        with self.assertRaises(ValueError):lha_values('DECAY 37 0\nDECAY 37 1\n')

    def test_energy_pdf_scale_and_cut_falsifiers(self):
        text='''6800 = ebeam1
6800 = ebeam2
1 = lpp1
1 = lpp2
0 = dsqrt_shat
-1 = dsqrt_shatmax
700 = scale
700 = dsqrt_q2fact1
700 = dsqrt_q2fact2
263000 = lhaid
0 = ptheavy
lhapdf = pdlabel
True = fixed_ren_scale
True = fixed_fac_scale
False = use_syst
none = systematics_program
5000 = nevents
{} = pt_min_pdg
'''
        validate_settings(text)
        for before,after in [('1 = lpp1','-1 = lpp1'),('0 = dsqrt_shat','900 = dsqrt_shat'),('6800 = ebeam1','7000 = ebeam1'),('263000','263001'),('700 = scale','350 = scale'),('lhapdf = pdlabel','nn23lo1 = pdlabel'),('True = fixed_fac_scale','False = fixed_fac_scale'),('5000 = nevents','1 = nevents'),('{} = pt_min_pdg','{6:20} = pt_min_pdg')]:
            with self.subTest(change=after),self.assertRaises(ValueError):validate_settings(text.replace(before,after))
        with self.assertRaises(ValueError):validate_settings(text+'6800 = ebeam1\n')
        with self.assertRaises(ValueError):validate_settings(text+'cuts.f = custom_fcts\n')

    def test_modified_executable_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp);sources={};receipt={}
            for part,key in [('Source','source_tree_sha256'),('SubProcesses','matrix_tree_sha256')]:
                (folder/part).mkdir();(folder/part/'matrix.f').write_text('original amplitude')
                sources[part]={'matrix.f':hashlib.sha256(b'original amplitude').hexdigest()}
                receipt[key]=hashlib.sha256(json.dumps(sources[part],sort_keys=True,separators=(',',':')).encode()).hexdigest()
            validate_sources(folder,sources,receipt)
            (folder/'SubProcesses/matrix.f').write_text('modified amplitude')
            with self.assertRaisesRegex(ValueError,'Executable source changed'):
                validate_sources(folder,sources,receipt)

if __name__=='__main__':unittest.main()
