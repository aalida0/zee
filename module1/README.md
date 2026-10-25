# Module 1 scalar interface 1.0.0

Run from the repository root:

```sh
python3 -m module1.scalar_constraints --input module1/example.json
python3 -m module1.scalar_constraints --jsonl --input points.jsonl --output results.jsonl
bash scripts/run_module1_validation.sh
```

Python API: `from module1.scalar_constraints import evaluate`; `evaluate(input_dict)`
returns the same versioned object as the CLI. `input.schema.json` and
`output.schema.json` freeze the input and output contracts. Every physical input is mandatory; no benchmark defaults are
silently inserted. JSONL preserves order and emits one result per line, including
errors. Duplicate keys, nonfinite numbers, unknown fields/operators, wrong units,
and unsupported versions are rejected. CLI exit 2 means an input/evaluation error;
physics FAIL/UNKNOWN results remain valid results and exit 0. No status is an
overall phenomenological acceptance. Consumers must inspect each gate's
`assessment` (`PASS`, `FAIL`, `UNKNOWN`). New incompatible contracts require a new
major version. Numerical tolerances and algorithms are part of this version.

`physical` uses Gate6 names: `mh1,mh2,ma,mH1,mH2` are positive ordered light/heavy
CP-even, CP-odd and charged masses in GeV; `v` is in GeV; `alpha,beta,gamma` are
radians; `m12sq` is the signed soft mass **squared** in GeV²; `lc,k1,k2,k12` are
dimensionless singlet/portal quartics. Require `.01<beta<pi/2-.01`,
`-pi/2<=gamma<=pi/2`; alpha is any finite angle. These define a supported convention
chart rather than a statement about excluded physics outside that chart.
The exact gamma endpoints are the continuous zero-cubic limits of the inherited
inversion. Either sign of m12sq and nontrivial signed alpha/gamma are supported.
`electroweak` specifies MW, MZ, on-shell scheme and a fixed 125 GeV reference Higgs.
The scalar light mass itself can vary. Below-threshold real loop integrals are
supported; a crossed threshold is explicitly UNKNOWN, never PASS.
`ew_fit` selects one U-floating fit. Both fits are reported as alternatives;
their chi² values are never added. `search` optionally specifies >=64 starts per
full gauge chart per seed and exactly two independent deterministic seeds.

Output fields are `schema_version,benchmark_id,status,global_zee_acceptance,input,
provenance,warnings,lagrangian,gates`. `global_zee_acceptance` is always null.
Top status is `SCALAR_PIPELINE_FAIL` if any gate has a verified failure, otherwise
`SCALAR_PIPELINE_UNKNOWN` because finite vacuum sampling never proves stability.
An error record contains version, benchmark ID (when recoverable),
`INPUT_OR_EVALUATION_ERROR`, error text and null global acceptance. Unsupported or
nonconverged numerical gates contain `status=UNKNOWN, assessment=UNKNOWN, reason`.
`gates` has reconstruction, bfb, unitarity, vacuum and ewpo. Each successful gate
has explicit status, assessment and evidence; consumers should tolerate additive
diagnostic fields. `lagrangian.parameters` uses exact SARAH parameter names and
declared units. `provenance` includes actual implementation and frozen-source
SHA256, literature versions, fit snapshot and the requested Module 0 identity.

## Potential and mixing

This is the **restricted CP-conserving Zee scalar potential with complex lepton
Yukawas**, as frozen in SARAH Module 0. It is not the most general renormalizable
scalar potential. Lambda6/7 are absent; no RG closure or RG-stability claim is made.
Yukawas do not enter these scalar tree and scalar one-loop gates.

For x=H1†H1, y=H2†H2, z=H1†H2, s=S†S, the exact potential is

```
V2 = M112*x + M222*y - 2*M12Sq*Re(z) + MCS2*s
V3 = 2*Mu4*Re(conj(S)*(H1+*H20-H10*H2+))
V4 = Lambda1*x²/2 + Lambda2*y²/2 + Lambda3*x*y
     + Lambda4*abs(z)² + Lambda5*Re(z²) + LambdaC*s²
     + (K1*x + K2*y - 2*K12*Re(z))*s
```

The Lagrangian contains `-V`. The singlet quartic has no factor 1/2;
the K12 sign is negative. Each complex field is (r+i*im)/sqrt(2).
The canonical real order is H1+,H10,H2+,H20,S+, each real then imaginary.
Vacuum coordinates are r2=v cos(beta), r6=v sin(beta).
The output gives mixing **rows**, with mass eigenstates = Z*(gauge fields):

```
ZH = [[cos(alpha),sin(alpha)],[-sin(alpha),cos(alpha)]]
ZA = [[cos(beta),sin(beta)],[-sin(beta),cos(beta)]]
ZP = [[cb,sb,0],[-sb*cg,cb*cg,sg],[sb*sg,-cb*sg,cg]]
```

ZA/ZP first rows are Goldstones. Thus h has gauge strength cos(beta-alpha)
and charged doublet/singlet mixing mass is -Mu4*v/sqrt(2). The two tadpoles
fix M112/M222. The existing Gate6 inversion is reused, with signed/endpoint
gamma extension only. The full 10-field polynomial is differentiated independently
in SymPy tests, including CP-even/odd and both real/imaginary charged blocks.

## BFB decision semantics

All quartics and all neutral/charged complex orientations are covered by the
bound, including K12. Since |z|²<=xy and 2|z|<=x+y,

```
V4 >= Lambda1*x²/2 + Lambda2*y²/2 + LambdaC*s²
      + [Lambda3+min(0,Lambda4-abs(Lambda5))]*x*y
      + (K1-abs(K12))*x*s + (K2-abs(K12))*y*s.
```

Strict copositivity of this 3-variable lower form is sufficient, using the
[3x3 copositivity criterion](https://arxiv.org/abs/1205.3781v3).
An alternative certificate uses strict 2HDM positivity and a positive semidefinite
portal matrix. Inequalities are recomputed at 60 digits with a positive margin.
These are **sufficient, not necessary** certificates. Strict positivity makes the
full tree potential coercive despite cubic/quadratic terms. No certificate implies
UNKNOWN unless a negative witness is found. Marginal/flat quartic directions are
UNKNOWN because dimensionful terms may dominate there.

Witness searches span the complete compact Gram-orbit domain: x+y+s=1,
z=rho*sqrt(x*y)*exp(i*phase), 0<=rho<=1. Two seeded optimizations and pure-field
axes supply candidates. Every negative candidate is reconstructed in canonical
complex fields and substituted at 60 digits. Numerical absence is never proof.
The interface is not a complete necessary-and-sufficient BFB classifier.

## Unitarity and vacuum

The complete 55 symmetrized two-particle states of 10 canonical real fields
are used. The quartic fourth derivative T gives
`M(ij,kl)=Tijkl/sqrt((1+delta_ij)*(1+delta_kl))`.
For angle-independent high-energy contacts, a0=M/(16*pi) and the strict tree
bound is max|eigenvalue(M)|<8*pi. Dimensionful exchange and finite-energy poles
are outside this high-energy tree test. Pure O(4) doublet eigenvalues are
3*Lambda and Lambda (9-fold); pure complex singlet gives 4*LambdaC and
2*LambdaC (2-fold). An independent Q,Y basis decomposes all 55 states; a random
real orthogonal rotation of all fields checks basis invariance.

Gate6's three charged screens agree in signed spectra. Its neutral 13x13
all-incoming matrix equals B.T*M*B. The physical Hermitian operator is
B.conj().T*M*B. Some signed eigenvalues therefore differ. An explicit basis
lift reproduces the inherited signs and confirms equal absolute spectra in this
CP-conserving sector. Output retains signed differences and the numerical
residuals. No frozen source was changed to force agreement.

Full V2+V3+V4 is minimized in two complementary six-real-field gauge charts and
a neutral complex slice, with two seeds and several initial scales. A general
SU2 x U1 transformation puts H1 into a real neutral component, with a residual
phase making H2+ real; the complementary chart covers singular H1=0 directions.
Singlet and neutral phases remain explicit. The ten-field gradient and Hessian
are checked after minimization; broken gauge tangents are removed using SVD
before demanding positive transverse curvature. A credible deeper stationary
minimum requires |grad|/v³<2e-7, transverse curvature/v²>2e-7, full Hessian/v²
>=-2e-7, gauge Ward residual/v²<2e-6, and an independently evaluated depth gap
<-1e-6*v⁴. Search boundary hits and saddles are rejected as stationary witnesses.
The search box is ±12*v per coordinate; it supplies no guarantee outside it.
`VACUUM_NO_DEEPER_WITNESS_FOUND` always has UNKNOWN assessment; a verified
`VACUUM_DEEPER_WITNESS` has FAIL. Nonconvergence is counted and never upgraded.

## Scalar oblique likelihood and sources

Reuse [Grimus 0802.4353v1](https://arxiv.org/html/0802.4353v1), Eqs.28,30,31
and [Florentino 2106.08332v1](https://arxiv.org/html/2106.08332v1) mixing.
The charged pair coefficient is -2; the -1/2 alternative and its difference are
reported, as documented in [Herrero-Garcia 1701.05345v2](https://arxiv.org/html/1701.05345v2),
App.A footnote 13. No claim that these alternatives are equivalent is made.
Quadrature uses 80/160 nodes, adapting through 640 until STU changes <2e-8.
Independent 80-digit log/arctan C2/C4/C5 and a full mixing-matrix T sum validate
the reused functions. The wrapper restores the fixed 125 GeV SM subtraction for
an arbitrary light scalar mass; the inherited scripts assumed mh=reference.

Published fit numbers were checked on 2026-10-25 against the
[Gfitter page](https://project-gfitter.web.cern.ch/Oblique_Parameters/) and
[PDG2025 Table10.8, U-floating column](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-standard-model.pdf).
Gfitter mean=(.03,.05,-.03), sigma=(.10,.12,.09), correlations=(.92,-.67,-.88).
PDG mean=(.021,.04,.008), sigma=(.096,.12,.092), correlations=(.91,-.62,-.83).
The PDG PDF says revised November2025 and is dated 2026-04-15. Fit versions and
actual constants are pinned in the unmodified A1h source hash. Covariances are
checked positive definite and chi² is computed with the full covariance, using
7.814727903251179 for the 95% three-dimensional ellipsoid. Alternative fits share
data. Non-oblique corrections and full electroweak acceptance are not evaluated.

The foundation pins match the snapshot and archived native Module 0 inventory
for the potential, Gate6 inversion and vacuum script. The requested tag/SHA is
absent from both available local Git object stores. This is an explicit ancestry
provenance limitation; no ancestry is inferred. Native SARAH is not rerun here.
Frozen Module 0 files and the original ~/zee working tree are untouched.
