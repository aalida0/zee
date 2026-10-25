"""Independent scalar-QED diagrams, signed sources, mixing and LFV regression."""
import copy
import json
import math
from pathlib import Path
import unittest
import numpy as np
from scipy.integrate import quad
from module1.scalar_constraints import reconstruct
from module2.interface import canonical_hash,decode
from module3 import core
from module4.charged_scalar import (component,ledger,scalar_loop_kernel,
    scalar_qed_tensor,euclidean_scalar_kernel,mass_basis_trace)
from module4.couplings import trilinears,rotations
from module4.interface import evaluate
from module4.amplitudes import combine,CHANNELS
from module4.matching_audit import outer_projection
from test_module4_physics import cases,ML,P,EXTRA,analytic,rows,ROOT

EVIDENCE={}


class ChargedScalarTests(unittest.TestCase):
    def test_two_triangle_seagull_Ward_Bose_and_convergence(self):
        residuals=[];without=[];convergence=[]
        for p,q,m in [(np.array([.2,.3,-.4,.1]),np.array([1.,.3,.2,-.2]),1.),
                      (np.array([-.3,.5,.1,.2]),np.array([.7,-.4,.2,1.1]),1.3),
                      (np.array([.9,.1,.3,-.2]),np.array([-.2,.8,.4,.5]),.7)]:
            triangle,seagull=scalar_qed_tensor(p,q,m,32);total=triangle+seagull
            swapped=sum(scalar_qed_tensor(q,p,m,32)).T
            residuals.extend([float(max(abs(p@total))),float(max(abs(total@q))),float(np.max(abs(total-swapped)))])
            without.append(float(max(abs(p@triangle))))
            # Doubling the seagull factor also falsifies the identity.
            self.assertGreater(max(abs(p@(triangle+2*seagull))),.01)
            convergence.append(float(np.max(abs(total-sum(scalar_qed_tensor(p,q,m,48))))))
            np.testing.assert_allclose(sum(scalar_qed_tensor(2*p,2*q,2*m)),total,rtol=2e-12,atol=1e-14)
        self.assertLess(max(residuals),2e-13)
        self.assertLess(max(convergence),2e-13)
        self.assertGreater(min(without),.01)
        EVIDENCE['full_scalar_QED_Ward_Bose_max_abs']=max(residuals)
        EVIDENCE['scalar_QED_32_to_48_nodes_max_abs']=max(convergence)
        EVIDENCE['Ward_without_seagull_min_abs']=min(without)
        EVIDENCE['UV_constant_coefficients']={'triangle_1':1,'triangle_2':1,'seagull':-2,'sum':0}

    def test_transverse_soft_vertex_from_diagrams_not_projection(self):
        errors=[];convergence=[]
        for k in (np.array([1.,.3,.2,-.2]),np.array([.2,-.8,.1,.5])):
            direction=np.array([.2,.3,-.4,.1])
            target=np.eye(4)*(direction@k)-np.outer(k,direction)
            coefficient=2*quad(lambda x:x*(1-x)/(1+x*(1-x)*(k@k)),0,1,epsabs=1e-13)[0]
            expected=coefficient*target
            last=None
            for eps in (1e-3,5e-4):
                got=(sum(scalar_qed_tensor(eps*direction,k))-sum(scalar_qed_tensor(-eps*direction,k)))/(2*eps)
                errors.append(float(np.max(abs(got-expected))))
                if last is not None:convergence.append(float(np.max(abs(got-expected))/np.max(abs(last-expected))))
                last=got
        self.assertLess(max(errors),6e-9)
        self.assertTrue(all(.20<v<.30 for v in convergence))
        EVIDENCE['soft_vertex_symmetric_derivative_max_abs']=max(errors)
        EVIDENCE['soft_derivative_half_step_error_ratios']=convergence

    def test_kernel_three_independent_representations_and_limits(self):
        errors=[];samples=[]
        for z in (.001,.1,.25,.413,1.,10.,100.):
            got,error=scalar_loop_kernel(z);f,g,_=analytic(z)
            parameter=euclidean_scalar_kernel(z)
            # Arhrib-Baek Eq.6; normalized with F2=-F_PRD/2.
            def fun(x):
                u=x*(1-x);t=(z-u)/u
                return u*(math.log1p(t)/(z-u) if abs(t)>1e-6 else (1-t/2+t*t/3)/u)
            published=quad(fun,0,1,epsabs=1e-12,epsrel=2e-12,limit=400)[0]
            errors.extend([abs(got/((f-g)/(2*z))-1),abs(got/parameter-1),abs(got/(-published/2)-1)])
            self.assertGreaterEqual(error,0);samples.append({'z':z,'F2':got,'F_PRD':published,'Euclidean':parameter})
        self.assertLess(max(errors),2e-10)
        small=1e-14;large=1e9
        self.assertLess(abs(scalar_loop_kernel(small)[0]/(1+math.log(small)/2)-1),1e-10)
        self.assertLess(abs(scalar_loop_kernel(large)[0]/(-(math.log(large)+5/3)/(12*large))-1),1e-9)
        EVIDENCE['scalar_kernel_independent_max_relative']=max(errors)
        EVIDENCE['kernel_source_samples']=samples

    def test_signed_Ilisie_and_PRD_diagonal_moment(self):
        errors=[];signs=[]
        alpha=1/137.035999084;v=P['v'];mi=ML[1];M=400.;mass=625.;charge=1.
        for g in (140.,-210.):
            c=mi/v*(1.3+.7j)
            coeff,_=component((c,c.conjugate()),g,mass,M,mi,alpha,charge)
            actual=mi*mi*sum(coeff).real
            z=(mass/M)**2
            F=quad(lambda x:x*(1-x)*math.log(z/(x*(1-x)))/(z-x*(1-x)),0,1,epsabs=1e-12)[0]
            ilisie=alpha*mi*mi/(8*math.pi**3*M*M)*1.3*(g/v)*(-F/2)
            GF=1/(math.sqrt(2)*v*v)
            prd=-alpha/(2*math.pi)*(GF*mi*mi/(4*math.sqrt(2)*math.pi**2))*1.3*(v*g)/(M*M)*F
            errors.extend([abs(actual/ilisie-1),abs(actual/prd-1)])
            signs.append(actual)
        self.assertLess(signs[0],0);self.assertGreater(signs[1],0)
        self.assertLess(max(errors),2e-12)
        # A scalar loop has no epsilon tensor. Purely axial external Yukawa
        # gives opposite imaginary chiral coefficients and zero magnetic moment.
        axial,_=component((.02j,-.02j),140.,mass,M,mi,alpha)
        self.assertEqual(sum(axial),0j);self.assertNotEqual(axial[0],0j)
        a,_=component((1,1),140.,mass,M,mi,alpha,2.)
        b,_=component((1,1),140.,mass,M,mi,alpha,-1.)
        np.testing.assert_allclose(a,4*b,rtol=1e-15)
        EVIDENCE['signed_gminus2_Ilisie_PRD_max_relative']=max(errors)
        EVIDENCE['gminus2_positive_negative_trilinear']=signs
        EVIDENCE['outer_matching_Dirac_residual']=max(outer_projection())

    def test_mass_basis_complex_unitary_and_offdiagonal_selection(self):
        errors=[];offdiag_sizes=[]
        rng=np.random.default_rng(7142)
        for inp,n in cases():
            p=inp['module2_input']['scalar']['record']['physical'];lag,_,_=reconstruct(p)
            G=trilinears(p,lag);mass=np.diag([p['mH1']**2,p['mH2']**2])
            U,_=np.linalg.qr(rng.normal(size=(2,2))+1j*rng.normal(size=(2,2)))
            for scalar,M in [('h',p['mh1']),('H',p['mh2']),('A',p['ma'])]:
                g=G[scalar][1:,1:]
                original=mass_basis_trace(mass,g,M)
                transformed=mass_basis_trace(U@mass@U.conj().T,U@g@U.conj().T,M)
                scale=max(abs(original),np.linalg.norm(g),1.)
                errors.append(abs(original-transformed)/scale)
                diagonal=np.diag(np.diag(g))
                errors.append(abs(original-mass_basis_trace(mass,diagonal,M))/scale)
                offdiag_sizes.append(abs(g[0,1]))
                if scalar=='A':self.assertLess(abs(original),2e-12)
        self.assertGreater(max(offdiag_sizes),1.)
        self.assertLess(max(errors),2e-13)
        EVIDENCE['unitary_basis_and_offdiagonal_max_relative']=float(max(errors))
        EVIDENCE['nonzero_offdiagonal_trilinear_max_GeV']=float(max(offdiag_sizes))

    def test_degenerate_mixing_and_decoupling_at_fixed_trilinear(self):
        for inp,n in cases()[:3]:
            p=inp['module2_input']['scalar']['record']['physical'];lag,_,_=reconstruct(p)
            G=trilinears(p,lag)['h'][1:,1:]
            M=450.;mass=np.eye(2)*500.**2
            expected=np.trace(G)*scalar_loop_kernel((500/M)**2)[0]
            np.testing.assert_allclose(mass_basis_trace(mass,G,M),expected,rtol=2e-15,atol=1e-14)
        values=[]
        for mass in (300.,3000.,30000.):
            values.append(np.linalg.norm(component((.02+.03j,.07-.01j),140.,mass,400.,ML[1],.0073)[0]))
        self.assertGreater(values[0],values[1]);self.assertGreater(values[1],values[2])
        a,_=component((.02+.03j,.07-.01j),140.,300.,400.,ML[1],.0073)
        b,_=component((.02+.03j,.07-.01j),280.,600.,800.,2*ML[1],.0073)
        np.testing.assert_allclose(b,a/4,rtol=2e-15)

    def test_all_NO_IO_rephasing_reverse_channels_and_coherence(self):
        errors=[];interference=[];representatives=[]
        phases=np.exp(1j*np.array([.37,-.74,1.19]));Pphase=np.diag(phases)
        for inp,n in cases():
            d,f=decode(n['D']),decode(n['F']);p=inp['module2_input']['scalar']['record']['physical']
            for channel,(i,j) in CHANNELS.items():
                charged=ledger(d,p,ML,.0073,i,j);shifted=ledger(Pphase.conj()@d@Pphase,p,ML,.0073,i,j)
                self.assertEqual(len(charged),6)
                for key,r in charged.items():
                    for c in ('C_L','C_R'):
                        expected=phases[j].conjugate()*phases[i]*r[c]
                        errors.append(abs(shifted[key][c]-expected)/max(abs(expected),1e-40))
                    if r['scalar']=='A':self.assertEqual(r['C_L'],0j);self.assertEqual(r['C_R'],0j)
                cs=combine(charged)
                previous=core.combine(core.dipole_ledger(f,d,p,ML,i,j))+combine({k:r for k,r in rows(d,p,i,j).items() if r['coherent_inclusion']})
                actual=core.radiative_width(previous+cs,ML[i],ML[j],.0073)
                separate=core.radiative_width(previous,ML[i],ML[j],.0073)+core.radiative_width(cs,ML[i],ML[j],.0073)
                expected=separate+.0073*ML[i]**5/2*(1-(ML[j]/ML[i])**2)**3*np.vdot(previous,cs).real
                errors.append(abs(actual/expected-1));interference.append((actual-separate)/separate)
                for C,M in core.vertices(d,p,ML).values():
                    a,_=component((C[j,i],C[i,j].conjugate()),140.,300.,M,ML[i],.0073)
                    b,_=component((C[i,j],C[j,i].conjugate()),140.,300.,M,ML[j],.0073)
                    errors.append(float(np.max(abs(ML[i]*a-ML[j]*b[::-1].conj()))/max(np.max(abs(ML[i]*a)),1e-40)))
                if channel=='mu_to_e_gamma' and inp['benchmark_id'].endswith('spectrum0'):
                    representatives.append({'witness':inp['benchmark_id'],'charged_CL_CR':[[z.real,z.imag] for z in cs],
                        'width_with_scalar_INCLUDED_ONLY':actual,'width_with_wrong_sign_falsifier':core.radiative_width(previous-cs,ML[i],ML[j],.0073)})
        self.assertLess(max(errors),2e-12)
        EVIDENCE['NO_IO_phase_reverse_coherence_max_relative']=float(max(errors))
        EVIDENCE['fractional_interference_range']=[float(min(interference)),float(max(interference))]
        EVIDENCE['NO_IO_charged_examples']=representatives

    def test_prior_validated_34_rows_and_blocked_W_are_unchanged(self):
        baseline=json.loads((ROOT/'module4/pre_charged_baseline.json').read_text())
        byid={r['benchmark_id']:r for r in baseline['witnesses']}
        for inp,n in cases():
            d=dict(schema_version='1.0.0',kind='module3_matching_input_v1',module3_input=inp,module2_output=n,two_loop_inputs=EXTRA)
            out=evaluate(d)
            self.assertEqual(canonical_hash(inp),byid[inp['benchmark_id']]['module3_input_sha256'])
            for channel,value in out['channels'].items():
                previous={k:r for k,r in value['ledger'].items() if not k.endswith('_scalar_gamma')}
                self.assertEqual(len(previous),34)
                self.assertEqual(canonical_hash(previous),byid[inp['benchmark_id']]['channels'][channel]['validated_34_rows_sha256'])
                self.assertEqual(canonical_hash(value['two_loop_candidates']),byid[inp['benchmark_id']]['channels'][channel]['excluded_W_rows_sha256'])
                self.assertEqual(len(value['ledger']),40);self.assertEqual(len(value['two_loop_candidates']),2)
        EVIDENCE['existing_validated_results_preservation']='PASS: 18 canonical signed 34-row ledger hashes and 18 excluded-W hashes match commit3326982'

    def test_invalid_and_complex_trilinear_fail_closed(self):
        for args in [((1,1),1+1j,300.,400.,.1,.0073),((1,1),140.,0,400.,.1,.0073),((1,),140.,300.,400.,.1,.0073)]:
            with self.assertRaises(ValueError):component(*args)
        for z in (0.,-1.,float('nan'),float('inf')):
            with self.assertRaises(ValueError):scalar_loop_kernel(z)


if __name__=='__main__':unittest.main()
