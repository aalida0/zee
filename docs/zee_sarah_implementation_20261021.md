# ZeeTypeII SARAH model — first source implementation (2026-10-21)

**Status: SARAH_INITIALIZED_CHECKMODEL_COMPLETED_WARNINGS_UNRESOLVED.**
User's first local SARAH 4.15.4 run (2026-10-21) initialized ZeeTypeII
in 6.21 s and completed CheckModel in 4.02 s. This is not
SARAH_CHECKMODEL_PASS and not model/physics validation.
See `work_sarah_console.log` and `work/sarah_zee/checkmodel.log`
on the local machine. The log reports `PossibleTerms::NonSUSY`
and seven missing gauge-eigenstate fermion metadata entries. The
metadata was subsequently corrected in source, pending local rerun.

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
antisymmetric lepton-doublet coupling. In the mass basis:
`M_e=(v1 Ye + v2 Ye2)/sqrt(2)` up to basis/index conventions.
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
