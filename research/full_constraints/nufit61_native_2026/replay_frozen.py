"""Physics-source-pinned NuFIT 6.1 screen of the FOUR frozen Zee witnesses.

Read-only replay of D12 low_joint D7/F13 NO/IO cards. Recomputes the
unchanged Module2 neutrino mass matrix, hashes outputs and Yukawas against
frozen witnesses, checks its closure and perturbativity, then applies the
seven native NuFIT 6.1 projections using a cached original XZ archive.

No Monte Carlo, no scanner mutation, no cosmology acceptance, no full 6D
oscillation confidence. Output is a scoped neutrino filter, not a global Zee
parameter-space acceptance.

python3 -m research.full_constraints.nufit61_native_2026.replay_frozen \
  --archive-dir NuFIT --output /tmp/nufit61_frozen_final.json
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from module2.interface import canonical_hash, decode, evaluate
from .scoped_compatibility import NuFIT61Compatibility
from .saved_targets import D12, D12_SHA256


def run(archive_dir, selection='IC24', verify_reconstruction=True):
    if hashlib.sha256(D12.read_bytes()).hexdigest() != D12_SHA256:
        raise ValueError('Frozen D12 file changed: aborting')
    frozen = json.loads(D12.read_text())
    if len(frozen['groups']) != 4:
        raise ValueError('Expected exactly four original scalar/NO-IO groups')
    filters = {order:NuFIT61Compatibility(archive_dir,order,selection)
               for order in ('NO','IO')}
    rows = []
    seen = set()
    for group in frozen['groups']:
        ordering = group['ordering']
        scalar = group['scalar']
        key = (scalar,ordering)
        if key in seen:
            raise ValueError('Duplicate frozen group')
        seen.add(key)
        witness = group['witnesses']['low_joint']
        inp = witness['module2_input']
        if inp['ordering'] != ordering:
            raise ValueError('Witness ordering mismatch')
        if canonical_hash(inp['scalar']['record']) != group['scalar_sha256']:
            raise ValueError('Frozen scalar source receipt mismatch')
        if canonical_hash(inp['scalar']['record']) != witness['scalar_sha256']:
            raise ValueError('Frozen witness scalar identity mismatch')
        if not verify_reconstruction:
            raise ValueError('This final replay requires actual Module2 reconstruction')
        out = evaluate(inp)
        if canonical_hash(out) != witness['module2_output_sha256']:
            raise ValueError('Frozen Module2 output hash mismatch: ' + witness['id'])
        for name in ('F','D','Ye','Ye2'):
            if canonical_hash(out[name]) != witness['yukawa_sha256'][name]:
                raise ValueError('Original Yukawa source identity changed: ' + witness['id'])
        if out['gates']['inverse'] != 'PASS' or out['gates']['observables'] != 'PASS':
            raise ValueError('Neutrino reconstruction failed: ' + witness['id'])
        Mnu = decode(out['Mnu'])
        target = decode(inp['target_eV'])
        closure = float(np.linalg.norm(Mnu-target)/np.linalg.norm(target))
        if not math.isfinite(closure) or closure >= 2e-9:
            raise ValueError('One-loop target closure failed: ' + witness['id'])
        largest_yukawa = max(float(np.max(np.abs(decode(out[name]))))
                             for name in ('F','D','Ye','Ye2'))
        perturbative = largest_yukawa < math.sqrt(4*math.pi)
        result = filters[ordering].evaluate(out['observables'])
        status = ('SCOPED_PASS' if result['status']=='SCOPED_PASS' and perturbative
                  else 'SCOPED_FAIL' if not perturbative or result['status']=='SCOPED_FAIL'
                  else 'SCOPED_UNKNOWN')
        rows.append({
            'witness_id':witness['id'], 'scalar':scalar, 'ordering':ordering,
            'source_input_sha256':canonical_hash(inp),
            'source_output_sha256':canonical_hash(out),
            'neutrino_mass_reconstruction_relative':closure,
            'one_loop_reconstruction':'PASS',
            'max_abs_Yukawa':largest_yukawa,
            'Yukawa_perturbativity_threshold':math.sqrt(4*math.pi),
            'Yukawa_perturbative':perturbative,
            'NuFIT61_scoped_status':status,
            'NuFIT61_details':result,
            'global_zee_acceptance':None,
        })
        print(status, witness['id'], '3D relative=',
              result['sections']['T23/DMA/DCP'].get('ordering_local_delta_chi2'),
              'reconstruction=', closure, flush=True)
    if len(seen) != 4 or {o for _,o in seen} != {'NO','IO'}:
        raise ValueError('Incomplete historical witness inventory')
    return {'status':'SCOPED_NEUTRINO_COMPLETED' if all(
                row['NuFIT61_scoped_status']=='SCOPED_PASS' for row in rows)
                else 'SCOPED_NEUTRINO_HAS_FAILURE_OR_UNKNOWN',
            'release':'NuFIT 6.1 (2025)', 'selection':selection,
            'frozen_D12_sha256':D12_SHA256,
            'source_authentication':'USER_UPLOADED_ARCHIVE_HASH_VERIFIED_UPSTREAM_UNVERIFIED',
            'one_loop_Zee_reconstruction_verified':True,
            'joint_six_dimensional_likelihood':False,
            'global_zee_acceptance':None,
            'cosmology': 'NOT_APPLIED_LIGHTEST_MASS_ASSUMED',
            'experimental_interpretation':
                'Intersection of six nominal 1D 3sigma screens and a separate 3D 99.73pct screen. Not a calibrated global 6D confidence region.',
            'results':rows}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive-dir',type=Path,required=True)
    p.add_argument('--selection',choices=('IC23','IC24'),default='IC24')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    report=run(a.archive_dir,a.selection)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(report['status'],'SAVED',a.output)


if __name__=='__main__':main()
