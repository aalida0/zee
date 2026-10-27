"""D4 independent amplitudes, inclusive sums, native evidence and BR gate."""
import copy
import json
import math
import unittest
from unittest.mock import patch

import numpy as np
import sympy as sp
from module1.scalar_constraints import reconstruct
from module2.interface import decode, encode
from module7.d4_inputs import ROOT, SM, families, ckm, rotations, sha, alpha_s, running_mass
from module7.d4_native import expected_coefficients, leptonic, trilinear
from module7.d4_decay_table import complete_total, expected_channels
from module7.d4_tree_kernels import scalar_fermions, scalar_scalar, scalar_vector


class DecayTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table=json.loads((ROOT/'validation/module7/d4_decay_table.json').read_text())
        cls.native=json.loads((ROOT/'validation/module7/d4_native_validation.json').read_text())
        cls.data,cls.d3=families()

    def test_native_versions_sources_and_actual_coefficients(self):
        n=self.native
        self.assertEqual(n['sarah_version'],'4.15.4');self.assertIn('15.0.1',n['math_version'])
        self.assertEqual(n['numeric_cases'],36);self.assertEqual(n['native_queries'],100)
        self.assertEqual(len(n['residuals']),36)
        for name,digest in n['source_sha256'].items():self.assertEqual(sha(ROOT/name),digest)
        for case in n['residuals']:
            for residual in case['maximum_absolute_residual_by_sector'].values():self.assertLess(residual,2e-10)
        c=n['native_falsifier_case'];want=expected_coefficients(c['input'])
        for a,b in zip(want,c['output']['coefficients']):
            for x,y in zip(a,b):self.assertAlmostEqual(abs(x-complex(y['real'],y['imag'])),0.,delta=2e-10)
        for name in ('exact_zero_CP_A','exact_zero_offdiagonal_photon','exact_zero_WZ_Wphoton',
                     'momentum_differences_verified','chirality_labels_verified'):
            self.assertIs(n[name],True)

    def test_signed_complex_native_falsifiers(self):
        case=self.native['native_falsifier_case'];card=case['input']
        good=expected_coefficients(card)
        changed=copy.deepcopy(card);changed['physical']['gamma']*=-1
        bad=expected_coefficients(changed)
        self.assertGreater(max(abs(a-b) for x,y in zip(good,bad) for a,b in zip(x,y)),.1)
        changed=copy.deepcopy(card)
        changed['rules']['Fzee']['imag'][0][1]+=.1
        changed['rules']['Fzee']['imag'][1][0]-=.1
        bad=expected_coefficients(changed)
        self.assertGreater(abs(good[56][0]-bad[56][0]),.01)
        # A complex CKM element changes its signed coefficient if conjugated.
        self.assertGreater(abs(good[4][1]+good[4][1].conjugate()),1e-5)
        with patch('module7.d4_native.ckm',return_value=np.eye(3)):
            bad=expected_coefficients(card)
        self.assertGreater(abs(good[4][1]-bad[4][1]),1e-5)

    def test_polynomial_potential_trilinear_and_CP_zero(self):
        # Independently expand V, including its Hermitian conjugate, then
        # differentiate with respect to physical charged and neutral fields.
        X,Y,h,A=sp.symbols('X Y h A',real=True)
        for r,_,_ in self.data[::4]:
            p=r['module2_input']['scalar']['record']['physical'];pars,_,_=reconstruct(p)
            zp,zh,za=rotations(p);v1=p['v']*math.cos(p['beta']);v2=p['v']*math.sin(p['beta'])
            C1,C2,S=zp[2]*X;D1,D2,T=zp[1]*Y
            for j in (0,1,2):
                if j<2:
                    n1=(v1+zh[j,0]*h)/sp.sqrt(2);n2=(v2+zh[j,1]*h)/sp.sqrt(2)
                    nc1,nc2=n1,n2;var=h
                else:
                    n1=(v1+sp.I*za[1,0]*A)/sp.sqrt(2);n2=(v2+sp.I*za[1,1]*A)/sp.sqrt(2)
                    nc1=(v1-sp.I*za[1,0]*A)/sp.sqrt(2);nc2=(v2-sp.I*za[1,1]*A)/sp.sqrt(2);var=A
                n11=D1*C1+nc1*n1;n22=D2*C2+nc2*n2
                n12=D1*C2+nc1*n2;n21=D2*C1+nc2*n1;a=pars
                V=(a['Lambda1']/2*n11**2+a['Lambda2']/2*n22**2+a['Lambda3']*n11*n22
                   +a['Lambda4']*n12*n21+a['Lambda5']/2*(n12**2+n21**2)
                   +a['K1']*S*T*n11+a['K2']*S*T*n22-a['K12']*S*T*(n12+n21)
                   +a['Mu4']*(T*(C1*n2-C2*n1)+S*(D1*nc2-D2*nc1)))
                actual=complex(sp.diff(sp.expand(V),X,Y,var).subs({X:0,Y:0,var:0}))
                want=trilinear(p,pars,j+1) if j<2 else 0.
                self.assertAlmostEqual(abs(actual-want),0.,delta=1e-10)
                if j<2:
                    doubled=dict(p,v=2*p['v']);pa=dict(pars,Mu4=2*pars['Mu4'])
                    self.assertAlmostEqual(trilinear(doubled,pa,j+1),2*want,delta=1e-10)

    def test_leptonic_PMNS_sum_phases_and_orientation(self):
        rng=np.random.default_rng(41454)
        u,_=np.linalg.qr(rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))
        for r,n,_ in self.data:
            p=r['module2_input']['scalar']['record']['physical']
            f,d=decode(n['F']),decode(n['D'])
            zp,_,_=rotations(p)
            for k in (1,2):
                a,b=leptonic(p,n,k);au,bu=a@u,b@u.conj()
                M=p[f'mH{k}']
                for i,ml in enumerate(SM['lepton_masses']):
                    norm=zp[k,2]**2*sum(abs(f[:,i])**2)+(math.cos(p['gamma']) if k==1 else math.sin(p['gamma']))**2*sum(abs(d[i,:])**2)
                    oracle=M/(16*math.pi)*(1-ml*ml/(M*M))**2*norm
                    plus=sum(scalar_fermions(M,0.,ml,x,y,1) for x,y in zip(a[i],b[i]))
                    rotated=sum(scalar_fermions(M,0.,ml,x,y,1) for x,y in zip(au[i],bu[i]))
                    minus=sum(scalar_fermions(M,ml,0.,-y.conjugate(),-x.conjugate(),1) for x,y in zip(a[i],b[i]))
                    self.assertAlmostEqual(plus,oracle,delta=2e-19)
                    self.assertAlmostEqual(plus,rotated,delta=2e-19)
                    self.assertAlmostEqual(plus,minus,delta=2e-19)
        # At nonzero neutrino mass the chiral interference is phase sensitive;
        # the native tree approximation explicitly sets this mass to zero.
        self.assertNotEqual(scalar_fermions(250.,1.,2.,1.,1j,1),scalar_fermions(250.,1.,2.,1.,1.,1))

    def test_quark_CKM_color_and_2021_aligned_width(self):
        self.assertLess(np.max(abs(ckm()@ckm().conj().T-np.eye(3))),4e-16)
        for spectrum in self.table['spectrum_tables'].values():
            p=spectrum['physical']
            for k in (1,2):
                t=spectrum['mothers'][f'H{k}'];M=t['mother_mass_GeV'];q=t['decay_yukawa_masses_GeV']
                d=math.cos(p['gamma']) if k==1 else -math.sin(p['gamma'])
                for i in range(3):
                    for j in range(3):
                        a=math.sqrt(2)*q[i]/p['v']/math.tan(p['beta'])*d*ckm()[i,j]
                        b=math.sqrt(2)*q[j+3]/p['v']*math.tan(p['beta'])*d*ckm()[i,j]
                        mi,mj=SM['kinematic_masses'][i],SM['kinematic_masses'][j+3]
                        oracle=scalar_fermions(M,mi,mj,a,b,3)
                        self.assertAlmostEqual(oracle,t['channels'][i*3+j]['width_GeV'],delta=2e-15)
                        self.assertAlmostEqual(oracle,3*scalar_fermions(M,mi,mj,a,b,1),delta=2e-15)
                # Eq74 in dimensionally consistent x=m²/M² form, all quark
                # masses identical in kinematics/Yukawas in this aligned check.
                mt,mb=172.4,4.78;xt,xb=(mt/M)**2,(mb/M)**2
                Y=d/math.tan(p['beta']);X=d*math.tan(p['beta'])
                lam=math.sqrt((1-xt-xb)**2-4*xt*xb)
                paper=3*M**3/(8*math.pi*p['v']**2)*lam*((1-xt-xb)*(Y*Y*xt+X*X*xb)-4*xt*xb*X*Y)
                kernel=scalar_fermions(M,mt,mb,math.sqrt(2)*mt/p['v']*Y,math.sqrt(2)*mb/p['v']*X,3)
                self.assertAlmostEqual(kernel,paper,delta=1e-13)

    def test_2021_leptonic_aligned_limit_only(self):
        # This is solely a limit of the validated general native structure.
        # The D2 families retain unrestricted complex F/D/Ye2 throughout.
        p=self.data[0][0]['module2_input']['scalar']['record']['physical']
        n={'F':encode(np.zeros((3,3),complex)),
           'Ye':encode(np.diag(np.sqrt(2)*np.array(SM['lepton_masses'])/(p['v']*math.cos(p['beta']))).astype(complex)),
           'Ye2':encode(np.zeros((3,3),complex))}
        for k in (1,2):
            a,b=leptonic(p,n,k);M=p[f'mH{k}']
            d=math.cos(p['gamma']) if k==1 else -math.sin(p['gamma'])
            Z=d*math.tan(p['beta'])
            for i,ml in enumerate(SM['lepton_masses']):
                oracle=ml*ml*M/(8*math.pi*p['v']**2)*Z*Z*(1-ml*ml/(M*M))**2
                width=sum(scalar_fermions(M,0.,ml,x,y,1) for x,y in zip(a[i],b[i]))
                self.assertAlmostEqual(width,oracle,delta=2e-16*max(1.,oracle))

    def test_bosonic_2021_thresholds_and_normalization(self):
        refs={250.:11.671906176399391,300.:9.411343258642537,350.:7.1240428396019855}
        for t in self.table['spectrum_tables'].values():
            p=t['physical'];g=2*SM['EW']['mW']/p['v']
            for k in (1,2):
                rows={r['channel']:r for r in t['mothers'][f'H{k}']['channels']}
                d=math.cos(p['gamma']) if k==1 else -math.sin(p['gamma'])
                for n,m,f in [('h',p['mh1'],math.sin(p['alpha']-p['beta'])),('H',p['mh2'],math.cos(p['alpha']-p['beta'])),('A',p['ma'],1.)]:
                    oracle=scalar_vector(p[f'mH{k}'],m,SM['EW']['mW'],g*d*f/2)
                    self.assertAlmostEqual(oracle,rows['W '+n]['width_GeV'],delta=1e-13)
                self.assertEqual(rows['W A']['status'],'CLOSED')
                self.assertEqual(rows[f'H{3-k} A']['status'],'FORBIDDEN_CP')
                self.assertEqual(rows['W Z']['width_GeV'],0.)
            rows={r['channel']:r for r in t['mothers']['H2']['channels']}
            self.assertEqual(rows['H1 Z']['width_GeV'],refs[p['mH1']])
            self.assertEqual(rows['W H']['status'],'OPEN');self.assertEqual(rows['H1 h']['status'],'OPEN')
            self.assertEqual(rows['H1 H']['status'],'CLOSED')
            pars,_,_=reconstruct(p)
            self.assertAlmostEqual(rows['H1 h']['width_GeV'],scalar_scalar(p['mH2'],p['mH1'],p['mh1'],trilinear(p,pars,1)),delta=1e-12)

    def test_running_scheme_and_threshold_continuity(self):
        for Q in [4.183,172.4]:
            self.assertAlmostEqual(alpha_s(Q-1e-7),alpha_s(Q+1e-7),delta=1e-8)
        for m,q in zip(SM['quark_reference_masses'],SM['quark_reference_scales']):
            self.assertAlmostEqual(running_mass(m,q,q),m,delta=1e-13)
            self.assertLess(running_mass(m,q,700.),m)
            self.assertAlmostEqual(running_mass(running_mass(m,q,700.),700.,q),m,delta=1e-12)
        self.assertEqual(SM['kinematic_masses'][2],172.4)
        self.assertNotEqual(SM['kinematic_masses'][2],163.9689)

    def test_all_ledgers_totals_families_and_scope(self):
        self.assertEqual(len(self.table['conditional_lepton_families']),12)
        for point in self.table['conditional_lepton_families']:
            for k in (1,2):
                key=f'H{k}';spec=self.table['spectrum_tables'][point['spectrum_name']]
                rows=spec['mothers'][key]['channels']+point['leptonic_channels'][key]
                self.assertEqual(set(r['channel'] for r in rows),expected_channels(k))
                self.assertEqual(complete_total(rows,k),point['mothers'][key])
                self.assertAlmostEqual(sum(point['mothers'][key]['branching_fractions'].values()),1.,delta=5e-16)
        for group in self.table['family_contrasts'].values():
            self.assertEqual(group['independent_D_hashes'],4)
            self.assertEqual(group['nonleptonic_width_spread_GeV'],0.)
            for vals in group['leptonic_sum_GeV'].values():self.assertGreater(max(vals.values()),min(vals.values()))
        self.assertFalse(self.table['COMPLETE_LFV']);self.assertFalse(self.table['2026_LINEARIZED_FLAVOR_FILTER_READY'])
        self.assertIsNone(self.table['global_zee_acceptance'])
        self.assertEqual(self.table['preserved_D3_statuses'],self.d3['statuses'])

    def test_BR_gate_missing_unknown_and_nonfinite_falsifiers(self):
        p=self.table['conditional_lepton_families'][0];spec=self.table['spectrum_tables'][p['spectrum_name']]
        rows=spec['mothers']['H2']['channels']+p['leptonic_channels']['H2']
        with self.assertRaises(ValueError):complete_total(rows[:-1],2)
        with self.assertRaises(ValueError):complete_total(rows+[rows[0]],2)
        for key,value in [('status','UNKNOWN_VERTEX'),('width_GeV',None),('width_GeV',float('nan')),
                          ('width_GeV',-1.),('width_minus_GeV',float('inf')),('independently_validated',False)]:
            changed=copy.deepcopy(rows);changed[0][key]=value
            result=complete_total(changed,2)
            self.assertEqual(result['status'],'BR_NOT_EVALUATED')
            self.assertIsNone(result['total_width_GeV']);self.assertIsNone(result['branching_fraction'])


if __name__=='__main__':unittest.main()
