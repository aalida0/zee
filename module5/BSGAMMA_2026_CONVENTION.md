# Gate C1: direct 2026 EFT convention audit (2026-10-27)

**GATE_C1_NUMERICAL_DIAGNOSTIC_PASS; EXTERNAL_CONVENTION_PASS**, restricted
to the real, leading-top, ms=0 charged-scalar LO dipoles already derived in
Gate A2. **2026_LINEARIZED_FLAVOR_FILTER_READY: false.** This is no full Zee
BR, likelihood, exclusion, allowed label or individual charged-mass bound.
Frozen production/contract UNKNOWN labels remain historical; this consumer's
new source bridge does not rewrite previous evidence or certify HyperIso's
generic observable/injection implementation.

## Independent operator bridge

The versioned sources inspected, with downloaded-byte SHA256 values in
[`linear_2026.json`](../validation/module5/linear_2026.json), are:

1. [Misiak et al., 2608.29863v1](https://arxiv.org/html/2608.29863v1),
   Eq.(2), Sec.IV Eq.(4), Fig.3 and references 42/43. Eq.(2) has
   `Q7=e mb/(16 pi²) (bar s_L sigma b_R) F`,
   `Q8=gs mb/(16 pi²) (bar s_L sigma T^a b_R) G^a`.
2. Its **reference 42**, [Bobeth–Misiak–Urban (BMU), hep-ph/9904413v1](https://arxiv.org/html/hep-ph/9904413v1),
   Sec.2 Eqs.(4),(5),(9)–(11), the displayed LO scalar matching formulas,
   normalization N/R1/R2, and Appendix B g1/g2. Eq.(9) explicitly has
   `L_eff = L_QCD×QED + kappa sum C_i P_i`,
   `kappa=4 GF/sqrt(2) Vts* Vtb`; Eq.(10) has **P7=Q7, P8=Q8**,
   with `g3=gs`. Thus `H_eff=-kappa sum C_i Q_i`, since the interaction
   Lagrangian is `-H_eff`. Eq.(11) starts at alpha_s^0, exactly the order
   requested for DeltaC7/8 by 2026 Eq.(4). There is no sign, 4, 16 pi²,
   electric-charge or alpha_s multiplier to apply to the frozen shifts.
3. [Florentino–Romao–Silva, 2106.08332v1](https://arxiv.org/html/2106.08332v1),
   Sec.IV.C.1 Eqs.(62)–(64), Appendix A.3 (rendered (90),(91), called
   (A6),(A7) in earlier evidence), fixes the two-state weighted structure.
   Its reference 16, [Borzumati–Greub, hep-ph/9802391v1](https://arxiv.org/html/hep-ph/9802391v1),
   Eq.(6), Eqs.(10),(11), Sec.3.1, independently fixes the same positive
   Yukawa Lagrangian, negative Hamiltonian, running mb operator mass and
   ordinary/effective coefficient relation. The 2021 rendered Eq.(90)
   contains an extra X_k in its up-quark term; we do not adopt that literal
   typo: the cited 1998 Eq.(6), 2021 Eq.(91), and native vertices agree.
4. The 2026 **reference 43**, [Hermann–Misiak–Steinhauser, 1208.2788v2](https://arxiv.org/html/1208.2788v2),
   Sec.2.1 Eqs.(3),(4), instead uses inverse-gs-normalized dipoles via
   [hep-ph/0401041v1](https://arxiv.org/html/hep-ph/0401041v1), Eqs.(2.1),(2.2).
   At leading order in renormalization, `P7,8=Q7,8/a_s`,
   `a_s=alpha_s/(4 pi)`, so `C_Q=C_P/a_s` and
   `C_P=a_s C_H(1)+...` implies `C_Q_LO=C_H(1)`.
   Feeding those rescaled C_P directly into Eq.(4) would be wrong.
   Eq.(4) of the 2012 source specifies `r=mt_MSbar(mu0)^2/M_H+^2`.

The needed bridge is source 2's explicit **Lagrangian plus operator plus
matching result**, cited directly by source 1. Agreement with HyperIso or a
qualitative enhancement alone would not supply it.

## Trace from the native amplitude to that source

The independent native proof remains
[`NATIVE_OPERATOR_MATCHING.md`](NATIVE_OPERATOR_MATCHING.md); it is not rerun.
Its physical scalar vertex follows from
`L_Y=sqrt(2)/v H_k+ bar u V (mt Y_k PL+md X_k PR) d+h.c.`,
`(X_k,Y_k)=a_k(tan beta,cot beta)`, `a=(cos gamma,-sin gamma)`.
The Feynman rule is i times this Lagrangian. In BMU Eq.(4), choose
`psi=t`, `phi=H_k-`, `C_ijk=delta_jk`, and

```
S_L=sqrt(2)/v mt Y_k Vts,  B_L=sqrt(2)/v mt Y_k Vtb,
S_R=sqrt(2)/v ms X_k Vts,  B_R=sqrt(2)/v mb X_k Vtb.
Qpsi=2/3, Qphi=-1, kappapsi=4/3, kappaphi=0, xi=1.
N=xi sqrt(2)/(8 M_k² GF Vts* Vtb), x=mt²/M_k².
N R1=x |Y_k|²/2, N R2=x X_k Y_k*/2   (ms=0, real X/Y here).
```

BMU's `D=partial+i e Q A+i gs T G` gives the native `-i e Q gamma`
fermion current. Its phi* is H+, explaining the negative Qphi and the
scalar attachment sign. Substitution into its LO matching gives

```
g1(x)=-x log(x)/(2(1-x)^4)+(x²-5x-2)/(12(1-x)^3),
g2(x)=log(x)/(1-x)^3+(3-x)/(2(1-x)^2),
C7_k=x/2 { |Y_k|² [2 g1(x)/3+g1(1/x)/x]
                       +X_k Y_k* [(2/3-x)g2(x)-1/2] },
C8_k=x/2 { |Y_k|² g1(x)+X_k Y_k* g2(x) }.
```

These are an independent published-source substitution, not a new loop
calculation or a fit to the frozen four kernels. For comparison with the
existing native proof, let `D=1+(x-1)t`. Its four already-derived integrals
obey `g1=-1/2 int t²(1-t)/D`,
`g1(1/x)/x=-1/2 int t(1-t)²/D`, `g2=-int t²/D`, and
`x g2+1/2=int t(1-t)/D`, all over [0,1]. Inserting them reproduces
the native signed projections exactly. With kappapsi/kappaphi above,
BMU's color expression reduces to g1/g2 on the open quark line:
no extra Nc, trace or Casimir multiplies C8. At x=1 the finite limits
are `g1=-1/24`, `g2=-1/3`.

Use the native representation `sigma^{mu nu}=i[gamma^mu,gamma^nu]/2`,
metric (+---), outgoing `A=epsilon* exp(+iqx)` and
`F_mu nu=i(q_mu epsilon*_nu-q_nu epsilon*_mu)`.
`bar s_L sigma b_R=bar s sigma PR b` has no additional projector factor;
antisymmetry supplies two. With L=-H the insertion is
`iM7=+2 kappa e mb/(16 pi²) C7 bar s sigma^{mu nu} q_nu PR b epsilon*_mu`;
Q8 replaces e by gs and inserts T^a. This agrees with the native projection
under the source-normalized scalar substitution above. The Letter does not
spell out the sigma commutator or Fourier convention. Those are not a new
physical sign uncertainty: a simultaneous sigma/Fourier/basis redefinition
transforms operators and matching coefficients inversely and leaves C Q,
SM–NP interference and Eq.(4) invariant after transforming its slope too.
An isolated sign flip with the published coefficients/slopes held fixed is
not such a convention change. The explicit source bridge fixes that relative
normalization; no missing global notation choice is used to demand a new
spinor calculation.

Both native/source products retain `Vts* Vtb`; dividing by kappa cancels
that factor, not its physical phase by setting CKM to one. Under
`q -> exp(i theta_q) q`, the CKM product and `bar s b` transform inversely.
The h.c. has conjugate CKM and exchanged projectors. Primed terms and
ms-suppressed pieces are omitted, not reidentified as Q7/Q8. At this
alpha_s^0 charged-scalar order `DeltaC1..6=0`, hence the finite
`C7eff=C7+sum y_i C_i`, `C8eff=C8+sum z_i C_i` redefinition gives
**DeltaC7eff=DeltaC7, DeltaC8eff=DeltaC8**. This is not an identity for
total SM coefficients or higher-order matching.

## Executed numerical diagnostic

The test's independent 70-digit BMU substitution checks 32 one-state
mass/tanbeta points (64 dipoles), including x=1 and heavy masses.
Maximum absolute residual against frozen LO: **5.551115123125783e-17**
(test tolerances 3e-13 relative / 2e-15 absolute, numerical only).
Two-state weighted matching and gamma endpoints also pass. Sec.IV/Fig.3
of the 2026 paper says Type-II enhances the rate, with enhancement decreasing
with tanbeta and decoupling with mass. The source substitution plus Eq.(4)
passes all three trends; this is a separate cross-check, not the operator proof.

At tanbeta=50 and reference mt_MSbar(160), the Eq.(4) values are:

| M_H+ [GeV] | DeltaC7_LO | DeltaC8_LO | Eq.(4) x 10^4 |
| --- | --- | --- | --- |
| 1000 | -0.0269714884095623 | -0.0316508194128120 | 3.83789313629705 |
| 2000 | -0.00963782265682371 | -0.0120575882442728 | 3.64806226141720 |
| 5000 | -0.00218524877288788 | -0.00287920374404645 | 3.56481554714442 |

These reproduce the **published linear formula with LO matching**, not
digitized central points on the paper's higher-order Fig.3 curve. That curve
includes NP matching through alpha_s²; its exact input list is referred to a
companion paper. No quantitative NNLO curve agreement is claimed.

The existing validated, unmodified HyperIso helper was executed read-only,
without patching, using pinned `reproducibility/inputs/thdm_reference.lha`
(SHA256 `984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374`).
It returned **mt_MSbar(160)=163.96892236746697 GeV**, matching historical
Gate B/C0. This is a specified reference input, not a new calibration to the
2026 paper's SM fit. The distinct mt=163 GeV example remains illustrative.

For mH1=550, mH2=900 GeV, tanbeta=5.3, gamma=1.09 and this reference top:

```
DeltaC7 = -0.03737804303348145
DeltaC8 = -0.04231149396472201
C7 term x 10^4 = +0.3180871462149272
C8 term x 10^4 = +0.09139282696379955
Eq.(4) x 10^4 = 3.9494799731787267
zero NP x 10^4 = 3.54
```

18 tests pass (11 direct diagnostic/source tests, 7 frozen contract tests),
no skips/failures/errors. Tests include interchange, gamma endpoints, separate
signed terms, genuine 81-GeV rejection, missing/scheme-tampered top inputs,
duplicate/nonfinite JSON, coefficient/metadata tampering including False=0
confusion, and original input hash verification. Original byte hashes cannot
be authenticated from reconstructed JSON alone: optional `--source-input`
checks them; without it the diagnostic explicitly reports NOT_VERIFIED.
The actual reference and illustrative runs use that option. The six explicit
inputs are required; no mass running or scheme conversion is silently done.

## Reproduction and remaining barriers

```
python -m unittest discover -s tests -p 'test_module5_bsgamma_2026_linear.py' -v
python -m unittest discover -s tests -p 'test_module5_two_state_patch_contract.py' -v
mkdir -p validation/module5/local
python -m module5.hyperiso_patch_contract --input module5/example_bsgamma_input.json --output validation/module5/local/2026_contract.json
python -m module5.bsgamma_2026_linear_diagnostic --input validation/module5/local/2026_contract.json --source-input module5/example_bsgamma_input.json --output validation/module5/local/2026_conditional.json
```

For the reference run, copy the example six-field JSON to
`local/2026_reference_input.json`, change only mt_MSbar_GeV to the explicit
helper value above, and use the same commands with `2026_reference_contract`
and `2026_reference_conditional` and the original `--source-input` path.
All inputs, resulting diagnostics and hashes are embedded in linear_2026.json;
downloaded papers and generated contracts remain ignored locally.

Uncomputed: O(DeltaC²), NP NLO/NNLO, mass/scheme matching and scale uncertainty,
additional LEFT operators, light-quark and finite-ms/primed effects. Neither
published sigma (SM 0.14, experiment 0.19 in units 1e-4) supplies a correlated
Zee NP uncertainty. Next: justify an accuracy/validity envelope against a
nonlinear treatment, calibrate matching inputs/NP errors, account for other
operators, and document covariance/statistical treatment before a scan filter.
No arbitrary shift threshold or 95% CL prescription is added.

HyperIso v1.0.3 peeled `09d26ac6e71d1528922097a896d15693589f636b` stays a
matching cross-check. Historical R1–R7 PASS is not rerun. C0's SM mode forced
BSM to zero and THDM+patch doubled it; neither is retried or repaired here.
Its archived R3 baseline is not mixed into the updated SM value. The 2026
670-GeV one-state Type-II bound is never imposed on either Zee charged mass.
