"""Synthetic format/interpolation regressions; no synthetic data are official."""
import copy
import hashlib
import itertools
import json
import lzma
import math
from pathlib import Path
import tempfile
import unittest
from module2.data import compare
from module2.interface import evaluate, validate_schema
from module2.nufit import read_projection, SECTIONS
from test_module2_interface import example

EVIDENCE = {}


def dataset(path, raw, ordering='NO', section='T23/DMA/DCP'):
    return {'schema_version':'1.0.0','dataset_id':'SYNTHETIC_FORMAT_TEST',
            'source':{'version':'NuFIT 6.1 (2025)','url':'https://www.nu-fit.org/?q=node%2F309',
                      'selection':'IC23 without SK atmospheric data'},
            'ordering':ordering,'likelihood':'PROFILED_DELTA_CHI2',
            'archive':{'path':str(path),'sha256':hashlib.sha256(raw).hexdigest()},
            'section':section,'assumptions':['Synthetic format regression; no official data or experimental inference.']}


class ProfileAudit(unittest.TestCase):
    def test_all_22_sections_native_axes_and_preserved_offsets(self):
        for ordering in ('NO','IO'):
            axes={'T12':[.2,.4],'T13':[.01,.03],'T23':[.4,.6],
                  'DMA':[2.4,2.6] if ordering=='NO' else [-2.6,-2.4],
                  'DMS':[-5.,-4.],'DCP':[0.,180.,360.]}
            lines=[]
            for section in SECTIONS:
                lines.append('# '+section)
                for point in reversed(list(itertools.product(*(axes[t] for t in section.split('/'))))):
                    # Multi-affine in nonphase coordinates and piecewise linear
                    # periodic in phase; positive offset deliberately preserved.
                    coords=[(v/180 if v<=180 else (360-v)/180) if t=='DCP' else v
                            for t,v in zip(section.split('/'),point)]
                    value=40+sum((i+1)*x for i,x in enumerate(coords))+math.prod(coords)
                    lines.append(' '.join(map(str,(*point,value))))
            plain=('\n'.join(lines)+'\n').encode()
            with tempfile.TemporaryDirectory() as tmp:
                for compressed in (False,True):
                    raw=lzma.compress(plain) if compressed else plain
                    path=Path(tmp)/'synthetic.xz';path.write_bytes(raw)
                    obs={'ordering':ordering,'sin2_theta12':.3,'sin2_theta13':.02,'sin2_theta23':.5,
                         'dm21_eV2':10**-4.5,'dm3l_eV2':.0025 if ordering=='NO' else -.0025,
                         'delta_rad':math.pi/2}
                    native={'T12':.3,'T13':.02,'T23':.5,'DMA':2.5 if ordering=='NO' else -2.5,'DMS':-4.5,'DCP':.5}
                    for section in SECTIONS:
                        d=dataset(path,raw,ordering,section);validate_schema(d,'dataset.schema.json')
                        r=compare(obs,d)
                        coords=[native[t] for t in section.split('/')]
                        expected=40+sum((i+1)*x for i,x in enumerate(coords))+math.prod(coords)
                        self.assertAlmostEqual(r['delta_chi2'],expected,places=11)
                        self.assertFalse(r['minimum_subtracted']);self.assertFalse(r['joint_likelihood'])
                        self.assertEqual(r['source_authentication'],'DECLARED_BY_INPUT_HASH_VERIFIED')
                    d=dataset(path,raw,ordering,'DCP')
                    self.assertEqual(compare(dict(obs,delta_rad=math.pi/2+4*math.pi),d)['delta_chi2'],compare(obs,d)['delta_chi2'])
                    self.assertEqual(compare(dict(obs,delta_rad=None),d)['status'],'UNKNOWN')
        EVIDENCE['synthetic_projection_sections_tested']=22
        EVIDENCE['native_projection_format_tests']='PASS_SYNTHETIC_ONLY'

    def test_fail_closed_hash_shape_source_and_domain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'grid.txt'
            raw=b'# T13/T12\n.01 .2 7\n.01 .4 8\n.03 .2 9\n.03 .4 10\n'
            path.write_bytes(raw);d=dataset(path,raw,section='T13/T12')
            obs={'ordering':'NO','sin2_theta13':.02,'sin2_theta12':.3}
            self.assertEqual(compare(obs,d)['delta_chi2'],8.5)
            self.assertEqual(compare(dict(obs,sin2_theta13=.04),d)['status'],'UNKNOWN')
            bad=copy.deepcopy(d);bad['archive']['sha256']='0'*64
            with self.assertRaises(ValueError):compare(obs,bad)
            for key,value in [('version','NuFIT 6.2 (2099)'),('selection','IC19 without SK atmospheric data'),('url','https://example.com/grid')]:
                bad=copy.deepcopy(d);bad['source'][key]=value
                with self.assertRaises(ValueError):compare(obs,bad)
            with self.assertRaises(ValueError): compare(dict(obs,ordering='IO'),d)
            for malformed in [raw+raw,raw.replace(b'.03 .4 10\n',b''),raw.replace(b'.03 .4 10',b'.01 .2 11'),
                              raw.replace(b'.03 .4 10',b'.03 .4 nan'),b'# DMA\n2.4 0\n']:
                path.write_bytes(malformed)
                with self.assertRaises(ValueError):read_projection(path,hashlib.sha256(malformed).hexdigest(),'T13/T12')

    def test_projection_through_JSON_API_keeps_Gaussian_separate(self):
        raw=b'# T13/T12\n.01 .2 7\n.01 .4 8\n.03 .2 9\n.03 .4 10\n'
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'grid';path.write_bytes(raw)
            x=example();x['dataset']=dataset(path,raw,section='T13/T12')
            r=evaluate(x)
            self.assertEqual(r['comparison']['likelihood'],'PROFILED_DELTA_CHI2')
            self.assertEqual(r['comparison']['combined_with_other_data'],False)
            self.assertIsNone(r['global_zee_acceptance'])
            x['dataset']['gaussian_chi2']=3
            with self.assertRaises(ValueError):evaluate(x)


if __name__=='__main__':unittest.main()
