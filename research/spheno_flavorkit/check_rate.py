"""Reconstruct the SPheno observable from measured K2 and rate inputs."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT/'research/spheno_flavorkit/local'

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--comparison', type=Path, default=LOCAL/'d15_br_compare.json')
p.add_argument('--logs', type=Path, default=LOCAL/'d15_runs')
a = p.parse_args()
results=[]
for row in json.loads(a.comparison.read_text())['records']:
    lines = (a.logs/f"group{row['group']}.log").read_text().splitlines()
    alpha, gamma_mu = [float(x) for x in next(x for x in lines if 'D15_BR_INPUT ' in x).split()[1:]]
    sm = [float(x) for x in next(x for x in lines if 'D15_SM ' in x).split()[1:]]
    k = [complex(*row['coefficients_GeV_minus2'][ch]['K2']) for ch in 'LR']
    width = alpha * sm[2]**5 * sum(abs(x)**2 for x in k) / 4
    reconstructed = width/(gamma_mu+width)
    residual = abs(reconstructed/row['spheno_BR']-1)
    # Spectrum prints nine significant digits; half a last unit can be
    # nearly 5e-9 relative at the bottom of the decimal decade.
    if residual > 5e-9:
        raise ValueError(f'BR reconstruction failed for group {row["group"]}: {residual}')
    results.append({'group':row['group'], 'relative_rounding_residual':residual,
                    'alpha':alpha, 'GammaMu_GeV':gamma_mu, 'BR':reconstructed,
                    'daughter_phase_space_factor':(1-(sm[1]/sm[2])**2)**3})
print(json.dumps(results,indent=2))
