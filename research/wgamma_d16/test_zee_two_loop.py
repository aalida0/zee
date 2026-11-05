"""Focused new common-class, F-subgraph and guarded-combination checks."""
import copy
import unittest
import mpmath as mp
import numpy as np
from module3.core import vertices
from module4.couplings import quarks
from .external_2hdm_hw_override import REFERENCE, ML, load_reference
from .neutral_fermion_z import z_kernels, z_kernels_log_radial, ledger
from .f_current_probe import probe
from .test_zee_mixed_hz import fixture
from .zee_two_loop import evaluate, witness, add
from .w_outer_reduction import reduce_denominators


class NewTwoLoopClasses(unittest.TestCase):
    def test_common_masters_direct_radial_reference_and_light_high_precision(self):
        ref=load_reference(REFERENCE)
        for z,r in ((.1,.3),(2.,.7),(.3,1.)):
            fast=z_kernels(z,r);direct=z_kernels_log_radial(z,r)
            np.testing.assert_allclose([x[0] for x in fast],[x[0] for x in direct],rtol=3e-10)
            if r!=1.:
                np.testing.assert_allclose([x[0] for x in fast],[ref.f4(z,z/r),ref.f3(z,z/r)],rtol=3e-10)
        # At electron-like ratios upstream float dilogs lose ~5e-7 absolute.
        # Validate against 45-digit 1D parameters rather than loosen to that.
        with mp.workdps(45):
            z,r=mp.mpf('1e-11'),mp.mpf('.4')
            def base(a,even):
                def fn(t):
                    u=t*(1-t)
                    return (1-2*u if even else 1)*mp.log(a/u)/(a-u)
                return 2*mp.quad(fn,[0,mp.mpf('1e-10'),mp.mpf('1e-5'),.1,.5])
            for index,even in enumerate((True,False)):
                precise=(base(z,even)-base(z/r,even))/(r-1)
                value,error=z_kernels(float(z),float(r))[index]
                self.assertLess(abs(float(precise)-value),max(error,3e-9))

    def test_common_signed_complex_L_R_at_arbitrary_charged_mixing(self):
        ref=load_reference(REFERENCE);p,D=fixture()
        fm={'up':.0022,'down':.0047,'strange':.095,'charm':1.27,'bottom':4.18,
            'top':172.5,'electron':ML[0],'muon':ML[1],'tau':ML[2]}
        mw,mz=80.379,91.1876;sw2=1-(mw/mz)**2;sw,cw=np.sqrt(sw2),mw/mz
        al=(2*mw/p['v'])**2*sw2/(4*np.pi);vze=(-.5+2*sw2)/(sw*cw)
        out=ledger(D,p,ML,mw,mz,fm,1,0)
        self.assertEqual(len(out),27)
        for name,(C,M) in vertices(D,p,ML).items():
            for f,Q,t3,nc in [('top',2/3,.5,3),('bottom',-1/3,-.5,3),('tau',-1,-.5,1)]:
                Y=C[2,2] if f=='tau' else quarks(fm[f],f,p)[name]
                vzf=(t3-2*Q*sw2)/(sw*cw)
                z,y=(fm[f]/M)**2,(fm[f]/mz)**2
                eff=Y.real*ref.f4(z,y)+1j*Y.imag*ref.f3(z,y)
                expected=-nc*al*Q*vzf*vze*fm[f]/(64*np.pi**3*ML[1]*M*M)*np.array([C[0,1]*eff,C[1,0].conjugate()*eff.conjugate()])
                np.testing.assert_allclose(out[name+'_'+f+'_Z_gamma']['C_LR'],expected,rtol=3e-8,atol=1e-24)
        with self.assertRaises(ValueError):
            ledger(D,p,ML,mw,mz,dict(fm,electron=0.),1,0)

    def test_F_spurion_massless_chirality_and_surviving_UV_subloop(self):
        F=np.array([[0,.02+.03j,-.01j],[-.02-.03j,0,.04],[.01j,-.04,0]])
        result=probe(F)
        self.assertEqual(result['same_projector_massless_chain_norm'],0.)
        self.assertGreater(result['opposite_projector_massless_chain_norm'],.1)
        self.assertEqual(result['subloop']['pole'],-1.)
        self.assertAlmostEqual(result['subloop']['finite'],4*np.log(2)-2,places=12)
        self.assertIsNone(result['full_F_dependent_C_LR'])
        self.assertGreater(abs(result['F_dagger_F'][0,1]),1e-5)
        P=np.diag(np.exp(1j*np.array([.3,-.7,.8])))
        np.testing.assert_allclose(probe(P@F@P)['F_dagger_F'],P.conj().T@result['F_dagger_F']@P,rtol=3e-15,atol=1e-18)

    def test_actual_NO_IO_coherent_once_with_unavailable_full_amplitude(self):
        signs=[]
        for order in ('NO','IO'):
            result=evaluate(witness(order))
            self.assertFalse(result['acceptance'])
            self.assertEqual(result['gates']['input_neutrino_forward'],'PASS')
            for c in result['channels'].values():
                rows=c['ledger'];self.assertEqual(len(rows),70)
                self.assertEqual(sum(r['loop_order']==1 for r in rows.values()),7)
                np.testing.assert_allclose(sum((r['C_LR'] for r in rows.values()),np.zeros(2,complex)),c['included_only_C_LR'],rtol=2e-15,atol=1e-30)
                for row in rows.values():
                    np.testing.assert_array_equal(row['K2_LR'],-row['C_LR'].conjugate())
                self.assertIsNone(c['full_C_LR']);self.assertIsNone(c['full_BR'])
                self.assertTrue(all(r['C_LR'] is None for r in c['unavailable_classes'].values()))
                signs.append(np.sign(c['one_two_loop_interference_norm2']))
        self.assertIn(-1,signs);self.assertIn(1,signs)

    def test_duplicate_and_source_mismatch_rejected(self):
        rows={};add(rows,'x',[1j,2.],0.,2,'test','test')
        with self.assertRaises(ValueError):
            add(rows,'x',[0.,0.],0.,2,'test','test')
        data=copy.deepcopy(witness('NO'))
        data['module2_output']['provenance']['input_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'provenance'):
            evaluate(data)

    def test_actual_W_parent_Taylor_reduction_retains_sunset_denominators(self):
        result=reduce_denominators()
        self.assertEqual(result['symbolic_residual'],'0')
        self.assertIn('v2',result['sunset_partial_fractions']['p1_q1'])
        self.assertIn('mW2',result['sunset_partial_fractions']['p1_q1'])


if __name__=='__main__':
    unittest.main()
