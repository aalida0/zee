"""Static scientific plots from validated D14D exports; no new integrations."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from module14.scan import file_sha
from .production_map_run import save

NOTE = ('Conditional LO 5FS; tree two-body decays. Physical B→Xsγ UNKNOWN; LFV partial; HiggsTools incomplete.\n'
        'Scale/PDF/decay theory errors unmeasured; no global acceptance or detector sensitivity.')


def plots(source, output):
    d = json.loads(source.read_text())
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': .18,
                         'svg.hashsalt': 'd14d-production-map'})

    def finish(fig, name):
        fig.text(.5, .025, NOTE, ha='center', va='bottom', fontsize=7)
        fig.tight_layout(rect=(0, .12, 1, 1))
        fig.savefig(output/(name+'.png'), dpi=180)
        svg = output/(name+'.svg')
        fig.savefig(svg, metadata={'Date': None})
        # Matplotlib emits trailing spaces inside multiline SVG path data.
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
        plt.close(fig)

    families = [r for r in d['families'] if r['energy_TeV'] == 13 and r['sigma_pb'] is not None]
    scalar = {r['id']: r for r in families if r['ordering'] == 'NO' and r['family'] == 0}
    offsets = {2264: (-8, 10), 14984: (5, -13), 13345: (-55, -8),
               8294: (-45, 15), 16385: (6, -17), 2616: (8, -12), 14187: (-5, 17)}
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    for ordering, family, marker in [('NO', 0, 'o'), ('NO', 1, 's'), ('IO', 0, '^'), ('IO', 1, 'v')]:
        rows = [r for r in families if (r['ordering'], r['family']) == (ordering, family)]
        ax.errorbar([r['mH2_GeV'] for r in rows], [r['sigma_times_BR_pb'] for r in rows],
                    yerr=[r['integration_error_on_sigma_times_BR_pb'] for r in rows],
                    fmt=marker, ms=4, alpha=.65, label=f'{ordering} family {family}')
    for r in scalar.values():
        ax.annotate(str(r['id']), (r['mH2_GeV'], r['sigma_times_BR_pb']),
                    xytext=offsets.get(r['id'], (4, 4)), textcoords='offset points', fontsize=7,
                    arrowprops={'arrowstyle': '-', 'color': '.5', 'lw': .4} if r['id'] in offsets else None)
    ax.set(xlabel=r'$m_{H_2^\pm}$ [GeV]', ylabel=r'$\sigma\,\mathrm{BR}(H_2^\pm\to H_1^\pm Z)$ [pb]',
           yscale='log', title='13 TeV: 16 vacuum-sufficient PASS / nominal-B-compatible points')
    ax.legend(fontsize=8, title='Integration errors only; family markers overlap', title_fontsize=8)
    finish(fig, 'cascade_rates_13TeV')

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    rows = list(scalar.values())
    gamma = np.array([abs(r['gamma_rad']) for r in rows])
    artist = ax.scatter([r['mH2_GeV'] for r in rows], [r['sigma_pb'] for r in rows],
                        c=[r['tanbeta'] for r in rows], s=35+110*gamma,
                        cmap='viridis', edgecolors='black', linewidths=.4)
    ax.errorbar([r['mH2_GeV'] for r in rows], [r['sigma_pb'] for r in rows],
                yerr=[r['integration_error_pb'] for r in rows], fmt='none', color='black', lw=.7)
    fig.colorbar(artist, ax=ax, label=r'$\tan\beta$')
    production_offsets = {**offsets, 13345: (-50, -12), 8294: (-36, 16),
                          16385: (0, -24), 14187: (8, -23), 2616: (12, 10)}
    for r in rows:
        ax.annotate(str(r['id']), (r['mH2_GeV'], r['sigma_pb']), xytext=production_offsets.get(r['id'], (4, 4)),
                    textcoords='offset points', fontsize=7,
                    arrowprops={'arrowstyle': '-', 'color': '.5', 'lw': .4} if r['id'] in production_offsets else None)
    handles = [plt.scatter([], [], s=35+110*g, color='gray', label=f'|γ|={g:.1f} rad') for g in (.2, .8, 1.4)]
    ax.legend(handles=handles, fontsize=8)
    ax.set(xlabel=r'$m_{H_2^\pm}$ [GeV]', ylabel=r'$\sigma(pp\to tH_2^-+\bar tH_2^+)$ [pb]',
           yscale='log', title='13 TeV LO 5FS: actual integrations; error bars are numerical only')
    finish(fig, 'production_mass_13TeV')

    fig, ax = plt.subplots(figsize=(8.5, 5.7))
    for vacuum, marker in [('PASS', 'o'), ('UNKNOWN', 'x')]:
        for nominal, color in [('APPROX_COMPATIBLE', '#167c80'), ('APPROX_DISFAVORED', '#bb7852')]:
            rows = [r for r in d['conditional_scalar_scatter']
                    if (r['vacuum'], r['nominal_bsgamma']) == (vacuum, nominal)]
            ax.scatter([r['mH1_GeV'] for r in rows], [r['mH2_GeV'] for r in rows],
                       marker=marker, color=color, alpha=.65, s=28,
                       label=f'Vacuum {vacuum}; nominal B {nominal.removeprefix("APPROX_").lower()} ({len(rows)})')
    for r in d['unresolved_subTeV_opportunities']:
        ax.scatter(r['physical']['mH1'], r['physical']['mH2'], facecolors='none', edgecolors='black', s=100)
        ax.annotate(str(r['id']), (r['physical']['mH1'], r['physical']['mH2']),
                    xytext=(5, -10), textcoords='offset points', fontsize=7)
    ax.axhline(1000, color='gray', ls='--', lw=.8)
    ax.set(xlabel=r'$m_{H_1^\pm}$ [GeV]', ylabel=r'$m_{H_2^\pm}$ [GeV]',
           title='Original 225-point conditional sample; six circled sub-TeV opportunities remain UNKNOWN')
    ax.legend(fontsize=8, loc='upper left')
    finish(fig, 'conditional_vacuum_scatter')

    fig, axes = plt.subplots(1, 2, figsize=(10, 5.5))
    ids = [r['id'] for r in d['energy_comparisons']]
    index = {(r['id'], r['energy_TeV']): r for r in d['rates']}
    for energy, offset in ((13, -.07), (14, .07)):
        rates = [index[i, energy] for i in ids]
        valid = [(j, r) for j, r in enumerate(rates) if r['sigma_pb'] is not None]
        axes[0].errorbar([j+offset for j, r in valid], [r['sigma_pb'] for j, r in valid],
                         yerr=[r['integration_error_pb'] for j, r in valid], fmt='o', label=f'{energy} TeV')
    ratios = [(j, r) for j, r in enumerate(d['energy_comparisons']) if r['sigma14_over_sigma13'] is not None]
    axes[1].errorbar([j for j, r in ratios], [r['sigma14_over_sigma13'] for j, r in ratios],
                     yerr=[r['integration_error_uncorrelated_quadrature'] for j, r in ratios], fmt='o', capsize=3)
    for ax in axes:
        ax.set_xticks(range(len(ids)), [str(i) for i in ids]); ax.set_xlabel('Original point ID')
    axes[0].set(ylabel='LO charge-summed production [pb]', yscale='log', title='Actual native integrations')
    axes[0].legend()
    axes[1].set(ylabel=r'$\sigma(14\ \mathrm{TeV})/\sigma(13\ \mathrm{TeV})$',
                title='Spectrum-specific ratios\nNumerical error: uncorrelated quadrature assumed')
    finish(fig, 'production_13_vs_14TeV')
    save(output/'plot_hashes.json', {'input_sha256': file_sha(source),
         'plotting_source_sha256': file_sha(Path(__file__)),
         'artifacts': {p.name: file_sha(p) for p in sorted(output.iterdir()) if p.suffix in ('.png', '.svg')}})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    plots(a.input, a.output)


if __name__ == '__main__':
    main()
