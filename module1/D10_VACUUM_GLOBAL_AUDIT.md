# D10: full complex restricted Zee tree vacuum

Executed locally on 2026-11-03, branch `feature/zee-d10-vacuum-global`, starting
commit `e3a7b205b54039c1e08cbbcb13ebb01c6766c44c` (D9B
`acfc7e4a9a446125aef6c491e30b239aaba303c4` is its parent).
All original calculations and implementation files are preserved.

## Physical outcomes

Five actual scalar survivors were recovered, including the actual D7 survivor
and all three staged historical F13 heavy spectra. Every point below passes
the **recomputed** reconstruction, sufficient all-orientation BFB, 55-state
tree unitarity, and selected Gfitter scalar-oblique screen. Those passes are
not full Zee phenomenological acceptance.

| Representative | charged masses GeV | Mu4 GeV | gamma rad | max unitarity eigenvalue | D10 tree vacuum |
|---|---:|---:|---:|---:|---|
| P2_beta_shift | 300, 700 | 943.400148 | 1.089000 | 18.136779 | UNKNOWN |
| d7_NO_neutral_near_heavy_07 | 298.726655, 532.932913 | 272.361690 | 1.316528 | 18.245067 | GLOBAL CERTIFIED |
| F13_heavy_0000981 | 552.645657, 885.788805 | 1115.357113 | 1.098329 | 21.056519 | UNKNOWN |
| F13_heavy_0001003 | 580.507287, 881.462152 | 1047.940285 | 1.081830 | 21.568114 | UNKNOWN |
| F13_heavy_0001330 | 572.231624, 873.207683 | 1026.119343 | 1.088950 | 24.696992 | GLOBAL CERTIFIED |

The final charged masses in this rounded table must be read with the exact
inputs in `d10_benchmarks.json`; no rounded table value defines a potential.
Two **separately labelled historical controls** are also rerun:
`aligned_decoupling_1500` (1500/2000 GeV, Mu4=0): GLOBAL CERTIFIED;
`physical_deeper_singlet` (120/400 GeV, Mu4=0): DEEPER VACUUM WITNESS.
None of the five representatives has a verified deeper minimum in these runs.

Machine evidence is [d10_vacuum_global.json](../validation/module1/d10_vacuum_global.json).
Every representative/control/deformation has `global_zee_acceptance=null`;
vacuum decay lifetime is `NOT_EVALUATED` throughout.

## Provenance and exact object being certified

[d10_benchmarks.json](d10_benchmarks.json) contains complete input records and
their hashes, raw source-file hashes and local source paths. It makes subsequent
reproduction independent of the availability of other checkouts.

| Input | SHA256 of sorted compact JSON |
|---|---|
| P2_beta_shift | `034e7f9e65606fae1cd7b052feb2a122ddbbf9887e424b7323161687dc8ae7c5` |
| d7_NO_neutral_near_heavy_07 | `ff0c551534e5051f223c00435293403e3b553f52e0cbec4344287da8b3dce862` |
| F13_heavy_0000981 | `e13c2c028ca21023fdbedce81cc13f9be4461f3b6439b025eb3ff0eb298b753f` |
| F13_heavy_0001003 | `42b18df7604d17994a970c189dfc4779f93a371cacdec8e8df1a2b6f4dc9c349` |
| F13_heavy_0001330 | `9117e7af53f9ad5c21f964a7c216de7af5824e903856fed54b9b237c922f4a1d` |
| aligned_decoupling_1500 | `8ec7ad0635c98d554fc659e5033f16be47a5680d0e13dca1a8f9af5c120e9b23` |
| physical_deeper_singlet | `4242602b9b4c74f59496a791d30db49de12c2da20399299ce5e05dabf5c4c200` |

P2 comes from the original Module1 example. D7 is regenerated using the frozen
`module9/d7_prepare.py` and pinned Module3 seed, then checked **equal to the
actual staged nested input** in the local D7 `part_002.jsonl`. It is the one
previously documented scoped D7 survivor, not a substitute generated point.
The F13 records come from the local F16
`F16_three_exact_F13_Zee_input_reconstruction.json`, raw SHA256
`8d2ff3cac333774c08358af856f3f29f07ac626ef1a3a81df65e839297c2e5e0`.
All supplied scalar masses, angles, soft mass and portals are retained; mh1=125
and v=246.21965 are independently confirmed by its spectrum and saved VEVs.
The frozen Module1 inversion agrees with the staged SARAH coefficients to
at most 4.10e-16 scaled difference. No UChicago/AF input or remote output was
invented. Controls are recovered from the existing Module1 validation history.

**Precision scope:** the certificates apply to the exact rational numbers
represented by the stored binary64 **Module1 reconstructed Lagrangian
coefficients**, hashed separately per point. They do not certify an uncertainty
region or every possible rounding of historical inputs. Binary reconstruction
leaves tiny neutral tadpole residuals. Instead of pretending those residuals
are zero, an exact rational Krawczyk contraction encloses the nearby exact
neutral stationary solution in a box of radius 1e-40 GeV. Its displacement
from the requested EW configuration is required to be below 1e-8 GeV.
The theorem applies to that exact EW stationary orbit, not an arbitrarily
rounded field vector. Approximate certified neutral (a,b) values are
(164.33474290262743,183.35268833930360) for D7,
(45.58667736437828,241.96274691158257) for F13_1330, and
(188.31917565842150,158.61905347547400) for the aligned control.

## Frozen potential, normalization and independent checks

The source is `models/SARAH/ZeeTypeII/ZeeTypeII.m`, hash
`78d6b48232f9a75a21b058301d9233dba3ed067e21f534d27c0d6f415484aa4d`,
with `LagNoHC` and `LagHC` combined as directed by AddHC. Module0's archived
inventory and Module1 foundation hashes are revalidated. The old missing
Module0 tag/ancestry limitation remains as documented by Module1; this task
does not repair or infer that historical ancestry.

Canonical complex fields are (r+i im)/sqrt(2), ordered H1+,H10,H2+,H20,S+.
With x=H1†H1, y=H2†H2, z=H1†H2=u+iw, s=|S|² and
d=H1+ H20-H10 H2+, the complete potential is

```
V2 = M112 x + M222 y - 2 M12Sq u + MCS2 s
V3 = 2 Mu4 Re(conj(S) d)
V4 = Lambda1 x²/2 + Lambda2 y²/2 + Lambda3 xy
     + (Lambda4+Lambda5)u² + (Lambda4-Lambda5)w²
     + LambdaC s² + (K1 x+K2 y-2 K12 u)s.
```

Explicitly, the cubic in canonical real fields is

```
Mu4/sqrt(2) * [r8(r0 r6-r1 r7-r2 r4+r3 r5)
              +r9(r0 r7+r1 r6-r2 r5-r3 r4)].
```

This fixes the negative K12 sign, cubic sign and singlet quartic factor.
`d10_polynomial.py` independently expands this complex-component expression
and symbolically differentiates its full ten-field gradient and Hessian;
it imports none of Module1's invariant or cubic tensors. Quadratic
coefficients have GeV² units, Mu4 GeV, quartics dimensionless, fields GeV;
V, gradient and Hessian have units GeV⁴, GeV³ and GeV² respectively.

The neutral tadpoles obey
M112=M12Sq*b/a-[Lambda1*a²+Lambda345*b²]/2 and its 1↔2 counterpart.
The existing inversion, signed charged mixing and full scalar spectrum are
reused unchanged. Every exact point is a local EW minimum with three gauge
Goldstones and positive transverse Hessian. Independent tests check these
null directions, generic SU(2) and hypercharge transformations (S has Y=1,
doublets Y=1/2), signed Mu4/K12 sensitivity, CP phases and charge misalignment.
Across 70 actual configurations (EW, origin and eight generic complex charged
configurations per input), maximum differences against Module1 are
1.33e-13 for V/v⁴, 9.59e-14 for gradient/v³, and 3.08e-14 for Hessian/v².
Tests additionally strengthen the portals/cubic to expose sign errors.

## Full-domain global certificate

This sufficient bound is derived here directly for the complete cubic-coupled
potential. It does not invoke a 2HDM-only vacuum theorem. Let

```
q = (x,y,u,w,s), q0 = (a²/2,b²/2,ab/2,0,0), Deltaq=q-q0,
n = a²+b², B = |b H1-a H2|²/n >= 0,
D = xy-u²-w² = |d|²,
mD² = n [M12Sq/(ab) - (Lambda4+Lambda5)/2],
mS² = MCS2 + (K1 a²+K2 b²-2 K12 ab)/2.
```

Use V4=qᵀCq with nonzero entries
C00=Lambda1/2, C11=Lambda2/2, C22=Lambda4+Lambda5,
C33=Lambda4-Lambda5, C44=LambdaC, C01=Lambda3/2,
C04=K1/2, C14=K2/2, C24=-K12 and their transposes.
Let J01=J10=1/2, J22=J33=-1, other entries zero, so qᵀJq=D.
For **any positive epsilon**, stationarity at q0 gives the exact identity

```
V - V_EW = Deltaqᵀ (C-epsilon J) Deltaq
           + epsilon |d+(Mu4/epsilon)S|²
           + (mD²-epsilon n/2) B
           + (mS²-Mu4²/epsilon) s.
```

Proof: expand the square, use |d|²=D and
D(q)=D(Deltaq)+(n/2)B. The neutral tadpoles make the remaining linear
doublet term mD²B; the singlet linear term is mS²s. A separate SymPy test
verifies the identity symbolically without specializing parameters.

It follows that V>=V_EW for **all ten real fields, without field bounds** if
C-epsilon J is positive semidefinite and the last two coefficients are
nonnegative. The implementation deliberately uses the stronger strict positive
conditions. A floating scalar optimization merely proposes a rational epsilon;
all five LDLᵀ pivots are then checked **exactly over Q**. Exact rational interval
evaluation on the certified neutral-root box verifies both remaining
coefficients. The root enclosure checks a strict Krawczyk self-map and a
Jacobian contraction norm below one with exact rational arithmetic, avoiding
roundoff assumptions and numerical root flags. Saved fractions are replayable.

| Certified point | exact epsilon | smallest exact LDL pivot, approx | mD²-epsilon n/2 GeV², lower bound approx | mS²-Mu4²/epsilon GeV², lower bound approx |
|---|---:|---:|---:|---:|
| D7 | 1650627/250000 | 0.148668 | 71557.947 | 90326.292 |
| F13_1330 | 1232051/200000 | 0.104770 | 482334.342 | 249954.697 |
| aligned control | 30281/200000 | 0.106934 | 2245410.603 | 4000000.000 |

The equality conditions force q=q0, B=s=0 for these strict certificates.
Their neutral EW orbit is the unique global orbit. No enumeration of saddles
or other stationary minima is required for this conclusion.

**Boundary coverage:** the identity is polynomial in full fields and holds at
H1=0, H2=0, S=0, d=0, the origin, charged doublet/singlet VEVs and complex
neutral VEVs. There is no division by a *variable field*, no gauge chart
restriction and no field-radius assumption. a,b are fixed positive certified
EW VEVs. The full complex square explicitly retains the relative singlet phase.

For the ideal exact zero-cubic aligned control, Lambda1=Lambda2=Lambda3=
lambda=mh1²/v², Lambda4=Lambda5=0 and M12Sq=M² sin(beta)cos(beta), giving the
particularly simple identity

```
V-V_EW = lambda/2 (x+y-v²/2)² + M² B + MCS2 s
         + (K1 x+K2 y-2K12 u)s + LambdaC s² >= 0.
```

The portal matrix is positive, MCS2>0 and LambdaC>0. The rational certificate
above also covers the small binary64 differences from that ideal limit.

## Numerical searches and verified counterexamples

The frozen Module1 evaluator was rerun with its actual 64 starts per full
chart, two seeds (123,104852), two complementary six-field charts and a
complex neutral slice. It makes **300 trials per input**, 2100 total, and
accepts 294 credible local minima per input; the remaining six trials are
rejected. These counts are repetitions, **not counts
of distinct stationary gauge orbits**. Each point has zero outer-bound hits.
The original ±12v box is unchanged and has no completeness guarantee.
The older Gate6 seven-real BFGS search is read for comparison but not used
as stronger evidence than Module1.

An independent SLSQP calculation uses the exact Gram domain. Write
x=v²A², y=v²B0², s=v²T², z=v²A B0 cos(eta) exp(i theta), with nonnegative
norm roots, eta in [0,pi/2], theta in [-pi,pi]. Minimize the singlet relative
phase **analytically**: V3_min=-2|Mu4|v³ A B0 T sin(eta). This phase is an
actual physical minimization, not an illicit gauge removal. The fields are
reconstructed with H1 neutral, H2+ real and singlet sign chosen to minimize
V3. Arbitrary complex neutral phases remain. The compact angular domain
includes all singular strata and their intersections; norm roots are bounded
by 12 in this numerical study only. For Mu4=0 any singlet phase is equivalent
in potential value. Tests verify the phase reduction against arbitrary complex
ten-field configurations and all pure-field boundaries.

Twenty-three SLSQP trials per input include EW, origin, single-norm axes,
CP-violating and charge-breaking configurations and 16 fixed-seed multiscale
starts. All 23 optimizer flags report success, but only 2,1,2,3,4,1,9 trials
(table order, followed by controls) survive the **full ten-field** independent
stationarity and transverse-Hessian tests. The others are rejected; success
flags never establish a minimum. All accepted minima for the five
representatives agree in depth with EW within roundoff. Module1 and SLSQP
do not provide a complete stationary-orbit inventory or a certified root count.

The historical singlet control has the exact stationary branch
H1=H2=0, r8=sqrt(-MCS2/LambdaC)=679.8831961897756 GeV, all other r=0.
Here MCS2=-46224.1160461225 GeV², LambdaC=0.1 and Mu4=0.
V=-MCS2²/(4 LambdaC)=-5.341672260613499e9 GeV⁴ and
DeltaV=-5.223265783960916e9 GeV⁴=-1.421187198259369 v⁴.
The singlet radial mass² is -2MCS2>0. The doublet Hessian consists of four
copies of a positive 2x2 block, with diagonals M112+K1 s and M222+K2 s
and off-diagonal -M12Sq-K12 s. Exact rational diagonal/determinant checks and
an interval depth inequality prove this is a deeper local minimum, with nine
positive transverse modes and one broken gauge mode. This exceptional branch
preserves SU(2) but breaks hypercharge; it is charged relative to the original
EW embedding. The stored 80-digit polynomial substitution independently checks
depth, gradient and all ten Hessian eigenvalues. Lifetime is not computed.

### Controlled cubic dependence

A five-point **deformation study**, distinct from the five original survivors,
changes only Mu4 of P2, holding every other Lagrangian coefficient fixed.
Neutral EW tadpoles and quartics/BFB/unitarity therefore stay fixed; the charged
masses/mixing change and EWPO is **not reclassified**. For positive Mu4,

```
Mu4 = (mH2²-mH1²) sin(2 gamma)/(sqrt(2) v).
```

The mass splitting and gamma cannot be varied independently at fixed other
charged matrix entries. This study tests one path, not a model-wide trend.

| Mu4 / original | Mu4 GeV | derived gamma rad | derived charged masses GeV | lowest accepted DeltaV/v⁴ |
|---|---:|---:|---:|---:|
| 0 | 0 | pi/2 | 419.387,635.700 | 0 |
| 0.5 | 471.700 | 1.258894 | 386.531,656.196 | 0 |
| 1 | 943.400 | 1.089000 | 300.000,700.000 | 0 |
| 1.25 | 1179.250 | 1.039045 | 234.747,724.495 | 0 |
| 1.5 | 1415.100 | 1.002277 | 135.947,749.345 | -0.198475369 |

The last case supplies a **mixed doublet/singlet charge-breaking** stationary
minimum, independently polished using 80-digit symbolic derivatives. A pinned
canonical field witness in GeV is

```
(0,0,161.80291128209644,0,459.83710213975801,0,
 232.17088429845256,0,201.05569456314806,0).
```

DeltaV=-7.294532375648121e8 GeV⁴. Full Hessian has four gauge zeros and six
positive transverse eigenvalues, the smallest 64348.07868 GeV²
(1.061427083 v²); gauge Ward residual/v² is 1.56e-15. The polished gradient/v³
is 2.85e-80; at the pinned binary fields the separate 80-digit recomputation
gives 3.50e-16. The EW transverse minimum remains mh1²/v²=0.257735717 and
both charged masses remain positive. Thus local positivity and BFB alone fail
to ensure an EW ground state even along this simple controlled path.
The EW point is a false local minimum; quantum metastability/decay lifetime
remains NOT EVALUATED. Numerical absence at the other four deformation points
is UNKNOWN, not a proof of stability or a located exact transition threshold.

## Unresolved cases, rigorous outer bounds, and bounded stop

P2, F13_0981 and F13_1003 remain `D10_UNKNOWN`. The proposed square-completion
residual has optimized numerical smallest eigenvalues approximately
-0.655930, -0.0235574, -0.0224963 respectively, and exact LDL rejects the
proposed rational epsilons. These are failures of a **sufficient ansatz**;
neither impossibility of every richer certificate nor deeper vacua follow.
No complete polynomial root count, interval covering of the interior or SOS
lower bound has been achieved for those three points.

An additional exact bound compactifies their unresolved domains. The positive
portal matrix and all-orientation doublet quartic bound give
V4>=k N², N=x+y+s, with a stored positive rational k. The cubic obeys
|V3|<=2|Mu4|sqrt(xys)<=|Mu4| N^(3/2)/2, and
V2>=-M N for
M=max(|M112|+|M12Sq|,|M222|+|M12Sq|,|MCS2|).
Consequently V>=t²(k t²-b t-M), t=sqrt(N), b=|Mu4|/2.
An exact rational check establishes a positive, increasing quadratic beyond
the saved integer bound T. The exact neutral-root enclosure verifies V_EW<0.
Thus **V>=0>V_EW outside ||r||=sqrt(2)T**, without sampling the exterior.

| UNKNOWN case | T GeV | sufficient outer exclusion radius ||r||/v |
|---|---:|---:|
| P2 | 15703 | 90.194 |
| F13_0981 | 18136 | 104.168 |
| F13_1003 | 17130 | 98.390 |

These conservative radii exceed the optimizer boxes; the unresolved interiors
include unsearched regions. They are usable compactness bounds, not claims
that the finite searches cover the full relevant domain.

Methods investigated: full-field stationary equations are ten cubic equations
with gauge-related positive-dimensional solution sets, so isolated-root
certification cannot simply count their roots. Generic gauge reduction leaves
six variables and at most 3^6 isolated complex roots by the crude degree bound,
but neutral strata have a stabilizer and chart degeneracies; H1=0/H2=0,
singlet-only, zero-charge and CP phases need explicit saturation/stratification.
Finite chart optimizations cannot close those algebraic components or certify
their multiplicities. A viable next method is a richer gauge-invariant SOS
certificate on the proven compact ball, with exact rational/interval validation
of the dual certificate. Alternatively stratify the stationary ideal, track all
isolated paths including singular endgames and certify/exclude each real root,
while treating non-isolated components separately. Merely applying interval
Newton to found roots establishes existence, not completeness.

This distinction agrees with [HomotopyContinuation's certification documentation](https://www.juliahomotopycontinuation.org/HomotopyContinuation.jl/stable/certification/),
which certifies supplied nonsingular square-system solutions. The known
[Zee charge-breaking study](https://arxiv.org/abs/hep-ph/0507128v3) already
identifies the cubic coupling as a reason 2HDM vacuum conclusions do not transfer.
For SOS background see [Lasserre's polynomial optimization hierarchy](https://arxiv.org/abs/2111.04610).
These references inform method selection; the D10 certificates above follow
from the displayed identity and exact computations, not from an external
theorem asserted for this model. No certifier library was installed, no Condor
jobs were submitted and no large random scan was launched. Work stops here
with three representative UNKNOWN cases and explicit next mathematical steps.

## Scan procedure and validation

1. Use the frozen sufficient BFB and full tree unitarity gates. UNKNOWN BFB
   remains UNKNOWN; it is not automatic rejection or acceptance.
2. Try the inexpensive exact Gram square-completion certificate after verifying
   the local EW stationary orbit. A strict certificate closes all field directions.
3. If it fails, run the reproducible full-field witness search; check depths,
   gradients, gauge modes and transverse Hessian independently. A deeper field
   value already disproves globality; a stationary witness adds physical detail.
4. Reserve richer SOS/interval/stratified enumeration for a small survivor set.
   Conditional use of UNKNOWN points must be explicitly labelled. Never emit
   `FULL_ZEE_ALLOWED=true` or convert no-witness status to global stability.

Nine new tests check the independent polynomial, signs/normalization, gauge
invariance and Goldstones, symbolic certificate identity, exact root and LDL
checks, negative proof controls, Gram reduction including singular strata,
analytic deeper singlet branch, controlled cubic counterexample and honest
status propagation. Reproduction requires only the existing scientific stack:

```
python3 scripts/zee_d10_vacuum_global.py
python3 -m unittest discover -s tests -p 'test_module1_d10_*.py' -v
python3 -m unittest discover -s tests -p 'test_module1*.py' -v
python3 -m unittest discover -s tests -v
git diff --check
```

`--recover` additionally rechecks the original local staged sources; normal
reproduction uses the committed snapshot. Full outputs/logs remain ignored
under `validation/module1/local/d10/`. The original Module1 validation driver
is deliberately not run: it requires its historical branch and overwrites
previous validation histories. The frozen Module1 tests are run directly.

The available pytest installation is obsolete and cannot import under Python
3.10; unittest is the repository's working test runner. Focused D10: 9/9 PASS;
Module1 including D10: 35/35 PASS. The full suite ran 377 tests with 13 skips,
two failures and 16 errors: Module3/4 tests insist on their historical branch
names, two Module5 class setups require absent local D9/D9B `rate_probe`
binaries, and Module9 requires missing `jsonschema` distribution metadata.
All five affected test modules were also run from an untouched archive of
the starting commit: the same two branch failures and 16 error entries recur
(28 tests run; the two native class setups run no tests). These are reproduced
baseline prerequisites, not D10 test regressions. Exact summaries and log hashes
are saved in the machine evidence. No previous tests were modified or bypassed.

Prior Module1 and F19 finite searches only established absence of a deeper
witness for the representative spectra. D10 adds full-domain exact sufficient
certificates for two actual survivors, a simple-limit certificate, exact outer
exclusion bounds, and an independent mixed cubic-driven counterexample.
Loop effective-potential effects, RG/UV stability, EFT validity, thermal history,
bounce actions, full flavor/Higgs/direct-search constraints and paper novelty
remain outside this tree-level result.
