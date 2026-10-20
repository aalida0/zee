# E6: source-audited Zee \(hH_i^+H_j^-\), charged-scalar \(h\to\gamma\gamma\) and 309-point HiggsSignals

## Purpose and scientific status

This gate continues the completed E2/E3/E4H/E5/E5A original-Zee scalar scan.

All **309** original scalar potentials had:
- a selected exact-central-NO-neutrino \(f,Y^\ell\) texture optimized in the implemented partial low-energy LFV objective;
- 24/48-point one-loop full-Zee RGE sampled BFB and 55-channel tree unitarity to chosen 10 TeV;
- no deeper numerical tree vacuum FOUND (not global proof);
- small direct \(h125\to e\mu,e\tau,\mu\tau\) branching ratio proxies;
- a REAL 159-observable HiggsSignals effective-coupling \(\chi^2\) in E5.

E5A revealed down-type couplings drive the main HiggsSignals tension; our preferred source benchmark **B4_0004143** had original conditional \(\Delta\chi^2_{\rm HS}=0.8164\), \(\kappa_b=0.96657\), cascade upper proxy \(0.59388\). Original cascade priority B4_0006862 had \(23.1068\) and proxy \(0.60437\). Both remain *unvalidated physically allowed*.

E6 derives **all \(hH_{1,2}^+H_{1,2}^-\) and \(hH_1^+H_2^-\) tree trilinears** from original Florentino Zee scalar potential; independently verifies them from the Higgs-basis map; computes BOTH charged-scalar one-loop \(h\to\gamma\gamma\) amplitudes; injects the interference into HiggsTools' original partial width, re-evaluates actual same-dataset HiggsSignals for all 309 spectra.

E6 does **NOT** compute a complete \(h\to Z\gamma\) correction: the off-diagonal \(ZH_1H_2\) current makes mixed-mass loops compulsory. The numerical source records this rather than adding an incorrectly diagonal-only rate. See Florentino, Romão, Silva *EPJC* **81 (2021) 1148**, DOI https://doi.org/10.1140/epjc/s10052-021-09956-2, **Appendix D, Eqs. (D.19–D.21)** for both on-shell decays including mixed-mass \(\Delta B_0\), \(C_0\) integrals and the nontrivial normalization. A generic 2018 hZγ one-loop paper is https://doi.org/10.1140/epjc/s10052-018-6349-0. A second nondegenerate-mass formula is https://doi.org/10.1140/epjc/s10052-022-10225-z.

**Do not claim “complete Zee gamma/Zgamma Higgs fit” or “model allowed” after E6.** This is a strictly improved *conditional h125 HiggsSignals* fit with a **complete LO charged-scalar \(\gamma\gamma\) loop subset**, but LO BSM amplitudes on top of HiggsTools' higher-order reference decay widths. The next independent validation must implement FULL hZγ off-diagonal mixed-mass amplitudes, fermion/W contributions at matching normalization, and compare to independent PV backend/old Florentino source limiting examples.

## 1. Exact scalar conventions and independent cubic derivatives

Use the **original gauge scalar potential** in \`docs/zee_full_ufo_implementation_contract.md\`, Eq. (16) of arXiv:2106.08332, and the full physical reconstruction in \`gate6_benchmark.py\`.

The charged gauge basis is \((\phi_1^+,\phi_2^+,\chi^+)\), and the charged rotation is

\[
G^+=c_\beta\phi_1^+ +s_\beta\phi_2^+,\quad
H_1^+=c_\gamma(-s_\beta\phi_1^+ +c_\beta\phi_2^+)+s_\gamma\chi^+,
\]
\[
H_2^+=-s_\gamma(-s_\beta\phi_1^+ +c_\beta\phi_2^+)+c_\gamma\chi^+ .
\]

For the CP-even 125 GeV scalar, \(h=\cos\alpha\,\rho_1+\sin\alpha\,\rho_2\).

The potential's **fixed-Lagrangian-quadratics charged Hessian** is

\[
{\cal M}_+^2(v_1,v_2)=
\begin{pmatrix}
m_{11}^2+\frac12(\lambda_1v_1^2+\lambda_3v_2^2)&
-m_{12}^2+\frac12(\lambda_4+\lambda_5)v_1v_2&
+\mu_4 v_2/\sqrt2\\
\cdot&m_{22}^2+\frac12(\lambda_2 v_2^2+\lambda_3v_1^2)&
-\mu_4 v_1/\sqrt2\\
\cdot&\cdot&m_C^2+\frac12(k_1v_1^2+k_2v_2^2-2k_{12}v_1v_2)
\end{pmatrix},
\]

where the quadratic masses \(m_{11}^2,m_{22}^2\) were determined ONCE by the tadpoles at the original vacuum, then *held fixed* for differentiation:

\[
g_{hij}=\left[U^T(\cos\alpha\,\partial_{v_1}{\cal M}_+^2+
\sin\alpha\,\partial_{v_2}{\cal M}_+^2)U\right]_{ij},\qquad i,j\in\{1,2\}.
\]

An independent Higgs-basis evaluation uses \(\delta=\alpha-\beta\), the actual source \`gate7_map_p2_to_yangwu.map_point\` quartics \(Z_3,Z_7,K_1,K_{12}\), and

\[
\partial_h{\cal M}_{+,(H_D,\chi)}^2 =
\begin{pmatrix}
v(Z_3\cos\delta+Z_7\sin\delta)&
-\mu_4\cos\delta/\sqrt2\\
-\mu_4\cos\delta/\sqrt2&
v(K_1\cos\delta+K_{12}\sin\delta)
\end{pmatrix}.
\]

Compare these *numerically independent algebraic paths* to relative \(2\times10^{-6}\), verify 0/charged mass eigenvalues, and verify the existing Gate 6 \(hH_1H_2\) trilinear. The full charged scalar \(Z\) generator in the \((H_D,\chi)\) basis is \(\text{diag}(1/2-s_W^2,-s_W^2)\); after rotation the \(ZH_1H_2\) generator is nonzero for nonzero mixing.

**Important:** trilinears here are **potential** coefficients in \(V\supset +g_{hij}hH_i^-H_j^+\), not Feynman-rule values; the interaction has \({\cal L}=-V\).

## 2. Charged scalar \(h\gamma\gamma\) amplitude and HiggsSignals

Using \(\tau_i=m_h^2/(4m_{H_i}^2)\), \(f(\tau)=\arcsin^2\sqrt\tau\) for \(\tau<1\),

\[
A_0(\tau)=-[\tau-f(\tau)]/\tau^2,\qquad
A_{H_i}=\frac{v g_{hii}}{2m_{H_i}^2} A_0(\tau_i).
\]

The CP-even LO amplitude is \(A_W+A_t+A_b+A_c+A_\tau +A_{H_1}+A_{H_2}\); CP-odd contributions from complex diagonal \(Y^\ell\) enter quadratically **without interference** with CP-even scalars.

Define

\[
R_{\gamma\gamma}^{\rm scalar} =
\frac{|A_{\rm SM-particle,even}^{LO}+A_{H_1}+A_{H_2}|^2
+|A_{\rm SM-particle,odd}^{LO}|^2}
{|A_{\rm SM-particle,even}^{LO}|^2+|A_{\rm SM-particle,odd}^{LO}|^2}.
\]

HiggsTools' previous E5 \(\Gamma(h\to\gamma\gamma)\) is multiplied by \(R_{\gamma\gamma}^{\rm scalar}\) using \`h.setDecayWidth("gamgam",...)\` *after* one \`effectiveCouplingInput()\` call and all three LFV width additions. Check exact updated total width and gamgam BR consistency. The leading-order ratio is anchored to the *same* higher-order HiggsTools baseline so relative higher-order model dependence remains an approximation.

Crucial: no off-diagonal H1-H2 loop in photon-photon because photon charge generator is an identity; h12 cubic cannot connect two diagonal photon current insertions. This is a physics cross-check in the source regression.

Actual HiggsSignals re-evaluates the SAME 159 HS observables and reference SM \(\chi^2=153.7181898\), reproducing EVERY E5 per-point \(\chi^2\) first to \(5\times10^{-6}\). Updated gamma width changes branching ratios of all other h decay channels and hence the correlated HS objective. Only the gamma channel is newly modified; the \(Z\gamma\) channel remains at the E5 effective approximation. The missing hZγ mixed scalar loops have NOT been faked or claimed negligible.

The source constructs up to 309 input points; strict E2/E3/E4H/E5 manifest/data SHA and original E5 output-evidence checks before modifying predictions. Output checkpoint fsynced after every point, \`--resume\` requires the identical current script and source/data manifest. Every output sets \`full_Zee_allowed_or_excluded=null\`.

## 3. ONE command for the entire AF job

All required code already committed to the \`gateA1p-independent-hepfit-typeii-matching\` branch:

- \`scripts/zee_gateE6_309_charged_gamma_higgssignals.py\`;
- \`tests/test_zee_gateE6_309_charged_gamma_higgssignals.py\`;
- \`scripts/zee_gateE6_one_shot.sh\`.

On UChicago AF:

\`\`\`bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
bash scripts/zee_gateE6_one_shot.sh
\`\`\`

This ONE command: activates existing \`.venv-flavor-f1\`, checks E2/E3/E4H/E5 and real HiggsTools/HSDataSet, runs source compilation checks and 8 unit tests, then re-evaluates original source E5 and scalar \(\gamma\gamma\) corrected HiggsSignals for all **309** source candidates with logging and completion assertions.

If interrupted, run \`bash scripts/zee_gateE6_one_shot.sh --resume\` *without modifying the source version*. On completion:

\`\`\`text
work/zee_E6_309_charged_gamma_HS_20261020_v1/
  manifest.json
  E6_309_checkpoint.jsonl
  E6_309_gamma_loop_corrected_HS_NOT_ALLOWED.jsonl
  E6_309_gamma_loop_HS_ranked_NOT_ALLOWED.csv
  summary.json
work/zee_E6_309_charged_gamma_HS_20261020_v1_run.log
\`\`\`

The final printed results contain the changed 309-sample median/range HiggsSignals statistic and exactly **five** priority source benchmarks: B4_0004143, B4_0003582, B4_0004173, B4_0006862 and B4_0006962.

**Only E6 code and synthetic/gauge-closure tests are committed at authoring time**; they have not been executed on UChicago AF. Do not invent an AF HiggsSignals result before execution.

## 4. Physical publication blockers after E6

- Full mixed-mass \(Z H_1^\pm H_2^\mp\) charged-scalar hZγ loops, including exact two-/three-point PV functions B0,C0 and conventional SM W/fermion interference; compare analytically/numerically with Florentino EPJC 81 (2021) 1148 **Appendix D** and independent numerical PV library. A diagonal-only Zgamma guess must not enter HS.
- Complete HiggsBounds for other CP-even, CP-odd, singly charged Zee scalar states, physical production/decay and experimental signatures.
- Neutrino likelihood beyond exact central NO, full LFV—including mu-e conversion, complete two-loop/Barr-Zee and CP phases—and properly matched two-charged B→Xsγ.
- Global vacuum certificate, perturbative UV scheme/thresholds and input EWPO uncertainties.

Source science cannot yet mark a Zee configuration fully ALLOWED. The current cascade upper proxy is NOT an on-shell rate or \(\mathrm{BR}_{\rm physical}(H_2\to H_1 Z)\).

If the charged \(\gamma\gamma\) update leaves B4_0004143 approximately SM Higgs-compatible, prioritize that benchmark for model-complete widths and production. If it changes the 125 fit substantially, use the corrected result—not E5—as the starting point for any proposed alignment scan. No \(\Delta\chi^2\) numerical threshold is automatically a 95% CL cut.
