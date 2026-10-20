# ZeeTypeII SARAH model — first source implementation (2026-10-21)

**Status: SARAH_TREE_SCALAR_AND_CHARGED_GAUGE_BENCHMARK_TESTS_PASS; FULL_ZEE_NOT_VALIDATED.**
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
