"""Profile the four *frozen* D7/F13 neutrino targets against authentic NuFIT 6.1.

This neither changes benchmark Yukawas nor constructs a six-dimensional
likelihood. The two profiled projections are reported separately (never added).

From repo root:
 python3 -m research.full_constraints.nufit61_native_2026.saved_targets \
   --archive-dir NuFIT --output /tmp/nufit61_D7_F13_targets.json
"""
import argparse
import hashlib
import json
from pathlib import Path

from module2.data import compare
from module2.interface import decode
from module2.observables import observables
from module11.d11b_offline_fit import load_source
from .verify import FILES

ROOT = Path(__file__).resolve().parents[3]
D12 = ROOT / 'validation/module12/d12_benchmarks.json'
D12_SHA256 = 'f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8'
SECTIONS = ('T23/DMA/DCP', 'T13/T12')


def dataset(path, ordering, selection, sha256, section):
    return {
        'schema_version': '1.0.0',
        'dataset_id': 'NuFIT61_native_' + ('IC24' if 'IC24' in selection else 'IC23')
            + '_' + ordering + '_' + section.replace('/', '_'),
        'source': {
            'version': 'NuFIT 6.1 (2025)',
            'url': 'https://www.nu-fit.org/?q=node%2F309',
            'selection': selection,
        },
        'ordering': ordering, 'likelihood': 'PROFILED_DELTA_CHI2',
        'archive': {'path': str(path.resolve()), 'sha256': sha256},
        'section': section,
        'assumptions': [
            'Single published profiled section; not a joint likelihood.',
            'The original frozen D11B/D12 neutrino target is not refitted.',
            'The D11B target was built from secondary NuFIT 6.1 IC24 summary values.',
        ],
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--archive-dir', type=Path, required=True)
    cli.add_argument('--output', type=Path, required=True)
    cli.add_argument('--include-ic23', action='store_true',
                     help='also produce a separate IC23 robustness comparison')
    a = cli.parse_args()

    actual_hash = hashlib.sha256(D12.read_bytes()).hexdigest()
    if actual_hash != D12_SHA256:
        raise ValueError('Frozen D12 benchmark hash differs from pinned receipt')
    source = load_source()  # pinned secondary-best-fit summary
    data = json.loads(D12.read_text())
    if len(data['groups']) != 4:
        raise ValueError('Expected exactly four D12 groups')
    used = set()
    rows = []
    for group in data['groups']:
        ordering = group['ordering']
        witness = group['witnesses']['low_joint']
        target = witness['module2_input']['target_eV']
        obs = observables(decode(target), ordering)
        if obs['mixing_status'] != 'PASS':
            raise ValueError('Undefined frozen neutrino-target PMNS observables')

        # Independent target check against the source pinned by D11B: if the
        # stored Yukawa family is changed, this comparison is not a replay.
        expected = source['oscillation_parameters'][ordering]
        for key, old_key in (('sin2_theta12','sin2theta12'),
                             ('sin2_theta13','sin2theta13'),
                             ('sin2_theta23','sin2theta23'),
                             ('dm21_eV2','dm21_eV2'),
                             ('dm3l_eV2','dm3ell_eV2')):
            if abs(obs[key] - expected[old_key]['bestfit']) > 2e-10:
                raise ValueError(f'{witness["id"]}: frozen target mismatch on {key}')
        key = (group['scalar'], ordering)
        if key in used:
            raise ValueError('Duplicate benchmark/ordering')
        used.add(key)

        comparisons = {}
        for filename, (file_ordering, selection, sha256, _) in FILES.items():
            if file_ordering != ordering:
                continue
            if not a.include_ic23 and 'IC23' in selection:
                continue
            path = a.archive_dir / filename
            # Each compare() independently checks the original .xz SHA256.
            projections = {}
            for section in SECTIONS:
                result = compare(obs, dataset(path, ordering, selection, sha256, section))
                if result['status'] != 'PASS' or result['experimental_acceptance'] is not None:
                    raise ValueError(f'Invalid projection comparison {filename}, {section}: {result}')
                projections[section] = result['delta_chi2']
            comparisons[selection] = projections

        rows.append({'benchmark_id':group['scalar'], 'witness_id':witness['id'],
                     'ordering':ordering, 'observables':{
                         k:obs[k] for k in ('sin2_theta12','sin2_theta13',
                              'sin2_theta23','dm21_eV2','dm3l_eV2','delta_rad')},
                     'projections':comparisons,
                     'physical_acceptance':None})
        print('PASS', witness['id'], comparisons, flush=True)

    result = {
        'status':'PASS_SCOPED_NEUTRINO_PROJECTION_CHECK',
        'source':'NuFIT 6.1 genuine user-supplied archives, upstream hashes unverified',
        'frozen_D12_sha256':D12_SHA256,
        'number_of_frozen_witnesses':len(rows),
        'profiles_independently_reported':list(SECTIONS),
        'joint_likelihood':False, 'global_zee_acceptance':None,
        'benchmarks_changed':False, 'results':rows,
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print('SAVED', str(a.output))


if __name__ == '__main__':
    main()
