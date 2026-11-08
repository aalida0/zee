# Resolved algebraic neutral-Yukawa map for 2HDM → Zee LFV (8 November 2026)

**Scope of this note:** a *source-level algebraic mapping*, not a new dipole or independently validated loop result. This note is a follow-up to the completed, pushed but `EXECUTION_BLOCKED` four-card run (Git `a1f65de33b6c2bb82077d256475439840835e554`). Existing `RESULT.json`, complex baselines, validations and physical unknowns remain untouched.

## Derivation from published source and frozen code

General 2HDM source: Altmannshofer et al., JHEP06(2025)156 and 2026 erratum, arXiv:2410.17313v4 [Eqs. (3), (5), (8), (10)–(13), (48), (54)–(55), (59)](https://arxiv.org/html/2410.17313v4). This mapping is established from the published **definitions**, not from post-erratum loop-function numerical execution.

The paper's Higgs-basis charged-lepton Yukawa matrices satisfy, explicitly in Eq. (12):
\[
\rho_\ell^\dagger
=\frac{Y_{\ell}^{(2)}\cos\beta-Y_{\ell}^{(1)}\sin\beta}{\sqrt{2}},
\]
with Eq. (11) defining the neutral mass-eigenstate coupling \(\bar\ell_{L,i}\,[\frac{m_i}{v}\delta_{ij}q_{k1}+(\rho_\ell^\dagger)_{ij}q_{k2}]\,\ell_{R,j}\,h_k\), in the action with an overall minus sign.

Frozen native convention: `module2/core.py::yukawa_rotation` and `module3/core.py::vertices`; `module3/CONVENTIONS.md`:
\[
D=Y_{e2}\cos\beta-Y_e\sin\beta,\qquad
C_h=\cos(\beta-\alpha)\frac{M_\ell}{v}-\sin(\beta-\alpha)\frac{D}{\sqrt2},
\quad C_H=\sin(\beta-\alpha)\frac{M_\ell}{v}+\cos(\beta-\alpha)\frac{D}{\sqrt2},
\quad C_A=-i\frac{D}{\sqrt2}.
\]

**Conclusion at the neutral Lagrangian level** with the same Higgs-basis gauge-field phase convention:
\[
\boxed{\rho_\ell^\dagger=D/\sqrt2},\qquad
\begin{array}{c|cc}
 &q_{k1}&q_{k2}\\
h&\cos(\beta-\alpha)&-\sin(\beta-\alpha)\\
H&\sin(\beta-\alpha)&+\cos(\beta-\alpha)\\
A&0&-i
\end{array}
\]
(up to an overall sign redefinition of the real CP-odd field `A`, applied consistently to all its vertices).

Use the source paper's **one-based e,μ,τ indexing**, \(\rho_\ell^\dagger{}_{ij}=\rho_{\ell,ji}^*\):
\[
\boxed{\rho_{\ell,21}^{*}=(\rho_\ell^\dagger)_{12}=D_{e\mu}/\sqrt2},\quad
\boxed{\rho_{\ell,12}=(\rho_\ell^\dagger)_{21}^{*}=D_{\mu e}^{*}/\sqrt2}.
\]

Thus the 2HDM source \(c_R\) neutral \(Z\gamma\) term in Eqs. (54)–(55), and \(c_R^{hZ}\) in Eq. (59), contain the **actual \(D_{e\mu}\)** direct entry; \(c_L\) contains **\(D_{\mu e}^*\)**, after preserving the paper's convention for which term is conjugated and how loop kernels transform. Do not swap these entries or substitute \((F^\dagger F)_{e\mu}\) for them.

**Operator map** from paper Eq. (48) and native `module3/core.py::OPERATOR`:
\[
\mathcal L^{2HDM}_{\rm dip}=-\frac{e m_\mu}{16\pi^2 v^2}\bar e\sigma^{\mu\nu}(c_LP_L+c_RP_R)\mu F_{\mu\nu}
\quad\longleftrightarrow\quad
\mathcal L^{Zee}_{\rm dip}=+\frac{e m_\mu}{2}\bar e\sigma^{\mu\nu}(C_LP_L+C_RP_R)\mu F_{\mu\nu},
\]
hence
\[
\boxed{C_{L,R}=-c_{L,R}/(8\pi^2v^2)}
\]
**provided the external field ordering and \(\sigma^{\mu\nu},F_{\mu\nu}\) definitions are matched as in the two specified actions**. This is the unambiguous algebraic prefactor, not independent validation of a loop implementation.

## What the previous study was unable to establish

The previous `EXECUTION_REPORT.md` described the whole ordered phase/chirality map as unfinished. **The neutral Yukawa and operator-level algebraic pieces above can now be regarded as solved on paper**, with the caveat that source **loop** phase, relative signs to other two-loop subsets and numerical evaluation are *still* unvalidated. Do not retroactively change the outcome `EXECUTION_BLOCKED` or claim that new amplitudes were run.

The official erratum JHEP07(2026)184 exists, the pinned `thdm.py` SHA256 `9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193` was previously checked, but its numerical implementation was not independently compared here. Eq. (54)–(55) post-erratum functions must be taken from the corrected release, not the 2025 version. The `hZ` Eq. (59) contains neutral \(q_{k1}q_{k2}\) mixing and is not a single-loop-Barr–Zee photon term; source says it is a distinct gauge group.

**Important:** The native charged-Higgs `D` couplings in `module3/core.py::dipole_ledger` involve charge-conjugation and neutrino-field orientation. Do **not** assume that matching the neutral \(\rho^\dagger=D/\sqrt2\) automatically validates the two-loop charged-current `tHp,cHp,tauHp` or singlet-\(F\) groups; they remain separate tasks.

## Decisive next minimal execution (rather than repeating card replay)

1. Extract exact paper v4 Eqs. (54)–(55) **Z-proportional** parts and Eq. (59) `hZ`. Pin public author `thdm.py` to hash above; never copy photon terms already in Module4. Test 2 genuinely complex nonzero source-only 2HDM vectors, using independent loop-function quadrature/analytic formula vs author code. Do not use arbitrary model-limit vectors as phenomenological Zee cards.
2. Obtain `q_{k1},q_{k2}` through the exact frozen `beta,alpha` and \(D_{e\mu},D_{\mu e}\) from four joined `texture` records in `CARD_PROVENANCE.json` and saved `validation/module12/d12_benchmarks.json` (not the separate `scale_0.001` witness family).
3. Compare signed \((c_L,c_R)\) to \((C_L,C_R)\) with operator map above, keeping neutral-photon Module4 terms **unchanged**, and execute both chiralities, CP-even/odd sign and \(D\)-zero rephasing tests.
4. If that passes, produce only 4-card Zγ / hZ complex term ledger and relative interference; otherwise a single exact numerical counterexample, not a new 69,570-token umbrella run. All uncomputed Zee-\(F\), kin, HZ, HW, μ→3e and conversion remain `UNKNOWN`.

## Present classification

- Source Yukawa map: **ALGEBRAICALLY_SOURCE_VERIFIED**.
- Source dipole operator prefactor: **ALGEBRAICALLY_SOURCE_VERIFIED**.
- 2HDM loop functions as independently implemented and tested here: **NOT TESTED**.
- Complex neutral new term \((\Delta C_L,\Delta C_R)\) on each Zee saved card: **NULL / NOT COMPUTED**.
- Existing four-card 6/6 replay tests: **PASS from prior execution**; no tests executed in this note.
- Physical LFV: **UNKNOWN**. Global acceptance: **null**.
