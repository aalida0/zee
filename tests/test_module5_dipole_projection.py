"""Independent numerator reduction and diagram-level LO projection audit."""
import math
from pathlib import Path
import sys
import unittest
import mpmath as mp
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT))
from zee_module5_dipole_projection import coefficients,diagrams
from module5.bsgamma_lo import compute,loop_functions
import test_module5_native_amplitudes as native_algebra


class LoopNumeratorTests(unittest.TestCase):
    def test_on_shell_numerators_and_gordon_projection(self):
        algebra=native_algebra.LocalDipoleAmplitudeAlgebraTests();algebra.setUp()
        g=algebra.g;pr=algebra.pr;pl=algebra.pl;sigma=algebra.sigma
        metric=np.array([1,-1,-1,-1])
        def slash(p):return sum(p[m]*metric[m]*g[m] for m in range(4))
        mb=1.3;mt=7.1;x=.23;y=.31;z=1-x-y
        p=np.array([mb,0,0,0]);s=np.array([mb/2,.6*mb/2,0,.8*mb/2]);q=p-s
        left=slash(s);right=slash(p)+mb*np.eye(4)
        at=(1-x)*s-y*p;ab=-x*s+(1-y)*p
        a=x*p+y*s;v=p+s-2*a
        maximum=0.
        for m in range(4):
            cases=[
                (pr@(slash(at)+mt*np.eye(4))@g[m]@(slash(ab)+mt*np.eye(4))@pr,
                 mt*((-2*y*p[m]-2*x*s[m])*pr+mb*g[m]@pl)),
                (pr@(slash(at)+mt*np.eye(4))@g[m]@(slash(ab)+mt*np.eye(4))@pl,
                 2*mb*(x*y*s[m]-y*(1-y)*p[m])*pr+(mt**2+mb**2*y*z)*g[m]@pl),
                (v[m]*pr@(slash(a)+mt*np.eye(4))@pr,mt*v[m]*pr),
                (v[m]*pr@(slash(a)+mt*np.eye(4))@pl,mb*x*v[m]*pr),
                ((p[m]+s[m])*pr,
                 1j*sum(sigma[m,n]*q[n]*metric[n] for n in range(4))@pr+mb*g[m]@pl)]
            for full,reduced in cases:
                residual=left@(full-reduced)@right
                maximum=max(maximum,float(np.linalg.norm(residual)))
        self.audit_evidence={'on_shell_numerator_comparisons':20,
                             'max_numerator_matrix_norm':maximum}
        self.assertLess(maximum,1e-12)


class DiagramProjectionTests(unittest.TestCase):
    def setUp(self):self.context=mp.workdps(70);self.context.__enter__()
    def tearDown(self):self.context.__exit__(None,None,None)

    def test_diagram_integrals_against_frozen_kernels(self):
        maximum=mp.mpf(0)
        for x in ('.0001','.03','.2','.75','1','1.25','3','30'):
            f=loop_functions(float(x))
            yy=coefficients(x,1,0);xy=coefficients(x,0,1)
            for actual,target in zip(yy+xy,(f['F7_1']/3,f['F8_1']/3,f['F7_2'],f['F8_2'])):
                maximum=max(maximum,abs((actual-target)/actual))
        self.audit_evidence={'diagram_kernel_comparisons':32,'max_relative_residual':float(maximum),
                             'working_decimal_digits':70}
        self.assertLess(maximum,mp.mpf('2e-11'))

    def test_signed_two_state_and_interchange(self):
        b=mp.mpf('.91');g=mp.mpf('.63');mt=mp.mpf(163)
        def independent(masses,angle):
            result=[mp.mpf(0),mp.mpf(0)]
            for mass,a in zip(masses,(mp.cos(angle),-mp.sin(angle))):
                pair=coefficients((mt/mass)**2,a*a/mp.tan(b)**2,a*a)
                result=[v+c for v,c in zip(result,pair)]
            return result
        total=independent((550,900),g)
        swapped=independent((900,550),g+mp.pi/2)
        native=compute(550,900,float(b),float(g),163,160)
        errors=[]
        for a,c,key in zip(total,swapped,('delta_C7_LO_at_matching_scale','delta_C8_LO_at_matching_scale')):
            self.assertLess(abs(a-c),mp.mpf('1e-65'))
            self.assertLess(abs(a-native[key]),mp.mpf('2e-14'))
            errors.append(float(abs(a-native[key])))
            self.assertGreater(abs(a+native[key]),mp.mpf('.01')) # opposite overall sign fails
        self.audit_evidence={'two_state_absolute_residuals_C7_C8':errors,
                             'independent_C7_C8':[str(v) for v in total]}

    def test_scale_label_cannot_replace_mass_running(self):
        a=compute(550,900,.91,.63,163,160)
        b=compute(550,900,.91,.63,163,81)
        for key in ('delta_C7_LO_at_matching_scale','delta_C8_LO_at_matching_scale'):
            self.assertEqual(a[key],b[key])
        self.assertEqual(a['matching_convention_status'],'MATCHING_CONVENTION_UNKNOWN')

    def test_charge_falsifiers(self):
        reference=coefficients('.2',.7,1)
        wrong_top=coefficients('.2',.7,1,qt=-mp.mpf(1)/3)
        wrong_scalar=coefficients('.2',.7,1,qs=-1)
        self.assertGreater(abs(reference[0]-wrong_top[0]),mp.mpf('.01'))
        self.assertGreater(abs(reference[0]-wrong_scalar[0]),mp.mpf('.01'))
        self.assertEqual(reference[1],wrong_scalar[1])

    def test_goldstone_separate_from_physical_scalar(self):
        goldstone=coefficients('.2',1,-1) # X=-1,Y=1
        physical=coefficients('.2',1,1)
        self.assertTrue(all(v>0 for v in goldstone))
        self.assertTrue(all(v<0 for v in physical))
        # The SM also contains W/ghost/gauge-fixing terms: never add this as NP.

    def test_beta_limits_and_heavy_state_decoupling(self):
        xy=coefficients('.2',0,1)
        large_beta=coefficients('.2',mp.mpf('1e-12'),1)
        small_beta=coefficients('.2',100,1)
        heavy=coefficients('1e-12',1,1)
        for a,b,c,h in zip(xy,large_beta,small_beta,heavy):
            self.assertLess(abs(a-b),mp.mpf('1e-12'))
            self.assertLess(c,a)
            self.assertLess(abs(h),mp.mpf('1e-10'))


if __name__=='__main__':unittest.main()
