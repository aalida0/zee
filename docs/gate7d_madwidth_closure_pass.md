# Gate 7D: MadWidth partial-width closure — PASS (2026-10-11)

Status: **LO NUMERICAL WIDTH CLOSURE PASS**, with an isolated,
quantitatively explained EW-scheme difference for W+hheavy.
Full physical Zee benchmark remains **NOT VALIDATED**.

## Actual AF MadWidth results supplied by user

Diagnostic: β=1.394, m(light H±)=300 GeV (PDG 228),
m(heavy H±)=700 GeV (PDG 227), γ=1.089.
Leptons set to Type-II *diagnostic* Yukawas; Zee f_ab=0
(radiative neutrino masses vanish).

| Channel | Independent Gate6 width (GeV) | MadWidth (GeV) | Relative residual |
|---|---:|---:|---:|
| heavy→light+Z | 9.411343198 | 9.411302014 | -4.376e-6 |
| heavy→tb | 1.558105505 | 1.558100405 | -3.273e-6 |
| heavy→W+hheavy | 1.071030743 | 1.093400235 | +2.08859e-2 |
| heavy→light+h125 | 0.267036409 | 0.267019995 | -6.147e-5 |
| light→tb | 0.0909493753 | 0.0909490011 | -4.115e-6 |

MadWidth total two-body widths in the neutrino-unfitted diagnostic:
`Γ(heavy)=12.36727 GeV`, `Γ(light)=0.09520432 GeV`.
Total decay table BR sums are 1.00000000942 and 0.99999999371,
consistent with rounding. These are **not a physical Zee BR**.

## Discrepancy resolved: electroweak input scheme

Gate6 independently used `MW=80.379 GeV`,
`sin²θW=0.23122`, `1/αEW=127.95`.
The unchanged UFO diagnostic card uses
`SMINPUTS[1]=127.9`, `SMINPUTS[2]=1.16637e-5 GeV^-2`
and `MASS[23]=91.1876 GeV`.

Yang/Wu `ZEE_UFO/parameters.py` calculates
`MW²=MZ²/2 + sqrt(MZ⁴/4 − παEW MZ²/(sqrt(2) GF))`.
This gives `MW=79.8243597462 GeV`,
`sin²θW=0.23369913342`, `gW=0.6483971672`.
Gate6 weak coupling was `gW=0.6517365667`.

Since vector width scales as `gW² λ(M²,m²,mW²)^(3/2) / mW²`,
and the W+hheavy channel is close to threshold:

`Γ(new scheme)/Γ(old scheme) = 1.0209243630`.

Predicted scheme-corrected Gate6 width:
`1.0934413796 GeV`, versus MadWidth `1.0934002345 GeV`.
Remaining relative residual: `-3.76290e-5`,
well below 0.1%. **The initial 2.09% discrepancy is therefore
consistent with electroweak scheme and threshold kinematics.**

Use a source-checked, card-input-driven audit instead of assuming
the card's mass/SMINPUTS values:

```bash
cd ~/zee
git pull --ff-only
python3 -m unittest discover -s tests -v
python3 scripts/gate7_ew_scheme_audit.py \
 --input-card work/gate7_madwidth/diagnostic_input_param_card.dat \
 --width-card work/gate7_madwidth/madwidth_output_param_card.dat \
 --output work/gate7_madwidth/ew_scheme_audit.json
```

The script fails if the EW-scheme corrected W+hheavy width
still differs by >= 0.1%, or if card masses are not as expected.

## What is actually established?

1. Existing original Zee UFO adapted at FeynRules source to the
   Type-II Higgs-basis quark Yukawas, exported in local Mathematica.
2. Gauge/mixed charged-state and tb heavy/light interactions present.
3. MG5 3.5.9 matrix element *diagram generation* works for 4FS
   associated production, mixed pair, and cascade decay.
4. Scalar quartic basis mapping closes analytically.
5. Five LO partial-width calculations close numerically after
   accounting for different tree-level EW input schemes.

## Major open gates (still mandatory)

- **Gauge consistency:** numerical Ward identities and suitable
  reference limits for new Type-II Yukawa amplitudes.
- **Collider backgrounds/rates:** ensure 6-diagram mixed production
  is compared to 3-diagram pure Z-DY baseline; match full EW scheme.
- **Physical model:** neutrino mass matrix, allowed f_ab and LFV;
  S/T/U, B→X_s gamma, Higgs/direct searches and flavor constraints.
- **Widths:** recompute consistent full partial-width inventory
  when leptonic inputs and potential channels are specified.
- **NLO:** freshly generate UV/R2 after Type-II Yukawa change;
  old Yang/Wu `ZEE_NLO` counterterms are not sufficient.

**Decision:** LO model and diagnostic benchmark pass,
not yet permission for full-event production or NLO physics claims.
