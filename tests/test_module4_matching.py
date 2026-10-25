"""Independent signed outer-loop matching and off-shell W source audit."""
import json
import math
from pathlib import Path
import unittest
import numpy as np
from module3 import core
from module3.tree import G, PL, PR
from module2.interface import decode
from module4.amplitudes import fermion_component, combine, CHANNELS
from module4.kernels import kernels
from module4.matching_audit import (METRIC, epsilon, sigma, outer_projection,
    euclidean_parameters, gm2calc_photon_functions, ilisie_fermion_functions,
    chang2001_pseudoscalar, w_source_decomposition, ilisie_w_integral, pinch_ward_check)
from test_module4_physics import cases, rows, ML, P

EVIDENCE={}


class MatchingAuditTests(unittest.TestCase):
    def test_sigma_gamma5_Hermitian_conjugation_and_action_vertex(self):
        identity=np.eye(4);g5=PR-PL;error=0.
        for mu in range(4):
            for nu in range(4):
                error=max(error,float(np.max(abs(G[mu]@G[nu]+G[nu]@G[mu]-2*METRIC[mu,nu]*identity))))
                error=max(error,float(np.max(abs(G[0]@sigma(mu,nu).conj().T@G[0]-sigma(mu,nu)))))
        # A_L bar(parent)_L sigma daughter_R conjugates to CL PL, no
        # chirality-label swap. gamma0 PR gamma0 = PL.
        for mu,nu in ((0,1),(2,3)):
            adj=G[0]@(sigma(mu,nu)@PR).conj().T@G[0]
            error=max(error,float(np.max(abs(adj-sigma(mu,nu)@PL))))
        trace=np.trace(G[0]@G[1]@G[2]@G[3]@g5)
        self.assertEqual(trace,-4j) # epsilon^0123=+1, gamma5=i gamma0 gamma1 gamma2 gamma3
        # Created photon wave exp(+i q.x): derive the emitted operator vertex
        # from i L with F_mu_nu, rather than guessing an S-matrix sign.
        q=np.array([1.,0.,0.,1.]);pol=np.array([0.,1.,0.,0.]);qc=METRIC@q;ec=METRIC@pol
        F=1j*(np.outer(qc,ec)-np.outer(ec,qc))
        X=(.03+.02j)*PL+(-.07+.01j)*PR;e=.313;mi=.106
        actual=1j*e*mi/2*sum(sigma(mu,nu)@X*F[mu,nu] for mu in range(4) for nu in range(4))
        expected=e*mi*sum(sigma(mu,nu)@X*ec[mu]*qc[nu] for mu in range(4) for nu in range(4))
        error=max(error,float(np.max(abs(actual-expected))))
        self.assertLess(error,1e-15)
        EVIDENCE['sigma_HC_and_action_vertex_max_abs']=error

    def test_outer_Wick_projection_both_orders_and_complex_chiralities(self):
        rng=np.random.default_rng(97134);errors=[]
        for _ in range(8):
            q=rng.normal(size=4);left,right=rng.normal(size=2)+1j*rng.normal(size=2)
            errors.extend(outer_projection(q,left,right))
        self.assertLess(max(errors),2e-14)
        EVIDENCE['outer_Dirac_projection_max_abs']=max(errors)
        EVIDENCE['physical_fermion_prefactor_sign']=-1
        EVIDENCE['physical_sign_basis']='Native -ieQ gamma and -i(C PL+Cdag PR); two orientations; incoming-to-outgoing real-photon crossing; explicit Wick angular average and emitted-operator vertex'

    def test_independent_Euclidean_parameters_and_three_primary_sources(self):
        errors=[];euclidean_errors=[];samples=[]
        for z in (.001,.1,.25,.413,1.,10.):
            f,g,_=kernels(z)[0]
            source_expected=np.array([-f,g])
            gm=np.array(gm2calc_photon_functions(z))
            ilisie=np.array(ilisie_fermion_functions(z))
            prd=chang2001_pseudoscalar(z)
            error=max(float(max(abs(gm/source_expected-1))),float(max(abs(ilisie/source_expected-1))),abs(prd/g-1))
            errors.append(error)
            direct=np.array(euclidean_parameters(z))
            euclidean_errors.append(float(max(abs(direct/[f,g]-1))))
            samples.append({'z':z,'Ilisie_scalar':float(ilisie[0]),'GM2Calc_scalar':float(gm[0]),
                            'PRD_pseudoscalar':prd,'physical_f_g':[-f,g]})
        self.assertLess(max(errors),2e-11)
        self.assertLess(max(euclidean_errors),2e-9)
        EVIDENCE['primary_sources_max_relative']=max(errors)
        EVIDENCE['Euclidean_no_log_parameters_max_relative']=max(euclidean_errors)
        EVIDENCE['source_comparison_samples']=samples

    def test_scalar_pseudoscalar_and_mixed_diagonal_moments(self):
        errors=[];samples={}
        mi,mf,M,alpha,nc,q=.1056583755,172.5,400.,1/137.035999084,3,2/3
        z=(mf/M)**2;fs,gp=ilisie_fermion_functions(z)
        for label,lepton,internal in [('scalar',.003,.6),('pseudoscalar',.003j,.6j),
                ('mixed',.003+.007j,.6-.4j)]:
            coefficients,_=fermion_component((lepton,lepton.conjugate()),internal,mf,M,mi,alpha,nc,q)
            actual=mi*mi*sum(coefficients).real
            reference=alpha*nc*q*q*mi/(4*math.pi**3*mf)*(
                lepton.real*internal.real*fs+lepton.imag*internal.imag*gp)
            errors.append(abs(actual/reference-1));samples[label]=actual
        self.assertLess(samples['scalar'],0);self.assertGreater(samples['pseudoscalar'],0)
        self.assertLess(max(errors),2e-12)
        EVIDENCE['signed_diagonal_moment_max_relative']=max(errors)
        EVIDENCE['signed_diagonal_moments']=samples

    def test_NO_IO_complex_reverse_channels_and_coherent_interference(self):
        errors=[];interference=[];examples=[]
        for inp,n in cases():
            d,f=decode(n['D']),decode(n['F']);p=inp['module2_input']['scalar']['record']['physical']
            for channel,(i,j) in CHANNELS.items():
                ledger=rows(d,p,i,j)
                fermions={k:r for k,r in ledger.items() if r['coherent_inclusion']}
                self.assertEqual(len(fermions),27)
                bz=combine(fermions)
                old=core.combine(core.dipole_ledger(f,d,p,ML,i,j))
                actual=core.radiative_width(old+bz,ML[i],ML[j],.0072973525692838015)
                scale=core.radiative_width(old,ML[i],ML[j],.0072973525692838015)+core.radiative_width(bz,ML[i],ML[j],.0072973525692838015)
                interference.append((actual-scale)/scale)
                # Explicit signed cross term, complex CL and CR separately.
                expected=scale+.0072973525692838015*ML[i]**5/2*(1-(ML[j]/ML[i])**2)**3*np.vdot(old,bz).real
                errors.append(abs(actual/expected-1))
                wrong=core.radiative_width(old-bz,ML[i],ML[j],.0072973525692838015)
                self.assertGreater(abs(actual-wrong)/scale,1e-7)
                for C,M in core.vertices(d,p,ML).values():
                    internal=.43+.17j
                    a,_=fermion_component((C[j,i],C[i,j].conjugate()),internal,172.5,M,ML[i],.0073,3,2/3)
                    b,_=fermion_component((C[i,j],C[j,i].conjugate()),internal,172.5,M,ML[j],.0073,3,2/3)
                    errors.append(float(np.max(abs(ML[i]*a-ML[j]*b[::-1].conj()))/max(np.max(abs(ML[i]*a)),1e-50)))
                if channel=='mu_to_e_gamma' and inp['benchmark_id'].endswith('spectrum0'):
                    examples.append({'witness':inp['benchmark_id'],'one_loop_CL_CR':[[z.real,z.imag] for z in old],
                                     'fermion_gamma_CL_CR':[[z.real,z.imag] for z in bz],
                                     'coherent_width_GeV_INCLUDED_ONLY':actual,
                                     'wrong_sign_width_GeV_falsifier':wrong})
        self.assertLess(max(errors),2e-13)
        EVIDENCE['NO_IO_coherence_reverse_max_relative']=max(errors)
        EVIDENCE['NO_IO_fractional_interference_range']=[min(interference),max(interference)]
        EVIDENCE['NO_IO_representative_signed_amplitudes']=examples

    def test_W_exact_source_difference_and_offshell_form_factors(self):
        residuals=[];table=[]
        for z in (.001,.01,.1,.25,.413,1.,10.,100.):
            data=w_source_decomposition(z);direct=ilisie_w_integral(z)
            residuals.extend([abs(direct/data['Ilisie']-1),
                abs(data['CHK']-data['Ilisie']-data['CHK_minus_Ilisie'])/max(abs(data['CHK']),1),
                abs(data['CHK']-data['Abe_transverse']-data['CHK_minus_Abe'])/max(abs(data['CHK']),1),
                abs(data['Ilisie']-data['Abe_transverse']-data['Ilisie_minus_Abe'])/max(abs(data['CHK']),1)])
            table.append(data)
        self.assertLess(max(residuals),2e-12)
        self.assertAlmostEqual(table[4]['old_signed_ratio'],-1.0105325699387073,delta=5e-14)
        # A mass-dependent additive discrepancy cannot be repaired by a
        # universal normalization or photon-charge conversion.
        ratios=[d['CHK']/d['Ilisie'] for d in table]
        self.assertGreater(max(ratios)-min(ratios),.001)
        EVIDENCE['W_source_decomposition_max_relative']=max(residuals)
        EVIDENCE['W_source_decomposition']=table

    def test_offshell_W_P_tensor_pinch_cancellation_scope(self):
        checks=[pinch_ward_check(p2=k) for k in [(2.,.4,-.3,.8),(7.,1.,-.7,3.),(1.,2.,3.,4.)]]
        self.assertTrue(all(r['Ward_before_pinch']>1 for r in checks))
        self.assertLess(max(r['Ward_after_pinch'] for r in checks),2e-12)
        EVIDENCE['W_offshell_Ward_checks']=checks
        EVIDENCE['W_matching_status']='BLOCKED: complete LFV B,C projections, pinch routing and independent R_xi cancellation absent; W remains excluded'


if __name__=='__main__':unittest.main()
