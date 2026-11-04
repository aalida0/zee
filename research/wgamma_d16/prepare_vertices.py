"""Generate independent native-vertex assertions; never change the frozen model."""
import copy
import json
import math
from pathlib import Path

import numpy as np

from module1.scalar_constraints import reconstruct
from module3.core import vertices
from module4.couplings import rotations
from module4.native import wl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def prepare():
    p0 = json.loads((ROOT / 'module1/example.json').read_text())['physical']
    points = [p0, dict(p0, mh2=437., ma=469., mH1=347., mH2=861.,
                       alpha=.31, beta=1.07, gamma=-.43, m12sq=31000.)]
    statements, records = [], []
    for point_index, p in enumerate(points):
        lag, _, _ = reconstruct(p)
        zh, za, zp = rotations(p)
        ml = np.array([.00051099895, .1056583755, 1.77686])
        rng = np.random.default_rng(16031 + point_index)
        D = .03 * (rng.normal(size=(3, 3)) + 1j*rng.normal(size=(3, 3)))
        F = .02 * (rng.normal(size=(3, 3)) + 1j*rng.normal(size=(3, 3)))
        F -= F.T
        sb, cb = math.sin(p['beta']), math.cos(p['beta'])
        S = np.diag(math.sqrt(2)*ml/p['v'])
        mats = dict(ZH=zh, ZA=za, ZP=zp, Ue=np.eye(3), Ve=np.eye(3),
                    Ye=cb*S-sb*D, Ye2=sb*S+cb*D, Fzee=F)
        e, g2 = .313, .647
        sw = e/g2
        mw = g2*p['v']/2  # same tree EW convention at every vertex
        for xi in (.5, 1., 3.):
            rules = [f'{name}[{a+1},{b+1}]->{wl(val)}'
                     for name, mat in mats.items()
                     for a, row in enumerate(mat) for b, val in enumerate(row)]
            rules += [f'{k}->{wl(v)}' for k, v in dict(lag, v1=p['v']*cb,
                      v2=p['v']*sb, g2=g2, g1=e/math.sqrt(1-sw*sw),
                      ThetaW=math.asin(sw)).items()]
            rules += [f'RXi[Wm]->{wl(xi)}']
            statements.append('rules={' + ','.join(rules) + '};')

            def check(key, ch, expected):
                statements.append(f'record[{json.dumps(key)},{ch},{wl(expected)},rules];')

            for k in (1, 2):
                kap = float(zh[k-1] @ np.array([cb, sb]))
                ms = p['mh1'] if k == 1 else p['mh2']
                check(f'sWW_{k}', 'g[lt2,lt3]', 1j*2*mw*mw*kap/p['v'])
                check(f'sGG_{k}', '1', -1j*ms*ms*kap/p['v'])
                for c in ('gWm', 'gWmC'):
                    check(f'sGhost_{{{k}, {c}}}', '1', -1j*xi*mw*mw*kap/p['v'])
                for c in (1, 2):
                    mom = ('Mom[hh[{' + str(k) + '}],lt3]-Mom[Hm[{1}],lt3]'
                           if c == 1 else
                           'Mom[conj[Hm[{1}]],lt3]-Mom[hh[{' + str(k) + '}],lt3]')
                    check(f'sWG_{{{k}, {c}}}', mom, -.5j*g2*kap)
                    check(f'sPhotonWG_{{{k}, {c}}}', 'g[lt2,lt3]', .5j*e*g2*kap)
                for a in (2, 3):
                    overlap = float(zh[k-1] @ zp[a-1, :2])
                    check(f'sWH_{{{k}, {a}}}',
                          f'Mom[hh[{{{k}}}],lt3]-Mom[Hm[{{{a}}}],lt3]', -.5j*g2*overlap)
                C = vertices(D, p, ml)['h' if k == 1 else 'H'][0]
                for a in (1, 2):
                    for b in (1, 2):
                        check(f'LFV_{{{k}, {a}, {b}}}', 'PL', -1j*C[a-1, b-1])
                        check(f'LFV_{{{k}, {a}, {b}}}', 'PR', -1j*C[b-1, a-1].conjugate())
            for a in (1, 2, 3):
                overlap = float(zp[a-1, :2] @ np.array([cb, sb]))
                for orientation in ('photonWG_', 'photonWGconj_'):
                    check(orientation+str(a), 'g[lt1,lt2]', 1j*e*mw*overlap)
                check(f'photonGG_{a}', f'Mom[conj[Hm[{{{a}}}]],lt1]-Mom[Hm[{{{a}}}],lt1]', -1j*e)
            check('photonPhotonWW', 'g[lt1,lt2]*g[lt3,lt4]', -2j*e*e)
            check('photonPhotonWW', 'g[lt1,lt3]*g[lt2,lt4]', 1j*e*e)
            check('photonPhotonWW', 'g[lt1,lt4]*g[lt2,lt3]', 1j*e*e)
            check('photonPhotonGG', 'g[lt1,lt2]', 2j*e*e)
            check('photonGhostMinus', 'Mom[gWm,lt1]', -1j*e)
            check('photonGhostPlus', 'Mom[gWmC,lt1]', 1j*e)
            for key in ('AGhostMinus', 'AGhostPlus'):
                check(key, '1', 0)
            check('AWG_1', 'Mom[Ah[{2}],lt3]-Mom[Hm[{1}],lt3]', 0)
            check('AWG_2', 'Mom[Ah[{2}],lt3]-Mom[conj[Hm[{1}]],lt3]', 0)
            check('Glepton', 'PL', -1j*math.sqrt(2)*ml[0]/p['v'])
            check('Glepton', 'PR', 0)
            check('Wlepton', 'LorentzProduct[gamma[lt3],PL]', -1j*g2/math.sqrt(2))
            for a in (2, 3):
                d = float(zp[a-1, :2] @ np.array([-sb, cb]))
                s = float(zp[a-1, 2])
                for i in (1, 2):
                    for j in (1, 2):
                        check(f'Hlepton_{{{a}, {i}, {j}}}', 'PL', -1j*d*D[i-1, j-1])
                        check(f'Hlepton_{{{a}, {i}, {j}}}', 'PR', -1j*s*F[j-1, i-1].conjugate())
        records.append(dict(physical=copy.deepcopy(p),
                            D=[[[z.real, z.imag] for z in row] for row in D],
                            F=[[[z.real, z.imag] for z in row] for row in F]))
    local = HERE / 'local'
    local.mkdir(exist_ok=True)
    (local / 'vertex_witnesses.m').write_text('\n'.join(statements) + '\n')
    (local / 'vertex_inputs.json').write_text(json.dumps(records, indent=2) + '\n')
    print('Prepared', sum(s.startswith('record[') for s in statements), 'native assertions')


if __name__ == '__main__':
    prepare()
