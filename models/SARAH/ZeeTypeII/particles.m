(* Neutral states hh={h,H}; Ah={G0,A}; charged Hm={G-,H1-,H2-}.
   Particle metadata follows THDM-II with corrected gauge-eigenstate entries. *)
ParticleDefinitions[GaugeES] = {
 {H10,{PDG -> {0},Mass -> Automatic,Width -> 0,
        FeynArtsNr -> 1,LaTeX -> "H_1^0",OutputName -> "H10"}},
 {H20,{PDG -> {0},Mass -> Automatic,Width -> 0,
        FeynArtsNr -> 2,LaTeX -> "H_2^0",OutputName -> "H20"}},
 {H1p,{PDG -> {0},Mass -> Automatic,Width -> 0,
        FeynArtsNr -> 3,LaTeX -> "H_1^+",OutputName -> "H1p"}},
 {H2p,{PDG -> {0},Mass -> Automatic,Width -> 0,
        FeynArtsNr -> 4,LaTeX -> "H_2^+",OutputName -> "H2p"}},
 {Sp,{PDG -> {0},Mass -> Automatic,Width -> 0,
      FeynArtsNr -> 5,LaTeX -> "s^+",OutputName -> "Sp"}},
 {VB,{Description -> "B-Boson"}},
 {VG,{Description -> "Gluon"}},
 {VWB,{Description -> "W-Bosons"}},
 {gB,{Description -> "B-Boson Ghost"}},
 {gG,{Description -> "Gluon Ghost"}},
 {gWB,{Description -> "W-Boson Ghost"}},
 (* Conventional SARAH names from Models/particles.m.
    Needed for gauge-eigenstate Dirac-spinor metadata in CheckModel. *)
 {Fd1,{Description -> "Dirac Left Down-Quark"}},
 {Fd2,{Description -> "Dirac Right Down-Quark"}},
 {Fu1,{Description -> "Dirac Left Up-Quark"}},
 {Fu2,{Description -> "Dirac Right Up-Quark"}},
 {Fe1,{Description -> "Dirac Left Electron"}},
 {Fe2,{Description -> "Dirac Right Electron"}},
 {Fv1,{Description -> "Dirac Left Neutrino"}}
};

ParticleDefinitions[EWSB] = {
 {hh,{Description -> "Higgs",PDG -> {25,35},Mass -> Automatic,
      Width -> Automatic,OutputName -> "hh"}},
 {Ah,{Description -> "Pseudo-Scalar Higgs",PDG -> {0,36},
      Mass -> Automatic,Width -> Automatic,OutputName -> "Ah"}},
 {Hm,{Description -> "Charged Higgs",PDG -> {0,37,9000037},
      Mass -> Automatic,Width -> Automatic,OutputName -> "Hm"}},
 {VP,{Description -> "Photon"}},
 {VZ,{Description -> "Z-Boson",Goldstone -> Ah[{1}]}},
 {VG,{Description -> "Gluon"}},
 {VWm,{Description -> "W-Boson",Goldstone -> Hm[{1}]}},
 {gP,{Description -> "Photon Ghost"}},
 {gWm,{Description -> "Negative W-Boson Ghost"}},
 {gWmC,{Description -> "Positive W-Boson Ghost"}},
 {gZ,{Description -> "Z-Boson Ghost"}},
 {gG,{Description -> "Gluon Ghost"}},
 {Fd,{Description -> "Down-Quarks"}},
 {Fu,{Description -> "Up-Quarks"}},
 {Fe,{Description -> "Leptons"}},
 {Fv,{Description -> "Neutrinos"}}
};

WeylFermionAndIndermediate = {
 {sigma1,{LaTeX -> "\\sigma_1"}},
 {sigma2,{LaTeX -> "\\sigma_2"}},
 {phi1,{LaTeX -> "\\phi_1"}},
 {phi2,{LaTeX -> "\\phi_2"}},
 {dR,{LaTeX -> "d_R"}},
 {eR,{LaTeX -> "e_R"}},
 {uR,{LaTeX -> "u_R"}},
 {eL,{LaTeX -> "e_L"}},
 {dL,{LaTeX -> "d_L"}},
 {uL,{LaTeX -> "u_L"}},
 {vL,{LaTeX -> "\\nu_L"}},
 {DR,{LaTeX -> "D_R"}},
 {ER,{LaTeX -> "E_R"}},
 {UR,{LaTeX -> "U_R"}},
 {DL,{LaTeX -> "D_L"}},
 {EL,{LaTeX -> "E_L"}},
 {UL,{LaTeX -> "U_L"}}
};
