"""Source-locked tree partial width tests, not collider cross-section or BR tests."""
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np

from module7.cascade_z import cascade_width,STATUS

ROOT=Path(__file__).resolve().parents[1]
BASE={"mH1_GeV":300.,"mH2_GeV":700.,"mZ_GeV":91.1876,
      "mW_GeV":80.379,"v_GeV":246.21965,"gamma_rad":1.089}

def independent_paper_eq72(x):
    M,m,mz,mw,v,gamma=(x[k] for k in
        ("mH2_GeV","mH1_GeV","mZ_GeV","mW_GeV","v_GeV","gamma_rad"))
    if M<=m+mz:return 0.
    g=2*mw/v
    d = (M*M-(m+mz)**2)*(M*M-(m-mz)**2)
    return (g*g/(64*math.pi*M**3*mw*mw)*
            ((-0.5*math.sin(2*gamma))**2)*d**1.5)


def four_vector_width(x, orientation=1, boosted=False):
    """Explicit physical polarisations, independent energies and charge rotation.

    All incoming: p_plus=P, p_minus=-k, hence J=P+k. Crossing the
    conjugate orientation reverses J. No initial spin average or 1/2!.
    """
    M,m,z,w,v,y = (x[k] for k in ('mH2_GeV','mH1_GeV','mZ_GeV',
                                 'mW_GeV','v_GeV','gamma_rad'))
    ez = (M*M+z*z-m*m)/(2*M)
    momentum = math.sqrt((ez-z)*(ez+z))
    n = np.array([2.,-3.,6.])/7
    t1 = np.cross(n,[0.,0.,1.]);t1 /= np.linalg.norm(t1)
    t2 = np.cross(n,t1)
    P = np.array([M,0.,0.,0.]);k = np.r_[M-ez,-momentum*n]
    q = P-k
    pols = [np.r_[0.,t1],np.r_[0.,t2],np.r_[momentum/z,ez*n/z]]
    def dot(a,b):return a[0]*b[0]-np.dot(a[1:],b[1:])
    def boost(a):
        velocity=np.array([.2,-.1,.3]);b2=np.dot(velocity,velocity)
        lorentz=1/math.sqrt(1-b2);ba=np.dot(velocity,a[1:])
        return np.r_[lorentz*(a[0]-ba), a[1:]+((lorentz-1)*ba/b2-lorentz*a[0])*velocity]
    if boosted:
        P,k,q=map(boost,(P,k,q));pols=list(map(boost,pols))
    assert abs(dot(q,q)-z*z)<1e-9
    for e in pols:
        assert abs(dot(e,q))<1e-10 and abs(dot(e,e)+1)<1e-12
    # T3=1/2 for doublet, T3=0 for singlet, Q=1 for both.
    sw2=1-(w/z)**2
    rotation=np.array([[math.cos(y),math.sin(y)],[-math.sin(y),math.cos(y)]])
    charge=rotation@np.diag([.5-sw2,-sw2])@rotation.T
    coupling=2*w/v/(w/z)*charge[0,1]
    current=orientation*(P+k)
    amplitudes=[coupling*dot(current,e) for e in pols]
    polsum=sum(a*a for a in amplitudes)
    projector=coupling**2*(-dot(current,current)+dot(current,q)**2/z**2)
    assert math.isclose(polsum,projector,rel_tol=2e-14)
    return momentum/(8*math.pi*M*M)*polsum

class CascadeTests(unittest.TestCase):
    def test_actual_native_vertex_evidence_and_gauge_normalization(self):
        import hashlib
        r=json.loads((ROOT/'validation/module7/native_vertex.json').read_text())
        self.assertEqual(r['status'],'NATIVE_VERTEX_VERIFIED')
        self.assertTrue(r['momentum_difference_verified'])
        self.assertEqual(len(r['cases']),24)
        self.assertLess(r['max_residual'],1e-12)
        for path,key in [('scripts/zee_d3_cascade_vertex.m','driver_sha256'),
                         ('models/SARAH/ZeeTypeII/ZeeTypeII.m','model_sha256')]:
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),r[key])
        for case in r['cases']:
            x={**BASE,**{k:case[k] for k in ('gamma_rad','mW_GeV','mZ_GeV','v_GeV')}}
            coefficient=cascade_width(x)['absolute_gauge_vertex_coefficient']
            for actual in case['absolute_coefficients'][:2]:
                self.assertAlmostEqual(actual,coefficient,delta=1e-15)
            self.assertLess(case['absolute_coefficients'][2],1e-15)

    def test_independent_four_vectors_both_crossings_and_boost(self):
        for m in (250.,300.,350.):
            x={**BASE,'mH1_GeV':m}
            for orientation in (-1,1):
                for boosted in (False,True):
                    actual=cascade_width(x)['partial_width_GeV']
                    self.assertAlmostEqual(four_vector_width(x,orientation,boosted),actual,delta=2e-13)
            simplified=(math.sin(2*x['gamma_rad'])**2*cascade_width(x)['kallen_sqrt_GeV2']**3/
                        (64*math.pi*x['v_GeV']**2*x['mH2_GeV']**3))
            self.assertAlmostEqual(simplified,actual,delta=1e-13)

    def test_frozen_full_rotation_charge_projection(self):
        from module1.scalar_constraints import validate_input,reconstruct
        seed=json.loads((ROOT/'module3/example.json').read_text())
        x,*_=validate_input(seed['module2_input']['scalar']['record'])
        *_,rec=reconstruct(x)
        zp=np.array(rec['mixing_rows']['ZP'])
        sw2=1-(BASE['mW_GeV']/BASE['mZ_GeV'])**2
        charge=zp@np.diag([.5-sw2,.5-sw2,-sw2])@zp.T
        self.assertAlmostEqual(2*charge[1,2],-.5*math.sin(2*x['gamma']),places=15)
        self.assertAlmostEqual(charge[2,1],charge[1,2],places=15)
        photon=zp@np.eye(3)@zp.T
        self.assertAlmostEqual(photon[1,2],0.,places=15)

    def test_paper_eq72_for_d2_three_spectra(self):
        for m in (250.,300.,350.):
            row={**BASE,"mH1_GeV":m}
            r=cascade_width(row)
            self.assertEqual(r["status"],STATUS)
            self.assertTrue(r["is_kinematically_open"])
            self.assertAlmostEqual(r["partial_width_GeV"],independent_paper_eq72(row),delta=1e-12)
            self.assertIsNone(r["branching_fraction"])
            self.assertIsNone(r["total_width_GeV"])
            self.assertIsNone(r["global_zee_acceptance"])

    def test_normalization_and_independent_projector(self):
        r=cascade_width(BASE)
        w,z=BASE["mW_GeV"],BASE["mZ_GeV"]
        g=2*w/BASE["v_GeV"]
        coeff=-math.sin(BASE["gamma_rad"])*math.cos(BASE["gamma_rad"])
        self.assertAlmostEqual(r["normalized_offdiagonal_Z_coupling"],coeff,places=15)
        self.assertAlmostEqual(r["absolute_gauge_vertex_coefficient"],
                               abs(g/(2*(w/z))*coeff),places=15)
        # In rest frame, |M|^2 summed over on-shell Z polarisations =
        # |g_Z|^2 * lambda(M^2,m^2,mZ^2) / mZ^2.
        M=BASE["mH2_GeV"]
        p3=r["kallen_sqrt_GeV2"]/(2*M)
        m2=r["absolute_gauge_vertex_coefficient"]**2*(
             r["kallen_sqrt_GeV2"]**2/z**2)
        width=p3/(8*math.pi*M*M)*m2
        self.assertAlmostEqual(width,r["partial_width_GeV"],places=12)

    def test_zero_mixing_and_sign_invariance(self):
        for gamma in (0.,math.pi/2,-math.pi/2):
            self.assertEqual(cascade_width({**BASE,"gamma_rad":gamma})["partial_width_GeV"],0.)
        reference=cascade_width(BASE)["partial_width_GeV"]
        self.assertAlmostEqual(reference,
              cascade_width({**BASE,"gamma_rad":-BASE["gamma_rad"]})["partial_width_GeV"],
              places=13)
        self.assertAlmostEqual(reference,
              cascade_width({**BASE,"gamma_rad":math.pi/2-BASE["gamma_rad"]})["partial_width_GeV"],
              places=13)

    def test_threshold_and_near_threshold(self):
        z=BASE["mZ_GeV"];m=BASE["mH1_GeV"]
        for M in (m+z-1.,m+z):
            row=cascade_width({**BASE,"mH2_GeV":M})
            self.assertFalse(row["is_kinematically_open"])
            self.assertEqual(row["partial_width_GeV"],0.)
        widths=[cascade_width({**BASE,"mH2_GeV":m+z+d})["partial_width_GeV"] 
                for d in (1e-4,1e-3,1e-2)]
        self.assertTrue(widths[0]<widths[1]<widths[2])
        # Smallest representable on-shell excess, with an independent Decimal
        # product; a square-polynomial subtraction loses this threshold.
        from decimal import Decimal,localcontext
        M=math.nextafter(m+z,math.inf)
        got=cascade_width({**BASE,'mH2_GeV':M})
        self.assertTrue(got['is_kinematically_open'])
        self.assertGreater(got['partial_width_GeV'],0.)
        with localcontext() as ctx:
            ctx.prec=60
            D=Decimal.from_float;dm,dz,dM=map(D,(m,z,M))
            expected=((dM-dm-dz)*(dM+dm+dz)*(dM-dm+dz)*(dM+dm-dz)).sqrt()
        self.assertAlmostEqual(got['kallen_sqrt_GeV2']/float(expected),1.,delta=1e-14)

    def test_fail_closed_bad_input(self):
        samples=(
            {**BASE,"mH1_GeV":800.},
            {**BASE,"mW_GeV":100.},
            {**BASE,"gamma_rad":2.},
            {**BASE,"v_GeV":float("nan")},
            {**BASE,"mH2_GeV":True},
            {**BASE,"unverified_Br":0.5},
        )
        for row in samples:
            with self.subTest(row=row),self.assertRaises(ValueError):
                cascade_width(row)

    def test_cli_idempotence_and_invalid_duplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            inp=Path(folder)/"in.json";out=Path(folder)/"out.json"
            inp.write_text(json.dumps(BASE))
            args=[sys.executable,"-m","module7.cascade_z","--input",str(inp),
                  "--output",str(out)]
            proc=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            output=json.loads(out.read_text())
            self.assertEqual(output["status"],STATUS)
            old=out.read_bytes()
            inp.write_text('{"mH1_GeV":300,"mH1_GeV":400}')
            bad=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)
            self.assertEqual(out.read_bytes(),old)

if __name__=="__main__":
    unittest.main()
