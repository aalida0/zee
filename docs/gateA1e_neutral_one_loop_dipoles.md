# Gate A1E — Neutral one-loop radiative LFV (partial only)

This builds on Gate A1B's hierarchical normal-ordering neutrino seed
and complements the **f-only charged-singlet** radiative calculation
in Gate A1C and the **neutral tree-level** tau 3-body decays in A1D.

## Independent theoretical normalization

- Lavoura, *General formulae for f1→f2γ*, EPJC29 (2003) 191,
  [arXiv:hep-ph/0302221](https://arxiv.org/abs/hep-ph/0302221),
  Eq.(26)-(30),(38)-(43), scalar-fermion loop. For neutral scalar
  S and internal charged lepton F: Q_F=-1, Q_B=0.
- Herrero-García et al. JHEP04(2017)130,
  [arXiv:1701.05345](https://arxiv.org/abs/1701.05345),
  Eqs.(3.12),(3.16)-(3.17), as independent leading-log limit.
- Scalar-lepton couplings: Chen [arXiv:2508.18757](https://arxiv.org/abs/2508.18757)
  Eq.(4), with Florentino's alpha/beta mixing convention
  [arXiv:2106.08332](https://arxiv.org/abs/2106.08332).

In the Lagrangian `L=-S * bar(l_i)[C_ij PL+C_ji* PR] l_j`,
Lavoura's external (i) and internal (k) Yukawas are
`L_i=C[k,i]`, `R_i=C[i,k].conj()`. The routine computes
both chiral Wilson coefficients with coherent internal e,mu,tau and
h125,Hheavy,A sums. The scalar mass ratio `t=(mF/mS)^2` is
retained in the finite loop functions (40),(42), with **zero external
momenta only in loop denominator functions** (lepton mass factors
needed for dipoles remain).

A controlled sparse Yukawa texture with only `Y[e,tau]` and
`Y[tau,mu]` yields Lavoura CL equal in absolute value to the
leading-log limit of Herrero Eq.(3.16) at mS=400 GeV to ~6e-5
relative, independently validating the internal-tau chirality term.

## Candidate numerical component results (not full branching fractions)

m(h125)=125 GeV; m(H)=580.7 GeV; m(A)=633.7 GeV;
alpha=1.398; beta=1.394; Y from A1B.

| Channel | neutral 1-loop squared contribution alone |
| --- | ---: |
| mu→e gamma | 2.013e-22 |
| tau→mu gamma | 7.760e-21 |
| tau→e gamma | 1.004e-23 |

**These are not lower or upper bounds** on the complete physical
Zee radiative branching ratios: charged scalar amplitudes and
two-loop Barr-Zee amplitudes (and interference) remain missing.
No overall LFV compatibility is established.

## Run on AF

```bash
cd /home/aalida/zee
git fetch origin gateA1e-neutral-one-loop-dipoles
git switch gateA1e-neutral-one-loop-dipoles
python3 -m unittest discover -s tests -p 'test_gateA1e_neutral_one_loop_dipoles.py' -v
python3 scripts/gateA1e_neutral_one_loop_dipoles.py \
  --output work/gateA1e_neutral_one_loop_dipoles.json
```

Test strategy: analytic small-t limits; independent Herrero
leading-log chirality check; zero off-diagonal LFV for diagonal
Y; finite complex interference and seed component regression.
This is a controlled partial radiative diagnostic, **not a
complete phenomenological LFV fitter**.

Next: charged scalar Y-dependent dipoles coherent with the f
contributions, one-loop interference and 2-loop Barr-Zee with
Type-II quark Yukawas; all LFV channels and scalar constraints
must then be checked at the SAME point.
