(* New mixed-HZ sources only. Frozen model is read, never regenerated. *)
out=FileNameJoin[{Directory[],"research","wgamma_d16","local"}];
Get[FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH","SARAH.m"}]];
SARAH[OutputDirectory]=FileNameJoin[{out,"sarah_mixed_hz"}];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],FileNameJoin[{Directory[],"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded] || TrueQ[SARAH`AbortStart],Exit[2]];
raw=Association[];
queries=Join[
 Flatten[Table[{ToString[{n,a,b},InputForm],{n,Hm[{a}],conj[Hm[{b}]]}},
  {n,{hh[{1}],hh[{2}],Ah[{2}],Ah[{1}]}},{a,{2,3}},{b,{2,3}}],2],
 Flatten[Table[{ToString[{n,a,b},InputForm],{Hm[{a}],conj[Hm[{b}]],n}},
  {n,{VP,VZ}},{a,{2,3}},{b,{2,3}}],2],
 Flatten[Table[{ToString[{"AZ",a,b},InputForm],{Hm[{a}],conj[Hm[{b}]],VP,VZ}},
  {a,{2,3}},{b,{2,3}}],1],
 Table[{ToString[{Ah[{2}],1,a},InputForm],{Ah[{2}],Hm[{1}],conj[Hm[{a}]]}},{a,{2,3}}],
 Table[{ToString[{Ah[{2}],a,1},InputForm],{Ah[{2}],Hm[{a}],conj[Hm[{1}]]}},{a,{2,3}}]];
Do[raw[d16item[[1]]]=SARAH`Vertex[d16item[[2]],Eigenstates->EWSB],{d16item,queries}];
Put[raw,FileNameJoin[{out,"mixed_hz_raw.m"}]];
Export[FileNameJoin[{out,"mixed_hz_raw.json"}],<|"raw"->Map[ToString[#,InputForm]&,raw],
 "Mathematica"->$Version,"SARAH"->ToString[SA`Version]|>,"RawJSON"];
Print["D16_MIXED_HZ_SOURCES ",Length[raw]];
Exit[0];
