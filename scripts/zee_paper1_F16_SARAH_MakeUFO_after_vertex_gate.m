(* F16 optional actual LO SARAH MakeUFO export, hard gated by source-closed
   THREE-CASE independent vertex result. Does not produce model-specific
   param_card or certify full MadWidth BR. Run ONLY after the previous
   SARAH fixture-local audit reports PASS. *)
root=Directory[];
dir=Environment["ZEE_F16_DIR"];
If[!StringQ[dir]||!DirectoryQ[dir],
 Print["F16_UFO_BLOCKED_NO_SOURCE_FIXTURE_DIR"];Exit[2]];
status=FileNameJoin[{dir,"F16_local_SARAH_vertex_status.txt"}];
wanted="F16_THREE_HEAVY_SARAH_MASS_GAUGE_CUBIC_COMPLEX_LEPTON_PASS_NOT_MADWIDTH";
If[!FileExistsQ[status]||StringTrim[Import[status,"Text"]]=!=wanted,
 Print["F16_UFO_BLOCKED_INDEPENDENT_THREE_POINT_SARAH_VERTEX_AUDIT_NOT_PASS"];
 Exit[3]];
sfile=FileNameJoin[{$HomeDirectory,".Mathematica","Applications",
 "SARAH-4.15.4","SARAH.m"}];
If[!FileExistsQ[sfile],Print["F16_UFO_NO_SARAH_INSTALL"];Exit[4]];
out=FileNameJoin[{dir,"F16_ZeeTypeII_LO_UFO_EXPORTED_UNVALIDATED"}];
If[FileExistsQ[out]||DirectoryQ[out],
 Print["F16_UFO_BLOCKED_REFUSE_OVERWRITE ",out];Exit[5]];
default=FileNameJoin[{DirectoryName[sfile],"Output","ZeeTypeII","EWSB","UFO"}];
(* If an earlier SARAH UFO is present, force an operator to investigate:
   never accidentally carry forward cached/corrupt source. *)
If[DirectoryQ[default],
 Print["F16_UFO_BLOCKED_STALE_SARAH_OUTPUT_EXISTS ",default];Exit[6]];
PrependTo[$Path,DirectoryName[sfile]];
CheckAbort[Get[sfile],Print["F16_UFO_SARAH_LOAD_ABORT"];Exit[7]];
SARAH[InputDirectories]=Prepend[SARAH[InputDirectories],
 FileNameJoin[{root,"models","SARAH"}]];
SARAH`Start["ZeeTypeII"];
If[!TrueQ[SARAH`ModelLoaded]||TrueQ[SARAH`AbortStart],
 Print["F16_UFO_START_FAILED"];Exit[8]];
Print["F16_UFO_SOURCE_GENERATION_START"];
CheckAbort[MakeUFO[],Print["F16_UFO_MAKEUFO_ABORT"];Exit[9]];
If[!DirectoryQ[default]||!And@@(FileExistsQ[
   FileNameJoin[{default,#}]]&/@
   {"parameters.py","particles.py","vertices.py","couplings.py","lorentz.py"}),
 Print["F16_UFO_OUTPUT_MISSING ",default];Exit[10]];
CopyDirectory[default,out];
Print["F16_UFO_EXPORTED_SOURCE_ONLY_NOT_PARAM_CARD_OR_FULL_WIDTH ",out];
Print["F16_UFO_SARAH_PDG_NOTE: H1=37,H2=9000037,neutral_H=35,A=36"];
Print["F16_UFO_NEXT: numerical model card mass/mixing/CKM coupling closure"];
Exit[0];
