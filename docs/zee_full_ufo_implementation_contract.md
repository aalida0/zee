# Full Zee-type UFO implementation contract — gate after scalar screen

**The repository does not yet contain a full gauge-complete Zee UFO.**
The Type-II 2HDM `2HDMtII_NLO` UFO is only a one-physical-charged-Higgs
Yukawa-production proxy. Do not use it for the H2→H1Z cascade.

## Target gauge theory

Gauge fields and matter: SM.
Additional scalar sector: Phi1 (SU2 doublet,Y=+1/2),
Phi2 (SU2 doublet,Y=+1/2), chi+ (SU2 singlet,Y=+1).

CP-conserving scalar potential, matching arXiv:2106.08332 eq (16):

V = m1²(Phi1†Phi1) + m2²(Phi2†Phi2)
    - m12²[(Phi1†Phi2)+h.c.]
    + (λ1/2)(Phi1†Phi1)² + (λ2/2)(Phi2†Phi2)²
    + λ3(Phi1†Phi1)(Phi2†Phi2)
    + λ4(Phi1†Phi2)(Phi2†Phi1)
    + (λ5/2)[(Phi1†Phi2)²+h.c.]
    + mC² χ+χ- + λC(χ+χ-)²
    + [μ4 Phi1^T(iσ2)Phi2 χ- + h.c.]
    + [k1(Phi1†Phi1)+k2(Phi2†Phi2)
       -k12((Phi1†Phi2)+(Phi2†Phi1))] χ+χ- .

Tree-level Type-II quark Yukawas from eqs (37)–(39); use CKM convention
consistent with the chosen UFO/generation flavor scheme.
Full Zee charged-singlet lepton couplings require an independent
antisymmetric flavor tensor f_ab L_a^T C iσ2 L_b chi+, plus compatible
charged-lepton Yukawas. Do not set this to zero if claiming a neutrino
mass-complete Zee model.

Scalar rotations: H1+ = cosγ HD+ + sinγ χ+;
H2+ = -sinγ HD+ + cosγ χ+. h125 = cosα Re Phi1^0 +
sinα Re Phi2^0 (deviations about VEV). The Z H1± H2∓ gauge
current is proportional to sinγ cosγ and MUST exist.

## Required FeynRules/SARAH export checks

1. Derive complete scalar/quark/lepton kinetic and Yukawa interactions
   from the SU2×U1 gauge basis; don't hand-insert a single off-diagonal
   Z vertex into an otherwise one-charged-scalar 2HDM UFO.
2. Verify neutral/charged Goldstones and diagonalization to
   (125,580.7,633.7,300,700) GeV within exact chosen beta and gamma.
3. Verify QED Ward identities: photon H1/H2 diagonal, no gamma H1 H2
   off-diagonal; the off-diagonal Z gauge vertex and W neutral-scalar
   vertices satisfy gauge-rotation identities.
4. Match tbH1/tbH2 vertices with cosγ and -sinγ rescaling of Type II;
   verify Z off-diagonal and all scalar cubic vertices.
5. Calculate complete H1/H2 widths, including Zee antisymmetric
   lepton Yukawas, Type-II tau nu, W h_i, H1 h125, H1 Z, and tb.
6. Reproduce the analytic partonic cross section of Z-mediated
   qqbar→H1±H2∓ and Type-II Yukawa proxy LO rate at identical inputs.
7. Check charge conjugation, Hermiticity, UV cancellations and relevant
   gauge/Ward tests. Include MG5 import/diagram smoke tests and
   independent analytic closure tests.
8. Re-run experimental constraints: electroweak precision, flavour
   B→X_s gamma, Higgs fit/direct searches, neutrino masses/LFV.

Full UFO acceptance: all eight checks with source, parameter card,
and reproducible AF logs. No event generation before that acceptance.

**Potential shortcut:** Search/source a peer-reviewed *original Zee*
(not Zee–Babu and not inert Zee) SARAH/FeynRules model as a starting
point, and independently validate every modification and mass convention.
