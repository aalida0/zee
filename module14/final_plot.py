"""Plot exported saved data only. No production interpolation or sensitivity."""
import argparse
import importlib.metadata
from pathlib import Path

from module14.conditional_scan.workflow import lines, load
from module14.scan import file_sha


def plot(directory, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    directory = Path(directory); audit = load(directory/'audit.json')
    if audit['status'] != 'COMPLETE' or any(file_sha(directory/n) != h for n, h in audit['files_sha256'].items()):
        raise ValueError('Export is incomplete or modified')
    rows = list(lines(directory/'families.jsonl'))
    with plt.rc_context({'svg.hashsalt': 'd14-final-export-1'}):
        fig, axes = plt.subplots(1, 2, figsize=(9, 3.5), layout='constrained')
        for ax, energy in zip(axes, ('13', '14')):
            selected = [r for r in rows if r[f'cascade_tb_{energy}_pb'] is not None]
            for vacuum, marker in (('PASS', 'o'), ('UNKNOWN', 'x')):
                points = [r for r in selected if r['vacuum_status'] == vacuum]
                if points:
                    ax.scatter([r['saved_results']['input_card']['physical']['mH2'] for r in points],
                               [r[f'cascade_tb_{energy}_pb'] for r in points], marker=marker, label='Vacuum '+vacuum)
            if not selected: ax.text(.5, .5, 'No documented production supplied', ha='center', transform=ax.transAxes)
            else: ax.legend(fontsize=7)
            ax.set(xlabel='Charged H2 mass [GeV]', ylabel='sigma x BR(H2 -> H1 Z) x BR(H1 -> tb) [pb]', title=energy+' TeV')
        fig.suptitle('Conditional diagnostic; LFV/Higgs incomplete; no global acceptance', fontsize=10)
        output = Path(output)
        if output.exists(): raise FileExistsError(output)
        fig.savefig(output, format='svg', metadata={'Date': None, 'Creator': 'D14; matplotlib '+importlib.metadata.version('matplotlib')})
        plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--export-dir', required=True); p.add_argument('--output', required=True)
    a = p.parse_args(); plot(a.export_dir, a.output)


if __name__ == '__main__': main()
