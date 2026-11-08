# CORRECTED preliminary neutral hZ Eq.(59) diagnostic — 8 November 2026

> **CHIRALITY CORRECTION**: The previous revision at commit cfb10fe assigned D[e,mu] to c_R and D[mu,e]* to c_L, contrary to the actual SARAH action. That reversed the native C_L/C_R coefficients and invalidated the reported coherent rate shifts. The source Eq.(59) loop-function integrals were not invalidated. This note supersedes the old complex coefficient and interference tables. No new author-code or two-loop amplitude validation is claimed.

**Evidence level:** Source equation evaluated using previously numerically integrated f7 loop functions; input Yukawa and baseline hashes unchanged; the corrected complex coefficients below are algebraic reorientation of the old provisional results. No independently evaluated author-code hZ group, no complete LFV, no physical exclusion. Physical LFV UNKNOWN.

## Source and fixed conventions

Altmannshofer et al., arXiv:2410.17313v4 Eq. (59), Eq. (35), Eq. (48): the neutral hZ group is separately gauge invariant in the pure 2HDM. Published **c_R** contains `rho_l,21*` and published **c_L** contains `rho_l,12`. The source `rho_l` is the matrix in the *bar(e_R) ... e_L* interaction.

For native SARAH `Ye conj[H1].e.l`, RH rows and LH columns, the physical neutral matrix in `module3/core.py::vertices` is `D`. The **correct** paper/native coupling dictionary (see `NEUTRAL_YUKAWA_ORDERED_MAPPING.md`) is

    rho_l = D/sqrt(2)
    c_L: rho_l,12       = D[e,mu]/sqrt(2)
    c_R: (rho_l,21)*   = D[mu,e]*/sqrt(2)
    C_L/R = -c_L/R/(8*pi^2*v^2), no L/R swap

The previous revision instead applied the *conjugated rho mapping*. The signed native frozen baseline itself is not changed.

## Equation evaluated

For CP-conserving scalar mixing, only H contributes to the subtracted heavy-neutral sum, `q_H1 q_H2=sin(beta-alpha)cos(beta-alpha)`. The common scalar factor is

    K = -(e alphaEM)/(48*pi*sin(thetaW)*cos(thetaW)) *
        (v^2/(mZ*m_mu))*sin(beta-alpha)*cos(beta-alpha) *
        [(v_e^Z)^2 (f7plus(mZ^2/mH^2)-f7plus(mZ^2/mh^2))
          + (a_e^Z)^2 (f7minus(mZ^2/mH^2)-f7minus(mZ^2/mh^2))].
    c_L = K*D[e,mu]/sqrt(2)
    c_R = K*conj(D[mu,e])/sqrt(2).

Eq. (35) f7 values were originally evaluated at 50-digit precision with both mpmath and independent SciPy one-dimensional quadratures. These check the loop integral but are NOT an independent author-code hZ amplitude check. Same preliminary electroweak inputs are retained: v=246.21965 GeV, mZ=91.1876 GeV, m_mu=0.1056583745 GeV, alphaEM=1/137.035999084, sin^2 thetaW=0.23122. Original source-hashed D7/F13 masses: tanbeta=(1.1157268700505090,5.3077513190433523), alpha_SusHi=(2.3627051010413220,2.9578268064201572), mh=125 GeV, mH=(492.43078309962277,707.08193786447146) GeV, alpha_physical=alpha_SusHi-pi/2.

D7 and F13 delta loop-function values (f7+,f7−) from the original preliminary source integration are respectively (-1.424737373,-0.8759489842) and (-1.722202669,-0.9674053207).

## Four source-texture cards: corrected coefficient orientation

The correction swaps the two formerly printed *hZ-only* chirality components. The loop factors and Euclidean norm of the hZ subvector are unchanged. Complex numbers below are truncated to the previously printed precision.

| Texture card | Corrected hZ C_L (GeV^-2) | Corrected hZ C_R (GeV^-2) | Norm(hZ)/Norm(frozen retained) | Corrected relative shift of *partial* mu→eγ rate |
|---|---|---|---:|---:|
| D7 NO, texture_0.0001 | (-2.24823 - 8.99292 i)e-30 | (4.18580 + 4.18580 i)e-28 | 4.24263e-13 | +1.76115e-13 |
| D7 IO, texture_0.0001 | (8.33889 + 37.4228 i)e-29 | 3.13935e-28 | 1.34662e-13 | +1.38774e-13 |
| F13 NO, texture_0.001 | (-4.21946 - 14.9304 i)e-32 | (-7.38585 + 7.38585 i)e-31 | 1.48923e-15 | +4.89018e-16 |
| F13 IO, texture_0.001 | (-3.54867 + 4.60173 i)e-31 | (-2.21576 - 1.47717 i)e-30 | 2.11007e-15 | -3.64986e-15 |

The rate fractional shifts are computed from the unchanged `BASELINE_REPLAY.json` complex vectors by the exact coherent identity

    deltaR/R_retained = [2*Re(conj(C_retained) dot deltaC_hZ) + |deltaC_hZ|^2] / |C_retained|^2.

The rounded, chirality-corrected numbers are not independently validated physical predictions. They show only that this **one** source-evaluated neutral hZ group is very small for these specific texture cards. They cannot be used to bound the not-yet-evaluated Zgamma/kinetic/HZ/HW/mixed F-gauge sectors or mark any card allowed.

## Relationship to Zgamma follow-up and archived numerical matching

The existing `module14/physics_adapters/lfv_reference.py` passes `rho = D/sqrt(2)` to the pinned source and matches the complex **fermion–photon** terms to native Module4, with an archived maximum relative residual approximately 3.2e-13; this prior comparison should be reused as chirality evidence, not rerun.

For **new neutral-fermion Zgamma**, independently check the actual f3/f4 exchange parts of corrected post-erratum arXiv v4 Eqs. (54)-(55) against the pinned author code for two nonzero complex test vectors, respecting cL/cR orientation above. Do not add the f1/f2 photon pieces again. If that check passes, apply the mapping to the same 4 texture cards. All original physical classification remains UNKNOWN.
