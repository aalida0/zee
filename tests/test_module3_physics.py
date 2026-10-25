"""Independent quadratures, Dirac traces, helicity sums, and signed checks."""
import ast
import copy
import itertools
import math
from pathlib import Path
import unittest
import mpmath as mp
import numpy as np
from scipy.integrate import quad
from module2.core import yukawa_rotation
from module3 import core, tree
from module3.witnesses import ML, example

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = {}
P = example()['module2_input']['scalar']['record']['physical']


def random_yukawas(seed=832):
    rng = np.random.default_rng(seed)
    a = (rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.03
    d = (rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.02
    return a-a.T,d


def quad_kernels(t):
    with mp.workdps(60):
        t = mp.mpf(t)
        den = lambda x: 1-x+x*t
        # Independent Feynman parameters, not a rational/log expression.
        intervals = [0,mp.mpf('.5'),mp.mpf('.99'),mp.mpf('.99999999'),1]
        a = mp.quad(lambda x:x*x*(1-x)/(2*den(x)),intervals)
        b = mp.quad(lambda x:x*x/den(x),intervals)
        c = mp.quad(lambda x:x*x*(1-x)/(2*(x+(1-x)*t)),intervals)
        return np.array([float(a),float(b),float(c)])


def legacy_functions(filename, names, namespace):
    """Load only named pure functions, never historical scan imports."""
    parsed = ast.parse((ROOT/'scripts'/filename).read_text())
    selected = [n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names]
    exec(compile(ast.Module(body=selected,type_ignores=[]),filename,'exec'),namespace)
    return namespace


class MappingTests(unittest.TestCase):
    def test_archived_complex_E3_conversion(self):
        from test_module2_physics import archived_cases
        errs = []
        for case in archived_cases():
            f,ye,y2 = [case[k] for k in ['FSARAH','YeSARAH','Ye2SARAH']]
            beta = case['Beta']
            d = -np.sin(beta)*ye+np.cos(beta)*y2
            errs += [np.max(abs(f-2*case['FChen'])),np.max(abs(d-np.sqrt(2)*case['YChen']))]
            p = dict(P,beta=beta,v=case['V'])
            alpha = p['alpha']
            h,H,A = [v[0] for v in core.vertices(d,p,ML).values()]
            self.assertTrue(np.allclose(h,(np.cos(alpha)*ye+np.sin(alpha)*y2)/np.sqrt(2),atol=2e-18,rtol=1e-12))
            self.assertTrue(np.allclose(H,(-np.sin(alpha)*ye+np.cos(alpha)*y2)/np.sqrt(2),atol=2e-18,rtol=1e-12))
            self.assertTrue(np.allclose(A,-1j*d/np.sqrt(2),atol=1e-18))
        self.assertLess(max(errs),1e-17)
        EVIDENCE['archived_F_D_conversion_max_abs'] = float(max(errs))

    def test_random_unrestricted_Ye_mass_closure_and_charged_rows(self):
        errors = []
        for seed in range(10):
            _,d = random_yukawas(seed)
            ye,y2 = yukawa_rotation(d,P['beta'],P['v'],ML)
            c,s = np.cos(P['beta']),np.sin(P['beta'])
            errors.append(np.max(abs(c*ye+s*y2-np.diag(np.sqrt(2)*ML/P['v']))))
            for dc,sc in [(np.cos(P['gamma']),np.sin(P['gamma'])),(-np.sin(P['gamma']),np.cos(P['gamma']))]:
                zp = [-s*dc,c*dc,sc]
                self.assertLess(np.max(abs(zp[0]*ye+zp[1]*y2-dc*d)),1e-17)
        EVIDENCE['Yukawa_rotation_max_abs'] = float(max(errors))

    def test_alignment_and_CP_odd_vertex(self):
        _,d = random_yukawas()
        p = dict(P,alpha=P['beta'])
        vs = core.vertices(d,p,ML)
        np.testing.assert_allclose(vs['h'][0],np.diag(ML/p['v']),atol=1e-18)
        np.testing.assert_allclose(vs['H'][0],d/np.sqrt(2),atol=1e-18)
        np.testing.assert_allclose(vs['A'][0],-1j*d/np.sqrt(2),atol=1e-18)


class DipoleTests(unittest.TestCase):
    def test_kernels_vs_independent_quadrature_including_unity(self):
        errors = []
        for t in [1e-12,1e-5,.2,.9999,1-1e-12,1.,np.nextafter(1.,2.),1+1e-12,1.0001,2.,1e4]:
            got,ref = np.array(core.kernels(t)),quad_kernels(t)
            err = float(np.max(abs(got-ref)/ref));errors.append(err)
            self.assertLess(err,5e-13)
        EVIDENCE['loop_kernel_max_relative_vs_quadrature'] = max(errors)

    def test_small_t_and_invalid_ratios(self):
        a,b,c = core.kernels(1e-14)
        self.assertAlmostEqual(a,1/6,delta=1e-12)
        self.assertAlmostEqual(b,-1.5-np.log(1e-14),delta=1e-11)
        self.assertAlmostEqual(c,1/12,delta=1e-12)
        self.assertEqual(core.kernels(0)[2],1/12)
        for x in [-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):core.kernels(x)

    def test_general_Lavoura_quadrature_all_channels(self):
        errors = []
        _,d = random_yukawas()
        for C,mass in core.vertices(d,P,ML).values():
            qs = [quad_kernels((mk/mass)**2) for mk in ML]
            for i,j in [(1,0),(2,0),(2,1)]:
                sig = np.zeros(2,complex)
                for k,mk in enumerate(ML):
                    li,lj = C[k,i],C[k,j]
                    ri,rj = C[i,k].conjugate(),C[j,k].conjugate()
                    lam,rho,zeta,ups = lj.conjugate()*li,rj.conjugate()*ri,lj.conjugate()*ri,rj.conjugate()*li
                    a,b,_ = qs[k]
                    # Lavoura QF=-1; remove common i and convert sigma.
                    sig += -np.array([rho*ML[i]*a+lam*ML[j]*a+ups*mk*b,
                                      lam*ML[i]*a+rho*ML[j]*a+zeta*mk*b])/(16*np.pi**2*mass**2)
                ref = -sig/ML[i]
                got = core.neutral_dipole(C,mass,i,j,ML)
                errors.append(float(np.linalg.norm(got-ref)/np.linalg.norm(ref)))
        self.assertLess(max(errors),1e-13)
        EVIDENCE['complex_dipole_max_relative_vs_parameter_integral'] = max(errors)

    def test_scalar_and_pseudoscalar_g_minus_2_sign_normalization(self):
        # Independent textbook Feynman-parameter g-2 integrals: retain
        # external mass in this reference and verify the heavy-scalar limit.
        m,M,y = ML[1],400.,.017
        C = np.diag([0,y,0]).astype(complex)
        # For the diagonal Hermitian operator count h.c. once:
        # e*m*c/2 = e*a/(4*m), so a=m²*(CL+CR).
        scalar = m*m*sum(core.neutral_dipole(C,M,1,1,ML)).real
        pseudo = m*m*sum(core.neutral_dipole(-1j*C,M,1,1,ML)).real
        r = (m/M)**2
        exact_s = y*y*r/(8*np.pi**2)*quad(lambda x:(1-x)**2*(1+x)/(x+r*(1-x)**2),0,1,epsabs=1e-12)[0]
        exact_p = -y*y*r/(8*np.pi**2)*quad(lambda x:(1-x)**3/(x+r*(1-x)**2),0,1,epsabs=1e-12)[0]
        self.assertGreater(scalar,0);self.assertLess(pseudo,0)
        error = max(abs(scalar/exact_s-1),abs(pseudo/exact_p-1))
        self.assertLess(error,3e-7)
        EVIDENCE['g_minus_2_heavy_limit_relative_error'] = error

    def test_charged_F_and_D_sign_from_same_QB(self):
        f,d = random_yukawas()
        for i,j in [(1,0),(2,0),(2,1)]:
            parts = core.dipole_ledger(f,d,P,ML,i,j)
            for name,m,dc,sc in [('H1',P['mH1'],np.cos(P['gamma']),np.sin(P['gamma'])),('H2',P['mH2'],-np.sin(P['gamma']),np.cos(P['gamma']))]:
                L = -sc*f[:,i];Lj = -sc*f[:,j]
                R = -dc*d[i,:].conjugate();Rj = -dc*d[j,:].conjugate()
                lam,rho = np.vdot(Lj,L),np.vdot(Rj,R)
                # Positive parameter integral 1/12 and QB=+1 in sigma;
                # same common conversion to C as neutral diagrams.
                ref = -np.array([rho+lam*ML[j]/ML[i],lam+rho*ML[j]/ML[i]])/(192*np.pi**2*m*m)
                got = np.array([parts[name+'_F'][k]+parts[name+'_D'][k] for k in ['C_L','C_R']])
                np.testing.assert_allclose(got,ref,rtol=2e-15,atol=1e-30)

    def test_Herrero_internal_tau_leading_log_signed(self):
        C = np.zeros((3,3),complex)
        C[0,2]=.003+.002j;C[2,1]=.021-.013j
        got = core.neutral_dipole(C,800.,1,0,ML)
        ref = C[0,2]*C[2,1]*(ML[2]/ML[1])*(np.log((800/ML[2])**2)-1.5)/(16*np.pi**2*800**2)
        self.assertLess(abs(got[0]/ref-1),3e-5)
        self.assertEqual(got[1],0j)
        EVIDENCE['signed_Herrero_leading_log_relative_error'] = float(abs(got[0]/ref-1))

    def test_legacy_after_exact_basis_conversion(self):
        f,d = random_yukawas()
        ns = {'np':np,'LEPTON_MASSES':ML}
        legacy_functions('gateA1e_neutral_one_loop_dipoles.py',{'loop_A','loop_B','neutral_dipole_for_scalar'},ns)
        errors = []
        for C,mass in core.vertices(d,P,ML).values():
            for i,j in [(1,0),(2,0),(2,1)]:
                old = np.array(ns['neutral_dipole_for_scalar'](C,mass,parent=i,daughter=j))
                new = core.neutral_dipole(C,mass,i,j,ML)
                errors.append(float(np.linalg.norm(new+old)/np.linalg.norm(new)))
        self.assertLess(max(errors),1e-13)
        # Old charged-singlet formula has the same sign as new C; neutral
        # and charged D require an overall minus. Thus the old coherent
        # assembly has a genuine relative-sign conflict in this mapping.
        ns = {'np':np,'GAMMA':P['gamma'],'M1':P['mH1'],'M2':P['mH2']}
        legacy_functions('gateA1c_charged_singlet_lfv.py',{'singlet_propagator_sum','dipole_coefficient_f_only'},ns)
        parts = core.dipole_ledger(f,d,P,ML,1,0)
        got = parts['H1_F']['C_R']+parts['H2_F']['C_R']
        old = ns['dipole_coefficient_f_only'](f/2,1,0)
        self.assertLess(abs(got-old),1e-26)
        self.assertGreater(abs(got+old),abs(got))
        ns = {'np':np,'GAMMA':P['gamma'],'M1':P['mH1'],'M2':P['mH2']}
        legacy_functions('gateA1f_charged_doublet_y_dipoles.py',{'charged_doublet_mass_weight','charged_doublet_y_dipole'},ns)
        oldD = ns['charged_doublet_y_dipole'](d/np.sqrt(2),parent=1,daughter=0)[0]
        self.assertLess(abs(parts['H1_D']['C_L']+parts['H2_D']['C_L']+oldD),1e-26)
        EVIDENCE['legacy_neutral_after_common_sign_max_relative_error'] = max(errors)
        EVIDENCE['legacy_relative_sign_conflict'] = 'A1c F agrees directly; A1e neutral/A1f D agree after common minus; old coherent sum cannot be reused'

    def test_rephasing_CP_and_reverse_channel_hermiticity(self):
        f,d = random_yukawas()
        phases = np.exp(1j*np.array([.3,-.8,1.2]));p=np.diag(phases)
        errors = []
        for i,j in [(1,0),(2,0),(2,1)]:
            orig = core.dipole_ledger(f,d,P,ML,i,j)
            trans = core.dipole_ledger(p@f@p,p.conj()@d@p,P,ML,i,j)
            cp = core.dipole_ledger(f.conj(),d.conj(),P,ML,i,j)
            for key in orig:
                for c in ['C_L','C_R']:
                    scale = max(abs(orig[key][c]),1e-30)
                    errors.append(abs(trans[key][c]-phases[j].conjugate()*phases[i]*orig[key][c])/scale)
                    self.assertLess(abs(cp[key][c]-orig[key][c].conjugate()),2e-26)
            for C,mass in core.vertices(d,P,ML).values():
                forward = core.neutral_dipole(C,mass,i,j,ML)
                reverse = core.neutral_dipole(C,mass,j,i,ML)
                np.testing.assert_allclose(ML[i]*forward,ML[j]*reverse[::-1].conj(),rtol=2e-14,atol=1e-28)
        self.assertLess(max(errors),1e-13)
        EVIDENCE['signed_rephasing_max_relative_residual'] = float(max(errors))

    def test_chirality_flip_transpose(self):
        _,d = random_yukawas()
        for C,m in core.vertices(d,P,ML).values():
            a=core.neutral_dipole(C,m,2,1,ML)
            b=core.neutral_dipole(C.conj().T,m,2,1,ML)
            np.testing.assert_allclose(a,b[::-1],rtol=2e-15,atol=1e-28)

    def test_charged_mixing_degenerate_and_pure_limits(self):
        f,d = random_yukawas()
        def charged(p,suffix):
            rows=core.dipole_ledger(f,d,p,ML,2,1)
            return np.array([sum(r[k] for n,r in rows.items() if n.endswith(suffix)) for k in ['C_L','C_R']])
        for suffix in ['_F','_D']:
            a=charged(dict(P,mH1=400.,mH2=400.,gamma=.11),suffix)
            b=charged(dict(P,mH1=400.,mH2=400.,gamma=1.32),suffix)
            np.testing.assert_allclose(a,b,rtol=2e-15)
        for gamma in [0,np.pi/2]:
            rows=core.dipole_ledger(f,d,dict(P,gamma=gamma),ML,2,1)
            absent='H1_F' if gamma==0 else 'H2_F'
            self.assertLess(abs(rows[absent]['C_R']),1e-40)

    def test_flavor_diagonal_and_zero_limits(self):
        d=np.diag([.01,.02,.03]);f=np.zeros((3,3),complex)
        for i,j in [(1,0),(2,0),(2,1)]:
            np.testing.assert_array_equal(core.combine(core.dipole_ledger(f,d,P,ML,i,j)),[0,0])

    def test_dimensional_scaling_and_yukawa_scaling(self):
        C=np.array([[.01,.02j,.03],[.04,.05,.06j],[.02j,.01,.03]])
        a=core.neutral_dipole(C,400,2,1,ML)
        b=core.neutral_dipole(C,800,2,1,2*ML)
        np.testing.assert_allclose(b,a/4,rtol=1e-15)
        np.testing.assert_allclose(core.neutral_dipole(2*C,400,2,1,ML),4*a,rtol=1e-15)

    def test_coherence_cancellation_and_rejected_mismatches(self):
        a=core.component([1+2j,3-4j],'test amplitude')
        b=core.component([-1-2j,-3+4j],'test cancelling amplitude')
        np.testing.assert_array_equal(core.combine({'a':a,'b':b}),[0,0])
        self.assertGreater(core.radiative_width(np.array([a['C_L'],a['C_R']]),1.,0.,.01),0)
        for key,val in [('basis','other'),('normalization','other'),('loop_order',2),('approximation','massive neutrino'),('validation_status','UNKNOWN')]:
            bad=copy.deepcopy(a);bad[key]=val
            with self.assertRaises(ValueError):core.combine({'a':a,'b':bad})
        with self.assertRaises(ValueError):core.combine({})

    def test_physical_neutral_degenerate_cancellation_subset(self):
        d=np.zeros((3,3),complex);d[0,2]=.03+.02j;d[2,1]=-.017+.013j
        p=dict(P,alpha=P['beta'],mh2=450.,ma=450.)
        rows=core.dipole_ledger(np.zeros((3,3),complex),d,p,ML,1,0)
        # Only the internal-tau flip survives; H and A cancel in this
        # declared scalar approximation. This says nothing about 2-loop terms.
        a=rows['H']['C_L'];b=rows['A']['C_L']
        self.assertGreater(abs(a),0);self.assertEqual(a+b,0j)
        np.testing.assert_array_equal(core.combine(rows),[0,0])
        changed=core.dipole_ledger(np.zeros((3,3),complex),d,dict(p,ma=451.),ML,1,0)
        self.assertGreater(abs(core.combine(changed)[0]),0)

    def test_neutrino_basis_unitarity_charged_contractions(self):
        f,d=random_yukawas();rng=np.random.default_rng(326)
        u,_=np.linalg.qr(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))
        left=u.T@f;right=u.conj().T@d.conj().T
        np.testing.assert_allclose(left.conj().T@left,f.conj().T@f,rtol=3e-14,atol=1e-18)
        np.testing.assert_allclose(right.conj().T@right,d@d.conj().T,rtol=3e-14,atol=1e-18)

    def test_external_invariant_approximation_against_exact_parameters(self):
        # Lavoura eqs.11-13 before dropping the external invariants.
        # Parameterize x=r*u, y=r*(1-u), z=1-r.
        M=80.;i,j,k=2,1,2;t=(ML[k]/M)**2
        nodes,weights=np.polynomial.legendre.leggauss(20)
        us=(nodes+1)/2;weights=weights/2
        def integral(kind):
            def radial(r):
                z=1-r
                den=z+r*t-z*r*(us*ML[i]**2+(1-us)*ML[j]**2)/M**2
                num=r*r*z*(us if kind==0 else 1-us) if kind<2 else r*r*np.ones_like(us)
                return float(np.sum(weights*num/den))
            return quad(radial,0,1,epsabs=1e-12,epsrel=2e-12)[0]
        exact=np.array([integral(0),integral(1),integral(2)])
        a,b,_=core.kernels(t)
        approx=np.array([a,a,b])
        err=float(np.max(abs(exact-approx)/exact))
        self.assertGreater(err,1e-7);self.assertLess(err,1e-3)
        EVIDENCE['external_invariant_approximation_error_at_80GeV']=err

    def test_radiative_width_independent_photon_trace(self):
        M,m=ML[2],ML[1];q=(M*M-m*m)/(2*M)
        p0=np.array([M,0,0,0]);p1=np.array([(M*M+m*m)/(2*M),0,0,-q])
        photon=np.array([q,0,0,q]);cov=photon*np.array([1,-1,-1,-1])
        cl,cr=.03+.02j,-.017+.013j
        trace=0j
        for mu in [1,2]:
            # sigma^{mu nu}=i/2 [gamma^mu,gamma^nu].
            op=sum(.5j*(tree.G[mu]@tree.G[nu]-tree.G[nu]@tree.G[mu])*cov[nu] for nu in range(4))@(cl*tree.PL+cr*tree.PR)
            adj=tree.G0@op.conj().T@tree.G0
            trace+=np.trace((tree.slash(p1)+m*np.eye(4))@op@(tree.slash(p0)+M*np.eye(4))@adj)/2
        alpha=.0073
        got=float(trace.real*4*np.pi*alpha*M*M*q/(8*np.pi*M*M))
        ref=core.radiative_width(np.array([cl,cr]),M,m,alpha)
        self.assertLess(abs(got/ref-1),1e-14)
        EVIDENCE['radiative_width_trace_relative_residual']=abs(got/ref-1)


class TreeAndWidthTests(unittest.TestCase):
    def test_massless_contact_analytic_identical_factor(self):
        c=np.zeros((3,3),complex);c[0,2]=1.;c[1,1]=1.
        distinct=tree.width({'s':(c,10.)},2,0,1,np.array([0.,0.,1.]),18,True)
        ref=2/(6144*np.pi**3*10**4)
        c[1,2]=1.;c[0,2]=0.
        identical=tree.width({'s':(c,10.)},2,1,1,np.array([0.,0.,1.]),18,True)
        # LL identical=1/2; LR identical=1, versus 1+1 distinct.
        self.assertLess(abs(distinct/ref-1),1e-13)
        self.assertLess(abs(identical/(.75*ref)-1),1e-13)
        EVIDENCE['massless_tree_analytic_relative_residual']=max(abs(distinct/ref-1),abs(identical/(.75*ref)-1))
        EVIDENCE['legacy_tree_rate_ratio_for_same_vertices']=4.

    def test_independent_spinor_sum_with_massive_interference(self):
        _,d=random_yukawas();sc=core.vertices(d,P,ML)
        M=ML[2];masses=(ML[0],ML[1],ML[1]);s=.7;z=-.37
        ps=tree.momenta(M,masses,s,z)
        direct,cross,ms=tree.tensors(sc,2,0,1)
        s13=ps[1]+ps[3];s13=s13[0]**2-s13[1:]@s13[1:]
        T=np.einsum('s,sabcd->abcd',1/(ms*ms-s),direct)-np.einsum('s,sabcd->abcd',1/(ms*ms-s13),cross)
        def spinors(p,m,anti=False):
            upper=np.sqrt(p[0]+m)*np.eye(2)
            lower=sum(p[k+1]*tree.PAULI[k] for k in range(3))/np.sqrt(p[0]+m)
            return np.vstack([lower,upper]) if anti else np.vstack([upper,lower])
        uu=[spinors(p,m,anti=k==3) for k,(p,m) in enumerate(zip(ps,[M,*masses]))]
        total=0.
        for h0,h1,h2,h3 in itertools.product(range(2),repeat=4):
            amp=0j
            for C,mass in sc.values():
                def vertex(a,b):return C[a,b]*tree.PL+C[b,a].conjugate()*tree.PR
                directamp=(uu[1][:,h1].conj()@tree.G0@vertex(0,2)@uu[0][:,h0])*(uu[2][:,h2].conj()@tree.G0@vertex(1,1)@uu[3][:,h3])/(mass*mass-s)
                crossamp=(uu[2][:,h2].conj()@tree.G0@vertex(1,2)@uu[0][:,h0])*(uu[1][:,h1].conj()@tree.G0@vertex(0,1)@uu[3][:,h3])/(mass*mass-s13)
                amp+=directamp-crossamp
            total+=abs(amp)**2/2
        got=tree.spin_sum(T,ps,M,masses)
        self.assertLess(abs(got/total-1),2e-14)
        EVIDENCE['massive_tree_tensor_vs_helicity_relative_residual']=abs(got/total-1)

    def test_distinct_flavor_crossed_contraction_nonzero(self):
        c=np.zeros((3,3),complex);c[1,2]=.1j;c[0,1]=.2
        # Direct e-tau and mu-mu couplings are zero; crossed survives.
        self.assertGreater(tree.width({'s':(c,400.)},2,0,1,ML,20),0)

    def test_tree_rephasing_CP_convergence_and_mass_effect(self):
        f,d=random_yukawas();p=np.diag(np.exp(1j*np.array([.4,-.3,.8])))
        scalars=core.vertices(d,P,ML)
        w=tree.width(scalars,2,1,1,ML,32)
        wp=tree.width(core.vertices(p.conj()@d@p,P,ML),2,1,1,ML,32)
        wc=tree.width(core.vertices(d.conj(),P,ML),2,1,1,ML,32)
        self.assertLess(abs(w/wp-1),2e-14);self.assertLess(abs(w/wc-1),2e-14)
        coarse=tree.width(scalars,2,1,1,ML,16)
        self.assertLess(abs(coarse/w-1),1e-5)
        massless=tree.width(scalars,2,1,1,np.array([0,0,ML[2]]),32)
        self.assertGreater(abs(w/massless-1),.01)

    def test_coherent_scalar_cancellation_and_threshold(self):
        c=np.zeros((3,3),complex);c[1,2]=.1;c[1,1]=.2
        # Degenerate scalar/pseudoscalar LL cancellation; LR adds.
        ws=tree.wilsons({'s':(c,400.),'p':(-1j*c,400.)},2,1,1)
        self.assertEqual(sum(v['direct']['LL'] for v in ws.values()),0j)
        self.assertGreater(abs(sum(v['direct']['LR'] for v in ws.values())),0)
        self.assertEqual(tree.width({'s':(c,400.)},1,0,1,ML,16),0.)
        with self.assertRaises(ValueError):tree.width({'s':(c,1.)},2,1,1,ML,16)

    def test_neutral_width_independent_trace_and_CP(self):
        _,d=random_yukawas();errors=[]
        for C,M in core.vertices(d,P,ML).values():
            for a,b in [(0,1),(0,2),(1,2)]:
                ma,mb=ML[a],ML[b]
                q=np.sqrt(tree.kallen(M*M,ma*ma,mb*mb))/(2*M)
                p1=np.array([np.sqrt(ma*ma+q*q),0,0,q]);p2=np.array([np.sqrt(mb*mb+q*q),0,0,-q])
                vertex=C[a,b]*tree.PL+C[b,a].conjugate()*tree.PR
                adj=tree.G0@vertex.conj().T@tree.G0
                tr=np.trace((tree.slash(p1)+ma*np.eye(4))@vertex@(tree.slash(p2)-mb*np.eye(4))@adj).real
                ref=q*tr/(8*np.pi*M*M)
                got=core.neutral_width(C,M,a,b,ML)
                errors.append(abs(got/ref-1))
                self.assertAlmostEqual(got,core.neutral_width(C,M,b,a,ML),delta=got*2e-15)
        self.assertLess(max(errors),1e-14)
        EVIDENCE['two_body_width_trace_max_relative_residual']=max(errors)

    def test_neutral_diagonal_scalar_pseudoscalar_threshold(self):
        y=.02;m=ML[2];M=4.
        C=np.diag([0,0,y]);beta=np.sqrt(1-4*m*m/M**2)
        self.assertAlmostEqual(core.neutral_width(C,M,2,2,ML),y*y*M*beta**3/(8*np.pi),delta=1e-20)
        self.assertAlmostEqual(core.neutral_width(-1j*C,M,2,2,ML),y*y*M*beta/(8*np.pi),delta=1e-20)
        self.assertEqual(core.neutral_width(C,2*m,2,2,ML),0.)

    def test_universality_general_GF_subtraction_and_basis(self):
        f=np.zeros((3,3),complex);f[0,1]=.02j;f-=f.T
        gf=1.1663787e-5
        out=core.universality(f,P,gf)
        # Herrero eq.3.29, f_Chen=F/2, rate shift sqrt(2)|f|²*w/GF.
        weight=np.sin(P['gamma'])**2/P['mH1']**2+np.cos(P['gamma'])**2/P['mH2']**2
        ref=np.sqrt(2)*abs(f[0,1]/2)**2*weight/gf
        self.assertAlmostEqual(out['rate_shifts_before_GF_subtraction']['mu_e'],ref,delta=ref*1e-15)
        self.assertAlmostEqual(out['g_tau_over_g_mu_squared_minus1'],-ref,delta=ref*1e-15)
        self.assertEqual(out['g_mu_over_g_e_squared_minus1'],0.)
        f[0,2]=f[1,2]=.02;f[2,0]=f[2,1]=-.02
        out=core.universality(f,P,gf)
        self.assertEqual(out['g_tau_over_g_mu_squared_minus1'],0.)
        self.assertEqual(out['physical_status'],'SUBSET_DIAGNOSTIC')


if __name__ == '__main__':unittest.main()
