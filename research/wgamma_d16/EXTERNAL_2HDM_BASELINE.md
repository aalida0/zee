# D16 corrected external 2HDM baseline — 2026-11-05

**Reference execution: PASS. Strict-limit full complex agreement: PASS on two
restricted potentials, three channels each. Generic-potential validation: FAIL
in the authors' `HW` term. Full Zee gauge completion: BLOCKED.**

The first numerical milestone has a delimited success: two independent complex
LFV inputs on reconstructed `Z3=Z7=0` potentials agree with the complete unmodified
author result, including nonzero kinetic and charged-fermion terms. This does
**not** resolve the generic nonzero-potential discrepancy below. No physical Zee
W coefficient is released. These formal F=0 fixtures are not neutrino fits or
accepted phenomenological points.

## Corrected source and reproduction

Official [repository](https://gitlab.com/jbrod/general-2hdm-pheno), pinned and
remote-HEAD verified at **b5035cd58d2a7e4a91e9790d045df062b97adffe**, authored
2026-04-30T21:05:38-04:00, Apache-2.0. The checkout is ignored and unchanged.
`external_2hdm_sources.json` records exact correction commits, dates, diff hashes,
paper/erratum hashes and successful network checks. The runner rejects an
incorrect HEAD or modified reference files. Python 3.10.12, NumPy 2.2.6,
SciPy 1.15.3 were used.

The mandatory [July 2026 erratum](https://doi.org/10.1007/JHEP07(2026)184)
corrects more than 5.7–5.8: it reverses the signs of original-journal
4.27, 4.29, 4.31, 5.4, 5.5, 5.14–5.19, 5.22, 5.23 and fixes the bracket in
4.26 (`f8e`). Its corrected neutral-fermion factors and conjugations are present
in the April correction commits; code verification is not based on publication
date alone. The compact comparison implements these sums in the frozen field
basis and uses the [v4 equations](https://arxiv.org/html/2410.17313v4), whose
continuous numbering differs from the journal numbering. The 2016 Abe erratum
belongs to the historical inner-tensor calculation, not this paper.

From the main repository root:

```bash
git clone https://gitlab.com/jbrod/general-2hdm-pheno research/wgamma_d16/local/general-2hdm-pheno
git -C research/wgamma_d16/local/general-2hdm-pheno checkout b5035cd58d2a7e4a91e9790d045df062b97adffe
python -m research.wgamma_d16.external_2hdm --output research/wgamma_d16/local/external-comparison.json
python -m research.wgamma_d16.external_2hdm_native --evidence research/wgamma_d16/local/external-comparison.json --output research/wgamma_d16/local/external-native.json
python -m unittest research.wgamma_d16.test_external_2hdm -v
```

Skip cloning when the checkout already exists. Native substitution requires
`wolframscript`; it evaluates saved SARAH expressions without starting SARAH.
`--require-full` on the comparison command writes evidence then exits **2** for
the unresolved generic discrepancy; ordinary research reproduction exits zero.
Tests pass by verifying both the successful comparisons and the explicit
falsifier, not by granting full physics acceptance.

The unmodified `example.py` executes completely. It gives
`cL=-0.021100+0.040702i`, `cR=0.002396-0.005345i` and
`Gamma(mu->e gamma)=2.380e-24 GeV`; full precision/stdout hash is in
`external_2hdm_evidence.json`. Its literal electron input is `511e-5 GeV`;
we preserve that example and explicitly use `0.00051099895 GeV` in our fixtures.
No positive rate is used as a signed amplitude oracle.

## Exact convention map

All matrices below are mass-basis matrices; our D has a right-Weyl row index.
The Higgs basis is `H_v=cb Phi1+sb Phi2`, `H_D=-sb Phi1+cb Phi2`.
Use the same positive e and sigma=i[gamma,gamma]/2. Matching the paper's
`-e mi c_X/(16 pi^2 v^2)` operator to our `+e mi C_X/2` gives

```
C_L = -c_L/(8 pi^2 v^2), C_R = -c_R/(8 pi^2 v^2)  [GeV^-2].
```

There is no chirality swap or conjugation in this operator conversion.
Authors' `i,j` are one-based parent,daughter; our indices are zero-based.
The native neutral coupling is `-i C_ab PL -i C_ba* PR`.

| Quantity | Author parameter in the strict Zee limit |
|---|---|
| neutral masses | `(Mh1,Mh2,Mh3)=(mh1,mh2,ma)` |
| charged mass | `MHp=mH1`, with `gamma=0` |
| angles | `theta12=beta-alpha`, `theta13=theta23=0` |
| `q_k1` | `(cos(delta),sin(delta),0)` |
| `q_k2` | `(-sin(delta),cos(delta),i)` |
| lepton matrix | `rho_l=D/sqrt(2)`; neither transpose nor conjugate |
| Type-II quarks | `rho_u=diag(mu,mc,mt) cot(beta)/v`, `rho_d=-diag(md,ms,mb) tan(beta)/v` |
| charged lepton vertex | `-sqrt(2) rho_l†_(ba)=-D_ab*`, same native R at gamma=0 |
| `h_k H- H+` | `L=-G_k h_k H- H+`, `G_k=v[q_k1 Z3+Re(q_k2 Z7)]` |

Indeed the paper's lepton PL coefficient is `m/v q1+rho_l q2*`, giving
`C_h=c_delta m/v-s_delta D/sqrt(2)`,
`C_H=s_delta m/v+c_delta D/sqrt(2)`, `C_A=-i D/sqrt(2)`.
The up-quark PL coefficient instead uses `rho_u* q2`; this distinction is
essential for the pseudoscalar and the corrected 5.7–5.8 conjugations.

Let `L345=Lambda3+Lambda4+Lambda5`, `t=(Lambda1+Lambda2-2 L345) sb² cb²`.
The restricted CP-conserving Higgs-basis quartics are

```
Z1=L1 cb^4+L2 sb^4+2 L345 sb² cb²
Z2=L1 sb^4+L2 cb^4+2 L345 sb² cb²
Z3=L3+t, Z4=L4+t, Z5=L5+t
Z6=-sb cb [L1 cb²-L2 sb²-L345(cb²-sb²)]
Z7=-sb cb [L1 sb²-L2 cb²+L345(cb²-sb²)]
Y1=-Z1 v²/2, Y3=-Z6 v²/2, Y2=mH1²-Z3 v²/2.
```

The executable independently checks the analytic Z3,Z7 rotation against
`G_h/v=c_delta Z3-s_delta Z7`, `G_H/v=s_delta Z3+c_delta Z7`, using the
frozen potential derivative and full Hessian reconstruction. It does not fit
trilinears independently of masses and quartics.

Comparison EW inputs satisfy `sw²=1-MW²/MZ²`, `g2=2 MW/v`,
`alpha=g2² sw²/(4 pi)`; the original author example uses its own inputs.
Author `MTpole` is converted internally; bottom/charm run to its weak scale.
We feed precisely these resulting masses to the frozen photon functions;
this is an explicitly aligned comparison scheme, not a change to Module4's
nominal unmatched production scheme. Authors neglect QED running and retain
leading Yukawa terms rather than every two-loop radiative correction.
The charged-quark expressions use the publication's unit-CKM approximation;
full flavor/CKM corrections are not validated by this fixture.

## Strict singlet removal and numerical evidence

Set `F=0`, `gamma=0`, hence `Mu4=0` at distinct charged masses, and
`K1=K2=K12=0`. Take the positive singlet mass squared to infinity with bounded
self-quartic; the fixtures use `mH2=10000 GeV` solely as an inert placeholder.
`H1` is the doublet, `H2` the singlet, and all neutral-singlet trilinears vanish.
The isolated singlet retains hypercharge: it is removed by the heavy-mass
limit and consistently matched EW inputs, not by assigning electric charge
zero. Doubling this removed mass leaves every mapped author input unchanged.

The two deterministic complex matrices use seeds 241017313 and 241017314.
Inputs, all 13 source-local terms, complex two-loop and total coefficients,
converted Wilsons, coherent widths and exact differences are archived for
mu->e, tau->e, tau->mu. The scalar masses/m12sq below are GeV/GeV².

| Full-agreement fixture | mH1 | m12sq | author cL (mu->e) | author cR (mu->e) |
|---|---:|---:|---|---|
| A, Z3=Z7=0 | 368.3720631063331 | 38364.93883271238 | 0.02614640643+0.02154331637i | -0.007834523811-0.02349284001i |
| B, Z3=Z7=0 | 336.6049219089992 | 53197.531120587824 | -0.04660503584+0.006932648142i | -0.01994177607+0.002235643828i |

These potentials are obtained by solving the two linear conditions in
m12sq and charged mass squared, then rechecking the full frozen Hessian.
Kinetic and charged-fermion terms remain nonzero. The comparison uses
independently arranged field-basis sums with shared author master functions;
it is not an independent evaluation of all two-loop master integrals or Rxi
cancellation. Independently integrated frozen photon kernels provide a
separate check for the already validated overlaps.

128 additional coefficient substitutions into **actual archived SARAH
expressions** pass at four spectra (maximum absolute residual
`1.03e-13`): both lepton chiralities, neutral quarks, both charged orientations,
trilinears, photon/Z currents and WW couplings. Evidence and source hash are
in `external_2hdm_native_evidence.json`. This does not assert a fresh SARAH run.
Complex lepton rephasing, null LFV, removed-singlet independence, charged-mass
dependence and width conversion are checked by six bounded tests.

## Generic-potential discrepancy: retain FAIL

In the pinned [source](https://gitlab.com/jbrod/general-2hdm-pheno/-/blob/b5035cd58d2a7e4a91e9790d045df062b97adffe/thdm.py#L1510),
`cR_llpg_HW` at line 1510 and `cL_llpg_HW` at line 1791 contain
`vev**3 / MW**2 / sw**2 / ml(i)`, followed by `f11 / Mh_k**2`.
The corrected paper's v4 equations (65),(66), journal (5.18),(5.19), instead
contain `v**3 / sw**2 / mi`, followed by the same dimensionless f11/Mh_k².
The printed page and erratum were visually checked. The code's electron-EDM
HW expression at line 1224 also has no extra inverse MW².

For generic fixture A (`mH1=420`, `m12sq=57700`), dimensionless HW contributions are

```
                 cL                              cR
code     -4.678224473e-8 -3.957973496e-8 i    1.504965873e-8 +4.224589202e-8 i
paper    -3.021762638e-4 -2.556537529e-4 i    9.720888071e-5 +2.728750167e-4 i
```

Numerically `HW_code=HW_paper/MW²` for both chiralities, all six generic
channel witnesses. Rescaling all masses and v by two at fixed dimensionless
couplings leaves paper c_HW unchanged but makes source c_HW a quarter as
large. Thus the source HW term has mass dimension -2 inside a sum otherwise
defined as dimensionless. This is an implementation/paper inconsistency,
not a scalar rephasing or L/R-normalization adjustment. The harness stores
both complete sums and does not patch the reference or endorse either as a
new physical Zee prediction. Resolve f11 normalization with corrected
upstream code or an independent derivation before generic common-2HDM PASS.

For the other 12 terms the worst generic group relative residual is
`7.25e-13`. The frozen full one-loop result has small **retained nonzero**
differences: it includes finite internal-mass kernels and daughter chirality
masses absent from the author's leading-mass expansion (and electron internal
flip). We compare the author's truncation separately and do not change the
frozen result. Exact differing inputs and complex residuals are saved.

## Coherent overlap ledger and next work

| Published class | Frozen overlap / action |
|---|---|
| one loop | Frozen Module3 already included; compare common expansion, never add again |
| neutral fermion h, gamma+Z | gamma part for t,c,b,tau agrees with independent Module4 quadrature; Z part is new; author omits the other five charged species already kept by Module4 |
| t/c/tau charged-Higgs+W | new to frozen coherent ledger; strict-limit common only; extend mixed charged states/F before use |
| hZ plus kinetic | new complete published 2HDM aggregate; never identify its uncompleted W inner kernel with a physical coefficient |
| potential HA | independent frozen charged-scalar/photon agrees, including sign and f9=-2 F2; already included |
| potential HZ, HW | new beyond photon subset; HW source inconsistency above; Zee mixed-current extensions remain |

The observer captures the 13 actual local terms without rewriting the source.
Only the combinations identified in paper Eq.(53) as gauge invariant are
eligible for a future coherent ledger; individual diagnostic locals are not
new gauge-independent W observables. Setting only neutral-fermion Z vector
currents to zero isolates its known photon overlap; it is never used to
manufacture a gauge-independent W-only output.

[Zee inventory](ZEE_EXTENSION_INVENTORY.md) and the machine-readable
`external_2hdm_inventory.json` classify all previous 26 inner diagrams, six
parent audit categories and additional singlet classes. Preserve the eight
computed W/G parent subloops as tensor/identity evidence. The immediate next
step is the HW source discrepancy, then a mixed-charged-current ST-complete
remainder; no further independent outer integration is prioritized here.
All previous D15/D16 evidence and frozen physics modules remain unchanged.
`matching.py` still returns null physical C_L,C_R and coherent_inclusion=false.
