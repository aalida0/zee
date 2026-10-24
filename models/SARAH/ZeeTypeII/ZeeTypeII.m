(* ZeeTypeII: CP-conserving Gate6 scalar potential, Type-II quarks,
   general complex charged-lepton Yukawas, antisymmetric Zee coupling.
   SOURCE_IMPLEMENTED_NOT_VALIDATED: requires SARAH 4.15.4 CheckModel.
   Baseline: scripts/gate6_benchmark.py (arXiv:2106.08332).
   The sign of Mu4 below reproduces M^2_(H_D+,S+)=-Mu4*v/Sqrt[2],
   with H_D+=-Sin[beta] H1p+Cos[beta] H2p. *)

Model`Name = "ZeeTypeII";
Model`NameLaTeX = "Type-II quark Zee model with general lepton Yukawas";
Model`Authors = "Zee project implementation";
Model`Date = "2026-10-21";

Gauge[[1]] = {B, U[1], hypercharge, g1, False};
Gauge[[2]] = {WB, SU[2], left, g2, True};
Gauge[[3]] = {G, SU[3], color, g3, False};

FermionFields[[1]] = {q, 3, {uL,dL}, 1/6, 2, 3};
FermionFields[[2]] = {l, 3, {vL,eL}, -1/2, 2, 1};
FermionFields[[3]] = {d, 3, conj[dR], 1/3, 1, -3};
FermionFields[[4]] = {u, 3, conj[uR], -2/3, 1, -3};
FermionFields[[5]] = {e, 3, conj[eR], 1, 1, 1};

ScalarFields[[1]] = {H1, 1, {H1p,H10}, 1/2, 2, 1};
ScalarFields[[2]] = {H2, 1, {H2p,H20}, 1/2, 2, 1};
(* Splus is an SU(2) singlet with Y=+1 and therefore Q=+1. *)
ScalarFields[[3]] = {Splus, 1, Sp, 1, 1, 1};

NameOfStates = {GaugeES, EWSB};

DEFINITION[GaugeES][Additional] = {
  {LagHC, {AddHC -> True}},
  {LagNoHC, {AddHC -> False}}
};

(* L = L_kin - V + L_Y. For the scalar potential:
 V2 = M112 |H1|^2 + M222 |H2|^2
      - (M12Sq H1^dag H2 + h.c.) + MCS2 |S+|^2.
 V4 = Lambda1/2 |H1|^4 + Lambda2/2 |H2|^4
      + Lambda3 |H1|^2 |H2|^2 + Lambda4 |H1^dag H2|^2
      + (Lambda5/2 (H1^dag H2)^2 + h.c.)
      + LambdaC |S+|^4 + K1 |S+|^2 |H1|^2
      + K2 |S+|^2 |H2|^2
      - K12 |S+|^2 (H1^dag H2 + h.c.).
 V3 = Mu4 S- (H1^T i sigma2 H2) + h.c.
 All scalar couplings here are REAL. The f and Ye2 matrices are complex.
 *)

LagNoHC = -(
    M112 conj[H1].H1 + M222 conj[H2].H2
  + MCS2 conj[Splus].Splus
  + Lambda1/2 conj[H1].H1.conj[H1].H1
  + Lambda2/2 conj[H2].H2.conj[H2].H2
  + Lambda3 conj[H1].H1.conj[H2].H2
  + Lambda4 conj[H1].H2.conj[H2].H1
  + LambdaC conj[Splus].Splus.conj[Splus].Splus
  + K1 conj[Splus].Splus.conj[H1].H1
  + K2 conj[Splus].Splus.conj[H2].H2
);

(* SARAH dot contraction H1.H2 is SU(2) antisymmetric.
   The fermion term Fzee/2 l.l.Splus uses two left Weyl lepton
   doublets. The 1/2 convention is subject to amplitude-level matching. *)
LagHC = -(
   -M12Sq conj[H1].H2
   + Lambda5/2 conj[H1].H2.conj[H1].H2
   - K12 conj[Splus].Splus.conj[H1].H2
   + Mu4 conj[Splus].H1.H2
   + Yd conj[H1].d.q
   + Ye conj[H1].e.l
   + Ye2 conj[H2].e.l
   - Yu H2.u.q
   + Fzee/2 l.l.Splus
);

DEFINITION[EWSB][GaugeSector] = {
 {{VB,VWB[3]},{VP,VZ},ZZ},
 {{VWB[1],VWB[2]},{VWm,conj[VWm]},ZW}
};

DEFINITION[EWSB][VEVs] = {
 {H10, {v1,1/Sqrt[2]}, {sigma1,I/Sqrt[2]}, {phi1,1/Sqrt[2]}},
 {H20, {v2,1/Sqrt[2]}, {sigma2,I/Sqrt[2]}, {phi2,1/Sqrt[2]}}
};

DEFINITION[EWSB][MatterSector] = {
 {{phi1,phi2},{hh,ZH}},
 {{sigma1,sigma2},{Ah,ZA}},
 {{conj[H1p],conj[H2p],conj[Sp]},{Hm,ZP}},
 {{{dL},{conj[dR]}},{{DL,Vd},{DR,Ud}}},
 {{{uL},{conj[uR]}},{{UL,Vu},{UR,Uu}}},
 {{{eL},{conj[eR]}},{{EL,Ve},{ER,Ue}}}
};

DEFINITION[EWSB][DiracSpinors] = {
 Fd -> {DL,conj[DR]},
 Fu -> {UL,conj[UR]},
 Fe -> {EL,conj[ER]},
 Fv -> {vL,0}
};

DEFINITION[GaugeES][DiracSpinors] = {
 Fd1 -> {dL,0}, Fd2 -> {0,dR},
 Fu1 -> {uL,0}, Fu2 -> {0,uR},
 Fe1 -> {eL,0}, Fe2 -> {0,eR},
 Fv1 -> {vL,0}
};
