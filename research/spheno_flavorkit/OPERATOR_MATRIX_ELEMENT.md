> Continuation (2026-11-04): the official projector has now been regenerated
> through FeynArts/FormCalc and compared symbolically; an actual-source tensor
> toy and a signed generated scalar/pseudoscalar magnetic-moment anchor run.
> See [PROJECTOR_REPRODUCTION.md](PROJECTOR_REPRODUCTION.md). The historical
> missing-toolchain statements below are superseded. The complete ordered
> off-diagonal crossing bridge is still not certified.

# Explicit dipole matrix-element check — partial

The overall operator map is **not established**. This note records identities
that can be checked independently of any numerical benchmark and precisely
identifies the remaining crossing/sign question. Run
`python3 research/spheno_flavorkit/operator_amplitude_test.py`.

Use metric `+---`, `sigma^{mu nu}=i[gamma^mu,gamma^nu]/2`, and
`F_{mu nu}=+i(q_mu epsilon_nu-q_nu epsilon_mu)` for an outgoing-created
photon. For `p=k+q`, `p²=m_i²`, `k²=m_j²`, `q²=q.epsilon=0` and
`X=C_L P_L+C_R P_R`, the D12 Lagrangian matrix element is

```
e m_i/2 ubar(k) sigma^{mu nu} X u(p) F_{mu nu}
= i e m_i ubar(k) sigma(q,epsilon) X u(p)
sigma(q,epsilon) = i qslash epsilonslash
ubar(k) sigma(q,epsilon) X u(p)
 = i [2 p.epsilon ubar(k) X u(p)
      - ubar(k) epsilonslash (m_i X_swapped + m_j X) u(p)] .
```

`X_swapped=C_L P_R+C_R P_L`. The opposite Fourier sign reverses this
matrix element. The Hermitian-conjugate operator has
`X_dagger_dirac=C_R* P_L+C_L* P_R`. Thus reversing the bilinear exchanges
chirality and conjugates the coefficients. An independently normalized
reverse operator would require a factor `m_i/m_j`.

The recovered `PreSARAH-1.0.3/Input/PhotonLLp.m:4-15` declares
`Op[6/7] Pair[ec[3],k[1]]`; `PreSARAH_package.m:91-95,154-158,246-249,726-749`
constructs `DiracChain[Spinor[k1,m1,-1],6 or 7,Spinor[k2,m2,1]]`, and
includes `PS sign=-1` and division by `I`. Unlike the names SL/SR, the
[FormCalc 8 manual](https://feynarts.de/formcalc/FC8Guide.pdf), p. 20,
identifies 6 as `P_R` and 7 as `P_L`, and `-1` as an antiparticle spinor.
The explicit test uses exactly that algebraic projector order with analytically
crossed `k1=-p`, `k2=k`, `q_cross=k1+k2=-q`. With `vbar(k1)` and `u(k2)`,

```
vbar(k1) sigma(q_cross,epsilon) X_dagger_dirac u(k2)
 = -i [2 k1.epsilon vbar(k1) X_dagger_dirac u(k2)
       + vbar(k1) epsilonslash (m_i X_dagger_dirac
                                    + m_j X_dagger_swapped) u(k2)] .
```

Both independent complex coefficients, two spin states, gauge invariance,
on-shell equations, both photon signs, Hermitian conjugation and the above
crossed identity are tested. The gauge-restoring vector term is retained;
matching only `k1.epsilon` without accounting for it is insufficient.

**Remaining issue:** the analytic spinor continuation has an arbitrary
external-state phase. The installed 2015 `Gamma2l.m:1-5,34-38,70-72,128+`
contains reduced expressions, not the original FormCalc chains or the exact
PreSARAH source that generated them. The recovered 1.0.3 archive is not shown
to be that source. In particular the relative sign between the recovered
`PS sign`, the photon/fermion crossing and the installed generated coupling
conventions has not been independently fixed. The test therefore does not
assert `K=-C*` or any alternative. A concrete next step is a FormCalc
single-diagram calculation using the installed SARAH generic vertices, with
both the pre-projection complex `DiracChain` and emitted OA coefficient
printed, followed by the same explicit spinor comparison with the exact
FeynArts external-state phases. The local FormCalc/FeynArts installation and
original generation input were not found. This is a bounded missing trace,
not evidence that the physical correspondence fails.
