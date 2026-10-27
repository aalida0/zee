"""Independent amplitudes checked against actual SARAH EWSB coefficients.

All incoming native coefficients retain i. Color delta is stripped once; Nc=3
belongs in the fermion width. H+ is conj[Hm[k+1]], H- is Hm[k+1].
"""
import json
import math

import numpy as np
from module2.interface import canonical_hash, decode
from module7.d4_inputs import ROOT, rotations, sha, yukawa_masses, ckm, native_cards


def trilinear(p, pars, neutral):
    """Project d(M_charged^2)/d h_j from the frozen potential, in GeV."""
    zp, zh, _ = rotations(p)
    x, y = zh[neutral-1]
    v1, v2 = p['v']*math.cos(p['beta']), p['v']*math.sin(p['beta'])
    a = pars
    cross = (a['Lambda4']+a['Lambda5'])*(v2*x+v1*y)/2
    matrix = np.array([
        [a['Lambda1']*v1*x+a['Lambda3']*v2*y, cross, a['Mu4']*y/math.sqrt(2)],
        [cross, a['Lambda2']*v2*y+a['Lambda3']*v1*x, -a['Mu4']*x/math.sqrt(2)],
        [a['Mu4']*y/math.sqrt(2), -a['Mu4']*x/math.sqrt(2),
         a['K1']*v1*x+a['K2']*v2*y-a['K12']*(v2*x+v1*y)]])
    return float(zp[1]@matrix@zp[2])


def leptonic(p, n, k):
    """Native H+ PL=-i s_k F_ji, PR=-i d_k D_ij*, in flavor basis.

    D has (charged right, neutrino left) indices. Native tree neutrinos are
    massless. The two helicities are orthogonal; no F-D interference survives.
    For any unitary U, F_ji -> (U.T F)_ai and D_ij* -> (D* U*)_ia.
    Each row/column norm is invariant, including all three neutrinos once.
    No 1/2 Majorana identical-particle factor: charged lepton and neutrino differ.
    """
    zp, _, _ = rotations(p)
    f, ye, ye2 = (decode(n[key]) for key in ('F','Ye','Ye2'))
    return -1j*zp[k,2]*f.T, -1j*(zp[k,0]*ye.conj()+zp[k,1]*ye2.conj())


def expected_coefficients(card):
    p, rules, Q = card['physical'], card['rules'], card['Q_GeV']
    zp, zh, za = rotations(p)
    masses = yukawa_masses(Q); V = ckm(); g = rules['g2']
    result = []
    # Type-II physical chiral amplitudes, independent of native nested sums.
    for k in (1,2):
        doublet = math.cos(p['gamma']) if k == 1 else -math.sin(p['gamma'])
        for i in range(3):
            for j in range(3):
                a = math.sqrt(2)/p['v']*masses[i]/math.tan(p['beta'])*doublet*V[i,j]
                b = math.sqrt(2)/p['v']*masses[j+3]*math.tan(p['beta'])*doublet*V[i,j]
                result.extend([[1j*a,1j*b],[1j*b.conjugate(),1j*a.conjugate()]])
    for k in (1,2):
        for j in range(2):
            c = -1j*g/2*float(zh[j]@zp[k,:2])
            result.extend([[c],[c]])
    for k in (1,2):
        c = g/2*float(za[1]@zp[k,:2]);result.extend([[c],[c]])
    result.extend([[-1j*trilinear(p,rules,1)],[-1j*trilinear(p,rules,2)],[0j]]*2)
    n = {'F': rules['Fzee'], 'Ye': rules['Ye'], 'Ye2': rules['Ye2']}
    for k in (1,2):
        a,b = leptonic(p,n,k)
        for i in range(3):
            for j in range(3):
                result.extend([[a[i,j],b[i,j]],[-b[i,j].conjugate(),-a[i,j].conjugate()]])
    cw = math.cos(rules['ThetaW'])
    result.extend([[0j],[1j*g*math.sin(2*p['gamma'])/(4*cw)]]+[[0j]]*8)
    return result


def validate_native():
    local = ROOT/'validation/module7/local'
    raw = json.loads((local/'d4_native.json').read_text())
    cards = json.loads((local/'d4_native_inputs.json').read_text())
    if canonical_hash(cards) != canonical_hash(native_cards()):
        raise ValueError('Native inputs do not reproduce authenticated D2 families and controls')
    if ('15.0.1' not in raw['math_version'] or raw['sarah_version'] != '4.15.4'
            or raw['input_sha256'] != sha(local/'d4_native_inputs.json')):
        raise ValueError('Native version/input mismatch')
    for name, digest in raw['source_sha256'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Native source changed: '+name)
    for flag in ['exact_zero_CP_A','exact_zero_offdiagonal_photon','exact_zero_WZ_Wphoton',
                 'momentum_differences_verified','chirality_labels_verified']:
        if raw.get(flag) is not True:
            raise ValueError('Native structural proof missing: '+flag)
    residuals = []
    count = 0
    if len(cards) != 36 or len(raw['numeric_cases']) != len(cards) or len(raw['queries']) != 100:
        raise ValueError('Native case inventory mismatch')
    for card, case in zip(cards,raw['numeric_cases']):
        if card['id'] != case['id']:
            raise ValueError('Native case ID mismatch')
        expected = expected_coefficients(card)
        maxima = {'quarks':0.,'W_neutrals':0.,'trilinears':0.,'leptons':0.,'gauge_controls':0.}
        for index,(want,got) in enumerate(zip(expected,case['coefficients'])):
            if len(want) != len(got):raise ValueError('Native chirality count mismatch')
            if len(expected) != len(case['coefficients']):raise ValueError('Native coefficient count mismatch')
            sector = ('quarks' if index<36 else 'W_neutrals' if index<48 else
                      'trilinears' if index<54 else 'leptons' if index<90 else 'gauge_controls')
            for a,b in zip(want,got):
                b = complex(b['real'],b['imag'])
                residual = abs(a-b)
                if not math.isfinite(residual) or residual > 2e-10*max(1.,abs(a)):
                    raise ValueError(f'Native amplitude conflict {card["id"]} query {index}: {a} vs {b}')
                maxima[sector] = max(maxima[sector],residual);count += 1
        residuals.append({'id':card['id'],'maximum_absolute_residual_by_sector':maxima})
    # Retain representative genuine expressions; full cases remain ignored.
    indices = [0,1,16,18,19]+list(range(36,54))+[54,55,56,57,72,73,74,75]+list(range(90,100))
    return {'status':'NATIVE_ALL_COMPETING_VERTICES_VERIFIED',
            'math_version':raw['math_version'],'sarah_version':raw['sarah_version'],
            'sarah_sha256':raw['sarah_sha256'],'source_sha256':raw['source_sha256'],
            'input_sha256':raw['input_sha256'],'raw_output_sha256':sha(local/'d4_native.json'),
            'native_queries':100,'numeric_cases':36,'signed_complex_coefficient_comparisons':count,
            'exact_zero_CP_A':True,'exact_zero_offdiagonal_photon':True,'exact_zero_WZ_Wphoton':True,
            'momentum_differences_verified':True,'chirality_labels_verified':True,
            'native_falsifier_case':{'input':cards[27],'output':raw['numeric_cases'][27]},
            'residuals':residuals,'representative_native_vertices':[
                {'query_index':i,'query':raw['queries'][i],'vertex':raw['raw_vertices'][i]} for i in indices]}


if __name__ == '__main__':
    evidence = validate_native()
    (ROOT/'validation/module7/d4_native_validation.json').write_text(json.dumps(evidence,indent=2,allow_nan=False)+'\n')
    print(evidence['status'],evidence['signed_complex_coefficient_comparisons'])
