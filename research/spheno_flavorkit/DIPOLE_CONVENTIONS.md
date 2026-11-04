**Current status: ONE_LOOP_COMPLEX_DIPOLE_PASS**, scoped to the experimentally
patched scalar one-loop subset, massless neutrinos and the external-momentum
expansion described in [CROSSING_BRIDGE.md](CROSSING_BRIDGE.md). The ordered
operator map is now derived and independently tested: `K2L=-conj(C_L)`,
`K2R=-conj(C_R)` for matched mass normalization. The reversed ordered
amplitude has the explicit initial/daughter mass factor.

The proof uses differentiated HC vertices in a disposable FeynArts model,
actual source phase normalization, and independent Fock/Dirac-spinor tests
with a signed QED reference. No post-projection candidate substitution is
used. Two new full physical-input cards and controlled pole-input variants
close separately by scalar and coherently; one new card passes all cheap
scalar gates, while the other's tree-unitarity failure is recorded.
This does not certify complete Zee LFV or other FlavorKit observables.
See [crossing_bridge_evidence.json](crossing_bridge_evidence.json).

The checkpoint material below is historical. Its statements that the
projector/crossing proof is missing are superseded by CROSSING_BRIDGE.md.

---

> Continuation (2026-11-04): the official projector has now been regenerated
> through FeynArts/FormCalc and compared symbolically; an actual-source tensor
> toy and a signed generated scalar/pseudoscalar magnetic-moment anchor run.
> See [PROJECTOR_REPRODUCTION.md](PROJECTOR_REPRODUCTION.md). The historical
> missing-toolchain statements below are superseded. The complete ordered
> off-diagonal crossing bridge is still not certified.

# D15 operator and charged-vertex audit

**Overall: NOT_EVALUATED.** The source inspection below fixes several pieces
of the conversion but does not fix the full complex map. In particular,
`K2L=-conj(C_L)` and `K2R=-conj(C_R)` remain numerical candidates, not a
derived result. Neither same-label nor exchanged-label mapping is certified.
The missing step is to trace the original PreSARAH form-factor projector,
external spinors, momentum flow, photon polarization and its Fourier/sign
conventions into the generated OA2lSL/SR expressions. The generated wrapper
and a rate alone cannot resolve that step.

## Operator algebra and source anchors

The frozen operator is `L=e m_i/2 bar(l_j) sigma^{mu nu}
(C_L P_L+C_R P_R) l_i F_{mu nu}+h.c.`, with `e>0`,
`sigma=i[gamma,gamma]/2` ([Module 4](../../module4/CONVENTIONS.md),
[Module 3](../../module3/CONVENTIONS.md)). Its coefficients have dimension
GeV^-2. For distinct flavors, the Hermitian conjugate of the L term is
`e m_i/2 C_L* bar(l_i) sigma P_R l_j F`; L and R exchange under
Hermitian conjugation because `gamma0 P_L gamma0=P_R` and sigma commutes
with the projectors. Reversing external order therefore conjugates and swaps
the chirality of the operator; if the reverse transition is separately
normalized by `m_j`, the coefficient also carries `m_i/m_j`. These facts do
not by themselves establish which external ordering the generated projector
calls L, nor the common sign relative to the frozen photon convention.

The installed SARAH 4.15.4 source
`FlavorKit/LFV/Operators/Photon_wrapper.m` specifies external fields
`{bar[ChargedLepton], ChargedLepton, Photon}`, associates OA2lSL/SR with
K2L/R, and divides each by `-2 e_MZ m_i(MZ)`; generated
`Observables/LowEnergy_ZeeTypeII.f90:5286-5297,5500-5514` confirms this for
the executable. Its `Calculate_LLpGamma` in
`Observables/FlavorKit_Observables_ZeeTypeII.f90:100-148` indexes `(i,j)`
and computes `alpha(0) m_i^5 (|K2L|²+|K2R|²)/4`, using pole `mf_l`
and no daughter-mass factor. Module 3 includes `(1-m_j²/m_i²)^3` and a
specified lifetime. These rate formulae fix the magnitude normalization in
the massless-daughter limit, not the sign, conjugation or chirality labels.
The raw OA coefficient includes the electromagnetic vertex and a mass; the
wrapper explicitly removes both, with its own negative half. No additional
factor of e or m_i should be assumed from the rate without tracing the
projector. At mu to e the missing phase-space factor alone is approximately
7.02e-5 in the rate.

For charged lepton field phases `P`, Module 3 records `F -> P F P`,
`D -> P* D P`, and `C(i->j) -> P_j* P_i C(i->j)` in its convention.
The mass term requires the same phase on left and right for each charged
lepton. A scalar eigenstate phase multiplies both of its vertices and cancels
in exchange. Such phases must be propagated to both calculations; adjusting
an arbitrary phase independently at each benchmark would not validate a map.

## Charged-scalar source comparison

The generated `Couplings_ZeeTypeII.f90:3850-3911,4110-4171` supplies both
orientations and L/R coefficients. For identity charged-lepton rotations,
antisymmetric F, real ZP and row `r`, define `s=ZP(r,3)` and
`X=ZP(r,1) Ye+ZP(r,2) Ye2`. With neutrino index k and charged index a,
the generated coefficients reduce to

```
Fv Fe conj(Hm):  L=-s F[k,a],       R=-X[a,k]*
bar(Fe) Fv Hm:   L=-X[a,k],         R=-s F[k,a]*
```

For the frozen rows `(-sin(beta) d, cos(beta) d, s)`,
`X=d D`, giving exactly the Module 3/Module 0 expressions
`L=-s F`, `R=-d D*` and the Hermitian-conjugate orientation. The physical
rows `(d,s)=(cos(gamma),sin(gamma)),(-sin(gamma),cos(gamma))` cover H1 and
H2. The pilot spectrum reported the second physical ZP row with opposite
sign: multiply *both* coefficients for that eigenstate by -1. This is an
algebraic source-level check under the stated rotations, **not** a numerical
comparison of all generated vertex values with the actual ZEL/ZER rotations;
that numerical gate remains NOT_EVALUATED. See
[Module 0](../../validation/module0/CONVENTIONS.md) and
[Module 4](../../module4/CONVENTIONS.md) for frozen vertex conventions.

## Recovered PreSARAH photon projector (continuation)

The official `PreSARAH-1.0.3.tar.gz` archive was recovered from
`https://sarah.hepforge.org/downloads/PreSARAH-1.0.3.tar.gz`; its SHA-256 is
`999142f4d4283bb70b225809e44440fd1ee29e289f1d956c051536e0bf1279bf`.
It was extracted only under ignored `local/`. Its
`PreSARAH-1.0.3/Input/PhotonLLp.m:1-20` explicitly sets external fields
`{bar[ChargedLepton],ChargedLepton,Photon}`, combinations `(2,1),(3,1),(3,2)`,
`FermionOrderExternal={1,2}`, `NeglectMasses={3}` and projectors
`OA2lSL=Op[6] Pair[ec[3],k[1]]`, `OA2lSR=Op[7] Pair[ec[3],k[1]]`.
The archive's `PreSARAH_package.m:91-95,151-160,248-249,258,726-749`
uses the 2-in/1-out FeynArts process `{F[3,{1}],-F[2,{1}]}->V[3]`,
chains `Spinor[k[1],MassEx1,-1]` and `Spinor[k[2],MassEx2,1]`,
`PS\`sign=-Signature[{1,2}]`, and extracts coefficients of the chain times
`Pair[ec[3],k[1]]` from the FormCalc amplitude divided by `I`. The installed
SARAH `Gamma2l.m:70-72` and generated LowEnergy call identify the first
and second array indices, respectively, with the first and second external
fields. The observable uses `(2,1)` for mu-to-e. This is a concrete projector
trace, but the archive predates the December 2015 generation timestamp in
installed `Gamma2l.m`; exact generator-version identity has not been proven.
The spinor crossing and Fourier conventions have not yet been independently
closed, so the numerical candidate remains **unproved**, including its sign.

## Explicit spinor identities

The independent calculation in [OPERATOR_MATRIX_ELEMENT.md](OPERATOR_MATRIX_ELEMENT.md)
verifies the Hermitian-conjugate chirality exchange, outgoing-photon sign,
Gordon reduction and the recovered crossed projector's spinor ordering. The
[FormCalc 8 manual](https://feynarts.de/formcalc/FC8Guide.pdf) specifies
`6=PR`, `7=PL`, correcting any inference from the coefficient names. The
installed generator's total crossing/sign convention remains unresolved; the
numerical mapping remains a candidate.
