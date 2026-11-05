# HW normalization: source-preserving resolution

The extra `MW**-2` in the pinned LFV implementation is an error in the
dimensionless coefficient. Remove it **only in our research adapter**. This
choice follows dimensions, a flavor-diagonal operator identity and the
independently implemented EDM observable, rather than publication authority.
The result is a validated normalization of the reference common-limit HW
term. It is not an independent derivation of every two-loop master reduction
or a complete Zee amplitude.

## Inputs actually examined

* [Pinned source](https://gitlab.com/jbrod/general-2hdm-pheno/-/blob/b5035cd58d2a7e4a91e9790d045df062b97adffe/thdm.py):
  `f11` lines 152–163; ratio definitions 651–663; EDM HW 1224–1230;
  LFV R 1511–1517, L 1792–1798; rate 1821–1823. The task's 1510/1791
  identify the immediately preceding comments. HEAD and original bytes of
  thdm.py, rge.py, adm.py, example.py and LICENSE.txt are verified before
  **and after** running. No monkeypatch, AST rewrite or source edit is used.
* [Paper v4](https://arxiv.org/html/2410.17313v4): potential/field definitions
  (4)–(8), Yukawa (13), EDM operator (16), mass ratios below (19), potential
  EDM (42),(44),(46), f11 (47), LFV operator (48), HW (65),(66).
* [July 2026 erratum](https://doi.org/10.1007/JHEP07(2026)184), read from
  the previously downloaded hash-verified PDF: reverses the potential-term
  signs in original journal (4.27),(4.29),(4.31),(5.14)–(5.19), among other
  corrections. It does not define a dimensionful f11 or insert an MW factor.
  The corrected v4 signs and pinned EDM code agree. Original journal numbering
  differs from continuous HTML numbering.

The existing `external_2hdm_sources.json` supplies PDF hashes. They are
rechecked in `hw_generic_evidence.json`; historical evidence is retained.

## Native dimensions and chirality

Use canonical fields, natural units, positive e and
`sigma^{mu nu}=i[gamma^mu,gamma^nu]/2`. The mass-basis interaction is

```
L_int = -h_k bar(l_b)[C_k,ba PL + C_k,ab* PR] l_a
        -G_k h_k H- H+,
C_k = q_k1 diag(m_l/v) + rho_l q_k2*,   rho_l=D/sqrt(2),
G_k = d^3 V/(dh_k dH- dH+) = v B_k,
B_k = q_k1 Z3 + Re(q_k2 Z7).
```

G is **mass dimension 1**, not a quartic or a mass cubed. It is the
coefficient in the Lagrangian; the all-incoming rule is `-i G`. The two
charged fields are distinct, so there is no identical-field factor 2.
The native full-potential Hessian derivative and the separate Higgs-basis
rotation independently agree with this G for every new potential. Yukawas,
q and Z have dimension zero. For parent i, daughter j, off-diagonal external
couplings are `Y_L=rho_ji q_k2*`, `Y_R=rho_ij* q_k2`. No transpose of D,
chirality exchange or extra complex conjugation is permitted.

The dipole operator `bar(l_j) sigma P_X l_i F` has dimension **5**. Its
Lagrangian coefficient kappa_X has dimension -1. The paper's convention is

```
kappa_X = -e m_i c_X/(16 pi^2 v^2),        [c_X]=0,
kappa_X = +e m_i C_X/2 in frozen Module3, [C_X]=-2,
C_X = -c_X/(8 pi^2 v^2).
```

The test constructs `i L` with an outgoing photon
`F_mu nu=i(q_mu eps_nu-q_nu eps_mu)` and explicit Dirac matrices in both
conventions. The **signed** matrices agree for two independent complex
chiralities. Previously validated frozen photon quadratures also agree with
the converted author HA and neutral-fermion photon groups. A width alone
would not establish this sign.

## f11 is dimensionless, including its masters

Its arguments are exactly `x=M_H+^2/M_hk^2`, `y=MW^2/M_hk^2`. Every term
in actual source f11 and paper (47) is a rational function of x,y times
logs, a dilogarithm or the dimensionless finite three-mass master Phi.
There is no implicit v, MW or renormalization scale in this function.

We independently integrate the master rather than use the author's
Clausen/dilog implementation:

```
Phi(a,b) = integral_0^1 du log(A/B)/(A-B),
A=a u+b(1-u), B=u(1-u),
Phi(1/(4x)) in the one-argument convention = Phi(x,x).
```

This is the finite Feynman-parameter representation after one parameter
integration. `log(A/B)/(A-B)` has the continuous limit `1/B` at A=B.
The dilogarithm is also directly integrated. Substitution in the **shared
published reduction** yields f11 at all 39 actual mass-ratio pairs, worst
absolute difference `4.49e-9` (cancellations among much larger master terms).
This verifies the master convention and dimensions independently; it does
not independently derive the graph numerator multiplying these masters.

The complete native combination is
`G_k Y_X f11/M_hk^2`, dimension -1. The corresponding dimensionless answer is

```
c_X^HW = alpha v^2/(32 pi sw^2 m_i)
         sum_k G_k Y_X,k f11(x_k,y_k)/M_hk^2,

kappa_X^HW = -e alpha/(512 pi^3 sw^2)
             sum_k G_k Y_X,k f11(x_k,y_k)/M_hk^2.
```

The prefactor is `e g2^2/[8(16 pi^2)^2]` in kappa, with the displayed
minus sign, since `alpha/sw^2=g2^2/(4 pi)`. The numerical normalization
relative to the EDM is fixed by the independent operator argument below.
Inserting `G=v B` reproduces v4 (65),(66). Keeping the source's additional
MW^-2 instead makes kappa dimension -3, or c dimension -2, **inside a sum
of dimensionless coefficients**. Redefining f11 as `MW^2 f11` would contradict
its actual function and ratio inputs; redefining G as `MW^2 G` would violate
the canonical potential derivative, its native vertex and HA/HZ. A single
operator-convention change would affect every group. None can absorb this
term-specific error. Dimensions alone do not select all possible numerical
constants; that is why we also need the following check.

## Independent diagonal-operator normalization check

Write one Hermitian chiral dipole pair as
`kappa_R O_R + kappa_R* O_L`. Expanding PL/PR gives
`Re(kappa_R) bar(l)sigma l F + i Im(kappa_R) bar(l)sigma gamma5 l F`.
Matching to the EDM operator `-i d/2 bar(l)sigma gamma5 l F` proves

```
d = -2 Im(kappa_R) = e m/(8 pi^2 v^2) Im(c_R),
c_L = c_R* for this diagonal potential class.
```

Do **not** take the off-diagonal expression with both chiralities and then
add its h.c. a second time after setting i=j: the diagonal pair is already
Hermitian. That would produce a spurious factor 2. The executable test also
checks this identity with explicit gamma matrices.

Here this comparison is physically the **same** HW class: one LFV/diagonal
neutral-Yukawa spurion, one real diagonal scalar trilinear, flavor-blind
gauge interactions, massless internal neutrinos, and leading external-mass
expansion. Its imaginary diagonal spurion has no SM-real diagonal-Yukawa
contamination. It does not require the one-loop EOM limit, which is different
and is deliberately excluded. Both potential photon and Z classes serve
as controls for the same operator identity.

Upstream explicitly rejects `i=j`. Without changing that source, the test
uses its allowed `(2,1)` channel with `m_mu=m_e` and both off-diagonal rho
entries equal to rho_11. Only the three potential locals are taken from this
formal auxiliary spurion input; it is not one of the model benchmarks.
The EDM locals are independently **captured from electron_EDM on the
original input**, rather than rewritten as a second copy of the LFV formula.

For G1, in GeV^-1:

| Class | Captured EDM | Derived from corrected LFV operator | Derived from original LFV source |
|---|---:|---:|---:|
| HA | +2.39576537105e-12 | +2.39576537105e-12 | +2.39576537105e-12 |
| HZ | +9.72063967807e-14 | +9.72063967807e-14 | +9.72063967807e-14 |
| HW | -1.48483521920e-12 | -1.48483521920e-12 | -2.29878825430e-16 |

All 39 diagonal class checks agree, including independently varied MW,
potentials and phases. Combined with fixed f11/G conventions, this selects
**MW^2 times the captured source HW**, rather than an arbitrary replacement
mass squared. The analytic identity, its Hermitian-pair factor, signed
operator matching, and independent masters go beyond comparing two copied
LFV expressions. The absolute EDM loop calculation is still a reference
input: we have not independently regenerated the authors' complete two-loop
numerators or Rxi cancellations. The validated claim is normalization and
complex coefficient closure in this shared reference calculation.

## Adapter, homogeneity and failures retained

`external_2hdm_hw_override.py` captures all 13 original local groups. It
reconstructs `AUTHOR_UNMODIFIED` from those groups and constructs
`PAPER_CORRECTED_HW` by replacing **only HW**, evaluated with native G and
neutral vertices. Their complex difference is retained for both chiralities
and every channel. The formerly conditional paper normalization now has the
scoped status `2HDM_REFERENCE_HW_OPERATOR_EDM_NORMALIZATION_VALIDATED`.
It is never a physical Zee W Wilson or a replacement of historical evidence.

At fixed dimensionless couplings, scaling matched physical masses and v by
lambda and m12sq by lambda^2 gives `G->lambda G`, `c->c`, `C->C/lambda^2`.
All 13 groups were checked at lambda=1/2,2 for all 39 channel inputs.
Original HW instead gives `c_HW->c_HW/lambda^2`; the other 12 pass. The
upstream empirical top pole/MSbar fit contains fixed GeV constants: its
argument is inverted to scale the **matched** top mass exactly. Rescaling
its argument naively is not a change of physical units. The hardcoded 2 GeV
light-quark input scale affects only species absent from these 13 groups.

`test_original_author_HW_diagonal_operator_normalization_EXPECTED_FAIL` is
an explicit unittest expected failure. It asserts the unmodified source
obeys the EDM identity, and fails. It must remain a failure until upstream
changes. Source checks remain byte-identical. A draft upstream report is
provided in `UPSTREAM_HW_ISSUE_DRAFT.md`; nothing has been sent.

Reproduce with the pinned checkout already present:

```bash
python -m research.wgamma_d16.external_2hdm_hw_override --output research/wgamma_d16/hw_generic_evidence.json
python -m unittest research.wgamma_d16.test_hw_normalization -v
```

The CLI writes detailed repeat/scale records to ignored
`local/hw_generic_details.json`, binds them by SHA256, and writes the tracked
coefficient evidence. Generic closure, scalar-constraint limits and the
separate restricted singlet HZ class are described in
`GENERIC_2HDM_CLOSURE.md` and `ZEE_EXTENSION_INVENTORY.md`.
