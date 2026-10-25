# Module 4 conventions and source conflict

Scientific status is **PARTIAL**. Native vertices and mathematical form factors
pass their stated checks. The implemented two-loop coefficients are
**source-specific candidates**, with `SOURCE_NORMALIZATION_CONFLICT`, and cannot
enter `combine`. The public output's coherent ledger contains only reproduced
Module 3 one-loop components. `two_loop_candidates` contains separate signed
complex coefficients for inspection; no candidate rate is reported. This is
intentional fail-closed behavior, not a complete two-loop prediction.

## Frozen operator and native field routing

GeV and radians; real positive diagonal charged-lepton masses. Keep exactly

```
L = e*m_i/2 bar(l_j) sigma_munu (CL PL + CR PR) l_i F_munu + h.c.
OPERATOR = module3.core.OPERATOR; CL,CR have dimension GeV^-2.
```

The frozen diagonal continuation is `a_i=m_i^2 Re(CL+CR)`, counting the
Hermitian diagonal operator once. The massive radiative width is
`alpha*m_i^5/4*(1-m_j^2/m_i^2)^3*(|CL|^2+|CR|^2)`.
No Module 3 definition, fit, or source file is changed.

The native driver loads `/home/amine/.Mathematica/Applications/SARAH/SARAH.m`
(resolving the installed symlink) and starts the checked-out `ZeeTypeII` once
per fresh run. `SARAH[OutputDirectory]` points inside the ignored local output.
`Fe/Fv` indices 1,2,3 are e,mu,tau; `hh[1,2]` are h,H; `Ah[2]` is A;
`Hm[1]` is G-, `Hm[2,3]` are H1-,H2-. `conj[Hm]` has positive charge.
Every vertex is saved symbolically, including its returned field ordering and
PL/PR or momentum tensor, before numerical substitution. The representative
raw expressions and worst signed residuals are in `native_evidence.json`;
the full raw dump and every complex assertion remain in the local log/JSON.

For `bar(Fe_a),Fe_b,s`, native coefficients are `-i C_ab PL` and
`-i C_ba* PR`. With `S=diag(sqrt(2)*m/v)`,
`Ye=cos(beta) S-sin(beta) D`, `Ye2=sin(beta) S+cos(beta) D`,

```
C_h = cos(beta-alpha) diag(m/v) - sin(beta-alpha) D/sqrt(2)
C_H = sin(beta-alpha) diag(m/v) + cos(beta-alpha) D/sqrt(2)
C_A = -i D/sqrt(2).
```

Both charged orientations are checked. For the positive-charge orientation
the common vertex factor gives `H+ bar(N_b)(L_ba PL+R_ba PR)e_a`, with
`L_ba=-s F_ba`, `R_ba=-d D_ab*`. The two physical charged rows have
`(d,s)=(cos gamma,sin gamma),(-sin gamma,cos gamma)`. There is no extra
Majorana factor two. Native antisymmetric F agrees with `F=2 f_legacy`;
`D=sqrt(2)Y_legacy`. F and Ye2 are nontrivial complex matrices from six valid
unrestricted NO/IO Module 2 family witnesses and three spectra, not external
F16 fixtures. Reverse flavor entries and both charged Hermitian partners are
evaluated separately. Complex quark rotation matrices also test mass routing.

The actual neutral Type-II quark vertices, independently reproduced from the
frozen source, are

```
C_up(h,H,A) = (m/v) (sin(alpha)/sin(beta), cos(alpha)/sin(beta), +i cot(beta))
C_down(h,H,A) = (m/v) (cos(alpha)/cos(beta), -sin(alpha)/cos(beta), +i tan(beta)).
```

CKM cancels in these diagonal neutral vertices; no CKM ansatz enters them.
Relative to the legacy implementation, A is rephased by minus one on **both**
ends. Such a field rephasing cancels from each exchange amplitude. Lepton
rephasing is `F->P F P`, `D->P* D P`, `C_X(i->j)->P_j* P_i C_X`.
Numerical tests retain signed complex coefficients, not only squared rates.

## Gate A normalization arbitration

Raw vertices agree with the Module 3 matrices and charged F,D routing.
The common Lavoura conversion and electric charges fix neutral versus charged
signs. An independent positive parameter integral for a charged scalar and a
massless neutral fermion gives
`a_l=-|R|^2 m_l^2/(96 pi^2 M^2)` (and analogously L). The scalar neutral
one-loop logarithm is positive. Combined with the native vertices these
support Module 3: A1c's F coefficient agrees directly, while legacy A1e neutral
and A1f D require a minus. A global field rephasing cannot repair that old
relative-sign conflict. Full existing signed Module 3 regressions run again.

Differentiating `J^2/(2M^2)` supplies two contracted currents, so the contact
coefficient is the product of the two vertices divided by M^2. A direct
massless chiral contact rate is `M_parent^5 |g_LL|^2/(6144 pi^3)` for distinct
negative leptons. An independent spin/phase-space calculation reproduces it;
the legacy half at the same vertices gives a rate smaller by four. This
arbitrates the implementation discrepancy; it does not claim a correction to
all conventions in Herrero-Garcia Eq.3.9 or change frozen Modules 0–3.

## Gate B: the signed source conflict

Davidson, EPJC76(2016)258, arXiv:1601.01949 Eq.16 has coefficient
`-4 GF/sqrt(2) m_i A_L` multiplying `bar(l_i)_L sigma l_j_R F`.
Taking its Hermitian conjugate routes it to Module 3 CL. Equating Lagrangian
coefficients, including the **minus**, gives

```
C_L = -4 sqrt(2) GF/e A_L*; C_R = -4 sqrt(2) GF/e A_R*.
```

This conversion reproduces the **signed** internal-flip logarithm in
Davidson Eq.18 and Module 3, after retaining/subtracting the separate
external-flip terms. It is not inferred from branching fractions. Applying
it literally to Eqs.21,23 gives the candidate

```
C_L(f,s) = +alpha Nc Q_f^2/(8 pi^3 m_i m_f)
           C_s[j,i] (Re C_s[f,f] f(z) + i Im C_s[f,f] g(z))
C_R(f,s) = +alpha Nc Q_f^2/(8 pi^3 m_i m_f)
           C_s[i,j]* (Re C_s[f,f] f(z) - i Im C_s[f,f] g(z)).
```

CHK Eqs.6–11 independently confirm the complex chiral kernel combination.
However, this is **insufficient to validate its overall physical sign**.
For a real scalar with diagonal SM-strength Yukawas, this candidate's
diagonal continuation is positive. Ilisie, arXiv:1502.04199 Eqs.4,19,25 gives
`F1(z)=-f(z)` and a negative scalar moment. For a pure pseudoscalar the
opposite discrepancy occurs: its `F1_tilde=g(z)` gives a positive moment,
whereas the candidate is negative. Direct parameter integrations give a
Davidson-candidate/Ilisie ratio **-1** in both cases. A common neutral-field
rephasing cannot change either product. The source one-loop scalar limit
agrees, so no silent common redefinition repairs the relative discrepancy.
This audit does **not** identify a definitive paper erratum or a new error in
the frozen foundations. An explicit signed two-loop matching calculation is
needed. Candidate coefficients remain UNKNOWN and excluded.

The old fermion implementation uses the opposite A-to-C sign. After its
common A-field rephasing and exact F,D conversion, its top/bottom/tau complex
amplitudes are minus the literal Davidson candidates. This agreement after
a minus is recorded as a conflict, not as validation of either coherent sum.
Candidates also include electron, muon, up, down, strange and charm loops.
Nominal light-quark loops do not establish precision hadronic contributions.

The direct kernels are
`g=z/2 integral log(u/z)/(u-z) dx`, `f=z/2 integral (1-2u)log(u/z)/(u-z) dx`,
`u=x(1-x)`. Stable removable-limit series and reflection symmetry handle
z=1/4 and endpoint panels. Independent Haber dilogarithms and identities
test small/large z; the direct f integral avoids large-z cancellation.
Errors are absolute quadrature estimates, never mass-scheme uncertainties.

## Gate C: W/photon source subset

The literal Davidson/CHK candidate in Module 3 normalization is

```
C_X(W,s) = -alpha/(16 pi^3 m_i v) C_s^X[j,i] kappa_s K_W(z)
K_W = 3f + 23g/4 + 3h/4 + (f-g)/(2z)
kappa_h=cos(beta-alpha); kappa_H=sin(beta-alpha); kappa_A=0.
```

Here h is the Haber/CHK function (negative), not a Higgs field.
CHK Eq.14 plus Eq.18 supplies the Goldstone term `(f-g)/(2z)`. These are
the source-defined photon subsets with their associated unphysical fields,
not a lone W diagram or full electroweak two-loop result. Native vertices
test `g_sWW = 2 mW^2 kappa_s/v` and the scalar-potential Ward relation
`G_sG+G- = m_s^2 kappa_s/v` using consistent g2,v. Scalar mixing enforces
`sum_s kappa_s C_s[j,i]=0` for j!=i. Consequently mass-independent terms and
degenerate h/H candidates cancel; exact alignment eliminates this subset.
There is no CP-odd WW coupling in this scalar limit.

Ilisie Eqs.21,28 yield a different signed diagonal result: at z=0.413,
the literal Davidson-candidate/Ilisie ratio is about -1.01053. Ilisie's
transverse form-factor construction explicitly discards some gauge-dependent
pieces canceled by other topologies (section4.1). These formulas cannot simply
be interchanged or supplemented with arbitrary finite terms. No fresh R_xi
diagram-by-diagram cancellation or reconciliation is claimed here. The
candidate remains excluded. The old W implementation's kernel agrees;
its coefficient again has the opposite overall A-to-C sign.

## Gates D and E: available evidence and omissions

`trilinears` differentiates the charged mass matrix with respect to the
neutral fields and rotates both charged legs. Native h/H diagonal and
off-diagonal trilinears agree with an independent invariant-polynomial
derivative. A's diagonal charged-scalar couplings vanish; its off-diagonal
ones need not vanish and are retained in the native evidence. Photon charge
is proportional to the identity for the two physical singly charged states;
native off-diagonal photon vertices vanish. One off-diagonal trilinear
therefore cannot close the simple two-photon scalar loop. Z currents can be
off-diagonal and are separately inventoried.

Ilisie Eqs.13,20,27 provide a published diagonal-moment scalar-loop reference.
The implemented **mathematical form factor only** is
`F2=(f-g)/(2z)`; it agrees with a direct parameter integral. The effective
tensor `T_munu=g_munu k.q-k_mu q_nu` obeys both photon Ward contractions.
This is not an explicit scalar-QED diagram/seagull cancellation calculation,
nor a validated LFV dipole mapping. No charged-scalar LFV amplitude is guessed:
**UNKNOWN_NOT_IMPLEMENTED** until that matching and an independent signed
LFV numerical reference close the gate.

Remaining **NOT_EVALUATED** amplitudes: fermion Zgamma (CHK Eq.12), W/Zgamma
and associated Goldstones (CHK Eqs.17,19), mixed charged-current W/Z and
charged-scalar/W topologies (Ilisie Fig.3, Eqs.22–24), CHK set C / additional
bosonic topologies, QED running/radiation, and finite external-invariant or
neutrino-mass corrections. No scheme-dependent finite terms are assembled.
Three-body dipole/non-dipole interference and mu-e conversion are outside
Module 4. Frozen NuFIT archive, global-vacuum, RG and full-phenomenology
limitations remain open. No partial rate implies allowance or exclusion.

## Interface and reproduction

`input.schema.json` v1 accepts `kind=module3_matching_input_v1`, a complete
Module 3 input, its complete matching Module 2 output, and explicit versioned
two-loop nominal masses. An optional complete Module 3 output is schema and
provenance checked and retained verbatim. Frozen source hashes, identities,
scalar provenance, algebraic forward closure, Yukawa mass rotation and every
supplied one-loop complex component are checked. No inverse solver, neutrino
fit or oscillation covariance selection runs inside the interface. Inputs
are provenance/consistency checked, not digitally authenticated.

The W mass must match the same scalar electroweak input. All nine loop masses
are explicit and lepton loop masses must match the external mass convention.
Only `NOMINAL_UNMATCHED` is currently accepted; a precision scheme is not
claimed by attaching a source label. Invalid inputs produce a nonzero CLI
exit without writing a result. Output schema v1 separates coherent included
rows, unvalidated source candidates, and unevaluated topologies.

```
bash scripts/run_module4_validation.sh --all-tests
python -m module4.interface --input module4/example.json \
  --output validation/module4/local/example_output.json
```

The fresh runner starts native SARAH once, runs the entire repository
unittest regression when requested, checks frozen paths, and regenerates
concise results and hashes. `--skip-native` is an offline diagnostic mode
that explicitly reports VERTEX_BLOCKED. Primary PDF hashes are pinned in
`sources.json`; full logs, raw dumps, PDFs and generated witness rules stay
ignored locally. No historical scan modules are imported; tests load only
named pure reference functions by AST.

The full suite also runs the inherited Module 3 branch guard unchanged.
It requires `feature/zee-lfv-module3`, so it fails on the required Module 4
branch. The runner records that exact failure as
`EXPECTED_BRANCH_GUARD_CONFLICT`, counts it in `failures`, and checks the
correct branch/ancestry in a new Module 4 test. Any additional failure makes
validation fail. A successful runner exit does not claim the unmodified
full suite is green; the expected branch conflict remains visible.
