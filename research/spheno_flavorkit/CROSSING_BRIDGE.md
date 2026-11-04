# Ordered off-diagonal dipole bridge

**Operator proof: PASS.** The independently differentiated toy gives

\[
 K_{2L}(i,j)=-C_L(i\to j)^*,\qquad K_{2R}(i,j)=-C_R(i\to j)^*
\]

when the operator and wrapper use the same initial mass. No coefficient-map
substitution is applied after projection. This result concerns the tested
scalar one-loop conventions, not complete Zee LFV. Compact source hashes and
results are in `crossing_bridge_evidence.json`.

## Action, conjugation and ordered fields

Use metric +---, `sigma^{mu nu}=i[gamma^mu,gamma^nu]/2`, e>0 and
`X=C_L P_L+C_R P_R`. Start with the actual ordered action

\[
 L_D={e m_i\over2}\bar l_j\sigma^{\mu\nu}X l_i F_{\mu\nu}
     +{e m_i\over2}\bar l_i\sigma^{\mu\nu}X_H l_j F_{\mu\nu},\quad
 X_H=C_R^*P_L+C_L^*P_R.
\]

The HC term has the **same m_i**, including when its flavor ordering is
reversed. HC exchanges chiral projectors because gamma0 P_L gamma0=P_R;
sigma commutes with gamma5. Distinct flavors are essential here.

The source does not assign physical negative-charge particles to the two
incoming placeholders merely because they are named F. Its external fields
are `{bar[ChargedLepton],ChargedLepton,Photon}` while its FeynArts process is
`{F[3],-F[2]} -> V[3]`. Thus the column spinor standing for the first
barred field is a **charge-conjugate Dirac field**. Introduce

\[
 \chi_a={\cal C}\bar l_a^T,\quad
 \bar\chi_a=-l_a^T{\cal C}^{-1},\quad {\cal C}=i\gamma^2\gamma^0.
\]

For Grassmann fields, moving the two fields through one another gives

\[
 \bar\psi\Gamma\eta
 =\bar\eta^c({\cal C}\Gamma^T{\cal C}^{-1})\psi^c.
\]

The transpose reverses matrix order. In particular
`C gamma^T C^-1=-gamma`, `C P_L/R^T C^-1=P_L/R`, and
`C (sigma X)^T C^-1=-sigma X`. Therefore the action in the actual
column-spinor fields of the toy is

\[
 L_D=-{e m_i\over2}\bar\chi_i\sigma X\chi_j F
     -{e m_i\over2}\bar\chi_j\sigma X_H\chi_i F.
\]

This minus is a Grassmann-field identity, not the minus obtained by HC,
not an adjustable spinor phase, and not a sign inferred from a rate.
`crossing_bridge_spinors.py` verifies the entire operator identity with
explicit anticommuting Fock matrices (four particle/antiparticle modes),
including both independent complex chiral coefficients. It also evaluates
`<l_j|L_D|l_i>` directly from those fields and the expanded photon tensor.

## Differentiated vertices and actual FeynArts model

All fields in a vertex have Fourier convention exp(-ipx). For a created
outgoing photon, `p_A=-q`, its external matrix element has exp(+iqx), and
`F_mu_nu=+i(q_mu eps_nu-q_nu eps_mu)`. Functional differentiation of the
second term above with respect to the **ordered** fields
`bar(chi_j),chi_i,A_mu`, followed by the i from iL, gives

\[
 V_{\bar\chi_j\chi_i A}^{\mu}
 =-{i e m_i\over2}[\not p_A,\gamma^\mu]X_H.
\]

The first term gives the same rule with X_H replaced by X. Reversing the
photon Fourier sign reverses these tensor vertices. In the original
negative-charge fields the QED Lagrangian is `+e bar(l) gamma l A`; it is
`-e bar(chi) gamma chi A` in the conjugate fields. Its independently signed
vertex is consequently `-i e gamma^mu`.

`crossing_bridge_toy.py` writes a disposable two-flavor FeynArts classes
model containing **both** of these differentiated vertices, with distinct
masses mI,mJ and a massless photon. It extends Lorentz.gen by the two
commutator structures and their transpose flipping rule, derived by reversing
the two gamma matrices. The physical class coefficients include their i.
CreateFeynAmp generates the external chains, outgoing conjugated polarization,
and its default prefactor; its output is never replaced by a candidate
amplitude. Both process orientations are generated separately.

The model also contains genuine diagonal QED vertices. An auxiliary vector
spurion on the two labeled external states carries exactly that signed
QED Dirac structure. This is a phase reference for the spinors, **not a
claim that QED has a flavor-changing photon coupling**. The true diagonal
channel independently checks the normalization/sign; the spurion lets the
same-state tensor/vector phase be checked with unequal external masses.

## Source-derived phase normalization and extraction

The default FeynArts `CreateFeynAmp` prefactor is
`-I (2 Pi)^(-4 LoopNumber)`. It returns the scattering amplitude M with
the common S-matrix i stripped; the classes vertices still contain their i.
In PreSARAH's generic triangles, `CheckChiralityCoupling` replaces a generic
coupling G by the SARAH/SPheno `coup` coefficient, with **no vertex i**.
The physical class vertex is `i*coup` (e.g. scalar `-i*y` vs stored `-y`,
positive-charge QED `-i*e` vs stored `-e`). All six saved generic triangle
amplitudes are explicitly checked to be homogeneous of degree **three** in G.
Thus to express the physical effective-action toy M in the same amplitude
normalization as the source triangles, use `M_source=M_FA/i^3=i M_FA`.
The loop measure and propagator phases are already in FormCalc and are not
changed. This conversion is derived before coefficient extraction; it is
not a sign chosen from the desired Wilson coefficient.

For forward ordering let `k3=k1+k2`, `eps.k3=0`, and use the source spinors
`vbar(k1,m_i),u(k2,m_j)`. FormCalc emits scalar-chain terms

\[
 M_{FA}\supset-2e m_i C_L^* S_6-2e m_i C_R^* S_7,\quad
 S_a=\bar v_1 P_a u_2\,(k_1\cdot\epsilon),\quad P_6=P_R,\ P_7=P_L.
\]

Its vector-chain terms are retained. In right-projector notation the complete
tensor contribution is

\[
 -e m_i\{2(k_1\cdot\epsilon)\bar v_1X_Hu_2
 +\bar v_1\not\epsilon(m_iX_H+m_jX_{H,swap})u_2\}.
\]

**FormCalc's** `DiracChain[6,eps]` is `P_R epsslash`, equal to
`epsslash P_L`. It is not `epsslash P_R`. The first explicit spinor attempt
read this incorrectly and failed; correcting the evaluator, rather than
changing any vertex or Wilson coefficient, resolves the mismatch. The
identity is stated explicitly in FormCalc75.m:5078–5079.

The actual held `Coefficient` expression is extracted from
`DownValues[CalcAnalyticPenguins2Fermion]` and executed on `M_source`.
`PS sign=-Signature[{1,2}]=-1`; the source divides by i. Since
`M_source/i=M_FA`, the coefficients after the common loop factor cancels are
`OA2lSL=+2e m_i C_L*`, `OA2lSR=+2e m_i C_R*`. The installed wrapper divides
by `-2e m_norm`, giving

\[
 (K_{2L},K_{2R})(i,j)
 =-{m_i^{operator}\over m_i^{norm}}(C_L^*,C_R^*).
\]

For the reversed **ordered amplitude**, still using the original action's
m_i, the independently generated result is

\[
 (K_{2L},K_{2R})(j,i)=-{m_i^{operator}\over m_j^{norm}}(C_R,C_L).
\]

This proves same-label conjugation in the forward convention and the reverse
mass factor. It does not describe an on-shell physical electron decay into a
muon. The forward and reverse symbolic assertions, independent coefficient
values, Fourier sign and field rephasing assertions all run on the model
output. There is no `cl -> -Conjugate[cr]` substitution after projection.

## On-shell LSZ/crossing check independent of FormCalc algebra

The spinor regression uses m_i=3, m_j=0.7, C_L=0.37+0.83i,
C_R=-0.29+0.41i, noncollinear photon momentum, both spins of each lepton,
and a transverse polarization with a nonzero gauge component. It evaluates
**the numerical scalar and vector coefficients exported from FormCalc**,
not a retyped Gordon identity.

For physical `p_i=p_j+q`, take the analytic continuation `v(-p)=u(p)`.
Forward source ordering uses `(k1,k2)=(-p_i,p_j)`; reverse source ordering
uses `(-p_j,p_i)`. Both satisfy the source Dirac equations. With
`M_D=i e m_i ubar_j sigma(q,eps) X u_i`, the exported forward amplitude
is `-M_D*`, and the reverse one is `-M_D`. Exactly the same common minus
occurs for the independently signed vector reference. The individual spinor
continuation phase is a state convention; QED fixes it consistently for
both tensor and vector. No relative sign in their interference is adjustable.
The HC operation and momentum crossing are computed separately.

There are 16 ordered tensor comparisons, 12 full Fock-operator comparisons,
Ward tests and lepton-field rephasings, with both Fourier signs. Maximum
absolute residuals are approximately 2.0e-15 (spinors), 8.9e-16 (Fock),
1.8e-16 (QED), 2.7e-15 (Ward), and 1.2e-15 (rephasing).
The previous diagonal g-2 anchor is consistent with this result but is not
used to choose any coefficient or phase in this new proof.

## Exact source anchors

Paths below are relative to the recovered pinned toolchain directory; its
actual file hashes and the installed wrapper hash are recorded in evidence.

- `PreSARAH-1.0.3/Input/PhotonLLp.m:4–15`: fields, fermion order, projectors.
- `PreSARAH-1.0.3/PreSARAH_package.m:91–98,154–160`: process, spinors, PS sign.
- Same file `:577–585,638–657,732–749`: coupling replacement, FORM invocation,
  generic amplitudes and exact coefficient extraction.
- `FeynArts-3.9/FeynArts/Analytic.m:10–16,74,90–95`: default prefactor and
  process header/external mass construction.
- `FeynArts-3.9/Models/Lorentz.gen:49–50,218–224,255–257,271–273`: external
  fermions, FFV basis/flipping and outgoing conjugate photon polarization.
- `FeynArts-3.9/Models/SM.mod:690–696,809–815`: physical vertex i conventions.
- `FormCalc-7.5/FormCalc75.m:2592–2608,5078–5079`: spinor and chirality encoding,
  order of the projector and subsequent gamma matrices.
- Installed `SARAH-4.15.4/FlavorKit/LFV/Operators/Photon_wrapper.m:3–22`:
  external fields and negative normalization. Generated
  `LowEnergy_ZeeTypeII.f90:5286–5297,5500–5514` implements it.

## Reproduction and scoped numerical closure

Use the existing recovered directory; no dependency recovery, generator
comparison or loop stress scan is repeated:

```sh
python3 research/spheno_flavorkit/crossing_bridge_toy.py --toolchain /absolute/path/to/the/recovered/d15_projector_directory
python3 research/spheno_flavorkit/crossing_bridge_spinors.py
python3 research/spheno_flavorkit/test_direct_amplitudes.py
python3 research/spheno_flavorkit/physical_card_closure.py
python3 research/spheno_flavorkit/compare_dipoles.py --workdir research/spheno_flavorkit/local/crossing_original_cards --output research/spheno_flavorkit/local/crossing_original_cards/comparison.json
python3 research/spheno_flavorkit/check_components.py --logs research/spheno_flavorkit/local/crossing_original_cards --output research/spheno_flavorkit/local/crossing_original_cards/components.json
python3 research/spheno_flavorkit/check_rate.py --logs research/spheno_flavorkit/local/crossing_original_cards --comparison research/spheno_flavorkit/local/crossing_original_cards/comparison.json > research/spheno_flavorkit/local/crossing-original-rates.json
python3 research/spheno_flavorkit/verify_crossing_closure.py
```

The default toy locates an existing recovered directory containing ampSave.m.
It writes only ignored `local/crossing_bridge/` models, source, chains and logs.
The spinor test reads those freshly exported coefficients. No Mathematica
version recovery or Zee model regeneration is performed.

After the proof, all 102 direct scalar-amplitude cases and 36 transformation
relations pass with the derived map. h/H/A/H1/H2 and coherent sums are
separate, including both chiralities, exact applicable nulls, conjugation,
rephasing, reverse ordering, gamma=0, charged decoupling and degeneracy.
All four original cards were rerun in a new directory, with actual complex
vertex readback and native-rate reconstruction.

Two new full model cards change scalar masses, mixing, F and Ye2, with Ye
and D reconstructed consistently. Both have positive reconstructed spectra,
sufficient BFB and EWPO PASS. Card 0 also has tree unitarity PASS; card 1
has tree unitarity FAIL. The latter remains useful for testing amplitudes but
is not an accepted model point. No new neutrino fit or vacuum certificate is
asserted. The unchanged generated executable evaluates both cards in two
input schemes. All per-scalar matched-input residuals are below 6.8e-11.

Replacing only SPheno's default electron/muon pole inputs by the D12 values
changes the coherent coefficients by up to 1.4e-7. On those same cards it
reduces the five-scalar coherent comparison with the physical-input D12
calculation to at most 3.7e-11. The full native K differs from the sum of
those five groups by a measured remainder up to 1.5e-24 GeV^-2 across the
original/new cards. It is retained explicitly; both that reconstruction and
the full native K versus the matched D12 coefficients pass the mixed
relative/absolute criterion below. A relative-only test on a tiny chirality
would misclassify this remainder (up to 7.4e-9 relative on the new cards).
The controlled 1.4e-7 pole-input shift is an input mismatch, not a loop error.
Per-point lepton-only, scalar-only and full readback shifts are also recorded.
The extra SMINPUTS rows require comment tokens because the actual reader
reads three fields; omitting them caused a preserved EOF failure. Using
long absolute output paths also exposed SPheno's character(120) filename
truncation; passing basenames with the isolated working directory fixes it.
Neither failure required changing generated code.

The matched computational criterion is `abs(delta)<=1e-10 abs(C)+1e-24
GeV^-2` per chirality, with exact nulls checked separately. It covers the
measured loop/equality approximation errors, including small electron loops;
it is not a universal uncertainty for arbitrary future mass ratios. Native
rates reconstructed from complex amplitudes, measured masses/alpha/GammaMu
agree within the 5e-9 printed-rounding criterion. The native rate omits the
physical daughter phase-space factor; this is recorded, not absorbed into a
phase or tolerance. The scalar loop calculation uses massless neutrinos and
neglects external momenta in loop denominators while retaining external
chirality flips. No uncomputed two-loop terms or complete Zee acceptance are
included. The experimental loop patch remains mandatory.

**Scoped decision: ONE_LOOP_COMPLEX_DIPOLE_PASS** for this source-bound,
experimentally patched scalar one-loop subset and these matched inputs.
This is neither a validation of all FlavorKit observables nor
`COMPLETE_ZEE_LFV_PASS`, and no D14 integration is performed.
