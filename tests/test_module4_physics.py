"""Independent source equations, analytic kernels and signed falsification checks."""
import ast
import copy
from functools import lru_cache
import json
import math
from pathlib import Path
import unittest
import mpmath as mp
import numpy as np
from module3 import core, tree
from module3.witnesses import example, ML
from module2.interface import evaluate as evaluate2, decode
from module1.scalar_constraints import reconstruct
from module4.kernels import kernels, w_kernel, charged_scalar_kernel
from module4.couplings import quarks, rotations, trilinears
from module4.amplitudes import ledger, fermion_component, combine, CHANNELS

ROOT=Path(__file__).resolve().parents[1]
P=example()['module2_input']['scalar']['record']['physical']
EXTRA=json.loads((ROOT/'module4/example.json').read_text())['two_loop_inputs']
EVIDENCE={}


@lru_cache(None)
def cases():
    out=[]
    for order in ('NO','IO'):
        for spectrum in range(3):
            inp=example(order,spectrum);n=evaluate2(inp['module2_input'])
            out.append((inp,n))
    return out


def analytic(z):
    with mp.workdps(65):
        z=mp.mpf(str(z))
        if z==mp.mpf('.25'):
            g=mp.log(2)
            h=-(1+2*mp.log(2))/6
        else:
            r=mp.sqrt(1-4*z);xp=(1+r)/2;xm=(1-r)/2
            g=mp.re(z/r*(mp.polylog(2,xp)-mp.polylog(2,xm)-mp.log(z)*mp.log(xp/xm)/2))
            h=z*(2*g+mp.log(z))/(1-4*z)
        f=z*(2+mp.log(z))+(1-2*z)*g
        return np.array([float(f),float(g),float(h)])


def pure_functions(path,names,ns):
    parsed=ast.parse((ROOT/path).read_text())
    selected=[x for x in parsed.body if isinstance(x,ast.FunctionDef) and x.name in names]
    if len(selected)!=len(names):raise ValueError('Missing pure reference function')
    exec(compile(ast.Module(body=selected,type_ignores=[]),path,'exec'),ns)
    return ns


def rows(D,p=P,i=1,j=0):
    return ledger(D,p,ML,.0072973525692838015,EXTRA['fermion_masses_GeV'],80.379,i,j)


def diagnostic_sum(rows):
    """Source-specific mathematical sum, NEVER a validated coherent prediction."""
    return np.array([sum(r[k] for r in rows.values()) for k in ('C_L','C_R')])


class KernelTests(unittest.TestCase):
    def test_direct_parameters_vs_haber_dilog_all_regimes(self):
        errors=[]
        for z in [1e-13,1e-9,1e-5,.01,.249999,.25,.250001,.413,1.,1e2,1e6,1e9]:
            got,err=kernels(z);ref=analytic(z)
            errors.append(float(max(abs((got-ref)/ref))))
            self.assertLess(errors[-1],3e-10)
            self.assertTrue(all(x>=0 for x in err))
        EVIDENCE['fg_h_direct_vs_analytic_max_relative']=max(errors)

    def test_asymptotics_and_h_derivative(self):
        z=1e9;f,g,h=kernels(z)[0]
        self.assertAlmostEqual(g/(math.log(z)/2+1),1,delta=2e-9)
        self.assertAlmostEqual(f/(math.log(z)/3+13/18),1,delta=2e-9)
        self.assertAlmostEqual(h/(-(math.log(z)+1)/2),1,delta=2e-9)
        z=1e-13;f,g,h=kernels(z)[0]
        self.assertLess(abs(g/(z/2*(math.log(z)**2+math.pi**2/3))-1),1e-10)
        self.assertLess(abs((f-g)/(z*(math.log(z)+2))-1),1e-10)
        for z in (.01,.25,1.,10.):
            with mp.workdps(50):
                zz=mp.mpf(str(z));eps=mp.mpf('1e-5')*zz
                # Five-point derivative of g/z, independent of the h integrand.
                vals=[analytic(float(zz+k*eps))[1]/float(zz+k*eps) for k in (-2,-1,1,2)]
                derivative=(vals[0]-8*vals[1]+8*vals[2]-vals[3])/(12*float(eps))
                self.assertLess(abs(zz**2*derivative/kernels(z)[0][2]-1),2e-10)

    def test_invalid_kernel_arguments(self):
        for z in (0,-1,float('nan'),float('inf'),1e-30,1e12):
            with self.assertRaises(ValueError):kernels(z)

    def test_reference_kernels_without_scan_imports(self):
        ns={'math':math,'quad':__import__('scipy.integrate',fromlist=['quad']).quad}
        pure_functions('reference/lfv/scripts/zee_barr_zee_kernels.py',{'_log_over_t','f','g'},ns)
        errs=[]
        for z in (1e-7,.001,.1,.25,.413,1.,10.):
            f,g,_=kernels(z)[0]
            errs.extend([abs(f/ns['f'](z)[0]-1),abs(g/ns['g'](z)[0]-1)])
        self.assertLess(max(errs),2e-9)
        EVIDENCE['legacy_fg_max_relative']=max(errs)


class AmplitudeTests(unittest.TestCase):
    def test_davidson_operator_mapping_sign_charge_and_complex_conjugation(self):
        alpha=.0073;gf=1.166e-5;mi=.106;mf=172.;m=400.;nc=3;q=2/3
        ext=np.array([.03+.02j,-.07+.01j]);internal=.2+.13j
        out,_=fermion_component(ext,internal,mf,m,mi,alpha,nc,q)
        e=math.sqrt(4*math.pi*alpha);f,g,_=analytic((mf/m)**2)
        terms=np.array([internal.real*f+1j*internal.imag*g,internal.real*f-1j*internal.imag*g])*ext
        # Davidson lhs is the coefficient of bar(parent)...daughter.
        A=-(e*alpha*nc*q*q/(16*math.pi**3*mf)*terms).conjugate()/(2*math.sqrt(2)*gf*mi)
        mapped=-4*math.sqrt(2)*gf/e*A.conjugate()
        # Preserve the literal source mismatch. Direct outer matching (separate
        # audit tests) gives -mapped; no sign is chosen from this comparison.
        np.testing.assert_allclose(out,-mapped,rtol=2e-13)
        self.assertGreater(np.linalg.norm(out-mapped),np.linalg.norm(out))
        # Eq18 signed leading log becomes the positive Module3 internal flip.
        C=np.zeros((3,3),complex);C[0,1]=ext[0];C[1,1]=.2
        native=core.neutral_dipole(C,m,1,0,ML)[0]
        rhs=-e*ML[1]/(32*math.pi**2*m*m)*(C[0,1]*C[1,1]*(math.log((ML[1]/m)**2)+1.5)).conjugate()
        mapped_loop=2/(e*ML[1])*rhs.conjugate()
        external_flip=C[0,1]*C[1,1]*core.kernels((ML[1]/m)**2)[0]/(16*math.pi**2*m*m)
        self.assertLess(abs((native-external_flip)/mapped_loop-1),3e-7)
        EVIDENCE['davidson_to_module3_overall_sign']=-1
        EVIDENCE['davidson_literal_opposite_physical_relative_residual']=float(max(abs((out+mapped)/out)))

    def test_charge_squared_color_chirality_and_pseudo_i_falsifiers(self):
        ext=(.04+.01j,.02-.03j)
        args=(ext,.2+.3j,172.,450.,.106,.0073)
        a,_=fermion_component(*args,3,2/3)
        b,_=fermion_component(*args,1,1)
        np.testing.assert_allclose(a,4/3*b,rtol=2e-15)
        c,_=fermion_component(*args,3,-2/3)
        np.testing.assert_array_equal(a,c)
        flipped,_=fermion_component(ext[::-1],(.2+.3j).conjugate(),172.,450.,.106,.0073,3,2/3)
        np.testing.assert_allclose(a,flipped[::-1],rtol=2e-15)
        pseudo,_=fermion_component((1,1),1j,172.,450.,.106,.0073,3,2/3)
        self.assertEqual(pseudo[0],-pseudo[1]);self.assertLess(pseudo[0].imag,0)
        scalar,_=fermion_component((1,1),1.,172.,450.,.106,.0073,3,2/3)
        self.assertLess(scalar[0].real,0)
        self.assertGreater(abs(pseudo[0]-scalar[0]),abs(scalar[0]))

    def test_all_witnesses_channels_complex_tau_and_rephasing(self):
        errors=[]
        phases=np.exp(1j*np.array([.43,-.7,1.2]));rotation=np.diag(phases)
        for inp,n in cases():
            D=decode(n['D']);p=inp['module2_input']['scalar']['record']['physical']
            self.assertGreater(abs(D[2,2].imag),0)
            for i,j in CHANNELS.values():
                base=rows(D,p,i,j);changed=rows(rotation.conj()@D@rotation,p,i,j)
                for key,r in base.items():
                    for c in ('C_L','C_R'):
                        expected=phases[j].conjugate()*phases[i]*r[c]
                        errors.append(abs(changed[key][c]-expected)/max(abs(expected),1e-40))
        self.assertLess(max(errors),2e-11)
        EVIDENCE['six_NO_IO_witnesses_rephasing_max_relative']=float(max(errors))

    def test_legacy_fermion_and_W_signed_comparison_after_A_field_rephase(self):
        D=decode(cases()[0][1]['D']);p=P;Y=D/math.sqrt(2)
        def old_scalars(Y,**kw):
            d=Y*math.sqrt(2);vs=core.vertices(d,p,ML)
            return [(C if s!='A' else -C,m) for s,(C,m) in vs.items()]
        ns={'math':math,'np':np,'VEV':p['v'],'ALPHA_EM':.0072973525692838015,
            'FERMIONS':{'top':(172.5,3,2/3),'bottom':(4.18,3,-1/3),'tau':(ML[2],1,-1)},
            'LEPTON_MASSES':ML,'scalar_couplings':old_scalars,
            'scalar_f':lambda z:(kernels(z)[0][0],0),'pseudoscalar_g':lambda z:(kernels(z)[0][1],0)}
        pure_functions('reference/lfv/scripts/zee_barr_zee_fermion_dipoles.py',{'quark_chiral_couplings','flav_bz_amplitudes'},ns)
        errors=[]
        for i,j in CHANNELS.values():
            old=np.array(ns['flav_bz_amplitudes'](p,Y,parent=i,daughter=j)[:2])
            subset={k:r for k,r in rows(D,p,i,j).items() if r['loop_species'] in ('top','bottom','tau')}
            new=diagnostic_sum(subset)
            errors.append(float(np.linalg.norm(new-old)/np.linalg.norm(new)))
            self.assertGreater(np.linalg.norm(new+old),np.linalg.norm(new))
        self.assertLess(max(errors),1e-12)
        EVIDENCE['legacy_fermion_physical_same_sign_max_relative']=max(errors)
        ns.update({'lru_cache':lru_cache,'quad':__import__('scipy.integrate',fromlist=['quad']).quad,
                   'MW_GEV':80.379,'MASSES':ML})
        pure_functions('reference/lfv/scripts/zee_gateD4_W_photon_barr_zee_27.py',
                       {'independent_h_integral','photon_W_kernel','w_photon_amplitudes'},ns)
        old=np.array(ns['w_photon_amplitudes'](p,Y,parent=1,daughter=0)[:2])
        new=diagnostic_sum({k:r for k,r in rows(D).items() if '_W_' in k})
        error=float(np.linalg.norm(new+old)/np.linalg.norm(new))
        self.assertLess(error,2e-12)
        EVIDENCE['legacy_W_after_required_overall_minus_relative']=error

    def test_aligned_HA_interference_top_add_bottom_cancel(self):
        p=dict(P,alpha=P['beta'],mh2=600.,ma=600.)
        d=np.zeros((3,3),complex);d[0,1]=.02+.03j
        r=rows(d,p)
        top=r['A_top_gamma']['C_L']/r['H_top_gamma']['C_L']
        bottom=r['A_bottom_gamma']['C_L']/r['H_bottom_gamma']['C_L']
        self.assertGreater(top.real,0);self.assertLess(bottom.real,0)
        self.assertLess(abs(top.imag)+abs(bottom.imag),1e-14)
        EVIDENCE['aligned_A_over_H_top_bottom']=[float(top.real),float(bottom.real)]

    def test_W_CHK_equations_goldstone_term_and_cancellation(self):
        errs=[]
        for z in (.0001,.01,.25,.413,1.,10.):
            f,g,h=analytic(z)
            ref=3*f+5*g+.75*(g+h)+(f-g)/(2*z)
            value,error=w_kernel(z)
            errs.append(abs(value/ref-1));self.assertGreaterEqual(error,0)
        self.assertLess(max(errs),2e-12)
        d=np.ones((3,3),complex)*(.02+.01j)
        for p in (dict(P,alpha=P['beta']),dict(P,mh2=P['mh1'])):
            w={k:r for k,r in rows(d,p).items() if '_W_' in k}
            self.assertLess(np.linalg.norm(diagnostic_sum(w)),2e-22)
            self.assertFalse(any(r['scalar']=='A' for r in w.values()))
        EVIDENCE['W_CHK14_plus18_max_relative']=max(errs)

    def test_decoupling_mass_scaling_and_massless_fermion_limit(self):
        d=np.zeros((3,3),complex);d[0,1]=.02j
        vals=[]
        for m in (1000.,10000.,100000.):
            p=dict(P,mh2=m,ma=m,alpha=P['beta']-.2*(1000/m)**2)
            vals.append(np.linalg.norm(diagnostic_sum(rows(d,p))))
        self.assertGreater(vals[0],vals[1]);self.assertGreater(vals[1],vals[2])
        # With a Yukawa proportional to m_f, the loop vanishes as m_f -> 0.
        a,_=fermion_component((1,1),1e-3/246.,1e-3,400.,1.,.0073,1,1)
        b,_=fermion_component((1,1),1e-4/246.,1e-4,400.,1.,.0073,1,1)
        self.assertLess(np.linalg.norm(b)/np.linalg.norm(a),.02)
        a,_=fermion_component((1,1),.2+.1j,172.,400.,1.,.0073,3,2/3)
        b,_=fermion_component((1,1),.2+.1j,344.,800.,2.,.0073,3,2/3)
        np.testing.assert_allclose(b,a/4,rtol=2e-15)

    def test_coherent_interference_rejects_operator_and_basis_mismatch(self):
        d=decode(cases()[0][1]['D']);r=rows(d)
        candidate=r['h_W_gamma']
        with self.assertRaises(ValueError):combine({'unvalidated':candidate})
        a=dict(candidate,validation_status='VALIDATION_PASS');b=copy.deepcopy(a)
        b['C_L']=-a['C_L'];b['C_R']=-a['C_R']
        np.testing.assert_array_equal(combine({'a':a,'b':b}),[0,0])
        self.assertGreater(core.radiative_width(np.array([a['C_L'],a['C_R']]),1.,0.,.0073),0)
        for key,value in [('operator_convention','oldA'),('basis','other'),('validation_status','UNKNOWN'),('loop_order',3)]:
            bad=dict(b);bad[key]=value
            with self.assertRaises(ValueError):combine({'a':a,'bad':bad})


class NativeAndFoundationAuditTests(unittest.TestCase):
    def test_independent_ilisie_signed_source_conflict_is_not_hidden(self):
        from scipy.integrate import quad
        ratios=[]
        for cp in ('scalar','pseudoscalar'):
            m,mf,M,v,alpha=ML[1],172.5,400.,P['v'],.0073
            phase=1 if cp=='scalar' else -1j
            c,_=fermion_component((phase*m/v,phase.conjugate()*m/v),phase*mf/v,mf,M,m,alpha,3,2/3)
            # Keep a reproducible record of the old literal Davidson candidate.
            source_davidson=-m*m*sum(c).real
            z=(mf/M)**2
            def integrand(x):
                u=x*(1-x)
                return z/2*((2*u-1) if cp=='scalar' else 1)*math.log(z/u)/(z-u)
            ilisief=quad(integrand,0,1,epsabs=1e-12,epsrel=1e-12)[0]
            source_ilisie=alpha*m*m/(4*math.pi**3*v*v)*3*(2/3)**2*ilisief
            ratio=source_davidson/source_ilisie
            self.assertAlmostEqual(ratio,-1,delta=2e-12)
            ratios.append(ratio)
        z=.413
        def w_integrand(x):
            u=x*(1-x)
            return .5*(x*(3*x*(4*x-1)+10)*z-u)/(z-u)*math.log(z/u)
        f3=quad(w_integrand,0,1,epsabs=1e-11,epsrel=1e-12)[0]
        ratio=-w_kernel(z)[0]/f3
        self.assertLess(ratio,-1.001)
        EVIDENCE['SOURCE_CONFLICT']={'fermion_scalar_and_pseudo_Davidson_over_Ilisie':ratios,
            'W_Davidson_over_Ilisie_at_z_0p413':ratio,
            'resolution':'Fermion physical sign fixed by independent outer matching; literal Davidson source sign retained as conflict. W excluded.',
            'qualification':'Ilisie transverse W form factor discards gauge-dependent non-Barr-Zee terms; no claim these are the same complete EW subset'}

    def test_charged_scalar_form_factor_and_photon_Ward_tensor(self):
        errors=[]
        for z in (.01,.1,.25,.413,1.,100.):
            f,g,_=analytic(z);expected=(f-g)/(2*z)
            value,error=charged_scalar_kernel(z)
            errors.append(abs(value/expected-1));self.assertGreaterEqual(error,0)
        self.assertLess(max(errors),1e-11)
        # Ilisie Eq9, q is the on-shell external photon. Both contractions
        # vanish for the transverse effective tensor, irrespective of S.
        metric=np.diag([1.,-1.,-1.,-1.]);q=np.array([2.,0.,0.,2.]);k=np.array([3.,.2,-.7,.9])
        tensor=metric*(k@metric@q)-np.outer(k,q)
        residual=max(np.max(abs((q@metric)@tensor)),np.max(abs(tensor@(metric@k))))
        self.assertLess(residual,1e-14)
        EVIDENCE['charged_scalar_F2_vs_analytic_max_relative']=max(errors)
        EVIDENCE['effective_transverse_tensor_Ward_residual']=float(residual)
        EVIDENCE['charged_scalar_amplitude']='UNKNOWN_NOT_IMPLEMENTED; F2 and native trilinears are not a matched LFV amplitude'

    def test_scalar_trilinears_independent_polynomial_derivatives(self):
        import sympy as s
        # Gauge invariants, with independent charged +/- variables. This is
        # differentiation of V, not transcription of SARAH vertex expressions.
        v1,v2,h1,h2,a1,a2,c1,c2,sm,p1,p2,sp=s.symbols('v1 v2 h1 h2 a1 a2 c1 c2 sm p1 p2 sp',real=True)
        l1,l2,l3,l4,l5,k1,k2,k12,mu=s.symbols('l1 l2 l3 l4 l5 k1 k2 k12 mu',real=True)
        x1=c1*p1+((v1+h1)**2+a1*a1)/2;x2=c2*p2+((v2+h2)**2+a2*a2)/2
        z12=c1*p2+(v1+h1-s.I*a1)*(v2+h2+s.I*a2)/2
        z21=c2*p1+(v2+h2-s.I*a2)*(v1+h1+s.I*a1)/2
        V=l1*x1*x1/2+l2*x2*x2/2+l3*x1*x2+l4*z12*z21+l5*(z12*z12+z21*z21)/2
        V+=sm*sp*(k1*x1+k2*x2-k12*(z12+z21))
        V+=mu/s.sqrt(2)*(sm*(p1*(v2+h2+s.I*a2)-(v1+h1+s.I*a1)*p2)+sp*(c1*(v2+h2-s.I*a2)-(v1+h1-s.I*a1)*c2))
        zero={x:0 for x in (h1,h2,a1,a2,c1,c2,sm,p1,p2,sp)}
        tensors=[s.Matrix([[s.diff(V,x,y,h).subs(zero) for y in (p1,p2,sp)] for x in (c1,c2,sm)]) for h in (h1,h2,a1,a2)]
        evaluate=s.lambdify((v1,v2,l1,l2,l3,l4,l5,k1,k2,k12,mu),tensors,'numpy')
        errors=[]
        for inp,n in cases():
            p=inp['module2_input']['scalar']['record']['physical'];q,_,_=reconstruct(p)
            args=[p['v']*math.cos(p['beta']),p['v']*math.sin(p['beta'])]+[q[k] for k in ('Lambda1','Lambda2','Lambda3','Lambda4','Lambda5','K1','K2','K12','Mu4')]
            tensors=evaluate(*args);zh,za,zp=rotations(p);got=trilinears(p,q)
            for cp,spec in enumerate(('h','H','A')):
                rot=zh[cp] if cp<2 else za[1];start=0 if cp<2 else 2
                ref=zp@(rot[0]*tensors[start]+rot[1]*tensors[start+1])@zp.T
                errors.append(float(np.max(abs(ref-got[spec]))))
        self.assertLess(max(errors),2e-12)
        EVIDENCE['scalar_trilinears_vs_polynomial_max_abs_GeV']=max(errors)

    def test_signed_one_loop_and_tree_reference_discrepancies(self):
        # Charged scalar with neutral massless fermion: direct positive
        # Feynman-parameter integral 1/12 and common C=-sigma/(i m).
        from scipy.integrate import quad
        d=np.zeros((3,3),complex);d[1,1]=.2
        p=dict(P,gamma=0)
        r=core.dipole_ledger(np.zeros((3,3)),d,p,ML,1,1)
        amu=ML[1]**2*(r['H1_D']['C_L']+r['H1_D']['C_R']).real
        ref=-abs(d[1,1])**2*ML[1]**2/(8*math.pi**2*p['mH1']**2)*quad(lambda x:x*x*(1-x),0,1)[0]
        self.assertLess(abs(amu/ref-1),2e-15)
        # Independent massless direct chiral contact rate; both LL and LR
        # enter for a real diagonal b coupling. No J^2 half survives matching.
        c=np.zeros((3,3),complex);c[0,2]=.2+.1j;c[1,1]=.3
        value=tree.width({'s':(c,200.)},2,0,1,np.array([0.,0.,1.]),18,True)
        expected=2*abs(c[0,2]*c[1,1])**2/(6144*math.pi**3*200**4)
        err=abs(value/expected-1);self.assertLess(err,2e-13)
        EVIDENCE['tree_contact_relative_residual']=err
        EVIDENCE['legacy_tree_same_vertex_rate_correction']=4.
        EVIDENCE['legacy_A1_sign_arbitration']='A1c F same; A1e neutral and A1f D opposite; native vertices and common charge/operator fix Module3 component signs'


if __name__=='__main__':unittest.main()
