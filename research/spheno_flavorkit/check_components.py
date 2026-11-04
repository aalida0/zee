"""Check numerical vertex readback and inspect individual raw scalar loops.

The K2-to-C relation in the output remains an unproved *candidate*. Component
residuals quantify a comparison, not a validation threshold or scheme error.
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from module3.core import neutral_dipole
COMPLEX = re.compile(r'\(\s*([^,]+),\s*([^\)]+)\)')

def pairs(line):
    return [complex(float(a), float(b)) for a, b in COMPLEX.findall(line)]

def pack(z):
    return [float(z.real), float(z.imag)]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--logs', type=Path, default=ROOT/'research/spheno_flavorkit/local/d15_runs')
    p.add_argument('--output', type=Path, default=ROOT/'research/spheno_flavorkit/local/d15_components.json')
    args = p.parse_args()
    data = json.loads((ROOT/'validation/module12/d12_benchmarks.json').read_text())
    records = []
    for n, group in enumerate(data['groups']):
        lines = (args.logs/f'group{n}.log').read_text().splitlines()
        sm = [float(x) for x in next(x for x in lines if 'D15_SM ' in x).split()[1:]]
        alpha, mi = sm[0], sm[5]
        masses = [float(x) for x in next(x for x in lines if 'D15_MASSES ' in x).split()[1:]]
        neutral = {k: np.zeros((3,3), complex) for k in ('hh1','hh2','Ah1','Ah2')}
        arrays = {k: np.zeros((3, 3), complex) for k in ('ZEL', 'ZER', 'F', 'Ye', 'Ye2')}
        zp = np.zeros((3, 3))
        vertices = {}
        sums = {}
        for line in lines:
            if 'D15_INPUT ' in line:
                prefix = line.split('(')[0].split()
                i, j, val = int(prefix[1])-1, int(prefix[2])-1, float(prefix[3])
                zp[i,j] = val
                for key, z in zip(arrays, pairs(line), strict=True):
                    arrays[key][i,j] = z
            if 'D15_NEUTRAL ' in line:
                prefix = line.split('(')[0].split()
                i, j, k = (int(v)-1 for v in prefix[1:4])
                vals = pairs(line)
                neutral[f'hh{k+1}'][i,j] = -vals[0]
                neutral[f'Ah{k+1}'][i,j] = -vals[2]
            if 'D15_VERTEX ' in line:
                prefix = line.split('(')[0].split()
                vertices[tuple(int(v)-1 for v in prefix[1:4])] = pairs(line)
            if 'D15_COMPONENT_' in line:
                prefix = line.split('(')[0].split()
                tag = prefix[0].removeprefix('D15_COMPONENT_')
                scalar = int(prefix[2] if tag == 'Hm' else prefix[1])
                key = f'{tag}{scalar}'
                sums[key] = sums.get(key, np.zeros(2, complex)) + np.array(pairs(line))
        if len(vertices) != 27 or not np.all(zp.any(axis=1)):
            raise ValueError('Incomplete vertex or mixing readback')
        # Generated analytical rules with the actual rotations and matrices.
        f, y, y2, zl, zr = (arrays[k] for k in ('F','Ye','Ye2','ZEL','ZER'))
        deviations = []
        for (k, a, r), actual in vertices.items():
            fl = sum(zl[a,j].conjugate() * (f[j,k]-f[k,j])*zp[r,2]/2 for j in range(3))
            fr = -sum((y[j,k].conjugate()*zp[r,0]+y2[j,k].conjugate()*zp[r,1])*zr[a,j] for j in range(3))
            expected = [fl, fr, fr.conjugate(), fl.conjugate()]
            deviations.extend(abs(np.array(actual)-expected))
        w = group['witnesses']['central']
        physical = w['module2_input']['scalar']['record']['physical']
        d = np.array(w['yukawas']['D']['real']) + 1j*np.array(w['yukawas']['D']['imag'])
        f0 = np.array(w['yukawas']['F']['real']) + 1j*np.array(w['yukawas']['F']['imag'])
        ideal_deviations = []
        row_signs = []
        for r, (ds, ss) in enumerate([(math.cos(physical['gamma']), math.sin(physical['gamma'])),
                                       (-math.sin(physical['gamma']), math.cos(physical['gamma']))], 1):
            target = np.array([-math.sin(physical['beta'])*ds, math.cos(physical['beta'])*ds, ss])
            sign = 1 if np.dot(zp[r], target) >= 0 else -1
            row_signs.append(sign)
            for k in range(3):
                for a in range(3):
                    expected = sign*np.array([-ss*f0[k,a], -ds*d[a,k].conjugate()])
                    ideal_deviations.extend(abs(np.array(vertices[k,a,r][:2])-expected))
        norm = -0.5/(math.sqrt(alpha*4*math.pi)*mi*16*math.pi**2)
        amps = w['signed_radiative']['mu_to_e_gamma']['signed_amplitudes']
        lookup = {'Ah2':['module3_A'], 'hh1':['module3_h'], 'hh2':['module3_H'],
                  'Hm2':['module3_H1_D','module3_H1_F'], 'Hm3':['module3_H2_D','module3_H2_F']}
        components = {}
        for key, names in lookup.items():
            sph = sums[key]*norm
            reference = sum((np.array([complex(amps[name]['C_'+ch]['real'], amps[name]['C_'+ch]['imag']) for ch in 'LR']) for name in names), np.zeros(2,complex))
            matched = None
            if key in neutral:
                mass = masses[{'hh1':6,'hh2':7,'Ah2':9}[key]]
                matched = neutral_dipole(neutral[key], mass, 1, 0, masses[:3])
            components[key] = {'same_input_candidate_relative_residual': [float(abs(k+c.conjugate())/abs(c)) if c else None for k,c in zip(sph,matched)] if matched is not None else None, 'K2': [pack(x) for x in sph], 'D12_C': [pack(x) for x in reference],
                               'candidate_relative_residual': [float(abs(k+c.conjugate())/abs(c)) if c else None for k,c in zip(sph,reference)]}
        records.append({'group':n, 'vertex_rule_max_abs':float(max(deviations)),
                        'frozen_vertex_max_abs':float(max(ideal_deviations)), 'scalar_row_signs':row_signs,
                        'input_max_abs_difference_F':float(np.max(abs(f-f0))),
                        'input_max_abs_difference_Ye':float(np.max(abs(y-(np.array(w['yukawas']['Ye']['real'])+1j*np.array(w['yukawas']['Ye']['imag']))))),
                        'input_max_abs_difference_Ye2':float(np.max(abs(y2-(np.array(w['yukawas']['Ye2']['real'])+1j*np.array(w['yukawas']['Ye2']['imag']))))),
                        'sm_readback':sm, 'masses_readback':masses, 'components':components})
    args.output.write_text(json.dumps({'status':'DIAGNOSTIC_ONLY', 'records':records}, indent=2)+'\n')
    print(json.dumps(records, indent=2))

if __name__ == '__main__':
    main()
