# First direct 2HDM → Type-II Zee LFV transfer: neutral scalar semileptonic matching
**9 November 2026 — implemented, independently numerically checked; incomplete full observables**

## Result and physical scope

**Delivered:** exact tree-level \(\mu\to e\) semileptonic **scalar** Wilson coefficients from neutral \(h,H,A\) exchange for all six Type-II quark flavors, with complex muon/electron chirality, three scalar-state contributions, illustrative proton/neutron trace-anomaly matching, and independent 2HDM limit tests. No source or frozen module was modified. Source code is `evaluate.py`, executable tests in `test_evaluate.py`, all four original low-texture coefficients in `RESULT.json` and **actually executed independent complex arithmetic** in `VALIDATION_RECEIPT.json`.

**Status:** `SOURCE_FORMULA_MATCHED_TREE_SUBSET`. This is a REAL leading **tree-level** component of the missing conversion UV vector, not a new one-loop result. The physical \(\mu\to e\) aluminium conversion rate and complete \(\mu\to3e\) remain `null`; `physical_lfv=UNKNOWN`, `global_acceptance=null`. No new parameter scan, collider, SPheno, F-gauge or two-loop calculation.

## Published 2HDM references and code contract

- **Wei-Shu Hou and Girish Kumar**, *Muon flavor violation in two-Higgs-doublet model with extra Yukawa couplings*, **Phys. Rev. D 102, 115017 (2020)**, [doi:10.1103/PhysRevD.102.115017](https://doi.org/10.1103/PhysRevD.102.115017), **Eqs. (10)–(12)**. In Eq. (12), the scalar quark coefficient is proportional to the *product* of a flavor-changing neutral lepton vertex and the **real** diagonal neutral quark vertex over the scalar mass squared; reverse flavor order specifies the opposite lepton chirality. Their coefficient normalization includes an explicit \(m_\mu m_q\) factor in the effective action. We compute the equivalent **unrescaled dimensionful coefficient** rather than silently copying their named L/R conventions.
- **Hou and Kumar**, *Charged lepton flavor violation in light of muon g-2*, **Eur. Phys. J. C 81, 1132 (2021)**, [doi:10.1140/epjc/s10052-021-09939-3](https://doi.org/10.1140/epjc/s10052-021-09939-3), **Eqs. (12)–(13)** for scalar effective Lagrangian and nuclear response; their stated \(f_{u,d,s}^{p,n}\) / heavy \(2/27\) implementation is supplemented by the explicit numerical inputs used in Hou–Kumar 2020.
- **Altmannshofer et al.**, [arXiv:2410.17313v4](https://arxiv.org/html/2410.17313v4), Eqs. (10)–(12), neutral Higgs-basis \(q_{k1},q_{k2}\). Their associated public `thdm.py` was already matched to native lepton photon subsets in `module14/physics_adapters/lfv_reference_evidence.json`. **This new scalar 4-fermion module is validated against the 2HDM source analytic structure and native independent quark/lepton vertex implementations; an independent 2HDM conversion code numeric full-observable match is NOT claimed.**
- Frozen native `module3/core.py::vertices` and `module4/couplings.py::quarks` are imported unchanged. The source/native lepton mapping is the **corrected** \(\rho_\ell=D/\sqrt2\), not \(\rho_\ell^\dagger=D/\sqrt2\). Quarks are Type-II, NOT 2017 Zee paper's suppressed extra-doublet quarks.

## Exact EFT action, conventions, and analytic 2HDM check

Native \(h/H/A\) lepton interaction is
\[
\mathcal L_Y=-\phi\,\bar e_a [C^\ell_{\phi,ab}P_L+(C^\ell_{\phi,ba})^*P_R]e_b
\]
and native real Type-II diagonal quark scalar parts are \(\operatorname{Re} C^q_{\phi,qq}\). Integrating out a heavy **real** neutral scalar at tree-level produces
\[
\mathcal L_{\rm eff}^{S}=\sum_{q=u,d,s,c,b,t}\left[
 S_L^q(\bar e P_L\mu)+S_R^q(\bar e P_R\mu)\right](\bar qq)
+\mathrm{h.c.},\quad
S_L^q=\sum_{\phi=h,H,A}\frac{C^\ell_{\phi,e\mu}\,\operatorname{Re}C^q_{\phi,qq}}{m_\phi^2},
\quad S_R^q=\sum_{\phi}\frac{(C^\ell_{\phi,\mu e})^*\,\operatorname{Re}C^q_{\phi,qq}}{m_\phi^2}.
\]
Thus \([S_{L,R}^q]=\mathrm{GeV}^{-2}\); \(S_{L,R}^q/(m_\mu m_q)\) are the corresponding dimensionful stripped factors for the source's explicit \(m_\mu m_q\) convention. **No extra factor \(1/2\)** belongs to the contracted tree graph, consistently with `module3/CONVENTIONS.md`.

For the frozen Type-II quarks, \(\delta=\beta-\alpha\), \(t_\beta=\tan\beta\),
\[
\kappa_u^h=\cos\delta-\cot\beta\sin\delta,\quad
\kappa_u^H=\sin\delta+\cot\beta\cos\delta,\quad
\kappa_d^h=\cos\delta+\tan\beta\sin\delta,\quad
\kappa_d^H=\sin\delta-\tan\beta\cos\delta.
\]
The **independent analytic 2HDM reduction** of the full native vertex sum is
\[
\frac{S_L^u}{m_u}=\frac{D_{e\mu}}{\sqrt2 v} T_u,\qquad
\frac{S_L^d}{m_d}=\frac{D_{e\mu}}{\sqrt2 v} T_d,
\quad\text{where}
\quad T_u= \sin\delta\cos\delta(m_H^{-2}-m_h^{-2})
 + \cot\beta(\sin^2\delta/m_h^2+\cos^2\delta/m_H^2),
\]
\[
T_d= \sin\delta\cos\delta(m_H^{-2}-m_h^{-2})
 - \tan\beta(\sin^2\delta/m_h^2+\cos^2\delta/m_H^2).
\]
For \(S_R\), replace \(D_{e\mu}\to D_{\mu e}^{*}\). The CP-odd \(A\) has purely imaginary *diagonal quark* vertices in the CP-conserving Type-II sector, so \(\operatorname{Re} C^q_A=0\): it contributes **no coherent scalar quark density**. Its pseudoscalar-current operators, if relevant to spin-dependent conversion, are distinct and have NOT been calculated here. Both \(S_L^q,S_R^q\) are independent of the Zee \(F\) and charged mixing \(\gamma\) *exactly at this neutral-tree order*. In strict alignment \(\delta=0\), \(T_u=+\cot\beta/m_H^2,\ T_d=-\tan\beta/m_H^2\), as required for the pure 2HDM.

The **illustrative** nucleon matching is
\[
S_X^N=m_N\left[\sum_{q=u,d,s}f_{Tq}^N\frac{S_X^q}{m_q}
+\frac{2f_{TG}^N}{27}\sum_{Q=c,b,t}\frac{S_X^Q}{m_Q}\right],
\quad f_{TG}^N=1-\sum_{q=u,d,s} f_{Tq}^N.
\]
We use \((f_{Tu}^p,f_{Td}^p,f_{Ts}^p)=(.024,.033,.043)\) and \((f_{Tu}^n,f_{Td}^n,f_{Ts}^n)=(.033,.024,.043)\) for a fixed numerical comparison, **not** a modern lattice-hadron systematic or QCD RG calculation. The original nuclear spin/interference action and proton/neutron interchange issues are documented in `lfv_lo_closure_2026/`; they are **not** bypassed by this isolated quark-to-nucleon projection.

## Four existing low-texture cards: new semileptonic subset

The table gives the **complex** projected left-chiral coefficient of \((\bar e P_L\mu)(\bar p p)\) in GeV\(^{-2}\), using the fixed nominal scalar fractions. The \(R\) coefficients and all six quark coefficients (per \(h,H,A\)) are in `RESULT.json`.

| Existing card | \(\mathrm{Re}\,S_L^p\) | \(\mathrm{Im}\,S_L^p\) |
|---|---:|---:|
| D7 NO / texture_0.0001 | \(-2.95218\times10^{-30}\) | \(-1.18087\times10^{-29}\) |
| D7 IO / texture_0.0001 | \(+1.09499\times10^{-28}\) | \(+4.91404\times10^{-28}\) |
| F13 NO / texture_0.001 | \(+1.47071\times10^{-30}\) | \(+5.20406\times10^{-30}\) |
| F13 IO / texture_0.001 | \(+1.23691\times10^{-29}\) | \(-1.60396\times10^{-29}\) |

These small amplitudes are explained by the archived low-texture \(D_{e\mu},D_{\mu e}\) entries of order \(10^{-21}\)–\(10^{-19}\), **not** by a full calculation showing the missing off-shell photon, Z or box amplitudes vanish. No experimental rate is obtained from this table.

## Independent numerical validation and remaining test run

Actually executed independent arithmetic from the *full frozen complex matrices* and native vertex algebra (not relying on precomputed coupling products) and compared to the new `RESULT.json`:
- **48 complex direct Type-II lepton–quark chiral contractions**, 4 cards × 6 quarks × 2 muon chiralities: maximum relative residual \(2.04\times10^{-15}\).
- **4 independently reproduced native 2HDM \(\mu\to3e\) neutral-tree `SLL` coefficients** compared with the earlier saved `lfv_lo_closure_2026/WILSON_LEDGER.json`: maximum relative residual \(1.12\times10^{-15}\).
- **3 separate analytic strict-alignment limit checks** \(T_u=\cot\beta/m_H^2\), \(T_d=-\tan\beta/m_H^2\): residual ≤ \(5.3\times10^{-23}\) absolute.

The executable Python research unit tests in `test_evaluate.py` additionally cover `F=0` decoupling, variation of charged mixing \(\gamma\), `D_{e\mu}=0` one-sided chirality, fictitious quark mass reparameterization, CP-odd scalar quark density zero, previous \(\mu\to3e\) neutral-tree source match and missing-operator rate rejection. **They have not been executed in the user's actual checkout here**; run the commands below, preserve their output, and report any discrepancy. The separate independent JS checks do *not* validate all loops or full nuclear uncertainties.

## Reproduce locally

```bash
cd ~/zee
git switch research/zee-full-constraints
git pull --ff-only origin research/zee-full-constraints
python3 -m unittest discover -s research/full_constraints/lfv_2hdm_transfer_2026 -p 'test_*.py' -v
python3 -m research.full_constraints.lfv_2hdm_transfer_2026.evaluate
git status --short
```

The evaluator reads frozen D12 data and writes only `research/full_constraints/lfv_2hdm_transfer_2026/RESULT.json`; existing modules and signed archives remain unchanged.

## Next **genuinely leading** transfer, rather than another two-loop campaign

1. Build the source-matched **general 2HDM and mixed Zee off-shell photon monopole \(K_1^{L,R}(q^2\to0)\)** in the **same ordered Wilson convention**, separating the doublet \(D\) sector from both charged mass-eigenstate \(F^\dagger F\) contributions; this is a *one-loop* operator needed for **both** \(\mu\to3e\) and conversion. Use source-verified functions and Ward identity, not merely on-shell \(\mu\to e\gamma\).
2. Add **one-loop low-q² \(Z\) penguin** and remaining physical charged-scalar \(D/F\) box terms with phase/chirality checks and source 2HDM limit. Crosscheck the existing restricted F box; do not count it twice.
3. Map the full signed semileptonic WET Wilson vector, QED/QCD evolution and nuclear response (Al first), reusing the already verified response kernel and correcting the public scalar p/n convention in an isolated bridge.
4. Only after leading matching establishes a **complete mandatory observable**, form the **physical** rate, uncertainties and pass/fail. This transfer intentionally does **not** mark a conversion observable complete or authorize a scan.

**Scope decision:** neutral 2HDM scalar-quark tree operators are now done and verified at source-formula level. The still essential missing physics is the off-shell penguin + mixed Zee box matching. Their absence cannot be fixed by relabeling the dipole as complete or treating them as zero.
