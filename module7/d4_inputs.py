"""D4 authenticated D2 inverse reuse and explicit LO decay input card."""
import cmath
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from module1.scalar_constraints import reconstruct
from module2.interface import canonical_hash, decode, encode, evaluate, strict_loads
from module6.d2_family_runner import generate

ROOT = Path(__file__).resolve().parents[1]
PINNED = {
    'module3/example.json': '6a55f774041a9d5e06bd6ea30a628bfcf5c840af0ddff30bce5f692a551c2915',
    'validation/module6/d2_scoped_scan.json': '79f4164b1bf74b21576e2711960dca3a415cc9eb03f133eb5a885ad10b607b84',
    'validation/module7/cascade_d3.json': 'cf9a9314197265a172305c287b9c3d306ec654e83ceeae6374e1dcf7c3346376',
}
SM = {
    'units': 'GeV unless dimensionless',
    'quark_order': ['u', 'c', 't', 'd', 's', 'b'],
    'quark_reference_masses': [0.00216, 1.2730, 162.5, 0.00470, 0.0935, 4.183],
    'quark_reference_scales': [2., 1.2730, 162.5, 2., 2., 4.183],
    'kinematic_masses': [0.00216, 1.2730, 172.4, 0.00470, 0.0935, 4.78],
    'kinematic_scheme': 't pole from cross section; b approximate two-loop pole; light/c reference MS masses used as partonic thresholds',
    'quark_source': 'https://pdg.lbl.gov/2024/download/db2024.pdf',
    'bottom_pole_source': 'https://pdg.lbl.gov/2024/listings/rpp2024-list-b-quark.pdf',
    'yukawa_scheme': 'MSbar one-loop QCD evolution to mother mass; continuous matching at mb=4.183 and mt_pole=172.4; no finite threshold terms',
    'alpha_s_mZ': 0.1180,
    'alpha_s_reference_GeV': 91.1876,
    'QCD_source': 'https://pdg.lbl.gov/2024/reviews/rpp2024-rev-qcd.pdf (9.3), one-loop mass anomalous dimension',
    'running_formula': 'alpha(Q)=alpha(q)/(1+alpha(q)*(11-2nf/3)*ln(Q/q)/(2pi)); m(Q)/m(q)=(alpha(Q)/alpha(q))**(12/(33-2nf)) piecewise',
    'scheme_sensitivity': 'also report same kinematics with unevolved reference Yukawa masses; diagnostic, not theory uncertainty',
    'CKM_Wolfenstein': {'lambda': 0.22501, 'A': 0.826, 'rhobar': 0.1591, 'etabar': 0.3523},
    'CKM_source': 'https://pdg.lbl.gov/2024/reviews/rpp2024-rev-ckm-matrix.pdf Eq12.3,12.4,12.26 (exact unitary construction)',
    'lepton_masses': [0.00051099895, 0.1056583755, 1.77686],
    'lepton_scheme': 'frozen D2 charged-lepton pole snapshot; no QED running',
    'lepton_source': 'module3/example.json module2_input.lepton_masses_GeV; https://pdg.lbl.gov/2024/listings/particle_properties.html',
    'EW': {'mW': 80.379, 'mZ': 91.1876, 'v': 246.21965},
    'EW_scheme': 'frozen D2 on-shell MW/MZ; g2=2mW/v, cw=mW/mZ, g1=g2*tan(thetaW)',
    'EW_source': 'module3/example.json SHA-bound snapshot; 2021 reference Appendix C; v from frozen scalar normalization',
    'neutrino_scheme': 'exact massless tree-level native Fv; inclusive three unitary-rotated neutrinos, both helicities; loop-induced mass effects uncomputed',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_pinned():
    for name, expected in PINNED.items():
        if sha(ROOT/name) != expected:
            raise ValueError('Pinned bytes mismatch: '+name)
    return [strict_loads((ROOT/name).read_text()) for name in PINNED]


def families():
    """Fast inverse only. Never execute pilot(), vacuum(), or scalar scan."""
    seed, d2, d3 = load_pinned()
    for name, expected in d2['source_sha256'].items():
        if name.startswith(('module1/', 'module2/', 'models/')) and sha(ROOT/name) != expected:
            raise ValueError('Frozen source mismatch: '+name)
    rows, _ = generate(seed, d2['selected_spectra'])
    result = []
    for row, evidence in zip(rows, d2['points']):
        n = evaluate(row['module2_input'])
        if (row['benchmark_id'] != evidence['benchmark_id']
                or canonical_hash(row) != evidence['input_sha256']
                or canonical_hash(row['module2_input']) != evidence['module2_input_sha256']
                or canonical_hash(n['D']) != evidence['D_sha256']
                or canonical_hash(n) != evidence['per_sector_output_sha256']['neutrino']):
            raise ValueError('D2 inverse hash mismatch')
        result.append((row, n, evidence))
    if len(result) != 12:
        raise ValueError('Require twelve conditional D2 families')
    return result, d3


def ckm():
    w = SM['CKM_Wolfenstein']
    l, a, r, e = (w[k] for k in ('lambda', 'A', 'rhobar', 'etabar'))
    z = a*l**3*complex(r, e)*math.sqrt(1-a*a*l**4)/(math.sqrt(1-l*l)*(1-a*a*l**4*complex(r, e)))
    s12, s23, s13 = l, a*l*l, abs(z)
    c12, c23, c13 = [math.sqrt(1-s*s) for s in (s12, s23, s13)]
    return np.array([[c12*c13, s12*c13, z.conjugate()],
                     [-s12*c23-c12*s23*z, c12*c23-s12*s23*z, s23*c13],
                     [s12*s23-c12*c23*z, -c12*s23-s12*c23*z, c23*c13]])


def alpha_segment(alpha, q, Q, nf):
    return alpha/(1+alpha*(11-2*nf/3)*math.log(Q/q)/(2*math.pi))


def alpha_s(Q):
    b, t = SM['quark_reference_masses'][5], SM['kinematic_masses'][2]
    z, a = SM['alpha_s_reference_GeV'], SM['alpha_s_mZ']
    if Q < b:
        return alpha_segment(alpha_segment(a, z, b, 5), b, Q, 4)
    if Q > t:
        return alpha_segment(alpha_segment(a, z, t, 5), t, Q, 6)
    return alpha_segment(a, z, Q, 5)


def running_mass(m, q, Q):
    if Q < q:
        return m/running_mass(1., Q, q)
    thresholds = [SM['quark_reference_masses'][5], SM['kinematic_masses'][2]]
    knots = [q]+[x for x in thresholds if q < x < Q]+[Q]
    for low, high in zip(knots, knots[1:]):
        mid = math.sqrt(low*high)
        nf = 4 if mid < thresholds[0] else 5 if mid < thresholds[1] else 6
        m *= (alpha_s(high)/alpha_s(low))**(12/(33-2*nf))
    return m


def yukawa_masses(Q):
    return [running_mass(m, q, Q) for m, q in zip(SM['quark_reference_masses'], SM['quark_reference_scales'])]


def rotations(p):
    cb, sb, cg, sg, ca, sa = [f(p[k]) for f,k in
        [(math.cos,'beta'),(math.sin,'beta'),(math.cos,'gamma'),(math.sin,'gamma'),(math.cos,'alpha'),(math.sin,'alpha')]]
    return (np.array([[cb,sb,0],[-sb*cg,cb*cg,sg],[sb*sg,-cb*sg,cg]]),
            np.array([[ca,sa],[-sa,ca]]), np.array([[cb,sb],[-sb,cb]]))


def native_card(p, n, Q, identity):
    zp, zh, za = rotations(p)
    pars, _, _ = reconstruct(p)
    cb, sb = math.cos(p['beta']), math.sin(p['beta'])
    masses = yukawa_masses(Q)
    g = 2*SM['EW']['mW']/p['v']; cw = SM['EW']['mW']/SM['EW']['mZ']
    rules = dict(pars, ZP=zp.tolist(), ZH=zh.tolist(), ZA=za.tolist(),
                 g2=g, g1=g*math.sqrt(1-cw*cw)/cw, ThetaW=math.acos(cw),
                 v1=p['v']*cb, v2=p['v']*sb)
    rules.update({k: encode(np.eye(3,dtype=complex)) for k in ['Vu','Uu','Ud','Ve','Ue']})
    rules.update(Vd=encode(ckm().conj().T),
                 Yu=encode(np.diag(np.sqrt(2)*np.array(masses[:3])/(p['v']*sb)).astype(complex)),
                 Yd=encode(np.diag(np.sqrt(2)*np.array(masses[3:])/(p['v']*cb))@ckm().conj().T),
                 Fzee=n['F'], Ye=n['Ye'], Ye2=n['Ye2'])
    return {'id': identity, 'physical': dict(p), 'Q_GeV': Q, 'rules': rules}


def native_cards():
    data, _ = families()
    cards = []
    for row,n,_ in data:
        p = row['module2_input']['scalar']['record']['physical']
        for k in (1,2):
            cards.append(native_card(p,n,p['mH'+str(k)],row['benchmark_id']+f'/H{k}'))
    # Distinct complex matrices and non-aligned angles falsify transpose/phase shortcuts.
    p = dict(data[0][0]['module2_input']['scalar']['record']['physical'])
    rng = np.random.default_rng(4154)
    f = rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)); f=(f-f.T)*.03
    ye = (rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.02
    ye2 = (rng.normal(size=(3,3))+1j*rng.normal(size=(3,3)))*.03
    n = {'F': encode(f), 'Ye': encode(ye), 'Ye2': encode(ye2)}
    for beta in (.6,1.394):
        for gamma in (0.,math.pi/2,-math.pi/2,1.089,-1.089,math.pi/2-1.089):
            p.update(beta=beta,gamma=gamma,alpha=.43)
            cards.append(native_card(p,n,700.,f'control/{beta}/{gamma}'))
    return cards


def prepare_native():
    cards = native_cards()
    path = ROOT/'validation/module7/local/d4_native_inputs.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(cards,allow_nan=False))
    print('D2 hash closures: 12; native input cases:',len(cards))


if __name__ == '__main__':
    prepare_native()
