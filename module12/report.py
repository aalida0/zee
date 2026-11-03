"""Finalize D12 evidence, execute local texture sensitivity, and plot results.

Run after module12.study and the optional scripts/zee_d12_superiso.py rebuild.
"""
import copy
import json
import platform
import scipy

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from module12.study import ROOT, LOCAL, OUTPUT, dump, proposals, evaluate_case, cascade_product
from module11.d11b_offline_fit import scalar_records, file_hash
from module2.interface import canonical_hash


def finalize():
    report = json.loads(OUTPUT.read_text())
    scalars, _ = scalar_records()
    backend = LOCAL/'superiso.json'
    if backend.exists():
        b = json.loads(backend.read_text())
        report['B_to_Xs_gamma'] = {k: v for k, v in b.items() if k not in ('controls', 'rows', 'source_sha256')}
        report['B_to_Xs_gamma'].update(
            distributed_fork_manifest_sha256=canonical_hash(b['source_sha256']),
            reconstruction_log_sha256=file_hash(str(backend.relative_to(ROOT))),
            controls={k: {s: r[s] for s in ('masses_GeV', 'tanbeta', 'BR_legacy_NLO')}
                      for k, r in b['controls'].items()},
            rows={k: {s: r[s] for s in ('masses_GeV', 'gamma', 'tanbeta', 'mu0_GeV', 'weights',
                                       'ordinary_parts', 'ordinary_total', 'BR_legacy_NLO',
                                       'command', 'stdout_sha256', 'scalar_sha256',
                                       'family_repeat_absolute_difference')}
                  for k, r in b['rows'].items()})
    report['experimental_reference'] = dict(
        accessed='2026-11-03', interpretation='Published measured upper limits/average, used only as diagnostic reference scales; no exclusion, likelihood or assigned theory uncertainty',
        mu_e_gamma=dict(upper_limit=1.5e-13, CL=.90,
                        primary='https://arxiv.org/abs/2504.15711v2',
                        version='MEG II 2021-2022 data; v2 30 July 2025; EPJC85 1177 and erratum EPJC85 1317',
                        current_review='https://pdg.lbl.gov/2026/listings/rpp2026-list-muon.pdf', page=5),
        mu_3e=dict(upper_limit=1e-12, CL=.90, experiment='SINDRUM Bellgardt et al., NPB299 (1988) 1',
                   current_review='https://pdg.lbl.gov/2026/listings/rpp2026-list-muon.pdf', page=5,
                   note='PDG2026 retains this measured bound. No Mu3e projected sensitivity used.'),
        B_Xs_gamma=dict(value=3.49e-4, error=0.19e-4,
                        source='https://pdg.lbl.gov/2026/tables/rpp2026-sum-mesons.pdf', page=132,
                        version='PDG2026 F. Takahashi et al., IJMPA41 2630011; PDF created 1 June 2026',
                        note='Measured inclusive radiative average; backend E_gamma>1.6 GeV, original legacy prescription; no combined experimental/theory pull'))
    report['limitations'] = [
        'Wgamma BLOCKED and excluded; Zgamma, WZ, other EW two-loop and non-dipole photon/Z penguins, boxes and interference missing.',
        'Scalar one-loop external-invariant/massless-neutrino approximation; exact one-loop UNKNOWN. Nominal unmatched Module4 mass/Yukawa card, including illustrative perturbative light-quark loops.',
        'Tree mu3e and tau3l subsets retain both contractions, exact final masses, propagators and identical-particle phase space; missing loops can interfere.',
        'Universality includes scalar F terms only, not D/mixed contributions; no precision-data test.',
        'Partial subset rates are neither lower nor upper bounds on full model rates; omitted amplitudes may interfere destructively.',
        'D10 proof covers only frozen reconstructed tree potentials, unchanged by Yukawa variations. Quantum vacuum and RG unknown; three other D10 representatives UNKNOWN.',
        'NuFIT6.1 secondary summary coordinates only; no joint likelihood, ordering preference, nuisance prior or cosmological mass filter.',
        'D4 analytic dictionary previously validated against native SARAH is applied here; no fresh D10 SARAH run. On-shell tree two-body BRs only; no off-shell or finite-width/NLO correction.',
        'No exact D10 production/PDF/cards; both collider energies and sigma times BR remain null. Hard Type-II production has no general lepton-Yukawa dependence.',
        'Bsgamma is source-verified legacy NLO QCD with original EM/power/normalization scheme; independent physical accuracy and 2026 global filter NOT_CERTIFIED.',
        'HiggsTools collider-search coverage incomplete; no mass exclusion, detector sensitivity or global model acceptance. Numerical tolerances are not theory uncertainties.']
    sensitivity_full = []
    for g in report['groups']:
        g['texture_sensitivity'] = []
        for name, spec, inp in proposals(scalars[g['scalar']], g['ordering']):
            if not name.startswith('texture_'):
                continue
            for factor in (.99, 1.01):
                varied = copy.deepcopy(inp)
                for part in ('real', 'imag'):
                    varied['homogeneous_coefficients'][part] = [factor*x for x in inp['homogeneous_coefficients'][part]]
                r = evaluate_case(varied)
                sensitivity_full.append(r)
                g['texture_sensitivity'].append(dict(base_design=name, coefficient_factor=factor,
                    metrics=r['metrics'], module2_output_sha256=r['module2_output_sha256'],
                    radiative=r['radiative'], mu_to_3e_tree=r['mu_to_3e_tree'],
                    cascade_product=cascade_product(r)))
        central = g['witnesses']['central']
        # Every nonleptonic channel is identical along the family. Store once.
        if 'nonleptonic_decay_channels' not in g:
            g['nonleptonic_decay_channels'] = {k: [r for r in central['decays'][k]['channels']
                                                  if not r['channel'].endswith('nu_all')] for k in ('H1', 'H2')}
        for role, row in g['witnesses'].items():
            for k in ('H1', 'H2'):
                row['decays'][k]['channels'] = [r for r in row['decays'][k]['channels'] if r['channel'].endswith('nu_all')]
            row.update(COMPLETE_LFV=False, global_zee_acceptance=None, mass_exclusion=None,
                       tree_vacuum='D10_GLOBAL_CERTIFIED', oscillation_target_tag=row['target']['label'],
                       **{'2026_GLOBAL_FLAVOR_FILTER_READY': False})
            row['sigma_times_BR_13p6_TeV_pb'] = None
            row['sigma_times_BR_14_TeV_pb'] = None
            if backend.exists():
                row['BR_B_Xs_gamma_legacy_NLO'] = report['B_to_Xs_gamma']['rows'][g['scalar']]['BR_legacy_NLO']
            g['witnesses'][role] = row
        family = g['family']
        g['summary'] = dict(
            BR_mu_e_gamma_range=[min(r['radiative']['mu_to_e_gamma'] for r in family), max(r['radiative']['mu_to_e_gamma'] for r in family)],
            BR_mu_3e_tree_range=[min(r['mu_to_3e_tree'] for r in family), max(r['mu_to_3e_tree'] for r in family)],
            cascade_product_range=[min(r['cascade_product'] for r in family), max(r['cascade_product'] for r in family)],
            BR_cascade_range=[min(r['BR_cascade'] for r in family), max(r['BR_cascade'] for r in family)],
            max_closure=max(r['metrics']['closure_relative'] for r in family),
            interpretation='Design extrema only, never bounds on full theory or distributions of viable models')
    dump(LOCAL/'sensitivity.json', sensitivity_full)
    report['evaluated_solution_count'] = sum(g['count']+len(g['texture_sensitivity']) for g in report['groups'])
    report['environment'] = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
                                 platform=platform.platform())
    report['sensitivity_log_sha256'] = file_hash(str((LOCAL/'sensitivity.json').relative_to(ROOT)))
    report['novelty_verdict'] = 'NOT_ESTABLISHED: flavor texture can retain the cascade, not a demonstrated unavoidable flavor-collider restriction; no paper headline yet'
    for p in [*sorted((ROOT/'module12').glob('*.py')), ROOT/'scripts/zee_d12_superiso.py']:
        report['source_sha256'][str(p.relative_to(ROOT))] = file_hash(str(p.relative_to(ROOT)))
    plot(report)
    dump(OUTPUT, report)
    audit(report)


def plot(report):
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.5), constrained_layout=True)
    for ax, g in zip(axes.flat, report['groups']):
        rows = g['family']
        x = [max(r['mu_to_3e_tree'], 1e-40) for r in rows]
        y = [r['radiative']['mu_to_e_gamma'] for r in rows]
        pts = ax.scatter(x, y, c=[r['cascade_product'] for r in rows], cmap='viridis', s=34)
        for role, marker in [('central', 's'), ('low_joint', '*'), ('high_joint', 'X')]:
            r = g['witnesses'][role]
            ax.scatter(max(r['mu_to_3e_tree'], 1e-40), r['radiative']['mu_to_e_gamma'],
                       facecolors='none', edgecolors='black', marker=marker, s=130, label=role)
        ax.axhline(1.5e-13, color='gray', ls='--', lw=.8)
        ax.axvline(1e-12, color='gray', ls='--', lw=.8)
        ax.set(xscale='log', yscale='log', xlabel=r'BR$_{tree}$(mu -> 3e); zeros clipped at $10^{-40}$',
               ylabel=r'BR$_{implemented}$(mu -> e gamma)',
               title=('D7' if g['scalar'].startswith('d7') else 'F13')+' / '+g['ordering'])
        fig.colorbar(pts, ax=ax, label='BR(H2 -> H1 Z) x BR(H1 -> tb)')
    axes.flat[0].legend(fontsize=7)
    fig.suptitle('D12: 112 closed perturbative designs; partial flavor rates, no exclusions')
    fig.savefig(ROOT/'module12/d12_family_correlation.png', dpi=160)
    plt.close(fig)


def sci(x):
    return f'{x:.4g}' if abs(x) >= 1e-45 else 'numerical zero'


def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(str, row))+' |' for row in rows])+'\n'


def audit(p):
    rows = []
    ranges = []
    trees = []
    leptons = []
    signed = []
    sensitivity = []
    for g in p['groups']:
        label = ('D7' if g['scalar'].startswith('d7') else 'F13')+' '+g['ordering']
        for role, r in g['witnesses'].items():
            d = r['decays']
            rows.append([label, role+' / '+r['design'], sci(r['radiative']['mu_to_e_gamma']),
                         sci(r['mu_to_3e_tree']), sci(r['radiative']['tau_to_mu_gamma']),
                         sci(r['radiative']['tau_to_e_gamma']),
                         f"{d['H2']['total']['branching_fraction']:.6f}",
                         f"{d['H1']['total']['branching_fractions']['t anti-b']:.6f}",
                         f"{r['cascade_product']:.6f}", sci(r['metrics']['closure_relative'])])
            leptons.append([label, role]+[', '.join(sci(d[k]['total']['branching_fractions'].get(l+' nu_all', 0.))
                                                  for l in ('e', 'mu', 'tau')) for k in ('H1', 'H2')])
            if role in ('central', 'low_joint'):
                s = r['signed_radiative']['mu_to_e_gamma']
                signed.append([label, role]+[sci(s['grouped_BR'][k]) for k in ('scalar_one_loop', 'fermion_photon_BZ', 'charged_scalar_photon_BZ')]+
                              [sci(sum(v['signed_BR'] for v in s['interference'])), sci(s['BR_implemented']), sci(s['coherence_ratio'])])
        r = g['witnesses']['low_joint']
        trees.append([label]+[sci(r['tree_observables'][k]['partial_BR']) for k in
                             ('tau_to_3e', 'tau_to_3mu', 'tau_to_mu_ee', 'tau_to_e_mumu')]+
                     [sci(r['universality'][k]) for k in ('delta_GF_mu_over_GF', 'g_tau_over_g_mu_squared_minus1')])
        s = g['summary']
        ranges.append([label, ' – '.join(sci(x) for x in s['BR_mu_e_gamma_range']),
                       ' – '.join(sci(x) for x in s['BR_mu_3e_tree_range']),
                       ' – '.join(sci(x) for x in s['cascade_product_range']), sci(s['max_closure'])])
        for base in ('texture_0.0001', 'texture_0.001', 'texture_0.01'):
            sub = [r for r in g['texture_sensitivity'] if r['base_design'] == base]
            sensitivity.append([label, base, ' – '.join(sci(v) for v in
                (min(r['radiative']['mu_to_e_gamma'] for r in sub), max(r['radiative']['mu_to_e_gamma'] for r in sub))),
                ' – '.join(sci(v) for v in (min(r['mu_to_3e_tree'] for r in sub), max(r['mu_to_3e_tree'] for r in sub)))])
    body = '''# D12 flavor–collider benchmark audit

Executed 2026-11-03 on `feature/zee-d12-flavor-collider-benchmarks`, descended
from real D11B `ad77620685a1dcf1f4ec1db612f2b3e1eacc8b31`.
**A large implemented LFV signal is not forced by the promising F13 cascade.**
The direct e–mu Yukawa entries can be suppressed inside a closed inverse family
with almost unchanged cascade BRs. Broad unrestricted homogeneous directions
instead raise LFV by many orders and can substantially dilute tb/cascade BRs.
These results establish a conditional flavor-texture effect, not global viability
or a new unavoidable flavor–collider correlation. **Novelty not established.**

## Exact spectra, neutrino inputs and bounded design

Only the two D10 representatives certified at their original full reconstructed
tree potentials are used. The other three D10 representatives retain UNKNOWN.
The historical NO in the D7 name does not restrict its neutrino ordering.

| Spectrum | mH1, mH2 / GeV | full scalar input canonical SHA256 |
| --- | --- | --- |
| D7 = d7_NO_neutral_near_heavy_07 | 298.7266553444879, 532.9329127809378 | ff0c551534e5051f223c00435293403e3b553f52e0cbec4344287da8b3dce862 |
| F13 = F13_heavy_0001330 | 572.2316243593124, 873.2076828282773 | 9117e7af53f9ad5c21f964a7c216de7af5824e903856fed54b9b237c922f4a1d |

The source-locked [JSON](../validation/module12/d12_benchmarks.json) stores four
explicit F,D,Ye,Ye2 witnesses per spectrum/ordering, exact Module2 input and
output hashes, scalar hashes, closure/round-trip residuals, all partial rates,
and the 112-design family table. Central references reproduce the *exact*
D11B input hashes and four Yukawa matrix hashes, checked against its stored
`reference_bestfit` witnesses. New solutions use the same frozen inverse API;
none of D11B's deliberately unstable trials is reused.

There are 28 specified designs per spectrum/ordering: seven F scales
(1e-7,1e-6,1e-5,1e-4,0.001,0.01,0.1), six homogeneous amplitudes
(1e-4,0.001,0.01,0.1,0.3,1) along the normalized complex D11B direction,
twelve seeded complex orientations/phases/charts with coefficient amplitudes
(0,1e-4,0.01,0.1), and three targeted textures at F=(1e-4,0.001,0.01).
Seed=121103 for NO, 121104 for IO, reset between spectra. All four Yukawa
matrices have max element <1; every solution passes the unchanged 2e-9 closure
tolerance. The design extrema are not parameter-space bounds or acceptance
fractions. Finalist reevaluations do not count as additional distinct solutions.

The central nuisance choice is m_lightest=0.01 eV, Majorana phases=(0.7,2.1)
rad. Diverse designs cross the nine D11B nuisance targets (m0=0.001,0.01,0.03;
phases=(0,0),(0.7,2.1),(2.3,0.4)). Oscillation coordinates are the pinned
NuFIT6.1 secondary best-fit-like summaries for each ordering, not a joint
likelihood or even a guaranteed joint minimizer. No ordering preference,
cosmological filter or statistical nuisance prior is imposed.

The optimization objective is the *discrete* minimum of
max[BR_implemented(mu e gamma)/(1.5e-13), BR_tree(mu3e)/(1e-12)] over the 28
designs. These denominators are measured reference scales, not a fit. The
targeted construction solves four real linear conditions D_e_mu=D_mu_e=0
in eight real native homogeneous coefficients, minimizing their Euclidean norm
with complex least squares and requiring norm<0.01. No inverse equation is
reimplemented. This aligns/cancels Yukawa entries, rather than claiming a
symmetry or an untuned generic point. An additional 24 actual ±1% coefficient
perturbations test local sensitivity: **136 distinct executed solutions total**.

## Paired same-input numerical witnesses

All BRs below are dimensionless. Gamma channels are the coherent implemented
subset, three-lepton channels neutral-tree subsets. `numerical zero` means
<1e-45 after imposing the texture, not a meaningful prediction of a full
branching ratio that small. The last column is a numerical closure residual.

'''
    body += table(['spectrum/order', 'role / source design', 'mu e gamma', 'mu3e tree', 'tau mu gamma', 'tau e gamma', 'BR H2→H1Z', 'BR H1→tb', 'BR product', 'closure'], rows)
    body += '\nDesign ranges (112 primary designs, not global bounds):\n\n'+table(['group', 'mu e gamma', 'mu3e tree', 'BR product', 'max closure'], ranges)
    body += '''
## Decay physics and competing channels

The frozen D4 `native_card → expected_coefficients → nonleptonic/leptons →
complete_total` functions recompute every width, retaining complex couplings,
both helicities, all nine quark pairs, exact unitary CKM and 27 inclusive or
exclusive channels per mother. The general analytic D4 dictionary was checked
against genuine SARAH at generic angles/complex matrices; this is its application
to new D10 inputs, **not a fresh SARAH export**. Source hashes and original native
evidence are checked before use. Every H+ total matches its conjugate; charge
widths are not added together. Same-parent daughters are closed, off-diagonal
photon and tree WZ/Wgamma vanish, and H2→H1A is CP forbidden in this potential.

Gamma(H2→H1Z) is **0.7286971594 GeV (D7)** and **5.8878233904 GeV (F13)**,
independent of leptonic family. At the central reference D7 has open competing
H2→tb=14.30696385 GeV, H1h=0.8783386822 GeV, Wh=0.0837444933 GeV;
WH and WA are closed. F13 has tb=1.1890131835 GeV,
WH=4.6754338447 GeV, H1h=0.3822671720 GeV, Wh=0.0009457117 GeV,
and the barely open WA=0.0015683317 GeV (threshold 872.63835 GeV).
Thus the 2021-style >70% cascade is **not** reproduced at either frozen
point: D7 is about 4.55%, F13 about 48.5%, once all open channels enter.
The scalar potential and its tree-vacuum proof are never deformed.

The complete frozen SM decay card is in JSON: kinematic mt=172.4, mb=4.78 GeV;
Yukawa reference masses run with one-loop piecewise QCD to each mother mass;
alpha_s(mZ)=0.1180. CKM uses exact unitary PDG2024 Wolfenstein construction.
Lepton masses, MW=80.379, MZ=91.1876, v=246.21965 match the frozen records.
These are specified LO inputs, not updated precision quark-mass predictions.
Off-shell channels, daughter finite widths and QCD/EW corrections remain absent;
the tiny WA width is especially threshold-sensitive.

Charged leptonic BRs below list (e nu, mu nu, tau nu), summed over three
massless tree neutrinos and both orthogonal helicities, for the same witnesses:

'''
    body += table(['group', 'role', 'H1 leptonic BRs (e,mu,tau)', 'H2 leptonic BRs (e,mu,tau)'], leptons)
    body += '''
## Signed LFV subset, interference and texture sensitivity

Module4 is called with the genuine Module2 output. It includes the frozen
Module3 scalar one-loop terms **once**, all coherently validated fermion/photon
and physical charged-scalar/photon Barr–Zee terms, both complex chiralities.
All Wgamma candidates are excluded. Zgamma, WZ and other missing EW pieces
are uncomputed. Exact one-loop accuracy remains UNKNOWN (external-invariant
expansion and massless neutrinos); two-loop mass/Yukawa inputs retain Module4's
explicit nominal unmatched card. Light-quark loops are illustrative perturbative
terms, not a hadronic precision calculation. No older approximate LFV assembly
is promoted to a full rate. Missing amplitudes can destructively interfere, so
these rates are **neither lower nor upper bounds** on the full theory.

Each JSON finalist retains every signed CL/CR component and isolated component
rate. The table groups amplitudes by topology *before* squaring. The signed
interference is between the three groups; within-group interference is already
included in their squared rates. Coherence ratio uses the sum of all individual
isolated diagram-row BRs in its denominator, not the grouped rates.

'''
    body += table(['group', 'role', 'one-loop BR', 'fermion BZ BR', 'charged BZ BR', 'signed cross BR', 'coherent BR', 'coherence ratio'], signed)
    body += '''
At fixed orientation, increasing F reduces the required particular D as 1/F.
This suppresses the approximately linear-in-D Barr–Zee transition until the
charged F†F term grows like F² in amplitude. Both chiralities prevent treating
that balance as a single real cancellation. Homogeneous coefficients can instead
increase unconstrained charged flavor couplings without raising neutrino masses.
The texture cancels the two *direct* e–mu entries. Residual tau-mediated
one-loop terms and F†F remain. This is an algebraically selected texture,
not evidence that all flavor observables vanish or that a protecting symmetry
exists. Very large homogeneous directions also involve large cancellations in
the neutrino forward mass; their actual closure is checked, not assumed.

Actual ±1% rescaling of all texture coefficients (holding F and target fixed):

'''
    body += table(['group', 'base texture', 'mu e gamma range (±1%)', 'mu3e tree range (±1%)'], sensitivity)
    body += '''
These are directional finite perturbations, not a full tuning measure in the
eight-dimensional coefficient space. The exact tree zero is texture-specific;
neighborhood results quantify how quickly it is lifted. The 0.001 textures
retain reduced muon subsets at these percent perturbations, while direct entries
at smaller F can be more sensitive. No radiative stability/RG claim is made.

All five Module3 tree channels are evaluated for the 16 finalists with
24/48-order phase-space quadrature and the unchanged 2e-5 relative-change check.
The amplitude has both ordered contractions with their Fermi minus sign; the
identical-particle 1/2 is in phase space after coherent squaring. Scalar
propagators and final lepton masses are retained. Photon/Z penguins, dipole
exchange and boxes could interfere. Selected low-joint witnesses give:

'''
    body += table(['group', 'tau3e tree', 'tau3mu tree', 'tau mu ee tree', 'tau e mumu tree', 'delta GF_mu/GF (F subset)', 'g_tau/g_mu squared minus 1 (F subset)'], trees)
    body += '''
Universality is only the frozen scalar F contribution (including the muon-GF
subtraction). D and mixed terms are missing. No universality or tau experimental
acceptance is assigned. Large partial widths/BRs in extreme examples are
diagnostic using fixed experimental lepton-width normalizations, not a
self-consistent global fit of lifetimes.

![Executed family correlation](d12_family_correlation.png)

The figure shows all 112 actual designs, with color equal to the recomputed
cascade × tb BR product. Dashed lines are published measured muon limits used
as diagnostic scales. They do not divide full-theory allowed/excluded regions.
Exact-texture tree zeros are clipped to 1e-40 for plotting only.

## Measured references, conditional B→Xs gamma and production

References verified online on **2026-11-03**:

- MEG II 2021–2022 data: measured BR(mu→e gamma)<1.5e-13 at 90% CL,
  [arXiv:2504.15711v2](https://arxiv.org/abs/2504.15711v2), revised 30 July 2025,
  EPJC85 (2025)1177 with erratum EPJC85 1317; retained in
  [PDG2026 muon listing](https://pdg.lbl.gov/2026/listings/rpp2026-list-muon.pdf),
  pp.5–6 (PDF created 1 June 2026). This is not the older 3.1e-13 combined result
  or the projected 6e-14 sensitivity.
- The same PDG2026 listing retains the measured SINDRUM Bellgardt et al.,
  NPB299 (1988)1 limit BR(mu→3e)<1e-12 at 90% CL. No projected Mu3e limit used.
- [PDG2026 meson summary p.132](https://pdg.lbl.gov/2026/tables/rpp2026-sum-mesons.pdf)
  gives measured inclusive b→s gamma=(3.49±0.19)e-4. Review: F. Takahashi et al.,
  IJMPA41 (2026)2630011; PDF created 1 June 2026. The stated error is the
  experimental average's uncertainty, not a theory error for this backend.

The official SuperIso v5.0 archive was downloaded afresh, with original SHA256
`7f8400e98ae80deac50af64486b980891e1630d729a0a4660ca309a4d7706b5f`.
Every distributed original source and every patched source byte is checked
against D9B's stored manifests; the exact tracked D9B patch is applied in
ignored D12 storage only. No previous audit or fork is overwritten. A newly
built client replays the SM, 550/900 one-state and coherent two-state D9B rates;
ordinary Q1–Q8 matching is checked. Each actual D10 charged mass is also checked
native versus independently injected one-state rate at its own tanbeta before
the two-state execution. C4/7/8 are ordinary NDR, no extra alpha_s multiplication,
weights=(cos²gamma,sin²gamma), a single coherent injection. Mu0=160 GeV,
running mt(mu0)=163.16587299291515 GeV; E_gamma>1.6 GeV and original mu_b/defaults.
NLO QCD matching/evolution/numerator retain legacy EM/power/semileptonic
prescriptions. Independent physical-rate accuracy is NOT_CERTIFIED; no NNLO or
certified 2026 global flavor likelihood is inferred.

'''
    b = p['B_to_Xs_gamma']
    if b['status'].startswith('EXECUTED'):
        body += table(['spectrum', 'tanbeta', 'BR legacy NLO', 'difference from measured central', 'relative difference', 'family repeat difference'],
                      [[k, sci(r['tanbeta']), sci(r['BR_legacy_NLO']), sci(r['BR_legacy_NLO']-3.49e-4),
                        f"{100*(r['BR_legacy_NLO']/3.49e-4-1):.3f}%", r['family_repeat_absolute_difference']]
                       for k, r in b['rows'].items()])
    body += '''
The positive differences identify conditional tension worth resolving, especially
for D7, without a sigma pull or mass cut: no source-matched theory uncertainty
was assigned. The original Type-II quark parameters/mixing fix these predictions;
NO/IO and leptonic homogeneous coefficients do not enter the backend command.
Repeated executions have zero rate difference and every same-scalar witness
links the identical rate. This factorization is not a new flavor correlation.

**13.6 TeV and 14 TeV production: NOT_EXECUTED; sigma and sigma×BR=null.**
The exact D10 MG5 runtime/UFO/generated process/PDF/card artifacts are absent
from this checkout, and no authenticated historical rate matches these complete
mass/mixing/tanbeta inputs. D5/D6's 700-GeV 5FS rates do not apply to 532.9 or
873.2 GeV; no F14 number or mass interpolation is substituted. The tabulated BR
products are ready to multiply an independently executed matching rate. No
detector efficiency, HL-LHC sensitivity or exclusion follows.

## Publishing outcome and limitations

[Florentino, Romão, Silva 2021](https://arxiv.org/abs/2106.08332) already studied
the H2→H1Z→tbZ cascade and tbH production; their Sec.7.7 reports BR>70% examples.
Here the exact tree-vacuum-certified D10 points instead give 4.55%/48.5%, with
explicit competing H1h/tb/WH channels. We add actual NO/IO inverse-family
flavor subsets and demonstrate how direct e–mu textures preserve those BRs.
This is a quantitative benchmark difference, not a new cascade mechanism.

[Herrero-García et al. 2017 v2](https://arxiv.org/abs/1701.05345v2) already scans
general Zee neutrino and LFV correlations, including radiative/trilepton modes.
Its Sec.3.3 and Sec.4 have particular approximations, textures, naturality choices
and fit data. Our IO targets have sin²theta23=0.5499, versus NO=0.4701, and
both close here; that algebraic observation with *partial* flavor cannot refute
their constrained fit or ordering conclusions. We have not reproduced their
same-input full rates or parameter restrictions. No comparable likelihood or
quantified literature-wide novelty claim is made.

The original central references show diagnostic muon-dipole tension even when
their cascade product is large. Suppressing the direct e–mu texture removes that
particular tension in the implemented subset with negligible cascade dilution.
Quantitatively, central→low-joint reduces BR_implemented(mu e gamma) by
8.95/8.47 orders for D7 NO/IO and 7.65/7.49 orders for F13 NO/IO. The paired
BR products change by only +0.00408%/+0.00558% and
−0.0000131%/−0.0000141%, respectively. Percent coefficient perturbations at
F=0.001 give muon dipole subsets of 1.37–1.41e-14/3.20–3.26e-14 (D7 NO/IO)
and 1.73–1.84e-16/4.08–4.24e-16 (F13 NO/IO), with tree mu3e below 3.4e-27.
Large F/homogeneous couplings can dilute the cascade product, but the low-LFV
textures keep an almost unchanged product: these two fixed spectra do **not**
establish an unavoidable loss of the collider signal from flavor. Nor is the
hard-production independence of lepton Yukawas a novel correlation.

A modest EPJC paper would require completing the missing LFV amplitudes and
non-dipole interference (especially Wgamma), matched independent flavor-rate
validation and theory uncertainties, exact D10 production with matched PDF and
scheme/scale variations, and a direct same-input comparison to the 2017/2021
analyses. A robust flavor-imposed change of the collider population or a new
testable hierarchy must then be demonstrated; a flat hard rate and selected
textures alone do not establish it. Detector work would be needed for reach.
HiggsTools/search coverage, quantum vacuum and RG remain unresolved.

`COMPLETE_LFV=false`, `2026_GLOBAL_FLAVOR_FILTER_READY=false`,
`global_zee_acceptance=null`, `mass_exclusion=null` everywhere. D10 is a
tree-level statement only. Numerical tolerances are not theoretical errors.

## Reproduction and checks

```bash
python3 -m module12.study
curl -fLsS https://superiso.in2p3.fr/download/superiso_v5.0.tgz -o /tmp/d12-superiso_v5.0.tgz
python3 scripts/zee_d12_superiso.py --archive /tmp/d12-superiso_v5.0.tgz
python3 -m module12.report
python3 -m unittest discover -s tests -p 'test_module12_*.py' -v
git diff --check
```

Detailed trial, sensitivity, reconstructed source/build and backend output logs
remain ignored under `validation/module12/local/`. The compact evidence retains
their hashes, source manifests and reproducible input recipes. Only Modules12,
its script/tests/evidence and the local-output ignore rule are new; Modules0–11
and their audits remain unchanged. Executed test outcome is recorded separately
in the completion log after checks.
'''
    (ROOT/'module12/D12_FLAVOR_COLLIDER_AUDIT.md').write_text(body)


if __name__ == '__main__':
    finalize()
