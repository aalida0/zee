# ZeeTypeII SARAH model — first source implementation (2026-10-21)

**Status: SARAH_GATE6_TREE_SCALAR_GAUGE_AND_SYNTHETIC_COMPLEX_LEPTON_PASS; E3_LOOP_UNMATCHED; FULL_ZEE_NOT_VALIDATED.**
User's first local SARAH 4.15.4 run (2026-10-21) initialized ZeeTypeII
in 6.21 s and completed CheckModel in 4.02 s. This is not
SARAH_CHECKMODEL_PASS and not model/physics validation.
See `work_sarah_console.log` and `work/sarah_zee/checkmodel.log`
on the local machine. The log reports `PossibleTerms::NonSUSY`
and seven missing gauge-eigenstate fermion metadata entries.
The latter disappeared after the `particles.m` correction (confirmed
in second local run). The `PossibleTerms::NonSUSY` warning persists.

The third local run numerically compared the actual SARAH CP-even,
CP-odd and charged matrices against the independent Gate6 fixture:
`max|delta M2| = {3.64e-12, 1.82e-12, 0} GeV^2`;
Goldstone residuals zero; scalar masses
`{125, 580.7, 633.7, 300, 700} GeV`.
Status: `SARAH_GATE6_TREE_MASS_MATRICES_NUMERIC_PASS`.
An earlier per-entry diagnostic-index typo erroneously labeled numerical
matrices as nonnumerical and printed Mathematica `Part::partw` warnings;
the full-matrix numeric test and final PASS were correct. The index has
since been repaired in source.

## Sources and precise scope

- Core: `models/SARAH/ZeeTypeII/ZeeTypeII.m`
- Parameters: `models/SARAH/ZeeTypeII/parameters.m`
- Particle metadata: `models/SARAH/ZeeTypeII/particles.m`
- Reproducible local runner: `scripts/zee_sarah_check.m`
- Repository source-level tests: `tests/test_zee_sarah_source.py`
- Reference: upstream SARAH `Models/THDM-II`, `THDM-III`, and
  `Leptoquarks/TwoScalarLeptoquarks`.
- Original potential convention: `scripts/gate6_benchmark.py`
  (arXiv:2106.08332). The new model is not a claim of a paper-equivalent
  Feynman-rule implementation.

## Field and scalar conventions

SU(2) doublets H1,H2 have Y=+1/2; complex charged singlet Splus has
Y=+1. CP-even, CP-odd and charged scalar matrices are respectively 2x2,
2x2 and 3x3. The charged matrix includes a Goldstone mode.

The potential in the SARAH source matches the Gate6 normalization:
`Lambda1/2 |H1|^4 + Lambda2/2 |H2|^4`,
`Lambda5/2 (H1^dag H2)^2 + h.c.`,
`LambdaC |S+|^4`,
`-K12 |S+|^2 (H1^dag H2 + h.c.)`,
and `Mu4 S- (H1^T i sigma2 H2)+h.c.`.
With `HD+=-sin(beta) H1p + cos(beta) H2p`, the expected off-diagonal
mass is `-Mu4 v/sqrt(2)`. Check this explicitly from SARAH, NOT just the
source comments.

Unlike SARAH THDM-II, `Ye2` is a general complex second-doublet
charged-lepton Yukawa in addition to `Ye`; `Fzee` is a complex
antisymmetric lepton-doublet coupling. SARAH's generated mass matrix, with mass-matrix rows carrying left
flavor and columns carrying right flavor, is explicitly
`M_e=(v1 Transpose[Ye] + v2 Transpose[Ye2])/sqrt(2)`.
This fixes the SARAH array index ordering but does not yet establish
the E3 weak-basis flavor rotation.
Hence **do not** use the built-in THDM-II SPheno prescription
`Ye = sqrt(2) m_e/v1` unless Ye2=0.

## Warning audit based on first local CheckModel run

1. `{d,q,conj[H2]}` and `{H1,q,u}`: wrong-doublet quark Yukawa
   structures. Omitted by the chosen Type-II quark *ansatz*. Verify any
   claimed symmetry with full Zee lepton/portal interactions.
2. `{H1,H1,conj[Splus]}`, `{H2,H2,conj[Splus]}`: candidate
   contractions with two identical commuting scalar doublets vanish
   under the antisymmetric SU(2) contraction. Verify independently.
3. `{d,conj[Splus],conj[u]}`: do not add automatically. Check
   Lorentz structure and impose the model's baryon-number selection
   explicitly; this is potentially problematic if actually allowed.
4. The four additional doublet-quartic terms correspond to allowed
   hard-breaking structures of the `lambda6/lambda7` class.
   With `Ye2`, `K12`, and the model's other symmetry-breaking
   interactions, the restricted potential may not be closed under
   one-loop RG evolution. This is an **open physics question**,
   not a harmless metadata warning. Do not silently set these
   couplings to zero in a purported general RGE analysis.
5. Missing `Fd1,Fu1,Fe1,Fv1,Fd2,Fu2,Fe2` were addressed in
   `particles.m` using SARAH's standard `Models/particles.m`
   descriptions. Rerun CheckModel to test warning removal.

## Local validation

Run from the **local** checkout (not /data on AF):

```bash
cd ~/zee
git pull --ff-only

python3 -m unittest discover -s tests -p 'test_zee_sarah_source.py' -v

set -o pipefail
math -script scripts/zee_sarah_check.m 2>&1 | tee work_sarah_console.log

# Next: numerical comparison with original Gate6 tree-level matrices
python3 scripts/zee_sarah_gate6_fixture.py
math -script scripts/zee_sarah_gate6_mass_audit.m \
  2>&1 | tee work_sarah_mass_audit_console.log

cat work/sarah_zee/checkmodel_status.txt
cat work/sarah_zee/mass_audit_status.txt
```

The second script compares the *actual generated SARAH matrices*
`MassMatrix[hh]`, `MassMatrix[Ah]`, `MassMatrix[Hm]` against
independent physical-input predictions derived from the original
`gate6_benchmark.py`, including charged/neutral Goldstone directions.
The full raw SARAH formulas are saved in
`work/sarah_zee/mass_matrices_raw.txt` for mismatch diagnostics.
Numerical mismatches are not automatically evidence of broken physics:
inspect basis ordering, conjugation, gauge fixing, tadpole substitutions,
and signs before resolving.

The loader finds installed `SARAH.m` explicitly because the batch
Mathematica `$Path` differs from interactive mode; it does **not**
modify the installed SARAH package. The initial run successfully
located and started SARAH 4.15.4.

## Next extraction: charged-Higgs Z and photon interactions

At tree level the charged doublet and singlet have different
Z charges, while their electric charge Q=+1 is equal. For a real
2x2 mixing by gamma in (H_D+,s+), the model-independent magnitude of
the off-diagonal derivative coupling is

```text
|g(Z H1+ H2-)| = g2 |sin(2 gamma)|/(4 cos(thetaW)).
g(gamma H1+ H2-) = 0.
```

The sign and i factors depend on particle order and all-incoming
momenta. The probe only extracts SARAH's exact vertex definitions:

```bash
cd ~/zee
git pull --ff-only
math -script scripts/zee_sarah_z_vertex_probe.m \
  2>&1 | tee work_sarah_z_vertex_console.log
cat work/sarah_zee/z_vertex_probe_status.txt
cat work/sarah_zee/z_vertex_raw.txt
```

Only `Z_VERTEX_EXTRACTED_NOT_YET_PHYSICS_VALIDATED` is intended
until the coefficients and momentum structures are checked.

## Local vertex extraction result and next quantitative gate

On 2026-10-21 the user ran `zee_sarah_z_vertex_probe.m` successfully:
`Z_VERTEX_EXTRACTED_NOT_YET_PHYSICS_VALIDATED`. SARAH 4.15.4 returns

```text
Z(H1+,H2-): (-i/2) * [
  (g2*cW-g1*sW) * (ZP[2,1]*ZP[3,1]+ZP[2,2]*ZP[3,2])
  -2*g1*sW*ZP[2,3]*ZP[3,3]
] * (p_H1+ - p_H2-)
```

Orthogonality of the charged scalar mixing matrix sets
`ZP[2,1]*ZP[3,1]+ZP[2,2]*ZP[3,2]
 = -ZP[2,3]*ZP[3,3]`.
Together with `g1=g2 tan(thetaW)`, this gives the expected
`|g_Z12|=g2*|sin(2 gamma)|/(4 cos(thetaW))`.
The extracted off-diagonal photon vertex vanishes under the
same orthogonality and gauge-coupling relations. The raw symbolic
expressions therefore agree analytically with the expected gauge
couplings, but do not yet demonstrate the **numeric** mixing
assignment and sign convention for the saved Gate6 benchmark.

A fail-closed numeric check is now available:

```bash
cd ~/zee
git pull --ff-only
python3 scripts/zee_sarah_gate6_fixture.py
math -script scripts/zee_sarah_z_vertex_numeric_audit.m \
  2>&1 | tee work_sarah_z_vertex_numeric_console.log
cat work/sarah_zee/z_vertex_numeric_status.txt
cat work/sarah_zee/z_vertex_numeric_results.txt
```

The test first verifies `ZP * Mcharged * Transpose[ZP]` is diagonal
with masses `{0, 300, 700} GeV`, then evaluates the SARAH
`Z_{23},Z_{32},gamma_{23},gamma_{22},gamma_{33},Z_{22},Z_{33}`
couplings. For explicitly chosen `g2=0.652` and
`sin^2(thetaW)=0.23122`, the expected off-diagonal Z coefficient
magnitude at `gamma=1.089` is approximately `0.1526723`.
Other predictions include `gamma_{23}=0` and diagonal
photon coefficients `-i*g2*sin(thetaW)`.

Passing the source-level tests does NOT establish that this audit has
run, and the status must remain `Z_VERTEX_NUMERIC_NOT_VALIDATED`
until the local Mathematica output is inspected.

## Charged scalar Z and photon vertices: local numeric result (2026-10-21)

The local Mathematica 15.0.1 + SARAH 4.15.4 numerical audit successfully
reproduced the independently defined Gate6 mixing and gauge-coupling
expectations. User-reported status:

```text
SARAH_GATE6_CHARGED_GAUGE_VERTEX_NUMERIC_PASS
```

At `beta=1.394`, `gamma=1.089`, `g2=0.652` and
`sin^2(thetaW)=0.23122`:

| Check | Local result |
|---|---:|
| Orthogonality `ZP ZP^T - I` | 4.961524821582043e-17 |
| `ZP M_C^2 ZP^T - diag(0,90000,490000)` (GeV^2) | 3.423047989924873e-11 |
| `Z H1+ H2-` coefficient | `+0.15267229094984194 I` |
| `Z H2+ H1-` coefficient | `+0.15267229094984194 I` |
| off-diagonal photon coefficient | `-1.3877787807814457e-17 I` |
| diagonal photon coefficient | `-0.313516422026024 I` |
| largest coefficient residual against analytic EW mixing relations | 1.1102230246251565e-16 |

All extracted structures are the expected two charged-scalar momenta
with opposite signs. This validates the **tree-level charged-scalar
gauge vertices at this benchmark**, not the full partial widths,
flavor-dependent couplings, quantum corrections or experimental
allowed/excluded status. Under our charged-state phase convention,
`gZ12 = g2*sin(2 gamma)/(4 cos(thetaW))`; the sign can change under
a field rephasing without changing the decay rate.

## Next: charged-lepton and antisymmetric Zee vertices

The source's `Fzee/2 l.l.Splus` term and its stated
`Form -> AntiSymmetric` option have not yet been shown to generate
correct physical flavor amplitudes. In particular, a successful
`CheckModel[]` or mass-matrix test does **not** prove that SARAH has
enforced `f_{ij}=-f_{ji}`, vanishing diagonal elements, or the factor
of 2 in a charged-singlet neutrino/charged-lepton vertex.

The source convention for earlier E3 results was explicitly recorded in
`scripts/zee_p1_e3_complex_flavor_fragments.py`:

```text
E3 Y: rows=charged leptons; columns=neutrinos.
Yang/Wu FeynRules ylz_UFO[nu,lep] = sqrt(2) * conj(Y_E3[lep,nu]).
```

**This is a previously proposed E3-to-FeynRules conversion, not
an established SARAH Ye2 mapping.** The SARAH weak-basis lepton Yukawa
matrices `Ye` and `Ye2` jointly generate the charged-lepton
mass matrix; matching them to E3 must account for all
flavor-basis rotations and chiral conventions.

A diagnostic-only probe is now available:

```bash
cd ~/zee
git pull --ff-only

python3 -m unittest discover -s tests \
  -p 'test_zee_sarah_source.py' -v

set -o pipefail
math -script scripts/zee_sarah_lepton_vertex_probe.m \
  2>&1 | tee work_sarah_lepton_vertex_console.log

cat work/sarah_zee/lepton_vertex_probe_status.txt
cat work/sarah_zee/lepton_vertices_raw.txt
```

Its expected end label if extraction completes is
`LEPTON_VERTEX_EXPRESSIONS_EXTRACTED_NOT_VALIDATED`, **not** a
physical Yukawa-sector pass. Inspect antisymmetry, the charged-lepton
mass matrix, all chiral structures and the relative f/Y terms next.
No `MakeSPheno[]` or complete Zee UFO generation until this gate is
resolved.

## Lepton vertex orientation warning and follow-up (2026-10-21)

The user's first local `zee_sarah_lepton_vertex_probe.m` run completed
with `LEPTON_VERTEX_EXPRESSIONS_EXTRACTED_NOT_VALIDATED`.
Key observations:

- The scalar/Yukawa lepton mass matrix is 3x3 with
  `M_e[i,j] = (v1 Ye[j,i] + v2 Ye2[j,i])/sqrt(2)`.
  This transposition is **required** in source-to-source matching.
- SARAH amended `Fzee` parameter metadata with
  `Symmetry -> AntiSymmetric`, but bare
  `Fzee[1,1]` and `Fzee[1,2]+Fzee[2,1]`
  remained symbolic in the default evaluation mode.
  SARAH's `UseSymmASymm` controls at least some parameter
  simplification: the metadata result alone does not prove that the
  physical f amplitudes have the intended antisymmetry/normalization.
- Only `Ye` and `Ye2` appeared in the probed
  `Vertex[{bar[Fe],Fv,Hm}]` and its conjugate, not `Fzee`.
  These are *ordinary* lepton Yukawa fermion orientations.
  The Zee operator involves two LH lepton doublets
  `L^T C i sigma2 L s+`, so check SAME-orientation fermion
  pairs (and HC) before concluding the interaction is absent.
  The first probe did not test these structures.

**Action taken:** Added diagnostic-only script
`scripts/zee_sarah_fzee_orientation_probe.m` with a matrix
of direct/generic and generation-specific vertex orientations:
ordinary `bar[Fe] Fv Hm`, same-orientation
`Fe Fv conj[Hm]`, `bar[Fe] bar[Fv] Hm` and reversals,
plus Weyl `eL vL Sp` GaugeES queries. It logs all expressions
to `work/sarah_zee/fzee_orientation_vertices.txt`.
Its status is either `FZEE_PRESENT_IN_PROBED_VERTICES_NORMALIZATION_NOT_VALIDATED`,
`FZEE_NOT_FOUND_IN_PROBED_ORIENTATIONS_NOT_VALIDATED`, or an
explicit failure; none should be treated as a physics PASS.

```bash
cd ~/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_sarah_source.py' -v

set -o pipefail
math -script scripts/zee_sarah_fzee_orientation_probe.m \
  2>&1 | tee work_sarah_fzee_orientation_console.log

cat work/sarah_zee/fzee_orientation_status.txt
grep -E 'ZEE_F_QUERY_RESULT|ZEE_F_FOUND_VERTEX|ZEE_F_MATCH|ZEE_F_SYMMETRY' \
  work_sarah_fzee_orientation_console.log
```

**Local probe attempt (2026-10-21):** First run returned
`SARAH_START_FAILED` immediately after loading the SARAH banner;
no `Preparing arrays` output and no f-vertex results appeared.
This was traced to the probe's incorrect use of `SA`Start`,
`SA`ModelLoaded`, `SA`AbortStart`, and `SA`Vertex`.
The public symbols are `SARAH`Start`, `SARAH`ModelLoaded`,
`SARAH`AbortStart`, and `SARAH`Vertex`.
The probe was corrected in GitHub; its result must be rerun locally.
The correct `SA`Version` symbol was not changed.
No failure of the physical Zee interaction is implied by this event.

This step is **not** a numerical amplitude normalization test.
After identifying the correct nonzero f vertices, construct
an independent simple complex `f_{e\mu}` fixture, derive the
same physical (s^+\bar\nu^c\ell) amplitude in both
source conventions (including charge conjugation, factorials,
mixing angles and lepton rotations), and compare both
complex components at two parameter points.

## Antisymmetric Zee singlet coupling located in physical vertices

The 2026-10-21 local SARAH 4.15.4 output for
`scripts/zee_sarah_fzee_orientation_probe.m` reports

```text
ZEE_F_SYMMETRY_SWITCH_VALUE UseSymmASymm False
ZEE_F_MATCH_COUNT 10
ZEE_F_ORIENTATION_STATUS FZEE_PRESENT_IN_PROBED_VERTICES_NORMALIZATION_NOT_VALIDATED
```

Of the 17 vertex orientations queried, **ten** contain `Fzee`.
The gauge-basis extraction is

```text
Vertex[{eL_i,vL_j,Sp}] = I/2 * (Fzee[i,j] - Fzee[j,i])
```

so with an explicitly antisymmetric `f` this is `I*f[i,j]`
and the same-flavor vertex is zero. The apparent unevaluated
`Fzee[1,1]` in the earlier probe is explained by the current
`UseSymmASymm=False` mode, not by absence of the symmetry metadata.

The mass-basis `Fe_a Fv_b Hm_k^+` charged-singlet vertex has

```text
PL: I/2 * sum_j conj(Ve[a,j])*(Fzee[j,b]-Fzee[b,j])*ZP[k,3]
PR: 0
```

and the conjugate `bar[Fe_a] bar[Fv_b] Hm_k^-` vertex has

```text
PL: 0
PR: I/2 * sum_j Ve[a,j]*(conj(Fzee[j,b])-conj(Fzee[b,j]))*ZP[k,3].
```

With antisymmetric `f`, these become
`I*ZP[k,3]*sum_j conj(Ve[a,j])*f[j,b]` and
`I*ZP[k,3]*sum_j Ve[a,j]*conj(f[j,b])`, respectively.
`ZP[2,3]=sin(gamma)`, `ZP[3,3]=cos(gamma)`
in the already-tested Gate6 convention.

The present result proves the **presence** and expected symbolic
antisymmetric difference structure of the generated f interaction;
it does not itself verify any complex numeric amplitude or E3 convention.

### Next local numerical check

Added `scripts/zee_sarah_fzee_numeric_audit.m`.
It compares eight independent SARAH-generated component vertices
at each of two explicitly antisymmetric **complex** f fixtures,
including a nontrivial complex unitary charged-lepton rotation,
against the direct Lagrangian expressions. It checks both charged
physical scalars, both chiral orientations, exchange antisymmetry,
the zero diagonal, and complex conjugation.

```bash
cd ~/zee
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_zee_sarah_source.py' -v
python3 scripts/zee_sarah_gate6_fixture.py
set -o pipefail
math -script scripts/zee_sarah_fzee_numeric_audit.m \
  2>&1 | tee work_sarah_fzee_numeric_console.log
cat work/sarah_zee/fzee_numeric_status.txt
cat work/sarah_zee/fzee_numeric_results.txt
```

Successful evaluation would report
`SARAH_ZEE_F_COMPLEX_VERTEX_NORMALIZATION_PASS_E3_UNMATCHED`.
This is **not a reported result yet**, and even if obtained would
not validate the E3 field-basis mapping, complete neutrino-loop
amplitudes, LFV, or an allowed point.

## Consolidated complex lepton validation (single gate, 2026-10-21)

**Previous numerical f-only probe failure:** The first local
`zee_sarah_fzee_numeric_audit.m` run stopped with
`FAIL FZEE_ABSENT gauge11`. For identical gauge-basis flavors the
model yields `I/2 (f11-f11) = 0` by algebra; SARAH legitimately
removes the symbol `Fzee` from that identically zero amplitude.
The probe was at fault, not the physics. The legacy script has been
corrected, but it is **superseded** as the recommended acceptance test.

At user request, further tree-level lepton checks have been
**consolidated into ONE comprehensive gate**:

`scripts/zee_sarah_integrated_lepton_validation.m`, run via

```bash
cd ~/zee
git pull --ff-only
bash scripts/zee_sarah_one_shot_lepton_validation.sh
```

This single command performs static source checks, regenerates the
Gate6 fixture (now including the physically consistent CP-even alpha),
and runs the local SARAH 4.15.4 amplitude audit.

The integrated audit independently tests:

1. Gate6 charged and CP-even scalar mixing diagonalization.
2. `Fzee` antisymmetry metadata; gauge-basis off-diagonal f
   vertices; **zero diagonal** gauge vertices without demanding a
   nonzero symbol inside them.
3. Both physical charged Higgses' singlet-origin f vertices, their
   complex conjugates, and the corresponding expected Weyl chirality.
4. General independent complex `Ye2` together with `Ye`, derived
   consistently from charged lepton masses and separately chosen
   **left- and right-handed unitary flavor rotations**.
5. Direct 3x3 lepton mass-matrix numerical closure, its physical
   biunitary diagonalization, and SM mass proportionality of the
   VEV-aligned neutral Yukawa combination.
6. Charged-Higgs doublet-origin Yukawa vertices of both charges and
   both physical states.
7. CP-even neutral scalar `hh[1]` and `hh[2]` charged lepton
   vertices with independent PL/PR complex amplitude predictions.

The benchmark configurations include a trivial and a nontrivial
complex flavor rotation, two full complex antisymmetric f matrices,
and two independent complex Ye2 matrices. The comparison uses exact
SARAH-extracted vertices but **independent component-Lagrangian
coefficients** as numerical reference. All individual complex
residuals are saved to
`work/sarah_zee/integrated_lepton_residuals.txt`, with an aggregate
status in `work/sarah_zee/integrated_lepton_status.txt`.

Intended successful status **if it passes locally**:
`SARAH_ZEE_INTEGRATED_TREE_LEPTON_COMPLEX_PASS_E3_LOOP_UNMATCHED`.
No such result has yet been observed. Errors are fail-closed and
retain diagnostic output. This remains only a tree-level synthetic
flavor validation; full source-to-source E3 flavor basis/normalization,
one-loop neutrino mass, Barr-Zee, CLFV and source-complete RGEs are
all **unvalidated**.

## Integrated tree-lepton harness failure and namespace-safe repair

The user's first local one-shot integrated validation (2026-10-21)
reported normal SARAH 4.15.4 initialization, successful charged and
CP-even Gate6 diagonalization (all residuals <= 3.43e-11 GeV^2),
and `ZEE_INTEGRATED_VERTEX_QUERIES 52`, but then emitted
`D::ivar: 2 is not a valid variable` and returned incorrect-looking
charged-lepton vertices containing pure scalar quartic couplings.
Status: `LEPTON_VERTEX_EXTRACTION_OR_CHIRALITY_FAILED`.

Root-cause candidate: the large Mathematica runner itself used
global assignments `a=pp[[1]]; b=pp[[2]]; k=kk; n=nn` while
constructing 52 queries. SARAH symbolic routines use short symbols
as dummy variables, and a value attached to one such Global symbol
can corrupt symbolic differentiation in the same Mathematica kernel.
The model Lagrangian did **not** change. The runner now uses
lexically substituted `With` generation labels, prefixed numeric
scalar angles, an explicit 52-query invariant, and a preflight
nonzero `Fzee` vertex sentinel. It fails with a named status on
dummy-variable contamination or sentinel failure, rather than
reporting fabricated physics results.

The test remains **unvalidated** until a new local run completes.
The usual single command is unchanged:

```bash
cd ~/zee
git pull --ff-only
bash scripts/zee_sarah_one_shot_lepton_validation.sh
```

If the validation fails again, inspect
`work/sarah_zee/integrated_lepton_console.log` and status before
any further physics changes. Do not generate new micro-probes;
repair the existing consolidated test instead.

## Integrated tree-level lepton numerical result — PASS (2026-10-21)

Local SARAH 4.15.4 run of the single-entry
`scripts/zee_sarah_one_shot_lepton_validation.sh` succeeded:

```text
ZEE_INTEGRATED_VERTEX_QUERIES 52
ZEE_INTEGRATED_FZEE_SENTINEL_PASS
ZEE_INTEGRATED_N_COMPARISONS 104
ZEE_INTEGRATED_MAX_RESIDUAL 1.734723475976807e-18
ZEE_INTEGRATED_SECTOR_MAX_RESIDUALS <|f -> 0., Y -> 1.734723475976807e-18|>
ZEE_INTEGRATED_STATUS SARAH_ZEE_INTEGRATED_TREE_LEPTON_COMPLEX_PASS_E3_LOOP_UNMATCHED
```

The two synthetic complex f,Ye,Ye2 cases (identity and independent
complex left/right lepton rotations) reproduced the charged-lepton
mass matrix at <=4.45e-16 GeV, charged/neutral scalar diagonalization
residuals <=3.43e-11 GeV^2, and all 104 vertex coefficients
to <=1.74e-18. Harmless shadowing notices for diagnostic references
`Global`a,b,k,n` occurred after the script checked dummy-variable
contamination. No `D::ivar` was observed. The earlier invalid
vertex-mismatch report was an artifact of global dummy symbols in
Mathematica; no change to the Zee Lagrangian was required.

**Scope:** actual SARAH-generated tree-level complex Yukawa
amplitude consistency at two synthetic points. Neither the specific
Chen/E3 f and Y normalization, one-loop neutrino matrix, flavor
likelihood, scalar theory completeness, nor exclusions are thereby
certified. Avoid labeling any E3 309 candidate `ALLOWED`.

### Source-convention warning for next E3 integration

The existing `gateB3_general_zee_charged_lepton_widths.py` documents
Higgs-basis charged Yukawa coefficients `sqrt(2)*Y_E3` and
singlet Yukawa coefficients `2*f_E3` as defined in Chen
arXiv:2508.18757 Eq.(4). The SARAH tree-level vertex extraction
instead returned coefficients `YeD=-sin(beta)*Ye+cos(beta)*Ye2`
and `fSARAH`. To compare the **same amplitudes** in charged-lepton
mass basis, require `|YeD|=sqrt(2)|Y_E3|` and
`|fSARAH|=2|f_E3|`. Precise complex conjugation, index orientation,
field phases and the sign of the Majorana self-energy need an
independent cross-code derivation; do not blindly identify the saved
E3 numerical matrices with SARAH parameters. Consistency of the
Chen log coefficient `kappa=sqrt(2)*sin(2gamma)*log(mH1^2/mH2^2)/(16pi^2)`
follows from those factors and `sum ZP[k,3] ZP[k,D] log(m_k^2)`.
This is **not yet** a generated one-loop self-energy test.

## Next ONE comprehensive E3–SARAH convention gate (2026-10-21)

Following the successful `104/104` complex tree-lepton comparison,
the next audit uses the **source-defined Chen/E3 normalization**,
not the previous arbitrary complex Yukawa matrices. No old E2/E3
artifacts are modified.

The source `gateA1b_hierarchical_no_seed.py` uses
`Mnu = kappa (f Ml Y + (f Ml Y)^T)` with
`kappa=sqrt(2)*sin(2 gamma)*log(mH1^2/mH2^2)/(16*pi^2)`.
The existing `gateB3_general_zee_charged_lepton_widths.py`
defines charged interactions with coefficients `2f` (singlet)
and `sqrt(2)Y` (non-VEV doublet), matching the published
Higgs-basis interaction convention in Chen arXiv:2508.18757
Eq.(4). The validated SARAH vertices instead have tree-level
coefficients `fSARAH` and `YD=-sin(beta)*Ye+cos(beta)*Ye2`
(with source lepton-index ordering).

**Do not reuse E3 f,Y numbers unchanged in SARAH.** In the fixed
charged-lepton diagonal convention used by the new test,

```text
fSARAH = 2*fE3
YD = sqrt(2)*Y_E3
S = cos(beta)*Ye+sin(beta)*Ye2 = sqrt(2)/v*diag(m_e,m_mu,m_tau)
Ye = cos(beta)*S - sin(beta)*YD
Ye2 = sin(beta)*S + cos(beta)*YD
```

The identification above is defined for the particular overall
relative field phases adopted in the test. A complete field and
one-loop self-energy phase audit is still open.

Two original-source-inspired *synthetic* flavor fixtures are built
by `scripts/zee_sarah_e3_convention_fixture.py`:
the A1b neutrino-null-vector seed at the Gate6 300/700 GeV
benchmark and a distinct B2 null root at 375/925 GeV.
Both use complex f,Y and independent neutrino rank-5 solutions.
The fixture also evaluates the charged-lepton-mass-dependent
finite one-loop scalar B0 log difference as an independent
Feynman-parameter integral. They are not two of the 309
optimized E3 archival source candidates.

`scripts/zee_sarah_e3_integrated_validation.m` consumes this
fixture and **actual SARAH-generated** GaugeES and EWSB lepton
vertices. It checks 81 vertex structures at each point
(9 gauge, 72 charged), 162 complex coefficient comparisons,
charged-lepton mass-matrix closure, 6 massless-neutrino
partial widths against the B3 source, sign-convention-chosen
neutrino loop-kernel contraction against A1b, and loop
renormalization-scale cancellation. The full residual ledger
is saved to `work/sarah_zee/e3_integrated_residuals.txt`.

One command (local Mathematica machine):

```bash
cd ~/zee
git pull --ff-only
bash scripts/zee_sarah_e3_one_shot.sh
```

The only intended success label is

```text
E3_SARAH_TREE_CONVENTION_AND_CHEN_KERNEL_CONSISTENT_SELFENERGY_UNVALIDATED
```

**No PASS has been obtained for this new audit yet.**
Even this PASS would establish only compatibility of Chen/E3
tree couplings, B3 LO widths and the specifically *assembled*
one-loop log kernel. It would NOT constitute an independent
SARAH `SelfEnergy` or a SPheno/FlavorKit generated
neutrino mass computation, nor an amplitude-level proof of
the complex weak-basis mapping for all 309 E3 points. A
true independently calculated one-loop Majorana self-energy
and its finite charged-lepton-mass terms remain future work.
No LFV/Barr-Zee/constraint or experimental allowed/excluded
status is warranted.

## Chen/E3 integrated run PASS and genuine SARAH self-energy gate (2026-10-21)

The user locally executed the one-shot complex E3–SARAH gate in SARAH
4.15.4. Both A1b and a second B2 null-root synthetic complex fixture
successfully passed:

```text
ZEE_E3_VERTEX_COMPARISONS 162
ZEE_E3_MAX_VERTEX_RESIDUAL 0.
ZEE_E3_MAX_WIDTH_RESIDUAL_GEV 5.421010862427522e-20
ZEE_E3_MAX_MNU_CONVENTION_RESIDUAL_EV 4.243133622402948e-15
ZEE_E3_MAX_SCALE_RESIDUAL_EV 8.010953012473591e-15
ZEE_E3_GENERATED_SELFENERGY_CHECKED False
ZEE_E3_REAL_309_ARCHIVE_TESTED False
E3_SARAH_TREE_CONVENTION_AND_CHEN_KERNEL_CONSISTENT_SELFENERGY_UNVALIDATED
```

This result establishes the tested
`fSARAH = 2*fE3` and `YD = sqrt(2)*Y_E3` mapping,
exact closure of the 162 mass-basis vertex coefficients,
the included B3 leptonic widths and convention-prescribed
Chen logarithmic neutrino formula with loop-scale cancellation.
**It does NOT derive the self-energy using SARAH's one-loop
diagram machinery.** That is an independent next requirement.

The finite charged-lepton-mass kernel differs from the
massless-loop approximation by as much as
`4.78672036e-6 eV` at these two complex test points
(relative shift `1.56145e-4` at the A1b point).
The finite correction is a real physical approximation effect,
not the `4.24e-15 eV` algebraic residual or a floating-point error.
It must be included or bounded in a precision neutrino fit.

### ONE next major-stage command: SARAH-generated loop expressions

According to SARAH's loop-corrections documentation, the independent
API is `CalcLoopCorrections[EWSB]`. Its model-generated results are
`SelfEnergy1LoopSum[EWSB]` and `SelfEnergy1LoopList[EWSB]`;
these include generic one-loop diagrams and finite integrals.

Added `scripts/zee_sarah_e3_independent_selfenergy_audit.m`
and one entrypoint `scripts/zee_sarah_e3_selfenergy_one_shot.sh`.
The wrapper reruns the **previous complete 162-vertex
convention/width/kernel check** and then asks SARAH to generate
the actual one-loop self energies. It exports a particle inventory
and full neutrino-related summed and diagram-list expressions;
both sets are derived from the SARAH loop generator rather than
Chen's manually prescribed neutrino formula.

```bash
cd ~/zee
git pull --ff-only
bash scripts/zee_sarah_e3_selfenergy_one_shot.sh
```

Expected files:

```text
work/sarah_zee/e3_sarah_selfenergy_status.txt
work/sarah_zee/e3_sarah_selfenergy_neutrino_raw.txt
work/sarah_zee/e3_sarah_selfenergy_inventory.txt
work/sarah_zee/e3_independent_selfenergy_console.log
```

**No outcome is presumed for the self-energy stage.**
It checks whether SARAH actually generates a neutrino self-energy
containing charged leptons and charged Higgs bosons, but it
**does not** turn generic neutrino wave-function self energies
into a Majorana mass assertion. In the current model,
`Fv -> {vL,0}` is represented as a one-chirality Dirac spinor;
this could prevent SARAH's standard fermion self-energy
conventions from directly representing the lepton-number-violating
Majorana neutrino mass. If no neutrino result is found, the
status is explicitly
`SARAH_NO_NEUTRINO_SELFENERGY_IN_CURRENT_FIELD_REPRESENTATION`
and we must examine a Majorana-compatible neutral-fermion
formulation or dedicated diagrammatic calculation.

Even the status
`SARAH_NEUTRINO_LOOP_TOPOLOGIES_EXTRACTED_MAJORANA_MASS_UNVALIDATED`
is ONLY a **topology extraction milestone**, not validation
of the finite Majorana mass matrix. The subsequent acceptance
gate must identify the chirality-flipping, lepton-number-violating
form factor, its one-loop symmetry factors, counterterms/scheme,
its finite B0 function and complex phases, and numerically compare
the resultant 3x3 symmetric matrix against both E3 fixtures.

The existing 309 E3 optimized configurations remain
**NOT FULL ZEE ALLOWED/EXCLUDED**, regardless of this result.

## Unresolved physics / blockers

1. Check the SU(2) dot contraction and sign of the Zee trilinear in SARAH
   and explicitly extract the charged 3x3 mass matrix and Goldstone null
   eigenvector. Compare physical eigenvalues/mixing with Gate6.
2. Verify `Fzee/2 l.l.Splus` normalization, fermion ordering, hermitian
   conjugation and antisymmetry, by a numerical flavor amplitude.
3. Determine the relation between SARAH `Ye2` and the E3 saved mass-basis
   complex Y matrix; ensure neutrino loop normalization agrees.
4. Confirm `Form -> AntiSymmetric` is honored by SARAH 4.15.4 for the
   non-SUSY Weyl contraction, including zero diagonal entries.
5. The source uses a CP-conserving scalar potential. Generic allowed
   hard symmetry-breaking terms are deliberately absent; confirm the
   intended flavor/symmetry hypothesis is radiatively consistent.
6. CKM, mass-basis lepton Yukawas, SPheno boundary conditions, loop-induced
   neutrino masses, LFV, full decays and B->Xs gamma remain unresolved.
7. `particles.m` PDG names and diagonalizing-matrix metadata need checks
   against generated output. No validated SPheno.m is asserted.

Do not run `MakeSPheno[]` before the model errors above are resolved.
No experimental allowed/excluded status is available.
