(* Probe-only SARAH vertices for H2+ -> H1+ Z.
   Do NOT mark as validated without coefficient and Lorentz-structure audit.
   Run from ~/zee: math -script scripts/zee_sarah_z_vertex_probe.m *)
root=Directory[];
outDir=FileNameJoin[{root,"work","sarah_zee"}];
If[!DirectoryQ[outDir],CreateDirectory[outDir,CreateIntermediateDirectories->True]];
statusFile=FileNameJoin[{outDir,"z_vertex_probe_status.txt"}];
setProbeStatus[zeeStatus_String]:=(
 Export[statusFile,zeeStatus<>"\n","Text"];
 Print["ZEE_Z_VERTEX_STATUS ",zeeStatus]
);
setProbeStatus["Z_VERTEX_NOT_VALIDATED"];
sarahFile=FileNameJoin[{$HomeDirectory,".Mathematica","Applications","SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[sarahFile],
 Print["FAIL SARAH_NOT_FOUND ",sarahFile];
 setProbeStatus["Z_VERTEX_NO_SARAH"];Exit[2]];
PrependTo[$Path,DirectoryName[sarahFile]];
loaded=CheckAbort[(Get[sarahFile];True),False];
If[!TrueQ[loaded]||!ValueQ[SA`Version],
 setProbeStatus["Z_VERTEX_LOAD_FAILED"];Exit[3]];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],
 FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],
 setProbeStatus["Z_VERTEX_START_FAILED"];Exit[4]];
(* Hm denotes the negatively charged field; conj[Hm] denotes positive.
   Convention: Hm[1] is Goldstone, 2=H1-, 3=H2-.
   We print both orders to expose momentum/sign conventions. *)
Print["ZEE_Z_VERTEX_EXPECTED_ABS_COEFF g2*Abs[Sin[2 gamma]]/(4 Cos[thetaW])"];
Print["ZEE_Z_VERTEX_NOTE  coefficient excludes external momentum difference"];
couplings={
 {"Z_2_3", {conj[Hm[{2}]],Hm[{3}],VZ}},
 {"Z_3_2", {conj[Hm[{3}]],Hm[{2}],VZ}},
 {"Z_2_2", {conj[Hm[{2}]],Hm[{2}],VZ}},
 {"Z_3_3", {conj[Hm[{3}]],Hm[{3}],VZ}},
 {"PHOTON_2_3", {conj[Hm[{2}]],Hm[{3}],VP}},
 {"PHOTON_2_2", {conj[Hm[{2}]],Hm[{2}],VP}},
 {"Z_GENERIC", {conj[Hm],Hm,VZ}}
};
results={};
Do[
 Print["ZEE_Z_VERTEX_BEGIN ",item[[1]]];
 val=CheckAbort[SARAH`Vertex[item[[2]],Eigenstates->EWSB],$Aborted];
 Print["ZEE_Z_VERTEX_VALUE ",item[[1]]," ",InputForm[val]];
 AppendTo[results,{item[[1]],val}],
 {item,couplings}
];
Export[FileNameJoin[{outDir,"z_vertex_raw.txt"}],
 StringRiffle[Table[
 ToString[results[[i,1]]]<>":\n"<>ToString[InputForm[results[[i,2]]]],
 {i,Length[results]}],"\n\n"],"Text"];
If[MemberQ[results,$Aborted,Infinity],
 setProbeStatus["Z_VERTEX_EXTRACTION_ABORTED"];Exit[5]];
setProbeStatus["Z_VERTEX_EXTRACTED_NOT_YET_PHYSICS_VALIDATED"];
Exit[0];
