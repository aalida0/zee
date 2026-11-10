# Reuse of corrected general-2HDM and Zee literature for LFV

**10 November 2026. Neutral Yukawa map PASS on 4/4 exact cards. Tree-only scalar conversion is at a numerical floor. PHYSICAL LFV UNKNOWN.**

## Primary physics source and transfer limits

**Altmannshofer, Assi, Brod, Hamer, Julio, Uttayarat and Volkov**, JHEP **06 (2025) 156**, arXiv:2410.17313, plus **erratum JHEP 07 (2026) 184**, published 21 July 2026. Their general-2HDM complete two-loop radiative LFV calculation has public source at https://gitlab.com/jbrod/general-2hdm-pheno. Its neutral-sector Yukawa mapping in Eqs. (11)–(13) is transferable to our CP-conserving neutral scalar spectrum. **The GitLab implementation itself was not run in this audit.**

The paper explicitly cautions that the bosonic contributions are gauge dependent if charged Higgs diagrams are omitted. The Zee model contains TWO charged scalars of mixed SU(2) representations, plus non-diagonal ZH1H2 couplings. There is NO unique charged Higgs mass MHp that can reproduce the full 2HDM bosonic two-loop result. Only separately demonstrated gauge-invariant neutral-fermion-loop subsets may be reused directly.

**Herrero-García et al.**, JHEP04(2017)130, arXiv:1701.05345, is a general Zee lepton/scan reference but explicitly sets second-doublet **up and down quark Yukawas to zero in Sec 2.5**, unlike our Type-II quark sector. Useful as a lepton-sector limit, not as a full Type-II mu-e conversion prediction.

**Florentino, Romão, Silva**, arXiv:2106.08332, is appropriate for the charged mixing and cascade scalar gauge vertices. **Coy–Frigerio**, arXiv:2110.09126, supplies only heavy/unmixed Zee EFT limits. The older **Davidson 2016 general-2HDM** analysis explains why W/top two-loop terms can be relevant even when one-loop amplitudes are small.

## Exact neutral Yukawa bridge (implemented and tested)

In native Module3 the D matrix has RH row / LH column. In the source Eq.(11) the neutral down-type Yukawa appears in LH,RH order. Accordingly,

$$
\rho_\ell=D/\sqrt{2},\quad \delta=\beta-\alpha.
$$

The neutral scalar mixing rows obey

$$
(q_{h1},q_{h2})=(\cos\delta,-\sin\delta),\quad
(q_{H1},q_{H2})=(\sin\delta,\cos\delta),\quad
(q_{A1},q_{A2})=(0,i).
$$

The source Yukawa for each neutral state is

$$
Y_{LR}^{S} = \mathrm{diag}(m_\ell/v)\,q_{S1}+\rho_\ell^\dagger q_{S2},
$$

which is equal to the conjugate-transpose of the frozen native Zee neutral vertex matrix. All h/H/A for all four frozen complex cards agree at numerical precision, including complex phases. Independent reconstruction of **D = -sin(beta)*Ye + cos(beta)*Ye2** from the frozen original full Yukawa records has maximum relative residual **4.87e-16**.

The direct e-mu entries of rho are of order 1e-19 for D7 or 1e-20 for F13, i.e. at the numeric roundoff floor of these frozen texture solutions. Single-e-mu-Yukawa neutral Barr–Zee loops are suppressed, but tau-chain double Yukawa insertions and Zee charged-gauge loops are NOT thereby bounded. The delivered machine-readable source-input dictionary deliberately omits MHp; no full 2HDM radiative rate was calculated.

## Tree-only CP-even Al-27 conversion, with LO heavy quark scalar matching

Using Type-II couplings **kappa_u=q1+q2*cot(beta)** and **kappa_d=q1-q2*tan(beta)** for h/H, and the heavy quark nucleon trace factor

$$
f_{TQ}^N={2\over27}(1-f_{Tu}^N-f_{Td}^N-f_{Ts}^N),
$$

the coherent tree CP-even scalar source includes u,d,s and the c,b,t trace anomaly at leading order. The aluminum response uses previously source-checked fixed overlaps Sp=0.0153, Sn=0.0163 and capture rate 4.64079e-19 GeV.

| Frozen card | central-f tree-only Al diagnostic | conditional maximum (all 6 light f_T^p,n in 0..0.10) |
| --- | ---: | ---: |
| D7 NO | 6.81e-44 | 2.70e-43 |
| D7 IO | 4.77e-44 | 1.89e-43 |
| F13 NO | 1.52e-46 | 5.43e-46 |
| F13 IO | 1.01e-45 | 3.62e-45 |

The tree-only amplitude is affine in all six f_T fractions, hence its quadratic rate is convex; all 2^6=64 vertices of the assumed input box were tested. This is a mathematical maximum of **the tree-only scalar subset at fixed nuclear overlap**, not a theory-uncertainty interval or upper/lower bound on the full conversion rate.

**Important precision caveat:** the numbers are controlled by off-diagonal D entries at numerical roundoff size. They are numerical-floor diagnostics, **not stable three-digit predictions**. If these texture zeros are enforced analytically, the tree scalar amplitude vanishes. Robustly, the neutral h/H tree-scalar sector is negligible for these frozen textures; nothing is inferred about loop scalar/gluon operators.

## Existing full one-loop observable shortcut

SARAH SPheno-files documentation and **Porod, Staub, Vicente, A flavor kit for BSM models**, EPJC 74 (2014) 2992, explicitly describe the generated **BR1LeptonTo3Leptons** routine in **LowEnergy_[Model].f90**. This is the highest-value source to recover for an independent native mu->3e contact/identical-electron/signed-interference check. The earlier three-Fortran upload contained only FlavorKit_LFV_ZeeTypeII.f90, Couplings_ZeeTypeII.f90 and LoopFunctions.f90; the original observable-body source was **not included**.

## Execution and delivery

12 fresh focused Python tests PASS. Reproducible Python bridge, neutral source-input JSON, LO tree conversion implementation, six-fraction envelope, fixed compact cards and full literature report are packaged in the conversation attachment named **zee_lfv_2hdm_literature_bridge_2026-11-10.zip**. No third-party code is republished. The GitLab general-2HDM program was NOT run; no physical LFV mu3e/Al/radiative rate was evaluated.

**Next exact blocker:** retrieve the generated LowEnergy_ZeeTypeII.f90 observable body, validate its native coefficient ordering against the original Fortran group ledger, and qualify finite-q2 photon, scalar scheme and omitted charged/bosonic two-loop contributions. Current physical_lfv=UNKNOWN, global_acceptance=null.
