"""Measurement-driven diagnostics on the two saved cards, never physical BRs.

No likelihood, amplitudes, parameter proposals or production are executed.
Signed delta includes interference; plotted domains are sensitivity domains.
"""
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from module2.interface import decode
from research.full_constraints.higgs.sushi_bridge import benchmark

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def calculate():
    evidence_path = HERE / 'H125_SIGNAL_STRENGTH_EVIDENCE.json'
    evidence = json.loads(evidence_path.read_text())
    exp = evidence['experimental_category']
    dataset = Path(exp['file'])
    assert digest(dataset) == exp['dataset_sha256']
    data = json.loads(dataset.read_text())
    assert data['subMeasurements']['vbfH_bb']['process']['channels'] == [['vbfH', 'bb']]
    assert 'ref' not in data['subMeasurements']['vbfH_bb']
    execution = json.loads((HERE / 'h125_receipts/EXECUTION.json').read_text())
    for path, expected in execution['external_source_sha256'].items():
        if 'higgstools/src/signals/' in path:
            assert digest(path) == expected
    # Native SM reference replay, no HiggsSignals call.
    import Higgs.predictions as HP
    ref = HP.SMHiggsEW(125.)
    sigma = ref.cxn(HP.Collider.LHC13, HP.Production.vbfH)
    br = ref.br(HP.Decay.bb)
    rate_ref = sigma * br
    assert math.isclose(rate_ref, exp['native_SM_reference_sigma_BR_pb'], rel_tol=1e-13)
    low, obs, high = data['subMeasurements']['vbfH_bb']['obs']
    sm_sum = evidence['matched_SM_known_sum_GeV']
    transfer = evidence['matched_SM_ledger_GeV']['bb'] / sm_sum / br
    cases = []
    max_inverse_residual = 0.
    max_propagator_residual = 0.
    for row in evidence['cases']:
        record, witness = benchmark(row['name'])
        assert row['scalar_sha256'] == record['input_sha256']
        assert row['yukawa_sha256'] == witness['yukawa_sha256']
        widths = row['width']['partial_widths_GeV']
        known = row['width']['known_channel_sum_GeV']
        numerator_pb_GeV = sigma * row['production_ratios']['VBF'] * widths['bb']
        rate0 = numerator_pb_GeV / known
        # These are endpoint distances, not bounds on any missing physics.
        delta68 = [numerator_pb_GeV / high - known,
                   numerator_pb_GeV / low - known]
        z = 1.959963984540054
        surrogate95 = [obs-z*(obs-low), obs+z*(high-obs)]
        delta95 = [numerator_pb_GeV / surrogate95[1] - known,
                   numerator_pb_GeV / surrogate95[0] - known]
        ew_proxy = widths['WW'] + widths['ZZ']
        budget = min(-delta68[0], delta68[1])
        # Cauchy-Schwarz: B+2 sqrt(A B) <= budget. A is NOT yet a
        # certified inclusive SM four-fermion norm; this remains a target.
        norm_target = (math.sqrt(ew_proxy + budget)-math.sqrt(ew_proxy))**2
        # Independent root inversion by bisection, not the algebraic inverse.
        for target, analytic in ((high, delta68[0]), (low, delta68[1])):
            a, b = -.999*known, 100*known
            for _ in range(100):
                mid = (a+b)/2
                if numerator_pb_GeV/(known+mid) > target:
                    a = mid
                else:
                    b = mid
            residual = abs((a+b)/2-analytic)
            max_inverse_residual = max(max_inverse_residual, residual)
            assert residual < 1e-16
        propagators = {}
        for key, mass in row['scalar_thresholds_GeV'].items():
            endpoint = 1/(mass*mass-125**2)
            sampled = max(1/(mass*mass-q) for q in np.linspace(0,125**2,1001))
            max_propagator_residual = max(max_propagator_residual, abs(endpoint-sampled))
            assert endpoint == sampled
            propagators[key] = dict(max_abs_GeV_minus2=endpoint,
                                    max_relative_contact_remainder=125**2/(mass*mass-125**2))
        points = []
        # Bounded by the maximal removal of the retained EW proxy and the
        # measured lower endpoint. Neither endpoint is a physics prior.
        for delta in np.linspace(-ew_proxy, delta68[1], 121):
            rate = numerator_pb_GeV/(known+float(delta))
            points.append(dict(signed_delta_GeV=float(delta), conditional_rate_pb=rate,
                               conditional_mu_native=rate/rate_ref))
        cases.append(dict(name=row['name'], scalar_sha256=row['scalar_sha256'],
            yukawa_sha256=row['yukawa_sha256'], known_sum_GeV=known,
            conditional_zero_delta_rate_pb=rate0,
            conditional_zero_delta_mu_native=rate0/rate_ref,
            conditional_zero_delta_mu_ledger=row['signal_strength_numerators']['VBF_bb']*sm_sum/known,
            signed_delta_to_68_endpoints_GeV=delta68,
            signed_delta_to_95_gaussian_surrogate_GeV=delta95,
            multiplicative_rate_error_to_68_endpoints=[low/rate0-1,high/rate0-1],
            retained_WW_ZZ_proxy_GeV=ew_proxy,
            conditional_Cauchy_BSM_norm_target_GeV=norm_target,
            invisible_only_Y_frobenius_target=math.sqrt(16*math.pi*delta68[1]/125),
            native_yukawa_frobenius={key:float(np.linalg.norm(decode(witness['yukawas'][key]))) for key in ('F','D')},
            heavy_scalar_propagator_bounds=propagators,
            conditional_curve=points,
            missing_physics_bounds=dict(disjoint_additional_width_GeV=None,
                signed_interference_interval_GeV=None, loop_Majorana_width_GeV=None,
                theory_rate_uncertainty=None, acceptance_bias=None),
            reason='Higgs-inserted mixed scalar/current norm, finite-momentum Majorana form factor and uncertainty transfer are unqualified; targets are not achieved bounds',
            physical_mu=None, physical_rate_pb=None, exclusion=None))
    source_paths = {
        'ATLAS_2011.08280v2':'/tmp/h125-gate-atlas.html',
        'Bilenky_hep-ph_9310302v1':'/tmp/lfv-bilenky.pdf',
        'Herrero_1701.05345v2':'/tmp/h125-gate-zee.html',
        'Prophecy_1912.02010v1':'/tmp/h125-gate-prophecy.html',
        'LET_hep-ph_9505225v1':'/tmp/h125-gate-let.pdf',
        'Schmidt_2512.17235_published':'/tmp/h125-gate-matching.pdf',
        'HDECAY_1801.09506v1':'/tmp/h125-gate-hdecay.html',
    }
    return dict(status='H125_ABSOLUTE_MU_BLOCKED', cases=cases,
        experimental=dict(id=201108280, source=str(dataset), sha256=digest(dataset),
            observed_rate_endpoints_pb=[low,obs,high], native_SM_rate_pb=rate_ref,
            native_SM_VBF_pb=sigma,native_SM_BRbb=br,
            observed_mu_native=[x/rate_ref for x in (low,obs,high)],
            surrogate95_rate_endpoints_pb=surrogate95,
            surrogate95_is_official_confidence_interval=False),
        matched_SM_ledger_to_native_BR_factor=transfer,
        interpretation='All curves and inverse budgets conditional; no complete model rate, nuisance distribution or likelihood evaluation',
        source_sha256={str(evidence_path):digest(evidence_path),str(Path(__file__).resolve()):digest(__file__),
                       **{p:digest(p) for p in execution['external_source_sha256'] if 'higgstools/src/signals/' in p}},
        full_text_sources={key:dict(local_read_path=p,sha256=digest(p)) for key,p in source_paths.items()},
        independent_checks=dict(bisection_inverse_max_absolute_GeV=max_inverse_residual,
                                propagator_endpoint_max_absolute_GeV_minus2=max_propagator_residual),
        HiggsSignals_calls=0,global_acceptance=None,final_scan_authorized=False)


if __name__ == '__main__':
    result = calculate()
    (HERE/'H125_VBF_BB_MATERIALITY.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7,4.3))
    low,obs,high=result['experimental']['observed_mu_native']
    ax.axhspan(low,high,color='gray',alpha=.18,label='Pinned one-error endpoints')
    ax.axhline(obs,color='gray',linestyle=':')
    for row in result['cases']:
        pts=row['conditional_curve']
        ax.plot([p['signed_delta_GeV']*1000 for p in pts],[p['conditional_mu_native'] for p in pts],label=row['name'])
    ax.set(xlabel='Signed missing width shift ΔΓ [MeV]',ylabel='Conditional μ, native SMHiggsEW reference',
           title='ATLAS VBF bb sensitivity only — physical μ UNKNOWN')
    ax.legend();fig.tight_layout()
    fig.savefig(HERE/'H125_VBF_BB_CONDITIONAL.png',dpi=160)
    print(json.dumps(dict(status=result['status'],independent_checks=result['independent_checks'],HiggsSignals_calls=0)))
