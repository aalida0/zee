(* Experimental generation configuration; unvalidated.  Frozen model untouched.
   Ye2 and Fzee are independent model parameters with Les Houches metadata;
   their complex input handling must be checked in the generated code. *)
OnlyLowEnergySPheno = True;
MINPAR = {{1,Lambda1Input},{2,Lambda2Input},{3,Lambda3Input},
 {4,Lambda4Input},{5,Lambda5Input},{6,LambdaCInput},
 {7,K1Input},{8,K2Input},{9,K12Input},{10,TanBeta},
 {11,M12SqInput},{12,MCS2Input},{13,Mu4Input}};
RealParameters = {TanBeta};
ParametersToSolveTadpoles = {M112,M222};
DEFINITION[MatchingConditions] = {
 {v1,vSM*Cos[ArcTan[TanBeta]]},{v2,vSM*Sin[ArcTan[TanBeta]]},
 {Ye,YeSM*vSM/v1-v2/v1*Ye2}, {Yd,YdSM*vSM/v1}, {Yu,YuSM*vSM/v2},
 {g1,g1SM},{g2,g2SM},{g3,g3SM}};
BoundaryLowScaleInput = {
 {Lambda1,Lambda1Input},{Lambda2,Lambda2Input},{Lambda3,Lambda3Input},
 {Lambda4,Lambda4Input},{Lambda5,Lambda5Input},{LambdaC,LambdaCInput},
 {K1,K1Input},{K2,K2Input},{K12,K12Input},{M12Sq,M12SqInput},
 {MCS2,MCS2Input},{Mu4,Mu4Input}};
ListDecayParticles = {Fu,Fe,Fd,hh,Ah,Hm};
DefaultInputValues = {Lambda1Input->0.1,Lambda2Input->0.27,Lambda3Input->1.1,
 Lambda4Input->-0.5,Lambda5Input->0.5,LambdaCInput->0.2,
 K1Input->0.1,K2Input->0.1,K12Input->0.,TanBeta->2.,
 M12SqInput->40000.,MCS2Input->90000.,Mu4Input->100.};
