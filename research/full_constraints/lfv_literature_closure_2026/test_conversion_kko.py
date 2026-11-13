import cmath
import math
import unittest
from .conversion_kko import *

class TestConversion(unittest.TestCase):
    def test_dipole_only_al_heeck_thapa(self):
        self.assertAlmostEqual(dipole_ratio('Al27'),.0027,delta=.0001)
        d=conversion_rate('Al27',cL=1e-8+2e-8j,cR=0)
        self.assertAlmostEqual(d['conversion_ratio']/radiative_br(1e-8+2e-8j,0),dipole_ratio('Al27'),places=12)
        self.assertAlmostEqual(d['conversion_ratio']/radiative_br(1e-8+2e-8j,0),.00266,delta=.0001)

    def test_kkotargets(self):
        self.assertAlmostEqual(TARGETS['Au197'].D,.189)
        self.assertGreater(dipole_ratio('Au197'),dipole_ratio('Al27'))
        self.assertTrue(all(conversion_rate(target,cR=1e-8)['conversion_ratio']>0
                            for target in TARGETS))

    def test_photon_valence_neutron_zero(self):
        for a in [1e-9,1e-9+3e-9j]:
            p,n=vector_nucleon(photon_monopole_vector(a))
            self.assertAlmostEqual(abs(n),0,delta=1e-23)
            self.assertAlmostEqual(abs(p + 8*math.pi*ALPHA0*a),0,delta=1e-23)

    def test_generic_neutron_vector_retained(self):
        # A Z-induced neutral vector contribution is physically allowed;
        # the restricted 2022 Eq41 omits it only for a photon-only vector.
        d=conversion_rate('Au197',gLV={'u':1e-8,'d':-2e-8})
        self.assertGreater(d['conversion_ratio'],0)
        self.assertAlmostEqual(d['partial_norm_right'],0)

    def test_scalar_pn_not_swapped_and_heavy_quark(self):
        fs={'p':{'u':.02,'d':.04,'s':.045},'n':{'u':.018,'d':.045,'s':.045}}
        masses={'u':.0022,'d':.0047,'s':.096,'c':1.27,'b':4.18,'t':173.}
        p,n=scalar_nucleon({'u':.0022},fs,masses)
        self.assertAlmostEqual(p/MP,.02)
        self.assertAlmostEqual(n/MN,.018)
        p,n=scalar_nucleon({'c':1.27},fs,masses)
        self.assertAlmostEqual(p/MP,(2/27)*(1-sum(fs['p'].values())))
        self.assertAlmostEqual(n/MN,(2/27)*(1-sum(fs['n'].values())))
        a=conversion_rate('Au197',gLS={'u':.0022},f_light=fs,masses=masses)
        self.assertGreater(a['conversion_ratio'],0)

    def test_complex_interference_and_chirality(self):
        c=1e-8
        lone=conversion_rate('Al27',cR=c)['conversion_ratio']
        # Construct vector-proton amplitude exactly opposite to cR dipole
        v=-(-math.sqrt(4*math.pi*ALPHA0)/(16*math.pi**2)*c*TARGETS['Al27'].D)/TARGETS['Al27'].Vp
        cancelled=conversion_rate('Al27',cR=c,gLV={'u':v/2})['conversion_ratio']
        # u-only gives p=2u,n=u, so Vn must also be cancelled; make pure proton.
        cancelled=conversion_rate('Al27',cR=c,gLV={'u':2*v/3,'d':-v/3})['conversion_ratio']
        self.assertLess(cancelled,lone*1e-24)
        same=conversion_rate('Al27',cR=c,gLV={'u':2*v/3,'d':-v/3})
        phase=cmath.exp(1j*.37)
        rotated=conversion_rate('Al27',cR=c*phase,gLV={'u':2*v/3*phase,'d':-v/3*phase})
        self.assertAlmostEqual(same['conversion_ratio'],rotated['conversion_ratio'],delta=1e-35)
        l=conversion_rate('Al27',cR=c)['conversion_ratio']
        r=conversion_rate('Al27',cL=c)['conversion_ratio']
        both=conversion_rate('Al27',cL=c,cR=c)['conversion_ratio']
        self.assertAlmostEqual(both,l+r)

    def test_fail_closed(self):
        with self.assertRaises(ValueError):conversion_rate('Al27',gLS={'u':1e-8})
        with self.assertRaises(ValueError):conversion_rate('Al27',gLV={'bad':1})
        with self.assertRaises(ValueError):conversion_rate('Al27',cL=float('nan'))
        self.assertIsNone(conversion_rate('Al27',cR=1e-8)['LFV_exclusion'])

if __name__=='__main__': unittest.main()
