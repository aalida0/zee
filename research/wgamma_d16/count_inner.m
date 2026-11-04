(* Independent topology cross-check ONLY, using the existing pinned SM
   FeynArts model. No SM coupling is used for Zee amplitude matching.
   Optional env D16_FEYNARTS specifies a pre-existing FeynArts directory. *)
tool=Environment["D16_FEYNARTS"];
If[!StringQ[tool],tool=FileNameJoin[{Directory[],"research","spheno_flavorkit","local","FeynArts-3.9"}]];
(* FeynArts3.9 defines Discard, which is protected in Mathematica15. *)
Unprotect[Discard];
Get[FileNameJoin[{tool,"FeynArts.m"}]];
t=CreateTopologies[1,1->2,ExcludeTopologies->{Tadpoles,WFCorrections}];
f=InsertFields[t,S[1]->{V[1],V[1]},Model->"SM",InsertionLevel->{Classes},
 ExcludeParticles->{F[1],F[2],F[3],F[4],V[2],S[1],S[2],U[1],U[2]}];
amps=CreateFeynAmp[f,Truncated->True];
out=FileNameJoin[{Directory[],"research","wgamma_d16","local"}];
Put[f,FileNameJoin[{out,"fa-inner.m"}]];
Put[amps,FileNameJoin[{out,"fa-inner-amplitudes.m"}]];
report=<|"status"->If[Length[amps]===26,"PASS","FAIL"],
 "scope"->"Topology cross-check using existing SM model, NOT Zee vertices or loop evaluation",
 "classes_amplitudes"->Length[amps],"feynarts_version"->$FeynArtsVersion,
 "model_path"->tool,"symmetry_factors"->ToString[Cases[f,SymmetryFactor->x_:>x,Infinity],InputForm]|>;
Export[FileNameJoin[{out,"fa-count.json"}],report,"RawJSON"];
Print["D16_COUNT ",Length[amps]];
Exit[If[report["status"]==="PASS",0,1]];
