# ZeeTypeII SARAH model — first source implementation (2026-10-21)

**Status: SOURCE_IMPLEMENTED_NOT_VALIDATED.** Neither SARAH Start nor
CheckModel has been run for this new ZeeTypeII model. The prior successful
run was for the *upstream THDM-II*, not the Zee model.

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

## Local validation

From the checked-out repository on the local machine:

```bash
cd ~/zee
git fetch origin
git switch feature/global-scan-priority1
git pull --ff-only
python3 -m unittest tests/test_zee_sarah_source.py -v
set -o pipefail\nmath -script scripts/zee_sarah_check.m 2>&1 | tee work_sarah_console.log
```

The script first locates and loads an installed `SARAH.m` from the local\nMathematica application directories (including\n`~/.Mathematica/Applications/SARAH-4.15.4/SARAH.m`). This avoids\ninteractive-versus-`math -script` differences in `$Path`.\nThe runner tests the loaded SARAH package state instead of incorrectly\nconsidering nonfatal `General::shdw` messages to be load failures.\nIt also avoids defining a pre-SARAH symbol named `s` in `Global``. It initializes\n`work/sarah_zee/checkmodel_status.txt` even if SARAH loading fails.\n\nThe script then prepends the *repository* `models/SARAH` directory to
`SARAH[InputDirectories]` and does not copy files into a Mathematica
installation. Mathematica message text is written to
`work/sarah_zee/checkmodel.log`, status to
`work/sarah_zee/checkmodel_status.txt`.

A process exit code of zero only establishes **completion**, not physics
validation. Inspect **all** messages in the console and log and classify
them before promoting the model to `SARAH_CHECKMODEL_PASS`.

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
