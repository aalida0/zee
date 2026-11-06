"""Frozen family identity and mock-only numerical-error regression."""
import json
from unittest.mock import patch
from module14.scan import digest, evaluate_family, scalar_status
from module14.fixtures.replay import saved


def family():
    rows = [json.loads(s) for s in saved()['pilot_output.jsonl'].splitlines()]
    return next(r for r in rows if r['id'] == 50)['neutrino'][0]


def test_frozen_family_seed_inputs_and_closure():
    config = json.loads(saved()['pilot_config.json'])
    outputs = [json.loads(s) for s in saved()['pilot_output.jsonl'].splitlines()]
    for row in outputs:
        ns = row['neutrino']
        if not isinstance(ns, list): continue
        assert len({n['seed_sha256'] for n in ns}) == 4
        for n in ns:
            assert n['seed_sha256'] == digest(['d14-neutrino-v1', config['seed'], row['id'], n['ordering'], n['family']])
            assert n['input_sha256'] == digest(n['input'])
            assert n['relative_residual'] < 2e-9


def test_worker_family_numerical_error_retains_identity():
    n = family()
    r = {'id':50, 'scalar':n['input']['scalar']['record']}
    with patch('module14.scan.neutrino_input', return_value=(n['seed_sha256'], n['target_spec'], n['input'])), \
         patch('module14.scan.neutrino_evaluate', side_effect=RuntimeError('mock interruption')):
        result = evaluate_family(r, 0, 'NO', 0, n['perturbativity_limit'])
    assert result['status'] == 'ERROR'
    assert result['input_sha256'] == n['input_sha256']


def test_family_input_construction_error_is_auditable():
    n = family();r={'id':50,'scalar_sha256':n['input']['scalar']['sha256']}
    with patch('module14.scan.neutrino_input',side_effect=ValueError('mock singular input')):
        result=evaluate_family(r,20261103,'NO',0,n['perturbativity_limit'])
    assert result['status']=='ERROR' and result['error_phase']=='input_construction'
    assert result['input'] is None and result['input_sha256'] is None
    assert result['scalar_sha256']==r['scalar_sha256']


def test_scalar_status_and_numerical_error_are_distinct():
    gates = {k: {'assessment': 'PASS'} for k in ('reconstruction', 'bfb', 'unitarity', 'ewpo', 'vacuum')}
    assert scalar_status(gates) == 'PASS'
    gates['vacuum']['assessment'] = 'UNKNOWN'
    assert scalar_status(gates) == 'UNKNOWN'
    gates['bfb']['assessment'] = 'FAIL'
    assert scalar_status(gates) == 'FAIL'
    gates['ewpo']['assessment'] = 'ERROR'
    assert scalar_status(gates) == 'ERROR'
