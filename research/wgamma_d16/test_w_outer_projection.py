"""Focused tests of the new topology; no full-gauge acceptance asserted."""
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import sympy as s
from sympy.parsing.mathematica import parse_mathematica
from .parent_integrals import numerator,native_parent_numerator
from .w_vacuum import (dipole_numerator,direct,sunset,topology_pair,
                       pole_identity,master_combination,gww_mass_difference,gww_numerator,X,Y,Z,W,D)

HERE=Path(__file__).resolve().parent


class RegulatedParent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence=json.loads((HERE/'w_outer_evidence.json').read_text())
        cls.temp=tempfile.TemporaryDirectory()
        cls.coefficients=Path(cls.temp.name)/'coefficients.json'
        cls.coefficients.write_text(json.dumps(cls.evidence['ibp']))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_native_signed_WWW_numerator(self):
        l=np.array([.2,.6,-.5,.4]);p=np.array([1.,0,0,0]);q=np.array([.5,0,0,.5])
        r=np.array([.1,-.4,.3,.2]);mw2=80.379**2
        actual=native_parent_numerator(l[None],p,q,r,mw2,310.**2,1.,('W','W','W'))[0]
        expected=2*mw2*np.array([numerator(mu,l,p,q) for mu in range(4)])
        np.testing.assert_allclose(actual,expected,rtol=1e-14,atol=1e-10)

    def test_independent_d_dimensional_open_Dirac_projection(self):
        expression=parse_mathematica(self.evidence['projection']['dipole_numerator'])
        expression=expression.subs(s.Symbol('mw')**2,W)
        self.assertEqual(s.cancel(expression-dipole_numerator()),0)
        finite=X/3+3*Z-4*Z**2/(3*Y)+W*Z/(X-W)
        self.assertEqual(s.cancel(dipole_numerator().subs(D,4)-finite),0)
        self.assertNotEqual(s.diff(dipole_numerator(),D).subs(D,4),0)

    def test_exact_IBP_double_and_single_poles_cancel(self):
        self.assertEqual(pole_identity(self.coefficients),(0,0))
        for record in self.evidence['witnesses']:
            np.testing.assert_allclose(record['ibp']['laurent'][:2],[0,0],atol=2e-12)

    def test_sector_subtraction_known_single_mass_master(self):
        values,errors=sunset((1.,0.,0.))
        # Exact gamma-function master, expanded with e^(2 gamma_E eps).
        np.testing.assert_allclose(values,[-.5,-1.5,-3.5-np.pi**2/4],atol=2e-9)
        self.assertLess(errors[2],2e-7)

    def test_independent_IBP_and_finite_radial_integrals(self):
        for h in ((125/80.379)**2,(310/80.379)**2):
            reduced=master_combination(h,self.coefficients)
            value,error=direct(h)
            self.assertLess(value,0)
            self.assertLess(abs(reduced['laurent'][2]-value),
                            max(2e-9,8*(reduced['error'][2]+error)))
        with self.assertRaises(ValueError):
            master_combination(4.,self.coefficients)
        self.assertTrue(np.isfinite(direct(4.)[0]))

    def test_complex_chiral_reverse_phases_dimensions_and_guards(self):
        args=(80.379,310.,246.21965,.7,.1056583755,.03+.02j,-.01+.04j)
        result=topology_pair(*args);c=result['topology_C_LR']
        self.assertTrue(np.all(abs(c)>0))
        reverse=topology_pair(*args[:4],.00051099895,args[6].conjugate(),args[5].conjugate())
        np.testing.assert_allclose(reverse['topology_C_LR'],
            args[4]/.00051099895*c[::-1].conjugate(),rtol=2e-14)
        scaled=topology_pair(2*args[0],2*args[1],2*args[2],args[3],2*args[4],*args[5:])
        np.testing.assert_allclose(scaled['topology_C_LR'],c/4,rtol=2e-14)
        phase=np.exp(.37j)
        rephased=topology_pair(*args[:5],phase*args[5],phase*args[6])
        np.testing.assert_allclose(rephased['topology_C_LR'],phase*c,rtol=2e-14)
        self.assertIsNone(result['physical_C_LR'])
        self.assertFalse(result['coherent_inclusion'])

    def test_unequal_mass_spinor_Pauli_projection_both_complex_chiralities(self):
        from .algebra import GAMMA,PL,PR,ID,slash,spinor,bar
        poly=[parse_mathematica(x) for x in self.evidence['projection']['polynomials']]
        symbols=s.symbols('ap bp cp aq bq cq')
        expr=s.expand(sum(poly)).subs({s.Symbol('mw')**2:W})
        subs={X:1.7,Y:2.1,Z:.31,W:.8,D:4}
        values=[complex(expr.coeff(x).subs(subs)) for x in symbols]
        ap,bp,cp,aq,bq,cq=values
        mi,mj=3.,.7
        pi=np.array([mi,0.,0.,0.]);pv=np.array([.2,-.8,1.2])
        pj=np.r_[np.sqrt(mj*mj+np.dot(pv,pv)),pv];q=pi-pj
        left,right=.03+.02j,-.01+.04j
        def vertex(p,k,mu):
            g=GAMMA[mu]
            return (ap*g@slash(p)+bp*slash(p)@g+cp*p[mu]*ID+
                    aq*g@slash(k)+bq*slash(k)@g+cq*k[mu]*ID)@PR
        rows=[];target=[]
        for mu in range(4):
            pauli=(slash(q)@GAMMA[mu]-GAMMA[mu]@slash(q))/2
            basis=[pauli@PL,pauli@PR,GAMMA[mu]@PL,GAMMA[mu]@PR,q[mu]*PL,q[mu]*PR]
            rev=vertex(pj,-q,mu)
            actual=right*vertex(pi,q,mu)+left*GAMMA[0]@rev.conjugate().T@GAMMA[0]
            for si in range(2):
                for sj in range(2):
                    ui=spinor(pi,mi,si);uj=bar(spinor(pj,mj,sj))
                    rows.append([uj@b@ui for b in basis]);target.append(uj@actual@ui)
        fit,_,rank,_=np.linalg.lstsq(rows,target,rcond=None)
        self.assertEqual(rank,6)
        expected=cp/2+bp+bq-aq
        np.testing.assert_allclose(fit[:2],expected*np.array([left,right]),rtol=2e-13,atol=1e-14)
        np.testing.assert_allclose(np.asarray(rows)@fit,target,atol=1e-13)

    def test_GWW_native_source_and_open_Dirac_projection(self):
        from .algebra import GAMMA,slash,PL
        l=np.array([.2,.6,-.5,.4]);p=np.array([1.,0,0,0]);q=np.array([.5,0,0,.5])
        r=np.array([.1,-.4,.3,.2]);w=80.379**2
        actual=native_parent_numerator(l[None],p,q,r,w,310.**2,1.,('G','W','W'))[0]
        expected=w*np.array([g@slash(p-l)@slash(l+r)@PL for g in GAMMA])
        np.testing.assert_allclose(actual,expected,rtol=1e-14,atol=1e-10)
        evidence=json.loads((HERE/'gww_outer_evidence.json').read_text())
        expr=parse_mathematica(evidence['projection']['dipole_numerator']).subs(s.Symbol('mw')**2,W)
        self.assertEqual(s.cancel(expr-gww_numerator()),0)

    def test_GWW_IBP_poles_and_independent_integrals(self):
        evidence=json.loads((HERE/'gww_outer_evidence.json').read_text())
        path=Path(self.temp.name)/'gww.json';path.write_text(json.dumps(evidence['ibp']))
        self.assertEqual(pole_identity(path),(0,s.Rational(1,4)))
        reference=master_combination(2.,path)
        for record in evidence['witnesses']:
            h=(record['ms']/80.379)**2
            value,error=gww_mass_difference(h)
            self.assertLess(value,0.)
            reduced=master_combination(h,path)
            self.assertLess(abs(value-reduced['laurent'][2]+reference['laurent'][2]),max(2e-9,8*(error+reduced['error'][2]+reference['error'][2])))


if __name__=='__main__':
    unittest.main()
