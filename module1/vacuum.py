"""Reproducible tree neutral/charge-breaking searches; never a global proof."""
import math
import numpy as np
from scipy.optimize import minimize, root
from .potential import Potential, component_value, gauge_audit

CHARTS = {'H1_neutral_H2charged_real': [2, 4, 6, 7, 8, 9],
          'H2_neutral_H1charged_real': [0, 2, 3, 6, 8, 9],
          'neutral_complex': [2, 6, 7]}


def search_vacuum(p, x, starts=64, seeds=(123, 104852)):
    v = x['v']; pot = Potential(p)
    ew = np.zeros(10); ew[[2, 6]] = v*np.array([math.cos(x['beta']), math.sin(x['beta'])])
    vew = component_value(ew, p)/v**4
    rows = []; best = None; witness = None
    for seed in seeds:
        rng = np.random.default_rng(seed)
        for chart, indices in CHARTS.items():
            ix = np.array(indices)

            def embed(t):
                r = np.zeros(10); r[ix] = t*v
                return r

            def fun(t):
                val, g = pot.evaluate(embed(t), hessian=False)
                return val/v**4, g[ix]/v**3

            def hess(t):
                return pot.evaluate(embed(t))[2][np.ix_(ix, ix)]/v**2

            count = starts if len(ix) == 6 else max(8, starts//4)
            choices = [ew[ix]/v, np.zeros(len(ix))]
            # Vary scales and phases; alternative gauge charts also cover
            # singular H1=0/H2=0 strata. Bounds limit the search, not physics.
            choices += [rng.normal(size=len(ix))*((.3, 1., 3., 6.)[k % 4]) for k in range(count)]
            valid = 0; boundaries = 0; failures = 0
            for initial in choices:
                result = minimize(fun, np.clip(initial, -12, 12), jac=True,
                                  method='L-BFGS-B', bounds=[(-12, 12)]*len(ix),
                                  options={'maxiter': 1200, 'ftol': 1e-14, 'gtol': 1e-10, 'maxls': 40})
                t = result.x
                boundary = bool(np.max(abs(t)) >= 12-1e-5)
                if boundary:
                    boundaries += 1
                else:
                    # Polish stationarity, then independently reject saddles
                    # in the FULL ten-field Hessian (not the gauge slice).
                    refined = root(lambda z: fun(z)[1], t, jac=hess, tol=1e-10)
                    if np.isfinite(refined.x).all() and np.max(abs(refined.x-t)) < .1:
                        t = refined.x
                r = embed(t)
                val, grad, h = pot.evaluate(r)
                direct = component_value(r, p)/v**4
                residual = abs(val/v**4-direct)/max(1., abs(direct))
                gn = float(np.max(abs(grad))/v**3)
                mineig = float(np.linalg.eigvalsh(h).min()/v**2)
                rank, transverse, ward = gauge_audit(r, h)
                credible = (np.isfinite(direct) and not boundary and gn < 2e-7
                            and mineig >= -2e-7 and transverse/v**2 > 2e-7
                            and ward/v**2 < 2e-6 and residual < 2e-10)
                if not credible:
                    failures += 1
                    continue
                valid += 1
                z = (r[::2]+1j*r[1::2])/np.sqrt(2)
                gramdet = max(0., np.vdot(z[:2], z[:2]).real*np.vdot(z[2:4], z[2:4]).real
                              -abs(np.vdot(z[:2], z[2:4]))**2)/v**4
                charged = abs(z[4])/v > 1e-5 or gramdet > 1e-10
                record = {'fields_GeV': r.tolist(), 'value_over_v4': direct,
                          'delta_over_v4': direct-vew, 'gradient_over_v3': gn,
                          'min_full_hessian_over_v2': mineig, 'potential_relative_residual': residual,
                          'broken_gauge_rank': rank, 'min_transverse_hessian_over_v2': transverse/v**2,
                          'gauge_ward_residual_over_v2': ward/v**2,
                          'kind': 'CHARGE_BREAKING' if charged else 'NEUTRAL',
                          'chart': chart, 'seed': seed}
                if best is None or direct < best['value_over_v4']:
                    best = record
                if direct-vew < -1e-6 and (witness is None or direct < witness['value_over_v4']):
                    witness = record
            rows.append({'seed': seed, 'chart': chart, 'attempts': len(choices),
                         'credible_stationary_minima': valid, 'rejected_or_nonconverged': failures,
                         'boundary_hits': boundaries})
    return {'status': 'VACUUM_DEEPER_WITNESS' if witness else 'VACUUM_NO_DEEPER_WITNESS_FOUND',
            'assessment': 'FAIL' if witness else 'UNKNOWN', 'order': 'tree',
            'global_stability_proven': False, 'neutral_value_over_v4': vew,
            'field_bound_in_units_v': 12, 'runs': rows, 'lowest_credible_minimum': best,
            'deeper_witness': witness, 'all_attempts_converged': all(r['rejected_or_nonconverged'] == 0 for r in rows)}
