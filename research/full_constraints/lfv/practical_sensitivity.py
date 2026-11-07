"""Sensitivity to coherent missing amplitudes, from frozen fixed-card receipts.

No Zee amplitudes are calculated here. A missing amplitude with norm smaller
than the distance to the experimental-limit sphere cannot change the decision.
The converse does not establish that such a contribution exists.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
validation = json.loads((ROOT / 'research/full_constraints/LFV_VALIDATION.json').read_text())
cards = json.loads((ROOT / 'validation/module12/d12_benchmarks.json').read_text())['groups']
limits = json.loads((ROOT / 'research/full_constraints/lfv/experiments.json').read_text())['limits']
rows = []
for group, receipt in zip(cards, validation['original_D12_cards'], strict=True):
    witness = group['witnesses']['central']
    assert witness['id'] == receipt['id']
    results = {}
    for channel, partial in witness['radiative'].items():
        bound = limits[channel]['upper_limit']
        ratio = partial / bound
        results[channel] = dict(partial_BR=partial, observed_limit=bound,
            partial_over_limit=ratio, minimum_missing_norm_over_partial=abs(1-math.sqrt(1/ratio)),
            status='UNKNOWN', exclusion=None)
    partial = receipt['partial_dipole_only_mu3e_BR_DIAGNOSTIC']
    bound = limits['mu_to_3e']['upper_limit']
    results['mu_to_3e'] = dict(partial_BR=partial, observed_limit=bound,
        partial_over_limit=partial/bound,
        minimum_missing_norm_over_partial=abs(1-math.sqrt(bound/partial)),
        status='UNKNOWN', exclusion=None)
    rows.append(dict(id=witness['id'], witness_sha256=receipt['witness_sha256'],
                     mu_dipole_coefficients_GeV_minus2=receipt['partial_dipole_coefficients'],
                     results=results))
print(json.dumps(dict(description='Distances in coherent amplitude norm, not bounds on omitted physics; mu3e norm is phase-space integrated.', cards=rows, global_acceptance=None),indent=2))
