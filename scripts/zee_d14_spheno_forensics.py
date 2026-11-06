#!/usr/bin/env python3
"""Read/hash-check saved D12 SPheno artifacts; never execute a native backend."""
import argparse
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from module14.scan import file_sha
from module2.core import forward


def slha(path):
    blocks, decays = {}, {}
    current = decay = None
    for line in path.read_text().splitlines():
        t = line.split('#')[0].split()
        if not t:
            continue
        if t[0].upper() == 'BLOCK':
            current = blocks.setdefault(t[1].upper(), {})
            decay = None
        elif t[0].upper() in ('DECAY', 'DECAY1L'):
            decay = {'total': float(t[2]), 'channels': []}
            decays.setdefault(t[0].upper(), {})[int(t[1])] = decay
            current = None
        elif current is not None:
            try:
                current[tuple(map(int, t[:-1]))] = float(t[-1].replace('D', 'E'))
            except ValueError:
                pass  # Textual SPINFO entries are not numerical evidence.
        elif decay is not None:
            decay['channels'].append({'br': float(t[0]), 'pdgs': list(map(int, t[2:]))})
    return blocks, decays


def matrix(b, name):
    return np.array([[b[name][i, j]+1j*b.get('IM'+name, {}).get((i, j), 0.)
                      for j in range(1, 4)] for i in range(1, 4)])


def inspect(local):
    evidence = json.loads((ROOT/'module14/physics_adapters/spheno_build_evidence.json').read_text())
    paths = {}
    for c in evidence['comparisons']:
        for name, sha in c['files_sha256'].items():
            paths[local/'runtime'/f"group{c['group']}"/name] = sha
    for name, sha in evidence['generated_source_sha256'].items():
        paths[local/'output'/name] = sha
    for name, sha in evidence['corrected_model_sha256'].items():
        paths[local/'models/ZeeTypeII'/name] = sha
    for name, key in [('generation.log', 'generation_log_sha256'), ('full-build.log', 'full_build_log_sha256')]:
        paths[local/name] = evidence[key]
    paths[ROOT/'validation/module12/d12_benchmarks.json'] = evidence['input_reference_sha256']
    # Complete the hash gate before interpreting any native artifact.
    for path, sha in paths.items():
        if not path.is_file() or file_sha(path) != sha:
            raise ValueError('Missing/changed pinned artifact: '+str(path))
    groups = json.loads((ROOT/'validation/module12/d12_benchmarks.json').read_text())['groups']
    rows = []
    for c, group in zip(evidence['comparisons'], groups):
        directory = local/'runtime'/f"group{c['group']}"
        tree, td = slha(directory/'tree.spc')
        full, fd = slha(directory/'full.spc')
        inventories = []
        for pdg, d in fd['DECAY1L'].items():
            channels = []
            for ch in d['channels']:
                br_tree = next((v['br'] for v in fd.get('DECAY', {}).get(pdg, {}).get('channels', [])
                                if v['pdgs'] == ch['pdgs']), None)
                parent = full['MASS'][pdg,]
                external = [full['MASS'].get((abs(k),), 0.) for k in ch['pdgs']]
                phase_space = None
                if len(external) == 2:
                    phase_space = math.sqrt(max(0., (1-((external[0]+external[1])/parent)**2)
                                                   *(1-((external[0]-external[1])/parent)**2)))
                channels.append(dict(ch, width_GeV=d['total']*ch['br'],
                    tree_at_full_spectrum_GeV=None if br_tree is None else br_tree*fd['DECAY'][pdg]['total'],
                    two_body_sqrt_lambda_over_parent_squared=phase_space,
                    external_masses_GeV=external))
            inventories.append({'pdg': pdg, 'mass_GeV': full['MASS'][pdg,],
                'total_GeV': d['total'], 'printed_br_sum': sum(v['br'] for v in channels),
                'unprinted_signed_remainder_GeV': d['total']*(1-sum(v['br'] for v in channels)),
                'channels': channels})
        zh = lambda b: np.array([[b['SCALARMIX'][i, j] for j in (1, 2)] for i in (1, 2)])
        overlap = abs(zh(full)@zh(tree).T)**2
        p = group['witnesses']['central']['module2_input']['scalar']['record']['physical']
        beta = np.arctan(full['MINPAR'][10,])
        native_d = -np.sin(beta)*matrix(full, 'YE')+np.cos(beta)*matrix(full, 'YEE2')
        w = group['witnesses']['central']
        original_d = np.array(w['yukawas']['D']['real'])+1j*np.array(w['yukawas']['D']['imag'])
        # Existing forward kernel at the exact saved scalar/lepton inputs only.
        reference_args = dict(m1=p['mH1'], m2=p['mH2'], gamma=p['gamma'], ml=w['module2_input']['lepton_masses_GeV'])
        native_d_masses = np.linalg.svd(forward(matrix(full, 'FZEE'), native_d, **reference_args), compute_uv=False)[::-1]
        s = np.cos(beta)*matrix(full, 'YE')+np.sin(beta)*matrix(full, 'YEE2')
        rows.append({'group': c['group'], 'id': c['id'], 'decays': inventories,
            'hWW_coupling_from_saved_full_parameters_GeV': {
                'real': full['GAUGE'][2,]**2/2*(full['HMIX'][102,]*full['SCALARMIX'][1,1]
                                             +full['HMIX'][103,]*full['SCALARMIX'][1,2]),
                'imag': 0., 'scope': 'Polynomial tree coupling at printed full parameters; not saved loop amplitude'},
            'tree_to_full_scalar_overlap_squared': overlap.tolist(),
            'tree_scalar_masses_GeV': [tree['MASS'][k,] for k in (25, 35)],
            'full_scalar_masses_GeV': [full['MASS'][k,] for k in (25, 35)],
            'full_vev_GeV': full['HMIX'][3,], 'tree_vev_GeV': tree['HMIX'][3,],
            'native_D_minus_original_max_abs': float(np.max(abs(native_d-original_d))),
            'native_running_mass_combination_GeV': (s.diagonal()*full['HMIX'][3,]/np.sqrt(2)).real.tolist(),
            'native_D_in_original_forward_masses_eV': native_d_masses.tolist(),
            'original_target_masses_eV': c['module2_neutrino_singular_values_eV'],
            'full_neutrino_masses_eV': c['full_scheme_neutrino_masses_eV'],
            'native_D_forward_to_full_relative_differences': (native_d_masses/np.array(c['full_scheme_neutrino_masses_eV'])-1).tolist(),
            'tree_neutrino_rotation_max_abs': float(np.max(abs(matrix(tree, 'UVMIX')))),
            'scale_GeV': 160., 'printed_branching_fraction_threshold': 1e-4})
    return {'status': 'DIAGNOSTIC_ONLY', 'SPHENO_FULL_LOOP_OPERATIVE': 'NO',
        'width_cause_status': 'FULL_LOOP_WIDTH_CAUSE_UNRESOLVED',
        'source_locations': {
            'Model_Data_ZeeTypeII.f90': '2074-2106: running EW/Ye matching, Ye2 fixed input',
            'LoopMasses_ZeeTypeII.f90': '132-174,212-305: EW/tadpoles; 586-614,854-1024: zero tree neutrino and one-loop self-energy; 1204-1386: scalar pole iteration',
            'Boundaries_ZeeTypeII.f90': '1606-1624: full loop masses followed by effective-SM light-Higgs overwrite',
            'LoopDecays/Wrapper_LoopDecay_hh_ZeeTypeII.f90': '2567-2665: hWW tree/interference plus real radiation, multiplicity 2',
            'LoopDecays/LoopDecayhh_ZeeTypeII.f90': '6531-6564: complex hWW coupling passed to real-photon routine',
            'BranchingRatios_ZeeTypeII.f90': '136-139: total is signed sum of channel array',
            'InputOutput_ZeeTypeII.f90': '5089-5300: positive BR threshold in DECAY1L output',
            'Settings.f90': '29,37-62: interference-only default, OS external kinematics, MS scheme and IR settings'},
        'native_reruns': 0, 'model_fixes': 0, 'verified_artifacts': len(paths),
        'reader_source_sha256': file_sha(__file__),
        'forward_kernel_sha256': file_sha(ROOT/'module2/core.py'),
        'artifact_hashes': {str(p.relative_to(local)) if p.is_relative_to(local) else str(p.relative_to(ROOT)): s
                            for p, s in paths.items()},
        'limitations': ['Printed positive BRs are thresholded; unprinted signed channel sum is unavailable.',
            'Wave/vertex/counterterm/real and complex amplitude values were not saved.',
            'Native D substitution is a scheme diagnostic, not a reconstructed native self-energy.'],
        'points': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = inspect(args.local)
    with args.output.open('x') as stream:
        stream.write(json.dumps(report, sort_keys=True, indent=2, allow_nan=False)+'\n')
