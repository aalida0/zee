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
