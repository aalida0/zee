"""Same-point D4 two-body charged-scalar widths, using the D12 application."""
import copy
import hashlib
import json
from pathlib import Path

from module7.d4_inputs import native_card, SM
from module7.d4_native import expected_coefficients
from module7.d4_decay_table import nonleptonic, leptons, complete_total
from module11.d11b_offline_fit import file_hash
from module2.interface import canonical_hash

ROOT = Path(__file__).resolve().parents[1]


def provenance():
    path = ROOT/'validation/module7/d4_native_validation.json'
    evidence = json.loads(path.read_text())
    for name, sha in evidence['source_sha256'].items():
        if file_hash(name) != sha:
            raise ValueError('D4 native source identity changed: '+name)
    files = [*(p for d in ('module1', 'module7', 'scripts') for p in sorted((ROOT/d).glob('*.py'))), ROOT/'module12/study.py', Path(__file__), path]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


class DecayCalculation:
    def __init__(self, scalar, first_family):
        self.scalar = scalar
        self.p = scalar['physical']
        self.provenance = provenance()
        self.cards = {}
        self.nonleptonic = {}
        for k in (1, 2):
            card = native_card(self.p, first_family, self.p[f'mH{k}'], 'D14')
            self.cards[k] = card
            self.nonleptonic[k] = nonleptonic(self.p, self.case(card), k)

    @staticmethod
    def case(card):
        return {'coefficients': [[{'real': c.real, 'imag': c.imag} for c in row]
                                 for row in expected_coefficients(card)]}

    def evaluate(self, family):
        mothers = {}
        for k in (1, 2):
            card = copy.deepcopy(self.cards[k])
            card['rules'].update(Fzee=family['F'], Ye=family['Ye'], Ye2=family['Ye2'])
            rows = self.nonleptonic[k] + leptons(self.p, self.case(card), k)
            total = complete_total(rows, k)
            if total['status'] != 'D4_COMPLETE_TWO_BODY_BR_PASS':
                return {'status': 'NOT_EVALUATED', 'reason': 'Incomplete D4 channels', 'details': total}
            # The complete inventory distinguishes closed channels from absent data.
            br = {r['channel']: r['width_GeV']/total['total_width_GeV'] for r in rows}
            mothers[f'H{k}'] = {'total': total, 'channels': rows,
                               'leptonic_branching_ratios': {l: br[l+' nu_all'] for l in ('e','mu','tau')},
                               'br_tb': br['t anti-b']}
            if k == 2:
                mothers['H2']['br_H1_Z'] = br['H1 Z']
        return {'status': 'PASS', 'mothers': mothers,
                'cascade_product': mothers['H2']['br_H1_Z']*mothers['H1']['br_tb'],
                'scalar_sha256': canonical_hash(self.scalar),
                'yukawa_sha256': {k: canonical_hash(family[k]) for k in ('F','D','Ye','Ye2')},
                'module2_input_sha256': family['input_sha256'],
                'source_sha256': self.provenance, 'sm_card_sha256': canonical_hash(SM),
                'scope': 'D4 on-shell tree two-body; no off-shell or loop corrections'}
