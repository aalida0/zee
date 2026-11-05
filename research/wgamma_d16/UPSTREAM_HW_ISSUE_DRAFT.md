# Draft only — nothing sent

Title: Extra inverse MW² in cL_llpg_HW and cR_llpg_HW at b5035cd

The corrected reference at b5035cd58d2a7e4a91e9790d045df062b97adffe has an
additional `/self.MW**2` in thdm.py lines 1511 and 1792, compared with v4
Eqs. (65),(66). f11 takes dimensionless squared-mass ratios and the potential
coefficient `q1 Z3+Re(q2 Z7)` is dimensionless. The resulting HW local has
dimension -2 while cL,cR and the other twelve locals are dimensionless.

We checked beyond the dimensional discrepancy. With one Hermitian diagonal
dipole pair the operator definitions imply
`d=e*m/(8*pi**2*v**2)*Im(cR)`. The potential HA and HZ groups satisfy that
relation against electron_EDM; HW satisfies it only after multiplying the
LFV HW local by MW². For a reconstructed nonzero-potential example with
Z3=.8,Z7=.3, the captured EDM HW is -1.48483521920e-12 GeV^-1, whereas the
original LFV operator gives -2.29878825430e-16 GeV^-1. Their ratio is MW².
Simultaneous matched mass/vev scaling also leaves the corrected cHW invariant
but scales the original cHW as inverse mass squared. Both chiralities and
all three LFV channels show the same discrepancy. Independent finite-master
quadrature confirms the convention of f11. We have not independently redone
the complete two-loop numerator reduction.

Suggested narrow fix for your review: remove `/self.MW**2` in those two
LFV locals. Our copy of your source remains unmodified. Reproducer in our
research adapter, with full input dictionaries and source pin:

```bash
python -m research.wgamma_d16.external_2hdm_hw_override --output research/wgamma_d16/hw_generic_evidence.json
python -m unittest research.wgamma_d16.test_hw_normalization -v
```

The original-source regression is explicitly an expected failure; the
adapter separately reports AUTHOR_UNMODIFIED and PAPER_CORRECTED_HW.
Please confirm whether any different convention was intended for the LFV HW
term. No issue or email has been submitted.
