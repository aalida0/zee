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

## SARAH genuine one-loop generation result and corrected external-label audit (2026-10-21)

The user ran `bash scripts/zee_sarah_e3_selfenergy_one_shot.sh`.
The previous 162/162 E3 complex Yukawa/width/Chen-kernel tests
passed again. SARAH then successfully executed
`CalcLoopCorrections[EWSB]` (all vertex lists generated, EWSB
self-energy calculation completed), and both
`SelfEnergy1LoopSum[EWSB]` and `SelfEnergy1LoopList[EWSB]`
were reported as lists.

**Crucial correction:** The first version of
`zee_sarah_e3_independent_selfenergy_audit.m` incorrectly
assumed a `SelfEnergy1LoopSum` entry had the form
`{particle,expression}`, then treated
`First/@SelfEnergy1LoopSum` as a particle inventory.
That output instead printed enormous fermionic scalar-integral
expressions as `ZEE_E3_SELFENERGY_PARTICLE_NAMES`, and
spuriously counted `2` neutrino sum rows and `1`
diagram-list row, because the false external-label test
looked for Fv anywhere inside the expressions. The resulting
status `SARAH_NEUTRINO_LOOP_TOPOLOGIES_EXTRACTED_MAJORANA_MASS_UNVALIDATED`
**is not a valid neutrino-specific certification** and has
been retired. The previous tree-level and convention PASS
results are unaffected.

Checked against SARAH's upstream
`Package/loopCorrections.m`, the correct data contract is

```text
SelfEnergy1LoopSum[EWSB] =
  Join[SelfEnergies1Loop[EWSB], SelfEnergyUnmixed[EWSB]]
ParticlesSelfEnergy1LoopSum[EWSB] = entryParticles
SelfEnergy1LoopList[EWSB][[i]] = {external_particle,diagram1,...}
```

The updated integrated audit performs a **fail-closed alignment**
of the entire summed-expression list against its genuine external
labels. It reports a compact inventory including each external
particle, expression head, and dimensions; it identifies neutrino
entries from the external label alone, and only then inspects
their sum/diagram list for `Mass[Fe[...]]`, `B0`, `Hm`
and `Fe` ingredients. It does **not** claim Majorana mass
generation from those ingredients.

Re-run the SAME one-shot major gate (no extra probes):

```bash
cd ~/zee
git pull --ff-only
bash scripts/zee_sarah_e3_selfenergy_one_shot.sh
```

After the run inspect

```bash
cat work/sarah_zee/e3_sarah_selfenergy_status.txt
cat work/sarah_zee/e3_sarah_selfenergy_inventory.txt
grep -E 'ZEE_E3_SELFENERGY_(N_|LABELS|NEUTRINO|MAJORANA|E3_MNU|STATUS)|FAIL ' \
  work/sarah_zee/e3_independent_selfenergy_console.log
```

**Current outcome:** SARAH loop expressions exist, but no
Majorana chirality-flipping self-energy was evaluated and
no independent comparison with the E3 neutrino matrix has
been performed. The next meaningful step after a corrected
inventory is an actual neutrino-sector, LNV
Majorana-symmetric self-energy extraction with its loop
symmetry factors, complex conjugation, finite charged-lepton
mass terms, and matrix-level numerical closure.

## 2026-10-21 local corrected Fv self-energy inventory: topology PASS, not Majorana mass

The user locally reran the corrected integrated
`zee_sarah_e3_selfenergy_one_shot.sh`. The previous
`162/162` E3–SARAH complex charged vertices/widths/Chen kernel
consistency gate again PASSED. SARAH independently generated the full
1-loop self-energy expressions (`CalcLoopCorrections[EWSB]`).
The **correct** particle-label metadata was aligned with the
summed self-energy list, and gave precisely 11 entries:

```text
{hh, Ah, Hm, Fd, Fu, Fe, Fv, VG, VP, VZ, VWm}
INDEX 7 EXTERNAL Fv SUM_HEAD List SUM_DIMENSIONS {3}
```

One external `Fv` sum and one `Fv` diagram inventory were
identified. The Fv sector genuinely contains `B0`,
`Mass[Fe[...]]`, `Hm[...]` and `Fe[...]`.
Status in the observed run:

```text
SARAH_NEUTRINO_EXTERNAL_SECTOR_FE_HM_B0_CANDIDATE_MAJORANA_UNVALIDATED
```

This is now a **verified charged-lepton/charged-Higgs neutrino
self-energy candidate topology**, not a Majorana mass result.
The loop amplitude still needs the lepton-number-violating
chiral form factor, the external Weyl/Majorana convention, and an
independent 3x3 symmetric complex numeric evaluation. Both
`MAJORANA_MASS_NUMERICALLY_EXTRACTED` and
`E3_MNU_NUMERICALLY_MATCHED` remain `False`.

Source check against SARAH upstream `Package/loopCorrections.m`:
`AddLoopFermion` returns the three components
`{Sigma1LoopS, Sigma1LoopR, Sigma1LoopL}`. For an external
four-component fermion with `AntiField[Fv]!=Fv`, this is a
Dirac-type form-factor convention, **not automatically the
Majorana LNV neutrino mass**. The current model defines
`Fv -> {vL,0}`. The loop form factors may therefore be
usable diagrammatically but cannot be promoted to a
Majorana mass without proving their external spinor and
charge-conjugation identification.

The existing integrated self-energy audit was expanded again
to export the precise three Fv components, test the
`SigmaS` channel (rather than all three channels mixed
together) for `B0`, charged-lepton mass and charged-Higgs
contributions, inspect both chiral vertices, and report
the Majorana-particle classification separately. The output
path is

```text
work/sarah_zee/e3_sarah_neutrino_sigma_components.txt
```

It is still the **same single large-stage test**:

```bash
cd ~/zee
git pull --ff-only
bash scripts/zee_sarah_e3_selfenergy_one_shot.sh
```

This source change has not yet been executed locally; it
cannot certify a neutrino mass until `SigmaS` is physically
interpreted and explicitly evaluated.

## 2026-10-21 corrected Fv SigmaS audit and controlled Majorana spinor A/B

The latest local `scripts/zee_sarah_e3_selfenergy_one_shot.sh`
run passes the 162 E3–SARAH complex benchmark vertex comparisons
and computes SARAH one-loop expressions for 11 particle sectors.
External `Fv` has the three generated fermionic components
`{SigmaS,SigmaR,SigmaL}`. The first (mass-type) component contains
`B0`, `Mass[Fe]`, charged Higgs `Hm`, and both
`Cp[..][PL]` and `Cp[..][PR]` factors. Local status:

```text
SARAH_FV_SIGMAS_FE_HM_B0_EXTRACTED_MAJORANA_AMPLITUDE_UNVALIDATED
ZEE_E3_FV_DIRAC_SPINOR_LEFT_ONLY True
ZEE_E3_FV_LISTED_MAJORANA_PARTICLE False
ZEE_E3_SIGMAS_HAS_B0 True
ZEE_E3_SIGMAS_HAS_MASS_FE True
ZEE_E3_SIGMAS_HAS_HM True
ZEE_E3_SIGMAS_HAS_CPL True
ZEE_E3_SIGMAS_HAS_CPR True
ZEE_E3_SIGMAS_COMPLEX_LNV_AMPLITUDE_VERIFIED False
```

**Important scientific interpretation:** The original
`Fv -> {vL,0}` is a left-only four-component representation,
NOT a SARAH Majorana spinor. Its ordinary Dirac
`SigmaS` cannot automatically be called the physical
LNV `<nu_L nu_L>` Majorana two-point function.
A nonzero `Mass[Fe] B0` product alone does not establish
the Majorana neutrino mass (nor the sign/symmetry factors).

SARAH's own documentation gives the supported Majorana packaging
`Fv -> {VL,conj[VL]}` for its Scotogenic model. For a clean
controlled experiment, the one-shot loop runner was extended
to construct an **isolated** model copy
`ZeeTypeIIMajoranaAudit` under
`work/sarah_zee/sarah_model_variants/`.
Only the model NAME and the EWSB four-component spinor
declaration are changed; the Lagrangian, Weyl field
content, Yukawas, scalar sector, masses and parameters
are byte-for-byte unchanged, as verified by the
reversible transformations and SHA256 manifest.
The production `models/SARAH/ZeeTypeII` directory is
never modified.

The updated SAME single command

```bash
cd ~/zee
git pull --ff-only
bash scripts/zee_sarah_e3_selfenergy_one_shot.sh
```

now runs the original SARAH Dirac-packaged
`SigmaS/R/L` audit, generates the temporary Majorana
variant and separately invokes SARAH's
`CalcLoopCorrections[EWSB]` for that variant. It checks
that SARAH classifies the new `Fv` as Majorana and
`AntiField[Fv]===Fv`, verifies the original gauge-basis
Weyl `f` vertex, and exports the resulting neutrino
`SigmaS/R/L` and complete neutrino diagram list in

```text
work/sarah_zee/e3_majorana_variant_manifest.json
work/sarah_zee/e3_majorana_ab_status.txt
work/sarah_zee/e3_majorana_ab_console.log
work/sarah_zee/e3_majorana_ab_sigma.txt
```

**No result of the new variant has yet been observed locally.**
Even `MAJORANA_AB_SARAH_SIGMAS_GENERATED_NUMERIC_MNU_AND_LNV_UNVALIDATED`
is a diagrammatic/representation success, NOT full loop
validation. The decisive future step is to extract the
lepton-number-violating symmetric 3x3 `SigmaS(0)` mass
matrix with correct one-loop normalization and phases,
including checking whether the different Majorana
packaging causes a factor-two in SARAH's generic
`AddLoopFermion`; only then can it be compared
numerically with the two complex E3 fixtures. Do not
introduce a tree neutrino Majorana mass or silently
change the production model while doing this.

## Majorana-packaged Fv A/B result — local PASS at the extraction stage (2026-10-21)

Local run (SARAH 4.15.4) of the **same major-stage one-shot script**
\`scripts/zee_sarah_e3_selfenergy_one_shot.sh\` completed both
the original left-only Dirac packaging and the isolated Majorana
packaging. The temporary \`ZeeTypeIIMajoranaAudit\` model was created
under \`work/sarah_zee/sarah_model_variants/\`; its production
Lagrangian, gauge/supermultiplet content, Weyl fields and Yukawa
operators match the standard model, except the EWSB Fv spinor
representation and unique model name. The generator checks a
reversible source-text transformation and hashes the inputs.
No tree-level neutrino mass was inserted.

Observed local diagnostic results:

\`\`\`text
ZEE_E3_MAJORANA_AB_SPINOR_DEFINITION_EXPECTED True
ZEE_E3_MAJORANA_AB_LISTED_AS_MAJORANA True
ZEE_E3_MAJORANA_AB_ANTIFIELD_SELF_CONJUGATE True
ZEE_E3_MAJORANA_AB_FZEE_GAUGE_VERTEX_PRESENT True
ZEE_E3_MAJORANA_AB_SIGMAS_DIMENSIONS {3}
ZEE_E3_MAJORANA_AB_SIGMAS_B0 True
ZEE_E3_MAJORANA_AB_SIGMAS_MASS_FE True
ZEE_E3_MAJORANA_AB_SIGMAS_CHARGED_HIGGS True
ZEE_E3_MAJORANA_AB_SIGMAS_COUPLINGS True
ZEE_E3_MAJORANA_AB_SIGMAS_TREE_MNU_ZERO_IDENTICALLY_ZERO False
ZEE_E3_MAJORANA_AB_SIGMAS_TREE_MNU_ZERO_MASS_SYMBOL_REMAINING False
ZEE_E3_MAJORANA_AB_COMPLEX_MNU_MATRIX_EXTRACTED False
ZEE_E3_MAJORANA_AB_CHEN_E3_NUMERIC_MATCH False
MAJORANA_AB_SARAH_SIGMAS_GENERATED_NUMERIC_MNU_AND_LNV_UNVALIDATED
\`\`\`

**Meaning and limitations:** The SARAH Majorana packaging is
recognized and preserves the known gauge-basis f operator.
The generated \`SigmaS\` is *symbolically* not identical to zero
after syntactically setting explicit tree Fv masses to zero.
This is a structural clue, not proof that the physical
\`<nu_L nu_L>\` mass is nonzero after reduction, and not proof
of the correct lepton-number-violating \`f/Y\` product.
It does NOT establish flavor symmetry of the complete 3x3
matrix, the sign/symmetry factor of the Majorana self-energy,
the finite B0 subtraction, or E3 numerical closure.

Additional important observation: Changing the four-component
representation changed SARAH's reported FFS *candidate vertex*
count from 12 for the original model to 10 for the Majorana
variant. Counts alone cannot demonstrate a missing physical
interaction: they can differ from charge-conjugate bookkeeping.
But they prohibit assuming that every physical Majorana
amplitude has the SAME chirality labels/normalization as the
previous 162 checked Dirac-packaged E3 vertices.

To enable the genuine next large physics gate without repeating
the same generic topology probes, the existing integrated
\`zee_sarah_e3_majorana_ab_validation.m\` has been extended to
export a machine-readable \`SigmaS\` expression, a complete
chirality-labeled \`Cp\` coupling atom inventory and charged
lepton/Higgs physical vertex orientations. These are all
generated by SARAH itself; **no numeric matrix PASS is claimed
by their mere existence.**

\`\`\`text
work/sarah_zee/e3_majorana_ab_sigma_machine.m
work/sarah_zee/e3_majorana_ab_sigma_couplings.txt
work/sarah_zee/e3_majorana_ab_physical_vertices.txt
\`\`\`

The next nontrivial acceptance is an independent **full one-loop
Majorana mass comparison** for the two complex E3 benchmark
fixtures, using the actual generated \`SigmaS\` coupling factors,
including the correct external charge-conjugation convention,
loop normalization, B0 finite part and relative charged scalar
mixing sign, with explicit \`f=0\`, vanishing charged mixing
and doublet-Yukawa-alignment null tests. The current fixture's
analytic Chen expression must remain a cross-code REFERENCE,
not be used to construct the claimed independent prediction.

**Avoid rerunning SARAH only to retrieve already-computed raw
expressions.** The previously generated
\`work/sarah_zee/e3_majorana_ab_sigma.txt\` on the user's
local machine can be supplied directly for source-level analysis;
a full one-shot rerun is needed only to produce the newer
machine-readable and Cp inventory outputs.

## Uploaded SARAH Majorana SigmaS reviewed; new one-shot complex matrix evaluation (2026-10-21)

The user supplied the actual
\`work/sarah_zee/e3_majorana_ab_sigma.txt\` (3,769 bytes).
The massless-tree-neutrino limit of the generated \`SigmaS\`
contains **exactly four** top-level contributions: two
charged-Higgs/charged-lepton FFS orientations and two W/charged
lepton FFV orientations. The explicit tree-neutrino-mass
dependent Z/Fv contribution disappears. The \`SigmaS\` is
still in terms of symbolic \`Cp[...][PL/PR]\`; no claim of a
nonzero physical LNV mass can be made before evaluating these
chirality-projected coefficients. In particular the W terms
MUST disappear after imposing the actual chiral gauge couplings;
simply observing a surviving symbolic W term is not evidence
of a physical W-generated neutrino mass.

SARAH upstream \`Package/loopCorrections.m\` function
\`AddLoopFermion\` has an explicit factor 2 when the external
fermion is Majorana; the two diagram inventory FFS terms carry
the factor 1/2, requiring consistent cancellation of factors.
Do NOT insert another ad hoc factor of 2.

The existing **single large integrated Majorana A/B**
\`scripts/zee_sarah_e3_majorana_ab_validation.m\` has now
been extended with a guarded **numerical full 3x3**
evaluation of the SARAH-generated \`SigmaS(0)\`.
It uses \`SARAH\`Vertex\` with the *exact field ordering and
chirality* in each saved \`Cp\`, evaluates those SARAH vertices
at both complex E3 flavor fixtures (with fSARAH=2 fE3 and
YD=sqrt2 YE3 only as a parameter conversion),
expands the generated internal loops and uses a finite B0
function at Q=100 and 1000 GeV.

Explicit tests: full 3x3 Majorana-mass symmetry, subtraction
scale cancellation, disappearance of W-only loops, change of
finite gauge regularization \`rMS\`, and **four** physically
required nulls (f=0, gamma=0, mH1=mH2, YD=0).
A nonzero signal is required to prevent all-zero output
from passing the four nulls. Each unphysical contribution is
tested to < 1e-15 GeV (about 1e-6 eV). The resulting
\`SigmaS/(16pi^2)\` is compared element-by-element to the
**independently supplied** finite-loop
\`zeeE3Cases[[i]]["FiniteMnuEV"]\` source matrix, with
both relative signs and complex conjugation reported.
The script does not automatically choose the sign/conjugation
that minimizes the discrepancy, since the external-field
Majorana self-energy convention must be derived.

Outputs after local execution:

\`\`\`text
work/sarah_zee/e3_majorana_ab_numeric_matrix_report.txt
work/sarah_zee/e3_majorana_ab_console.log
work/sarah_zee/e3_majorana_ab_status.txt
\`\`\`

**No new numerical 3x3 result has been obtained yet.**
The augmented Mathematica code has undergone source-only
bracket/static-contract checks. An unresolved \`Cp\` or other
unexpected symbolic factor fails closed with
\`MAJORANA_AB_NUMERIC_SIGMAS_NOT_RESOLVED\`.
A failed required gauge, symmetry or null test fails with
\`MAJORANA_AB_NUMERIC_MATRIX_STRUCTURE_OR_NULL_FAILURE\`.
Passing basic numerical and null checks reports
\`MAJORANA_AB_NUMERIC_SIGMAS_AND_NULLS_PASS_E3_SIGN_UNVALIDATED\`:
this is still NOT a Chen/E3 neutrino mass PASS.

Since the earlier A/B results, source E3 fixture and diagnostic
SARAH variant already exist, the direct large numerical gate
can be run without repeating all previous 162-vertex tests:

\`\`\`bash
cd ~/zee
git pull --ff-only
set -o pipefail
math -script scripts/zee_sarah_e3_majorana_ab_validation.m \
  2>&1 | tee work/sarah_zee/e3_majorana_ab_console.log
cat work/sarah_zee/e3_majorana_ab_status.txt
grep -E 'ZEE_E3_MAJORANA_(NUMERIC|NULL)|FAIL |STATUS' \
  work/sarah_zee/e3_majorana_ab_console.log
\`\`\`

This is a SINGLE comprehensive stage, not a series of small
probes. If the previous status/model/fixture is missing, use
the full \`bash scripts/zee_sarah_e3_selfenergy_one_shot.sh\`
instead.

## 2026-10-21: generated Majorana 3x3 matrix numerical result and finite-B0 reference correction

The user executed the full Majorana-packed SARAH SigmaS 3x3
evaluation and both complex benchmarks passed symmetry,
subtraction-scale independence, vanishing W-sector, rMS independence,
and all four physical nulls (f=0, gamma=0, charged mass degeneracy,
non-VEV Yukawa=0). The computed signal is nonzero, max ~0.03065 eV.

The original E3 fixture used a **120-node Gauss–Legendre**
integral for the finite-mass B0 log difference. This was
insufficiently accurate for the tau-lepton endpoint: its
error is -1.82453e-5 at (300,700) GeV and -1.77408e-5
at (375,925) GeV. This explains the residual
~3e-7 eV between the reference finite neutrino matrix and
the transformed SARAH result. The correct finite-mass log is

    I(a,b,z) = log(a/b) + z*(log(a/z)/(a-z)-log(b/z)/(b-z))

for a=mH1^2, b=mH2^2, z=mell^2, with I=log(a/b) for z=0.
A high-precision independent integration confirms this
analytic expression. The fixture now evaluates it directly,
with an optional adaptive SciPy quadrature cross-check.
Fixture metadata explicitly declares
`FiniteKernelMethod = ANALYTIC_CLOSED_FORM`; the
SARAH numerical audit refuses stale quadrature fixtures.

The actual independently generated SARAH SigmaS matrix
has the complex orientation -Conjugate[E3] up to the
old quadrature error. The latest audit tests this
mapping **with no automatic choice of sign/conjugation**.
As an additional independent phase check, the matrix gate
tests all 72 charged-scalar lepton chirality coefficients
at each complex point against Lagrangian-derived
expected structures, including signs and conjugations,
before comparing the 3x3 matrices. It then tests the
**fixed** -Conjugate[SARAH SigmaS] reference residual
to 5e-11 eV. The sign of SigmaS in the inverse propagator
and the Majorana external-state field phase should still be
derived at the spinor level before claiming a complete
model convention certification.

No new SARAH result has yet been obtained with the corrected
finite-loop reference and expanded phase checks.

To rerun only the comprehensive numerical matrix stage,
regenerate the independent reference first:

```bash
cd ~/zee
git pull --ff-only
python3 -m unittest discover -s tests -p 'test_zee_sarah_source.py' -v
python3 scripts/zee_sarah_e3_convention_fixture.py
set -o pipefail
math -script scripts/zee_sarah_e3_majorana_ab_validation.m \
  2>&1 | tee work/sarah_zee/e3_majorana_ab_console.log
cat work/sarah_zee/e3_majorana_ab_status.txt
grep -E 'COMPLEX_VERTEX_CONVENTIONS|FIXED_NEGCONJ|ANALYTIC_B0|NUMERIC_FAILURE|STATUS' \
  work/sarah_zee/e3_majorana_ab_console.log
```

This remains the existing integrated stage, not a new script.
The optimized 309 E3 points and the full Zee flavor/global
likelihood are still not certified.

## 2026-10-21 — independent Majorana 3x3 loop result: numerical PASS in fixed convention

The user locally reran the same Majorana A/B integrated \`SigmaS\`
numerical stage after regenerating the E3 reference with the exact
analytical finite B0 integral. SARAH 4.15.4 initialized the isolated
\`ZeeTypeIIMajoranaAudit\` model, generated the 1-loop diagrams and
physical vertices, and evaluated the complete complex symmetric 3x3
neutrino scalar self-energy at two independent complex Yukawa
realizations \`A1b_original\` and \`B2_second_null_root\`.
These two Yukawa realizations share the *same targeted neutrino matrix*,
but differ in charged-Higgs masses, mixing angle and flavor decomposition.

Observed status:

\`\`\`text
MAJORANA_AB_SARAH_3X3_FINITE_B0_NEGCONJ_MATCH_PHASE_SIGN_DERIVATION_PENDING
\`\`\`

Observed acceptance diagnostics:

\`\`\`text
A1b:  72 complex physical vertices, max residual = 0
B2:   72 complex physical vertices, max residual = 0
A1b:  max abs[-Conjugate(M_SARAH) - M_E3] = 2.5084101472715546e-15 eV
B2:   max abs[-Conjugate(M_SARAH) - M_E3] = 7.008283073000786e-16 eV
A1b:  relative complex residual = 8.183918101628462e-14
B2:   relative complex residual = 2.2863808155204075e-14
A1b:  SigmaS matrix symmetry = 2.3120400991731073e-25 GeV
B2:   SigmaS matrix symmetry = 1.2431919375586428e-24 GeV
Both: W gauge-sector scalar self-energy = 0
Both: renormalization scale variation <= 1.2652e-21 GeV
Both: rMS scheme-switch variation = 0
Both: f=0 and gamma=0 nulls = exactly 0
Both: charged-mass-degenerate and YD=0 nulls <= 4.047e-21 GeV
\`\`\`

This result **numerically validates the independent, SARAH-generated
one-loop mass-type self-energy** against the exact E3 finite kernel
within a FIXED \`-Conjugate\` comparison convention at TWO complex
synthetic Yukawa realizations. It does **not** by itself prove the
corresponding relative field-phase/charge-conjugation choice is
equivalent for CP-odd physical observables, and does not validate
any of the E3 309 optimized candidate points or flavor likelihoods.

The previous 120-point Gauss-Legendre reference was underresolved;
the exact finite kernel eliminated an artificial ~3e-7 eV
difference. The sign/conjugation relation was not selected by
a best-of-four optimization in the latest test.

### Independent amplitude-level sign/conjugation derivation (SARAH source)

Source: upstream SARAH \`Package/loopCorrections.m\`,
\`AddLoopFermion\`, \`FFS\` contribution:

\`\`\`
SigmaS_raw = Sum[m_internal * Cp[...][PR] *
                 conj[Cp[...][PL]] * B0 * diagram_symmetry *
                 diagram_coefficient]
\`\`\`

For a Majorana external \`Fv\`, \`AddLoopFermion\` multiplies by 2.
Each of the two charge-conjugate FFS diagrams carries a factor 1/2:
thus **2 × (1/2) = 1 per charged diagram orientation**. No
additional factor 2 should be inserted.

At the fixed diagonal lepton basis and real charged scalar mixings,
the independently SARAH-validated vertices are

\`\`\`
gL(Fv_i,bar(Fe_l),Hm_k)       = -i * D_(l i,k)
gR(Fv_i,bar(Fe_l),Hm_k)       = -i * conj(fSARAH_(i l)) * ZP_(k3)
gL(Fv_i,conj(Hm_k),Fe_l)      = -i * fSARAH_(i l) * ZP_(k3)
gR(Fv_i,conj(Hm_k),Fe_l)      = -i * conj(D_(l i,k))
D_(l i,k) = ZP_(k1) Ye_(l i) + ZP_(k2) Ye2_(l i).
\`\`\`

Consequently the sum of the two physical FFS loop orientations is

\`\`\`
SigmaS_ij_raw = Sum_(l,k=H1,H2) [
 m_l B0fin(0;m_l^2,m_Hk^2) ZP_(k3)
 ( conj(fSARAH_(i l) D_(l j,k)) +
   conj(fSARAH_(j l) D_(l i,k)) )
].
\`\`\`

Write \`YD=-sin(beta)Ye+cos(beta)Ye2\`; the Goldstone-direction
terms drop out of k=H1,H2. The charged scalar mixing satisfies

\`\`\`
ZP_(H1,3) ZP_(H1,D) = +sin(gamma)cos(gamma)
ZP_(H2,3) ZP_(H2,D) = -sin(gamma)cos(gamma).
\`\`\`

By the *finite* Passarino-Veltman identity

\`\`\`
B0fin(m_l^2,mH1^2)-B0fin(m_l^2,mH2^2) =
 - Integral_0^1 dx ln[(x*m_l^2+(1-x)*mH1^2) /
                     (x*m_l^2+(1-x)*mH2^2)]
 = -I_l,
\`\`\`

and the source conversions \`fSARAH=2*fE3\` and
\`YD=sqrt(2)*Y_E3\`, the algebra gives

\`\`\`
SigmaS_ij^SARAH / (16*pi^2)
  = -(sqrt(2) sin(2 gamma)/(16*pi^2))
    Sum_l [m_l I_l (f_E3_(i l) Y_E3_(l j)
                  + f_E3_(j l) Y_E3_(l i))]^*
  = -Conjugate[(Mnu_E3)_ij].
\`\`\`

This derives the **self-energy contraction orientation** and
the relative minus sign from SARAH's FFS rule, vertex chirality
and finite B0 ordering—rather than simply fitting a sign after
numerical evaluation.

**Remaining field-theory distinction:** Conversion between a
four-component \`SigmaS\` coefficient, the left-Weyl Majorana
operator \`-1/2 nu_L^T C^{-1} Mnu nu_L + h.c.\`, and external
charge-conjugation/field-phase conventions must still be
documented to establish CP-sensitive observables. A common
Majorana-field rephase can change an overall mass sign;
complex conjugation is NOT generally an innocuous flavor
rephase in the presence of CP violation. The intended production
model still declares \`Fv->{vL,0}\`: the validated Majorana
representation exists in an isolated test variant, not yet in
the production SARAH source.

To make the amplitude-level derivation independently testable,
the existing large \`zee_sarah_e3_majorana_ab_validation.m\`
has been extended again: its new \`zeeABAmplitudeFromCp\` evaluates
the two FFS chirality products with SARAH's actual generated
physical vertices and the independent analytic B0 function,
without inserting \`f Ml Y\` or any E3 reference into the
prediction. It compares this direct chiral contraction with
the original SUMMED SARAH \`SigmaS\` matrix at both points.
Any source Majorana factor, diagram factor or chirality error
fails with \`sarah_amplitude_factor_or_chirality_...\`.
This newly added check **has not yet been run locally**.

The one command for that updated large numeric stage:

\`\`\`bash
cd ~/zee && git pull --ff-only
math -script scripts/zee_sarah_e3_majorana_ab_validation.m \
  2>&1 | tee work/sarah_zee/e3_majorana_ab_console.log
grep -E 'CP_LOOP_AMPLITUDE_DERIVATION|FIXED_NEGCONJ|STATUS|FAIL' \
  work/sarah_zee/e3_majorana_ab_console.log
\`\`\`

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
