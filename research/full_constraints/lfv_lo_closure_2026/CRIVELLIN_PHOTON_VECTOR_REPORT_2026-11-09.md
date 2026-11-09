# Independent charged-singlet off-shell photon matching and aluminium conversion diagnostic

**9 November 2026 — source-check PASSED for restricted F-only QED vector; physical LFV UNKNOWN.**

## Primary source and source-specific operator

Crivellin, Kirk, Manzari and Panizzi, *Searching for Lepton Flavour (Universality) Violation and Collider Signals from a Singly-Charged Scalar Singlet*, **Phys. Rev. D 103, 073002 (2021)**, [arXiv:2012.09845v3](https://arxiv.org/pdf/2012.09845), [DOI](https://doi.org/10.1103/PhysRevD.103.073002): Lagrangian (1), dipole (9), Appendix Eqs. (A1)–(A4) and (A7). Their *pure singlet* low-$q^2$ photon vector coefficient is

$$
C^{V,LL}_{qq}=C^{V,LR}_{qq}
=\frac{e^2 Q_q}{288\pi^2 m_\phi^2}\lambda_{13}^{*}\lambda_{23},
\qquad
O^{V,LL(R)}_{qq}=(\bar e\gamma_\mu P_L\mu)(\bar q\gamma^\mu P_{L(R)}q).
$$

The frozen native charged-singlet vertex is $L_{ki}=-F_{ki}$ with $F$ antisymmetric. Its unitarity-reduced external product is $(F^\dagger F)_{e\mu}=F^*_{\tau e}F_{\tau\mu}=F^*_{e\tau}F_{\mu\tau}$; this has the same orientation as $\lambda_{13}^*\lambda_{23}$.

Photon couplings do not mix the two charged mass eigenstates. The direct two-state extension of the F-only loop topology thus uses $w_F=\sin^2\gamma/m_{H_1^\pm}^2+\cos^2\gamma/m_{H_2^\pm}^2$:

$$
C^{V,LL}_{qq}=C^{V,LR}_{qq}
=\frac{e^2Q_q}{288\pi^2}(F^\dagger F)_{e\mu}w_F.
$$

This is **not** the entire mixed-Zee one-loop semileptonic vector. The D-sector, non-photon penguins and boxes are separate.

## Independent comparison to the existing 2025 source transfer

The earlier Hundi source topology gives

$$
A_{1L}^{F}=-\frac{(F^\dagger F)_{e\mu}w_F}{288\pi^2}.
$$

So the *source-normalization bridge* for the F-only vector operator is

$$
C^{V,LL}_{qq}=C^{V,LR}_{qq}=-e^2Q_q A_{1L}^{F}.
$$

For the source's coherent vector nucleon current ($f^u_{Vp}=2$, $f^d_{Vp}=1$, $f^u_{Vn}=1$, $f^d_{Vn}=2$), adding the $P_L$ and $P_R$ quark coefficients gives

$$
g^{(p)}_L=2(C_{u,LL}+C_{u,LR})+(C_{d,LL}+C_{d,LR})=-2e^2 A_{1L}^F,
\quad
g^{(n)}_L=(C_{u,LL}+C_{u,LR})+2(C_{d,LL}+C_{d,LR})=0.
$$

The **neutron cancellation is exact** within this photon charge-current source subset. The proton relation reproduces the archived complex A1 on all four cards to $\leq1.86\times10^{-16}$ relative; all four independent weighted-scalar form-factor controls pass.

### On-shell source sign warning

The same 2021 paper Eq. (9) defines

$$
c_R^{(\mathrm{source})}=+\frac{e m_\mu}{384\pi^2}
(F^\dagger F)_{e\mu} w_F.
$$

The frozen Module 3 effective action uses $\mathcal L_{\mathrm{eff}}=e m_\mu\bar e\sigma^{\mu\nu}C_RP_R\mu F_{\mu\nu}/2+\mathrm{h.c.}$; its charged-only $e m_\mu C_R/2$ is the *negative* of the above displayed $c_R^{(\mathrm{source})}$ (same magnitude, $\leq 2\times10^{-16}$ residual after a minus sign). Because the two references write different effective amplitude/operator conventions, this is **not automatically a physics discrepancy**. It **is** a mandatory sign/phase-bridge test before combining the source vector with the native dipole or other Zee amplitudes. Do not silently identify the two effective-action coefficients.

## Numerical diagnostic: F-only photon vector in 27Al

Following Crivellin Eq. (A3) for the vector source and Eq. (A7) for the capture rate, use the KKO equal-density illustrative overlaps $V^{(p)}_\mathrm{Al}=0.0161$, $V^{(n)}_\mathrm{Al}=0.0173$ (e.g. NPB 932 (2018) 471, Table 3), $\Gamma_\mathrm{capt}^\mathrm{Al}=4.6\times10^{-19}$ GeV, and only the $F$-sector photon monopole.

$$
R_{\mu e}^{(\mathrm{Al});F\gamma V\text{-only}}
=\frac{4m_\mu^5}{\Gamma_\mathrm{capt}^\mathrm{Al}}
\left|g_L^{(p)}V_\mathrm{Al}^{(p)}
+g_L^{(n)}V_\mathrm{Al}^{(n)}\right|^2.
$$

| Original card | F photon vector-only $R_{\mu e}(\mathrm{Al})$ |
| --- | ---: |
| D7 NO / texture 0.0001 | $3.46008\times10^{-25}$ |
| D7 IO / texture 0.0001 | $1.04481\times10^{-24}$ |
| F13 NO / texture 0.001 | $2.16218\times10^{-22}$ |
| F13 IO / texture 0.001 | $6.52897\times10^{-22}$ |

**These are restricted quadratic diagnostics, not full physical conversion predictions.** They are neither upper nor lower bounds on the full coherent rate. In particular, they omit the charged F/D dipole and its unknown signed interference, the doublet charged photon, neutral h/H/A photon, low-$q^2$ Z, tree scalar semileptonic operators, loop boxes and RG matching. $^{27}$Al has no observed SINDRUM-II gold bound to apply; the nuclear overlaps quoted here are one reference prescription, not the full theory uncertainty.

An alternative archived aluminium overlap $V_p=0.0159$ would change the photon-only rate by $(0.0159/0.0161)^2\approx0.975$, a *diagnostic nuclear-input variation*, not an error envelope.

## Execution/evidence

Code: [crivellin_photon_vector.py](crivellin_photon_vector.py) and [test_crivellin_photon_vector.py](test_crivellin_photon_vector.py). JSON with per-card complex quark Wilsons, proton/neutron vectors, source dipoles and numeric validation: [CRIVELLIN_SINGLET_PHOTON_CONVERSION_SOURCE_MATCH_2026-11-09.json](CRIVELLIN_SINGLET_PHOTON_CONVERSION_SOURCE_MATCH_2026-11-09.json).

Four complex cards evaluated directly through authenticated GitHub source arithmetic in JavaScript. Independent weighted-state comparisons, neutron electric-charge cancellation, proton/A1 relation, and on-shell Eq.(9) magnitude control passed (relative residuals $\lesssim2\times10^{-16}$). The newly committed Python module/unit tests have not been executed in the user's checkout by this agent; this calculation does **not** assert that local checkout validation ran.

**Next decision:** Preserve $physical\_lfv=\mathrm{UNKNOWN}$. Obtain a common native amplitude-level sign bridge for the charged source Eq.(9), and complete the missing neutral photon, low-$q^2$ Z and mixed box coefficients; then implement source-checked full interference in $\mu\to3e$ and conversion. Do not repeat the already validated restricted F-loop kernels or launch a scan.
