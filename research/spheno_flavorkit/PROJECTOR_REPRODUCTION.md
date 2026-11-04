# Official projector reproduction and independent signed tests

The original external dependency obstacle has been recovered. Official
PreSARAH 1.0.3 plus FeynArts 3.9 and FormCalc 7.5 reproduce the installed
SARAH 4.15.4 photon coefficients. Different archive dates do not prevent this.
The 44 emitted coefficient expressions (tree, waves, and all six triangle
classes, both dipoles and monopoles) agree as exact symbolic polynomials;
their 15 loop-integral assignments also agree. The comparator verifies the
executable Fortran strings against the associated symbolic strings within
each file before comparing the two files. It retains signs, chirality,
external mass labels and integral arguments.

Archives (official sources):

- https://feynarts.de/FeynArts-3.9.tar.gz
- https://feynarts.de/formcalc/FormCalc-7.5.tar.gz
- https://sarah.hepforge.org/downloads/PreSARAH-1.0.3.tar.gz

The hashes are pinned in `reproduce_projector.py`. Place these in ignored
`local/`, the last archive named `PreSARAH-1.0.3.download`, then run

```sh
python3 research/spheno_flavorkit/reproduce_projector.py
```

The script creates a fresh disposable directory, builds only the symbolic
MathLink helpers, runs the original generator, runs the analytic toy, and
compares the regenerated expressions. It needs Wolfram, gcc, SymPy and the
installed SARAH snapshot. It does not change any installed package or model.
MathLink subprocess communication required execution outside this session's
sandbox. No Mathematica license problem occurred.

Recovery attempts and diagnoses:

1. FeynArts 3.5 / FormCalc 7.5 were recovered first. The FormCalc build script
   fails at its legacy `mcc`, absent in the Wolfram 15 installation.
2. Direct `mprep`/gcc compilation succeeds with `MLCONST=const` and the
   installed shared MathLink library. Interface 3 compilation failed because
   the installed header requires interface 4. Static linking failed on newer
   C++/uuid symbols; shared linking succeeds.
3. Old package path discovery uses `File /. FileInformation[...]`; modern
   Wolfram keys differ. Disposable copies use `$InputFileName` instead.
4. FeynArts 3.5 also collides with new System symbols. After renaming those
   internal symbols, a minimal tree amplitude runs through FORM. PreSARAH
   still fails because 3.5 does not implement `DiagramDelete`. The exact
   failed argument is `CreateFeynAmp[DiagramDelete[TopologyList[...],{}]]`.
5. Official FeynArts 3.9 supplies this API. Its obsolete Discard alias is
   renamed in the reproducible disposable build. No physics rule is patched.
6. Default FormCalc momentum elimination retains k2.epsilon in SFF/FSS.
   PreSARAH extracts k1.epsilon and consequently emits zero dipoles for these
   classes. `SetOptions[DeclareProcess,MomElim->2]` fixes the basis before
   projection, yielding exact installed expressions. Setting that option on
   CalcFeynAmp instead was rejected and did not fix the failure.
7. LoopTools symbols must be declared as in the original PreSARAH wrapper,
   on separately parsed lines before loading the package. Global shadow
   symbols otherwise prevent integral substitutions. The final run has no
   such warnings.

## Independent analytic toy

`projector_toy.m` inserts a known tensor vertex into a disposable FeynArts
amplitude, with independent coefficients `cl=2+3i`, `cr=-5+7i`. Fermion
masses are equal for consistent declared external kinematics; the two fields
are distinct. It sends the commutator of actual Dirac matrices through FORM,
retains vector terms, and evaluates the **held Coefficient expression from
DownValues[CalcAnalyticPenguins2Fermion]**, not a Python reimplementation.
For the explicitly inserted raw vertex

```
-i e m/2 vbar2 [qslash,epsslash] (cl PL+cr PR) u1
```

FormCalc produces scalar-chain coefficients `2 i e m {cr,cl}` in the
`{6,7}` basis; source PS sign and division by I give `-2 e m {cr,cl}`.
The wrapper gives `{cr,cl}`. The 16pi² extraction and oo16pi² output factors
cancel for this tree effective vertex. The test also exercises independent
complex values, HC coefficient exchange and both Fourier signs at the
extractor level. These latter checks are algebraic substitutions, not two
new full model calculations. No Zee coefficient or rate enters the test.

**Do not confuse this raw-vertex result with a complete physical D12 map.**
In particular it is not itself `-conj(C)`. Identifying the tensor vertex with
the physical ordered SARAH fields requires the external-state/Wick crossing
bridge. The source fixes the first flavor index to bar(l_i), the second to
l_j, and 6=PR, 7=PL. HC therefore swaps the Lagrangian projectors while the
6/7 naming swaps them back. That identifies the same-label conjugate
candidate; the common sign additionally needs a physical reference.

## Independent physical sign reference

`test_signed_scalar_anchor.py` calls the **actual compiled generated
CalculateGamma2l**, with a diagonal real scalar Yukawa or pseudoscalar
Yukawa and the generated photon-vertex sign. It varies the scalar mass over
100, 1000 and 10000 GeV. It compares signed coefficients, never BRs, against
independent positive/negative magnetic-moment parameter integrals:

```
aS = +y² r/(8pi²) integral x²(2-x)/(1-x+r x²)
aP = -y² r/(8pi²) integral x³/(1-x+r x²), r=m²/M².
```

Both signs require `a=-m² Re(K2L+K2R)` in this generated source, whereas D12
uses `a=+m² Re(CL+CR)`. Replacing r*x² by r*x gives the backend's external
mass approximation. Agreement with that integral is better than 5e-16;
the exact external-mass correction falls from about 1e-6 at 100 GeV to
1e-10 at 10000 GeV. This independently selects the negative diagonal sign.
It does **not alone** determine off-diagonal complex ordering or chirality.

The projector is now reproducible and a same-source physical sign anchor
exists. The remaining proof obligation is to combine the raw tensor toy's
external-state ordering and the SARAH ordered effective vertex in one
explicit crossed amplitude. Until that bridge is demonstrated, the overall
complex map remains open; no external dependency currently prevents it.

## Additional amplitude diagnostics

`test_direct_amplitudes.py` uses seed 151103 to generate six new complex
antisymmetric F and general D matrices, scalar masses and signed mixing
angles. It calls the actual generated API directly, with source-rule
vertices, and compares h/H/A/H1/H2 separately and coherently against frozen
Module3. It runs 102 cases, including reverse coefficients, conjugation,
rephasing, zero-F/zero-D, exact charged/neutral LFV nulls, charged gamma=0,
10x charged decoupling, and degenerate charged masses with different gamma.
The maximum residual relative to the larger chirality is 3.17e-12 under
the still-candidate `K=-conj(C)` conversion. Each chirality must satisfy
`abs(delta)<=1e-10 abs(C)+1e-24 GeV^-2`; exact nulls must be zero.
The relative term accommodates the measured primitive-loop/equality errors;
the absolute term treats tiny amplitudes and zero crossings explicitly.
These are numerical regression criteria for **matched inputs**, not a
physical input-scheme uncertainty or a universal Zee validation tolerance.
The six points are vertex-level amplitude inputs, not certified scalar
vacua or neutrino fits. No model regeneration or Lagrangian edit occurs.

`check_components.py` now also compares H1/H2 with **actual generated
complex vertex readback** at the four original points (maximum relative
residual 2.7e-15). Neutral matched residuals remain below 6.9e-11.
Controlled lepton-mass-only and scalar-mass-only shifts and the full
readback shift are recorded per point. Full-input coherent shifts relative
to the D12 snapshots reach 2.0e-7. These deterministic shifts cannot be
advertised as a general theory/scheme uncertainty envelope.
