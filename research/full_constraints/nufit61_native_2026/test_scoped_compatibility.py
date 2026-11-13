"""Synthetic/fail-closed tests. Optional authentic archive checks via env var."""
import hashlib
import itertools
import lzma
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from . import scoped_compatibility as scoped
from .verify import SECTIONS


AXES = {'T12':(.2,.4),'T13':(.01,.03),'T23':(.4,.6),
        'DMS':(-5.,-4.),'DMA':(2.4,2.6),'DCP':(-180.,0.,180.)}


def generate(ordering='NO', offset=0.):
    axes = dict(AXES)
    if ordering=='IO':
        axes['DMA']=(-2.6,-2.4)
    rows = ['### '+('Normal' if ordering=='NO' else 'Inverted')+' Ordering']
    for section in SECTIONS:
        tokens = section.split('/')
        rows.append('# '+section+' projection')
        for coords in itertools.product(*(axes[t] for t in tokens)):
            cost = 0.
            for token, value in zip(tokens, coords):
                if token=='T12': cost += (value-.2)*100
                if token=='T23': cost += (value-.4)*100
                if token=='DCP': cost += abs(value)/180*0.1
                if token=='DMA': cost += (abs(value)-2.4)*0.1
            rows.append(' '.join(map(str,(*coords,offset+cost))))
    return ('\n'.join(rows)+'\n').encode()


class ScopedCompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)
        self.obs={'ordering':'NO','sin2_theta12':.2,'sin2_theta13':.01,
                  'sin2_theta23':.4,'dm21_eV2':1e-5,'dm3l_eV2':.0024,
                  'delta_rad':0.}

    def make(self, ordering='NO', offset=0., broken=False):
        filename='v61.release-TByes-'+ordering+'.txt.xz'
        content=generate(ordering, offset)
        if broken:
            content=content.replace(b'# T12 projection\n0.2 0.0\n',
                                    b'# T12 projection\n0.2 0.0\n0.2 0.0\n')
        raw=lzma.compress(content)
        (self.path/filename).write_bytes(raw)
        return filename, hashlib.sha256(raw).hexdigest()

    def test_synthetic_pass_fail_unknown_and_separate_components(self):
        fn, sha = self.make()
        with patch.dict(scoped.FILES, {fn:('NO','IC24 with SK atmospheric data',sha,0.)}):
            f=scoped.NuFIT61Compatibility(self.path,'NO')
            r=f.evaluate(self.obs)
            self.assertEqual(r['status'],'SCOPED_PASS')
            self.assertEqual(len(r['sections']),7)
            self.assertIsNone(r['global_zee_acceptance'])
            self.assertFalse(r['projection_sums_used'])
            mod=dict(self.obs,sin2_theta12=.4)
            bad=f.evaluate(mod)
            self.assertEqual(bad['status'],'SCOPED_FAIL')
            self.assertEqual(bad['sections']['T12']['status'],'FAIL')
            unknown=f.evaluate(dict(self.obs,sin2_theta13=.5))
            self.assertEqual(unknown['status'],'SCOPED_UNKNOWN')
            self.assertEqual(unknown['sections']['T13']['status'],'UNKNOWN')
            self.assertEqual(f.evaluate(dict(self.obs,dm21_eV2=0.))['status'],'SCOPED_UNKNOWN')
            self.assertEqual(f.evaluate(dict(self.obs,delta_rad=2*math.pi))['status'],'SCOPED_PASS')
            self.assertEqual(f.evaluate(dict(self.obs,delta_rad=-2*math.pi))['status'],'SCOPED_PASS')
            with self.assertRaises(ValueError): f.evaluate(dict(self.obs,ordering='IO'))
            with self.assertRaises(ValueError): f.evaluate(dict(self.obs,sin2_theta23=1.1))
            with self.assertRaises(ValueError): f.evaluate(dict(self.obs,sin2_theta23=float('nan')))
            with self.assertRaises(ValueError): f.evaluate(dict(self.obs,sin2_theta23=True))

    def test_io_local_threshold_and_absolute_ordering_offset(self):
        fn, sha = self.make('IO', 5.908214)
        obs=dict(self.obs,ordering='IO',dm3l_eV2=-.0024)
        with patch.dict(scoped.FILES, {fn:('IO','IC24 with SK atmospheric data',sha,5.908214)}):
            f=scoped.NuFIT61Compatibility(self.path,'IO')
            r=f.evaluate(obs)
            self.assertEqual(r['status'],'SCOPED_PASS')
            self.assertAlmostEqual(r['sections']['T23/DMA/DCP']['absolute_delta_chi2'],5.908214)
            self.assertAlmostEqual(r['sections']['T23/DMA/DCP']['ordering_local_delta_chi2'],0.)

    def test_bad_hash_and_shape_rejected(self):
        fn, sha = self.make()
        with patch.dict(scoped.FILES,{fn:('NO','IC24 with SK atmospheric data','0'*64,0.)}):
            with self.assertRaisesRegex(ValueError,'SHA256'):
                scoped.NuFIT61Compatibility(self.path,'NO')
        fn,sha = self.make(broken=True)
        with patch.dict(scoped.FILES,{fn:('NO','IC24 with SK atmospheric data',sha,0.)}):
            with self.assertRaisesRegex(ValueError,'grid'):
                scoped.NuFIT61Compatibility(self.path,'NO')

    @unittest.skipUnless(os.getenv('NUFIT61_ARCHIVE_DIR'),'optional official archives not provided')
    def test_native_archive_reference_points(self):
        archive_dir=os.environ['NUFIT61_ARCHIVE_DIR']
        for ordering in ('NO','IO'):
            f=scoped.NuFIT61Compatibility(archive_dir,ordering)
            obs={'ordering':ordering,'sin2_theta12':.3081 if ordering=='NO' else .308,
                 'sin2_theta13':.0225 if ordering=='NO' else .0226,
                 'sin2_theta23':.4701 if ordering=='NO' else .5499,
                 'dm21_eV2':7.53e-5,
                 'dm3l_eV2':.0025102 if ordering=='NO' else -.0024848,
                 'delta_rad':math.pi*(1.17 if ordering=='NO' else 1.53)}
            r=f.evaluate(obs)
            self.assertEqual(r['status'],'SCOPED_PASS')
            absolute = r['sections']['T23/DMA/DCP']['absolute_delta_chi2']
            self.assertAlmostEqual(absolute,
                0.004925922925127852 if ordering=='NO' else 5.916879105951998,
                places=9)


if __name__=='__main__':unittest.main()
