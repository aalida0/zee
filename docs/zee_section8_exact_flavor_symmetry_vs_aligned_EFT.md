# Section 8 flavor-consistency decision and P2 BFB correction (2026-10-18)

## Source-level problem

Florentino, Romão, Silva EPJC 81 (2021) 1148, Section 8:
the original Zee–Wolfenstein lepton-sector Z2 Yukawas yield the
disfavored zero-diagonal neutrino mass texture. Taking unrestricted
leptonic Y1,Y2 permits neutrino data but breaks the exact original
Z2 that their Type-II quark construction appealed to to forbid
neutral quark FCNC. Merely setting a Type-II-like quark Yukawa
texture at one scale is an aligned phenomenological ansatz, not a
proof of a common exact symmetry or RG stability.

**Additional scalar-level Z2 observation** based on Eq. (17):
if phi1 is even and phi2 odd, the mixed singlet quartic
`-k12*(phi1^dag phi2 + h.c.) chi^+chi^-` is Z2-ODD for
either charge choice for chi. A strictly exact Z2 at the
dimension-four level therefore requires **k12=0**. The
`m12sq*(phi1^dag phi2+h.c.)` term is soft breaking;
`mu4 phi1^T i sigma2 phi2 chi^-` may be Z2 invariant when
chi is odd. The nonzero Table 2 P2 k12=0.01267 GeV^0
is incompatible with a claim that an exact Z2 symmetry
enforces the full published scalar and quark Yukawa
Lagrangian as-is. lambda5 is Z2-even; lambda6=lambda7=0.

**Two scientifically distinct paths**:

### A. Exact family-dependent discrete Z2 at dimension four

Use the viable-flavor-texture method of Primulando, Julio,
Uttayarat EPJC 82 (2022) 253,
https://doi.org/10.1140/epjc/s10052-022-10189-0 .
As one **concrete hypothesis to test** set
`Z2(phi1)=+, Z2(phi2)=-, Z2(chi+)=-`;
`Z2(Q_L)=+,Z2(u_R)=-,Z2(d_R)=+`, giving
Type-II quark Yukawas;
`Z2(L_e)=-,Z2(L_mu)=Z2(L_tau)=+`,
`Z2(e_R)=Z2(mu_R)=Z2(tau_R)=+`.
This leaves the mu4 mixing term invariant, permits
neutrino-generating nonuniversal leptonic doublet Yukawas,
and forbids unwanted wrong-doublet quark Yukawas at
dimension four.

In that **symmetry flavor basis**, allowed f Yukawas
are f_{e mu}, f_{e tau}; f_{mu tau}=0 in this basis.
The allowed lepton Yukawa matrices have different ROW
textures: phi1 rows mu,tau; phi2 row e. They cannot
be enforced by directly zeroing arbitrary entries of the
B2 MASS-BASIS f/Y matrices: after charged-lepton mass
diagonalization, rotations mix f entries. Must implement
the symmetry-basis matrices, diagonalize M_ell,
translate to Higgs basis and the existing B2 convention,
and close the 1-loop neutrino matrix. Apply full LFV.

Enforce **k12=0** (and lambda6=lambda7=0) at the
exact Z2 dimension-4 level. Keep m12sq as a
soft breaking spurion; beta and scalar masses must be
re-screened. This is a stricter subset of the
2021 restricted scalar *functional form*, not a
reproduction of Table 2 P2 with k12=0.01267.
Other flavor charge assignments or symmetry groups may
allow alternative texture solutions and scalar-potential
constraints, but require an explicit operator/charge audit.

Important known phenomenological caveat:
the specific Primulando/Julio/Uttayarat 2022 texture
selects quasidegenerate neutrinos sum~0.10–0.13 eV
and tanbeta ≲0.5 or ≳10 in its scan.
This is not automatically compatible with
old P2 tanbeta~5.6 or with every cosmological
mass-sum likelihood. Test rather than assume.

### B. Explicit aligned quark-Yukawa effective ansatz

Keep exact Florentino Eq17, including nonzero k12,
and fully general Zee lepton Yukawas. Define
Type-II `rho^u=cotbeta*kappa^u`,
`rho^d=-tanbeta*kappa^d` at a fixed matching
scale and document it as a **boundary condition**,
not an exact protecting symmetry. Derive and test
1-loop RGE-induced wrong-doublet quark Yukawas,
neutral FCNC operators, beta/lambda running and
the finite validity range (e.g. 1–10 TeV);
confront CKM meson mixing/rare decays. References:
Pich & Tuzon Phys Rev D 80 091702 (2009)
https://doi.org/10.1103/PhysRevD.80.091702
and Braeuninger, Ibarra, Simonetto Phys Lett B
692 189 (2010), DOI 10.1016/j.physletb.2010.07.039.
Only when all induced quark flavor effects are shown
small can this be used as a consistent **low-energy
phenomenology assumption**. This is the least invasive
extension of existing A1V and B2 code, but it is NOT
an exact symmetry completion and must not be marketed
as one.

**Decision rule:** for a flagship HL-LHC
*fully constrained Zee interpretation* prefer Path A
(or independently validated alternative UV completion)
if it admits neutrino/LFV-compatible masses and a useful
HL-LHC rate. Path B is a defensible effective-model
fallback provided RGE stability and induced FCNCs
are quantitatively constrained. Do not combine arbitrary
B2 Yukawas with an exact Type-II Z2 statement.

## Important independent BFB correction for Table 2 P2

Our previous P2 pilot chose alpha=beta=1.398 and
mH1=300,mH2=700 GeV, m12sq=58000 GeV²,
k1=1.082, k2=.00398,k12=.01267.
This particular point has **lambda1 ~-2.56798**,
which violates even the necessary lambda1>=0
BFB condition: it is genuinely quartic unbounded
in the phi1-only direction. This is **not** just
overstrictness of the original Gate6 sufficient
global quartic screen. Mass reconstruction passes,
unitarity passes, but BFB fails.

The paper's Table 2 says beta varies in
`alpha*(1±.01)`, NOT beta=alpha.
At beta=1.394 (allowed within the source interval)
the same other inputs give
lambda1~+1.6369, lambda2~+.2514,
and satisfy the **ordinary 2HDM neutral quartic
BFB**. In addition, the singlet quartic sector is
certified nonnegative by a **less conservative
analytic sufficient BFB condition**:

If x1=|phi1|²,x2=|phi2|²,xc=|chi|²,
|Re(phi1^dag phi2)|<=sqrt(x1*x2).
Then `xc*(k1*x1+k2*x2-2*k12*Re(phi1^dag phi2))`
is >=0 whenever k1>=0, k2>=0,
and `k12²<=k1*k2`.
At the P2 table inputs,
k1*k2-k12²~0.0041458311>0.
Combined with lambda_c>=0 and
the standard exact 2HDM BFB conditions,
this **certifies global large-field quartic BFB**
at beta=1.394. It does not prove the chosen
EW vacuum is the deepest charge-preserving
stationary point: a separate multi-start
charge-breaking-vacuum check is still needed.

Existing Gate6 BFB uses stronger
`k2>=abs(k12)` and so *still* reports false
at this beta. Do not silently rewrite Gate6
or confuse its stricter filter with a failed
necessary condition. The reproduction driver now
separately reports `ALTERNATIVE_ANALYTIC_BFB_SUFFICIENT`
and `LAMBDA1`. Its regression tests
specifically verify the beta=alpha necessary
failure and beta=1.394 alternative sufficient
quartic certificate.

## AF next

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_reproduce_florentino_2021_regions.py' -v
python3 scripts/zee_reproduce_florentino_2021_regions.py \
  --benchmark P2 --mH1 300 --mH2 700 --beta 1.394 \
  --output work/florentino2021_P2_beta1394_BFB_audit_v1.json
```

**Future gate before calling physics points allowed:**
For Path A freeze allowed operators in gauge flavor basis
and numerically verify symmetry, charged-lepton
mass diagonalization, PMNS/oscillation likelihood,
full LFV and the modern two-state b->s gamma
at matched quark TypeII. For Path B validate
the one-loop RGE-induced quark misalignment and
FCNC, plus all other full model constraints.

No physical "allowed point" status has been obtained.


## Patch: source key mismatch in P2 quartic BFB audit (2026-10-18)

First AF test of the alternate analytic BFB helper found 3 of 8
P2 tests failing with `KeyError: 'lc'`.
This was a **code-level field-name typo**:
`gate6_benchmark.benchmark(... )["inputs"]` serializes the
singlet self-coupling under `"lambda_c"`, not `"lc"`.
The source call accepts the keyword `lc`; its output schema
uses the different full name. Corrected the helper to read
`("k1","k2","k12","lambda_c")` in commit `f79114e3`.
Four independent family-Z2 operator tests had already
PASSED; no issue with their charge rules was indicated.

Manual independent arithmetic cross-check for published
Table-2 P2 with mH1=300, mH2=700, alpha=1.398,
m12sq=58000, k1=1.082,k2=.00398,k12=.01267:
- beta=1.398: lambda1 ~ -2.56798150: **necessarily
  unbounded quartic**, despite mass eigenvalue closure.
- beta=1.394: lambda1 ~ +1.63690503,
  lambda2 ~ +0.25140194, lambda3 ~ +2.61651365,
  lambda4 ~ -1.18196052, lambda5 ~ -1.09819999;
  neutral quartic BFB margins 3.2580,0.97785 >0;
  singlet cross-PSD determinant 0.0041458311 >0;
  **alternative sufficient quartic BFB PASS**,
  original stronger `Gate6` sufficient-BFB screen
  still reports False because k2 < |k12|.
- No global-minimum or modern-2026 experimental
  verdict follows from these tests.

Re-run P2 tests and the beta=1.394 reproduction after
`git pull --ff-only`. Do not confuse independent
arithmetical checks with executing repository regression
tests on AF, which the user must still perform.


## AF outcome: actual beta=1.394 P2 source-region pilot and branching fractions (2026-10-18)

User ran the corrected Florentino Table2 P2 representative
at alpha=1.398, beta=1.394, gamma=1.089, mH1=300,
mH2=700, mh2=580.7, ma=633.7,
m12sq=58000 GeV^2, k1=1.082,k2=0.00398,
k12=+0.01267, lambda_c=4.473.

Actual AF output:
```
MASS_RECONSTRUCTION PASS
OLD_STRONGER_SUFFICIENT_BFB False
ALTERNATIVE_ANALYTIC_BFB_SUFFICIENT True
LAMBDA1 1.6369050315668792
TREE_UNITARITY True
MAX_UNITARITY_EIGENVALUE 18.083873017299958
BR_H2_H1Z_INCLUDED_ONLY 0.7608003869543065
BR_H1_tb_INCLUDED_ONLY 0.9559329373337353
HISTORICAL_ALLOWED_REPRODUCED False
```
Thus the prior beta=alpha point's necessary BFB
failure was solved by choosing beta inside the published
allowed *range*, and an independent analytically sufficient
BFB proves the quartic boundedness at this chosen
representative, even though the older more restrictive
Gate6 sufficient screen remains false.
No claim about global charge-breaking vacuum,
experiment 2026, full physical BRs, or
a historically published single parameter point.

**Section 8 decision update:** This P2 point has
tanbeta=tan(1.394)~5.597, and nonzero hard-Z2
k12=0.01267. It CANNOT be treated as
an exact family-dependent-Z2 benchmark using the
specific Primulando/Julio/Uttayarat 2022 flavor
texture: that construction requires k12=0
in dimension-4 scalar quartics, and the *published*
neutrino-fit scan favored tanbeta≲0.5 or ≳10,
with the small-tanbeta branch LFV excluded.
Reference https://doi.org/10.1140/epjc/s10052-022-10189-0 .
This is a warning about their specific fitted texture,
not a theorem excluding every family-dependent Z2
or every general Zee model at tanbeta~5.6.

We added a provenance-tagged `--k12 0` override
to the literature P2 scalar reproduction driver.
This defines a NEW scalar point with dimension-4
quartic hard Z2 breaking removed; it does NOT
reproduce the original published P2 values.
At beta=1.394, k12=0, the ordinary Gate6
sufficient BFB will pass because k1,k2>0 and
the neutral BFB margins already passed;
this still does NOT make tanbeta5.6 a confirmed
family-Z2 neutrino/LFV fit or a global vacuum minimum.

Immediate AF test:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_reproduce_florentino_2021_regions.py' -v
python3 scripts/zee_reproduce_florentino_2021_regions.py \
  --benchmark P2 --mH1 300 --mH2 700 --beta 1.394 --k12 0 \
  --output work/florentino2021_P2_new_familyZ2_k120_scalar_v1.json
```

For symmetry-constrained neutrino fit the 2022 paper
uses in the FAMILY charge basis
`M_ell = v/sqrt(2) [[Y_e sinβ, Y_mu sinβ,
Y_tau sinβ],[0,Y_mumu cosβ,0],[0,0,Y_tautau cosβ]]`.
The antisymmetric f has only f_{e mu} and f_{e tau}
before lepton mass-basis rotation. With
`U_L^dag M_ell U_R=diag(mell)`,
`fhat=U_L^T f U_L` and
`Yhat=U_L^dag diag(-cotβ,tanβ,tanβ)
M_ell U_R/v` in the cited 2022 convention.
Do **NOT** naively apply this texture to B2's
already diagonal-mell mass basis. The 2022 one-loop
`Mnu=kappa2022*(fhat Mdiag Yhat^T +
 (fhat Mdiag Yhat^T)^T)`
has `kappa2022=sin(2gamma)*ln(m1²/m2²)/(16pi²)`.
Our Chen-based B2 uses
`kappaB2=sqrt(2)*kappa2022`; before comparing
numerically, match the coupling normalization
(and if same f conventions, define
`YB2 = Yhat^T/sqrt(2)`) with independent
one-loop benchmark checks.

A high-tanbeta (>=10) symmetry-compatible
scalar scan cannot just reuse the published
m12sq=58000 GeV². For any CP-even potential
in the repo conventions,
`lambda1 = [mh² cos²(alpha)+mH² sin²(alpha)
             -m12sq*tanbeta]/[v² cos²(beta)]`.
At alpha=1.398, mH=580.7 GeV, positivity
requires roughly
`m12sq < 32770.55 GeV²`
already at tanbeta=10, whereas the
P2 table has 58000 GeV². Accordingly
scan alpha,beta and m12sq together
when extending the family-Z2 model into
the flavor-favored tanbeta>10 region;
fixed-P2 parameters cannot do the job.

## AF gate: source-inspired P2 k12=0 *quartic* variant confirmed (2026-10-18)

User confirms:

```
SOURCE P2
alpha=1.398, beta=1.394, gamma=1.089,
k1=1.082, k12=0, k2=.00398, lc=4.473,
m12sq=58000 GeV^2, mH1=300, mH2=700,
ma=633.7, mh2=580.7, mh1=125
K12_SOURCE_OVERRIDDEN True
MASS_RECONSTRUCTION PASS
OLD_STRONGER_SUFFICIENT_BFB True
ALTERNATIVE_ANALYTIC_BFB_SUFFICIENT True
LAMBDA1 1.6369050315668792
TREE_UNITARITY True
MAX_UNITARITY_EIGENVALUE 18.083843117923735
BR_H2_H1Z_INCLUDED_ONLY 0.7606635666057693
BR_H1_tb_INCLUDED_ONLY 0.9559329373337353
HISTORICAL_ALLOWED_REPRODUCED False
```

At the quartic level the symmetry-compatible k12=0
scalar point now satisfies both the existing and new
sufficient BFB checks, and mass/unitarity close. The
nearby nonzero-k12 historical representative had
BR_H2_H1Z=0.76080038695 and same BR_H1_tb, so
switching k12 to zero has **not reduced the
included-channel gauge cascade rate materially**.

**NEXT physics step, now implemented:**
`scripts/zee_section8_family_z2_neutrino_texture_pilot.py`
is a new independent, source-faithful realization
of Primulando et al. EPJC 82 (2022) 253
Eqs. (1)-(2),(8)-(10),(13),(17), and
`tests/test_zee_section8_family_z2_neutrino_texture_pilot.py`
tests its charged-lepton mass, symmetry-texture,
biorthogonal rotation and Majorana symmetry.
Source: https://doi.org/10.1140/epjc/s10052-022-10189-0 .

It constructs in the charge basis
`M_l=[[a,b,c],[0,d,0],[0,0,e]]`,
`f=[[0,1,r exp(i theta)],[-1,0,0],
[-r exp(i theta),0,0]]`.
Choose `m_e < d < m_mu < e < m_tau` and
derive b² and c² from the minor-eigenvalue
characteristic polynomial, `a=me*m_mu*m_tau/(d*e)`.
This exactly reproduces all THREE charged-lepton
masses and reduces the continuous charged-lepton
texture to two parameters d,e.
Use SVD `O_L^T M_l O_R=diag(ml)`, then
`fhat=O_L^T f O_L`,
`Yhat=O_L^T diag(-cotbeta,tanbeta,tanbeta) M_l O_R/v`,
`Mnu=kappa2022*(fhat*diag_ml*Yhat^T +
Yhat*diag_ml*fhat^T)`,
`kappa2022=sin(2 gamma) ln(m1²/m2²)/(16π²)`.
This is NOT just an unrestricted complex
f,Y B2 solution: both textures come from
the symmetry basis with exact zero entries.

The pilot's differential-evolution option optimizes
a transparent, fixed **illustrative target proxy**
using the old A1B central input values for
sin²theta12,13,23, Δmsol²/Δmatm², J_CP,
not the full NuFIT likelihood. Score weights are
non-physical arbitrary denominators; never
call the reported numerical score a χ²/CL.
It does not compute LFV, vacuum, HiggsTools,
modern flavor or exclusion. Also do NOT pass
the 2022 Yhat directly into the Chen-based
B2/B3 lepton-width code without checking
normalization, transpose and conjugation.

AF first run:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_section8_family_z2_neutrino_texture_pilot.py' -v
python3 scripts/zee_section8_family_z2_neutrino_texture_pilot.py \
  --tanbeta 5.597170833164245 --ordering NO \
  --mH1 300 --mH2 700 --gamma 1.089 \
  --maxiter 65 --popsize 10 --seed 20261018 \
  --output work/zee_section8_familyZ2_P2_tanb5597_NO_proxy_v1.json
```

For comparison a second optional **lepton-only
counterfactual** scan at `--tanbeta 10` can
test the literature-preferred high-tanbeta lepton
texture. That does NOT constitute a valid scalar
benchmark at alpha1.398/m12sq58000: the original
P2 scalar inputs fail lambda1 positivity at
tanbeta10, so those must be re-screened with
different m12sq/neutral parameters BEFORE
any combined model claim.

After the algebraic texture has passed its
regression tests: match 2022 and Chen Yukawa
conventions, connect correct mass-basis f/Y
to the physical LFV backend, then implement
a real source-pinned NuFIT 6.1 likelihood
over both orderings, phases and charged-lepton
texture parameters, with current cosmological
neutrino sum considered as independent
data-dependent consistency check.

Stop if constrained full leptonic fit cannot
find any physically supported high-tanbeta
textures in the scalar+quark flavor viable
region. No count of 2026 allowed Zee points
has been obtained.

## Actual AF P2-inspired family-Z2 NO neutrino pilot (2026-10-18)

User ran exact charged-lepton diagonalization and source-
equation family-Z2 neutrino texture exploratory optimizer
at mH1=300,mH2=700,gamma=1.089,tanbeta=5.59717, NO:
```
CHARGED_MASS_CLOSURE_GEV 4.163336342344337e-17
PROXY_SCORE_NOT_CHISQUARE 66.5772884474936
sin2theta12 0.2970336121
sin2theta13 0.02271851853
sin2theta23 0.88101259875
mass_ratio 0.03266106465
J_CP -0.01782342843
masses_eV (0.00055479,0.00911433,0.05034191)
sum_masses_eV 0.0600110
f_e_mu_to_match_atm_abs 3.3226990e-7
COMPLETE_NUFIT_LIKELIHOOD False
COMPLETE_LFV False
PHYSICAL_ALLOWED False
```

**Interpretation:** charged-lepton masses close essentially
exactly. But sin²theta23=0.881 is far outside NuFIT 6.1
(2025) NO 3-sigma range 0.432–0.587
(using NuFIT 6.1 IC23 without SK atmospheric table).
The old A1B target 0.561 is NOT a full NuFIT likelihood.
The mass sum near 0.060 eV is irrelevant as an
“allowed solution” because oscillation mixing fails.
Proxy score 66.58 is NOT a chi²; one optimizer seed
is NOT a proof of absence of solutions.

**Crucial independent literature check:** Primulando,
Julio, Uttayarat EPJC 82 (2022) 253 Sect 3
[https://doi.org/10.1140/epjc/s10052-022-10189-0]
explicitly fitted 5 oscillation observables in NO
and IO, concluding **quasidegenerate** neutrinos
(sum 0.10–0.13 eV) with the cosmology assumptions
of that date; their surviving fits were IO, with
tanbeta around <0.5 or >10, low tanbeta
further LFV disfavored.
The current hierarchical NO output does not
contradict the paper because its theta23 is badly
incompatible with oscillation data. The source
equations 8,9,10,13,17,20,21 agree with the
implemented symmetry-basis f, charged lepton
texture, Yhat transpose and mixing formulas.

**NEW modern cosmology tension:** DESI DR2
(+Planck/ACT) Phys Rev D 112 (2025) 083513,
DOI 10.1103/w9pk-xsk7 finds
sum mnu <0.0642 eV at 95% under selected
LambdaCDM and neutrino assumptions.
DESI DR2 changing-dark-energy model w0wa
instead reports <0.16 eV.
A 2026 analysis using other CMB data gives
limits 0.082,0.11,0.138 eV according
to combinations (Phys Lett B 879 (2026)
140659 DOI 10.1016/j.physletb.2026.140659).
Therefore even if we reproduce 2022's
quasidegenerate IO/high-tanbeta solutions,
some modern ΛCDM cosmological likelihoods
press them strongly. Do NOT declare
model excluded in all cosmologies; name
the dataset and model assumptions.

**Next minimal physics question:** independently
reproduce the *qualitative* 2022 IO high-tanbeta
fit with multiple seeds, WITHOUT claiming
these high-tanbeta lepton-only settings
pass the original P2 scalar potential.

New `scripts/zee_section8_family_z2_neutrino_grid.py`
reuses the exact symmetry-basis family textures
and loops over tanbeta (default 5.597,10,15,20),
NO and IO, 3 independent optimizer seeds each
(24 optimizations). It writes
`grid_NOT_NUFIT.csv` plus `summary.json`
and prints sin²theta23, sum mnu, texture ratio
and proxy score. All runs are **lepton-only
counterfactuals** at high tanbeta until the
neutral scalar m12sq and alpha/beta etc are
re-screened. Its residual uses arbitrary
fixed target scales, NOT a NuFIT likelihood.
It does not use B2's unrestricted Yukawa
fit, and no physical allowed claims follow.

AF commands:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_section8_family_z2_neutrino_grid.py' -v
python3 scripts/zee_section8_family_z2_neutrino_grid.py \
  --tanbetas 5.597170833164245,10,15,20 \
  --orderings NO,IO \
  --seeds 20261018,20261019,20261020 \
  --mH1 300 --mH2 700 --gamma 1.089 \
  --maxiter 65 --popsize 10 \
  --output-dir work/zee_section8_familyZ2_neutrino_ordering_grid_v1
```

**Decision**: if multiple high-tanbeta IO seeds
yield low *proxy* mismatch, correct mixing,
and ~0.10–0.13 eV sum, that supports
source-equation reproduction ONLY. Then do
NuFIT 6.1 correlated data, current cosmological
dataset variants, full LFV and separate scalar
potential scan before generating a model-complete
benchmark. If no seeds reproduce published
results, audit search bounds, mass basis phase
conventions, charged lepton texture, PMNS
ordering and local/global optimizer convergence.
Do not infer mathematical no-go from a
restricted finite numerical scan.

## Gate result: 24-run NO/IO lepton-only multi-seed pilot (2026-10-18)

The user ran `zee_section8_family_z2_neutrino_grid.py`
with tanbeta=[5.59717,10,15,20], 3 seeds each and
both orderings; 24 jobs finished. Best rows:

| tanbeta | NO proxy (not chi²) | IO proxy (not chi²) | IO sin²theta23 | IO Σmν [eV] |
|---|---:|---:|---:|---:|
| 5.597 | 66.5773 | 14.1633 | 0.49835 | 0.09984 |
| 10 | 67.4894 | 13.4737 | 0.49949 | 0.09986 |
| 15 | 67.4917 | 13.3276 | 0.49982 | 0.09987 |
| 20 | 67.4925 | 13.2793 | 0.49994 | 0.09987 |

Each IO slice converged to essentially the same
best minimum in all 3 seeds; NO at tanbeta=15
also had one much worse local solution. The
IO minimum-near Σmν≈0.100 eV is **NOT by itself**
the fully viable published 2022 quasi-degenerate
solution, and the diagnostic threshold
`m_lightest/m_heaviest>=0.5` in the old grid
is *stricter than the source definition*:
the paper Eq/paragraph around Fig 2 reports
`2 <= m1/m3 <= 15` for IO,
including a lightest/heaviest ratio down to ~0.067.
Do not call the old quasidegenerate boolean a
paper compatibility test.

**Reason to change the objective, not merely more seeds:**
the old A1B-proxy input fixed
sin²theta23=.561, sin²theta13=.02195,
sin²theta12=.307, J≈-.0287 (old NO δ=240°),
R=7.49e-5/2.534e-3≈.02956, and chose
arbitrary proxy residual scales.
Primulando et al. EPJC 82 (2022) 253
**Table 1 IO upper octant** instead specifies:
```
sin²theta12 = .304 ±.013
sin²theta23 = .575 ±.018
sin²theta13 = .02238 ±.00063
R=Δm_sol²/Δm_atm² = .0297 ±.0034
J_CP = -.0327 (+.0066,-.0008)
```
(source Table 1,
https://link.springer.com/content/pdf/10.1140/epjc/s10052-022-10189-0.pdf).
The strongly asymmetric J IO measurement cannot
be replaced with the previous arbitrary fixed
CP weight if attempting to reproduce the source.

New script:
`scripts/zee_section8_reproduce_2022_IO_table1.py`
+ `tests/test_zee_section8_reproduce_2022_IO_table1.py`
uses the **actual 2022 IO upper-octant** Table1
central values and separate plus/minus 1σ widths,
wider bounded DE optimization in x,y,log10(r),theta,
and records full candidate texture parameters,
per-observable residuals, physical IO m1/m3,
and 2%-near-search-boundary flags. The
score is the sum of five separately standardized
squared marginal residuals; it is **NOT a
correlated experimental χ²**, and does not use
NuFIT2025/2026 data, LFV, constraints, or
physically screened high tanbeta scalar potential.

AF source-reproduction run:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_section8_reproduce_2022_IO_table1.py' -v
python3 scripts/zee_section8_reproduce_2022_IO_table1.py \
  --tanbetas 5.597170833164245,10,15,20 \
  --seeds 20261018,20261019,20261020 \
  --mH1 300 --mH2 700 --gamma 1.089 \
  --maxiter 90 --popsize 12 \
  --output-dir work/zee_section8_repro_2022_IO_Table1_v1
```

If this *source-matched* scan cannot find
a small per-observable residual combination,
inspect fitted d,e,r,phase, whether x,y or
log10r are at numerical boundaries, objective
scales and ordering/CP sign conventions.
2022 published fits from Fig2 may also be
in different first/second θ23 octants; this
script explicitly targets **upper octant only**.
Do not reject all possible family-Z2 textures
on a finite upper-octant scan.

Only after source reproduction should we switch
to a genuine NuFIT 6.1 likelihood with both
octants/orderings, modern cosmological choices,
matching 2022 vs Chen model Yukawa
normalizations, full LFV, and scalar re-screening.


## Crucial correction: 12 source-matched IO scans were fitted to central values, not source-accepted 2σ windows (2026-10-18)

Actual AF `zee_section8_reproduce_2022_IO_table1.py` ran
12 source Table1 upper-octant IO proxy optimizations,
3 seeds at tanbeta=[5.59717,10,15,20].
At tanbeta=5.597,10,15,20 respective best
`SCORE_DIAG` = 43.91267,43.93816,43.94472,
43.94702, uniformly far from central targets.
All converged to a near-rank-2 IO neutrino
matrix, Σmν≈0.09994–0.09995 eV and enormously
large `m1/m3` ≈ 7907.7,22811.9,44229.1,
65950.5 respectively, far outside the
paper's observed `2≲m1/m3≲15`.
For representative tanbeta5.597: sin²theta23
=.54106,J_CP=-.01126, with standardized
source residuals: sin²theta12 +5.399,
J_CP +3.249, sin²theta23 -1.886,
sin²theta13 +.787, mass ratio -.175.
**Not a reproduction**, even qualitatively
with respect to published mass ratio.

**Found two defects in the reproduction METHOD,
not yet established as physics-model defects:**

1. Paper Section 3 *accepted* points where
   **each of five neutrino observables is in
   its 2σ range**, plus source historical
   `Σmν<0.13 eV` (Planck+BAO) and reported
   `2≲m1/m3≲15`. The earlier reproduction
   script instead globally minimizes a sum
   of all central-value squared residuals,
   which can select a source-excluded near-rank2
   basin over narrow source-accepted regions.
2. The charged lepton coordinate
   `e=m_mu+(m_tau-m_mu)*expit(y)` had
   y bounded `[-12,12]`, excluding
   proximity to m_tau reached around
   `y≈14.3` by an independent numerical
   optimization. The old report's
   `AT_BOUNDARY False` does not test
   *missing regions outside the box*.

**Independent exploratory numerical validation,
not executed on AF:** Directly optimizing
the source 2σ **violation**, broadening
x,y to [-25,25], and including the
IO mass-ratio observed range penalty,
I obtained best source-style residual penalty
~0.0208 with at tanbeta=5.6,10,15,20,
`sin²theta12≈0.330, sin²theta23≈0.612,
sin²theta13≈0.02112,J≈-0.02658,
R≈0.02290, m1/m3≈1.86` in one
exploratory branch. This lies close to
some source 2σ edges but **does not reproduce
the paper**: m1/m3 is still below 2,
and the corresponding Σmν can exceed the
paper's 0.13 eV historical bound. This
numerical result is only evidence the
old minimizer misdiagnosed feasibility;
it is NOT a source 2σ+cosmology pass.

**New corrected gate:**
`scripts/zee_section8_2022_2sigma_acceptance.py`
plus `tests/test_zee_section8_2022_2sigma_acceptance.py`.
- uses five separate two-sigma marginal
  acceptance windows as in the 2022
  paper, with the asymmetric J_CP errors.
- expands logistic x,y from ±12 to ±22
  and log10(r) from ±4 to ±5.
- separately records IO m1/m3 in the
  descriptive paper range 2..15 and
  historical Σmν<0.13 eV; uses both
  as optimization penalties to find
  source-qualitatively representative
  points. These are NOT independent modern
  experiment-exclusion tests.
- prints each five-observable 2σ result,
  physical ratio, sum masses,
  near-tau charged texture gap and
  charges SVD mass closure; no physical
  Zee-allowed assertion or NuFIT 6.1 fit.

**AF commands:**

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_section8_2022_2sigma_acceptance.py' -v
python3 scripts/zee_section8_2022_2sigma_acceptance.py \
  --tanbetas 10,15,20 \
  --seeds 20261018,20261019,20261020 \
  --mH1 300 --mH2 700 --gamma 1.089 \
  --maxiter 145 --popsize 18 \
  --output-dir work/zee_section8_2022_source_2sigma_gate_v1
```

If a source-style historical fit is found,
**do not promote to physical benchmark**:
the scalar potential at tanbeta10–20
is unvalidated (published P2 m12sq58000
would violate lambda1>0), NuFIT 6.1
likelihood/full LFV/current neutrino
cosmology plus modern two-state b→sγ
remain missing. If no source fit found,
the 2022 paper also explicitly accepts
FIRST-octant theta23; current gate only
tests the Table1 UPPER octant. It may
be necessary to implement the separately
quoted first-octant reference and audit
search quality, parameterization
conditioning near e≈m_tau.


## Nine-job source-upper-octant 2sigma gate FAILED; independent first-octant candidate identified (2026-10-18)

The user completed `scripts/zee_section8_2022_2sigma_acceptance.py` on AF:
tanbeta=10/15/20 × 3 seeds = 9.
**0/9 upper-octant SOURCE_STYLE passes.**
Every slice found similar local minimum
`VIOLATION≈2.1432–2.1437` (not χ²),
Σmν≈0.14135 eV > historical 0.13 eV
bound, IO m1/m3≈2.058.
At tanbeta=15:
sin²theta12=.330022,
sin²theta13=.0210624,
sin²theta23=.627555,
J_CP=-.0238658,
Δmsol²/Δmatm²=.0365402.
Against 2022 upper-octant Table1 source
the residuals are roughly
`(+2.002,-2.091,+2.920,+1.339,+2.012)`
in (s12,s13,s23,J,ratio).
The charged texture's `e` variable sits very
close to m_tau (MTAU-e≈9e-7 GeV).
These are not accepted upper-octant or
cosmology-compatible historical points.
They do NOT exclude the family-dependent
Z2 model because the 2022 paper explicitly
allows a separate **first octant**,
which our preceding scripts did not search.

**Independent numeric cross-check (not source-likelihood-certified):**
Using an independent small matrix/SVD/eigensolver
in the isolated Python runtime and SciPy DE at
tanbeta=15, setting a provisional *first-octant
exploratory* `0.43<=sin²theta23<=0.49`
window while retaining each of the OTHER
FOUR 2022 Table1 IO 2sigma requirements
and historical Σmν<0.13, found a candidate:
```
tanbeta = 15
logistic-coordinate witness (x,y,log10r,phase)
 = (-3.8318906,-8.45647671,-0.62476731,-3.1167578)
d_GeV ≈ 0.002741073843
e_GeV ≈ 0.106013463006 (just ABOVE m_mu)
r ≈ 0.23726446
sin²theta12 = 0.3181898745  (2022 IO residual +1.0915σ)
sin²theta13 = 0.0211307363  (2022 IO residual -1.9830σ)
sin²theta23 = 0.4364576483  (FIRST octant; exploratory window only)
J_CP        = -0.0198756174 (2022 IO residual +1.9431σ)
R           = 0.0364999668  (2022 IO residual +1.99999σ)
m1_eV       = 0.04974863
m2_eV       = 0.05066968
m3_eV       = 0.00578073
sum_mnu_eV  = 0.1061990453  (< historical .13)
m1/m3       = 8.60593686   (within published 2..15)
```
This witness passes **four** published
Table1 IO marginal 2sigma intervals plus a
*PROVISIONAL* first-octant window,
the 2022 historical cosmological threshold,
and the 2..15 observed mass ratio.
It is NOT a mathematically certified or
experimentally source-accepted **five**
observable fit, since source Table1 quotes
the **UPPER** octant's numerical 1sigma
central value; it does not tabulate
the first-octant likelihood. Must retrieve
original NuFIT5.0 theta23 first-octant
profile or construct a valid current NuFIT6.1
likelihood to decide physical oscillation pass.
Independent runs with a narrower exploratory
first-octant .43-.49 window also found
numerical-violation=0 branches at tanbeta
15 and 20, showing that the best-fit
upper octant's failure is not a universal
texture no-go.

**Crucial difference:** Old upper-octant
optimizers saturated e≈m_tau.
The new first-octant witness has
e≈0.106013 GeV just ABOVE m_mu, in a
distinct charged-lepton texture basin.
No hard zero in f,Y was changed and no
unrestricted B2 Yukawa parameters were added.

New reproducible script:
`scripts/zee_section8_IO_first_octant_witness.py`
plus
`tests/test_zee_section8_IO_first_octant_witness.py`.
The deterministic witness test is the
immediate next cheap AF gate and does
**NOT** require another optimizer run:

```bash
cd /home/aalida/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_section8_IO_first_octant_witness.py' -v
python3 scripts/zee_section8_IO_first_octant_witness.py \
  --witness-only \
  --output work/zee_section8_IO_first_octant_witness_v1.json
```

After successful witness reproducibility, NEXT
gate is a genuinely source-pinned NuFIT5.0
first-octant likelihood/profile or current
NuFIT6.1, not more upper-octant optimizing.
Modern cosmological interpretation of IO
Σmν~0.106 eV requires a specified dataset
and cosmological model; source 2022 .13 eV
bound is historical only.
All high-tanbeta scalar-potential constraints
are NOT_EVALUATED: the original 2021 P2
scalar point with m12sq=58000 and beta=1.394
cannot simply be replaced by tanbeta15.

No fully allowed Zee benchmarks yet.
