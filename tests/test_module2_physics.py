"""Independent quadratures, native archived matrices and analytic PDG witnesses."""
import json
import math
from pathlib import Path
import re
import unittest
import mpmath as mp
import numpy as np
from module2.core import forward, loop_kernel, weights, null_cone, solve_fixed_f, yukawa_rotation, NumericalUnknown
from module2.observables import observables, takagi

ROOT = Path(__file__).resolve().parents[1]
ML = np.array([.00051099895, .1056583755, 1.77686])
EVIDENCE = {}


def pmns(squares=(.307, .02195, .561), delta=4.2, alpha21=.7, alpha31=2.1):
    s12, s13, s23 = np.sqrt(squares)
    c12, c13, c23 = np.sqrt(1-np.array(squares))
    e = np.exp(1j*delta)
    V = np.array([[c12*c13,s12*c13,s13/e],[-s12*c23-c12*s23*s13*e,c12*c23-s12*s23*s13*e,s23*c13],[s12*s23-c12*c23*s13*e,-c12*s23-s12*c23*s13*e,c23*c13]])
    return V@np.diag([1,np.exp(.5j*alpha21),np.exp(.5j*alpha31)])


def target(ordering, lightest=.001, delta=4.2):
    ds, da = 7.49e-5, 2.534e-3 if ordering == 'NO' else -2.510e-3
    m = np.sqrt([lightest**2,lightest**2+ds,lightest**2+da]) if ordering == 'NO' else np.sqrt([lightest**2-da-ds,lightest**2-da,lightest**2])
    U = pmns(delta=delta)
    return U.conj()@np.diag(m)@U.conj().T, m, U


def quad_kernel(m1,m2,ml):
    with mp.workdps(80):
        a,b,z = [mp.mpf(float(x))**2 for x in (m1,m2,ml)]
        # Separate endpoint scales from electron through tau; independent integral.
        return float(mp.quad(lambda x: mp.log(a/b) if not z and x == 1 else mp.log1p((1-x)*(a-b)/(x*z+(1-x)*b)),[0,.5,.9,.99,.9999,.99999999,1]))


def archived_cases():
    text = (ROOT/'validation/module0/fixtures/e3_charged_loop_fixture.m').read_text()
    numeric = r'[+-]?\d+\.\d+\*\^[+-]\d+'
    for chunk in text.split('<|')[1:]:
        out = {'Label':re.search(r'"Label" -> "([^"]+)"',chunk)[1]}
        for key in ['M1','M2','Gamma','Beta','V']:
            out[key] = float(re.search('"'+key+'" -> ('+numeric+')',chunk)[1].replace('*^','e'))
        for key in ['FSARAH','YeSARAH','Ye2SARAH','FChen','YChen','FiniteMnuEV','FiniteLogs','LeptonMasses']:
            tail = chunk.split('"'+key+'" -> ',1)[1]
            end, depth = 0,0
            for i,c in enumerate(tail):
                depth += (c=='{')-(c=='}')
                if depth==0:
                    end=i+1
                    break
            nums=np.array([float(x.replace('*^','e')) for x in re.findall(numeric,tail[:end])])
            out[key]=nums if key in ('FiniteLogs','LeptonMasses') else (nums[::2]+1j*nums[1::2]).reshape(3,3)
        yield out


class ForwardTests(unittest.TestCase):
    def test_high_precision_integral(self):
        errors=[]
        for a,b in [(300,700),(375,925),(800,800.00000001),(300,np.nextafter(300.,math.inf)),(1.77686,2),(.0001,.0002),(1e5,2e5),(700,300)]:
            for ml in [0,*ML]:
                got,ref=loop_kernel(a,b,ml),quad_kernel(a,b,ml)
                errors.append(abs(got-ref)/max(abs(ref),1e-300))
                self.assertLessEqual(errors[-1],5e-14)
        EVIDENCE['kernel_max_relative_error_vs_80_digit_quadrature']=max(errors)

    def test_native_e3_and_independent_chiral_products(self):
        native=json.loads((ROOT/'validation/module0/report/majorana_physical.json').read_text())
        residuals=[]
        for case,ref in zip(archived_cases(),native['results']):
            self.assertEqual(case['Label'],ref['label'])
            F=case['FSARAH']; Ye=case['YeSARAH']; Ye2=case['Ye2SARAH']
            beta,gamma=case['Beta'],case['Gamma']
            D=-math.sin(beta)*Ye+math.cos(beta)*Ye2
            self.assertLess(np.max(abs(F-2*case['FChen'])),1e-18)
            self.assertLess(np.max(abs(D-np.sqrt(2)*case['YChen'])),1e-17)
            S=math.cos(beta)*Ye+math.sin(beta)*Ye2
            self.assertLess(np.max(abs(S-np.diag(np.sqrt(2)*ML/case['V']))),1e-17)
            M=forward(F,D,m1=case['M1'],m2=case['M2'],gamma=gamma,ml=ML)
            archived=np.array(ref['mass_matrix_real_eV'])+1j*np.array(ref['mass_matrix_imag_eV'])
            residual=float(np.max(abs(M-archived)))
            self.assertLess(residual,5e-11)
            self.assertLess(np.max(abs(M-case['FiniteMnuEV'])),2e-14)
            # Independent all-incoming chiral products and finite B0 quadrature.
            SL=np.zeros((3,3),complex); SR=SL.copy()
            with mp.workdps(65):
                for mass,dc,sc in [(case['M1'],math.cos(gamma),math.sin(gamma)),(case['M2'],-math.sin(gamma),math.cos(gamma))]:
                    for l,ml in enumerate(ML):
                        z,a=mp.mpf(float(ml))**2,mp.mpf(mass)**2
                        B0=float(-mp.quad(lambda x: mp.log(x*z+(1-x)*a),[0,.9,.99,.9999,1]))
                        for CL,CR in [(-1j*dc*D[l],-1j*sc*F[:,l].conj()),(-1j*sc*F[:,l],-1j*dc*D[l].conj())]:
                            SL+=ml*B0*np.outer(CR,CL.conj())
                            SR+=ml*B0*np.outer(CL,CR.conj())
            physical=-(SL.conj()+SR)*1e9/(32*math.pi**2)
            self.assertLess(np.max(abs(SR-SL.conj())),1e-22)
            self.assertLess(np.max(abs(M-physical)),2e-13)
            # Phase-sensitive archived Takagi columns, with sign freedom only.
            m,U,_=takagi(M,'NO')
            Ua=(np.array(ref['takagi_rotation_real'])+1j*np.array(ref['takagi_rotation_imag']))[:,::-1]
            overlap=U.conj().T@Ua
            self.assertLess(np.max(abs(abs(overlap)-np.eye(3))),2e-9)
            self.assertLess(np.max(abs(overlap.imag)),2e-9)
            self.assertLess(np.max(abs(m-np.array(ref['takagi_masses_eV'])[::-1])),5e-11)
            residuals.append({'label':case['Label'],'complex_mass_residual_eV':residual,
                              'chiral_product_residual_eV':float(np.max(abs(M-physical))),
                              'takagi_phase_residual':float(max(np.max(abs(abs(overlap)-np.eye(3))),np.max(abs(overlap.imag))))})
        EVIDENCE['archived_native_E3']=residuals

    def test_symmetries_limits_and_units(self):
        rng=np.random.default_rng(20261025)
        F=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3));F=F-F.T
        D=rng.normal(size=(3,3))+1j*rng.normal(size=(3,3))
        kw=dict(m1=300,m2=700,gamma=.7,ml=ML)
        M=forward(F,D,**kw)
        self.assertTrue(np.array_equal(M,M.T))
        P=np.diag(np.exp(1j*rng.uniform(-3,3,3)))
        self.assertLess(np.max(abs(forward(P@F@P,P.conj()@D@P,**kw)-P@M@P))/np.max(abs(M)),2e-15)
        self.assertLess(np.max(abs(forward(F,D,m1=700,m2=300,gamma=-.7,ml=ML)-M)),1e-7)
        for a,b,g in [(300,300,.7),(300,700,0),(300,700,math.pi/2),(300,700,-math.pi/2)]:
            self.assertEqual(np.max(abs(forward(F,D,m1=a,m2=b,gamma=g,ml=ML))),0)
        self.assertEqual(np.max(abs(forward(F,np.zeros((3,3)),**kw))),0)
        self.assertEqual(np.max(abs(forward(F*0,D,**kw))),0)
        # Scaling every mass (including leptons) by k multiplies M by k.
        self.assertLess(np.max(abs(forward(F,D,m1=900,m2=2100,gamma=.7,ml=3*ML)-3*M))/np.max(abs(M)),3e-15)
        # Fixed splitting and mixing: charged heavy masses decouple together.
        norms=[np.linalg.norm(forward(F,D,m1=a,m2=math.sqrt(a*a+1e5),gamma=.7,ml=ML)) for a in [300,3000,30000]]
        self.assertTrue(norms[0]>norms[1]>norms[2])
        with self.assertRaises(ValueError): forward(np.eye(3),D,**kw)
        with self.assertRaises(ValueError): forward(F,D,m1=-1,m2=700,gamma=.7,ml=ML)
        # Chen limiting coefficient is algebraically derived, never fitted.
        chen=math.sqrt(2)*math.sin(1.4)/(16*math.pi**2)*math.log(300**2/700**2)
        small=ML*1e-5
        C=(F/2*small)@(D/math.sqrt(2))
        self.assertLess(np.linalg.norm(forward(F,D,m1=300,m2=700,gamma=.7,ml=small)-chen*(C+C.T)*1e9)/np.linalg.norm(chen*(C+C.T)*1e9),1e-12)


class InverseTests(unittest.TestCase):
    def test_families_and_orderings(self):
        rng=np.random.default_rng(1729);errs=[];witnesses=[]
        for ordering in ['NO','IO']:
            M,m,U=target(ordering)
            for a,b,g in [(300,700,1.089),(375,925,.71),(850,1400,-.32)]:
                kw=dict(m1=a,m2=b,gamma=g,ml=ML)
                for t in [.25+.1j,-.7+.8j,1.3-.4j]:
                    for root in [0,1]:
                        F,n=null_cone(M,t,.002,root)
                        F*=np.exp(.43j)
                        self.assertLess(abs(n.T@M@n),1e-14)
                        self.assertLess(np.linalg.norm(F@n),1e-17)
                        self.assertGreater(abs(n.conj().T@M@n),1e-6) # wrong Hermitian constraint fails
                        sol=solve_fixed_f(F,M,**kw)
                        self.assertEqual((sol['rank'],sol['nullity_complex']),(5,4))
                        H=sol['homogeneous']
                        self.assertEqual(np.linalg.matrix_rank(H.reshape(4,9)),4)
                        self.assertLess(np.linalg.norm(H.reshape(4,9)@H.reshape(4,9).conj().T-np.eye(4)),1e-14)
                        for _ in range(3):
                            z=(rng.normal(size=4)+1j*rng.normal(size=4))*np.linalg.norm(sol['D0'])*.5
                            D=sol['D0']+np.einsum('k,kij->ij',z,H)
                            recon=forward(F,D,**kw)
                            err=float(np.max(abs(recon-M)))
                            self.assertLess(err,2e-12);errs.append(err)
                witnesses.append({'ordering':ordering,'charged_masses_GeV':[a,b],'gamma_rad':g,'masses_eV':m.tolist(),'rank':5,'nullity_complex':4})
        EVIDENCE['family_max_closure_eV']=max(errs)
        EVIDENCE['physical_witnesses']=witnesses
        EVIDENCE['random_family_reconstructions']=len(errs)

    def test_real_and_singular_cases(self):
        F=np.array([[0,.1,.2],[-.1,0,.3],[-.2,-.3,0]])
        D=np.arange(9).reshape(3,3)*1e-7
        kw=dict(m1=300,m2=700,gamma=.7,ml=ML)
        M=forward(F,D,**kw)
        s=solve_fixed_f(F,M,**kw)
        self.assertLess(np.max(abs(s['D0'].imag)),1e-18)
        with self.assertRaises(ValueError):solve_fixed_f(F,np.eye(3),**kw)
        with self.assertRaises(NumericalUnknown):solve_fixed_f(F*0,M,**kw)
        for p in [dict(m1=300,m2=300,gamma=.7,ml=ML),dict(m1=300,m2=700,gamma=0,ml=ML)]:
            with self.assertRaises(NumericalUnknown):solve_fixed_f(F,M,**p)
        # Charts with a zero quadratic coefficient and all-zero targets.
        for M,t,chart in [(np.zeros((3,3)),.2j,(0,1,2)),(np.diag([1.,0,1]),1j,(0,1,2)),(np.diag([0.,1,1]),.4,(1,2,0))]:
            F,n=null_cone(M,t,.1,chart=chart)
            self.assertLess(abs(n.T@M@n),1e-13)
        with self.assertRaises(NumericalUnknown):null_cone(np.diag([1.,0,1]),0,.1)
        with self.assertRaises(NumericalUnknown):solve_fixed_f(np.array([[0,.1,0],[-.1,0,0],[0,0,0]]),np.zeros((3,3)),m1=300,m2=700,gamma=.7,ml=[1e-15,.1,1])


class ObservableTests(unittest.TestCase):
    def test_pdg_phases_and_absolute_masses(self):
        errors=[]
        for ordering in ['NO','IO']:
            for light in [0,.001,.1]:
                for delta in [.3,2.1,4.2,5.9]:
                    M,m,U=target(ordering,light,delta)
                    o=observables(M,ordering)
                    self.assertLess(np.max(abs(np.array(o['masses_eV'])-m)),2e-15)
                    self.assertLess(max(abs(o[k]-x) for k,x in zip(['sin2_theta12','sin2_theta13','sin2_theta23'],[.307,.02195,.561])),2e-12)
                    self.assertLess(max(abs(o[k]-math.asin(math.sqrt(x))) for k,x in zip(['theta12_rad','theta13_rad','theta23_rad'],[.307,.02195,.561])),2e-12)
                    error=abs(np.angle(np.exp(1j*(o['delta_rad']-delta))));errors.append(error)
                    self.assertLess(error,2e-11)
                    self.assertAlmostEqual(o['sin_delta'],math.sin(delta),places=11)
                    self.assertAlmostEqual(o['cos_delta'],math.cos(delta),places=11)
                    expected_J=np.prod(np.sqrt([.307,1-.307,.561,1-.561,.02195]))*(1-.02195)*math.sin(delta)
                    self.assertAlmostEqual(o['J_CP'],expected_J,places=12)
                    if light>0 or ordering=='IO':
                        self.assertLess(abs(np.angle(np.exp(1j*(o['alpha21_rad']-.7)))),2e-11)
                    if light>0:
                        self.assertLess(abs(np.angle(np.exp(1j*(o['alpha31_rad']-2.1)))),2e-11)
                    elif ordering=='NO':
                        self.assertIsNone(o['alpha21_rad']);self.assertIsNone(o['alpha31_rad'])
                        self.assertLess(abs(np.angle(np.exp(1j*(o['majorana_pair_phases_rad']['32']-1.4)))),2e-11)
                    else:
                        self.assertIsNone(o['alpha31_rad'])
                    self.assertAlmostEqual(o['dm21_eV2'],7.49e-5,places=14)
                    self.assertAlmostEqual(o['dm3l_eV2'],2.534e-3 if ordering=='NO' else -2.510e-3,places=14)
                    self.assertAlmostEqual(o['m_beta_eV'],np.sqrt(sum(abs(U[0])**2*m*m)),places=14)
                    self.assertAlmostEqual(o['m_bb_eV'],abs(sum(U[0]**2*m)),places=14)
                    P=np.diag(np.exp(1j*np.array([.7,-1.3,2.2])))
                    oo=observables(P@M@P,ordering)
                    for k in ['J_CP','sin_delta','cos_delta','sin2_theta12','m_beta_eV','m_bb_eV']:
                        self.assertAlmostEqual(o[k],oo[k],places=11)
                    cp=observables(M.conj(),ordering)
                    self.assertAlmostEqual(cp['J_CP'],-o['J_CP'],places=12)
                    self.assertAlmostEqual(cp['sin_delta'],-o['sin_delta'],places=11)
        EVIDENCE['max_signed_Dirac_phase_error_rad']=max(errors)

    def test_degeneracies_and_random_unitaries(self):
        rng=np.random.default_rng(886)
        worst=0.
        for masses in [[0,0,0],[0,0,.05],[.05,.05,.05],[.01,.01,.05],[0,.01,.05],[.05,.05+1e-13,.05001],[1e-12,.01,.05]]:
            for _ in range(10):
                Q,_=np.linalg.qr(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))
                M=Q.conj()@np.diag(masses)@Q.conj().T
                for ordering in ['NO','IO']:
                    m,U,d=takagi(M,ordering)
                    self.assertLess(d['unitarity'],2e-12)
                    self.assertLess(d['reconstruction_relative'],2e-12)
                    worst=max(worst,d['reconstruction_relative'])
                    self.assertLess(np.max(abs(np.sort(m)-masses)),2e-15)
            if len(set(masses))<3:
                o=observables(M,'NO');self.assertEqual(o['mixing_status'],'UNKNOWN');self.assertIsNone(o['delta_rad'])
        o=observables(np.diag([.001,.01,.05]),'NO')
        self.assertIsNone(o['delta_rad']);self.assertIsNone(o['alpha31_rad'])
        with self.assertRaises(ValueError):takagi(np.eye(3),'automatic')
        EVIDENCE['takagi_max_relative_reconstruction']=worst


if __name__=='__main__':unittest.main()
