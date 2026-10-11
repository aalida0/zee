# Gate A1F — charged-doublet Y dipoles and a coherent scalar one-loop screen

**Scope:** combines existing A1C f-only and A1E neutral one-loop
dipoles with the missing charged-doublet Y-only scalar loop.
**NOT** full Zee radiative LFV: no Barr-Zee or independent all-diagram
cross-check, no global scalar/flavour fit.

## Charged lepton / charged scalar chirality convention

Chen [arXiv:2508.18757](https://arxiv.org/abs/2508.18757)
Eq.(4): the Higgs-basis doublet component has
`-L = sqrt(2) bar(ell_R) Y^ell nu_L H^- + h.c.`
Hence the charged scalar H+ vertex with internal neutrino k:
`R_(k,i) = sqrt(2) * doublet_fraction * (Y^ell)_(i,k)^*`.

Lavoura, *General formulae for f1 -> f2 gamma*,
[arXiv:hep-ph/0302221](https://arxiv.org/abs/hep-ph/0302221),
Eqs.(26)-(30),(38)-(43), with internal Q_F=0, external
charged lepton Q_f=-1 and Q_B=+1. Eq.(41) equals `1/12` as
`m_nu/mH->0`. Neutrino-mass terms are negligible.

Using Florentino's charged mixing convention,
[arXiv:2106.08332](https://arxiv.org/abs/2106.08332)
Eq.(22), H1 doublet fraction cos(gamma), H2 -sin(gamma):

```
wY = cos(gamma)^2/mH1^2 + sin(gamma)^2/mH2^2
C_L^(Y+) = (Y @ Y.conj().T)[daughter,parent] * wY/(96*pi^2)
C_R^(Y+) = 0   (neglecting tiny neutrino masses)
```

All dipole coefficients use the `C_L,C_R` convention of
Herrero-Garcia et al. [arXiv:1701.05345](https://arxiv.org/abs/1701.05345),
Eq.(3.12). The one-loop amplitude components are summed
**before squaring**, unlike simple addition of branching fractions.

## Expected A1B seed diagnostics

| Channel | Y-only charged squared contribution | coherent scalar one-loop only |
|---|---:|---:|
| mu->e gamma | 2.88299e-32 | 1.52247e-18 |
| tau->mu gamma | 3.08636e-29 | 2.57700e-20 |
| tau->e gamma | 3.91789e-35 | 3.83378e-19 |

**Do not label these physical full BRs.** In particular:
- Neutral one-loop and charged singlet amplitudes can interfere;
  coherent one-loop results differ from the sum of BR components.
- Two-loop Barr-Zee amplitudes in Type-II quark scenario are missing.
- Full amplitude phase/chirality conventions require independent model
  implementation validation (FeynRules/UFO or published examples).
- Other LFV observables and all scalar/flavour constraints remain absent.

The strong suppression of the Y-only charged contributions arises
from `max|Y|~9.46e-6` of this *minimum-norm* Yukawa seed. It does
NOT characterize a global flavour-parameter scan; four complex
Yukawa directions remain unconstrained by neutrino masses.

## Run on the AF

```bash
cd /home/aalida/zee
git fetch origin gateA1f-charged-doublet-Y-dipoles
git switch gateA1f-charged-doublet-Y-dipoles
python3 -m unittest discover -s tests -p 'test_gateA1f_charged_doublet_y_dipoles.py' -v
python3 scripts/gateA1f_charged_doublet_y_dipoles.py \
  --output work/gateA1f_charged_doublet_y_dipoles.json
```

Stop/go: regression PASS allows only this one-loop component
screen to be treated as reproducible. Do not claim LFV or global
benchmark viability. The next high-value check is electroweak oblique
S/T/U at these 300/700/580.7/633.7 masses: failure can exclude this
scalar candidate independently of small LFV contributions.
