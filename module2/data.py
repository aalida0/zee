"""Explicit source-versioned Gaussian comparison; no acceptance classifier."""
import numpy as np
from .core import real_number

OBS_UNITS = {'sin2_theta12': '1', 'sin2_theta13': '1', 'sin2_theta23': '1',
             'dm21_eV2': 'eV^2', 'dm3l_eV2': 'eV^2', 'delta_rad': 'rad'}


def compare(obs, dataset):
    if dataset is None:
        return {'status': 'NOT_EVALUATED', 'reason': 'No oscillation dataset selected'}
    if not isinstance(dataset, dict) or set(dataset) != {'schema_version', 'dataset_id', 'source', 'ordering', 'observables', 'units', 'mean', 'covariance', 'likelihood', 'assumptions'}:
        raise ValueError('Invalid dataset fields')
    if dataset['schema_version'] != '1.0.0' or dataset['likelihood'] != 'GAUSSIAN_APPROXIMATION':
        raise ValueError('Only explicitly labeled Gaussian approximation is supported')
    if dataset['ordering'] != obs['ordering']:
        raise ValueError('Dataset ordering mismatch')
    if not isinstance(dataset['source'], dict) or set(dataset['source']) != {'version', 'url', 'selection'} or any(not isinstance(x, str) or not x.strip() for x in dataset['source'].values()):
        raise ValueError('Dataset source/version/selection required')
    if not isinstance(dataset['dataset_id'], str) or not dataset['dataset_id'].strip() or not isinstance(dataset['assumptions'], list) or not dataset['assumptions'] or any(not isinstance(x, str) or not x.strip() for x in dataset['assumptions']):
        raise ValueError('Dataset identity and assumptions required')
    names = dataset['observables']
    if not isinstance(names, list) or not names or any(x not in OBS_UNITS for x in names) or len(names) != len(set(names)):
        raise ValueError('Invalid or duplicate dataset observables')
    if dataset['units'] != {x: OBS_UNITS[x] for x in names}:
        raise ValueError('Dataset units mismatch')
    mean = np.array([real_number(x) for x in dataset['mean']])
    cov = np.array([[real_number(x) for x in row] for row in dataset['covariance']])
    n = len(names)
    if mean.shape != (n,) or cov.shape != (n, n) or not np.allclose(cov, cov.T, atol=0, rtol=1e-13):
        raise ValueError('Invalid mean/covariance dimensions or symmetry')
    if any((name.startswith('sin2') and not 0 <= value <= 1) or (name == 'dm21_eV2' and value <= 0) or (name == 'dm3l_eV2' and value*(1 if dataset['ordering'] == 'NO' else -1) <= 0) for name, value in zip(names, mean)):
        raise ValueError('Dataset mean outside physical convention')
    try:
        L = np.linalg.cholesky(cov)
    except np.linalg.LinAlgError as exc:
        raise ValueError('Covariance must be positive definite') from exc
    if any(obs.get(x) is None for x in names):
        return {'status': 'UNKNOWN', 'dataset_id': dataset['dataset_id'], 'reason': 'Requested observable undefined'}
    d = np.array([obs[x] for x in names])-mean
    if 'delta_rad' in names:
        i = names.index('delta_rad')
        d[i] = (d[i]+np.pi) % (2*np.pi)-np.pi
    z = np.linalg.solve(L, d)
    return {'status': 'PASS', 'meaning': 'Comparison computed; no experimental acceptance assigned',
            'likelihood': 'GAUSSIAN_APPROXIMATION', 'dataset_id': dataset['dataset_id'],
            'source': dataset['source'], 'chi2': float(z@z), 'dimensions': n,
            'residual': d.tolist(), 'assumptions': dataset['assumptions'],
            'official_multidimensional_likelihood': False, 'experimental_acceptance': None}
