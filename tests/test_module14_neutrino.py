import json
from pathlib import Path

from module14.scan import digest, evaluate_family, neutrino_input, scalar_status


def row():
    scalar = json.loads(Path('module1/example.json').read_text())
    return {'id': 91, 'scalar': scalar, 'scalar_sha256': digest(scalar)}


def test_family_seed_and_inputs_are_deterministic_and_distinct():
    r = row()
    first = neutrino_input(r, 123, 'NO', 0)
    assert first == neutrino_input(r, 123, 'NO', 0)
    variants = [neutrino_input(r, 123, o, i)[0] for o in ('NO', 'IO') for i in range(2)]
    assert len(set(variants)) == 4
    other = dict(r, id=92)
    assert neutrino_input(other, 123, 'NO', 0)[0] != first[0]


def test_inverse_closure_and_perturbativity():
    for ordering in ('NO', 'IO'):
        result = evaluate_family(row(), 123, ordering, 0, 1000)
        assert result['status'] == 'PASS'
        assert result['relative_residual'] < 2e-9
        assert set(result['max_abs_yukawas']) == {'F', 'D', 'Ye', 'Ye2'}
        assert result['input_sha256'] == digest(result['input'])


def test_scalar_status_and_numerical_error_are_distinct():
    gates = {k: {'assessment': 'PASS'} for k in ('reconstruction', 'bfb', 'unitarity', 'ewpo', 'vacuum')}
    assert scalar_status(gates) == 'PASS'
    gates['vacuum']['assessment'] = 'UNKNOWN'
    assert scalar_status(gates) == 'UNKNOWN'
    gates['bfb']['assessment'] = 'FAIL'
    assert scalar_status(gates) == 'FAIL'
    gates['ewpo']['assessment'] = 'ERROR'
    assert scalar_status(gates) == 'ERROR'
