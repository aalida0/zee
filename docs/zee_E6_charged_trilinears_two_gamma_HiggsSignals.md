# E6 — Original Zee charged-scalar loops in \(h\to\gamma\gamma\) and \(h\to Z\gamma\), 309-source HiggsSignals

**Implementation status (20 October 2026):** E6 scripts, tests and the one-shot AF runner are committed. **The AF unit tests and full 309-point numerical E6 campaign have NOT been executed.** This is an improved *conditional* 125 GeV HiggsSignals calculation, **NOT** a complete experimentally allowed Zee fit.

## Physics motivation and source

E2 established 309 of 395 10-TeV-running-theory-screened original scalar potentials with **no deeper tree vacuum found** in 128-start C5 finite searches (not global minima proofs). E3 optimized one neutrino-closed \`f,Y^\ell\` family per original potential, applied incomplete LFV (one-loop + selected two-loop terms), and reran 10 TeV sampled theory. E4H found tiny direct h(125) LFV branching-ratio proxies. E5 evaluated all 309 in **actual HiggsTools HiggsSignals, 159 observables**, with \(\chi^2_{\rm SM}=153.71818978\). In the E5 approximation \(\Delta\chi^2\) median **112.99** because the original Type-II-like κb can be very small. E5A source-closed all 309 and showed diagnostic bottom/down/strange coupling resets improve 306/309, with median reference shift to 0.659; **the resets are not physical Zee models**.

The preferred source benchmark **B4_0004143** has cascade *upper proxy* 0.5938792, κb=0.96657, E5 conditional \(\Delta\chi^2=0.81644\). Benchmark B4_0006862 has proxy 0.6043677 but \(\Delta\chi^2=23.1068\). Actual cascade production and full widths are NOT available.

The primary physics source for E6 is **Florentino, Romão and Silva**, *Off diagonal charged scalar couplings with the Z boson: the Zee model as an example*, Eur. Phys. J. C **81** (2021) 1148, arXiv:2106.08332, DOI https://doi.org/10.1140/epjc/s10052-021-09956-2. Especially **Appendix B, Eq. (B5)** (charged-scalar \(h\gamma\gamma\)) and **Eq. (B6)** (mixed-mass \(hZ\gamma\)). NOT Appendix D! The detailed scalar benchmark reconstruction is \`gate6_benchmark.benchmark()\`; Higgs basis mapping is \`gate7_map_p2_to_yangwu.map_point()\`.

## Tree cubic couplings — two independent parameterizations

For fixed original Zee potential, charged gauge fields \((\phi_1^+,\phi_2^+,\chi^+)\), \(G^+=c_\beta\phi_1^+ +s_\beta\phi_2^+\), and
\[
H_1^+=c_\gamma(-s_\beta\phi_1^+ +c_\beta\phi_2^+)+s_\gamma\chi^+,\qquad
H_2^+=-s_\gamma(-s_\beta\phi_1^+ +c_\beta\phi_2^+)+c_\gamma\chi^+.
\]
The 125 GeV physical scalar is \(h=c_\alpha\rho_1+s_\alpha\rho_2\). E6 reconstructs the full 3×3 gauge-basis charged mass Hessian with **fixed original quadratic Lagrangian masses** \(m_{11}^2,m_{22}^2,m_C^2\), and obtains
\[
g_{hij} = [U^T(c_\alpha\partial_{v_1}+s_\alpha\partial_{v_2})\mathcal{M}_+^2U]_{ij},
\quad
V\supset +g_{hij}\,hH_i^-H_j^+.
\]
Numerical central differencing of the gauge-basis Hessian is independently compared to the **analytic Higgs-basis** charged doublet/singlet matrix:
\[
\partial_h\mathcal M_{+,(H_D,\chi)}^2 =
\begin{pmatrix}
v(Z_3 c_\delta+ Z_7 s_\delta)&-\mu_4 c_\delta/\sqrt 2\\
-\mu_4 c_\delta/\sqrt2&v(K_1 c_\delta+K_{12}s_\delta)
\end{pmatrix},
\quad \delta=\alpha-\beta.
\]
Further checks: 3×3 mass eigenvalues \(0,m_{H1}^2,m_{H2}^2\); source Gate6 preexisting offdiagonal \(hH_1H_2\) cubic; and exact \(Z_{12}=-\tfrac14\sin(2\gamma)\) in the basis \(Z=\mathrm{diag}(1/2-s_W^2,-s_W^2)\). For the original Gate6 nominal reference the algebraic independent benchmark is
\[
(g_{h11},g_{h22},g_{h12})\simeq(-397.485544,\ 1073.509393,\ 110.510637)\ {\rm GeV}.
\]
These are **tree potential** coefficients, not Feynman-rule signs.

## One-loop charged scalar contribution to \(h\to\gamma\gamma\)

With \(\tau_i=m_h^2/(4m_{H_i}^2)\) and \(A_0(\tau)=-[\tau-\arcsin^2\sqrt\tau]/\tau^2\),
\[
\mathcal A_{H_i}^{\gamma\gamma}
  ={v g_{hii}\over 2m_{H_i}^2}A_0(\tau_i).
\]
The photon charge matrix is the identity among mass eigenstates; hence offdiagonal \(hH_1 H_2\) cannot enter a two-photon scalar triangle. E6 sums BOTH diagonal charged scalar loops coherently with the altered LO W/top/bottom/charm/tau CP-even amplitude; CP-odd complex lepton Yukawas enter the squared rate separately. It scales HiggsTools' *saved E5 model* diphoton partial width by \((|A_{\rm even}+A_{H1}+A_{H2}|^2+|A_{\rm odd}|^2)/(|A_{\rm even}|^2+|A_{\rm odd}|^2)\), recomputes total width and HiggsSignals χ². It checks the LO SM-particle predicted ratio against the actual HiggsTools relative baseline within a diagnostic 8% tolerance, or fails closed.

## One-loop \(h\to Z\gamma\): **mixed masses included**

Z is not diagonal: \(Z_{12}=-\tfrac14\sin 2\gamma\). Thus both ordered mixed triangles \(H_1H_2\) and \(H_2H_1\) contribute, in addition to two diagonal charged loops. E6 source \`zee_gateE6_zgamma_mixed_PV.py\` implements **the finite unequal-mass \(B_0,C_0\) expression of Florentino Appendix B, Eq. (B6)** with Gauss–Legendre quadrature, retaining explicit ordering, and validates:
- symmetry \(F(m_i,m_j)=F(m_j,m_i)\) and both mixed contributions;
- independent **48/64-point** quadrature agreement;
- independent analytic **equal-mass \(I_1(a,b)\) limit**
\[
F(m,m)=-{m_h^2-M_Z^2\over2m^2}
 I_1(4m^2/m_h^2,4m^2/M_Z^2);
\]
- exact vanishing of the scalar term when every \(g_{hij}\to0\), recovering the SM LO reference.

The same helper implements LO SM W and complex fermionic CP-even/CP-odd terms using \(I_1,I_2\), then computes the full **LO charged-scalar-plus-modified-SM** \(Z\gamma\) rate divided by LO SM. That ratio scales the HiggsTools SM-reference \(\Gamma(h\to Z\gamma)\), since in E5 the effective \(Z\gamma\) coupling was deliberately fixed to 1. The hγγ and hZγ widths are updated *once each*, with exact total-width invariants, before recomputing the SAME 159-observable HiggsSignals correlated χ². Source/cubic/PV/W loop invariants are tested. **Higher-order matching of the SM and BSM Zgamma amplitudes remains approximate and has not been independently calibrated.**

The 48/64 quadrature was independently checked in the extreme original source range \(m_{H1}=200\), \(m_{H2}=1600\) GeV, agreeing at the \(10^{-9}\) relative level. Exact unequal-mass corner cases outside this range should fail closed, not silently be relabeled as allowed.

## Single AF run, **all 309 original spectra**, with source fingerprints

Committed code:
\`scripts/zee_gateE6_309_charged_gamma_higgssignals.py\`,
\`scripts/zee_gateE6_zgamma_mixed_PV.py\`,
\`tests/test_zee_gateE6_309_charged_gamma_higgssignals.py\`,
\`scripts/zee_gateE6_one_shot.sh\`.

All E2/E3/E4H/E5 data are **read-only** and source SHA verified. The original E5 per-candidate χ² must reproduce within \(5\times10^{-6}\) before any loop correction; 159 observed HiggsSignals observables and SM \(\chi^2=153.71819\) are independently checked. Saved checkpoint is resumable with source and both E6 code SHA fingerprints; every row has \`full_Zee_allowed_or_excluded: null\`.

One UChicago AF shell invocation:

\`\`\`bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
bash scripts/zee_gateE6_one_shot.sh
\`\`\`

This activates \`.venv-flavor-f1\` and HiggsTools, checks existing results, compiles three sources, runs E6 physics regression tests, completes the 309-point HiggsSignals run in a **fresh** \`work/zee_E6_309_charged_gamma_HS_20261020_v1/\`, and prints five priority benchmark updated χ² values.

On interruption run \`bash scripts/zee_gateE6_one_shot.sh --resume\` against unchanged source and inputs. Do not overwrite an already completed output.

Outputs:
\`\`\`text
work/zee_E6_309_charged_gamma_HS_20261020_v1/
  E6_309_checkpoint.jsonl
  E6_309_gamma_Zgamma_loop_corrected_HS_NOT_ALLOWED.jsonl
  E6_309_gamma_Zgamma_loop_HS_ranked_NOT_ALLOWED.csv
  manifest.json
  summary.json
work/zee_E6_309_charged_gamma_HS_20261020_v1_run.log
\`\`\`

## Remaining non-negotiable publication blockers

The complete **physical** Zee h125 HiggsSignals prediction requires cross-validation of the modified W/fermion \(Z\gamma\) amplitudes and consistent matching to higher-order SM baseline and production definitions, plus full-model heavy-state **HiggsBounds** (with production and all relevant decays), a completed neutrino/mu-e conversion/complete CLFV likelihood, matched two-charged precision \(B\to X_s\gamma\), charged scalar widths and cross sections, and rigorous global vacuum/UV consistency. The source B4 cascade number is a *proxy upper bound*, **not** a physical BR or event yield. No \(\Delta\chi^2\) cut is calibrated into a complete-model CL; **zero points are certified fully allowed** by E6 alone.
