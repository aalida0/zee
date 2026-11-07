#!/usr/bin/env python3
"""Arithmetic audit of four saved D12 cards; no new amplitudes or model points."""
import hashlib
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parents[3]
path = root / 'validation/module12/d12_benchmarks.json'
data = json.loads(path.read_text())
def matrix(x):
    return [[complex(x['real'][i][j], x['imag'][i][j]) for j in range(3)] for i in range(3)]
def cval(z):
    return {'real': z.real, 'imag': z.imag, 'abs': abs(z)}
def norm(z):
    return math.sqrt(sum(abs(v)**2 for v in z))
def cpair(x):
    return [complex(v['real'], v['imag']) for v in x]
rows = []
for g in data['groups']:
    w = g['witnesses']['low_joint']
    f, d = (matrix(w['yukawas'][k]) for k in ('F', 'D'))
    rad = w['signed_radiative']['mu_to_e_gamma']
    groups = {k: cpair(v) for k, v in rad['grouped_amplitudes'].items()}
    summed = [sum(v[i] for v in groups.values()) for i in range(2)]
    saved = [complex(rad[k]['real'], rad[k]['imag']) for k in ('C_L', 'C_R')]
    rows.append({'id': w['id'], 'yukawa_sha256': w['yukawa_sha256'],
        'D_em': cval(d[0][1]), 'D_me': cval(d[1][0]),
        'FdagF_em': cval(sum(f[k][0].conjugate()*f[k][1] for k in range(3))),
        'DdagD_em': cval(sum(d[k][0].conjugate()*d[k][1] for k in range(3))),
        'DDdag_em': cval(sum(d[0][k]*d[1][k].conjugate() for k in range(3))),
        'retained_complex_CL_CR': [cval(x) for x in saved],
        'retained_norm': norm(saved),
        'group_norms': {k: norm(v) for k, v in groups.items()},
        'group_sum_residual': norm([a-b for a,b in zip(summed,saved)]),
        'note': 'Coupling products are diagnostics, not missing amplitude estimates; no chirality or diagram matching assumed.'})
print(json.dumps({'input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'cards': rows}, indent=2))
