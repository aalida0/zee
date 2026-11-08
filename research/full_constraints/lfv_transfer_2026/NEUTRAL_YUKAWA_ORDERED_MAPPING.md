# CORRECTED: neutral 2HDM ↔ native Zee lepton chirality mapping (8 Nov 2026)

**Supersedes the erroneous mapping committed as 6195fc3.** The old document identified the native D matrix with the paper's rho-dagger, which is WRONG. A 2026-11-08 independent Zgamma pilot detected the conflict. This note corrects the algebraic map only. It does not claim that any new Zgamma group or hZ group has been independently matched. The original pilot remains EXECUTION_BLOCKED and physical LFV remains UNKNOWN.

## Explicit field orientation

Published Altmannshofer et al., arXiv:2410.17313v4, Eqs. (10)–(12): the leptonic source is

    L_Y  =  - h_k [bar(e_L,i) (m_i/v delta_ij q_k1 + (rho_l^dagger)_ij q_k2) e_R,j + h.c.]

The Yukawa matrices in this formula are LH-row / RH-column. By contrast, the *native SARAH model source*, models/SARAH/ZeeTypeII/ZeeTypeII.m, defines the term `Ye conj[H1].e.l + Ye2 conj[H2].e.l`. The native frozen module3/core.py::vertices defines

    L_native = -s bar(e)_a [C_ab PL + (C_ba)* PR] e_b,
    C_h = cos(beta-alpha) diag(m/v) - sin(beta-alpha) D/sqrt(2),
    C_H = sin(beta-alpha) diag(m/v) + cos(beta-alpha) D/sqrt(2),
    C_A = -i D/sqrt(2).

A scalar term with PL on the incoming fermion is `bar(e_R,a) ... e_L,b`; thus native D has an **RH row and LH column**. The published paper's corresponding matrix for `bar(e_R) ... e_L` is **rho_l**, the Hermitian conjugate of the matrix in the paper's explicit `bar(e_L) ... e_R` term.

Therefore, when referring to the physical native arrays,

    CORRECT: rho_l        = D / sqrt(2)
    CORRECT: rho_l^dagger = D^dagger / sqrt(2)
    WRONG:   rho_l^dagger = D / sqrt(2)   [previous 6195fc3 note]

The paper's `Y_e^(1,2)` (LH-row/RH-column) are the Hermitian conjugates of the native SARAH `Ye,Ye2` arrays; that was the missed index-orientation step when interpreting published Eq. (12).

With 1-based paper flavor labels 1=e, 2=mu, the source dipole terms are

    c_L: rho_l,12        = D[e,mu]/sqrt(2)
    c_R: (rho_l,21)^*    = (D[mu,e])^*/sqrt(2)

Paper Eq. (48) and native module3/core.py::OPERATOR share the *same* projector placement on the incoming muon. The overall normalization, without a chirality exchange, is

    C_L = -c_L/(8*pi^2*v^2)
    C_R = -c_R/(8*pi^2*v^2)

with the published and frozen sigma and F conventions. For the neutral CP-conserving fields, the h,H,A factors remain the frozen native coefficients `q_h1=cos(beta-alpha), q_h2=-sin(beta-alpha), q_H1=sin(beta-alpha), q_H2=cos(beta-alpha), q_A1=0, q_A2=-i`, with consistent field orientation.

## Already archived **independent complex photon check** (do not redo)

The existing `module14/physics_adapters/lfv_reference.py::fixed_card_reference` **already passes the native matrix directly as `rho = D/sqrt(2)`** into the pinned public author's `thdm.py` and maps the outputs as

    coefficients = -array([cL_llpg, cR_llpg]).T/(8*pi^2*v^2).

`module14/physics_adapters/lfv_reference_evidence.json` records complex per-chirality photon subsets and maximum relative matching residual ~3.2e-13, comparing them to native Module4 on the four original D12 central cards and multiple radiative channels. This *validates the general ordered convention in that photon subset*, but DOES NOT by itself validate a NEW neutral-fermion Zgamma coefficient; the Z-exchange kernel, corrected 2026 coefficients and full two-loop phases need distinct nonzero numerical controls. The source-matched photon check was already done, so repeating it would waste work.

## Numerical hZ precursor must be corrected

The previous `HZ_EQ59_PRELIMINARY_NUMERICAL_2026-11-08.md` used the erroneous conjugated map. Its old complex C_L/C_R table **and stated interference shifts are invalid**; refer to the corrected notice and numbers at the very top of that report. At the printed precision of the old preliminary Eq.(59) coefficients, the correct new `C_L` is the old `C_R`, and the correct new `C_R` is the old `C_L`. The scalar group norm is therefore unchanged, but the interference with frozen baseline changes. That is merely an algebraic reorientation of a preliminary evaluation, NOT independent author-code validation.

## Next minimal calculation

Read paper arXiv:2410.17313v4 Eqs. (48), (54), (55) (verified arXiv post-correction version), and 2026 erratum JHEP07(2026)184; use pinned author's b5035cd5 thdm.py. Retain the genuine Z-exchange parts `f3/f4`, including the published top/charm versus bottom/tau conjugations, and do NOT duplicate photon `f1/f2` already in Module4. Reuse the validated rho mapping and archived photon comparison as a **prerequisite that is already satisfied**.

Execute TWO nonzero complex independent Zgamma controls against author code, test cL/cR routing with D[e,mu] and D[mu,e] switched on one at a time, and only then evaluate exact 4 texture cards. If controls fail, preserve the counterexample and maintain UNKNOWN. Do not rerun provenance reconstruction, source literature audit, full hZ/kinetic sectors, B/Higgs/vacuum, or generate new scan cards.

## References / evidence

- Published source: https://arxiv.org/html/2410.17313v4 Eqs. (10)–(12), (48), (54)–(55), (59).
- Official erratum: https://doi.org/10.1007/JHEP07(2026)184 (verified exists, independent full formula review not claimed here).
- Native SARAH: `models/SARAH/ZeeTypeII/ZeeTypeII.m`, `module3/core.py::vertices`, `module3/CONVENTIONS.md`.
- Independent archived controls: `module14/physics_adapters/lfv_reference.py`, `module14/physics_adapters/lfv_reference_evidence.json`, `module4/amplitudes.py::fermion_component`.
