"""Independent numerical physics controls; existing cards and analytic limits only."""
import copy
import json
import math
from pathlib import Path
import unittest
import mpmath as mp
import numpy as np
from scipy.integrate import dblquad
from module1.scalar_constraints import reconstruct
from module1.d10_polynomial import evaluate, NAMES
from module4.couplings import rotations, trilinears
from module4.charged_scalar import scalar_qed_tensor
from module13.higgstools import inputs
from research.full_constraints.higgs.diphoton import amplitude, benchmark, loops, MASSES, HT_MASSES, ALPHA_TREE
from research.full_constraints.higgs.coverage import classify, require, sha, ROOT

EVIDENCE={}
DATASET=Path('/tmp/zee-d14c-dataset.json')


def integral_loops(t):
    """2HDMC Eq.28 logarithmic Feynman integral, independent of asin/acosh."""
    with mp.workdps(65):
        t=mp.mpf(str(t));points=[mp.mpf(0),mp.mpf('.5'),mp.mpf(1)]
        if t>1:
            root=mp.sqrt(1-1/t);points=[0,(1-root)/2,mp.mpf('.5'),(1+root)/2,1]
        def integrand(y):
            if y==0:return -4*t
            z=1-4*t*y*(1-y)
            if z==0:return 0 # measure-zero endpoint; quadrature never needs its value
            return (mp.log(abs(z))-(1j*mp.pi if z<0 else 0))/y
        f=-mp.quad(integrand,points)/2
        return tuple(complex(x) for x in ((f-t)/t**2,2*(t+(t-1)*f)/t**2,
                                         -(2*t*t+3*t+3*(2*t-1)*f)/t**2,2*f/t))


class DiphotonTests(unittest.TestCase):
    def test_all_spin_functions_vs_independent_log_integral(self):
        residual=[]
        for t in (1e-8,1e-5,.01,.13,.605,.99,1.,1.01,4.,1e4,1e10):
            a=np.asarray(loops(t));b=np.asarray(integral_loops(t))
            residual.append(float(max(abs((a-b)/b))))
        EVIDENCE['loop_vs_log_integral_max_relative']=max(residual)
        self.assertLess(max(residual),2e-11)

    def test_scalar_and_fermion_triangle_parameters(self):
        residual=[]
        for mass in (80.379,172.4,298.7266553444879,532.9329127809378,873.2076828282773):
            t=(125/(2*mass))**2
            a0=dblquad(lambda y,x:8*x*y/(1-4*t*x*y),0,1,lambda x:0,lambda x:1-x,epsabs=2e-12)[0]
            af=dblquad(lambda y,x:4*(1-4*x*y)/(1-4*t*x*y),0,1,lambda x:0,lambda x:1-x,epsabs=2e-12)[0]
            ap=dblquad(lambda y,x:4/(1-4*t*x*y),0,1,lambda x:0,lambda x:1-x,epsabs=2e-12)[0]
            got=loops(t);residual.extend(abs(got[i]-v) for i,v in [(0,a0),(1,af),(3,ap)])
        EVIDENCE['triangle_parameter_max_abs']=max(residual)
        self.assertLess(max(residual),2e-12)

    def test_D12_complete_complex_amplitudes_independent_parameters(self):
        residual=[]
        for name in ('D7','F13'):
            record,w=inputs(name);p=record['input']['physical'];out=benchmark(p,w)
            even=out['kV']*integral_loops((p['mh1']/(2*MASSES['W']))**2)[2];odd=0j
            for f,k in out['kappas'].items():
                ref=integral_loops((p['mh1']/(2*MASSES[f]))**2)
                weight=4/3 if f in ('u','c','t') else 1/3 if f in ('d','s','b') else 1
                even+=weight*k.real*ref[1];odd+=weight*k.imag*ref[3]
            for mass,g,q in out['charged']:
                t=(p['mh1']/(2*mass))**2
                a0=dblquad(lambda y,x:8*x*y/(1-4*t*x*y),0,1,lambda x:0,lambda x:1-x,epsabs=2e-12)[0]
                even+=q*q*g*p['v']/(2*mass*mass)*a0
            residual.extend([abs(even-out['full']['even']),abs(odd-out['full']['odd'])])
            refwidth=ALPHA_TREE**2*p['mh1']**3/(256*math.pi**3*p['v']**2)*(abs(even)**2+abs(odd)**2)
            self.assertAlmostEqual(refwidth/out['full']['width_GeV'],1,delta=2e-13)
        EVIDENCE['D12_complete_complex_amplitude_max_abs']=float(max(residual))
        self.assertLess(max(residual),2e-12)

    def test_inverse_tau_published_sign_and_two_state_sum(self):
        # Bhattacharyya-Das Eqs.3-5 use +AW, -At and kappa=-g*v/(2m^2).
        # Compare full signed tensor to minus our convention, not just |A|^2.
        k={f:0 for f in MASSES if f!='W'};k['t']=1
        charged=[(300.,120.,1),(900.,-310.,1)]
        out=amplitude(125,1,k,charged)
        def f(inv):return math.asin(1/math.sqrt(inv))**2
        tw=(2*MASSES['W']/125)**2;tt=(2*MASSES['t']/125)**2
        ref=2+3*tw+3*tw*(2-tw)*f(tw)-(4/3)*2*tt*(1+(1-tt)*f(tt))
        for mass,g,q in charged:
            ts=(2*mass/125)**2
            ref+=(-g*246.21965/(2*mass*mass))*(-ts*(1-ts*f(ts)))
        self.assertAlmostEqual(ref,-out['even'].real,delta=2e-12)

    def test_sm_and_independent_compiled_HiggsTools_even_amplitude(self):
        import Higgs.predictions as HP
        residual=[]
        for ku,kd,kl,kv in [(1,1,1,1),(.9,1.2,.7,.98),(-1,1,1,1)]:
            c=HP.NeutralEffectiveCouplings();k={}
            for fs,val in [(('u','c','t'),ku),(('d','s','b'),kd),(('e','mu','tau'),kl)]:
                for f in fs:k[f]=val
            for attr,val in [('uu',ku),('cc',ku),('tt',ku),('dd',kd),('ss',kd),('bb',kd),('ee',kl),('mumu',kl),('tautau',kl)]:setattr(c,attr,complex(val))
            c.WW=c.ZZ=kv
            pred=HP.Predictions();h=pred.addParticle(HP.NeutralScalar('h',HP.CP.even));h.setMass(125)
            HP.effectiveCouplingInput(h,c,reference=HP.ReferenceModel.SMHiggsEW)
            refpred=HP.Predictions();sm=refpred.addParticle(HP.NeutralScalar('h',HP.CP.even));sm.setMass(125)
            HP.effectiveCouplingInput(sm,HP.smLikeEffCouplings,reference=HP.ReferenceModel.SMHiggsEW)
            target=h.br(HP.Decay.gamgam)*h.totalWidth()/(sm.br(HP.Decay.gamgam)*sm.totalWidth())
            ours=amplitude(125,kv,k,masses=HT_MASSES)['norm']/amplitude(125,1,{f:1 for f in k},masses=HT_MASSES)['norm']
            residual.append(abs(target-ours));self.assertAlmostEqual(target,ours,delta=2e-12)
        EVIDENCE['HiggsTools_compiled_even_ratio_max_abs']=max(residual)
        base=amplitude(125,1,{f:1 for f in MASSES if f!='W'})
        EVIDENCE['SM_one_loop_width_GeV']=base['width_GeV'];EVIDENCE['SM_even_amplitude']=[base['even'].real,base['even'].imag]
        self.assertTrue(9e-6<base['width_GeV']<1.1e-5)
        self.assertLess(base['even_terms']['W'].real,0)
        self.assertGreater(base['even_terms']['t'].real,0)

    def test_cp_odd_tau_not_doubled_mu_and_no_unpolarized_interference(self):
        k={f:0 for f in MASSES if f!='W'};k['tau']=1j
        out=amplitude(125,0,k)
        self.assertEqual(out['even'],0);self.assertNotEqual(out['odd'],0)
        self.assertEqual(out['odd_terms']['mu'],0)
        k['tau']=-1j
        self.assertEqual(out['norm'],amplitude(125,0,k)['norm'])
        k['tau']=1
        a=amplitude(125,1,k);k['tau']=1+1j;b=amplitude(125,1,k)
        self.assertAlmostEqual(b['norm'],a['norm']+out['norm'],delta=1e-13)
        # Numerical falsifier of the pinned source's omitted odd tau term.
        import Higgs.predictions as HP
        pr=HP.Predictions();h=pr.addParticle(HP.NeutralScalar('h',HP.CP.even));h.setMass(125)
        c=HP.NeutralEffectiveCouplings();c.tautau=1j
        HP.effectiveCouplingInput(h,c,reference=HP.ReferenceModel.SMHiggsEW)
        native_width=h.br(HP.Decay.gamgam)*h.totalWidth()
        self.assertEqual(native_width,0)
        self.assertGreater(out['width_GeV'],0)
        EVIDENCE['pinned_HiggsTools_tau_only_CPodd_gamma_width_GeV']=native_width
        EVIDENCE['independent_tau_only_CPodd_gamma_width_GeV']=out['width_GeV']

    def test_trilinears_vs_independent_expanded_potential_on_D12_cards(self):
        residual=[]
        for name in ('D7','F13'):
            record,w=inputs(name);p=record['input']['physical'];q,_,_=reconstruct(p)
            zh,_,zp=rotations(p);r=np.zeros(10);r[2]=p['v']*math.cos(p['beta']);r[6]=p['v']*math.sin(p['beta'])
            direction=np.zeros(10);direction[2],direction[6]=zh[0]
            # Hessian is quadratic; central derivative is exact up to roundoff.
            eps=.25
            plus=evaluate(r+eps*direction,q)[2];minus=evaluate(r-eps*direction,q)[2]
            ref=zp@((plus-minus)/(2*eps))[np.ix_([0,4,8],[0,4,8])]@zp.T
            got=trilinears(p,q)['h'];residual.append(float(np.max(abs(ref-got))))
            self.assertLess(residual[-1],2e-9)
        EVIDENCE['D12_trilinear_polynomial_max_abs_GeV']=max(residual)

    def test_scalar_qed_Ward_Bose_and_seagull_cancellation(self):
        p=np.array([.3,-.2,.4,.1]);q=np.array([.1,.3,-.1,.4])
        a,b=scalar_qed_tensor(p,q,order=40);t=a+b
        residual=max(np.max(abs(p@t)),np.max(abs(t@q)))
        t2=sum(scalar_qed_tensor(q,p,order=40))
        EVIDENCE['scalar_QED_Ward_max_abs']=float(residual)
        self.assertLess(residual,2e-13);self.assertLess(np.max(abs(t-t2.T)),2e-13)
        self.assertGreater(np.max(abs(p@a)),1e-3)

    def test_polarization_width_normalization_and_identical_photons(self):
        mh=125.;alpha=1/137.035999084;v=246.21965;s=-6.4+.07j
        metric=np.diag([1.,-1.,-1.,-1.]);p=np.array([mh/2,0,0,mh/2]);q=np.array([mh/2,0,0,-mh/2])
        tensor=(p@metric@q)*metric-np.outer(q,p)
        pol=[np.array([0.,1,0,0]),np.array([0.,0,1,0])]
        squared=sum(abs(alpha*s/(2*math.pi*v)*(e@tensor@f))**2 for e in pol for f in pol)
        width=squared/(32*math.pi*mh) # includes identical photons 1/2!
        ref=alpha**2*mh**3*abs(s)**2/(256*math.pi**3*v*v)
        self.assertAlmostEqual(width/ref,1,delta=5e-16)
        EVIDENCE['polarization_width_relative_residual']=abs(width/ref-1)

    def test_charge_sign_coherence_and_fixed_trilinear_decoupling(self):
        k={f:1 for f in MASSES if f!='W'}
        a=amplitude(125,1,k,[(500,100,1),(800,-200,1)])
        b=amplitude(125,1,k,[(800,-200,-1),(500,100,-1)])
        self.assertAlmostEqual(a['norm'],b['norm'],delta=1e-14)
        c=amplitude(125,1,k,[(500,-100,1),(800,200,1)])
        self.assertGreater(abs(a['norm']-c['norm']),.01)
        base=amplitude(125,1,k)['even']
        d1=amplitude(125,1,k,[(1e4,100,1)])['even']-base
        d2=amplitude(125,1,k,[(1e5,100,1)])['even']-base
        self.assertAlmostEqual((d1/d2).real,100,delta=.003)
        EVIDENCE['fixed_trilinear_decoupling_amplitude_ratio']=(d1/d2).real

    def test_mixing_endpoints_equal_mass_and_trace(self):
        # Analytic model-limit controls; no new physical benchmark proposals.
        g=np.diag([30.,80.]);m=500.;v=246.21965;t=(125/(2*m))**2
        vals=[]
        for angle in (0.,math.pi/2,-math.pi/2,.71):
            c,s=math.cos(angle),math.sin(angle);r=np.array([[c,s],[-s,c]])
            rotated=r@g@r.T
            vals.append(np.trace(rotated)*v/(2*m*m)*loops(t)[0])
        self.assertLess(max(abs(x-vals[0]) for x in vals),1e-16)
        self.assertAlmostEqual(loops(1e-10)[0].real,1/3,delta=2e-11)
        self.assertAlmostEqual(loops(1e-10)[1].real,4/3,delta=4e-11)
        self.assertAlmostEqual(loops(1e-10)[2].real,-7,delta=2e-10)
        # EFT low energy theorem: A_s -> (v/6) d log det M^2 / dh.
        expected=v/6*np.trace(g)/m**2
        got=np.trace(g)*v/(2*m*m)*loops(1e-10)[0]
        self.assertAlmostEqual(got.real/expected,1,delta=1e-10)

    def test_fail_closed_nonfinite_missing_and_nonhermitian(self):
        k={f:1 for f in MASSES if f!='W'}
        for bad in (0,-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):amplitude(bad,1,k)
        with self.assertRaises(ValueError):amplitude(125,1,{},[])
        with self.assertRaises(ValueError):amplitude(125,1,k,[(500,1j,1)])
        with self.assertRaises(ValueError):amplitude(125,1,k,[(500,1,float('nan'))])


class CoverageTests(unittest.TestCase):
    def test_exact_rate_bridge_rejects_energy_pdf_charge_and_family_tampering(self):
        from research.full_constraints.higgs.study import bound_rate
        m=json.loads((ROOT/'module14/conditional_scan/production_map_13_14.json').read_text())
        dataset=DATASET
        if not dataset.exists():self.fail('Original fixed-card dataset required for rate bridge check')
        require(sha(dataset)==m['dataset_sha256'],'Wrong saved dataset')
        f=next(f for f in m['families'] if f['energy_TeV']==13)
        rate=next(r for r in m['rates'] if r['energy_TeV']==13 and r['id']==f['id'])
        row=next(r for r in json.loads(dataset.read_text())['rows'] if r['id']==f['id'] and r['neutrino']['input_sha256']==f['module2_input_sha256'])
        self.assertGreater(bound_rate(rate,f,row)['sigma_pb'],0)
        for key,bad in [('energy_TeV',14),('pdf','wrong'),('charge_definition','H2plus_only'),('sigma_pb',rate['sigma_pb']*2),('muF_GeV',1)]:
            changed=copy.deepcopy(rate);changed[key]=bad
            with self.assertRaises(ValueError):bound_rate(changed,f,row)
        changed=copy.deepcopy(f);changed['yukawa_sha256']['F']='tampered'
        with self.assertRaises(ValueError):bound_rate(rate,changed,row)
        changed=copy.deepcopy(rate);key=next(iter(changed['source_sha256']));changed['source_sha256'][key]='tampered'
        with self.assertRaises(ValueError):bound_rate(changed,f,row)

    def test_width_replacement_preserves_sum_without_inclusive_inv_double_count(self):
        import Higgs.predictions as HP
        from module13.higgstools import h125
        r,w=inputs('D7');pr=HP.Predictions();h125(pr,r['input']['physical'],w);h=pr.particle('h')
        before=h.totalWidth();old=h.br(HP.Decay.gamgam)*before
        h.setDecayWidth(HP.Decay.gamgam,2*old)
        self.assertAlmostEqual(h.totalWidth(),before+old,delta=2e-17)
        self.assertAlmostEqual(sum(h.br(d) for key,d in HP.Decay.__members__.items() if key not in ('none','inv')),1,delta=2e-15)
        self.assertGreater(sum(h.br(d) for d in HP.Decay.__members__.values()),1)

    def test_mass_only_rejection_and_tree_zero_is_not_loop_zero(self):
        d=dict(category='singleCharge',limitClass='ChannelLimit',grid_axes={'mass':[200,1000]},process={'channels':[['vbfHpm','WZ']]},collider='LHC13')
        p=inputs('D7')[0]['input']['physical'];c=dict(physical=p,production_available=[])
        self.assertEqual(classify(d,c)['status'],'MISSING_PREDICTION')
        d['grid_axes']={'mass':[50,100]};self.assertEqual(classify(d,c)['status'],'NOT_APPLICABLE')
        d['grid_axes']={'mass':[200,1000]};d['process']={'channels':[['Hpmtb','tb']]};c['production_available']=['H2:Hpmtb:LHC13']
        out=classify(d,c);self.assertEqual(out['central_LO_two_body_inputs_available'],['H2'])
        self.assertEqual(out['status'],'MISSING_PREDICTION')

    def test_pinned_datasets_all_limits_and_unknowns(self):
        p=ROOT/'research/full_constraints/higgs/COVERAGE.json'
        if not p.exists():self.skipTest('Run coverage inventory before final persisted-artifact check')
        r=json.loads(p.read_text());self.assertEqual(len(r['limits']),310)
        self.assertEqual(len({x['id'] for x in r['limits']}),310)
        self.assertEqual(sum(x['n_observables'] for x in r['measurements']),159)
        self.assertEqual(len(r['cases']),18)
        for x in r['limits']:
            self.assertEqual(len(x['cases']),18)
            self.assertEqual(sha(Path(r['datasets']['HB']['path'])/x['file']),x['sha256'])
        self.assertIsNone(r['global_acceptance'])
        require(True,'test')
        with self.assertRaises(ValueError):require(False,'tampered identity')

if __name__=='__main__':unittest.main(verbosity=2)
