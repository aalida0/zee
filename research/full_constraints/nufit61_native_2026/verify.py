"""Verify real NuFIT 6.1 .xz tables and optionally the existing module2 backend.

From the repository root:
 python -m research.full_constraints.nufit61_native_2026.verify --archive-dir /path/to/archives
Add --backend for real Module2 tests, and --full-3d for memory-intensive 3D parsing.
No experimental acceptance or joint six-dimensional likelihood is constructed.
"""
import argparse
import hashlib
import json
import lzma
import math
from pathlib import Path
import numpy as np

# These hashes bind the four user-provided archives, not independently verified upstream hashes.
FILES = {
    'v61.release-TBoff-NO.txt.xz': ('NO', 'IC23 without SK atmospheric data',
        '58b113927c13f55925558e1ef0a598b357a237cde5c466b9f660cc08569970f6', 0.0),
    'v61.release-TBoff-IO.txt.xz': ('IO', 'IC23 without SK atmospheric data',
        '6e14ce52503d053ce4d8d0171ffecae24c2dd3dc41be99c3c5c952f321331f16', 1.485872),
    'v61.release-TByes-NO.txt.xz': ('NO', 'IC24 with SK atmospheric data',
        'c74bd6df84297a8429cd3b9e1239751cd0762756f1ec0c2a31248d78570b26e4', 0.0),
    'v61.release-TByes-IO.txt.xz': ('IO', 'IC24 with SK atmospheric data',
        'd92fbd1886a85738080a394a6af513ec1ac49d5e474a6517cada0c2c6f3b96b2', 5.908214),
}
SECTIONS = ('T23/DMA/DCP','T13/T12','T13/DMS','T12/DMS','T13/T23','T13/DMA',
            'T23/DMA','T13/DCP','T23/DCP','DMA/DCP','T12/T23','T12/DCP',
            'T12/DMA','DMS/T23','DMS/DCP','DMS/DMA','T13','T12','T23',
            'DCP','DMS','DMA')


def verify_archive(path, sha, minimum):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == sha, f'{path}: SHA256 mismatch'
    results = {}
    active, lines = None, []

    def finish():
        if active is None:
            return
        ndim = active.count('/')+1
        values = np.fromstring(''.join(lines), sep=' ')
        assert values.size and values.size % (ndim+1) == 0, f'{path}: {active}: invalid columns'
        data = values.reshape((-1, ndim+1))
        assert np.isfinite(data).all(), f'{path}: {active}: nonfinite values'
        axes = [np.unique(data[:, i]) for i in range(ndim)]
        shape = tuple(map(len, axes))
        assert math.prod(shape) == len(data), f'{path}: {active}: incomplete Cartesian grid'
        flat = np.ravel_multi_index(
            [np.searchsorted(axis, data[:, i]) for i, axis in enumerate(axes)], shape)
        assert len(np.unique(flat)) == len(data), f'{path}: {active}: duplicate grid nodes'
        assert np.isclose(data[:, -1].min(), minimum, atol=1e-8, rtol=0), f'{path}: {active}: ordering offset lost'
        point = data[np.argmin(data[:, -1])]
        results[active] = {'rows':len(data), 'shape':list(shape), 'min':float(point[-1]),
                           'coordinates':point[:-1].tolist()}
        if active == 'DCP':
            assert np.isclose(data[0, -1], data[-1, -1], atol=1e-8, rtol=0), f'{path}: nonperiodic endpoint'

    with lzma.open(path, 'rt') as handle:
        for line in handle:
            if line.startswith('# '):
                finish()
                active, lines = line[2:].split()[0], []
                assert active in SECTIONS and active not in results, f'{path}: unknown or repeated section {active}'
            elif active is not None and line.strip() and not line.startswith('#'):
                lines.append(line)
        finish()
    assert tuple(results) == SECTIONS, f'{path}: unexpected projection sequence'
    assert sum(x['rows'] for x in results.values()) == 1450245, f'{path}: row count'
    assert results['T23/DMA/DCP']['shape'] == [101, 165, 73], f'{path}: 3D shape'
    return results


def test_backend(path, ordering, selection, sha, data, full_3d):
    from module2.nufit import read_projection, interpolate
    from module2.data import compare
    names = ('T12','T13','T23','DMS','DMA','DCP','T13/T12','T23/DCP')
    if full_3d:
        names += ('T23/DMA/DCP',)
    mapping = {'T12':'sin2_theta12','T13':'sin2_theta13','T23':'sin2_theta23',
               'DMS':'dm21_eV2','DMA':'dm3l_eV2','DCP':'delta_rad'}
    for name in names:
        axes, grid = read_projection(path, sha, name)
        record = data[name]
        assert list(grid.shape) == record['shape']
        assert abs(float(grid.min()) - record['min']) < 1e-8
        assert abs(interpolate(axes, grid, record['coordinates']) - record['min']) < 1e-7
        obs = {'ordering':ordering}
        for token, value in zip(name.split('/'), record['coordinates']):
            obs[mapping[token]] = (10**value if token=='DMS' else
                                   value*1e-3 if token=='DMA' else
                                   math.radians(value) if token=='DCP' else value)
        dataset = {'schema_version':'1.0.0', 'dataset_id':'NuFIT61_REAL_'+name.replace('/','_'),
            'source':{'version':'NuFIT 6.1 (2025)',
                      'url':'https://www.nu-fit.org/?q=node%2F309', 'selection':selection},
            'ordering':ordering, 'likelihood':'PROFILED_DELTA_CHI2',
            'archive':{'path':str(path.resolve()),'sha256':sha}, 'section':name,
            'assumptions':['Single profiled projection; not a six-parameter joint fit.']}
        value = compare(obs, dataset)
        assert value['status'] == 'PASS' and value['experimental_acceptance'] is None
        assert abs(value['delta_chi2']-record['min']) < 1e-7
        if 'DCP' in name:
            obs['delta_rad'] += 2*math.pi
            shifted = compare(obs, dataset)
            assert shifted['status'] == 'PASS'
            assert abs(shifted['delta_chi2']-record['min']) < 1e-7
    return list(names)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive-dir',type=Path,required=True)
    p.add_argument('--backend',action='store_true',help='also test production module2')
    p.add_argument('--full-3d',action='store_true',help='test million-row Module2 parsing, memory intensive')
    p.add_argument('--output',type=Path)
    args = p.parse_args()
    reports = []
    for filename, (ordering, selection, sha, minimum) in FILES.items():
        path = args.archive_dir/filename
        checked = verify_archive(path, sha, minimum)
        backend = test_backend(path, ordering, selection, sha, checked, args.full_3d) if args.backend else []
        reports.append({'filename':filename,'ordering':ordering,'selection':selection,
            'sha256':sha,'offset':minimum,'sections_verified':len(checked),
            'numeric_rows':sum(x['rows'] for x in checked.values()),
            'backend_sections_verified':backend,
            'best_3d_coordinates':checked['T23/DMA/DCP']['coordinates']})
        print('PASS', filename, '22 projections; offset', minimum,
              'Module2 sections', len(backend), flush=True)
    report = {'status':'PASS','release':'NuFIT 6.1 (2025)','archives':reports,
        'source_authentication':'USER_UPLOADED_HASH_VERIFIED_OFFICIAL_UPSTREAM_HASH_UNVERIFIED',
        'joint_likelihood':False,'global_zee_acceptance':None}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
