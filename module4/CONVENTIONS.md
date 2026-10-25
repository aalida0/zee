# Module 4 conventions

Scientific status is **PARTIAL**. The signed fermion/photon and charged-scalar/photon matching is now
**VALIDATION_PASS** and is included coherently. Its nominal unmatched
mass/Yukawa scheme and omitted physical topologies prevent a full prediction.
W coefficients remain UNKNOWN, excluded from the coherent ledger. Charged-scalar
matching, seagulls and off-diagonal selection are derived independently in
[CHARGED_SCALAR_AUDIT.md](CHARGED_SCALAR_AUDIT.md).

The detailed source-to-equation derivation, disposition of the old -1,
exact W-kernel differences, and scoped gauge checks are in
[MATCHING_AUDIT.md](MATCHING_AUDIT.md). It supersedes the first audit's blanket
two-loop quarantine; the literal Davidson comparison remains recorded.

## Frozen basis and operator

Use GeV, radians, positive real diagonal charged-lepton masses, metric
(+---), sigma_munu=i[gamma_mu,gamma_nu]/2 and e>0. Keep exactly

```
L=e*m_i/2*bar(l_j)*sigma_munu*(CL*PL+CR*PR)*l_i*F_munu+h.c.
```

CL,CR have dimension GeV^-2. The emitted-photon vertex, including its sign,
is derived from i L in the matching audit. The frozen diagonal continuation
is `a_i=m_i^2 Re(CL+CR)`, counting the Hermitian diagonal operator once.
The radiative width is
`alpha*m_i^5/4*(1-m_j^2/m_i^2)^3*(|CL|^2+|CR|^2)`.
No Module3 definition or source is changed.

## Native fields, vertices and phases

The fresh driver loads the installed
`/home/amine/.Mathematica/Applications/SARAH/SARAH.m`, starts the checked-out
ZeeTypeII once, and writes only ignored local output. Every vertex is saved
symbolically with its returned field ordering and projector/momentum tensor
before numerical substitution. Representative raw expressions and worst
signed residuals are in `native_evidence.json`; full assertions and dumps
are in `validation/module4/local/`.

Fe/Fv indices 1,2,3 are e,mu,tau; hh1=h, hh2=H, Ah2=A;
Hm1=G-, Hm2=H1-, Hm3=H2-. conj[Hm] has positive charge. For
`bar(Fe_a),Fe_b,s`, the native rule is `-i C_ab PL-i C_ba* PR`.
With S=diag(sqrt(2)*m/v), Ye=cos(beta)S-sin(beta)D,
Ye2=sin(beta)S+cos(beta)D,

```
C_h=cos(beta-alpha) diag(m/v)-sin(beta-alpha) D/sqrt(2)
C_H=sin(beta-alpha) diag(m/v)+cos(beta-alpha) D/sqrt(2)
C_A=-i D/sqrt(2).
```

Both charged orientations give `H+ bar(N_b)(L_ba PL+R_ba PR)e_a`,
L_ba=-s F_ba, R_ba=-d D_ab*, with physical rows
(d,s)=(cos gamma,sin gamma),(-sin gamma,cos gamma). There is no extra
Majorana factor two. Native F=2 f_legacy and D=sqrt(2)Y_legacy.
Six physically distinct unrestricted complex NO/IO witnesses from Module2
and three spectra are tested, including quark mass rotations.

The native neutral Type-II quark coefficients are

```
C_up(h,H,A)=(m/v)(sin(alpha)/sin(beta), cos(alpha)/sin(beta), +i cot(beta))
C_down(h,H,A)=(m/v)(cos(alpha)/cos(beta), -sin(alpha)/cos(beta), +i tan(beta)).
```

CKM cancels in these neutral diagonal coefficients. The new native photon
checks establish `-i e Q_f gamma_mu` for both chiralities: charged leptons
+i e, up quarks -2i e/3, down quarks +i e/3. The legacy A field is rephased
by -1 at both ends; that sign cancels in exchange. Lepton rephasing is
F->P F P, D->P* D P, C_X(i->j)->P_j* P_i C_X.

## Component arbitration and retained omissions

Native vertices and the common Lavoura charge/operator conversion support
Module3's component signs: A1c F agrees, legacy A1e neutral and A1f D require
a minus. The independent massless-neutral-fermion charged-scalar moment is
`-|R|^2 m_l^2/(96 pi^2 M^2)`. The neutral scalar one-loop logarithm is positive.
A field rephasing cannot repair the legacy relative-sign conflict.

The contact coefficient from J^2/(2M^2) is the product of the two vertices
divided by M^2 after the two contractions. An independent direct massless
chiral contact rate is `M_parent^5 |g_LL|^2/(6144 pi^3)` for distinct negative
leptons. The legacy half at the same vertices produces a rate smaller by
four. This resolves the implementation comparison, not all possible paper
conventions. Frozen Modules0–3 and their tests remain unchanged.

For charged scalars the native diagonal/off-diagonal h/H trilinears agree
with an independent potential-polynomial derivative. A's diagonal couplings
vanish, but its off-diagonal couplings need not. Photon charge is the identity
in the charged mass basis; off-diagonal photon vertices vanish. A lone
off-diagonal trilinear cannot close the simple two-photon scalar loop.
The two scalar-QED triangles and native two-photon seagull satisfy both
photon Ward identities before projection. With L=-G s H- H+, the matched
coefficient is alpha Q² G C_s^X F2(m_H²/M_s²)/(16 pi³ m_i M_s²), where
F2=(f-g)/(2z)<0. Signed Ilisie and independent Arhrib–Baek moments agree;
the six physical H1/H2 rows (including two zero A rows) are now included.

W matching remains BLOCKED_GAUGE_MATCHING: the exact CHK/Ilisie/Abe
form-factor differences are known and the off-shell P/pinch Ward identity
is checked, but the complete general-LFV B,C reductions and independent R_xi
cancellation have not been established. W candidates are excluded. Remaining
Zgamma, WZ, charged-current, mixed scalar/W, additional bosonic, QED and
external-invariant/neutrino-mass contributions remain NOT_EVALUATED.
No arbitrary finite pieces are added. Three-body interference and mu-e
conversion remain outside Module4. The frozen NuFIT archive, global vacuum,
RG and full-phenomenology limitations remain open.

## Versioned interface

Input/output schema v1 is structurally unchanged; the implementation is
version 1.2.0. Input `kind=module3_matching_input_v1` contains a complete
Module3 input, its matching complete Module2 output, and explicit versioned
two-loop masses. An optional complete Module3 output is schema/provenance
checked and preserved verbatim. Frozen source hashes, identities, scalar
provenance, algebraic forward closure, Yukawa mass rotation and all supplied
complex one-loop components are checked. No inverse solver, neutrino fit or
covariance selection runs in the interface. Records are consistency and
provenance checked, not digitally authenticated.

All nine charged-fermion loop masses are explicit; lepton masses and mW must
match the same supplied external/scalar electroweak records. Only
NOMINAL_UNMATCHED is currently accepted. Output contains 40 coherent rows
per channel (7 frozen one-loop, 27 fermion/photon, 6 charged-scalar/photon), two excluded W
candidates, and explicitly unevaluated topologies. Numerical errors describe
quadrature only, never scheme or truncation errors. Rates remain
INCLUDED_TOPOLOGIES_ONLY with no experimental allowance or exclusion.

```
bash scripts/run_module4_validation.sh --all-tests
python -m module4.interface --input module4/example.json \
  --output validation/module4/local/example_output.json
```

The full runner executes unchanged Module3 tests in an ephemeral clone of
its exact annotated component tag, on its original branch name. Other tests
and Module4 compatibility run on the required current branch. Both actual
results are reported separately; no inherited guard is changed or waived.
`--skip-native` explicitly reports VERTEX_BLOCKED. Logs, raw dumps, PDFs and
generated witnesses remain ignored locally; no historical scan is imported.
