import math
import unittest

import numpy as np

from module2.interface import decode
from module3 import tree
from research.full_constraints.lfv_2hdm_transfer_2026.evaluate import read_cards
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_native_monopole_source import (
    ALPHA, ME, MMU, MTAU, GAMMA_TAU, EXPECTED, K1_JSON, K2_JSON, SHA,
    complex_pair, evaluate, photon_rate
)
import json


class NativeTauPhotonMonopoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger=json.loads(K1_JSON.read_text())
        cls.one=evaluate()
        cls.cards=read_cards()

    def test_sources_verified_and_not_physical(self):
        self.assertEqual(self.ledger["source_sha256"], SHA)
        self.assertEqual(tuple(self.one["cards"]),EXPECTED)
        self.assertEqual(self.one["physical_lfv"],"UNKNOWN")
        self.assertIsNone(self.one["global_acceptance"])
        self.assertFalse(self.one["full_Zee_two_loop_included"])
        for row in self.one["cards"].values():
            self.assertEqual(len(row),4)
            for x in row.values():
                self.assertIsNone(x["physical_total_BR"])
                self.assertGreater(x["photon_only_source_BR"],0.)

    def test_full_F_D_exact_source_decomposition(self):
        for card,row in self.ledger["cards"].items():
            for flavor,x in row.items():
                for chir in ("L","R"):
                    full=complex_pair(x["OA1"+chir])
                    d=complex_pair(x["OA1"+chir+"_D_ONLY"])
                    f=complex_pair(x["OA1L_F_ONLY"]) if chir=="L" else 0j
                    self.assertLess(abs(full-f-d)/max(abs(full),abs(f)+abs(d),1e-35),4e-15)

    def test_F_only_vs_independent_analytic_F_dagger_F(self):
        e=math.sqrt(4*math.pi*ALPHA)
        for label,w in zip(EXPECTED,self.cards):
            scalar=w["module2_input"]["scalar"]["record"]["physical"]
            ml=w["module2_input"]["lepton_masses_GeV"]
            F=decode(w["yukawas"]["F"])
            W=(math.sin(scalar["gamma"])**2/scalar["mH1"]**2+
               math.cos(scalar["gamma"])**2/scalar["mH2"]**2)/(192*math.pi**2)
            for flavor,daughter in (("tauegamma",0),("taumugamma",1)):
                analytic=sum(np.conjugate(F[k,daughter])*F[k,2] for k in range(3))*W
                native=complex_pair(self.ledger["cards"][label][flavor]["OA1L_F_ONLY"])/e
                self.assertLess(abs(native+2*analytic/3)/max(abs(native),1e-35),4e-14)

    def test_source_observable_positive_and_phase_invariance(self):
        a=photon_rate(1+2j,.2-.4j,-.5+.2j,.4+.3j,ME,ME)
        phase=complex(math.cos(.71),math.sin(.71))
        b=photon_rate(phase*(1+2j),phase*(.2-.4j),
                      phase*(-.5+.2j),phase*(.4+.3j),ME,ME)
        self.assertAlmostEqual(a["photon_only_source_BR"]/b["photon_only_source_BR"],1.,places=12)
        self.assertAlmostEqual(a["dipole_leading_log_BR"]/b["dipole_leading_log_BR"],1.,places=12)
        for x in (a,b):
            self.assertIsNone(x["physical_total_BR"])
        with self.assertRaises(ValueError):
            photon_rate(1,0,0,0,MMU,MTAU)

    def test_source_analytic_e_light_limit_vs_independent_spinor(self):
        # Direct Dirac-spinor confirmation of the -4 K1L * K2R* cross
        # in the historical SARAH convention. A relative factor i from the
        # electromagnetic field strength is ESSENTIAL for this interference.
        M=MTAU; m=ME
        sn,sw=np.polynomial.legendre.leggauss(24)
        zn,zw=np.polynomial.legendre.leggauss(12)
        lo,hi=(2*m)**2,(M-m)**2
        logr=math.log(hi/lo)
        MET=np.array([1.,-1.,-1.,-1.])
        sigma=np.array([[.5j*(tree.G[mu]@tree.G[nu]-tree.G[nu]@tree.G[mu])
                         for nu in range(4)] for mu in range(4)])
        factor=4*math.pi*ALPHA
        norm=factor**2*M**5/(512*math.pi**3)
        one=0.
        both=0.
        for t,wt in zip(sn,sw):
            s=lo*math.exp(logr*(t+1)/2)
            jac=s*logr/2
            phase=math.sqrt(max(0.,tree.kallen(M*M,m*m,s)*tree.kallen(s,m*m,m*m)))
            phase/=512*math.pi**3*M**3*s
            for z,wz in zip(zn,zw):
                ps=tree.momenta(M,(m,m,m),s,z)
                def tensor(vec,dip):
                    direct=np.zeros((4,4,4,4),complex)
                    cross=np.zeros_like(direct)
                    for idx,crossed in ((2,False),(1,True)):
                        q=ps[idx]+ps[3];qcov=q*MET
                        q2=q[0]**2-np.dot(q[1:],q[1:])
                        arr=np.zeros_like(direct)
                        for mu in range(4):
                            vector=tree.G0@tree.G[mu]@(tree.PL*vec)
                            sigmaq=np.einsum('nab,n->ab',sigma[mu],qcov)
                            magnetic=1j*tree.G0@sigmaq@tree.PR*(M*dip/q2)
                            spectator=tree.G0@tree.G[mu]*MET[mu]
                            if crossed:
                                arr-=np.einsum('cb,ad->abcd',vector+magnetic,spectator)
                            else:
                                arr+=np.einsum('ab,cd->abcd',vector+magnetic,spectator)
                        if crossed:cross=arr
                        else:direct=arr
                    return factor*(direct+cross)
                v=tensor(1,0)
                vd=tensor(1,1)
                # identical final negative fermions (factor 1/2).
                one+=wt*wz*jac*phase*tree.spin_sum(v,ps,M,(m,m,m))/2
                both+=wt*wz*jac*phase*tree.spin_sum(vd,ps,M,(m,m,m))/2
        dipole=photon_rate(0,0,0,1,m,m)["dipole_leading_log_BR"]*GAMMA_TAU
        x=(both-one-dipole)/norm
        self.assertLess(abs(one/norm-1),2e-5)
        self.assertLess(abs(x+4),1e-3)

    def test_reject_wrong_source_checksum_and_nonfinite_inputs(self):
        import tempfile
        from pathlib import Path
        old=json.loads(K1_JSON.read_text())
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"input.json"
            old["source_sha256"]["generated"]="0"*64
            path.write_text(json.dumps(old))
            with self.assertRaises(ValueError):
                evaluate(k1_path=path)
        with self.assertRaises(ValueError):
            complex_pair([float('nan'),0])


if __name__=="__main__":
    unittest.main()
